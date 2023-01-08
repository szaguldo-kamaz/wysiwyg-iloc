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
            self.serial = trackerserial;
            self.timecode = 0;
            self.pose = None;
            self.pose_euler_deg = None;
            self.button = 0;
            self.yawaxis   = 0;
            self.pitchaxis = 1;
            self.rollaxis  = 2;
            self.wldbobj = wldbobj;
            self.xoffset_tracker = 0.0;
            self.yoffset_tracker = 0.0;
            self.zoffset_tracker = 0.0;
            self.yawoffset_trackerself_tracker   = 0.0;
            self.pitchoffset_trackerself_tracker = 0.0;
            self.rolloffset_trackerself_tracker  = 0.0;

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
            newth = th - self.wldbobj.yawoffset_world;
            rotatedpos = self.wldbobj.polar2rect(r, newth);
            offrotpos = [ rotatedpos[0] + self.wldbobj.xoffset_world + self.xoffset_tracker,
                          rotatedpos[1] + self.wldbobj.yoffset_world + self.yoffset_tracker,
                          rawpos[2]     + self.wldbobj.zoffset_world + self.zoffset_tracker ];

            return offrotpos

        def get_position_pixel(self):
            trackpos = self.get_position();
            return [ trackpos[0] * self.wldbobj.pixelratio, trackpos[1] * self.wldbobj.pixelratio ];

        def get_orientation_radians(self, whichaxis, offset_trackerself_world, offset_trackerself_tracker, reversedir):
            orientation_radians = self.get_raw_orientation_euler_radians();
            # angle -180-+180 -> 0-360
            angle = orientation_radians[whichaxis] + math.pi - offset_trackerself_world - offset_trackerself_tracker;
            if angle >= 2*math.pi:
                angle -= 2*math.pi;
            if angle < 0:
                angle += 2*math.pi;
            if reversedir:
                angle = 2*math.pi - angle;
            return angle

        def get_yaw_radians(self):
            return self.get_orientation_radians(self.yawaxis, self.wldbobj.yawoffset_trackerself_world, self.yawoffset_trackerself_tracker, self.wldbobj.reverse_yawdir);

        def get_yaw_degrees(self):
            return math.degrees(self.get_yaw_radians());

        def get_pitch_radians(self):
            return self.get_orientation_radians(self.pitchaxis, self.wldbobj.pitchoffset_trackerself_world, self.pitchoffset_trackerself_tracker, self.wldbobj.reverse_pitchdir);

        def get_pitch_degrees(self):
            return math.degrees(self.get_pitch_radians());

        def get_roll_radians(self):
            return self.get_orientation_radians(self.rollaxis, self.wldbobj.rolloffset_trackerself_world, self.rolloffset_trackerself_tracker, self.wldbobj.reverse_rolldir);

        def get_roll_degrees(self):
            return math.degrees(self.get_roll_radians());

        def was_button_pressed(self):
            if self.button == 1:
                self.button = 0;
                return True
            else:
                return False

        def set_yawaxis(self, yawaxisno):
            self.yawaxis = yawaxisno;

        def set_pitchaxis(self, pitchaxisno):
            self.pitchaxis = pitchaxisno;

        def set_rollaxis(self, rollaxisno):
            self.rollaxis = rollaxisno;

        def calibrate_tracker(self, xoffset_tracker, yoffset_tracker, zoffset_tracker, yawoffset_trackerself_tracker, pitchoffset_trackerself_tracker, rolloffset_trackerself_tracker):
            self.xoffset_tracker = xoffset_tracker;
            self.yoffset_tracker = yoffset_tracker;
            self.zoffset_tracker = zoffset_tracker;
            self.yawoffset_trackerself_tracker   = yawoffset_trackerself_tracker;
            self.pitchoffset_trackerself_tracker = pitchoffset_trackerself_tracker;
            self.rolloffset_trackerself_tracker  = rolloffset_trackerself_tracker;

        def get_calibration_data_tracker(self):
            return [ self.xoffset_tracker, self.yoffset_tracker, self.zoffset_tracker, self.yawoffset_trackerself_tracker, self.pitchoffset_trackerself_tracker, self.rolloffset_trackerself_tracker ];


    def __init__(self, roomsize):
        self.roomsize = roomsize;
        self.roomcenter = [ roomsize[0] / 2, roomsize[1] / 2 ];
        self.tracked_objects = {};
        self.all_tracked_objs_have_valid_pose = False;
        self.xoffset_world = 0.0;
        self.yoffset_world = 0.0;
        self.zoffset_world = 0.0;
        self.yawoffset_world   = 0.0;
        self.pitchoffset_world = 0.0;
        self.rolloffset_world  = 0.0;
        self.yawoffset_trackerself_world   = 0.0;
        self.pitchoffset_trackerself_world = 0.0;
        self.rolloffset_trackerself_world  = 0.0;
        self.pixelratio = 200;
        self.swapx = False;
        self.swapy = False;
        self.reverse_yawdir   = False;
        self.reverse_pitchdir = False;
        self.reverse_rolldir  = False;
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

    def set_reverseyawdir(self, reverse_yawdir):
        self.reverse_yawdir = reverse_yawdir;

    def set_reversepitchdir(self, reverse_pitchdir):
        self.reverse_pitchdir = reverse_pitchdir;

    def set_reverserolldir(self, reverse_rolldir):
        self.reverse_rolldir = reverse_rolldir;

    def calibrate_world(self, xoffset_world, yoffset_world, zoffset_world, yawoffset_world, yawoffset_trackerself_world, pitchoffset_world, pitchoffset_trackerself_world, rolloffset_world, rolloffset_trackerself_world, pixelratio, swapx, swapy, reverse_yawdir, reverse_pitchdir, reverse_rolldir):
        self.xoffset_world = xoffset_world;
        self.yoffset_world = yoffset_world;
        self.zoffset_world = zoffset_world;
        self.yawoffset_world   = yawoffset_world;
        self.pitchoffset_world = pitchoffset_world;
        self.rolloffset_world  = rolloffset_world;
        self.yawoffset_trackerself_world   = yawoffset_trackerself_world;
        self.pitchoffset_trackerself_world = pitchoffset_trackerself_world;
        self.rolloffset_trackerself_world  = rolloffset_trackerself_world;
        self.pixelratio = pixelratio;
        self.swapx = swapx;
        self.swapy = swapy;
        self.reverse_yawdir   = reverse_yawdir;
        self.reverse_pitchdir = reverse_pitchdir;
        self.reverse_rolldir  = reverse_rolldir;

    def calibrate_from_file(self, calibdata_filename):
        # try to read previous calibration config data
        try:  # todo better exception handling...
            calibdatafile = open(calibdata_filename,"r");
            calibdata = calibdatafile.readlines();
            calibdatafile.close();
            if len(calibdata) == 0:
                sys.stderr.writelines("WIL_LocDataBase: Empty calibration config file?\n");
                sys.exit(1);

            linezerosplit = calibdata[0].split();

            gwcount = 0;
            for goodkeyword in [ "wxoff", "wyoff", "wzoff", "wyaw", "wpitch", "wroll", "wyaw_t", "wpitch_t", "wroll_t", "pixrat", "swapx", "swapy", "revyaw", "revpitch", "revroll" ]:
                if linezerosplit[gwcount] != goodkeyword + ":":
                    sys.stderr.writelines("WIL_LocDataBase: Bad calibration config file: line 0, keyword %d should be %s!\n"%(gwcount/2, goodkeyword));
                    sys.exit(1);
                gwcount += 2;

            xoffset_world = float(linezerosplit[1]);
            yoffset_world = float(linezerosplit[3]);
            zoffset_world = float(linezerosplit[5]);
            yawoffset_world   = math.radians(float(linezerosplit[7]));
            pitchoffset_world = math.radians(float(linezerosplit[9]));
            rolloffset_world  = math.radians(float(linezerosplit[11]));
            yawoffset_trackerself_world   = math.radians(float(linezerosplit[13]));
            pitchoffset_trackerself_world = math.radians(float(linezerosplit[15]));
            rolloffset_trackerself_world  = math.radians(float(linezerosplit[17]));
            pixelratio = int(linezerosplit[19]);
            swapx = bool(int(linezerosplit[21]));
            swapy = bool(int(linezerosplit[23]));
            reverse_yawdir   = bool(int(linezerosplit[25]));
            reverse_pitchdir = bool(int(linezerosplit[27]));
            reverse_rolldir  = bool(int(linezerosplit[29]));

            if self.verbose:
                print("Setting these calibration parameters: offset x: %s y: %s z: %s | world yaw: %s/%s pitch: %s/%s roll: %s/%s | obj yaw: %s/%s pitch: %s/%s roll: %s/%s | pixrat: %d swapx: %d swapy: %d revyaw: %d revpitch: %d revroll :%d"%
                      (xoffset_world, yoffset_world, zoffset_world,
                       yawoffset_world, math.degrees(yawoffset_world), yawoffset_trackerself_world, math.degrees(yawoffset_trackerself_world),
                       pitchoffset_world, math.degrees(pitchoffset_world), pitchoffset_trackerself_world, math.degrees(pitchoffset_trackerself_world),
                       rolloffset_world, math.degrees(rolloffset_world), rolloffset_trackerself_world, math.degrees(rolloffset_trackerself_world),
                       pixelratio, swapx, swapy, reverse_yawdir, reverse_pitchdir, reverse_rolldir) );

            self.calibrate_world(xoffset_world, yoffset_world, zoffset_world,
                                 yawoffset_world, yawoffset_trackerself_world,
                                 pitchoffset_world, pitchoffset_trackerself_world,
                                 rolloffset_world, rolloffset_trackerself_world,
                                 pixelratio, swapx, swapy, reverse_yawdir, reverse_pitchdir, reverse_rolldir);

            if len(calibdata) > 1:
                currlinecount = 0;
                for configline in calibdata[1:]:
                    currlinecount += 1;
                    trackeradjustlinesplit = configline.split();
                    gwcount = 0;
                    for goodkeyword in [ "tracker", "xoff", "yoff", "zoff", "yawoff_t", "pitchoff_t", "rolloff_t" ]:
                        if trackeradjustlinesplit[gwcount] != goodkeyword + ":":
                            sys.stderr.writelines("WIL_LocDataBase: Bad calibration config file: line %d, keyword %d should be %s!\n"%(currlinecount, gwcount/2, goodkeyword));
                            sys.exit(1);
                        gwcount += 2;

                    trackerserial = trackeradjustlinesplit[1];
                    if trackerserial not in self.tracked_objects.keys():
                        sys.stderr.writelines("WIL_LocDataBase: WARNING: Possibly bad calibration config file: line %d: no such tracker listed in wilconfig: %s!\n"%(currlinecount, trackeradjustlinesplit[1]));
