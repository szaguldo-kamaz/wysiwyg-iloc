# WYSIWYG Indoor Localization
#   Gather pose/button information from VIVE system using libsurvive
#
# Author: David Vincze
#
# https://github.com/szaguldo-kamaz/
#

import pysurvive, sys
from WIL_LocDataBase import WILLocDataBase


class WILLocDataLibSurvive(WILLocDataBase):

    def __init__(self, roomsize, verbose=False):
        WILLocDataBase.__init__(self, roomsize, verbose);
        self.ctx = pysurvive.init();
        if self.ctx is None:
            print("WILLocDataLibSurvive: FATAL: Cannot init pysurvive context!");
            sys.exit(1);
        pysurvive.install_button_fn(self.ctx, self.button_func);
        pysurvive.install_pose_fn(self.ctx, self.pose_func);

    def __del__(self):
        pysurvive.close(self.ctx);

    def update(self):
        return pysurvive.poll(self.ctx);

    def add_tracker_by_serial(self, trackerserial):
        if trackerserial not in self.tracked_objects.keys():
            self.tracked_objects[trackerserial] = {'timecode':0, 'pose':None, 'button':0};
            self.all_tracked_objs_have_valid_pose = False;
            return self.WILTracker(trackerserial, self);

    def pose_func(self, obj, timecode, pose):
        trackerserial = obj.contents.serial_number.decode('utf8');
        if trackerserial not in self.tracked_objects.keys():
            self.tracked_objects[trackerserial] = {'timecode':timecode, 'pose':pose, 'button':0};
        else:
            self.tracked_objects[trackerserial]['timecode'] = timecode;
            self.tracked_objects[trackerserial]['pose'] = pose;

    def button_func(self, obj, eventtype, buttonid, axisids, axisvals):
        trackerserial = obj.contents.serial_number.decode('utf8');
        if trackerserial not in self.tracked_objects.keys():
            self.tracked_objects[trackerserial] = {'timecode':0, 'pose':[0]*7, 'button':0};
        else:
            if buttonid == 3:  # sys button on tracker
                if   eventtype == pysurvive.SURVIVE_INPUT_EVENT_BUTTON_UP:
                    self.tracked_objects[trackerserial]['button'] = 1;
                elif eventtype == pysurvive.SURVIVE_INPUT_EVENT_BUTTON_DOWN:
                    self.tracked_objects[trackerserial]['button'] = 0;
