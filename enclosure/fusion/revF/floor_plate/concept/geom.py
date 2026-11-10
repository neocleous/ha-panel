# Concept geometry for the floor plate (block 1), world mm, x = x_rel (+x = viewer's left), from the model's sections
# (f1a / f1b, version 42). Outline W = REF_F_outer at z 6 (wall line above the R6 bottom fillet).
import math
from shapely.geometry import Polygon, Point, box, LineString
from shapely.ops import unary_union

W_HALF = [(87.6, 7.5), (90.3, 7.2), (92.7, 6.4), (94.7, 5.2), (96.3, 3.8), (97.7, 2.0), (98.8, -0.1), (99.5, -2.6),
          (99.6, -5.2), (99.1, -11.5), (98.8, -14.7), (97.7, -21.0), (97.1, -24.0), (95.6, -29.8), (94.6, -32.7),
          (93.4, -36.0), (91.9, -39.6), (90.1, -43.4), (87.8, -47.4), (85.2, -51.5), (83.7, -53.6), (80.3, -57.6),
          (78.5, -59.6), (75.1, -62.9), (71.5, -66.0), (65.8, -70.1), (61.7, -72.6), (57.5, -74.8), (53.1, -76.7),
          (48.8, -78.4), (44.5, -79.8), (40.4, -81.0), (36.4, -81.9), (30.7, -83.0), (25.6, -83.7), (20.9, -84.2),
          (11.9, -84.8), (0.0, -85.0)]
W = Polygon(W_HALF + [(-x, y) for (x, y) in reversed(W_HALF[:-1])])
JOINT_Y = -55.0                                   # cloth strip ends at the joint (rev F); seam on the wall at -57.7..-58.3

def off(d):                                       # plan offset inward by d (wall vertical at the floor)
    return W.buffer(-d, join_style=1, resolution=32)

FRONT = box(-200, JOINT_Y, 200, 50)               # forward of the joint
# today's fabric band on the underside: fillet + 6 mm strip (W .. W-12) forward of the joint
CLOTH_NOW = W.difference(off(12.0)).intersection(FRONT)
# concept: fillet + 1 mm (W .. W-7) forward of the joint (rev D pattern), hard land W-7 .. W-8
CLOTH_NEW = W.difference(off(7.0)).intersection(FRONT)

# --- components (plan) ---
PI = box(-43.2, -58.0, 41.9, -2.0)
PI_PORTS = [box(41.9, -18.3, 45.15, -3.7), box(41.9, -36.3, 45.15, -21.6), box(41.9, -55.8, 45.15, -39.8)]
PI_BOSSES = [(18.35, -5.5), (-39.65, -5.5), (18.35, -54.5), (-39.65, -54.5)]
SD_SOCKET = box(-44.9, -36.0, -29.4, -24.0)
ADAPTER = box(-38.2, -71.3, -25.7, -59.3)
PLUG = box(-25.7, -71.5, -5.7, -59.1)
USBA_PLUG = Polygon([(45.1, -22.9), (55.1, -22.9), (55.1, -35.0), (53.0, -35.0), (53.0, -45.0), (47.0, -45.0), (47.0, -35.0), (45.1, -35.0)])
USBA_CABLE = box(50.0, -53.5, 54.0, -45.0)
PI_CABLE = LineString([(6.3, -65.3), (11.0, -66.0), (16.5, -67.2), (20.5, -66.8), (24.6, -66.6)])
USB4085 = box(18.8, -69.9, 31.2, -63.3)
BOX_L = Polygon([(46.0, -3.7), (46.0, -52.0), (74.9, -52.0), (78.6, -47.3), (81.8, -42.6), (84.3, -37.9), (85.8, -34.8),
                 (87.2, -31.3), (89.1, -25.5), (90.8, -18.2), (91.6, -12.8), (92.5, -4.0), (92.4, -3.7)])
BOX_R = Polygon([(-46.0, -3.7), (-92.4, -3.7), (-92.5, -4.0), (-91.8, -11.3), (-90.7, -18.5), (-89.6, -23.7), (-88.6, -27.2),
                 (-87.4, -30.6), (-86.1, -34.0), (-84.7, -37.2), (-82.1, -42.1), (-78.9, -47.0), (-74.9, -52.0), (-64.0, -52.0),
                 (-64.0, -31.0), (-61.3, -31.0), (-61.3, -23.6), (-46.0, -23.6)])
