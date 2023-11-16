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
        self.destip = destip
        self.destport = destport
        self.sock_trackerdata = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.packetno_trackerdata = -1

    def __del__(self):
        self.sock_trackerdata.close()

    def send(self, tracker):
        trackerpos    = tracker.get_raw_position()
        trackeroriq   = tracker.get_raw_orientation_quat()
        trackerbutton = tracker.was_button_pressed( ["system", "trigger"] )
        trackerserial = tracker.serial
        self.send_rawdata(trackerpos, trackeroriq, trackerbutton, trackerserial)

    def send_rawdata(self, trackerpos, trackeroriq, trackerbutton, trackerserial):

        self.packetno_trackerdata = self.packetno_trackerdata + 1
        if self.packetno_trackerdata == 65536:
            self.packetno_trackerdata = 0

        packetno_trackerdata_hi = self.packetno_trackerdata >> 8
        packetno_trackerdata_lo = self.packetno_trackerdata & 0xFF

        data = bytearray(72)
        data[ 0: 1] = [ packetno_trackerdata_hi, packetno_trackerdata_lo ]
        data[ 2:14] = bytes(trackerserial, 'ascii')
        data[14:70] = struct.pack("ddddddd", trackerpos[0], trackerpos[1], trackerpos[2], trackeroriq[0], trackeroriq[1], trackeroriq[2], trackeroriq[3])
        data[71]    = trackerbutton

        self.sock_trackerdata.sendto(bytes(data), (self.destip, self.destport))
