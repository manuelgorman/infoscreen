from CoreLib import *
import vfdpos
import time

fac = vfdpos.WincorNixdorfDisplayFactory()
display = fac.get_vfd_pos()[0]

while True:
    display.clearscreen()
    display.poscur(1, 1)
    display.write_msg(CoreLib.padLine("==== COVID-19 ===="))
    time.sleep(0.5)
    display.clearscreen()
    display.poscur(2,1)
    display.write_msg(CoreLib.padLine("== REMAIN INDOORS =="))
    time.sleep(0.5)
