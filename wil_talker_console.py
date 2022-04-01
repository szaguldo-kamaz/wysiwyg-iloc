# WYSIWYG Indoor Localization
# Sample code:
#   Gather and adjust pose information - then just print it on the console
#
# Author: David Vincze
#
# https://github.com/szaguldo-kamaz/
#

import time, sys
from wil_config  import wil_config
from WIL import WIL


# configuration

calibdata_filename = 'wil_calibparams-OK.txt';

### start ###

wilobj = WIL(wil_config.locdata_source, wil_config.playareapixels);

for trackername in wil_config.trackers.keys():
    wilobj.add_tracker(trackername, wil_config.trackers[trackername]['serial']);
    wilobj.trackers[trackername].set_rotaxis(wil_config.trackers[trackername]['rotaxis']);

# try to read previous calibration config data (set verbose so calibrate_from_file() will print actual values)
wilobj.set_verbose(True);

if wilobj.calibrate_from_file(calibdata_filename):
    [ xoffset, yoffset, zoffset, orientoffset_world, orientoffset_obj, pixelratio, swapx, swapy, reverse_rotdir ] = wilobj.get_calibration_data();
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

while True:

    if wilobj.update() != 0:
        print("WIL update error!");
        break

    for trackername in wilobj.get_tracker_names():
        trackerpos  = wilobj.trackers[trackername].get_raw_position();
        trackeroriq = wilobj.trackers[trackername].get_raw_orientation_quat();
        print("%s(%s) %s %s"%(trackername, wilobj.trackers[trackername].serial, trackerpos, trackeroriq));

    time.sleep(0.01);

sock_trackerinfo.close();
