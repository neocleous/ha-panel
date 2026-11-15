# aud5_calls.py - assembly audit of the front shell split (2026-11-15): a typed record of the calls run in Fusion.
# Model "HA Panel v5 - tapered" version 64. Every call below was read-only except the picture calls (aud5p_pictures.py), whose
# AUD_* templates were deleted afterwards; the document was then closed without saving and version 64 opened again.
#
# This file is a record, not a runnable script. Blocks 0 and 1 are described (their exact call text was not kept when the
# session's context was compacted); the calls of blocks 2 to 4 are copied as run, condensed (prints dropped). Results are in sys.modules['aud5'].R under
# the keys named here, and in the report claude/report-assembly-audit-split-2026-11-15.md.
#
# Libraries, loaded from docs by git blob hash (checked before exec):
#   v5f_k_lib.py   ba8588482cd63f378ce5b98547aa702716f4855c  as sys.modules['aud5k']   (k)
#   v5f_m_lib.py   62790f5aece862608eec414bfd419b2aa47ca04a  as sys.modules['aud5m']   (sys.modules['v5f_k'] -> 'aud5k')
#   aud4_lib.py    181243c7068e2715b299f519df4a7ac8948c95eb  as sys.modules['aud5']    (aud4k -> aud5k, aud4m -> aud5m)
#   aud5x_lib.py   cdec604d3e54f1484a7d4c0d9675d7af76ea7f09  as sys.modules['aud5x']   (this folder)
#   v5f_k_pic.py   2efbc86b33be0fb90550efc8d56031c426804326  as a namespace with k = aud5k (revF/floor_plate/fusion)
#   aud5p_pictures.py 8382ccc7ff6caff7ab91677f92206d29ce09ea01 as sys.modules['aud5p'] (this folder)
# Fresh module names were used throughout: aud4_lib's tl() caches temporary copies by body name (lesson 181).
#
# Every call opened with:
#   k = sys.modules['aud5k']; a5 = sys.modules['aud5']; x = sys.modules['aud5x']; R = a5.R; X = k.K(); t0 = time.time()
# and kept a time check inside each loop (the connector gives up at 80 s while the script runs on).

# ---------------------------------------------------------------- block 0: preflight (described)
# X.state(): version 64 of 64, not modified, 397 bodies, 37 visible, no AUD_*, no duplicates.
# k.current(X, leads=True): 96 in the unit (16 leads, 13 keep-outs).
# R['guard0']: the nine guard volumes, read with X.body(n).volume * 1000; all equal to the brief.
# R['keylines_ec']: the enclosure chat's box-top key lines (KEY20 at 6, 10, 14 deg): only the door touches (left 12.11 / 12.46 / 1.86 mm3,
#   right 12.11 / 12.47 / 12.56), and at 14 deg on the left also LEAD_USB_RESP 10.74 mm3.
# R['ride64'] (with R['ride_ready'], crops rideS of the shell and rideP of the screen plate): a5.ride_setup / a5.ride over the 45 movers
#   x 23 steps = 1,035 positions; none touching; nearest 0.080 to the plate (Pi signal and display power leads' parts, 12 out), 1.223 to
#   the shell (the USB lead's held part, 0.5 out).
# Templates reproduced before use:
#   R['iron_v63'], R['iron_v63b']: the iron (sections 6 x 10, 10 x 65, 16.8 x 98) on the one-piece shell's tilted holes, on the holes' true
#     axes from k.holes_of: +2.36 / +2.35 (the print re-check's figures). On the enclosure chat's BOXTOP line it gave +2.41 (lesson 188).
#   R['key_v63']: KEY20 (2.4 x 101) on the version 63 lines: +2.80 both sides, rim +6.16 / +6.15.
#   R['reach_J8_bodies'], R['reach_J8_leads']: a5.reach for J8: 2 of 6 by bodies (up25, to-x25), 0 of 6 with the flat leads.
#   tweezers (a5.TWEEZ as a jaws body) on J8: tip r 2 free 5 of 6, r 3 1 of 6.
#   R['jaws']: a5.jaws with a5.PLIERS on the USB-C sleeve, grid 30-35 deg x 10-15 deg: ribbon 3.81-10.03 mm3, Pi power lap 0.07 / 4.89 /
#     63.94 mm3, board 0.190-0.306 mm.

