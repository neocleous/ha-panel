# rev F split (2026-11-15), block 2: the front shell split, the boxes' top lugs (1a) and the tongue noses (D141).
# Brief: claude/brief-enclosure-front-shell-split-2026-11-14.md. Decisions: 1a, 2a (thin plate, black, even 1 mm gap), 3a.
# Each function is the body of one connector call's run(_context), in order. Model "HA Panel v5 - tapered": version 63 (g18) -> 64 (g19).
# Libraries already in Fusion's sys.modules: v5f_k (v5f_k_lib.py @fafa8fd), split_lib (lib/split_lib.py). World mm; slab frame (x, d, up).
import adsk.core, adsk.fusion, sys, os, time

U0, U1, XP = -89.93, 34.77, 98.75                     # the plate's outline: up range, half width (0.3 inside the slab frame's lip)
POS = {'TL': (70.0, 27.0), 'TR': (-70.0, 27.0), 'BL': (85.0, -82.0), 'BR': (-85.0, -82.0)}     # plate screws (x, up)
BOXTOP = ((1.0, (58.5, -0.77, 80.0)), (-1.0, (-58.6, -0.43, 80.0)))   # box-top screw lines: side sign, a point on the 10 deg line


def split(_context):                                  # step 1: HOUSING_F_front -> _v63 (hidden); new rest + HOUSING_F_plate (black)
    k = sys.modules['v5f_k']; X = k.K()
    src = X.body('HOUSING_F_front')
    P = X.cp(src); X.sec(P, X.dbox(-XP, XP, -5.0, 12.8, U0, U1))                # the seat in front of d 12.8
    for g, p0 in BOXTOP:                                                         # box-top inserts, through, on the 10 deg lines
        u = (g * 0.17365, 0.98481, 0.0)
        X.dif(P, X.cyl((p0[0] - u[0] * 4.0, p0[1] - u[1] * 4.0, 80.0), (p0[0] + u[0] * 9.0, p0[1] + u[1] * 9.0, 80.0), 2.0))
    for x, up in POS.values():
        X.dif(P, X.cyld(x, up, 1.7, 4.0, 14.0))                                  # plate screws, along the normal
    X.dif(P, X.cyld(85.0, -82.0, 3.625, 11.4, 14.0))                            # round pocket for the left-bottom peg
    X.dif(P, X.dbox(-89.375, -80.625, 11.4, 14.0, -85.625, -78.375))             # slot for the right-bottom peg, free along x
    R = X.cp(src)
    X.dif(R, X.dbox(-106.0, 106.0, -5.0, 13.0, -101.0, 46.0))                    # nothing in front of d 13.0: even 1 mm gap to the frame (d 12.0)
    shb = X.cp(src)
    X.dif(shb, X.dbox(50.0, 67.5, 14.0, 18.5, -70.0, -52.0)); X.dif(shb, X.dbox(-67.5, -50.0, 14.0, 18.5, -70.0, -52.0))
    W = X.cp(src); X.sec(W, X.dbox(-XP, XP, 12.8, 14.8, U0, U1))                # the 2 mm layer behind the seat
    SW = X.tbm.copy(shb); X.sec(SW, X.dbox(-XP, XP, 14.85, 15.65, U0, U1))      # what runs on behind it (side walls, ribs, radar pocket)
    ext = X.tbm.copy(SW)
    for i in range(1, 5):
        X.uni(ext, X.move_n(X.tbm.copy(SW), 0.8 * i))
    X.dif(W, ext); X.dif(R, W)                                                   # the layer goes except in front of what runs on
    X.dif(R, X.dbox(50.0, 67.5, 14.0, 18.5, -70.0, -52.0)); X.dif(R, X.dbox(-67.5, -50.0, 14.0, 18.5, -70.0, -52.0))   # old box-top bosses
    for tag, (x, up) in POS.items():
        if tag[0] == 'T':
            bo = X.cyld(x, up, 4.5, 12.8, 26.0)                                  # column back into the top of the shell
        else:
            s = 1.0 if x > 0 else -1.0
            bo = X.cyld(x, up, 4.5, 12.8, 19.4)
            X.uni(bo, X.dbox(x + s * 3.0, s * 93.0, 13.0, 19.4, up - 2.0, up + 2.0))   # web to the side wall
            X.uni(bo, X.cyld(x, up, 3.5, 11.6, 12.8))                            # peg 7.0 x 1.2 into the plate
        X.uni(R, bo)
    for tag, (x, up) in POS.items():                                             # Ruthex M3 x 5.7: 4.0 x 6.35
        d0 = 11.6 if tag[0] == 'B' else 12.8
        X.dif(R, X.cyld(x, up, 2.0, d0 - 0.5, d0 + 6.35))
    for s in (1.0, -1.0):                                                        # D141: lip top 0.15 lower under the noses
        X.dif(R, X.wbox(s * 24.2, s * 35.8, 1.0, 3.66, 4.05, 4.30))
    X.swap('HOUSING_F_front', R, '_v63')
    pb = X.add(P, 'HOUSING_F_plate', like=X.body('HOUSING_F_front_v63'), show=True)
    blk = X.des.appearances.itemByName('Plastic - Matte (Black)')                # added from the library if missing (see the call)
    if blk is not None:
        pb.appearance = blk
    # printed: plate 68255.48 lumps 1 | rest 104428.62 lumps 1 | bodies 394 visible 37


