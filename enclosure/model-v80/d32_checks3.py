# Block 3: the fits at the faces that moved, read on the model as it stands. READ-ONLY (temporary bodies only).
#   fits     smallest distances, body to body: boxes on their seats, feet in their recesses, door and shell on the base plate's
#            lands and pads, and over its top; noses to the lips; the Pi and the cradle over the faces under them; tabs to the
#            screen plate; the shell's lip to the strips and the cap; the frame end's tip to the door; the plug to its pocket
#   faces    the moved level faces themselves: height, area, off the grid, and what stands in front within 1.0 (d30's method)
#   screws   computed from the model's faces: each floor screw's thread in its insert (M3 x 8, head on the counterbore's floor)
# Run: runpy.run_path(D + 'd32_checks3.py')['main'](stage, tag)  -> d32_<stage>_<tag>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')
I30 = runpy.run_path(D + 'd30_inspect3.py')
PLN = adsk.core.SurfaceTypes.PlaneSurfaceType


def dist(k, X, a, b):
    r = X.mm.measureMinimumDistance(a, b)
    return r.value * 10.0, k.r2(k.W(r.positionOne), 3), k.r2(k.W(r.positionTwo), 3)


def st_fits(k, X):
    P = X.body('FLOOR_PLATE')
    rows = [('SPKBOX_L', 'FLOOR_PLATE'), ('SPKBOX_R', 'FLOOR_PLATE'), ('FOOT_FL', 'FLOOR_PLATE'), ('FOOT_FR', 'FLOOR_PLATE'), ('FOOT_RL', 'FLOOR_PLATE'),
            ('FOOT_RR', 'FLOOR_PLATE'), ('HOUSING_F_door', 'FLOOR_PLATE'), ('HOUSING_F_front', 'FLOOR_PLATE'), ('PI5_F', 'FLOOR_PLATE'),
            ('CRADLE_5807', 'FLOOR_PLATE'), ('SPKBOX_L', 'HOUSING_F_plate'), ('SPKBOX_R', 'HOUSING_F_plate'), ('HOUSING_F_front', 'HOUSING_F_door'),
            ('HOUSING_F_front', 'MIC_strip_L_env'), ('HOUSING_F_front', 'MIC_strip_R_env'), ('USBA_plug_env', 'SPKBOX_L'), ('SPKBOX_L', 'HOUSING_F_front'),
            ('SPKBOX_R', 'HOUSING_F_front'), ('LEAD_USB_RESP', 'SPKBOX_L'), ('LEAD_USB_RESP', 'FLOOR_PLATE'), ('GROMMET_usbc_F', 'FLOOR_PLATE')]
    for a, b in rows:
        A = X.body(a); B = X.body(b)
        if A is None or B is None:
            print('%-18s to %-18s: a body is missing' % (a, b)); continue
        d, p, q = dist(k, X, A, B)
        print('%-18s to %-18s %8.4f  at %s / %s' % (a, b, d, p, q))
    low = X.wbox(-120, 120, -110, 30, -1.0, 2.401); X.sec(low, X.tbm.copy(P))               # the plate without what stands on its top
    for n in ('HOUSING_F_door', 'HOUSING_F_front', 'SPKBOX_L', 'SPKBOX_R', 'GROMMET_usbc_F', 'CRADLE_5807', 'PI5_F', 'LEAD_USB_RESP'):
        b = X.body(n)
        if b is None:
            continue
        d, p, q = dist(k, X, b, low)
        print('%-18s to the plate below z 2.401 (its top and rim) %8.4f  at %s / %s' % (n, d, p, q))
    # the tip of the frame's left lower end and the lip, each to what stands behind it
    for nm, bx, others in (('frame end\'s tip', (65.0, 70.0, -64.0, -62.9, 6.0, 8.0), ('HOUSING_F_door',)),
                           ('lip under the cap\'s seam', (-60.5, 60.5, -23.6, -22.0, 175.5, 177.6), ('MIC_strip_L_env', 'MIC_strip_R_env', 'HOUSING_F_cap', 'LEAD_MIC_L', 'LEAD_MIC_R'))):
        c = L['crop'](X, 'HOUSING_F_front', bx)
        for o in others:
            d, p, q = dist(k, X, c, X.body(o))
            print('shell, %-26s to %-16s %8.4f  at %s / %s' % (nm, o, d, p, q))
    for s, sx in (('L', 1), ('R', -1)):
        a, b = sorted((sx * 54.0, sx * 63.1))
        c = L['crop'](X, 'SPKBOX_' + s, (a, b, -6.0, 0.0, 75.0, 85.0))
        d, p, q = dist(k, X, c, X.body('HOUSING_F_plate'))
        print('SPKBOX_%s tab to the screen plate %8.4f  at %s / %s' % (s, d, p, q))
    for sx in (1, -1):
        a, b = sorted((sx * 24.0, sx * 36.0))
        c = L['crop'](X, 'FLOOR_PLATE', (a, b, 0.9, 2.4, 4.0, 5.0)); sh = L['crop'](X, 'HOUSING_F_front', (a, b, 0.0, 4.0, 2.5, 4.39))
        d, p, q = dist(k, X, c, sh)
        print('nose at x %+d (above z 4.0, in front of y 0.9) to the shell below z 4.39 (the lip) %8.4f  at %s / %s' % (sx * 30, d, p, q))


