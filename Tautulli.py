import requests
import logging
from CoreLib import CoreLib, DataSource


class TautulliAPI(DataSource):

    def __init__(self, token, url):
        self.apiToken = token
        self.requestUrl = url
        print("[PlexPy] Initialized")

    def makeRequest(self, function, data=None):
        logging.debug("[PlexPy(MakeRequest)] Preparing request")

        params = {"apikey": self.apiToken, "cmd": function}

        if data != None:
            params = {**data, **params}

        logging.debug("[PlexPy(MakeRequest,%s)] %s" %
                      (self.requestUrl, function))

        r = requests.get(self.requestUrl, params=params)

        return r.json()["response"]

    def topTenUsers(self):
        resp = self.makeRequest(
            "get_plays_by_top_10_users", data={"time_range": 1000})
        stats = []

        i = 0
        for user in resp['data']['categories']:
            total = 0
            for lib in resp['data']['series']:
                total += lib['data'][i]
            stats.append([user, total])
            i += 1
        ret = []
        for obj in stats:
            ret.append({"name": obj[0], "count": obj[1]})

        return ret

    def nowPlaying(self):
        resp = self.makeRequest("get_activity")
        return resp['data']

    @staticmethod
    def prepTopTen(PlexData):
        plex_string = ""
        for user in PlexData:
            user_name = CoreLib.stripEmail(user['name'])
            plex_string += " %s (%s) " % (user_name, user['count'])

        return plex_string

    @staticmethod
    def prepNowPlaying(NowPlayingData):
        np_string = ""
        for playingItem in NowPlayingData['sessions']:
            if playingItem['media_type'] == 'episode':
                title = "%s S%sE%s" % (
                    playingItem['grandparent_title'], playingItem['parent_media_index'], playingItem['media_index'])
            elif playingItem['media_type'] == 'movie':
                title = playingItem['title']
            elif playingItem['media_type'] == 'track':
                title = "%s/%s" % (playingItem['grandparent_title'],
                                   playingItem['title'])
            if len(NowPlayingData['sessions']) > 1:
                seperator = " |"
            else:
                seperator = ""
            np_string += "%s - %s (%s%%)%s " % (CoreLib.stripEmail(
                playingItem['user']), title, playingItem['progress_percent'], seperator)

        return np_string

    def getData(self):
        logging.debug("[~] Fetching new data")

        try:
            nowPlayingData = self.nowPlaying()
            line1 = "Now Playing [%s]" % nowPlayingData['stream_count']
            line2 = TautulliAPI.prepNowPlaying(nowPlayingData)
        except Exception as e:
            logging.warn(CoreLib.GetErrorMessage(e))
            line1 = "Now Playing [ERR]"
            line2 = CoreLib.GetErrorMessage(e)
        finally:
            nowPlayingLines = [line1, line2]

        try:
            topTen = self.topTenUsers()
            line1 = "Plex - Top 10"
            line2 = TautulliAPI.prepTopTen(topTen)
        except Exception as e:
            logging.warn(CoreLib.GetErrorMessage(e))
            line1 = "Plex - Top 10 [ERR]"
            line2 = CoreLib.GetErrorMessage(e)
        finally:
            topTenLines = [line1, line2]

        lines = [nowPlayingLines, topTenLines]
        return lines


if __name__ == "__main__":
    print("[PlexPy] Running Standalone")
    ppy = TautulliAPI("38ba0c43f33e480d8d4a761f72d72a59", "https://tautulli.manuelgorman.co.uk/api/v2")
    print(ppy.getData())

    #ppy = PlexPyApi("xxxxx","http://10.0.0.100:8000/api/v2")
# print(ppy.makeRequest("get_plays_by_top_10_users"))
    # print(ppy.topTenUsers())
    # print(ppy.nowPlaying())

    #active = ppy.makeRequest("get_activity")["data"]["sessions"]

    # for watch_user in active:
    # print(watch_user["friendly_name"] +":", watch_user["title"])
