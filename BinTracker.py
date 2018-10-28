import datetime
import json, logging
from CoreLib import CoreLib,DataSource

class BinTracker:
    """Class for displaying Gorgie Road bin information"""
    
    title = "Bin Collection"

    def __init__(self,file):
            fileH = open(file, "r")
            txt = fileH.read()
            self.binDict = json.loads(txt)
            fileH.close()
            self.dayOfWeek = self.binDict["dayofweek"]
            self.title = "Bin Collections"
            logging.debug("[BinTracker] Initialized")
            

    def next_weekday(self,date):
        """ Date: after which to find the next day. Weekday: int for which day you wish to find, 0=Monday, 6=Sunday"""
        days_ahead = self.dayOfWeek - date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return date + datetime.timedelta(days_ahead)
            
    def get_next_collection(self):
        currentMonth, currentDay = datetime.datetime.now().strftime("%m"), datetime.datetime.now().strftime("%d")
        next_wed = self.next_weekday(datetime.datetime.now())
        next_wed_day = next_wed.strftime("%d")
        next_wed_month = next_wed.strftime("%m")
        logging.debug("[+] Checking %s/%s" % (next_wed_day,next_wed_month))
        bins = []
        for binType in self.binDict["groups"][self.binDict[next_wed_month][next_wed_day]]:
            bins.append(self.binDict["bins"][binType])
            logging.debug("[~] " + self.binDict["bins"][binType])
        return bins

    def getData(self):
        data = self.get_next_collection()
        dataString = ""
        for collection in data:
            if data.index(collection) == len(data)-1:
                dataString += collection
            else:
                dataString += collection+", "

        return [[self.title, dataString]]



if __name__ == "__main__":
    print("[BinTracker] Running Standalone")
    bt = BinTracker("binschedule.json") 
    print(bt.get_next_collection())
    print(bt.next_weekday(datetime.datetime.now()))
    print (bt.getData())