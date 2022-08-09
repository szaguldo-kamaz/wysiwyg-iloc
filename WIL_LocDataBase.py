# WYSIWYG Indoor Localization
#   Gather pose/button information from a localization system
#
# Author: David Vincze
#
# https://github.com/szaguldo-kamaz/
#

import math, sys


class WILLocDataBase:

    class WILTracker:

        def __init__(self, trackerserial, wldbobj):
            self.serial  = trackerserial;
            self.timecode = 0;
            self.pose = None;
            self.pose_euler_deg = None;
            self.button = 0;
            self.rotaxis = 0;
            self.wldbobj = wldbobj;
            self.xoffset_tracker = 0.0;
            self.yoffset_tracker = 0.0;
            self.zoffset_tracker = 0.0;
            self.rotoffset_trackerself_tracker = 0.0;

        def get_raw_position(self):
            return self.wldbobj.get_raw_position(self.serial);

        def get_raw_orientation_quat(self):
            return self.wldbobj.get_raw_orientation_quat(self.serial);

        def get_raw_orientation_euler_radians(self):
            return self.wldbobj.get_raw_orientation_euler_radians(self.serial);

        def get_raw_orientation_euler_degrees(self):
            return self.wldbobj.get_raw_orientation_euler_degrees(self.serial);

        def get_position(self):
            return self.wldbobj.get_position(self.serial);

        def get_position_pixel(self):
            return self.wldbobj.get_position_pixel(self.serial);

        def get_orientation_radians(self):
            return self.wldbobj.get_orientation_radians(self.serial);

        def get_orientation_degrees(self):
            return self.wldbobj.get_orientation_degrees(self.serial);

        def was_button_pressed(self):
            return self.wldbobj.was_button_pressed(self.serial);

        def set_rotaxis(self, rotaxisno):
            return self.wldbobj.set_tracker_rotaxis_by_serial(self.serial, rotaxisno);

        def calibrate_tracker(self, xoffset_tracker, yoffset_tracker, zoffset_tracker, rotoffset_trackerself_tracker):
            self.xoffset_tracker = xoffset_tracker;
            self.yoffset_tracker = yoffset_tracker;
            self.zoffset_tracker = zoffset_tracker;
            self.rotoffset_trackerself_tracker = rotoffset_trackerself_tracker;

        def get_calibration_data_tracker(self):
            return [ self.xoffset_tracker, self.yoffset_tracker, self.zoffset_tracker, self.rotoffset_trackerself_tracker ];


    def __init__(self, roomsize):
        self.roomsize = roomsize;
        self.roomcenter = [ roomsize[0] / 2, roomsize[1] / 2 ];
        self.tracked_objects = {};
        self.all_tracked_objs_have_valid_pose = False;
        self.xoffset_world = 0.0;
        self.yoffset_world = 0.0;
        self.zoffset_world = 0.0;
        self.rotoffset_world = 0.0;
        self.rotoffset_trackerself = 0.0;
        self.pixelratio = 200;
        self.swapx = False;
        self.swapy = False;
        self.reverse_rotdir = False;
        self.verbose = False;

    def set_verbose(self, verbose):
        self.verbose = verbose;

    def polar2rect(self, r, theta):
        return [ r*math.cos(theta), r*math.sin(theta) ]

    def rect2polar(self, x, y):
        r = math.sqrt(x**2 + y**2);
        theta = math.atan2(y,x);
        return [ r, theta ]

    def quattoeuler(self, q):
        try:
            # q = [ w, x, y, z ]
            t2 = 2 * (q[0] * q[2] - q[3] * q[1]);
            if t2 > 1.0:
                if t2 > 1.01:
                    print("T2over: ", t2);
                t2 = 1.0;
            if t2 < -1.0:
                if t2 < -1.01:
                    print("T2below: ", t2);
                t2 = -1.0;

            euler = [ math.atan2(2 * (q[0] * q[1] + q[2] * q[3]), 1 - 2 * (q[1] * q[1] + q[2] * q[2])),
                      t2,
                      math.atan2(2 * (q[0] * q[3] + q[1] * q[2]), 1 - 2 * (q[2] * q[2] + q[3] * q[3])) ];
            return euler
        except:
            print("DEBUG BAD quat: ", q);
            return False

    def set_swapx(self, swapx):
        self.swapx = swapx;

    def set_swapy(self, swapy):
        self.swapy = swapy;

    def set_reverserotdir(self, reverse_rotdir):
        self.reverse_rotdir = reverserotdir;

    def calibrate_world(self, xoffset_world, yoffset_world, zoffset_world, rotoffset_world, rotoffset_trackerself, pixelratio, swapx, swapy, reverse_rotdir):
        self.xoffset_world = xoffset_world;
        self.yoffset_world = yoffset_world;
        self.zoffset_world = zoffset_world;
        self.rotoffset_world = rotoffset_world;
        self.rotoffset_trackerself = rotoffset_trackerself;
        self.pixelratio = pixelratio;
        self.swapx = swapx;
        self.swapy = swapy;
        self.reverse_rotdir = reverse_rotdir;

    def calibrate_from_file(self, calibdata_filename):
        # try to read previous calibration config data
        try:
            calibdatafile = open(calibdata_filename,"r");
            calibdata = calibdatafile.readlines();
            calibdatafile.close();
            if len(calibdata) != 1:
                print("Something is wrong with the data format %s! Should be only 1 line! Exiting..."%(calibdata_filename));
                sys.exit(1);

            xoffset_world = float(calibdata[0].split()[1]);
            yoffset_world = float(calibdata[0].split()[3]);
            zoffset_world = float(calibdata[0].split()[5]);
            rotoffset_world = math.radians(float(calibdata[0].split()[7]));
            rotoffset_trackerself   = math.radians(float(calibdata[0].split()[9]));
            pixelratio = int(calibdata[0].split()[11]);
            swapx = bool(int(calibdata[0].split()[13]));
            swapy = bool(int(calibdata[0].split()[15]));
            reverse_rotdir = bool(int(calibdata[0].split()[17]));

            if self.verbose:
                print("Setting these calibration parameters: offx: %s, offy: %s, offz: %s, worrot: %s/%s objrot: %s/%s pixrat: %d swapx: %d swapy: %d revrot: %d"%
                    (self.xoffset_world, self.yoffset_world, self.zoffset_world, self.rotoffset_world, math.degrees(self.rotoffset_world),
                     self.rotoffset_trackerself, math.degrees(self.rotoffset_trackerself), self.pixelratio, self.swapx, self.swapy, self.reverse_rotdir));

            self.calibrate_world(xoffset_world, yoffset_world, zoffset_world, rotoffset_world, rotoffset_trackerself, pixelratio, swapx, swapy, reverse_rotdir);

            return True

        except:

            return False

    def get_calibration_data_world(self):
        return [ self.xoffset_world, self.yoffset_world, self.zoffset_world, self.rotoffset_world, self.rotoffset_trackerself, self.pixelratio, self.swapx, self.swapy, self.reverse_rotdir ]

    def all_poses_valid(self):
        self.all_tracked_objs_have_valid_pose = True;
        for trackobj in self.tracked_objects.keys():
            if self.tracked_objects[trackobj].pose == None:
                self.all_tracked_objs_have_valid_pose = False;
                break
        return self.all_tracked_objs_have_valid_pose

    def get_raw_position(self, tracker_serial):
        return self.tracked_objects[tracker_serial].pose[0:3];

    def get_raw_orientation_quat(self, tracker_serial):
        return self.tracked_objects[tracker_serial].pose[3:7];

    def get_raw_orientation_euler_radians(self, tracker_serial):
        if self.tracked_objects[tracker_serial].pose_euler_deg != None:
            return [ math.radians(deg) for deg in self.tracked_objects[tracker_serial].pose_euler_deg[3:6] ];
        else:
            return self.quattoeuler(self.tracked_objects[tracker_serial].pose[3:7]);

    def get_raw_orientation_euler_degrees(self, tracker_serial):
        if self.tracked_objects[tracker_serial].pose_euler_deg != None:
            return self.tracked_objects[tracker_serial].pose_euler_deg[3:6];
        else:
            return [ math.degrees(radian) for radian in self.quattoeuler(self.tracked_objects[tracker_serial].pose[3:7]) ];

    def get_position(self, tracker_serial):
        rawpos = self.get_raw_position(tracker_serial);
        if self.swapx:
            rawpos[0] = -rawpos[0];
        if self.swapy:
            rawpos[1] = -rawpos[1];
        [r, th] = self.rect2polar(rawpos[0], rawpos[1]);
