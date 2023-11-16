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

        def __init__(self, trackerserial, wldbobj, reftrackerobj = None):

            self.serial = trackerserial
            self.wldbobj = wldbobj
            self.timecode = 0
            self.pose = None
            self.pose_euler_deg = None
            self.buttons = { 'system': False, 'trigger': False, 'menu': False, 'grip': False,
                             'trackpad_press': False, 'trackpad_touch': False,
                             'trackpad_x': 0.0, 'trackpad_y': 0.0 }

            if reftrackerobj == None:
                self.parenttrackerobj = None
                self.trackertype = 1
                self.yawaxis   = 0
                self.pitchaxis = 1
                self.rollaxis  = 2
                self.xoffset_tracker = 0.0
                self.yoffset_tracker = 0.0
                self.zoffset_tracker = 0.0
                self.yawoffset_trackerself_tracker   = 0.0  # radians
                self.pitchoffset_trackerself_tracker = 0.0  # radians
                self.rolloffset_trackerself_tracker  = 0.0  # radians
            else:
                self.parenttrackerobj = reftrackerobj
                self.trackertype = 2
                self.yawaxis   = reftrackerobj.yawaxis  # copy?
                self.pitchaxis = reftrackerobj.pitchaxis
                self.rollaxis  = reftrackerobj.rollaxis
                self.xoffset_tracker = reftrackerobj.xoffset_tracker
                self.yoffset_tracker = reftrackerobj.yoffset_tracker
                self.zoffset_tracker = reftrackerobj.zoffset_tracker
                self.yawoffset_trackerself_tracker   = reftrackerobj.yawoffset_trackerself_tracker    # radians
                self.pitchoffset_trackerself_tracker = reftrackerobj.pitchoffset_trackerself_tracker  # radians
                self.rolloffset_trackerself_tracker  = reftrackerobj.rolloffset_trackerself_tracker   # radians


        def update_from_parent(self):
            if self.parenttrackerobj != None:
                self.pose = self.parenttrackerobj.get_raw_position() + self.parenttrackerobj.get_raw_orientation_quat()
                self.pose_euler_deg = self.pose[0:3] + self.parenttrackerobj.get_raw_orientation_euler_degrees()
                self.buttons = self.parenttrackerobj.buttons

        def get_raw_position(self):
            return self.pose[0:3]

        def get_raw_orientation_quat(self):
            return self.pose[3:7]

        def get_raw_orientation_euler_radians(self):
            if self.pose_euler_deg != None:
                return [ math.radians(deg) for deg in self.pose_euler_deg[3:6] ]
            else:
                return self.wldbobj.quattoeuler(self.pose[3:7])

        def get_raw_orientation_euler_degrees(self):
            if self.pose_euler_deg != None:
                return self.pose_euler_deg[3:6]
            else:
                return [ math.degrees(radian) for radian in self.wldbobj.quattoeuler(self.pose[3:7]) ]

        def get_position(self):
            rawpos = self.get_raw_position()
            if self.wldbobj.swapx:
                rawpos[0] = -rawpos[0]
            if self.wldbobj.swapy:
                rawpos[1] = -rawpos[1]
            [r, th] = self.wldbobj.rect2polar(rawpos[0], rawpos[1])
