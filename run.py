from new_display import ScreenData
import configparser, threading, logging

# Read in our config
config = configparser.ConfigParser()
config.read('display.conf')

# Initialize the ScreenData object
screendata = ScreenData(config)

updateThread = threading.Thread(name="UpdateThread", target=screendata.update_data_loop)
updateThread.start()
logging.debug("Started UpdateThread")
displayThread = threading.Thread(name="DisplayThread", target=screendata.display_data_loop)
displayThread.start()
logging.debug("Started DisplayThread")