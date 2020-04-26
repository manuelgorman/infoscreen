import requests
from datetime import datetime
from CoreLib import *
import logging

class MetOffice(DataSource):
	"""Class for retrieving Metoffice weather data"""
	WeatherCodes = {
		"NA":	"Not available",
		"0":	"Clear",
		"1":	"Sunny",
		"2":	"Partly cloudy",
		"3":	"Partly cloudy",
		"5":	"Mist",
		"6":	"Fog",
		"7":	"Cloudy",
		"8":	"Overcast",
		"9":	"Light rain showers",
		"10":	"Light rain showers",
		"11":	"Drizzle",
		"12":	"Light rain",
		"13":	"Heavy rain showers",
		"14":	"Heavy rain showers",
		"15":	"Heavy rain",
		"16":	"Sleet showers",
		"17":	"Sleet showers",
		"18":	"Sleet",
		"19":	"Hail showers",
		"20":	"Hail showers",
		"21":	"Hail",
		"22":	"Light snow showers",
		"23":	"Light snow showers",
		"24":	"Light snow",
		"25":	"Heavy snow showers",
		"26":	"Heavy snow showers",
		"27":	"Heavy snow",
		"28":	"Thunder showers",
		"29":	"Thunder showers",
		"30":	"Thunder"
		}
	#TODO: Add checking for if data needs updated
	def __init__(self,token,locationCode):
			self.apiToken = token
			self.requestUrl = "http://datapoint.metoffice.gov.uk/public/data"
			self.latestData = {}
			self.locationCode = locationCode
			logging.debug("[MetOffice] Initialized")
			
	def makeRequest(self, endpoint, data):
		"""Makes request to MetOffice at specified endpoint with url params data"""

		logging.debug("[MetOffice(MakeRequest)] Preparing request")
		fullUrl = self.requestUrl + endpoint
		mainparams = {"key":self.apiToken}

		if data != None:
			payload = CoreLib.merge_two_dicts(data, mainparams)
		else:
			payload = mainparams
		logging.debug("[MetOffice(MakeRequest)] Executing query: %s PARAMS: %s" % (fullUrl,payload))
		r = requests.get(fullUrl,params=payload)
		return r.json()

	def process_data(self,weatherData):
		sufx = "\u00b0C "
		if "F" in weatherData:
			weather_string = weatherData["F"]+sufx
		elif "FDm" in weatherData:
			weather_string = weatherData["FDm"]+sufx
		else:
			weather_string = weatherData["FNm"]+sufx
		weather_string += MetOffice.WeatherCodes[weatherData["W"]]
		return weather_string

	def getWeather(self):
		wxData = self.makeRequest("/val/wxfcs/all/json/"+str(self.locationCode),{"res":"daily"})
		return wxData["SiteRep"]["DV"]["Location"]["Period"]
		#print(wxData)

	def getData(self): 
		wxData = self.makeRequest("/val/wxfcs/all/json/"+str(self.locationCode),{"res":"daily"})
		dataWeWant = wxData["SiteRep"]["DV"]["Location"]["Period"][0]['Rep']
		curData = self.makeRequest("/val/wxfcs/all/json/"+str(self.locationCode), {"res":"3hourly"})
		currentWeather = self.process_data( 
			curData["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][0]
		)
		dayWeather = self.process_data(dataWeWant[0])
		nightWeather = self.process_data(dataWeWant[1])
		return [["Weather Now", currentWeather], ["Today's Weather", dayWeather], ["Tonight's Weather", nightWeather]]
	
if __name__ == "__main__":
	print("[MetOffice] Running Standalone")
	mo = MetOffice("APIKEY","351872")

	x = mo.getData()
	print(x)

