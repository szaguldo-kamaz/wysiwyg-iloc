# WYSIWYG Indoor Localization
#   Gather pose/button information from localization system
#
# Author: David Vincze
#
# https://github.com/szaguldo-kamaz/
#

from wil_config            import wil_config
from WIL_LocDataLibSurvive import WILLocDataLibSurvive
from WIL_LocDataSteamVR    import WILLocDataSteamVR
from WIL_LocDataROS        import WILLocDataROS
from WIL_LocDataRemoteUDP  import WILLocDataRemoteUDP


class WILLocData:

    def __init__(self, locdatasource, playareapixels):
        if   locdatasource == wil_config.LOCDATA_SOURCE_LIBSURVIVE:
            self.dataiface = WILLocDataLibSurvive(playareapixels);
        elif locdatasource == wil_config.LOCDATA_SOURCE_STEAMVR:
            self.dataiface = WILLocDataSteamVR(playareapixels);
        elif locdatasource == wil_config.LOCDATA_SOURCE_ROS:
            self.dataiface = WILLocDataROS(playareapixels);
        elif locdatasource == wil_config.LOCDATA_SOURCE_REMOTEUDP:
            self.dataiface = WILLocDataRemoteUDP(playareapixels);
        else:
            print("Unknown locdata_source was specified. Exiting.");
            sys.exit(1);  # should be an exception. maybe later...
