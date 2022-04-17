# WYSIWYG Indoor Localization
#
# Find calibration parameters
#   Adjust localization sys data to the real environment (using floor projection)
#
# Usage:
#  mouse dragging with left button pressed: adjust x,y offset
#  mouse scrollwheel: adjust world orientation offset
#  mouse scrollwheel with left button pressed: adjust object orientation offset
#  keys + - : adjust pixratio
#  keys x y r : toggle swap x, y, rotdir
#  key Esc : exit without saving calibration parameters
#  key Enter : save calibration parameters and exit
#
# Author: David Vincze
#
# https://github.com/szaguldo-kamaz/
#

import math, sys
import PySimpleGUI as sg
from wil_config  import wil_config
from WIL import WIL
from draw_rotated_things.draw_rotated_things import *


# configuration

#floorprojectionmode = True; # fullscreen
floorprojectionmode = False; # windowed - for testing
calibdata_filename_in  = "wil_calibparams-OK.txt";
calibdata_filename_out = "wil_calibparams-NEW.txt";
default_pixelratio = wil_config.playareapixels[1] / 4;
default_swapx = False;
default_swapy = True;
default_reverse_rotdir = True;
windowbackgroundcolor = '#000000';
linecolor1 = '#FFFFFF';
linecolor2 = '#00FF00';
linecolor3 = '#FF00FF';
statusfont = "Verdana 14";
plotsize_small = 15;
plotsize_large = 40;


### start ###


wilobj = WIL(wil_config.locdata_source, wil_config.playareapixels);
for trackername in wil_config.trackers.keys():
    wilobj.add_tracker(trackername, wil_config.trackers[trackername]['serial']);
    wilobj.trackers[trackername].set_rotaxis(wil_config.trackers[trackername]['rotaxis']);

# try to read previous calibration config data
if wilobj.calibrate_from_file(calibdata_filename_in):
    [ xoffset, yoffset, zoffset, orientoffset_world, orientoffset_obj, pixelratio, swapx, swapy, reverse_rotdir ] = wilobj.get_calibration_data();
    print("Calibration data loaded from: %s"%(calibdata_filename_in));
else:
    print("Cannot load calibration data from: %s, using default values."%(calibdata_filename_in));
    xoffset = 0.0;
    yoffset = 0.0;
    zoffset = 0.0;
    orientoffset_world = 0.0;
    orientoffset_obj   = 0.0;
    pixelratio = default_pixelratio;
    swapx = default_swapx;
    swapy = default_swapy;
    reverse_rotdir = default_reverse_rotdir;
    wilobj.calibrate(xoffset, yoffset, zoffset, orientoffset_world, orientoffset_obj, pixelratio, swapx, swapy, reverse_rotdir);

# init gui
sg.theme('DarkGrey5');
graphsize = (wil_config.playareapixels[0], wil_config.playareapixels[1]);
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
graph.draw_rectangle( [1, 1], [wil_config.playareapixels[0] - 2, wil_config.playareapixels[1] - 1], line_color=linecolor1, line_width=3);

# color2
for no in range(0,4):
    graph.draw_line( ((wil_config.playareapixels[0]/2) - (2*no*100) - 100, 0) , ((wil_config.playareapixels[0]/2) - (2*no*100)-100,wil_config.playareapixels[1]), color=linecolor2);
    graph.draw_line( ((wil_config.playareapixels[0]/2) + (2*no*100) + 100, 0) , ((wil_config.playareapixels[0]/2) + (2*no*100)+100,wil_config.playareapixels[1]), color=linecolor2);
for no in range(0,3):
    graph.draw_line( (0, (wil_config.playareapixels[1]/2) - (2*no*100) - 100, 0) , (wil_config.playareapixels[0], (wil_config.playareapixels[1]/2) - (2*no*100) - 100), color=linecolor2);
    graph.draw_line( (0, (wil_config.playareapixels[1]/2) + (2*no*100) + 100, 0) , (wil_config.playareapixels[0], (wil_config.playareapixels[1]/2) + (2*no*100) + 100), color=linecolor2);
# color3 should be above color2 lines
for no in range(1,4):
    graph.draw_line( ((wil_config.playareapixels[0]/2) - (2*no*100),0) , ((wil_config.playareapixels[0]/2) - (2*no*100),wil_config.playareapixels[1]), color=linecolor3);
    graph.draw_line( ((wil_config.playareapixels[0]/2) + (2*no*100),0) , ((wil_config.playareapixels[0]/2) + (2*no*100),wil_config.playareapixels[1]), color=linecolor3);
for no in range(1,3):
    graph.draw_line( (0, (wil_config.playareapixels[1]/2) - (2*no*100)) , (wil_config.playareapixels[0], (wil_config.playareapixels[1]/2) - (2*no*100)), color=linecolor3);
    graph.draw_line( (0, (wil_config.playareapixels[1]/2) + (2*no*100)) , (wil_config.playareapixels[0], (wil_config.playareapixels[1]/2) + (2*no*100)), color=linecolor3);
