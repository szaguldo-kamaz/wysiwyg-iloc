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
            return self.pose[0:3];

        def get_raw_orientation_quat(self):
            return self.pose[3:7];

        def get_raw_orientation_euler_radians(self):
            if self.pose_euler_deg != None:
                return [ math.radians(deg) for deg in self.pose_euler_deg[3:6] ];
            else:
                return self.wldbobj.quattoeuler(self.pose[3:7]);

        def get_raw_orientation_euler_degrees(self):
            if self.pose_euler_deg != None:
                return self.pose_euler_deg[3:6];
            else:
                return [ math.degrees(radian) for radian in self.wldbobj.quattoeuler(self.pose[3:7]) ];

        def get_position(self):
            rawpos = self.get_raw_position();
            if self.wldbobj.swapx:
                rawpos[0] = -rawpos[0];
            if self.wldbobj.swapy:
                rawpos[1] = -rawpos[1];
            [r, th] = self.wldbobj.rect2polar(rawpos[0], rawpos[1]);
#            [r, th] = self.wldbobj.rect2polar(offsetpos[0], offsetpos[1]);
            newth = th - self.wldbobj.rotoffset_world;
            rotatedpos = self.wldbobj.polar2rect(r, newth);
            offrotpos = [ rotatedpos[0] + self.wldbobj.xoffset_world + self.xoffset_tracker,
                          rotatedpos[1] + self.wldbobj.yoffset_world + self.yoffset_tracker,
                          rawpos[2]     + self.wldbobj.zoffset_world + self.zoffset_tracker ];

            return offrotpos

        def get_position_pixel(self):
            trackpos = self.get_position();
            return [ trackpos[0] * self.wldbobj.pixelratio, trackpos[1] * self.wldbobj.pixelratio ];

        def get_orientation_radians(self):
            rot_radians = self.get_raw_orientation_euler_radians();
            # rot angle -180-+180 -> 0-360
            angle = rot_radians[self.rotaxis] + math.pi - self.wldbobj.rotoffset_trackerself_world - self.rotoffset_trackerself_tracker;
            if angle >= 2*math.pi:
                angle -= 2*math.pi;
            if angle < 0:
                angle += 2*math.pi;
            if self.wldbobj.reverse_rotdir:
                angle = 2*math.pi - angle;
            return angle

        def get_orientation_degrees(self):
            return math.degrees(self.get_orientation_radians());

        def was_button_pressed(self):
            if self.button == 1:
                self.button = 0;
                return True
            else:
                return False

        def set_rotaxis(self, rotaxisno):
            self.rotaxis = rotaxisno;

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
        self.rotoffset_trackerself_world = 0.0;
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

    def calibrate_world(self, xoffset_world, yoffset_world, zoffset_world, rotoffset_world, rotoffset_trackerself_world, pixelratio, swapx, swapy, reverse_rotdir):
        self.xoffset_world = xoffset_world;
        self.yoffset_world = yoffset_world;
        self.zoffset_world = zoffset_world;
        self.rotoffset_world = rotoffset_world;
        self.rotoffset_trackerself_world = rotoffset_trackerself_world;
        self.pixelratio = pixelratio;
        self.swapx = swapx;
        self.swapy = swapy;
        self.reverse_rotdir = reverse_rotdir;

    def calibrate_from_file(self, calibdata_filename):
        # try to read previous calibration config data
        try:  # todo better exception handling...
            calibdatafile = open(calibdata_filename,"r");
            calibdata = calibdatafile.readlines();
            calibdatafile.close();
            if len(calibdata) == 0:
                print("Empty calibration config file?");
                sys.exit(1);

            linezerosplit = calibdata[0].split();

            gwcount = 0;
            for goodkeyword in [ "wxoff", "wyoff", "wzoff", "worioff", "worioff_t", "pixrat", "swapx", "swapy", "revrot" ]:
                if linezerosplit[gwcount] != goodkeyword + ":":
                    print("Bad calibration config file: line 0, keyword %d should be %s!"%(gwcount/2, goodkeyword));
                    sys.exit(1);
                gwcount += 2;

            xoffset_world = float(linezerosplit[1]);
            yoffset_world = float(linezerosplit[3]);
            zoffset_world = float(linezerosplit[5]);
            rotoffset_world = math.radians(float(linezerosplit[7]));
            rotoffset_trackerself_world = math.radians(float(linezerosplit[9]));
            pixelratio = int(linezerosplit[11]);
            swapx = bool(int(linezerosplit[13]));
            swapy = bool(int(linezerosplit[15]));
            reverse_rotdir = bool(int(linezerosplit[17]));

            if self.verbose:
                print("Setting these calibration parameters: offx: %s, offy: %s, offz: %s, worrot: %s/%s objrot: %s/%s pixrat: %d swapx: %d swapy: %d revrot: %d"%
                    (xoffset_world, yoffset_world, zoffset_world, rotoffset_world, math.degrees(rotoffset_world),
                     rotoffset_trackerself_world, math.degrees(rotoffset_trackerself_world), pixelratio, swapx, swapy, reverse_rotdir));

            self.calibrate_world(xoffset_world, yoffset_world, zoffset_world, rotoffset_world, rotoffset_trackerself_world, pixelratio, swapx, swapy, reverse_rotdir);

            if len(calibdata) > 1:
                currlinecount = 0;
                for configline in calibdata[1:]:
                    currlinecount += 1;
                    trackeradjustlinesplit = configline.split();
                    gwcount = 0;
                    for goodkeyword in [ "tracker", "xoff", "yoff", "zoff", "orioff_t" ]:
                        if trackeradjustlinesplit[gwcount] != goodkeyword + ":":
                            print("Bad calibration config file: line %d, keyword %d should be %s!"%(currlinecount, gwcount/2, goodkeyword));
                            sys.exit(1);
                        gwcount += 2;

                    trackerserial = trackeradjustlinesplit[1];
                    if trackerserial not in self.tracked_objects.keys():
                        print("Bad calibration config file: line %d: no such tracker listed in wilconfig: %s!"%(currlinecount, trackeradjustlinesplit[1]));
                        sys.exit(1);

                    xoffset_tracker = float(trackeradjustlinesplit[3]);
                    yoffset_tracker = float(trackeradjustlinesplit[5]);
                    zoffset_tracker = float(trackeradjustlinesplit[7]);
                    rotoffset_trackerself_tracker = math.radians(float(trackeradjustlinesplit[9]));

                    if self.verbose:
                        print("Setting these calibration parameters for tracker %s: offx: %s, offy: %s, offz: %s, objrot: %s/%s"%
                            (trackerserial, xoffset_tracker, yoffset_tracker, zoffset_tracker, rotoffset_trackerself_tracker, math.degrees(rotoffset_trackerself_tracker)) );

                    self.tracked_objects[trackerserial].calibrate_tracker(xoffset_tracker, yoffset_tracker, zoffset_tracker, rotoffset_trackerself_tracker);

            return True

        except:

            return False

    def get_calibration_data_world(self):
        return [ self.xoffset_world, self.yoffset_world, self.zoffset_world, self.rotoffset_world, self.rotoffset_trackerself_world, self.pixelratio, self.swapx, self.swapy, self.reverse_rotdir ]

    def all_poses_valid(self):
        self.all_tracked_objs_have_valid_pose = True;
        for trackobj in self.tracked_objects.keys():
            if self.tracked_objects[trackobj].pose == None:
                self.all_tracked_objs_have_valid_pose = False;
                break
        return self.all_tracked_objs_have_valid_pose

    # ROS and SteamVR overrides this
    def add_tracker_by_serial(self, trackerserial):
        if trackerserial not in self.tracked_objects.keys():
            self.tracked_objects[trackerserial] = self.WILTracker(trackerserial, self);
            self.all_tracked_objs_have_valid_pose = False;
            return self.tracked_objects[trackerserial];
