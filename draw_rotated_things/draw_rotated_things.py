# draw_rotated_things v0.3
# for use with PySimpleGUI
# see examples (Demo_draw_rotated_*)
#
# author: David Vincze
# github.com/szaguldo-kamaz/
#

import math


def calc_rotated_point(coord_center, rotcentangle, rotcentdist):

    coord = (coord_center[0], coord_center[1] - rotcentdist)
    cosangle = math.cos(rotcentangle)
    sinangle = math.sin(rotcentangle)

    coord_rot = ((coord[0] - coord_center[0]) * cosangle - (coord[1] - coord_center[1]) * sinangle + coord_center[0],
                 (coord[0] - coord_center[0]) * sinangle + (coord[1] - coord_center[1]) * cosangle + coord_center[1])

    return coord_rot


def calc_rotated_polygon(polycoords, polycenter, angle, rotcentangle=0, rotcentdist=0):

    cosangle = math.cos(angle)
    sinangle = math.sin(angle)

    cosangle_cd = math.cos(rotcentangle)
    sinangle_cd = math.sin(rotcentangle)
    coord_cd = (polycenter[0], polycenter[1] - rotcentdist)

    coord_rot = []
    for c in range(0, len(polycoords)):
        temp = [ (polycoords[c][0] - polycenter[0]) * cosangle - (polycoords[c][1] - polycenter[1]) * sinangle + polycenter[0],
                 (polycoords[c][0] - polycenter[0]) * sinangle + (polycoords[c][1] - polycenter[1]) * cosangle + polycenter[1] ]
        coord_rot.append(
               [ (temp[0] - coord_cd[0]) * cosangle_cd - (temp[1] - coord_cd[1]) * sinangle_cd + polycenter[0],
                 (temp[0] - coord_cd[0]) * sinangle_cd + (temp[1] - coord_cd[1]) * cosangle_cd + polycenter[1] ] )

    return coord_rot


def calc_rotated_line(coord, angle, rotcentangle=0, rotcentdist=0):
# this could also be just a calc_rotate_polygon wrapper...
#    polycoords = coord
#    polycenter = ( int((coord[0][0] + coord[1][0])/2), int((coord[0][1] + coord[1][1])/2) )
#    return calc_rotated_polygon(polycoords, polycenter, angle, rotcentangle=rotcentangle, rotcentdist=rotcentdist)
#
# ... but this one is probably cheaper
    coord_center = ( int((coord[0][0] + coord[1][0])/2), int((coord[0][1] + coord[1][1])/2) )
    cosangle = math.cos(angle)
    sinangle = math.sin(angle)

    coord_rot = ( ((coord[0][0] - coord_center[0]) * cosangle - (coord[0][1] - coord_center[1]) * sinangle + coord_center[0],
                   (coord[0][0] - coord_center[0]) * sinangle + (coord[0][1] - coord_center[1]) * cosangle + coord_center[1]),
                  ((coord[1][0] - coord_center[0]) * cosangle - (coord[1][1] - coord_center[1]) * sinangle + coord_center[0],
                   (coord[1][0] - coord_center[0]) * sinangle + (coord[1][1] - coord_center[1]) * cosangle + coord_center[1]) )

    if rotcentangle != 0 or rotcentdist != 0:
        cosangle_cd = math.cos(rotcentangle)
        sinangle_cd = math.sin(rotcentangle)
        coord_cd = (coord_center[0], coord_center[1] - rotcentdist)
        coord_rot = ( ((coord_rot[0][0] - coord_cd[0]) * cosangle_cd - (coord_rot[0][1] - coord_cd[1]) * sinangle_cd + coord_center[0],
                       (coord_rot[0][0] - coord_cd[0]) * sinangle_cd + (coord_rot[0][1] - coord_cd[1]) * cosangle_cd + coord_center[1]),
                      ((coord_rot[1][0] - coord_cd[0]) * cosangle_cd - (coord_rot[1][1] - coord_cd[1]) * sinangle_cd + coord_center[0],
                       (coord_rot[1][0] - coord_cd[0]) * sinangle_cd + (coord_rot[1][1] - coord_cd[1]) * cosangle_cd + coord_center[1]) )

    return coord_rot


def draw_rotated_circle(graph, coord_center, radius, angle, rotcentdist, linecolor, linewidth=1, fillcolor=None):

    coord_rot = calc_rotated_point(coord_center, angle, rotcentdist)
    return graph.draw_circle(coord_rot, radius, line_width=linewidth, line_color=linecolor, fill_color=fillcolor)


def draw_rotated_line(graph, coord, angle, color, rotcentangle=0, rotcentdist=0, linewidth=1):

    coord_rot = calc_rotated_line(coord, angle, rotcentangle, rotcentdist)
    return graph.draw_line(coord_rot[0], coord_rot[1], color=color, width=linewidth)


def draw_rotated_polygon(graph, polycoords, polycenter, angle, outlinecolor, rotcentangle=0, rotcentdist=0, fill=True, fillcolor=None, linewidth=1):

    coord_rot = calc_rotated_polygon(polycoords, polycenter, angle, rotcentangle, rotcentdist)

    if fill:
        if fillcolor == None:
            fillcolor = outlinecolor
        return graph.draw_polygon(coord_rot, line_color=outlinecolor, fill_color=fillcolor)

    else:
        coord_rot.append(coord_rot[0])
        return graph.draw_lines(coord_rot, width=linewidth, color=outlinecolor)


def draw_rotated_rectangle(graph, rectcoord, angle, outlinecolor, rotcentangle=0, rotcentdist=0, fill=True, fillcolor=None, linewidth=1):

    polycoords = ( rectcoord[0], (rectcoord[1][0], rectcoord[0][1]), rectcoord[1], (rectcoord[0][0], rectcoord[1][1]) )
    polycenter = ( int((rectcoord[0][0] + rectcoord[1][0])/2), int((rectcoord[0][1] + rectcoord[1][1])/2) )

    return draw_rotated_polygon(graph, polycoords, polycenter, angle, outlinecolor, rotcentangle=rotcentangle, rotcentdist=rotcentdist, fill=fill, fillcolor=fillcolor, linewidth=linewidth)