SLOT_L = unary_union([box(46.0, -36.95, 55.65, -20.95), box(46.0, -53.0, 57.15, -36.0)])   # USB-A slot in the +x box
TOUCH = box(-45.0, 2.7, 45.0, 4.3)
TOUCH_KO = box(-43.0, -0.2, 43.0, 2.7)
CLIPS = [box(40.5, -8.5, 45.0, 2.0), box(-45.0, -8.5, -40.5, 2.0)]
MAIN = box(-45.0, -65.0, 45.0, -63.4)
MAIN_ENV = box(-45.0, -63.4, 45.0, -33.4)
CRADLE_BOSSES = [(-1.5, -72.5), (6.5, -72.5)]
CRADLE_BODY = Polygon([(-11.0, -84.6), (11.0, -84.6), (11.0, -81.6), (10.5, -81.6), (10.5, -60.5), (-5.2, -60.5),
                       (-5.2, -72.0), (-10.5, -72.0), (-10.5, -81.6), (-11.0, -81.6)])
DOOR_BOSSES = [(19.0, -74.5), (-19.0, -77.0), (50.0, -67.0), (-50.0, -67.0)]
DOOR_INNER_HALF = [(74.6, -55.3), (72.9, -57.1), (69.4, -60.2), (64.3, -64.2), (58.9, -67.5), (52.4, -70.7), (50.6, -71.5),
                   (46.7, -73.0), (43.2, -74.1), (36.8, -75.8), (28.6, -77.3), (20.2, -78.3), (18.0, -78.5), (11.2, -78.8),
                   (2.0, -79.0)]
DOOR_INNER = LineString(DOOR_INNER_HALF + [(-x, y) for (x, y) in reversed(DOOR_INNER_HALF[:-1])])
BRACKET_FEET_NOW = [(49.5, -58.0), (-65.0, -57.0)]
BRACKET_FEET_NEW = [(65.0, -57.0), (-65.0, -57.0)]          # +x half cranked as the mirror of the -x half (d17)
BRACKET_COLS = [box(46.5, -62.5, 52.5, -58.5), box(-52.5, -62.5, -46.5, -58.5)]
ZIP_POSTS = [box(55.2, -58.5, 57.0, -54.5), box(60.0, -58.5, 61.8, -54.5)]
FEET_NOW = {'FL': (80.0, -11.5), 'FR': (-80.0, -11.5), 'RL': (30.0, -69.0), 'RR': (-30.0, -69.0)}
FEET_NEW = {'FL': (80.0, -11.5), 'FR': (-80.0, -11.5), 'RL': (30.0, -69.0), 'RR': (-31.2, -68.5)}
INTAKE_BB = (-41.2, 39.8, -57.7, -6.7)

def intake_holes():
    xs = [INTAKE_BB[0] + 3.0 * i for i in range(int((INTAKE_BB[1] - INTAKE_BB[0]) / 3.0 + 1.01))]
    ys = [INTAKE_BB[3] - 3.0 * j for j in range(int((INTAKE_BB[3] - INTAKE_BB[2]) / 3.0 + 1.01))]
    pts = [(x, y) for x in xs for y in ys if all(math.hypot(x - bx, y - by) >= 4.5 for (bx, by) in PI_BOSSES)]
    return pts

# --- concept: plate (lower outline seen from below), ring lip, arm bosses ---
ARM_BOSSES = [(48.6, -57.6), (-47.2, -57.6)]      # shell bosses, Ruthex M3, bearing on the plate's rear tabs
ARM_R = 3.5
PLATE_FRONT_Y = 7.5 - 10.3                        # W-10.3: the plate's lower edge at the chin (lip on the ring lip to W-8.3)
PLATE = Polygon([
    (45.5, PLATE_FRONT_Y), (45.5, -20.6), (55.8, -20.6), (55.8, -53.9),          # +x side, strip under the opened USB-A slot
    (52.6, -53.9), (52.6, -61.6), (44.6, -61.6), (44.6, -59.5),                 # +x arm-boss tab
    (-5.4, -59.5), (-5.4, -71.8), (-23.6, -71.8), (-23.6, -72.7), (-24.3, -72.7),                                # behind the Pi; plug zone
    (-24.3, -77.06), (-28.7, -76.45), (-36.5, -75.05), (-38.8, -74.43),      # follows the door's bottom flange (z 2.9) 0.85 forward: 0.55 shell land
    (-38.8, -61.6), (-51.5, -61.6), (-51.5, -53.6),              # adapter + RR foot zone; -x arm-boss tab
    (-45.5, -53.6), (-45.5, PLATE_FRONT_Y)])
PLATE_LIP = box(-45.5, PLATE_FRONT_Y, 45.5, 7.5 - 8.3)    # the plate's upper half reaching forward over the ring lip
RING_LIP = box(-45.5, 7.5 - 10.0, 45.5, 7.5 - 8.0)        # shell, z 0-1.25, under the plate's lip
OPENING = PLATE.buffer(0.3, join_style=2)
