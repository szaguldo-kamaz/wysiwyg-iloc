# WYSIWYG Indoor Localization
#
# Find calibration parameters
#   Adjust localization sys data to the real environment (using floor projection)
#
# Usage:
#  mouse dragging with left button pressed: adjust world x, y offset
#  mouse scrollwheel: adjust world yaw offset
#  mouse scrollwheel with left button pressed: adjust tracker self yaw offset
#  keys + - : adjust pixratio
#  keys x y r : toggle swap x, y, yawdir
#  key z : in invidivual tracker adjustment mode: take the selected tracker as the reference zero height
#          in world adjustment mode: take the tracker with the lowest height as reference zero height
#  key c : start/stop pose data capture to file
#  key Esc : exit without saving calibration parameters
#  key Enter : save calibration parameters and exit
#
# Author: David Vincze
#
# https://github.com/szaguldo-kamaz/
#

import math, sys, datetime, os, time
import PySimpleGUI as sg
from WIL import WIL
from draw_rotated_things.draw_rotated_things import *


# configuration

#floorprojectionmode = True; # fullscreen
floorprojectionmode = False; # windowed - for testing
calibdata_filename  = "wil_calibparams.txt";
default_swapx = False;
default_swapy = True;
default_reverse_yawdir   = True;
default_reverse_pitchdir = False;
default_reverse_rolldir  = False;
default_pixelratio = 200;
windowbackgroundcolor = '#000000';
linecolor1 = '#FFFFFF';
linecolor2 = '#00FF00';
linecolor3 = '#FF00FF';
statusfont = "Verdana 14";
plotsize_small = 15;
plotsize_large = 40;


### start ###

if len(sys.argv) > 1:
    wilobj = WIL(sys.argv[1]);
else:
    wilobj = WIL();

# try to read previous calibration config data
if wilobj.calibrate_from_file(calibdata_filename):

    [ xoffset_world, yoffset_world, zoffset_world,
      yawoffset_world, yawoffset_trackerself,
      pitchoffset_world, pitchoffset_trackerself,
      rolloffset_world, rolloffset_trackerself,
      pixelratio, swapx, swapy,
      reverse_yawdir, reverse_pitchdir, reverse_rolldir ] = wilobj.get_calibration_data_world();
    print("Calibration data loaded from: %s"%(calibdata_filename));

else:

    print("Cannot load calibration data from: %s, using default values."%(calibdata_filename));
    xoffset_world = 0.0;
    yoffset_world = 0.0;
    zoffset_world = 0.0;
    yawoffset_world   = 0.0;
    pitchoffset_world = 0.0;
    rolloffset_world  = 0.0;
    yawoffset_trackerself   = 0.0;
    pitchoffset_trackerself = 0.0;
    rolloffset_trackerself  = 0.0;
    pixelratio = default_pixelratio;
    swapx = default_swapx;
    swapy = default_swapy;
    reverse_yawdir   = default_reverse_yawdir;
    reverse_pitchdir = default_reverse_pitchdir;
    reverse_rolldir  = default_reverse_rolldir;
    wilobj.calibrate_world(xoffset_world, yoffset_world, zoffset_world,
                           yawoffset_world, yawoffset_trackerself,
                           pitchoffset_world, pitchoffset_trackerself,
                           rolloffset_world, rolloffset_trackerself,
                           pixelratio, swapx, swapy,
                           reverse_yawdir, reverse_pitchdir, reverse_rolldir);

# init gui
sg.theme('DarkGrey5');
graphsize = (wilobj.config.playareapixels[0], wilobj.config.playareapixels[1]);
left_side_layout = [ [ sg.Graph(
                            graphsize, (0, graphsize[1]), (graphsize[0], 0),
                            background_color=windowbackgroundcolor,
                            change_submits=True,
                            drag_submits=True,
                            enable_events=True,
                            key='-GRAPH-', pad=(0,0)) ]
                   ];
layout = [[ sg.pin(sg.Column(left_side_layout, key='-LEFTSIDE-', background_color=windowbackgroundcolor, pad=(0,0))) ]];

