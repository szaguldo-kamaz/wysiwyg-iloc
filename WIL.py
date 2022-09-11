# WYSIWYG Indoor Localization
#   Gather pose/button information from localization system
#
# Author: David Vincze
#
# https://github.com/szaguldo-kamaz/
#


import importlib


class WIL:

    def __init__(self, wil_config_filename = "wil_config.py"):

        if wil_config_filename[-3:] == ".py":
            wil_config_filename = wil_config_filename[:-3];

        wilc = importlib.import_module(wil_config_filename);

        self.config = wilc.wil_config;
        self.trackers = {};
        self.trackers_by_serial = {};
        self.trackers_by_name = self.trackers;
        self.verbose = False;

        if   self.config.locdata_source == self.config.LOCDATA_SOURCE_LIBSURVIVE:
            from WIL_LocDataLibSurvive import WILLocDataLibSurvive
            self.locdata = WILLocDataLibSurvive(self.config.playareapixels);
        elif self.config.locdata_source == self.config.LOCDATA_SOURCE_STEAMVR:
            from WIL_LocDataSteamVR    import WILLocDataSteamVR
            self.locdata = WILLocDataSteamVR(self.config.playareapixels);
        elif self.config.locdata_source == self.config.LOCDATA_SOURCE_ROS:
            from WIL_LocDataROS        import WILLocDataROS
            self.locdata = WILLocDataROS(self.config.playareapixels);
        elif self.config.locdata_source == self.config.LOCDATA_SOURCE_REMOTEUDP:
            from WIL_LocDataRemoteUDP  import WILLocDataRemoteUDP
            self.locdata = WILLocDataRemoteUDP(self.config.playareapixels);
        elif self.config.locdata_source == self.config.LOCDATA_SOURCE_FILE:
            from WIL_LocDataFile       import WILLocDataFile
            self.locdata = WILLocDataFile(self.config.playareapixels);
        else:
            print("Unknown LocData_source was specified. Exiting.");
            sys.exit(1);  # should be an exception. maybe later...

        for trackername in self.config.trackers.keys():
            self.add_tracker(trackername, self.config.trackers[trackername]['serial']);
            self.trackers[trackername].set_rotaxis(self.config.trackers[trackername]['rotaxis']);

    def set_verbose(self, verbose):
        self.verbose = verbose;
        self.locdata.verbose = verbose;

    def add_tracker(self, trackername, trackerserial):
        self.trackers_by_serial[trackerserial] = self.locdata.add_tracker_by_serial(trackerserial);
        self.trackers[trackername] = self.trackers_by_serial[trackerserial];

    def get_tracker_names(self):
        return list(self.trackers.keys());

    def get_tracker_serials(self):
        return self.trackers_by_serial.keys();

    def calibrate_world(self, xoffset_world, yoffset_world, zoffset_world, rotoffset_world, rotoffset_trackerself, pixelratio, swapx, swapy, reverse_rotdir):
        self.locdata.calibrate_world(xoffset_world, yoffset_world, zoffset_world, rotoffset_world, rotoffset_trackerself, pixelratio, swapx, swapy, reverse_rotdir);

    def calibrate_from_file(self, calibdata_filename):
        return self.locdata.calibrate_from_file(calibdata_filename);

    def get_calibration_data_world(self):
        return self.locdata.get_calibration_data_world();

    def update(self):
        return self.locdata.update();

    def all_poses_valid(self):
        return self.locdata.all_poses_valid();