def lugs_noses(_context):                             # step 2: lugs 3.168 along the screw line; insert pocket; gusset; nose chamfers
    k = sys.modules['v5f_k']; X = k.K()
    SH = 3.168                                        # lug front y -3.9 -> -0.78: 0.3 behind the plate at the lug's top (z 84); the plate leans back 12 deg
    for name, (g, p0) in zip(('SPKBOX_L', 'SPKBOX_R'), BOXTOP):
        u = (g * 0.17365, 0.98481, 0.0)
        P = lambda s: (p0[0] + u[0] * s, p0[1] + u[1] * s, 80.0)
        sy = lambda y: (y - p0[1]) / u[1]
        src = X.body(name); x0, x1 = sorted((g * 53.6, g * 62.4))
        tab = X.cp(src); X.sec(tab, X.wbox(x0, x1, -8.6, -3.7, 76.0, 84.5))
        mv = X.tbm.copy(tab); X.move(mv, u[0] * SH, u[1] * SH, 0.0)
        nb = X.cp(src); X.dif(nb, X.tbm.copy(tab)); X.uni(nb, mv)
        gx0, gx1 = sorted((g * (53.8 + 0.55), g * (62.2 + 0.55)))
        gus = X.wbox(gx0, gx1, -5.0, -0.78, 76.0 - 4.22, 76.0)                    # 45 deg gusset under the new overhang
        mid = ((gx0 + gx1) / 2.0, (-5.0 - 0.78) / 2.0, 76.0 - 4.22 / 2.0)
        X.dif(gus, X.obox((mid[0], mid[1] + 2.0 * 0.70711, mid[2] - 2.0 * 0.70711), (1, 0, 0), (0, 0.70711, 0.70711), 12.0, 10.0, 4.0))
        X.uni(nb, gus)
        s_end = sy(4.254) - 5.7                                                  # insert flush with the plate's front (y 4.254 at z 80)
        X.dif(nb, X.cyl(P(sy(-0.78) + 0.5), P(s_end - 0.1), 2.6))               # pocket 5.2 to 0.1 behind the insert's end
        X.dif(nb, X.cyl(P(sy(-0.78) - 12.0), P(sy(-0.78) + 0.5), 1.8))          # clearance 3.6
        X.swap(name, nb, '_v63')
    fp = X.cp(X.body('FLOOR_PLATE'))
    for s in (1.0, -1.0):                                                        # D141: 0.4 x 45 under each nose's front edge (y 2.35, z 4.35)
        X.dif(fp, X.obox((s * 30.0, 2.35, 4.35), (1, 0, 0), (0, 0.70711, 0.70711), 11.0, 2.0, 0.5657))
    X.swap('FLOOR_PLATE', fp, '_v63')
    # printed: SPKBOX_L 26086.63, SPKBOX_R 26807.97 (1 lump each; insert 0.59 into the lug), FLOOR_PLATE 32450.57; bodies 397, visible 37


def save_g19(_context):                               # visible set restored, no AUD_ body, then the named version
    doc = adsk.core.Application.get().activeDocument
    doc.save('rev F WIP 2026-11-15 g19: front shell split (D140) - screen plate HOUSING_F_plate (seat only, back d 12.8, black, even 1 mm gap all round) '
             '+ rest HOUSING_F_front (layer between the side walls removed, fronts trimmed to d 13.0, 4 screw bosses, 2 spigots); one-piece shell kept hidden as '
             'HOUSING_F_front_v63; box lugs 3.17 forward on the screw lines (1a) with insert pocket and gusset; D141: nose chamfer 0.4x45, lip top 0.15 lower; '
             'checks in block 3; not for print')                                 # -> version 64


def export_g19(_context):
    des = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    path = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-g19.f3d')
    em = des.exportManager
    print(em.execute(em.createFusionArchiveExportOptions(path)), os.path.getsize(path))    # True 183015526