# middle cross is a bit thicker, and color1 (white)
graph.draw_line( (wil_config.playareapixels[0]/2, 0), (wil_config.playareapixels[0]/2, wil_config.playareapixels[1]), color=linecolor1, width=2);
graph.draw_line( (0, wil_config.playareapixels[1]/2), (wil_config.playareapixels[0], wil_config.playareapixels[1]/2), color=linecolor1, width=2);

trackedobjs = {};
for tracker in wilobj.get_tracker_names():
    trackedobjs[tracker] = {};
    trackedobjs[tracker]['posraw']      = [ 0, 0, 0 ];
    trackedobjs[tracker]['oriraw']      = [ 0, 0, 0, 0 ];
    trackedobjs[tracker]['pos']         = [ 0, 0, 0 ];
    trackedobjs[tracker]['pospixel']    = [ wil_config.playareapixels[0]/2, wil_config.playareapixels[1]/2 ];
    trackedobjs[tracker]['orideg']      = 0;
    trackedobjs[tracker]['orirad']      = 0;
    trackedobjs[tracker]['plotobj']     = 0;
    trackedobjs[tracker]['plotsize']    = plotsize_small;
    trackedobjs[tracker]['plotoriobj']      = 0;
    trackedobjs[tracker]['plotorimarkobj']  = 0;
    trackedobjs[tracker]['plotlabelobj']    = 0;
    trackedobjs[tracker]['plotlabeloffset'] = 50;
    trackedobjs[tracker]['plotlabeltext']   = wil_config.trackers[tracker]['labeltext'];
    trackedobjs[tracker]['color']           = wil_config.trackers[tracker]['color'];

#trackedobjs[tracker]['plotsize'] = plotsize_small;
#robotpos_plotsize       = 80;
#toypos_plotsize         = 35;
#ownerpos_plotsize       = 110;
#strangerpos_plotsize    = 35;

dragpos = [ -1, -1 ];
needoffsetupdate = True;
offset_label = 0;

print("Waiting for all the tracked devices to appear...");
while not wilobj.all_poses_valid():
    if wilobj.update() != 0:
        print("WIL update error!");
        break

print("I see all the tracked devices.");

