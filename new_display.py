from CoreLib import *
from BinTracker import BinTracker
from MetOffice import MetOffice
import threading, logging, time, configparser, vfdpos

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

class ScreenData(object):
	def __init__(self):
		self.lock = threading.Lock()
		self.dataArray = []
	def getData(self):
		logging.debug("Waiting for lock")
		self.lock.acquire()
		try:
			logging.debug("Lock acquired")
			returnval = dataArray
		finally:
			self.lock.release()
		return returnval

	def updateData(self, data):
		logging.debug("Waiting for lock")
		self.lock.acquire()
		try:
			logging.debug("Lock acquired")
			dataArray = data
		finally:
			self.lock.release()

def update_data(screendata, updateinterval, sources):
	lastupdate = 0
	while True:
		now = time.time()
		if now - lastupdate >= updateinterval:
			logging.debug("Performing update")
			newList = []
			for source in sources:
				data = source.getData()
				for item in data:
					newList.append(item)
			
			screendata.updateData(newList)
			lastupdate = time.time()

		else:
			logging.debug("Sleeping")
			time.sleep(0.5)

def display_data():
	pass


config = configparser.ConfigParser()
config.read('display.conf')
screendata = ScreenData()
bt = BinTracker('binschedule.json')
mo = MetOffice(config['MetOffice']['Key'],config['MetOffice']['LocationCode'])
sources = [bt,mo]
updateThread = threading.Thread(name="UpdateThread", target=update_data,args=(screendata,60,sources))
updateThread.start()