if floorprojectionmode:
    window = sg.Window('wysiwyg-iloc calibration tool', layout, return_keyboard_events=True, finalize=True, margins=(0,0), use_default_focus=False, background_color=windowbackgroundcolor, no_titlebar=True, location=(0, 0), size=(1280, 800), keep_on_top=True)
    window.Maximize();
else:
    window = sg.Window('wysiwyg-iloc calibration tool', layout, return_keyboard_events=True, finalize=True, margins=(0,0), use_default_focus=False, background_color=windowbackgroundcolor)

graph = window['-GRAPH-'];
window.bind('<Button-4>', '+SCRUP+');
window.bind('<Button-5>', '+SCRDN+');

# draw playarea borders
graph.draw_rectangle( [1, 1], [wilobj.config.playareapixels[0] - 2, wilobj.config.playareapixels[1] - 1], line_color=linecolor1, line_width=3);

# color2
for no in range(0,4):
    graph.draw_line( ((wilobj.config.playareapixels[0]/2) - (2*no*100) - 100, 0) , ((wilobj.config.playareapixels[0]/2) - (2*no*100)-100,wilobj.config.playareapixels[1]), color=linecolor2);
    graph.draw_line( ((wilobj.config.playareapixels[0]/2) + (2*no*100) + 100, 0) , ((wilobj.config.playareapixels[0]/2) + (2*no*100)+100,wilobj.config.playareapixels[1]), color=linecolor2);
for no in range(0,3):
    graph.draw_line( (0, (wilobj.config.playareapixels[1]/2) - (2*no*100) - 100, 0) , (wilobj.config.playareapixels[0], (wilobj.config.playareapixels[1]/2) - (2*no*100) - 100), color=linecolor2);
    graph.draw_line( (0, (wilobj.config.playareapixels[1]/2) + (2*no*100) + 100, 0) , (wilobj.config.playareapixels[0], (wilobj.config.playareapixels[1]/2) + (2*no*100) + 100), color=linecolor2);
# color3 should be above color2 lines
for no in range(1,4):
    graph.draw_line( ((wilobj.config.playareapixels[0]/2) - (2*no*100),0) , ((wilobj.config.playareapixels[0]/2) - (2*no*100),wilobj.config.playareapixels[1]), color=linecolor3);
    graph.draw_line( ((wilobj.config.playareapixels[0]/2) + (2*no*100),0) , ((wilobj.config.playareapixels[0]/2) + (2*no*100),wilobj.config.playareapixels[1]), color=linecolor3);
for no in range(1,3):
    graph.draw_line( (0, (wilobj.config.playareapixels[1]/2) - (2*no*100)) , (wilobj.config.playareapixels[0], (wilobj.config.playareapixels[1]/2) - (2*no*100)), color=linecolor3);
    graph.draw_line( (0, (wilobj.config.playareapixels[1]/2) + (2*no*100)) , (wilobj.config.playareapixels[0], (wilobj.config.playareapixels[1]/2) + (2*no*100)), color=linecolor3);
# middle cross is a bit thicker, and color1 (white)
graph.draw_line( (wilobj.config.playareapixels[0]/2, 0), (wilobj.config.playareapixels[0]/2, wilobj.config.playareapixels[1]), color=linecolor1, width=2);
graph.draw_line( (0, wilobj.config.playareapixels[1]/2), (wilobj.config.playareapixels[0], wilobj.config.playareapixels[1]/2), color=linecolor1, width=2);

