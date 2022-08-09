# WYSIWYG Indoor Localization
#   Gather pose/button information from previously saved pose data
#   (with wil_talker_file.py)
#   best practice is to use a symlink to point "wil_data_input.csv" to the actual data file you want to use
#
# Author: David Vincze
#
# https://github.com/szaguldo-kamaz/
#

from WIL_LocDataBase import WILLocDataBase
import time, struct


class WILLocDataFile(WILLocDataBase):

    def __init__(self, roomsize):
        WILLocDataBase.__init__(self, roomsize);
        self.datafile = open("wil_data_input.csv", "r");  # symlink
        self.dataline = self.datafile.readline().strip().split(',');
        if   len(self.dataline) == 9:  # quaternions
            self.datatype = 1;
        elif len(self.dataline) == 8:  # euler degrees
            self.datatype = 2;
        else:
            raise ValueError
        self.eofreached = False;
        self.start_file_timestamp = float(self.dataline[0]);
        self.dataline_timestamp = self.start_file_timestamp;
        self.start_real_timestamp = time.time();
        self.elapsed_filetime = self.dataline_timestamp - self.start_file_timestamp;


    def __del__(self):
        self.datafile.close();


    def update(self):

        if self.eofreached:
            return 0

        while (time.time() - self.start_real_timestamp) > self.elapsed_filetime:
            trackerserial = self.dataline[1];
            if self.datatype == 2:
                self.tracked_objects[trackerserial].pose = list(map(float, self.dataline[2:5])) + [0.0]*4;
                self.tracked_objects[trackerserial].pose_euler_deg = list(map(float, self.dataline[2:]));
            else:
                self.tracked_objects[trackerserial].pose = list(map(float, self.dataline[2:]));
                self.tracked_objects[trackerserial].pose_euler_deg = list(map(float, self.dataline[2:5])) + [0.0]*3;
            self.dataline = self.datafile.readline().strip().split(',');
            if self.dataline == ['']:
                self.eofreached = True;
                print("WIL_LocDataFile: EOF reached. No more pose updates!");
                break
            else:
                self.dataline_timestamp = float(self.dataline[0]);
                self.elapsed_filetime = self.dataline_timestamp - self.start_file_timestamp;

        return 0
