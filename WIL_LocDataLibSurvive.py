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

    def __init__(self, roomsize):
        WILLocDataBase.__init__(self, roomsize);
        self.ctx = pysurvive.init();
        if self.ctx is None:
            sys.stderr.writelines("WILLocDataLibSurvive: FATAL: Cannot init pysurvive context!\n");
            sys.exit(1);
        pysurvive.install_button_fn(self.ctx, self.button_func);
        pysurvive.install_pose_fn(self.ctx, self.pose_func);

    def __del__(self):
        pysurvive.close(self.ctx);

    def update_poses_from_src(self):
        return pysurvive.poll(self.ctx);

    def pose_func(self, obj, timecode, pose):
        trackerserial = obj.contents.serial_number.decode('utf8');
        if trackerserial not in self.tracked_objects.keys():
            self.add_tracker_by_serial(trackerserial);
        self.tracked_objects[trackerserial].timecode = timecode;
        self.tracked_objects[trackerserial].pose = pose;

    def button_func(self, obj, eventtype, buttonid, axisids, axisvals):
        trackerserial = obj.contents.serial_number.decode('utf8');
        if trackerserial not in self.tracked_objects.keys():
            self.add_tracker_by_serial(trackerserial);
#            self.tracked_objects[trackerserial].pose = [0]*7;
        else:
            if buttonid == 3:  # sys button on tracker
                if   eventtype == pysurvive.SURVIVE_INPUT_EVENT_BUTTON_UP:
                    self.tracked_objects[trackerserial].buttons['system'] = True;
                elif eventtype == pysurvive.SURVIVE_INPUT_EVENT_BUTTON_DOWN:
                    self.tracked_objects[trackerserial].buttons['system'] = False;
