# WYSIWYG Indoor Localization
#   WILRemoteUDP - construct and send UDP packet with adjusted pose data
#
# Author: David Vincze
#
# https://github.com/szaguldo-kamaz/
#

import socket, struct


class WILRemoteUDP:

    def __init__(self, destip, destport):
        self.destip = destip;
        self.destport = destport;
        self.sock_trackerdata = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
        self.packetno_trackerdata = -1;

    def __del__(self):
        self.sock_trackerdata.close();

    def send(self, tracker):
        trackerpos    = tracker.get_raw_position();
        trackeroriq   = tracker.get_raw_orientation_quat();
        trackerbutton = tracker.was_button_pressed();
        trackerserial = tracker.serial;
        self.send_rawdata(trackerpos, trackeroriq, trackerbutton, trackerserial);

    def send_rawdata(self, trackerpos, trackeroriq, trackerbutton, trackerserial):

        self.packetno_trackerdata = self.packetno_trackerdata + 1;
        if self.packetno_trackerdata == 65536:
            self.packetno_trackerdata = 0;

        packetno_trackerdata_hi = self.packetno_trackerdata >> 8;
        packetno_trackerdata_lo = self.packetno_trackerdata & 0xFF;

        data = bytearray(72);
        data[ 0: 1] = [ packetno_trackerdata_hi, packetno_trackerdata_lo ];
        data[ 2:14] = bytes(trackerserial, 'ascii');
        data[14:22] = struct.pack("d", trackerpos[0]);
        data[22:30] = struct.pack("d", trackerpos[1]);
        data[30:38] = struct.pack("d", trackerpos[2]);
        data[38:46] = struct.pack("d", trackeroriq[0]);
        data[46:54] = struct.pack("d", trackeroriq[1]);
        data[54:62] = struct.pack("d", trackeroriq[2]);
        data[62:70] = struct.pack("d", trackeroriq[3]);
        data[71]    = trackerbutton;

        self.sock_trackerdata.sendto(bytes(data), (self.destip, self.destport));
