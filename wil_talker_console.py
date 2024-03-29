# WYSIWYG Indoor Localization
# Sample code:
#   Gather and adjust pose information - then just print it on the console
#
# Author: David Vincze
#
# https://github.com/szaguldo-kamaz/
#

import time, sys
from WIL import WIL


## configuration ##

calibdata_filename = 'wil_calibparams.txt'

### start ###

if len(sys.argv) > 1:
    wilobj = WIL(sys.argv[1])
else:
    wilobj = WIL()

# try to read previous calibration config data (set verbose so calibrate_from_file() will print actual values)
wilobj.set_verbose(True)

if wilobj.calibrate_from_file(calibdata_filename):
    print(f"Calibration data loaded from: {calibdata_filename}")
else:
    print(f"Cannot load calibration data from: {calibdata_filename}, using default values (no calibration).")

wilobj.set_verbose(False)


print("Waiting for all the tracked devices to be actually tracked...")

while not wilobj.all_poses_valid():
    if wilobj.update() != 0:
        print("WIL update error!")
        break

print("I see all the tracked devices.")

while True:

    if wilobj.update() != 0:
        print("WIL update error!")
        break

    for trackername in wilobj.get_tracker_names():
        trackerpos  = wilobj.trackers[trackername].get_raw_position()
        trackeroriq = wilobj.trackers[trackername].get_raw_orientation_quat()
        trackerorie = wilobj.trackers[trackername].get_raw_orientation_euler_degrees()
        print(f"{trackername}({wilobj.trackers[trackername].serial}) {trackerpos} {trackeroriq} {trackerorie}")

    time.sleep(0.01)

sock_trackerinfo.close()
