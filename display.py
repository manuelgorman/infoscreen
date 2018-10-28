import sys, configparser, time, vfdpos, re, signal, math, logging
from MetOffice import MetOffice
from LothianBusTracker import LothianBusTracker
from PlexPy import PlexPyApi
from CurrencyLayer import CurrencyLayer
from BinTracker import BinTracker
from datetime import datetime
from usb.core import USBError as USBError


class PeacefulKill:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGTERM, self.exit_peacefully)
        signal.signal(signal.SIGINT, self.exit_peacefully)

    def exit_peacefully(self, signum, frame):
        self.kill_now = True

class DisplayWorker:
    """Main class for display. Just call mainLoop in a loop"""

    
    
    
    def __init__(self, killer, config):
        self.killer = killer
        self.mo = MetOffice(config['MetOffice']['Key'],config['MetOffice']['LocationCode'])
        self.lb = LothianBusTracker(config['LothianBuses']['Key'])
        self.stopsToCity = [36232687,36232624]
        self.stopsFromCity = [36236528]
        self.pp = PlexPyApi(config['Tautulli']['Key'], config['Tautulli']['Address'])

        self.cl = CurrencyLayer(config['CurrencyLayer']['Key'], config['CurrencyLayer']['Address'])

        self.bintracker = BinTracker('binschedule.json')

        self.line_array = []
        self.email_regex = re.compile('(^.*)@.*',re.IGNORECASE)

        self.update_interval = 60 #Minimum time between data refreshes (seconds)

        self.scroll_interval = config['App']['ScrollInterval']
        self.scroll_wait_time = config['App']['ScrollWaitTime']
        self.wait_time = config['App']['WaitTime']
        print('[DisplayWorker] Data Sources Initialized')
        
        fac = vfdpos.WincorNixdorfDisplayFactory()
        self.display = fac.get_vfd_pos()[0]
        self.display.clearscreen()
        self.display.poscur(1,1)
        print('[DisplayWorker] Screen Initialized')

        
    def mainLoop(self):
        if self.needs_update:
            self.updateData()

        for info in self.line_array:
            self.writeLines(info)
            if self.killer.kill_now:
                break
            time.sleep(self.wait_time)

        time_since_update = datetime.now() - self.last_update
        print('[DisplayWorker] Last update: %s seconds ago' % (time_since_update.seconds))
        if time_since_update.seconds > self.update_interval:
            self.needs_update = True
        
    def updateData(self):
        update_text = ['Updating Data!','Met Office']
        print('[DisplayWorker] Refreshing data feeds')
        self.writeLines(update_text, line1Index=4)
        weatherData = self.mo.getWeather()
        print(weatherData)
        self.display.poscur(2,1)
        self.display.write_msg("Lothian Buses 1".rjust(20," "))
        busData = self.lb.getUNextBuses(self.stopsToCity)
        self.display.poscur(2,1)
        self.display.write_msg("Lothian Buses 2".rjust(20," "))
        afcBusData = self.lb.getUNextBuses(self.stopsFromCity)
        self.display.poscur(2,1)
        self.display.write_msg("Plex Views".rjust(20," "))
        plexData = self.pp.topTenUsers()
        self.display.poscur(2,1)
        self.display.write_msg("Now Playing".rjust(20," "))
        nowPlayingData = self.pp.nowPlaying()
        self.display.poscur(2,1)
        self.display.write_msg("Bitcoin Value".rjust(20," "))
        currencyData = self.cl.BTCtoUSDGBP()

        #for datasource in enabled_sources....
        
        self.last_update = datetime.now()
        self.needs_update = False

        self.line_array = []
        self.line_array.append(self.prepNowPlayingData(nowPlayingData))
        self.line_array.append(self.prepPlexData(plexData))
        self.line_array.append(self.prepBinData())
        self.line_array.append(self.prepBusData(busData, 'to'))
        self.line_array.append(self.prepBusData(afcBusData, 'from'))
        self.line_array.append(self.prepWeatherData(weatherData[0]['Rep'][0]))
        self.line_array.append(self.prepWeatherData(weatherData[0]['Rep'][1]))
        self.line_array.append(self.prepCurrencyData(currencyData))
        
        
        
    def writeLines(self, lineArray, line1Index=1, line2Index=1):
        print('[DisplayWorker] Writing to screen')
        print('[DisplayWorker] Line 1: %s' % lineArray[0])
        print('[DisplayWorker] Line 2: %s' % lineArray[1])
        self.display.clearscreen()
        self.display.poscur(1,line1Index)
        self.display.write_msg(lineArray[0])
        self.display.poscur(2,line2Index)
        if len(lineArray[1])> 20:
            string = lineArray[1]
            first = True
            while len(string) > 19:
                self.display.poscur(2,1)
                self.display.write_msg(string[0:20])
                string=string[1:]
                if first:
                    time.sleep(self.scroll_wait_time)
                    first = False
                else:
                    if self.killer.kill_now:
                        break
                    time.sleep(self.scroll_interval)
        else:            
            self.display.write_msg(lineArray[1])

    def prepBusData(self, busData, toFrom):
        print('[DisplayWorker] Processing bus data')
        bus_string=""
        for bus in busData:
            if busData[bus][0] != 'N' and busData[bus][0] < 60:
                bus_string += bus+":"+str(busData[bus][0])+"m  "
        line1 = "Buses "+toFrom+" city"
        linediff = math.floor((20 - len(line1))/2)
        line1 = (" " * linediff)+line1
        return [line1, bus_string]

    def prepPlexData(self, plexData):
        print('[DisplayWorker] Processing Plex data')
        plex_string = ""
        for user in plexData:
            user_name = self.stripEmail(user['name'])
            plex_string += " %s (%s) " % (user_name, user['count'])
        line1 = "Plex Plays"
        linediff = math.floor((20 - len(line1))/2)
        line1 = (" "*linediff)+line1
        return [line1,plex_string]

    def prepWeatherData(self, weatherData):
        print('[DisplayWorker] Processing weather data')
        sufx = "\u00b0C "
        if "FDm" in weatherData:
            weather_string = weatherData["FDm"]+sufx
            title = "Today's Weather"
        else:
            weather_string = weatherData["FNm"]+sufx
            title = "Tonight's Weather"
        weather_string += MetOffice.WeatherCodes[weatherData["W"]]

        return [self.padLine(title), weather_string]

    def prepNowPlayingData(self, nowPlayingData):
        print('[DisplayWorker] Processing Now Playing data')
        np_string = ""
        line1 = self.padLine("Now Playing (%s)" % (nowPlayingData['stream_count']))
        for playingItem in nowPlayingData['sessions']:
            if playingItem['media_type'] == 'episode':
                title = "%s S%sE%s" % (playingItem['grandparent_title'],playingItem['parent_media_index'],playingItem['media_index'])
            elif playingItem['media_type'] == 'movie':
                title = playingItem['title']
            elif playingItem['media_type'] == 'track':
                title = "%s/%s" % (playingItem['grandparent_title'],playingItem['title'])
            if len(nowPlayingData['sessions']) > 1:
                seperator = " |"
            else:
                seperator = ""
            np_string += "%s - %s (%s%%)%s " % (self.stripEmail(playingItem['user']),title,playingItem['progress_percent'],seperator)

        return [line1,np_string]
    
    def prepCurrencyData(self, data):
        print("[DisplayWorker] Processing Bitcoin Data")
        dollar = "$%s" % data[0]
        pound =  "£%s" % data[1]
        return [self.padLine("1 BTC"),(dollar.ljust(10," ")+pound.rjust(10," "))]
        
        
        
    def padLine(self, line):
        linediff = math.floor((20 - len(line))/2)
        return (" "*linediff)+line

    def stripEmail(self, username):
        if "@" in username:
            return self.email_regex.match(username).group(1)
        else:
            return username

    def prepBinData(self):
        nextBins = self.bintracker.get_next_collection()
        binStr = ""
        for bin in nextBins:
            b = bin + " "
            binStr += b
        nextBinDay = self.bintracker.next_weekday(datetime.now())
        daysDiff = nextBinDay - datetime.now()
        countdown = daysDiff.days
        return [self.padLine("%s days to bins" % countdown),binStr]

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('display.conf')
    killer = PeacefulKill()
    dispW = DisplayWorker(killer, config)
    dispW.updateData()
    while True:
        try:
            dispW.mainLoop()
            if killer.kill_now:
                break
        except KeyboardInterrupt:
            break
        except USBError:
            print('[DisplayWorker] Aww she dead, USB Error') 
            exc_type, value, exc_traceback = sys.exc_info()
            print(exc_type, value, exc_traceback)
            time.sleep(10)
            #sys.exit(-1)
        except:
            print('[DisplayWorker] Unhandled exception caught, waiting 10 seconds and restarting main loop')
            time.sleep(10)

    print('[DisplayWorker] Caught kill signal. Terminating.')
    sys.exit(0)
