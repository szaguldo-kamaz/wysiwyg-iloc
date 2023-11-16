# WYSIWYG Indoor Localization
#
# Author: David Vincze
#
# https://github.com/szaguldo-kamaz/
#

import struct, socket
from wil_config    import wil_config
from WIL_RemoteUDP import WILRemoteUDP


destip = "127.0.0.1"
destport_trackerdata = 60003

sampleposedata = (
    [-4.0512, -0.9123, -2.0132,  0.198, 0.821, 0.88, 0.34],
    [ 0.2441,  1.8238,  1.0112,  0.201, 0.152, 0.03, 0.22],
    [ 1.1419,  2.9232,  1.0011,  0.610, 0.321, 0.92, 0.71],
    [ 2.9124,  3.4234,  1.0104,  0.012, 0.351, 0.02, 0.32]
)

wrudp = WILRemoteUDP(destip, destport_trackerdata)
sampleno = 0

for trackername in wil_config.trackers.keys():
    wrudp.send_rawdata(sampleposedata[sampleno][0:3], sampleposedata[sampleno][3:7], 0, wil_config.trackers[trackername]['serial'])
    sampleno += 1