# ---------------------------------------------------------------- block 1: the changed steps (described)
# R['holes_v63'], R['holes_plate'], R['post_holes'], R['plate_holes2']: k.holes_of on the shell, the plate and the v63 shell.
# R['bt_geom'], R['bt_geom2']: the plate and the lugs along the box-top lines (x.bt_line, x.bt_point): plate back s 1.145 / 0.805, front
#   5.105 / 4.765; lug seat -3.44 / -3.79, pocket floor -1.0 / -1.35, front face -0.01 / -0.35.
# R[('ins', 'left'/'right')]: x.insert_body, the plate's box-top inserts (4.6 x 5.7) flush with the plate's front face.
# R['ins_check']: insert to lug 0.268 / 0.30 radial; end to floor 0.42; lug top to plate 0.292 at home, contact after 0.32 of pull.
# R['iron_step2']: x.line with the iron on the four post holes (+4.76) and the plate's two holes (+4.22).
# R['step19_key_finger']: KEY20 along the normal at the four plate screws (+7.98 top, +8.11 bottom) and a5.finger in the six directions
#   (top 4 of 6, bottom 5 of 6).
# R['fix_unit'], R['mov_unit'], R['lateral'], R['lateral_px'], R['lateral_px2'], R['unit_home_gaps'], R['entry'], R['window'],
#   R['ins_drop']: the plate unit's window and the inserts' entry: xv booleans in small steps (lesson 190).
# R['key21']: KEY20 from the new box-top heads at 6, 10, 14 deg (x.bt_head_top, x.bt_key_dir) through crops v64L / v64R of the shell.
# R['lanes'], R['key23']: the four K5 lanes (KO_K5_*) and KEY25 (3.0 x 112) from the display screws' heads at d 15.8.
# R['cap_lcd'], R['added']: material added at version 64 against the _v63 bodies (shell posts and webs; lugs; nothing on the base plate).
# R['plate_off']: the plate off along its normal with the boxes in; nearest 0.171 at 0.6.
# R['sidewall'], R['sw_section'], R['behind_plate'], R['chin_groove']: sections for the cloth's edges and the plate's give.

# ---------------------------------------------------------------- block 2 and 3: copied as run
# R['lip_pockets']: k.holes_of(shell, 4.0, 4.3), meant for 4 mm holes. It takes radii, so it returned the 8.0 to 8.6 mm cylinders (lesson 189):
#   the 10 lip magnet pockets, 8 driver-screw head pockets and 3 K5 lane holes. A fingertip (r 8, 60 long) went along each, 4 ways
#   (straight, 15 deg up / down / in), on HOUSING_F_front and HOUSING_F_front_v63. The magnet pockets were the same on both, except the two
#   top ones (z 147.4): 15 deg from above free at version 64, 672 / 698 mm3 into the one-piece shell's front wall.
def key25_usb(X, k, a5, x, R):                        # the 2.5 key on the two left lanes, heads at d 15.8 (v64) and 16.8 (one-piece shell)
    KEY25 = getattr(k, 'KEY25', [(3.0, 112.0), (39.0, 4.0)])
    its = x.body_items(X, ['LEAD_USB_RESP'], [])
    out = {}
    for nm, up, q in (('upper left', 6.57, (0.0, 0.9063, -0.4226)), ('lower left', -61.43, (0.0, 0.9063, 0.4226))):
        for d in (15.8, 16.8):
            o = k.W(k.Dp(50.05, d, up)); u = a5.wdir(q)
            out[(nm, d)] = x.line(X, o, u, KEY25, its)['min']
    R['key23_usb'] = out        # upper left 2.66 (d 15.8) / 2.98 (d 16.8); lower left 3.29 / 3.29


def lift_lugs(X, k, a5, R, t0, bb, bgap):              # plate unit out: the module 1.5 forward, then up 95, against the boxes' lugs
    lugs = []
    for side, xr in (('L', (44.0, 72.0)), ('R', (-72.0, -44.0))):
        for p in a5.crop(X, 'SPKBOX_' + side, 'lugcrop' + side, (xr[0], xr[1], -14.0, 4.0, 60.0, 95.0)):
            lugs.append(('lug ' + side, p, a5.m.bb6(p)))
    lbb = [bb(p) for l, p, q in lugs]
    POS = [(0.5, 0.0), (1.0, 0.0), (1.5, 0.0)] + [(1.5, h) for h in (1, 2, 3, 4, 6, 8, 10, 12, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, 95)]
    cand = []
    for lab, p in R['ride_mov']:
        q = bb(p); sw = [q[0], q[1], q[2], q[3] + 1.5, q[4], q[5] + 95.0]
        if min(bgap(sw, c) for c in lbb) <= 3.0:
            cand.append((lab, p))
    res = R.setdefault('lift_lugs', {})
    for lab, p in cand:
        for b, h in POS:
            if (lab, b, h) not in res and time.time() - t0 < 60.0:
                res[(lab, b, h)] = a5.mingap(X, a5.mv(X, p, (0.0, b, h)), lugs, 3.0)
    # nearest: LCD_pogo_header_d14.1 3.143 (b 0.5, h 0); MAIN_pcb 6.505; MAIN_conn 7.70; RESP_CARRIER 8.577; nothing touching