trackernames = wilobj.get_tracker_names();
trackercount = len(trackernames);
trackedobjs = {};
for tracker in trackernames:
    trackedobjs[tracker] = {};
    trackedobjs[tracker]['posraw']      = [ 0, 0, 0 ];
    trackedobjs[tracker]['oriraw']      = [ 0, 0, 0, 0 ];
    trackedobjs[tracker]['pos']         = [ 0, 0, 0 ];
    trackedobjs[tracker]['pospixel']    = [ wilobj.config.playareapixels[0]/2, wilobj.config.playareapixels[1]/2 ];
    trackedobjs[tracker]['orideg']      = 0;
    trackedobjs[tracker]['orirad']      = 0;
    trackedobjs[tracker]['plotobj']     = 0;
    trackedobjs[tracker]['plotsize']    = wilobj.config.trackers[tracker]['radius'];
    trackedobjs[tracker]['plotoriobj']      = 0;
    trackedobjs[tracker]['plotorimarkobj']  = 0;
    trackedobjs[tracker]['plotselectedobj'] = 0;
    trackedobjs[tracker]['plotlabelobj']    = 0;
    trackedobjs[tracker]['plotoutsidexobj']  = 0;
    trackedobjs[tracker]['plotoutsideyobj']  = 0;
    trackedobjs[tracker]['plotlabeloffset'] = 50;
    trackedobjs[tracker]['plotlabeltext']   = wilobj.config.trackers[tracker]['labeltext'];
    trackedobjs[tracker]['color']           = wilobj.config.trackers[tracker]['color'];
#    trackedobjs[tracker]['fillcolor']       = wilobj.config.trackers[tracker]['color'];
    trackedobjs[tracker]['fillcolor']       = None;
    trackedobjs[tracker]['linewidth']       = 7;

dragpos = [ -1, -1 ];
needoffsetupdate = True;
offset_label = 0;
individualtrackermode = False;
individualtrackermode_whichtracker = 0;
individualtracker_yawoffset_trackerself = 1;
paused = False;
capture_to_file = False;
capture_bgflash_counter = 0;
capturefile = None;


print("Waiting for all the tracked devices to appear...");
while not wilobj.all_poses_valid():
    if wilobj.update() != 0:
        print("WIL update error!");
        break

print("I see all the tracked devices.");

def gen_calibdata():
        calibdata = "wxoff: %03.3f wyoff: %03.3f wzoff: %03.3f wyaw: %05.1f wpitch: %05.1f wroll: %05.1f wyaw_t: %05.1f wpitch_t: %05.1f wroll_t: %05.1f pixrat: %d swapx: %d swapy: %d revyaw: %d revpitch: %d revroll: %d\r\n"% \
                     (xoffset_world, yoffset_world, zoffset_world,
                      math.degrees(yawoffset_world), math.degrees(pitchoffset_world), math.degrees(rolloffset_world),
                      math.degrees(yawoffset_trackerself), math.degrees(pitchoffset_trackerself), math.degrees(rolloffset_trackerself),
                      pixelratio, swapx, swapy, reverse_yawdir, reverse_pitchdir, reverse_rolldir);
        for trackername in trackernames:
            if trackername[-4:] == '-PTR':  # exclude pointer trackers, as those are redundant
                continue
            trackcalibdata = wilobj.trackers[trackername].get_calibration_data_tracker();
            calibdata += "tracker: %s xoff: %03.3f yoff: %03.3f zoff: %03.3f yawoff_t: %05.1f pitchoff_t: %05.1f rolloff_t: %05.1f\r\n"%(
                wilobj.config.trackers[trackername]['serial'],
                trackcalibdata[0], trackcalibdata[1], trackcalibdata[2],
                math.degrees(trackcalibdata[3]), math.degrees(trackcalibdata[4]), math.degrees(trackcalibdata[5]) );

        return calibdata


