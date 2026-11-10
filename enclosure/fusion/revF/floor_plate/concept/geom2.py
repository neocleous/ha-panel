# Concept v2 (Daniel 2026-11-10 09:10): base plate = the whole underside out to the edge, speaker boxes and Pi on it,
# main board behind the display. World mm, x = x_rel (+x = viewer's left). Data from the version 42 model:
# f1a (REF_F_outer plan sections at z 0.05 / 2.5), f1c (side sections at x_rel 0.3 and 70.5, wall reference, boxes),
# f1d (main-board fit, pose B).
import math
from shapely.geometry import Polygon, Point, box, LineString
from geom import *

C12 = math.cos(math.radians(12.0)); S12 = math.sin(math.radians(12.0)); HH = 143.3


def D2W(Y, Zd):
    """design (depth Y, height Zd along the slab) -> world (y, z)"""
    return (Y * C12 - Zd * S12, HH + Y * S12 + Zd * C12)


def mirror(half):
    return half + [(-x, y) for (x, y) in reversed(half[1:-1])]


Z25_HALF = [(0, 6.4), (87.6, 6.4), (90.1, 6.1), (92.2, 5.4), (94.0, 4.3), (95.5, 3.0), (96.8, 1.4), (97.8, -0.5), (98.4, -2.7),
            (98.5, -5.1), (97.7, -14.2), (96.7, -20.2), (96.2, -23.1), (95.5, -25.9), (93.8, -31.5), (91.9, -36.9), (90.7, -39.6),
            (88.0, -44.9), (86.4, -47.5), (83.1, -52.4), (81.4, -54.6), (77.7, -58.9), (75.7, -60.9), (71.4, -64.6), (66.8, -68.0),
            (64.4, -69.6), (62.0, -71.1), (56.9, -73.8), (54.2, -75.0), (48.9, -77.2), (41.4, -79.6), (36.8, -80.7), (32.0, -81.7),
            (27.8, -82.3), (23.0, -82.9), (13.5, -83.6), (0.0, -83.9)]
Z0_HALF = [(0, 2.3), (87.6, 2.3), (88.7, 2.2), (90.5, 1.7), (91.3, 1.2), (92.6, 0.2), (93.6, -1.2), (94.0, -2.0), (94.4, -3.9),
           (94.4, -4.9), (94.1, -9.5), (93.5, -14.6), (92.6, -20.0), (92.0, -22.9), (90.4, -28.7), (89.4, -31.7), (87.0, -37.7),
           (84.1, -43.5), (82.4, -46.2), (78.9, -51.2), (75.1, -55.6), (73.1, -57.7), (68.7, -61.5), (64.1, -65.0), (61.7, -66.5),
           (56.6, -69.4), (54.0, -70.7), (48.7, -72.9), (41.2, -75.4), (36.6, -76.5), (32.4, -77.4), (28.4, -78.1), (23.0, -78.8),
           (12.4, -79.5), (0.0, -79.8)]
Z25 = Polygon(mirror(Z25_HALF))          # plate's top edge = the body's outline at z 2.5
Z0 = Polygon(mirror(Z0_HALF))            # flat underside
BOX2_L = Polygon([(46.0, -3.7), (46.0, -52.0), (79.3, -52.0), (82.5, -47.7), (86.5, -41.1), (88.7, -36.6), (91.2, -30.3),
                  (92.9, -24.4), (94.5, -17.2), (95.2, -11.9), (95.9, -3.7)])
BOX2_R = Polygon([(-46.0, -3.7), (-95.9, -3.7), (-95.2, -11.9), (-94.5, -17.2), (-92.9, -24.4), (-91.2, -30.3), (-88.7, -36.6),
                  (-86.5, -41.1), (-82.5, -47.7), (-79.3, -52.0), (-64.0, -52.0), (-64.0, -31.0), (-61.3, -31.0), (-61.3, -23.6),
                  (-46.0, -23.6)])
FRAME_L = box(47.5, -3.0, 93.5, 0.0); FRAME_R = box(-93.5, -3.0, -47.5, 0.0)
PLATE_SHELL = [(78.5, -50.0), (-78.5, -50.0)]                     # plate screws into posts on the side walls (concept)
BOX_PLATE = [(51.0, -12.0), (64.0, -45.0), (-51.0, -12.0), (-72.0, -38.0)]   # box-bottom screws (concept)
TAB_X = 57.0                                                      # box-top screw, z about 80, from the back
TONGUES = [box(22.0, -0.9, 34.0, 2.9), box(-34.0, -0.9, -22.0, 2.9)]
# main board behind the display: f1d pose B (board centre x_rel 2.55, Zd -28.5; back face 24.6 behind the LCD PCB)
MB_XC = 2.55; MB_ZC = -28.5; MB_YB = -32.0; MB_YF = -33.6