#            [r, th] = self.wldbobj.rect2polar(offsetpos[0], offsetpos[1])
            newth = th - self.wldbobj.yawoffset_world
            rotatedpos = self.wldbobj.polar2rect(r, newth)
            offrotpos = [ rotatedpos[0] + self.wldbobj.xoffset_world + self.xoffset_tracker,
                          rotatedpos[1] + self.wldbobj.yoffset_world + self.yoffset_tracker,
                          rawpos[2]     + self.wldbobj.zoffset_world + self.zoffset_tracker ]

            if self.trackertype == 2:  # "pointer" tracker
                if 180.0 < self.get_pitch_degrees() < 270.0:  # 180 - straight (horizontal), 270 down (vertical)
                    pointer_r = math.tan(math.pi*1.5 - self.get_pitch_radians()) * (rawpos[2] + self.wldbobj.zoffset_world + self.zoffset_tracker)  # rawpos[2] should be z (height)
                    pointer_th = self.get_yaw_radians() - (math.pi / 2)
                    pointer_offpos = self.wldbobj.polar2rect(pointer_r, pointer_th)
                    offrotpos[0] += pointer_offpos[0]
                    offrotpos[1] += pointer_offpos[1]
                    offrotpos[2] = 0.0
                else:
                    offrotpos = None

            return offrotpos

        def get_position_pixel(self):
            trackpos = self.get_position()
            if trackpos != None:
                return [ trackpos[0] * self.wldbobj.pixelratio, trackpos[1] * self.wldbobj.pixelratio, trackpos[2] * self.wldbobj.pixelratio ]
            else:
                return None

        def get_orientation_radians(self, whichaxis, offset_trackerself_world, offset_trackerself_tracker, reversedir):
            orientation_radians = self.get_raw_orientation_euler_radians()
            # angle -180-+180 -> 0-360
            angle = orientation_radians[whichaxis] + math.pi - offset_trackerself_world - offset_trackerself_tracker
            if angle >= 2*math.pi:
                angle -= 2*math.pi
            if angle < 0:
                angle += 2*math.pi
            if reversedir:
                angle = 2*math.pi - angle
            return angle

        def get_yaw_radians(self):
            return self.get_orientation_radians(self.yawaxis, self.wldbobj.yawoffset_trackerself_world, self.yawoffset_trackerself_tracker, self.wldbobj.reverse_yawdir)

        def get_yaw_degrees(self):
            return math.degrees(self.get_yaw_radians())

        def get_pitch_radians(self):
            return self.get_orientation_radians(self.pitchaxis, self.wldbobj.pitchoffset_trackerself_world, self.pitchoffset_trackerself_tracker, self.wldbobj.reverse_pitchdir)

        def get_pitch_degrees(self):
            return math.degrees(self.get_pitch_radians())

        def get_roll_radians(self):
            return self.get_orientation_radians(self.rollaxis, self.wldbobj.rolloffset_trackerself_world, self.rolloffset_trackerself_tracker, self.wldbobj.reverse_rolldir)

        def get_roll_degrees(self):
            return math.degrees(self.get_roll_radians())

        def was_button_pressed(self, whichbuttons):
            retval = False
            for button in whichbuttons:
                if self.buttons[button]:
                    self.buttons[button] = False
                    retval = True
            return retval

        def set_yawaxis(self, yawaxisno):
            self.yawaxis = yawaxisno

        def set_pitchaxis(self, pitchaxisno):
            self.pitchaxis = pitchaxisno

        def set_rollaxis(self, rollaxisno):
            self.rollaxis = rollaxisno

        def calibrate_tracker(self, xoffset_tracker, yoffset_tracker, zoffset_tracker, yawoffset_trackerself_tracker, pitchoffset_trackerself_tracker, rolloffset_trackerself_tracker):
            self.xoffset_tracker = xoffset_tracker
            self.yoffset_tracker = yoffset_tracker
            self.zoffset_tracker = zoffset_tracker
            self.yawoffset_trackerself_tracker   = yawoffset_trackerself_tracker
            self.pitchoffset_trackerself_tracker = pitchoffset_trackerself_tracker
            self.rolloffset_trackerself_tracker  = rolloffset_trackerself_tracker

        def get_calibration_data_tracker(self):
            return [ self.xoffset_tracker, self.yoffset_tracker, self.zoffset_tracker, self.yawoffset_trackerself_tracker, self.pitchoffset_trackerself_tracker, self.rolloffset_trackerself_tracker ]


    def __init__(self, roomsize):

        self.roomsize = roomsize
        self.roomcenter = [ roomsize[0] / 2, roomsize[1] / 2 ]
        self.tracked_objects = {}
        self.all_tracked_objs_have_valid_pose = False
        self.xoffset_world = 0.0
        self.yoffset_world = 0.0
        self.zoffset_world = 0.0
        self.yawoffset_world   = 0.0
        self.pitchoffset_world = 0.0
        self.rolloffset_world  = 0.0
        self.yawoffset_trackerself_world   = 0.0
        self.pitchoffset_trackerself_world = 0.0
        self.rolloffset_trackerself_world  = 0.0
        self.pixelratio = 200
        self.swapx = False
        self.swapy = False
        self.reverse_yawdir   = False
        self.reverse_pitchdir = False
        self.reverse_rolldir  = False
        self.verbose = False


    def set_verbose(self, verbose):
        self.verbose = verbose

    def polar2rect(self, r, theta):
        return [ r*math.cos(theta), r*math.sin(theta) ]

    def rect2polar(self, x, y):
        r = math.sqrt(x**2 + y**2)
        theta = math.atan2(y,x)
        return [ r, theta ]

    # from: https://steamcommunity.com/app/250820/discussions/0/1728711392744037419/
    # http://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToEuler/index.htm
    def quattoeuler(self, q):

        [ qw, qx, qy, qz ] = q

        test = qx * qy + qz * qw
        if (test > 0.499):  # singularity at north pole
            yaw = 2 * math.atan2(qx, qw)  # heading
            pitch = math.pi / 2  # attitude
            roll = 0  # bank

        elif (test < -0.499):  # singularity at south pole
            yaw = -2 * math.atan2(qx, qw)  # heading
            pitch = -math.pi / 2  # attitude
            roll = 0  # bank

        else:
            sqx = qx * qx
            sqy = qy * qy
            sqz = qz * qz
            yaw = math.atan2(2 * qy * qw - 2 * qx * qz, 1 - 2 * sqy - 2 * sqz)  # heading
            pitch = math.asin(2 * test)  # attitude
            roll = math.atan2(2 * qx * qw - 2 * qy * qz, 1 - 2 * sqx - 2 * sqz)  # bank

        return [ yaw, roll, pitch ]


    def set_swapx(self, swapx):
        self.swapx = swapx

    def set_swapy(self, swapy):
        self.swapy = swapy

    def set_reverseyawdir(self, reverse_yawdir):
        self.reverse_yawdir = reverse_yawdir

    def set_reversepitchdir(self, reverse_pitchdir):
        self.reverse_pitchdir = reverse_pitchdir

    def set_reverserolldir(self, reverse_rolldir):
        self.reverse_rolldir = reverse_rolldir

    def calibrate_world(self, xoffset_world, yoffset_world, zoffset_world, yawoffset_world, yawoffset_trackerself_world, pitchoffset_world, pitchoffset_trackerself_world, rolloffset_world, rolloffset_trackerself_world, pixelratio, swapx, swapy, reverse_yawdir, reverse_pitchdir, reverse_rolldir):
        self.xoffset_world = xoffset_world
        self.yoffset_world = yoffset_world
        self.zoffset_world = zoffset_world
        self.yawoffset_world   = yawoffset_world
        self.pitchoffset_world = pitchoffset_world
        self.rolloffset_world  = rolloffset_world
        self.yawoffset_trackerself_world   = yawoffset_trackerself_world
        self.pitchoffset_trackerself_world = pitchoffset_trackerself_world
        self.rolloffset_trackerself_world  = rolloffset_trackerself_world
        self.pixelratio = pixelratio
        self.swapx = swapx
        self.swapy = swapy
        self.reverse_yawdir   = reverse_yawdir
        self.reverse_pitchdir = reverse_pitchdir
        self.reverse_rolldir  = reverse_rolldir


    def calibrate_from_file(self, calibdata_filename):
        # try to read previous calibration config data
        try:  # todo better exception handling...
            calibdatafile = open(calibdata_filename,"r")
            calibdata = calibdatafile.readlines()
            calibdatafile.close()
            if len(calibdata) == 0:
                sys.stderr.writelines("WIL_LocDataBase: Empty calibration config file?\n")
                sys.exit(1)

            linezero_split = calibdata[0].split()

            gwcount = 0
            for goodkeyword in [ "wxoff", "wyoff", "wzoff", "wyaw", "wpitch", "wroll", "wyaw_t", "wpitch_t", "wroll_t", "pixrat", "swapx", "swapy", "revyaw", "revpitch", "revroll" ]:
                if linezero_split[gwcount] != goodkeyword + ":":
                    sys.stderr.writelines("WIL_LocDataBase: Bad calibration config file: line 0, keyword %d should be %s!\n"%(gwcount/2, goodkeyword))
                    sys.exit(1)
                gwcount += 2

            xoffset_world = float(linezero_split[1])
            yoffset_world = float(linezero_split[3])
            zoffset_world = float(linezero_split[5])
            yawoffset_world   = math.radians(float(linezero_split[7]))
            pitchoffset_world = math.radians(float(linezero_split[9]))
            rolloffset_world  = math.radians(float(linezero_split[11]))
            yawoffset_trackerself_world   = math.radians(float(linezero_split[13]))
            pitchoffset_trackerself_world = math.radians(float(linezero_split[15]))
            rolloffset_trackerself_world  = math.radians(float(linezero_split[17]))
            pixelratio = int(linezero_split[19])
            swapx = bool(int(linezero_split[21]))
            swapy = bool(int(linezero_split[23]))
            reverse_yawdir   = bool(int(linezero_split[25]))
            reverse_pitchdir = bool(int(linezero_split[27]))
            reverse_rolldir  = bool(int(linezero_split[29]))

            if self.verbose:
                print("Setting these calibration parameters: offset x: %s y: %s z: %s | world yaw: %s/%s pitch: %s/%s roll: %s/%s | obj yaw: %s/%s pitch: %s/%s roll: %s/%s | pixrat: %d swapx: %d swapy: %d revyaw: %d revpitch: %d revroll :%d"%
                      (xoffset_world, yoffset_world, zoffset_world,
                       yawoffset_world, math.degrees(yawoffset_world), yawoffset_trackerself_world, math.degrees(yawoffset_trackerself_world),
                       pitchoffset_world, math.degrees(pitchoffset_world), pitchoffset_trackerself_world, math.degrees(pitchoffset_trackerself_world),
                       rolloffset_world, math.degrees(rolloffset_world), rolloffset_trackerself_world, math.degrees(rolloffset_trackerself_world),
                       pixelratio, swapx, swapy, reverse_yawdir, reverse_pitchdir, reverse_rolldir) )

            self.calibrate_world(xoffset_world, yoffset_world, zoffset_world,
                                 yawoffset_world, yawoffset_trackerself_world,
                                 pitchoffset_world, pitchoffset_trackerself_world,
                                 rolloffset_world, rolloffset_trackerself_world,
                                 pixelratio, swapx, swapy, reverse_yawdir, reverse_pitchdir, reverse_rolldir)

            if len(calibdata) > 1:
                currlinecount = 0
                for configline in calibdata[1:]:
                    currlinecount += 1
                    trackeradjustlinesplit = configline.split()
                    gwcount = 0
                    for goodkeyword in [ "tracker", "xoff", "yoff", "zoff", "yawoff_t", "pitchoff_t", "rolloff_t" ]:
                        if trackeradjustlinesplit[gwcount] != goodkeyword + ":":
                            sys.stderr.writelines("WIL_LocDataBase: Bad calibration config file: line %d, keyword %d should be %s!\n"%(currlinecount, gwcount/2, goodkeyword))
                            sys.exit(1)
                        gwcount += 2

                    trackerserial = trackeradjustlinesplit[1]
                    if trackerserial[-4:] == '-PTR':  # pointer trackers should not be in the config file, but skip them, just in case
                        continue
                    if trackerserial not in self.tracked_objects.keys():
                        sys.stderr.writelines("WIL_LocDataBase: WARNING: Possibly bad calibration config file: line %d: no such tracker listed in wilconfig: %s!\n"%(currlinecount, trackeradjustlinesplit[1]))
