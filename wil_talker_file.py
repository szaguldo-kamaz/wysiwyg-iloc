# WYSIWYG Indoor Localization
# Sample code:
#   Gather and adjust pose information - then dump data into a file
#
# Author: David Vincze
#
# https://github.com/szaguldo-kamaz/
#

import time, sys, shutil, datetime
from wil_config  import wil_config
from WIL import WIL


# configuration

calibdata_filename = 'wil_calibparams-OK.txt';
dataout_orient_euler = False;
dataout_filename = 'wil_data_' + ('q', 'e')[dataout_orient_euler] + datetime.datetime.today().strftime("_%Y_%m_%d__%H-%m-%S") + '.csv';
datagatherinterval = 0.01;  # sec

### start ###

wilobj = WIL(wil_config.locdata_source, wil_config.playareapixels);

for trackername in wil_config.trackers.keys():
    wilobj.add_tracker(trackername, wil_config.trackers[trackername]['serial']);
    wilobj.trackers[trackername].set_rotaxis(wil_config.trackers[trackername]['rotaxis']);

# try to read previous calibration config data (set verbose so calibrate_from_file() will print actual values)
wilobj.set_verbose(True);

if wilobj.calibrate_from_file(calibdata_filename):
    print("Calibration data loaded from: %s"%(calibdata_filename));
else:
    print("Cannot load calibration data from: %s, using default values (no calibration)."%(calibdata_filename));

wilobj.set_verbose(False);


print("Waiting for all the tracked devices to be actually tracked...");

while not wilobj.all_poses_valid():
    if wilobj.update() != 0:
        print("WIL update error!");
        break

print("I see all the tracked devices.");

# preserve calibparams file
shutil.copy2(calibdata_filename, dataout_filename[:-4] + '__' + calibdata_filename);

dataout = open(dataout_filename, "w", newline="\n");
# format: timestamp, tracker serial, posedata

while True:

    if wilobj.update() != 0:
        print("WIL update error!");
        break

    for trackername in wilobj.get_tracker_names():
        trackerpos = wilobj.trackers[trackername].get_raw_position();
        if dataout_orient_euler:
            trackerorie = wilobj.trackers[trackername].get_raw_orientation_euler_degrees();
            dataout.write("%s,%s,%f,%f,%f,%f,%f,%f\r\n"%(time.time(), wilobj.trackers[trackername].serial, trackerpos[0], trackerpos[1], trackerpos[2], trackerorie[0], trackerorie[1], trackerorie[2]));
        else:
            trackeroriq = wilobj.trackers[trackername].get_raw_orientation_quat();
            dataout.write("%s,%s,%f,%f,%f,%f,%f,%f,%f\r\n"%(time.time(), wilobj.trackers[trackername].serial, trackerpos[0], trackerpos[1], trackerpos[2], trackeroriq[0], trackeroriq[1], trackeroriq[2], trackeroriq[3]));

    time.sleep(datagatherinterval);

dateout.close();