#                        sys.exit(1);

                    xoffset_tracker = float(trackeradjustlinesplit[3]);
                    yoffset_tracker = float(trackeradjustlinesplit[5]);
                    zoffset_tracker = float(trackeradjustlinesplit[7]);
                    yawoffset_trackerself_tracker   = math.radians(float(trackeradjustlinesplit[9]));
                    pitchoffset_trackerself_tracker = math.radians(float(trackeradjustlinesplit[11]));
                    rolloffset_trackerself_tracker  = math.radians(float(trackeradjustlinesplit[13]));

                    if self.verbose:
                        print("Setting these calibration parameters for tracker %s: offset x: %s, y: %s, z: %s, yaw: %s/%s, pitch: %s/%s, roll: %s/%s"%
                              (trackerserial, xoffset_tracker, yoffset_tracker, zoffset_tracker,
                              yawoffset_trackerself_tracker, math.degrees(yawoffset_trackerself_tracker),
                              pitchoffset_trackerself_tracker, math.degrees(pitchoffset_trackerself_tracker),
                              rolloffset_trackerself_tracker, math.degrees(rolloffset_trackerself_tracker) )
                             );

                    self.tracked_objects[trackerserial].calibrate_tracker(xoffset_tracker, yoffset_tracker, zoffset_tracker, yawoffset_trackerself_tracker, pitchoffset_trackerself_tracker, rolloffset_trackerself_tracker);

            return True

        except:

            return False

    def get_calibration_data_world(self):
        return [ self.xoffset_world, self.yoffset_world, self.zoffset_world, self.yawoffset_world, self.yawoffset_trackerself_world, self.pitchoffset_world, self.pitchoffset_trackerself_world, self.rolloffset_world, self.rolloffset_trackerself_world, self.pixelratio, self.swapx, self.swapy, self.reverse_yawdir, self.reverse_pitchdir, self.reverse_rolldir ]

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
