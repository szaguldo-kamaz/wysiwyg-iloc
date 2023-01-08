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
import time, struct, sys


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


    def update_poses_from_src(self):
        return self.update_poses_from_src_timebase(time.time());


    def update_poses_from_src_timebase(self, currenttime):

        if self.eofreached:
            return 0

        while (currenttime - self.start_real_timestamp) > self.elapsed_filetime:
            trackerserial = self.dataline[1];
            if trackerserial[0] == '*':
                buttonline = True;
                trackerserial = trackerserial[1:];
            else:
                buttonline = False;
            if trackerserial not in self.tracked_objects.keys():
                sys.stderr.writelines("WIL_LocDataFile: WARNING: Unrecognized tracker: %s\n"%(trackerserial));
            else:
                if buttonline:
                    self.tracked_objects[trackerserial].button['system'] = bool(self.dataline[2]);
                    self.tracked_objects[trackerserial].button['menu'] = bool(self.dataline[3]);
                    self.tracked_objects[trackerserial].button['grip'] = bool(self.dataline[4]);
                    self.tracked_objects[trackerserial].button['trigger'] = float(self.dataline[5]);
                    self.tracked_objects[trackerserial].button['trackpad_press'] = bool(self.dataline[6]);
                    self.tracked_objects[trackerserial].button['trackpad_touch'] = bool(self.dataline[7]);
                    self.tracked_objects[trackerserial].button['trackpad_x'] = float(self.dataline[8]);
                    self.tracked_objects[trackerserial].button['trackpad_y'] = float(self.dataline[9]);
                else:
                    if self.datatype == 2:
                        self.tracked_objects[trackerserial].pose = list(map(float, self.dataline[2:5])) + [0.0]*4;
                        self.tracked_objects[trackerserial].pose_euler_deg = list(map(float, self.dataline[2:]));
                    else:
                        self.tracked_objects[trackerserial].pose = list(map(float, self.dataline[2:]));
                        self.tracked_objects[trackerserial].pose_euler_deg = list(map(float, self.dataline[2:5])) + [0.0]*3;

            self.dataline = self.datafile.readline().strip().split(',');
            if self.dataline == ['']:
                self.eofreached = True;
                sys.stderr.writelines("WIL_LocDataFile: EOF reached. No more pose updates!\n");
                break
            else:
                self.dataline_timestamp = float(self.dataline[0]);
                self.elapsed_filetime = self.dataline_timestamp - self.start_file_timestamp;

        return 0
