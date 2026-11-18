# rev F g22, block 2: the checks on version 67 as run on 2026-11-18 (all read-only).
# k = sys.modules['c3k'] (v5f_k_lib.py), k.K4NS = v5f_k4a_unit_checks.py, c3 = the c3_*.py files.
# Old bodies are the hidden backups <name>_v66. World mm; unit moved by (0, -b, -h) = shell forward b, lifted h.
#
# Lessons (continue README's list)
# 242. K4NS['way_in'] and the default 'slide' name USBA_cable_env, which this document does not hold. way_in was replaced by
#      window() below; slide ran with its fixed list filtered by X.body(n) is not None.
# 243. app.measureManager.measureMinimumDistance(realBody, temporaryBody) works and is fast (about 0.1 s against the shell).
#      Axis-to-shell distances come from a temporary cylinder of radius 0.05 plus 0.05.
# 244. The same check on the old bodies: wrap K4NS['crop'], K4NS['pieces'] and k.tcopy so that the changed names map to
#      <name>_v66, and run under another tag ('v66x'). Restore the three in a finally block.
# 245. The pictures' fill is not reliable where outlines touch; decide solid or air by a small box's volume.
# 246. Booleans of a part with the cropped shell take 2 to 3 s each: keep grids small and resumable (state in k.c).
# 247. K4NS['matrix'] returns (pairs, left, bodies) and raises 'call again' while the shell's slabs are built: call until left is 0.
import math, sys, time
import adsk.core, adsk.fusion

CHANGED = ('HOUSING_F_front', 'HOUSING_F_door', 'HOUSING_F_cap', 'FLOOR_PLATE', 'SPKBOX_L', 'SPKBOX_R', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R')


def matrix(X, k):                                     # check 7: 96 bodies, 4,560 pairs, 76 not zero = version 66's 76
    res, left, n = k.K4NS['matrix'](X, 'v67')         # compare as unordered pairs (lesson 241)
    # changed: door x KO_capkey_BL 108.966 -> 186.223, _BR 108.793 -> 186.375, _SL 211.189 -> 211.287, _SR 211.128 -> 211.243


def window(X, k):                                     # check 1: overlap of a unit part, moved (0, -b, -h), with the cropped shell
    crops = {'box': (-110.0, 110.0, -70.0, -30.0, 0.0, 95.0), 'base': (-110.0, 110.0, -70.0, 12.0, -5.0, 14.0),
             'heads': (-110.0, 110.0, -20.0, 12.0, -5.0, 95.0), 'front': (-110.0, 110.0, -30.0, 12.0, -5.0, 95.0)}
    # boxes, b 1.00 1.15 1.49 1.50 at h 0 5 22 25: 0.0; b 1.51: 1.957 / 2.013 (h 0), 0.071 (h 25). Version 66 at 1.51, h 0: 1.192 / 1.184.
    # base plate, b 1.00 and 1.04 at h 1 and 2: 0.36 / 0.07 and 0.83 / 0.17 (version 66: 0.36 / 0.07 and 0.50 / 0.10), the noses on the
    #   lips' front faces at y 1.3; b 1.05 and more: 0.0 at every h. Driver screw heads, b 1.10 to 1.30, h 0 5 10: 0.0.
    # shell minus old shell beyond x +-85, y > -20, z < 95: + the toe's end (1.235), - the two leaves (2.44): the corners' step is as it was.


def reaches(X, k):                                    # check 2: K4NS['reach'] for the 13 targets of K4NS['ORDER'], fingertip 16
    # version 67 = version 66 (lesson 244) in free directions: Pi 1x3 4/5, Pi 2x5 4/5, Pi 2x3 5/5, display 1x3 4/5, DSI 0/5,
    # J9 5/6, J8 2/6, J1 6/6, J6 6/6, J5 3/6, J10 5/6, J11 5/6, J2 3/6. Six blocked directions are blocked by more (lip, clip, box).
    pass


def key_lines(X, k):                                  # check 2: axis to shell inside y -66 .. -50 (lesson 243), old -> new
    # box-top screws (lug hole axis, 10 deg in plan, z 80.0): left 7.40 -> 7.17, right 7.34 -> 7.11;
    #   4 deg further out (the 6 deg line): left 3.76 -> 3.58, right 3.38 -> 3.21
    # cap keys' lanes (keep-outs r 2.5): back 4.95 -> 4.17 and 4.96 -> 4.18; side 4.11 -> 3.35 both
    # display screws' lanes (keep-outs r 3.5): LL 3.57 -> 3.57, LR 4.53 -> 4.50, UL 3.58 -> 3.50, UR 3.58 -> 3.58
    pass


def pliers(X, k, c3):                                 # check 2: v5f_m3a_usbc_reach.py's jaws against the shell, old / new, mm3
    # from 45 deg below (the service way, unit lowered): 0.0 / 0.0 at 0, 3.6 and 7.2 out, pliers and tweezers
    # 'to-x25', unit in place: seated 0.0 / 0.0; 3.6 out 3.9 / 9.0 (pliers), 0.4 / 1.7 (tweezers); 7.2 out 14.2 / 23.9, 5.7 / 9.5
    pass


def neighbours(X, k):                                 # checks 2 to 4: nearest bodies to what was added (lesson 243)
    # lip's added layer: USB lead 0.01 (0.81 to the old shell, at x 46.6, y -59.3, z 108.7); display screws' lanes 0.07 / 0.08 / 0.08 / 1.0;
    #   cap keys' lanes 0.85 (side), 1.67 (back); door 1.4; boxes 1.5; left speaker lead 2.76; hood 3.98; base plate 4.0; right speaker lead 4.23
    # the way in and out, layer moved (0, b, h), b 1.15 and 1.5, h 0 .. 230 (16 heights): boxes 0.00 at b 1.5 (the stop), base plate 4.0,
    #   every other unit body 20.8 or more
    # door's added ribs: VEML6030 lead 5.76, supply module's tolerance envelope 9.47, Pi power lead 9.53; cap keys' side lanes 3.34
    # nose tops: touch board's keep-out 0.45, touch board 0.57, shell 1.09. Web fill: touch board 0.89, bezel 1.8. Toe fill: base plate 0.43.
    # fill under the roof ledge: screen plate 1.25, cap 1.40
    pass


def sizes(X, k):                                      # check 7: k.needle_t along a line
    # door bar at x 3 along y: 2.55 / 2.57 / 2.61 -> 4.57 / 4.61 / 4.66 (z 65 / 88 / 110); width 3.0
    # pilot (axis y -7.05, z 38): 2.0 to the front, 2.0 to the rear, both boxes; clip's lug 1.65 behind its hole
    # groove web 1.00 (d 13.8 .. 14.8) at x 0 and 47; toe 0.85 at y 1.6; nose 1.17 at its lead-in (y 2.0), 1.2 behind it
    pass


def others(X, k):
    # K4NS['chambers']: left box 118.536 / 86.945 cm3, right 120.881 / 88.986 cm3, both closed
    # K4NS['slide'] (left box sliding on, 17 positions): 0.0 everywhere
    # outer skin (c3.outside): shell 52.779 in two lumps of 26.389; door, cap, base plate, boxes, clips 0.0
    pass