while True:

    event, values = window.read(1);

    if wilobj.update() != 0:
        print("WIL update error!");
        break

    if wilobj.all_poses_valid():

        for trackername in wilobj.get_tracker_names():

            if wilobj.trackers[trackername].was_button_pressed():
                if trackedobjs[trackername]['plotsize'] == plotsize_small:
                    trackedobjs[trackername]['plotsize'] = plotsize_large;
                else:
                    trackedobjs[trackername]['plotsize'] = plotsize_small;

            trackedobjs[trackername]['posraw']      = wilobj.trackers[trackername].get_raw_position();
            trackedobjs[trackername]['oriraw']      = wilobj.trackers[trackername].get_raw_orientation_euler_degrees();
            trackedobjs[trackername]['pos']         = wilobj.trackers[trackername].get_position();
            trackedobjs[trackername]['orideg']      = wilobj.trackers[trackername].get_orientation_degrees();
            trackedobjs[trackername]['orirad']      = wilobj.trackers[trackername].get_orientation_radians();
            trackedobjs[trackername]['pospixel']    = wilobj.trackers[trackername].get_position_pixel();
            trackedobjs[trackername]['pospixel'][0] = trackedobjs[trackername]['pospixel'][0] + wil_config.playareapixels[0]/2;
            trackedobjs[trackername]['pospixel'][1] = trackedobjs[trackername]['pospixel'][1] + wil_config.playareapixels[1]/2;

            if trackedobjs[trackername]['pospixel'][1] > (wil_config.playareapixels[1]-80):
                trackedobjs[trackername]['labeloffset'] = -70;
            else:
                trackedobjs[trackername]['labeloffset'] = 50;

            graph.delete_figure(trackedobjs[trackername]['plotobj']);
            graph.delete_figure(trackedobjs[trackername]['plotoriobj']);
            graph.delete_figure(trackedobjs[trackername]['plotorimarkobj']);
            graph.delete_figure(trackedobjs[trackername]['plotlabelobj']);

            trackertext = "%s %03.3f %03.3f %03.3f %03.3f\n      (%03.3f %03.3f %03.3f %03.2f)"%(
                    trackedobjs[trackername]['plotlabeltext'],
                    trackedobjs[trackername]['pos'][0], trackedobjs[trackername]['pos'][1], trackedobjs[trackername]['pos'][2],
                    trackedobjs[trackername]['orideg'],
                    trackedobjs[trackername]['posraw'][0], trackedobjs[trackername]['posraw'][1], trackedobjs[trackername]['posraw'][2],
                    trackedobjs[trackername]['oriraw'][2]);

            trackedobjs[trackername]['plotobj']        = graph.draw_circle(trackedobjs[trackername]['pospixel'], trackedobjs[trackername]['plotsize'], line_color=trackedobjs[trackername]['color'], fill_color=trackedobjs[trackername]['color']);
            trackedobjs[trackername]['plotoriobj']     = draw_rotated_line(graph,
                    [ [ trackedobjs[trackername]['pospixel'][0], trackedobjs[trackername]['pospixel'][1] - trackedobjs[trackername]['plotsize']*2 ], 
                      [ trackedobjs[trackername]['pospixel'][0], trackedobjs[trackername]['pospixel'][1] + trackedobjs[trackername]['plotsize']*2 ] ], 
                    trackedobjs[trackername]['orirad'], trackedobjs[trackername]['color'], linewidth=5);
            trackedobjs[trackername]['plotorimarkobj'] = draw_rotated_circle(graph,
                    trackedobjs[trackername]['pospixel'], trackedobjs[trackername]['plotsize']/2,
                    trackedobjs[trackername]['orirad'], trackedobjs[trackername]['plotsize']*2, trackedobjs[trackername]['color'], linewidth=3);
            trackedobjs[trackername]['plotlabelobj']   = graph.draw_text(trackertext,
                    [ trackedobjs[trackername]['pospixel'][0], trackedobjs[trackername]['pospixel'][1] + trackedobjs[trackername]['plotlabeloffset'] ],
                    color=trackedobjs[trackername]['color'], font=statusfont);


    if event in ["KP_Add:86", "plus:21", "equal:21", "+"]:
        pixelratio += 5;
        needoffsetupdate = True;

    if event in ["KP_Subtract:82", "underscore:20", "minus:20", "-"]:
        pixelratio -= 5;
        needoffsetupdate = True;

    if event in ["KP_Divide:106", "x:53", "x"]:
        swapx = not swapx;
        needoffsetupdate = True;

    if event in ["KP_Multiply:63", "y:29", "y"]:
        swapy = not swapy;
        needoffsetupdate = True;

    if event in ["r:27", "r"]:
        reverse_rotdir = not reverse_rotdir;
        needoffsetupdate = True;

    if event in (sg.WIN_CLOSED, 'Escape:9', 'Escape:27'):
        print("EXIT: Not saving calibration data!");
        break

    if event in ("Return:36", "KP_Enter:104", "\n", "\r"):
        calibdata = "xoff: %03.3f yoff: %03.3f zoff: %03.3f rotoff_w: %05.1f rotoff_o: %05.1f pixrat: %d swapx: %d swapy: %d revrot: %d%c%c"%(xoffset, yoffset, zoffset, math.degrees(orientoffset_world), math.degrees(orientoffset_obj), pixelratio, swapx, swapy, reverse_rotdir, 0x0D, 0x0A);
        print("Saving calibration parameters: ", calibdata);
        calibdatafile = open(calibdata_filename_out, "w");
        calibdatafile.write(calibdata);
        calibdatafile.close();
        break

    if (event == '-GRAPH-'):
        window.set_cursor("cross_reverse");
        if dragpos == [ -1, -1 ]:
            dragpos = [ values['-GRAPH-'][0], values['-GRAPH-'][1] ];
        else:
            newdragpos = [ values['-GRAPH-'][0], values['-GRAPH-'][1] ];
            xoffset += (newdragpos[0] - dragpos[0]) / pixelratio;
            yoffset += (newdragpos[1] - dragpos[1]) / pixelratio;
            dragpos = newdragpos;
            needoffsetupdate = True;

    if (event == '-GRAPH-+UP'):
        window.set_cursor("arrow");
        dragpos = [ -1, -1 ];
        needoffsetupdate = True;

    if event in ("+SCRDN+", "MouseWheel:Down"):
        if dragpos == [ -1, -1 ]:
            orientoffset_world -= math.radians(0.5);
            if orientoffset_world < 0:
                orientoffset_world = math.radians(359.5);
        else:
            orientoffset_obj -= math.radians(0.5);
            if orientoffset_obj < 0:
                orientoffset_obj = math.radians(359.5);
        needoffsetupdate = True;

    if event in ("+SCRUP+", "MouseWheel:Up"):
        if dragpos == [ -1, -1 ]:
            orientoffset_world += math.radians(0.5);
            if orientoffset_world >= (2*math.pi):
                orientoffset_world = 0;
        else:
            orientoffset_obj += math.radians(0.5);
            if orientoffset_obj >= (2*math.pi):
                orientoffset_obj = 0;
        needoffsetupdate = True;

    if needoffsetupdate:
        graph.delete_figure(offset_label);
        if swapx:           swapx_char = '!';
        else:               swapx_char = ' ';
        if swapy:           swapy_char = '!';
        else:               swapy_char = ' ';
        if reverse_rotdir:  revrot_char = '!';
        else:               revrot_char = ' ';
        offset_text = "Offset: %03.3f%c %03.3f%c %03.3f Rw/Ro:%05.1f/%05.1f%c pixrat: %d"%(xoffset, swapx_char, yoffset, swapy_char, zoffset, math.degrees(orientoffset_world), math.degrees(orientoffset_obj), revrot_char, pixelratio);
        offset_label = graph.draw_text(offset_text, [320, 20], color='#FFFFFF', font=statusfont);
        needoffsetupdate = False;
        wilobj.calibrate(xoffset, yoffset, zoffset, orientoffset_world, orientoffset_obj, pixelratio, swapx, swapy, reverse_rotdir);


window.close();