#                        sys.exit(1)

                    xoffset_tracker = float(trackeradjustlinesplit[3])
                    yoffset_tracker = float(trackeradjustlinesplit[5])
                    zoffset_tracker = float(trackeradjustlinesplit[7])
                    yawoffset_trackerself_tracker   = math.radians(float(trackeradjustlinesplit[9]))
                    pitchoffset_trackerself_tracker = math.radians(float(trackeradjustlinesplit[11]))
                    rolloffset_trackerself_tracker  = math.radians(float(trackeradjustlinesplit[13]))

                    if self.verbose:
                        print("Setting these calibration parameters for tracker %s: offset x: %s, y: %s, z: %s, yaw: %s/%s, pitch: %s/%s, roll: %s/%s"%
                              (trackerserial, xoffset_tracker, yoffset_tracker, zoffset_tracker,
                              yawoffset_trackerself_tracker, math.degrees(yawoffset_trackerself_tracker),
                              pitchoffset_trackerself_tracker, math.degrees(pitchoffset_trackerself_tracker),
                              rolloffset_trackerself_tracker, math.degrees(rolloffset_trackerself_tracker) )
                             )

                    self.tracked_objects[trackerserial].calibrate_tracker(xoffset_tracker, yoffset_tracker, zoffset_tracker, yawoffset_trackerself_tracker, pitchoffset_trackerself_tracker, rolloffset_trackerself_tracker)

            return True

        except:

            return False


    def get_calibration_data_world(self):
        return [ self.xoffset_world, self.yoffset_world, self.zoffset_world, self.yawoffset_world, self.yawoffset_trackerself_world, self.pitchoffset_world, self.pitchoffset_trackerself_world, self.rolloffset_world, self.rolloffset_trackerself_world, self.pixelratio, self.swapx, self.swapy, self.reverse_yawdir, self.reverse_pitchdir, self.reverse_rolldir ]

    def all_poses_valid(self):
        self.all_tracked_objs_have_valid_pose = True
        for trackobj in self.tracked_objects.keys():
            if self.tracked_objects[trackobj].pose == None:
                self.all_tracked_objs_have_valid_pose = False
                break
        return self.all_tracked_objs_have_valid_pose

    # ROS and SteamVR overrides this
    def add_tracker_by_serial(self, trackerserial):
        if trackerserial not in self.tracked_objects.keys():
            self.tracked_objects[trackerserial] = self.WILTracker(trackerserial, self)
            self.all_tracked_objs_have_valid_pose = False
            return self.tracked_objects[trackerserial]

    def update(self):
        retcode = self.update_poses_from_src()
        # PTR trackers
        for trackobjname in self.tracked_objects.keys():
            if self.tracked_objects[trackobjname].trackertype == 2:
                self.tracked_objects[trackobjname].update_from_parent()
        return retcode

    def add_pointer_tracker(self, trackerobj):
        self.tracked_objects[trackerobj.serial + '-PTR'] = self.WILTracker(trackerobj.serial + '-PTR', self, trackerobj)
        return self.tracked_objects[trackerobj.serial + '-PTR']
