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
    trackers['robot']   = {'serial': 'LHR-XXXXXXX1', 'yawaxis': 1, 'pitchaxis': 2, 'rollaxis': 0, 'radius': 15, 'labeltext': 'ROBOT', 'color': '#FF0000'};
    trackers['object1'] = {'serial': 'LHR-XXXXXXX2', 'yawaxis': 1, 'pitchaxis': 2, 'rollaxis': 0, 'radius': 15, 'labeltext': 'OBJ1',  'color': '#0080FF'};
    trackers['human1']  = {'serial': 'LHR-XXXXXXX3', 'yawaxis': 1, 'pitchaxis': 2, 'rollaxis': 0, 'radius': 15, 'labeltext': 'HUM1',  'color': '#0000FF'};
    trackers['human2']  = {'serial': 'LHR-XXXXXXX4', 'yawaxis': 1, 'pitchaxis': 2, 'rollaxis': 0, 'radius': 15, 'labeltext': 'HUM2',  'color': '#FF00FF'};