def st_faces(k, X):
    k.budget(70)
    level = I30['level']; near_face = I30['near_face']; fbox = I30['fbox']
    P = X.body('FLOOR_PLATE')
    for f, p, s in sorted(level(k, P, 2), key=lambda r: r[1][2]):
        if not any(abs(p[2] - zz) < 0.003 for zz in (0.4, 3.8, 4.4, 7.4, 12.4)) or f.area * 100 < 1.0:
            continue
        o = p[2] - round(p[2] / 0.2) * 0.2
        print('FLOOR_PLATE z %.2f %-4s %8.2f mm2 at (%.1f, %.1f), off the grid %+.3f: %s' % (p[2], 'up' if s > 0 else 'down', f.area * 100, p[0], p[1], o, near_face(k, X, P, f, p, s, 2)))
        if k.late():
            print('time'); return
    S = X.body('HOUSING_F_front')
    for f, p, s in level(k, S, 1):
        if abs(p[1] + 23.2) < 0.003 or abs(p[1] + 63.4) < 0.003:
            h = 6.7992 - p[1]
            print('HOUSING_F_front y %.4f %s %8.2f mm2 box %s, height %.4f off %+.4f: %s' % (p[1], 'looks +y' if s > 0 else 'looks -y', f.area * 100, fbox(k, f), h, h - round(h / 0.2) * 0.2, near_face(k, X, S, f, p, s, 1)))
    for nm in ('SPKBOX_L', 'SPKBOX_R'):
        b = X.body(nm)
        for f, p, s in level(k, b, 1):
            if abs(p[1] + 0.80) < 0.003 or abs(p[1] + 20.80) < 0.003:
                h = p[1] + 52.0
                print('%s y %.4f %s %8.2f mm2, height %.4f off %+.4f: %s' % (nm, p[1], 'looks +y' if s > 0 else 'looks -y', f.area * 100, h, h - round(h / 0.2) * 0.2, near_face(k, X, b, f, p, s, 1)))
        for f, p, s in level(k, b, 2):
            if p[2] < 4.0 and s < 0 and f.area * 100 > 5.0:
                print('%s z %.4f down %8.2f mm2: %s' % (nm, p[2], f.area * 100, near_face(k, X, b, f, p, s, 2)))


def st_screws(k, X):
    """The four floor screws (base plate to boxes): from the counterbore's floor and the box's bottom face as modelled."""
    P = X.body('FLOOR_PLATE')
    cb = sorted(set(round(k.W(f.pointOnFace)[2], 3) for f, p, s in I30['level'](k, P, 2) if s < 0 and abs(k.W(f.pointOnFace)[2] - 1.0) < 0.01))
    for nm in ('SPKBOX_L', 'SPKBOX_R'):
        b = X.body(nm)
        bot = min(p[2] for f, p, s in I30['level'](k, b, 2) if s < 0 and f.area * 100 > 500)
        holes = []
        for f in b.faces:
            gm = f.geometry
            if gm.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType and abs(gm.radius * 10 - 2.0) < 0.01 and abs(abs(k.unit(k.wv(gm.axis))[2]) - 1) < 1e-3:
                bx = I30['fbox'](k, f)
                if bx and bx[4] < 5.0:
                    holes.append((round(k.W(gm.origin)[0], 2), round(k.W(gm.origin)[1], 2), bx[4], bx[5]))
        for h in sorted(set(holes)):
            tip = cb[0] + 8.0
            print('%s floor insert hole at (%.2f, %.2f): from z %.2f to %.2f (%.2f deep); counterbore floor z %.2f, screw tip z %.2f: thread in the insert %.2f of 5.7, tip %.2f below the hole\'s floor; plate under the head %.2f' % (
                nm, h[0], h[1], h[2], h[3], h[3] - h[2], cb[0], tip, min(tip, h[2] + 5.7) - h[2], h[3] - tip, h[2] - cb[0]))


def _main(stage, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'fits': st_fits, 'faces': st_faces, 'screws': st_screws}[stage](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(stage, tag='', **kw):
    L['out']('d32_%s%s.txt' % (stage, ('_' + tag) if tag else ''), _main, stage, **kw)
# END
