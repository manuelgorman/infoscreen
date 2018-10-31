import requests

class PlexPyApi:

	def __init__(self,token,url):
		self.apiToken = token
		self.requestUrl = url
		print("[PlexPy] Initialized")

	def makeRequest(self,function,data=None):
		print("[PlexPy(MakeRequest)] Preparing request")

		params = {"apikey": self.apiToken, "cmd": function}

		if data != None:
			params = {**data, **params}

		print("[PlexPy(MakeRequest,%s)] %s" % (self.requestUrl,function))

		r = requests.get(self.requestUrl,params=params)

		return r.json()["response"]

	def topTenUsers(self):
		resp = self.makeRequest("get_plays_by_top_10_users",data={"time_range":1000})
		stats = {}

		i = 0
		for user in resp['data']['categories']:
			total = 0
			for lib in resp['data']['series']:
				total += lib['data'][i]
			stats[user] = total
			i += 1
		ret = []
		for obj in stats:
			ret.append({"name":obj, "count":stats[obj]})

		return ret

	def nowPlaying(self):
		resp = self.makeRequest("get_activity")
		return resp['data']

	

if __name__ == "__main__":
	print("[PlexPy] Running Standalone")
	ppy = PlexPyApi("xxxxx","http://10.0.0.100:8000/api/v2")
##    print(ppy.makeRequest("get_plays_by_top_10_users"))
	#print(ppy.topTenUsers())
	print(ppy.nowPlaying())

	#active = ppy.makeRequest("get_activity")["data"]["sessions"]

	#for watch_user in active:
	   # print(watch_user["friendly_name"] +":", watch_user["title"])