def magnets(X, k, a5, R, t0, unit, perp):              # the lip magnet pockets (cylinder faces r 4.15) and a fingertip along / off their line
    st = R.setdefault('mag2', {})
    pk = []
    for f in X.body('HOUSING_F_front').faces:
        g = f.geometry
        if g.surfaceType != adsk.core.SurfaceTypes.CylinderSurfaceType or abs(g.radius * 10.0 - 4.15) > 0.01:
            continue
        a = (g.axis.x, g.axis.y, g.axis.z)
        a = unit(tuple(-c for c in a) if a[1] < 0 else a)
        cs = sorted((tuple(k.W(e.geometry.center)) for e in f.edges if e.geometry.curveType == adsk.core.Curve3DTypes.Circle3DCurveType),
                    key=lambda c: sum(c[i] * a[i] for i in range(3)))
        if len(cs) >= 2:
            pk.append((cs[-1], a, sum((cs[-1][i] - cs[0][i]) * a[i] for i in range(3))))
    # nine found (the tenth, at x +57.3 z 94.1, has split edges: added as the mirror of x -57.3); depth 1.57-1.58
    T = math.tan(math.radians(15.0))
    sh64 = [('shell', t) for t in k.parts(X, 'HOUSING_F_front')] + [('door', t) for t in k.parts(X, 'HOUSING_F_door')]
    for i, (m_, a, dp) in enumerate(pk):
        inn = perp((-math.copysign(1.0, m_[0]), 0.0, 0.0), a); upp = perp((0.0, 0.0, 1.0), a)
        dirs = {'straight': a, '15 in': unit(tuple(a[j] + T * inn[j] for j in range(3))), '15 out': unit(tuple(a[j] - T * inn[j] for j in range(3))),
                '15 up': unit(tuple(a[j] + T * upp[j] for j in range(3))), '15 down': unit(tuple(a[j] - T * upp[j] for j in range(3)))}
        for dn, di in dirs.items():
            tool = a5.finger(X, tuple(m_[j] + a[j] * 0.3 for j in range(3)), di, 8.0, 60.0)
            st.setdefault('res', {})[('v64', i, dn)] = {n: round(X.xv(tool, t), 1) for n, t in sh64 if tool.boundingBox.intersects(t.boundingBox)}
    # all ten free along their line (<= 1 mm3); x -57.3 z 94.1 grazes 0.9 mm3 straight, free at 15 deg in; the same 0.9 on HOUSING_F_front_v63


def slide_v64(X, a5, R, t0):                           # step 15 with the version 64 left box (aud4_lib's slide, unchanged)
    a5.slide_setup(X)
    a5.slide(X, t0, 60.0)       # 51 positions; the box touches only the base plate at home (by design); SPK_L 2.02 from the USB-A plug


# ---------------------------------------------------------------- pictures: aud5p_pictures.py
# NOT read-only. setup(X, pic namespace) -> pic_step19 / tidy -> pic_step21 / tidy -> pic_step23 -> finish; copy_old() copied five earlier
# pictures under their new step numbers. Saved with viewport.saveAsImageFile at 1600 x 1200 to ~/Documents/HA_panel_renders/audit-split/:
# step19_plate.png 191,591 B; step21_key.png 167,461 B; step23_notches.png 154,313 B. Templates deleted before each next picture and at the end (15, 12, 13, 9); visible set restored.
# Then: document close with userConfirmedCloseWithoutSave; open lineage urn:adsk.wipprod:dm.lineage:OwCt3IsjSrWMOTr8NrG2Bg (version 64).
# R['guard1'] after reopening: the nine guard volumes equal to R['guard0']; 397 bodies, 37 visible (the same set), no AUD_*, not modified.
