import requests
from hashlib import md5
from datetime import datetime

class LothianBusTracker:
	"""Class for retrieving and displaying next bus info for Lothian Buses"""
	

	def __init__(self,token):
			self.apiToken = token
			self.requestUrl = "http://ws.mybustracker.co.uk"
			print("[BusTracker] Initialized")
			
	def makeRequest(self, functionName, args=None):
			"""Makes request to LB """

			#Build and hash API token
			print("[BusTracker(MakeRequest)] Computing MD5 token")
			date = datetime.now().strftime("%Y%m%d%H")
			tokenString = self.apiToken+date
			md5Token = md5(bytes(tokenString, encoding='utf-8')).hexdigest()
			print("[BusTracker(MakeRequest)] Timestamp:", date)
			


			#Send request
			mainArgs = {"module":"json", "key":md5Token, "function":functionName}
			if args != None:
				payload = {**args, **mainArgs}
			else:
				payload = mainArgs
				
			print("[BusTracker(MakeRequest,%s)] %s | %s" % (self.requestUrl,functionName,args))
			r = requests.post(self.requestUrl, data=payload)
			return r.json()
			
			
	def getNextBuses(self,stopcodes):
		"""Takes a list of stopcodes and returns a dictionary of services and their arrival times"""
		stops = {}
		i = 1
		for stopcode in stopcodes:
			print("[BusTracker(NextBuses)] Added stop:", str(stopcode))
			stops["stopId"+str(i)] = stopcode
			i += 1
		print("[BusTracker(NextBuses)] Requesting Data...")
		returned_info = self.makeRequest("getBusTimes",args=stops)
		buses = {}
		print("[BusTracker(NextBuses)] Processing Data...")
		for service in returned_info["busTimes"]:
			buses[service["mnemoService"]] = []
			for individual_bus in service["timeDatas"]:
				buses[service["mnemoService"]].append(individual_bus["minutes"])                                             
		return buses

	def getUNextBuses(self,stopcodes):
		"""Takes a list of stopcodes and returns a unique dictionary of services and their arrival times"""
		stops = {}
		i = 1
		for stopcode in stopcodes:
			print("[BusTracker(UNextBuses)] Added stop:", str(stopcode))
			stops["stopId"+str(i)] = stopcode
			i += 1
		print("[BusTracker(UNextBuses)] Requesting Data...")
		returned_info = self.makeRequest("getBusTimes",args=stops)
		buses = {}
		print("[BusTracker(UNextBuses)] Processing Data...")
		for service in returned_info["busTimes"]:
			buses[service["mnemoService"]] = []
			buses[service["mnemoService"]].append(service["timeDatas"][0]["minutes"])                                             
		return buses

if __name__ == "__main__":
	print("[BusTracker] Running Standalone")
	lb = LothianBusTracker("xxxxxxx")
	buses = lb.getUNextBuses([36232687,36232624])
	#json = lb.makeRequest("getBusTimes",args={"stopId1":36232687})
	#print(json) 
	print(buses)
