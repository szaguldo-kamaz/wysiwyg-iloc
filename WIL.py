# WYSIWYG Indoor Localization
#   Gather pose/button information from localization system
#
# Author: David Vincze
#
# https://github.com/szaguldo-kamaz/
#

from wil_config            import wil_config


class WIL:

    def __init__(self, locdatasource, playareapixels):

        self.trackers = {};
        self.trackers_by_serial = {};
        self.trackers_by_name = self.trackers;
        self.locdatasource = locdatasource;
        self.verbose = False;

        if   locdatasource == wil_config.LOCDATA_SOURCE_LIBSURVIVE:
            from WIL_LocDataLibSurvive import WILLocDataLibSurvive
            self.locdata = WILLocDataLibSurvive(playareapixels);
        elif locdatasource == wil_config.LOCDATA_SOURCE_STEAMVR:
            from WIL_LocDataSteamVR    import WILLocDataSteamVR
            self.locdata = WILLocDataSteamVR(playareapixels);
        elif locdatasource == wil_config.LOCDATA_SOURCE_ROS:
            from WIL_LocDataROS        import WILLocDataROS
            self.locdata = WILLocDataROS(playareapixels);
        elif locdatasource == wil_config.LOCDATA_SOURCE_REMOTEUDP:
            from WIL_LocDataRemoteUDP  import WILLocDataRemoteUDP
            self.locdata = WILLocDataRemoteUDP(playareapixels);
        elif locdatasource == wil_config.LOCDATA_SOURCE_FILE:
            from WIL_LocDataFile       import WILLocDataFile
            self.locdata = WILLocDataFile(playareapixels);
        else:
            print("Unknown LocData_source was specified. Exiting.");
            sys.exit(1);  # should be an exception. maybe later...

    def set_verbose(self, verbose):
        self.verbose = verbose;
        self.locdata.verbose = verbose;

    def add_tracker(self, trackername, trackerserial):
        self.trackers_by_serial[trackerserial] = self.locdata.add_tracker_by_serial(trackerserial);
        self.trackers[trackername] = self.trackers_by_serial[trackerserial];

    def get_tracker_names(self):
        return self.trackers.keys();

    def get_tracker_serials(self):
        return self.trackers_by_serial.keys();

    def calibrate(self, xoffset, yoffset, zoffset, rotoffset_world, rotoffset_obj, pixelratio, swapx, swapy, reverse_rotdir):
        self.locdata.calibrate(xoffset, yoffset, zoffset, rotoffset_world, rotoffset_obj, pixelratio, swapx, swapy, reverse_rotdir);

    def calibrate_from_file(self, calibdata_filename):
        return self.locdata.calibrate_from_file(calibdata_filename);

    def get_calibration_data(self):
        return self.locdata.get_calibration_data();

    def update(self):
        return self.locdata.update();

    def all_poses_valid(self):
        return self.locdata.all_poses_valid();
