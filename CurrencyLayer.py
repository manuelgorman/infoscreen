import requests
from datetime import datetime

class CurrencyLayer:

    def __init__(self,token,url):
        self.apiToken = token
        self.requestUrl = url
        self.last_update = datetime(1996,1,1)
        print("[CurrencyLayer] Initialized")

    def makeRequest(self,data=None):
        print("[CurrencyLayer(MakeRequest)] Preparing request")

        params = {"access_key": self.apiToken}

        if data != None:
            params = {**data, **params}

        print("[CurrencyLayer(MakeRequest,%s)] %s" % (self.requestUrl,data))

        r = requests.get(self.requestUrl,params=params)
        vals = r.json()["quotes"]
        
        USDvalue = 1/vals["USDBTC"]
        GBPvalue = USDvalue * vals["USDGBP"]
    
        return [round(USDvalue,2),round(GBPvalue,2)]

    def BTCtoUSDGBP(self):
        print("[CurrencyLayer(BTCtoUSDGBP)] Fetching quotes")
        
        time_since_update = datetime.now() - self.last_update
        if time_since_update.total_seconds() > 3660:
            print("[CurrencyLayer(BTCtoUSDGBP)] More than 1 hour since last update. Grabbing...")
            currencies = "GBP,BTC"
            source = "USD"
            params = {"currencies": currencies,
                      "source":     source}
            
            self.values = self.makeRequest(data=params)
            self.last_update = datetime.now()
        else:
            print("[CurrencyLayer(BTCtoUSDGBP)] Last update %s seconds ago. No update required" % (time_since_update.total_seconds()))
        return(self.values)
    

if __name__ == "__main__":
    print("[CurrencyLayer] Running Standalone")
    ppy = CurrencyLayer("xxxxx","http://apilayer.net/api/live")
    q = ppy.BTCtoUSDGBP()
    print("1BTC:")
    print("$%s" % (q[0]))
    print("£%s" % (q[1]))
##  