while True:

    if capture_bgflash_counter > 0:
        capture_bgflash_counter -= 1;
        if capture_bgflash_counter == 0:
            graph.update(background_color = windowbackgroundcolor);
            needoffsetupdate = True;
            capture_to_file = True;
            capturefilename = 'wil_data_q' + datetime.datetime.today().strftime("_%Y_%m_%d__%H-%M-%S") + '.csv';
            capturefile = open(capturefilename, "w", newline="\n");
            calibdatafile = open(capturefilename[:-4] + '__' + calibdata_filename, "w", newline="\n");
            calibdatafile.write(gen_calibdata());
            calibdatafile.close();

    event, values = window.read(1);

    if event in ["space:65", " "]:
        paused = not paused;
        needoffsetupdate = True;

    if not paused:
        if wilobj.update() != 0:
            print("WIL update error!");
            break

    if wilobj.all_poses_valid():

        for trackername in trackernames:

            if wilobj.trackers[trackername].was_button_pressed(['system', 'menu']):
                if trackedobjs[trackername]['plotsize'] == plotsize_small:
                    trackedobjs[trackername]['plotsize'] = plotsize_large;
                else:
                    trackedobjs[trackername]['plotsize'] = plotsize_small;

            trackedobjs[trackername]['posraw']      = wilobj.trackers[trackername].get_raw_position();
            trackedobjs[trackername]['oriraw']      = wilobj.trackers[trackername].get_raw_orientation_euler_degrees();
            trackedobjs[trackername]['orirawq']     = wilobj.trackers[trackername].get_raw_orientation_quat();
            trackedobjs[trackername]['pos']         = wilobj.trackers[trackername].get_position();
            trackedobjs[trackername]['yawdeg']      = wilobj.trackers[trackername].get_yaw_degrees();
            trackedobjs[trackername]['yawrad']      = wilobj.trackers[trackername].get_yaw_radians();
            trackedobjs[trackername]['pitchdeg']    = wilobj.trackers[trackername].get_pitch_degrees();
            trackedobjs[trackername]['pitchrad']    = wilobj.trackers[trackername].get_pitch_radians();
            trackedobjs[trackername]['rolldeg']     = wilobj.trackers[trackername].get_roll_degrees();
            trackedobjs[trackername]['rollrad']     = wilobj.trackers[trackername].get_roll_radians();
            trackedobjs[trackername]['pospixel']    = wilobj.trackers[trackername].get_position_pixel();

            if capture_to_file:
                capturetime = time.time();
                capturefile.write("%s,%s,%f,%f,%f,%f,%f,%f,%f\r\n"%(
                        capturetime, wilobj.trackers[trackername].serial,
                        trackedobjs[trackername]['posraw'][0], trackedobjs[trackername]['posraw'][1], trackedobjs[trackername]['posraw'][2],
                        trackedobjs[trackername]['orirawq'][0], trackedobjs[trackername]['orirawq'][1], trackedobjs[trackername]['orirawq'][2], trackedobjs[trackername]['orirawq'][3]
                    ));
                capturefile.write("%s,*%s,%d,%d,%d,%f,%d,%d,%f,%f\r\n"%(
                        capturetime, wilobj.trackers[trackername].serial,
                        wilobj.trackers[trackername].buttons['system'],
                        wilobj.trackers[trackername].buttons['menu'],
                        wilobj.trackers[trackername].buttons['grip'],
                        wilobj.trackers[trackername].buttons['trigger'],
                        wilobj.trackers[trackername].buttons['trackpad_press'],
                        wilobj.trackers[trackername].buttons['trackpad_touch'],
                        wilobj.trackers[trackername].buttons['trackpad_x'],
                        wilobj.trackers[trackername].buttons['trackpad_y']
                    ));

            graph.delete_figure(trackedobjs[trackername]['plotobj']);
            graph.delete_figure(trackedobjs[trackername]['plotselectedobj']);
            graph.delete_figure(trackedobjs[trackername]['plotoriobj']);
            graph.delete_figure(trackedobjs[trackername]['plotorimarkobj']);
            graph.delete_figure(trackedobjs[trackername]['plotlabelobj']);
            graph.delete_figure(trackedobjs[trackername]['plotoutsidexobj']);
            graph.delete_figure(trackedobjs[trackername]['plotoutsideyobj']);

            if trackedobjs[trackername]['pospixel'] != None:

                trackedobjs[trackername]['pospixel'][0] = trackedobjs[trackername]['pospixel'][0] + wilobj.config.playareapixels[0]/2;
                trackedobjs[trackername]['pospixel'][1] = trackedobjs[trackername]['pospixel'][1] + wilobj.config.playareapixels[1]/2;

                # draw thick lines for giving a hint when the sensed positions are outside of the playarea
                # vertical axis
                if not (0 < trackedobjs[trackername]['pospixel'][0] < wilobj.config.playareapixels[0]):

                    if trackedobjs[trackername]['pospixel'][1] < 40:
                        plotoutsidexbar_posy_top = 0;
                        plotoutsidexbar_posy_bottom = 80;
                    elif trackedobjs[trackername]['pospixel'][1] > (wilobj.config.playareapixels[1] - 40):
                        plotoutsidexbar_posy_top = wilobj.config.playareapixels[1] - 80;
                        plotoutsidexbar_posy_bottom = wilobj.config.playareapixels[1];
                    else:
                        plotoutsidexbar_posy_top = trackedobjs[trackername]['pospixel'][1] - 40;
                        plotoutsidexbar_posy_bottom = trackedobjs[trackername]['pospixel'][1] + 40;

                    if trackedobjs[trackername]['pospixel'][0] < 0:
                        plotoutsidexbar_posx = 15;
                    else:
                        plotoutsidexbar_posx = wilobj.config.playareapixels[0] - 15;

                    trackedobjs[trackername]['plotoutsidexobj'] = graph.draw_line(
                        (plotoutsidexbar_posx, plotoutsidexbar_posy_top),
                        (plotoutsidexbar_posx, plotoutsidexbar_posy_bottom),
                        trackedobjs[trackername]['color'], width=30
                    );
                # horiziontal axis
                if not (0 < trackedobjs[trackername]['pospixel'][1] < wilobj.config.playareapixels[1]):

                    if trackedobjs[trackername]['pospixel'][0] < 40:
                        plotoutsidexbar_posx_left = 0;
                        plotoutsidexbar_posx_right = 80;
                    elif trackedobjs[trackername]['pospixel'][0] > (wilobj.config.playareapixels[0] - 40):
                        plotoutsidexbar_posx_left = wilobj.config.playareapixels[0] - 80;
                        plotoutsidexbar_posx_right = wilobj.config.playareapixels[0];
                    else:
                        plotoutsidexbar_posx_left = trackedobjs[trackername]['pospixel'][0] - 40;
                        plotoutsidexbar_posx_right = trackedobjs[trackername]['pospixel'][0] + 40;

                    if trackedobjs[trackername]['pospixel'][1] < 0:
                        plotoutsidexbar_posy = 15;
                    else:
                        plotoutsidexbar_posy = wilobj.config.playareapixels[1] - 15;

                    trackedobjs[trackername]['plotoutsideyobj'] = graph.draw_line(
                        (plotoutsidexbar_posx_left, plotoutsidexbar_posy),
                        (plotoutsidexbar_posx_right, plotoutsidexbar_posy),
                        trackedobjs[trackername]['color'], width=30
                    );

                if trackedobjs[trackername]['pospixel'][1] < trackedobjs[trackername]['plotsize'] + 80:
                    trackedobjs[trackername]['plotlabeloffset'] = trackedobjs[trackername]['plotsize'] + 40;
                else:
                    trackedobjs[trackername]['plotlabeloffset'] = -trackedobjs[trackername]['plotsize'] - 40;

                trackertext = "%s %03.3f %03.3f %03.3f %03.2f %03.2f %03.2f\n      (%03.3f %03.3f %03.3f %03.2f %03.2f %03.2f)"%(
                        trackedobjs[trackername]['plotlabeltext'],
                        trackedobjs[trackername]['pos'][0], trackedobjs[trackername]['pos'][1], trackedobjs[trackername]['pos'][2],
                        trackedobjs[trackername]['yawdeg'], trackedobjs[trackername]['pitchdeg'], trackedobjs[trackername]['rolldeg'],
                        trackedobjs[trackername]['posraw'][0], trackedobjs[trackername]['posraw'][1], trackedobjs[trackername]['posraw'][2],
                        trackedobjs[trackername]['oriraw'][wilobj.trackers[trackername].yawaxis], trackedobjs[trackername]['oriraw'][wilobj.trackers[trackername].pitchaxis], trackedobjs[trackername]['oriraw'][wilobj.trackers[trackername].rollaxis] );

                if wilobj.trackers[trackername].trackertype == 2:  # pointer tracker
                    trackedobjs[trackername]['plotobj'] = graph.draw_circle(trackedobjs[trackername]['pospixel'], plotsize_small * (1 + 2*wilobj.trackers[trackername].buttons['trigger']), line_color=trackedobjs[trackername]['color'], fill_color=trackedobjs[trackername]['color'], line_width=trackedobjs[trackername]['linewidth']);
                    # permanent
                    if wilobj.trackers[trackername].buttons['trackpad_press']:
                        graph.draw_circle(trackedobjs[trackername]['pospixel'], plotsize_small/2, line_color=trackedobjs[trackername]['color'], fill_color=trackedobjs[trackername]['color'], line_width=trackedobjs[trackername]['linewidth']);

                else:
                    trackedobjs[trackername]['plotobj']        = graph.draw_circle(trackedobjs[trackername]['pospixel'], trackedobjs[trackername]['plotsize'], line_color=trackedobjs[trackername]['color'], fill_color=trackedobjs[trackername]['fillcolor'], line_width=trackedobjs[trackername]['linewidth']);
                    trackedobjs[trackername]['plotoriobj']     = draw_rotated_line(graph,
                            [ [ trackedobjs[trackername]['pospixel'][0], trackedobjs[trackername]['pospixel'][1] - trackedobjs[trackername]['plotsize']*2 ],
                              [ trackedobjs[trackername]['pospixel'][0], trackedobjs[trackername]['pospixel'][1] + trackedobjs[trackername]['plotsize']*2 ] ],
                            trackedobjs[trackername]['yawrad'], trackedobjs[trackername]['color'], linewidth=5);
                    trackedobjs[trackername]['plotorimarkobj'] = draw_rotated_circle(graph,
                            trackedobjs[trackername]['pospixel'], trackedobjs[trackername]['plotsize']/2,
                            trackedobjs[trackername]['yawrad'], trackedobjs[trackername]['plotsize']*2, trackedobjs[trackername]['color'], linewidth=3);

                trackedobjs[trackername]['plotlabelobj']   = graph.draw_text(trackertext,
                        [ trackedobjs[trackername]['pospixel'][0], trackedobjs[trackername]['pospixel'][1] + trackedobjs[trackername]['plotlabeloffset'] ],
                        color=trackedobjs[trackername]['color'], font=statusfont);

                if individualtrackermode and individualtrackermode_whichtracker == trackername:
                    trackedobjs[trackername]['plotselectedobj'] = graph.draw_circle(trackedobjs[trackername]['pospixel'], trackedobjs[trackername]['plotsize'] + 40, line_color='white', line_width=5);

            else:  # pospixel is None
                trackedobjs[trackername]['plotobj'] = 0;

    # start/stop capture
    if event in ["c:54", "c"]:
        if capture_to_file:
            capture_to_file = False;
            capturefile.close();
        else:
            capture_bgflash_counter = 100;
            graph.update(background_color = 'white');

    # choose individual trackers for calibration
    if event in ["1:10", "1", "2:11", "2", "3:12", "3", "4:13", "4", "5:14", "5", "6:15", "6", "7:16", "7", "8:17", "8", "9:18", "9", "0:19", "0"]:
        selectedtrackerno = int(event[0]) - 1;
        if selectedtrackerno == -1:
            selectedtrackerno = 10;
        if selectedtrackerno < trackercount:
            if individualtrackermode and individualtrackermode_whichtracker == trackernames[selectedtrackerno]:
                individualtrackermode = False;
            else:
                individualtrackermode = True;
                individualtrackermode_whichtracker = trackernames[selectedtrackerno];
                individualtracker_xoffset = wilobj.trackers[individualtrackermode_whichtracker].xoffset_tracker;
                individualtracker_yoffset = wilobj.trackers[individualtrackermode_whichtracker].yoffset_tracker;
                individualtracker_zoffset = wilobj.trackers[individualtrackermode_whichtracker].zoffset_tracker;
                individualtracker_yawoffset_trackerself   = wilobj.trackers[individualtrackermode_whichtracker].yawoffset_trackerself_tracker;
                individualtracker_pitchoffset_trackerself = wilobj.trackers[individualtrackermode_whichtracker].pitchoffset_trackerself_tracker;
                individualtracker_rolloffset_trackerself  = wilobj.trackers[individualtrackermode_whichtracker].rolloffset_trackerself_tracker;
            needoffsetupdate = True;

    # back to world calibration (from individual tracker calibration)
    if event in ["BackSpace:22"]:
        needoffsetupdate = True;
        individualtrackermode = False;

    if event in ["KP_Add:86", "plus:21", "equal:21", "+"] and not individualtrackermode:
        pixelratio += 5;
        needoffsetupdate = True;

    if event in ["KP_Subtract:82", "underscore:20", "minus:20", "-"] and not individualtrackermode:
        pixelratio -= 5;
        needoffsetupdate = True;

    if event in ["KP_Divide:106", "x:53", "x"] and not individualtrackermode:
        swapx = not swapx;
        needoffsetupdate = True;

    if event in ["KP_Multiply:63", "y:29", "y"] and not individualtrackermode:
        swapy = not swapy;
        needoffsetupdate = True;

    if event in ["r:27", "r"] and not individualtrackermode:
        reverse_yawdir = not reverse_yawdir;
        needoffsetupdate = True;

    if event in ["z:52", "z"]:
        needoffsetupdate = True;
        if individualtrackermode:
            zoffset_world = -trackedobjs[individualtrackermode_whichtracker]['posraw'][2];
            individualtrackermode = False;
        else:
            zoffset_world = -min([ trackedobjs[trackername]['posraw'][2] for trackername in trackernames ]);

    if event in (sg.WIN_CLOSED, 'Escape:9', 'Escape:27'):
        print("EXIT: Not saving calibration data!");
        break

    if event in ("Return:36", "KP_Enter:104", "\n", "\r"):

        if os.path.exists(calibdata_filename):
            calibdata_filename_backup_timestamp = datetime.datetime.today().strftime("_%Y_%m_%d__%H-%M-%S");
            calibdata_filename_backup = calibdata_filename[:-4] + calibdata_filename_backup_timestamp + ".txt";
            calibdata_filename_backup_seqno = 0;
            while os.path.exists(calibdata_filename_backup):
                calibdata_filename_backup_seqno += 1;
                calibdata_filename_backup = calibdata_filename[:-4] + calibdata_filename_backup_timestamp + "_%d"%(calibdata_filename_backup_seqno) + ".txt";
            print("Backing up previous calibration parameters file as:", calibdata_filename_backup);
            os.rename(calibdata_filename, calibdata_filename_backup);

        calibdata = gen_calibdata();
        print("Saving calibration parameters: ", calibdata);
        calibdatafile = open(calibdata_filename, "w", newline="\n");
        calibdatafile.write(calibdata);
        calibdatafile.close();
        break

    if (event == '-GRAPH-'):
        window.set_cursor("cross_reverse");
        if dragpos == [ -1, -1 ]:
            dragpos = [ values['-GRAPH-'][0], values['-GRAPH-'][1] ];
        else:
            newdragpos = [ values['-GRAPH-'][0], values['-GRAPH-'][1] ];
            dragposdiff_x = (newdragpos[0] - dragpos[0]) / pixelratio;
            dragposdiff_y = (newdragpos[1] - dragpos[1]) / pixelratio;
            if individualtrackermode:
                individualtracker_xoffset += dragposdiff_x;
                individualtracker_yoffset += dragposdiff_y;
            else:
                xoffset_world += dragposdiff_x;
                yoffset_world += dragposdiff_y;
            dragpos = newdragpos;
            needoffsetupdate = True;

    if (event == '-GRAPH-+UP'):
        window.set_cursor("arrow");
        dragpos = [ -1, -1 ];
        needoffsetupdate = True;

    if event in ("+SCRDN+", "MouseWheel:Down"):
        if dragpos == [ -1, -1 ]:
            if not individualtrackermode:
                yawoffset_world -= math.radians(0.5);
                if yawoffset_world < 0:
                    yawoffset_world = math.radians(359.5);
        else:
            temp_yawoffset_trackerself = [ yawoffset_trackerself, individualtracker_yawoffset_trackerself][individualtrackermode] - math.radians(0.5);
            if temp_yawoffset_trackerself < 0:
                temp_yawoffset_trackerself = math.radians(359.5);
            if individualtrackermode:
                individualtracker_yawoffset_trackerself = temp_yawoffset_trackerself;
            else:
                yawoffset_trackerself = temp_yawoffset_trackerself;
        needoffsetupdate = True;

    if event in ("+SCRUP+", "MouseWheel:Up"):
        if dragpos == [ -1, -1 ]:
            if not individualtrackermode:
                yawoffset_world += math.radians(0.5);
                if yawoffset_world >= (2*math.pi):
                    yawoffset_world = 0;
        else:
            temp_yawoffset_trackerself = [ yawoffset_trackerself, individualtracker_yawoffset_trackerself][individualtrackermode] + math.radians(0.5);
            if temp_yawoffset_trackerself >= (2*math.pi):
                temp_yawoffset_trackerself = 0;
            if individualtrackermode:
                individualtracker_yawoffset_trackerself = temp_yawoffset_trackerself;
            else:
                yawoffset_trackerself = temp_yawoffset_trackerself;
        needoffsetupdate = True;

    if needoffsetupdate:

        if individualtrackermode:
            offset_text = "Offset(%s:%s): %03.3f %03.3f %03.3f YawT:%05.1f PitchT:%05.1f RollT:%05.1f"% \
                          (individualtrackermode_whichtracker, wilobj.config.trackers[individualtrackermode_whichtracker]['serial'],
                           individualtracker_xoffset, individualtracker_yoffset, individualtracker_zoffset,
                           math.degrees(individualtracker_yawoffset_trackerself),
                           math.degrees(individualtracker_pitchoffset_trackerself),
                           math.degrees(individualtracker_rolloffset_trackerself) );
            wilobj.trackers[individualtrackermode_whichtracker].calibrate_tracker(
                    individualtracker_xoffset, individualtracker_yoffset, individualtracker_zoffset,
                    individualtracker_yawoffset_trackerself, individualtracker_pitchoffset_trackerself, individualtracker_rolloffset_trackerself);

        else:

            if swapx:           swapx_char = '!';
            else:               swapx_char = ' ';
            if swapy:           swapy_char = '!';
            else:               swapy_char = ' ';
            if reverse_yawdir:  revyaw_char = '!';
            else:               revyaw_char = ' ';
            offset_text = "%sOffset: %03.3f%c %03.3f%c %03.3f Yw/Yt:%05.1f/%05.1f%c Pw/Pt:%05.1f/%05.1f Rw/Rt:%05.1f/%05.1f pixrat: %d"% \
                          (["", "CAPTURING "][int(capture_to_file)],
                           xoffset_world, swapx_char, yoffset_world, swapy_char, zoffset_world,
                           math.degrees(yawoffset_world), math.degrees(yawoffset_trackerself), revyaw_char,
                           math.degrees(pitchoffset_world), math.degrees(pitchoffset_trackerself),
                           math.degrees(rolloffset_world), math.degrees(rolloffset_trackerself),
                           pixelratio);
            wilobj.calibrate_world(xoffset_world, yoffset_world, zoffset_world,
                                   yawoffset_world,   yawoffset_trackerself,
                                   pitchoffset_world, pitchoffset_trackerself,
                                   rolloffset_world,  rolloffset_trackerself,
                                   pixelratio, swapx, swapy,
                                   reverse_yawdir, reverse_pitchdir, reverse_rolldir);

        graph.delete_figure(offset_label);
        offset_label = graph.draw_text(offset_text, [20, 20], color='#FFFFFF', font=statusfont, text_location = sg.TEXT_LOCATION_LEFT);
        needoffsetupdate = False;


window.close();

if capturefile != None:
    capturefile.close();
