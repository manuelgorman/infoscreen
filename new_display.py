from CoreLib import *
from BinTracker import BinTracker
from MetOffice import MetOffice
from Tautulli import TautulliAPI
import threading
import logging
import time
import vfdpos
logging.basicConfig(level=logging.INFO,
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
        self.display.poscur(1, 1)
        self.display.write_msg("Loading...!")
        bt = BinTracker('binschedule.json')
        mo = MetOffice(self.config['MetOffice']['Key'],
                       config['MetOffice']['LocationCode'])
        tt = TautulliAPI(self.config['Tautulli']
                         ['Key'], config['Tautulli']['Address'])
        #self.sources = [bt, mo, tt]
        self.sources = [mo, tt]

    def writeScreenData(self, lineArray):
        logging.debug("Waiting for ScreenLock")
        # Wait for lock on screen
        self.screenlock.acquire()
        try:
            while True: 
                try:
                    self.display.clearscreen()
                    logging.debug("ScreenLock acquired")
                    logging.info("LINE1: "+lineArray[0])
                    logging.info("LINE2: "+lineArray[1])
                    # Position cursor and write first line
                    self.display.poscur(1, 1)
                    self.display.write_msg(self.pad_line(lineArray[0]))

                    # Position cursor and write second line
                    self.display.poscur(2, 1)
                    if len(lineArray[1]) > 20:

                        string = lineArray[1]
                        first = True
                        while len(string) > 19:
                            self.display.poscur(2, 1)
                            self.display.write_msg(string[0:20])
                            string = string[1:]
                            if first:
                                time.sleep(
                                    int(self.config['App']['ScrollingWaitTime']))

                                first = False
                            else:
                                time.sleep(float(self.config['App']['ScrollInterval']))
                    else:
                        self.display.write_msg(self.pad_line(lineArray[1]))
                    break
                except usb.core.USBError:
                    logging.warn("Display write failed, trying again in 200ms")
                    time.sleep(0.2)
        finally:
            # Release lock on screen
            self.screenlock.release()

    def update_data(self):
        logging.info("Performing data update....")
        logging.debug("Waiting for lock")
        self.lock.acquire()
        try:
            logging.debug("Lock acquired")
            newList = []
            for source in self.sources:
                try:
                    data = source.getData()
                    for item in data:
                        logging.debug("Added: "+item[0])
                        newList.append(item)
                except:
                    pass

            self.dataArray = newList
        finally:
            self.lock.release()
            logging.info("Data update completed. Going back to sleep.")

    def update_data_loop(self):
        # when this is called, we have 'never' done an update
        lastupdate = 0
        while True:
            # what is now
            now = time.time()
            if now - lastupdate >= int(self.config['App']['DataRefreshInterval']):
                logging.debug("Performing update")

                # Get new data and add to array
                self.update_data()

                # note that this is the last time we ran an update
                lastupdate = time.time()

            else:
                logging.debug("Sleeping")
                time.sleep(0.5)

    def pad_line(self, line):
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
