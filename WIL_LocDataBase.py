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
            self.wldbobj = wldbobj;

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


    def __init__(self, roomsize):
        self.roomsize = roomsize;
        self.roomcenter = [ roomsize[0] / 2, roomsize[1] / 2 ];
        self.tracked_objects = {};
        self.all_tracked_objs_have_valid_pose = False;
        self.xoffset = 0.0;
        self.yoffset = 0.0;
        self.zoffset = 0.0;
        self.rotoffset_world = 0.0;
        self.rotoffset_obj = 0.0;
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
            euler = [ math.atan2(2 * (q[0] * q[1] + q[2] * q[3]), 1 - 2 * (q[1] * q[1] + q[2] * q[2])),
                      math.asin (2 * (q[0] * q[2] - q[3] * q[1])),
                      math.atan2(2 * (q[0] * q[3] + q[1] * q[2]), 1 - 2 * (q[2] * q[2] + q[3] * q[3])) ];
            return euler
        except:
            print("DEBUG BAD quat: ", q);
            t2 = 2 * (q[0] * q[2] - q[3] * q[1]);
#            max(min(t2, 1.0), -1.0);
            print("T2: ", t2);
            return False


    def set_swapx(self, swapx):
        self.swapx = swapx;

    def set_swapy(self, swapy):
        self.swapy = swapy;

    def set_reverserotdir(self, reverse_rotdir):
        self.reverse_rotdir = reverserotdir;

    def calibrate(self, xoffset, yoffset, zoffset, rotoffset_world, rotoffset_obj, pixelratio, swapx, swapy, reverse_rotdir):
        self.xoffset = xoffset;
        self.yoffset = yoffset;
        self.zoffset = zoffset;
        self.rotoffset_world = rotoffset_world;
        self.rotoffset_obj = rotoffset_obj;
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
            self.xoffset = float(calibdata[0].split()[1]);
            self.yoffset = float(calibdata[0].split()[3]);
            self.zoffset = float(calibdata[0].split()[5]);
            self.rotoffset_world = math.radians(float(calibdata[0].split()[7]));
            self.rotoffset_obj   = math.radians(float(calibdata[0].split()[9]));
            self.pixelratio = int(calibdata[0].split()[11]);
            self.swapx = bool(int(calibdata[0].split()[13]));
            self.swapy = bool(int(calibdata[0].split()[15]));
            self.reverse_rotdir = bool(int(calibdata[0].split()[17]));
            if self.verbose:
                print("Setting these calibration parameters: offx: %s, offy: %s, offz: %s, worrot: %s/%s objrot: %s/%s pixrat: %d swapx: %d swapy: %d revrot: %d"%
                    (self.xoffset, self.yoffset, self.zoffset, self.rotoffset_world, math.degrees(self.rotoffset_world),
                     self.rotoffset_obj, math.degrees(self.rotoffset_obj), self.pixelratio, self.swapx, self.swapy, self.reverse_rotdir));
            return True
        except:
            return False

    def get_calibration_data(self):
        return [ self.xoffset, self.yoffset, self.zoffset, self.rotoffset_world, self.rotoffset_obj, self.pixelratio, self.swapx, self.swapy, self.reverse_rotdir ]

    def all_poses_valid(self):
        self.all_tracked_objs_have_valid_pose = True;
        for trackobj in self.tracked_objects.keys():
            if self.tracked_objects[trackobj]['pose'] == None:
                self.all_tracked_objs_have_valid_pose = False;
                break
        return self.all_tracked_objs_have_valid_pose

    def get_raw_position(self, tracker_serial):
        return self.tracked_objects[tracker_serial]['pose'][0:3];

    def get_raw_orientation_quat(self, tracker_serial):
        return self.tracked_objects[tracker_serial]['pose'][3:8];

    def get_raw_orientation_euler_radians(self, tracker_serial):
        return self.quattoeuler(self.tracked_objects[tracker_serial]['pose'][3:8]);

    def get_raw_orientation_euler_degrees(self, tracker_serial):
        return [ math.degrees(radian) for radian in self.quattoeuler(self.tracked_objects[tracker_serial]['pose'][3:8]) ];

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
        offrotpos = [ rotatedpos[0] + self.xoffset, rotatedpos[1] + self.yoffset, rawpos[2] + self.zoffset ];
        return offrotpos

    def get_position_pixel(self, tracker_serial):
        trackpos = self.get_position(tracker_serial);
        return [ trackpos[0] * self.pixelratio, trackpos[1] * self.pixelratio ];

    def get_orientation_radians(self, tracker_serial):
        rot_radians = self.quattoeuler(self.tracked_objects[tracker_serial]['pose'][3:8]);
        # rot angle -180-+180 -> 0-360
        angle = rot_radians[self.tracked_objects[tracker_serial]['rotaxis']] + math.pi - self.rotoffset_obj;
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
        if self.tracked_objects[tracker_serial]['button'] == 1:
            self.tracked_objects[tracker_serial]['button'] = 0;
            return True
        else:
            return False

    def set_tracker_rotaxis_by_serial(self, tracker_serial, rotaxisno):
        self.tracked_objects[tracker_serial]['rotaxis'] = rotaxisno;