#        [r, th] = self.rect2polar(offsetpos[0], offsetpos[1]);
        newth = th - self.rotoffset_world;
        rotatedpos = self.polar2rect(r, newth);
        offrotpos = [ rotatedpos[0] + self.xoffset_world, rotatedpos[1] + self.yoffset_world, rawpos[2] + self.zoffset_world ];
        return offrotpos

    def get_position_pixel(self, tracker_serial):
        trackpos = self.get_position(tracker_serial);
        return [ trackpos[0] * self.pixelratio, trackpos[1] * self.pixelratio ];

    def get_orientation_radians(self, tracker_serial):
        rot_radians = self.get_raw_orientation_euler_radians(tracker_serial);
        # rot angle -180-+180 -> 0-360
        angle = rot_radians[self.tracked_objects[tracker_serial].rotaxis] + math.pi - self.rotoffset_trackerself;
        if angle >= 2*math.pi:
            angle = robotangle - 2*math.pi;
        if angle < 0:
            angle = 2*math.pi + angle;
        if self.reverse_rotdir:
            angle = 2*math.pi - angle;
        return angle

    def get_orientation_degrees(self, tracker_serial):
        return math.degrees(self.get_orientation_radians(tracker_serial));

    def was_button_pressed(self, tracker_serial):
        if self.tracked_objects[tracker_serial].button == 1:
            self.tracked_objects[tracker_serial].button = 0;
            return True
        else:
            return False

    def set_tracker_rotaxis_by_serial(self, tracker_serial, rotaxisno):
        self.tracked_objects[tracker_serial].rotaxis = rotaxisno;

    # ROS and SteamVR overrides this
    def add_tracker_by_serial(self, trackerserial):
        if trackerserial not in self.tracked_objects.keys():
            self.tracked_objects[trackerserial] = self.WILTracker(trackerserial, self);
            self.all_tracked_objs_have_valid_pose = False;
            return self.tracked_objects[trackerserial];
