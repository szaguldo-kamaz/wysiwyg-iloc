# WYSIWYG Indoor Localization
#   Gather pose/button information from incoming UDP packets
#   (possibly from a remote system doing the actual localization data gathering)
#
# Author: David Vincze
#
# https://github.com/szaguldo-kamaz/
#

from WIL_LocDataBase import WILLocDataBase
import socket, select, struct


class WILLocDataRemoteUDP(WILLocDataBase):

    def __init__(self, roomsize):
        WILLocDataBase.__init__(self, roomsize);
        bindip = "0.0.0.0";
        portno_trackerinfo = 60003;
        self.sock_trackerinfo = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
        self.sock_trackerinfo.bind((bindip, portno_trackerinfo));
        self.last_packetno = -1;


    def __del__(self):
        self.sock_trackerinfo.close();


    def update(self):
        sockreadable, _, _ = select.select([self.sock_trackerinfo], [], [], 0);
        while len(sockreadable) > 0:
            if self.sock_trackerinfo in sockreadable:
                data, addr = self.sock_trackerinfo.recvfrom(72);
                if len(data) < 72:
                    print("WILLocDataRemoteUDP.update: Dropped too small (%d bytes data) packet! Contents: -%s-"%(len(data), data));
                    return

                packetno_recv = (data[0] << 8) + data[1];
                if packetno_recv > self.last_packetno:
                    if packetno_recv == 65535:
                        self.last_packetno = 0;
                    else:
                        self.last_packetno = packetno_recv;
                    trackerserial = data[2:14];
                    trackerserial = trackerserial.decode('ascii');
                    trackerpose   = [ struct.unpack("d", data[14:22])[0],
                                      struct.unpack("d", data[22:30])[0],
                                      struct.unpack("d", data[30:38])[0],
                                      struct.unpack("d", data[38:46])[0],
                                      struct.unpack("d", data[46:54])[0],
                                      struct.unpack("d", data[54:62])[0],
                                      struct.unpack("d", data[62:70])[0] ];
                    trackerbutton = data[71];

                    self.tracked_objects[trackerserial].pose = trackerpose;
                    if trackerbutton == 1:  # button is a trigger, sets a state, which is cleared elsewhere (was_button_pressed)
                        self.tracked_objects[trackerserial].button = 1;

            sockreadable, _, _ = select.select([self.sock_trackerinfo], [], [], 0);

        return 0
