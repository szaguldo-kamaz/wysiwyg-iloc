# WYSIWYG Indoor Localization
#  Configuration
#
# Author: David Vincze
#
# https://github.com/szaguldo-kamaz/
#

class wil_config:

    LOCDATA_SOURCE_LIBSURVIVE = 1;
    LOCDATA_SOURCE_STEAMVR    = 2;
    LOCDATA_SOURCE_ROS        = 3;
    LOCDATA_SOURCE_REMOTEUDP  = 4;
    LOCDATA_SOURCE_FILE       = 5;

    locdata_source = LOCDATA_SOURCE_STEAMVR;

    playareapixels = [ 1280, 800 ];  # projector resolution

    trackers = {};
    trackers['robot']   = {'serial':'LHR-XXXXXXX1', 'color':'#FF0000', 'labeltext':'ROBOT', 'rotaxis': 0};
    trackers['object1'] = {'serial':'LHR-XXXXXXX2', 'color':'#0080FF', 'labeltext':'OBJ1',  'rotaxis': 0};
    trackers['human1']  = {'serial':'LHR-XXXXXXX3', 'color':'#0000FF', 'labeltext':'HUM1',  'rotaxis': 0};
    trackers['human2']  = {'serial':'LHR-XXXXXXX4', 'color':'#FF00FF', 'labeltext':'HUM2',  'rotaxis': 0};
