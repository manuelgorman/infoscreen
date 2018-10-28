from CoreLib import *
from BinTracker import BinTracker
from MetOffice import MetOffice

bt = BinTracker('binschedule.json')
mo = MetOffice("xxxxx","353668")

services = [bt,mo]
displayarr = []
for service in services:
    data = service.getData()
    for item in data:
        displayarr.append(item)

for thing in displayarr:
    print("L1: " + thing[0])
    print("L2: " +thing[1])