from CoreLib import *
from BinTracker import BinTracker
from MetOffice import MetOffice
import threading, logging, time, configparser, vfdpos

logging.basicConfig(level=logging.DEBUG,
					format='[%(levelname)s] (%(threadName)-10s) %(message)s',
					)

class ScreenData(object):
	def __init__(self, config):
		self.lock = threading.Lock()
		self.screenlock = threading.Lock()
		self.dataArray = []
		self.config = config
		fac = vfdpos.WincorNixdorfDisplayFactory()
		self.display = fac.get_vfd_pos()[0]
		self.display.clearscreen()
		bt = BinTracker('binschedule.json')
		mo = MetOffice(self.config['MetOffice']['Key'],config['MetOffice']['LocationCode'])
		self.sources = [bt,mo]

	def updateDataArray(self, data):
		"""Safely replaces the active data array with a new one"""
		logging.debug("Waiting for lock")
		self.lock.acquire()
		try:
			logging.debug("Lock acquired")
			dataArray = data
		finally:
			self.lock.release()
	
	def writeScreenData(self,lineArray):
		logging.debug("Waiting for ScreenLock")
		# Wait for lock on screen
		self.screenlock.acquire()
		try:
			self.display.clearscreen()
			logging.debug("ScreenLock acquired")
			logging.info("LINE1: "+self.pad_line(lineArray[0]))
			logging.info("LINE2: "+lineArray[1])
			# Position cursor and write first line
			self.display.poscur(1,1)
			self.display.write_msg(lineArray[0])

			# Position cursor and write second line
			self.display.poscur(2,1)
			if len(lineArray[1]) > 20:
				
				string = lineArray[1]
				first = True
				while len(string) > 19:
					self.display.poscur(2,1)
					self.display.write_msg(string[0:20])
					string = string[1:]
					if first:
						time.sleep(int(self.config['App']['ScrollingWaitTime']))
						
						first = False
					else:
						time.sleep(float(self.config['App']['ScrollInterval']))
			else:
				self.display.write_msg(lineArray[1])
		finally:
			# Release lock on screen
			self.screenlock.release()

	def update_data(self):
		logging.debug("Waiting for lock")
		self.lock.acquire()
		try:
			logging.debug("Lock acquired")
			newList = []
			for source in self.sources:
				data = source.getData()
				for item in data:
					logging.debug("Added: "+item[0])
					newList.append(item)
				
			self.dataArray = newList
		finally:
			self.lock.release()

	def update_data_loop(self):
		# when this is called, we have 'never' done an update
		lastupdate = 0
		while True:
			# what is now
			now = time.time()
			if now - lastupdate >= int(self.config['App']['DataRefreshInterval']):
				logging.debug("Performing update")

				# Get new data
				new_data = self.update_data()

				# Add new data to active array
				self.updateDataArray(new_data)

				# note that this is the last time we ran an update
				lastupdate = time.time()

			else:
				logging.debug("Sleeping")
				time.sleep(0.5)

	def pad_line(self,line):
		linediff = math.floor((20 - len(line))/2)
		line = (" "*linediff)+line
		return line

	def display_data_loop(self):
		while True:
			logging.debug("New loop")
			for data_item in self.dataArray:
				logging.debug("Writing new item")
				self.writeScreenData(data_item)
				time.sleep(int(self.config['App']['WaitTime']))

		

# Read in our config
config = configparser.ConfigParser()
config.read('display.conf')

# Initialize the ScreenData object
screendata = ScreenData(config)

# Perform an inital data update
screendata.updateDataArray(screendata.update_data())

updateThread = threading.Thread(name="UpdateThread", target=screendata.update_data_loop)
updateThread.start()
logging.debug("Started UpdateThread")
displayThread = threading.Thread(name="DisplayThread", target=screendata.display_data_loop)
displayThread.start()
logging.debug("Started DisplayThread")