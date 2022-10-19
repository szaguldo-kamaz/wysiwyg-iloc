# WYSIWYG Indoor Localization
#   Gather pose/button information from localization system - then send it to WILLocDataRemoteUDP (probably to another node)
#
# Author: David Vincze
#
# https://github.com/szaguldo-kamaz/
#

import socket, time, sys, struct
from WIL           import WIL
from WIL_RemoteUDP import WILRemoteUDP


# configuration

destip = "127.0.0.1";
destport_trackerdata = 60003;

### start ###

if len(sys.argv) > 1:
    wilobj = WIL(sys.argv[1]);
else:
    wilobj = WIL();

if wilobj.config.locdata_source == wilobj.config.LOCDATA_SOURCE_REMOTEUDP:
    print("RemoteUDP to RemoteUDP makes no sense. Exiting.")
    sys.exit(1);

wilobj.calibrate_world(0.0, 0.0, 0.0,  0.0, 0.0,  0.0, 0.0,  0.0, 0.0,  0, 0, 0,  0, 0, 0);

print("Waiting for all the tracked devices to be actually tracked...");
while not wilobj.all_poses_valid():
    if wilobj.update() != 0:
        print("WIL update error!");
        break

print("I see all the tracked devices.");

wrudp = WILRemoteUDP(destip, destport_trackerdata);

while True:

    if wilobj.update() != 0:
        print("WIL update error!");
        break

    for trackername in wilobj.get_tracker_names():
        wrudp.send(wilobj.trackers[trackername]);

    time.sleep(0.01);
