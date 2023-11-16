# WYSIWYG Indoor Localization
#   Gather pose/button information from VIVE system using SteamVR+OpenVR+triad_openvr
#
# Author: David Vincze
#
# https://github.com/szaguldo-kamaz/
#

import sys, math
import triad_openvr.triad_openvr
from WIL_LocDataBase import WILLocDataBase


class WILLocDataSteamVR(WILLocDataBase):

    def __init__(self, roomsize):
        WILLocDataBase.__init__(self, roomsize)
        self.wil_triadopenvr = triad_openvr.triad_openvr.triad_openvr()
        self.wil_triadopenvr.print_discovered_objects()
        self.devname_to_serial = {}
        self.serial_to_devname = {}
        self.available_objects = []
        for device in self.wil_triadopenvr.devices:
            trackerserial = self.wil_triadopenvr.devices[device].get_serial()
            if trackerserial != "Null Serial Number":
                self.available_objects.append(trackerserial)
                self.devname_to_serial[device] = trackerserial
                self.serial_to_devname[trackerserial] = device
        if len(self.available_objects) == 0:
            sys.stderr.writelines("WILLocDataSteamVR: FATAL: No trackable devices were detected! Exit.\n")
            sys.exit(1)  # should be an exception, maybe later..
        if self.verbose:
            print("\nBe sure to check that all your trackers were detected! They won't be added later on!\n")


    def __del__(self):
        pass


    def update_poses_from_src(self):

        for trackerserial in self.tracked_objects.keys():

            # "pointer" tracker
            if self.tracked_objects[trackerserial].trackertype == 2:
                continue

            # this is only for VIVE Controllers
            buttons = self.wil_triadopenvr.devices[self.serial_to_devname[trackerserial]].get_controller_inputs()
            self.tracked_objects[trackerserial].buttons['trigger'] = buttons['trigger']
            self.tracked_objects[trackerserial].buttons['menu'] = buttons['menu_button']
            self.tracked_objects[trackerserial].buttons['trackpad_press'] = buttons['trackpad_pressed']
            self.tracked_objects[trackerserial].buttons['grip'] = buttons['grip_button']
            self.tracked_objects[trackerserial].buttons['trackpad_touch'] = buttons['trackpad_touched']
            self.tracked_objects[trackerserial].buttons['trackpad_x'] = buttons['trackpad_x']
            self.tracked_objects[trackerserial].buttons['trackpad_y'] = buttons['trackpad_y']

#            pose_euler = self.wil_triadopenvr.devices[self.serial_to_devname[trackerserial]].get_pose_euler()
#            if pose_euler != None:
#                [x, y, z, orx, orz, ory] = pose_euler
#                self.tracked_objects[trackerserial].pose_euler_deg = [x, z, y, orx, orz, ory]

            try:  # sometimes get_pose fails, with math errors (divby0, etc.)...
                posequat = self.wil_triadopenvr.devices[self.serial_to_devname[trackerserial]].get_pose_quaternion()
            except:
                posequat = None  # sometimes get_pose also gives None

            if posequat != None:
                [x, y, z, qw, qx, qy, qz] = posequat
                self.tracked_objects[trackerserial].pose = [x, z, y, qw, qx, qy, qz]
                self.tracked_objects[trackerserial].pose_euler_deg = [x, z, y] + list(map(math.degrees, self.quattoeuler([qw, qx, qy, qz])))
#                self.tracked_objects[trackerserial].timecode = time.time()

        return 0


    def add_tracker_by_serial(self, trackerserial):

        if trackerserial not in self.available_objects:
            sys.stderr.writelines("WILLocDataSteamVR: FATAL: Tracker with serial %s not found! Check SteamVR?\n"%(trackerserial))
            sys.exit(0)
        if trackerserial not in self.tracked_objects.keys():
            self.tracked_objects[trackerserial] = self.WILTracker(trackerserial, self)
            return self.tracked_objects[trackerserial]
        else:
            sys.stderr.writelines("WILLocDataSteamVR: WARN: Tracker with serial %s already added!\n"%(trackerserial))
