# WYSIWYG Indoor Localization
# Sample code:
#   Gather and adjust pose information - then dump data into a file
#
# Author: David Vincze
#
# https://github.com/szaguldo-kamaz/
#

import time, sys, shutil, datetime
from WIL import WIL


# configuration

calibdata_filename = 'wil_calibparams.txt'
dataout_orient_euler = False
dataout_filename = 'wil_data_' + ('q', 'e')[dataout_orient_euler] + datetime.datetime.today().strftime("_%Y_%m_%d__%H-%M-%S") + '.csv'
datagatherinterval = 0.01  # sec

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

# preserve calibparams file
shutil.copy2(calibdata_filename, dataout_filename[:-4] + '__' + calibdata_filename)

dataout = open(dataout_filename, "w", newline="\n")
# format: timestamp, tracker serial, posedata

while True:

    if wilobj.update() != 0:
        print("WIL update error!")
        break

    for trackername in wilobj.get_tracker_names():
        if wilobj.trackers[trackername].trackertype == 2:  # don't save PTR, those can/should be recalculated
            continue
        trackerpos = wilobj.trackers[trackername].get_raw_position()
        if dataout_orient_euler:
            trackerorie = wilobj.trackers[trackername].get_raw_orientation_euler_degrees()
            dataout.write("%s,%s,%f,%f,%f,%f,%f,%f\r\n"%(time.time(), wilobj.trackers[trackername].serial, trackerpos[0], trackerpos[1], trackerpos[2], trackerorie[0], trackerorie[1], trackerorie[2]))
        else:
            trackeroriq = wilobj.trackers[trackername].get_raw_orientation_quat()
            dataout.write("%s,%s,%f,%f,%f,%f,%f,%f,%f\r\n"%(time.time(), wilobj.trackers[trackername].serial, trackerpos[0], trackerpos[1], trackerpos[2], trackeroriq[0], trackeroriq[1], trackeroriq[2], trackeroriq[3]))

        dataout.write("%s,*%s,%d,%d,%d,%f,%d,%d,%f,%f\r\n"%(time.time(), wilobj.trackers[trackername].serial, wilobj.trackers[trackername].buttons['system'], wilobj.trackers[trackername].buttons['menu'], wilobj.trackers[trackername].buttons['grip'], wilobj.trackers[trackername].buttons['trigger'], wilobj.trackers[trackername].buttons['trackpad_press'], wilobj.trackers[trackername].buttons['trackpad_touch'], wilobj.trackers[trackername].buttons['trackpad_x'], wilobj.trackers[trackername].buttons['trackpad_y']))

    time.sleep(datagatherinterval)

dataout.close()
