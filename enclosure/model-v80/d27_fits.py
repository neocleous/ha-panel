# Block 2 and the close: the fits at the drivers, read on the model as it stands (after the put; on the saved version when
# the document is not modified). READ-ONLY: temporary bodies only (this Fusion measures distances to temporary bodies, so no
# TMP_ body is added to the document).
#   near     smallest distances, body to body, between the bodies of the drivers' joint (model bodies; no TMP)
#   push     the plate unit pushed forward in steps against the shell and the screen plate: the order of the stops; the seat's
#            contact area; D429's figures by needles (tongue faces to the lips, the noses over the lips), after p59_preflight
#   ring     each driver's ring as a temporary body of its own (36 across, 2.0 proud), the flange's front disc, the magnet and the
#            connector's envelope: their true distances to the shell or the box at home, with the nearest points
#   walk     the shell's way down, after p52b_window: the plate unit b behind and h below its place against the shell cropped
#            near the movers. case 'drivers' (driver, foam, screw heads against the bay), 'tongues' (base plate at the chin),
#            'frame' (boxes at the door frame's lower ends), 'boxes' (the boxes' fronts and clips' blocks against the shell);
#            side = to one side by s (+ toward the viewer's left)
#   clipkey  the 2.0 key on each clip's screw (d14's sweep) with the true distance to the nearest body every 15 deg
#   grid     level faces (square to the print's height) of the boxes, the shell and the clips where this pass changed them, with
#            their height above the bed and what they miss the layer grid by
#   guards   counts, and the guard volumes of all 17 printed parts by both readings (D425), beside version 79's
# Run: runpy.run_path(D + 'd27_fits.py')['main'](stage, tag, **kw)  -> d27_<stage>_<tag>.txt
import runpy, math, re, time
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')
AX = 70.5; AZ = 28.0
PLN = adsk.core.SurfaceTypes.PlaneSurfaceType


def dist(k, X, a, b):
    r = X.mm.measureMinimumDistance(a, b)
    return r.value * 10.0, k.r2(k.W(r.positionOne), 3), k.r2(k.W(r.positionTwo), 3)


def st_near(k, X):
    P = [('SPK_L', 'HOUSING_F_front'), ('SPK_R', 'HOUSING_F_front'), ('DRV_screw_heads_env', 'HOUSING_F_front'), ('DRV_screw_heads_env', 'SPK_L'),
         ('FOAM_spk_L_env', 'SPKBOX_L'), ('FOAM_spk_L_env', 'SPK_L'), ('FOAM_spk_R_env', 'SPKBOX_R'), ('FOAM_spk_R_env', 'SPK_R'),
         ('SPKBOX_L', 'HOUSING_F_front'), ('SPKBOX_R', 'HOUSING_F_front'), ('SPKBOX_L', 'HOUSING_F_plate'), ('SPKBOX_R', 'HOUSING_F_plate'),
         ('FLOOR_PLATE', 'HOUSING_F_front'), ('SPK_L', 'SPKBOX_L'), ('SPK_R', 'SPKBOX_R'), ('USBA_plug_env', 'SPKBOX_L'), ('USBA_plug_env', 'SPK_L'),
         ('LEAD_SPK_L', 'SPK_L'), ('LEAD_SPK_R', 'SPK_R'), ('LEAD_SPK_L', 'SPKBOX_L'), ('LEAD_SPK_R', 'SPKBOX_R'),
         ('TOUCH_CLIP_L', 'SPKBOX_L'), ('TOUCH_CLIP_R', 'SPKBOX_R'), ('TOUCH_CLIP_L', 'HOUSING_F_front'), ('TOUCH_CLIP_R', 'HOUSING_F_front'),
         ('TOUCH_CLIP_L', 'TOUCH_PCB'), ('TOUCH_CLIP_R', 'TOUCH_PCB'), ('TOUCH_CLIP_L', 'RADAR_HOLDER'), ('TOUCH_CLIP_L', 'LD2410C_env_F'),
         ('TOUCH_CLIP_R', 'GPIO_plugA_env'), ('TOUCH_CLIP_L', 'PIPWR_a_env'), ('RADAR_HOLDER', 'SPKBOX_L'), ('SPK_L', 'TOUCH_CLIP_L')]
    for a, b in P:
        A = X.body(a); B = X.body(b)
        if A is None or B is None:
            print('%-22s to %-18s: a body is missing' % (a, b)); continue
        d, p, q = dist(k, X, A, B)
        print('%-22s to %-18s %8.4f  at %s / %s' % (a, b, d, p, q))


UNIT = ['SPK_L', 'SPK_R', 'DRV_screw_heads_env', 'FOAM_spk_L_env', 'FOAM_spk_R_env', 'SPKBOX_L', 'SPKBOX_R', 'FLOOR_PLATE', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R']


def ny(k, X, c, x, z, y0=-3.0, y1=8.0):
    return [(round(y0 + a, 2), round(y0 + b, 2)) for a, b in k.needle_t(X, [c], (x, y0, z), (x, y1, z), 0.02)]


def st_push(k, X):
    k.budget(72)
    fixed = {'HOUSING_F_front': L['crop'](X, 'HOUSING_F_front', (-110, 110, -62, 8, 0, 90)), 'HOUSING_F_plate': X.tbm.copy(X.body('HOUSING_F_plate')),
             'TOUCH_PCB': X.tbm.copy(X.body('TOUCH_PCB'))}
    movers = {}
    for n in UNIT:
        m = X.tbm.copy(X.body(n))
        if n == 'FLOOR_PLATE':
            X.sec(m, X.wbox(-110, 110, -8, 9, -1, 15))
        movers[n] = m
    first = {}
    for d in (0.0, 0.02, 0.1, 0.2, 0.24, 0.26, 0.28, 0.3, 0.32, 0.34, 0.36, 0.4, 0.5, 0.6, 0.68, 0.72, 0.8):
        for n, m in movers.items():
            t = X.move(X.tbm.copy(m), 0.0, d, 0.0)
            for fn, f in fixed.items():
                if (n, fn) in first:
                    continue
                v = X.xv(t, f)
                if abs(v) > 0.0005:
                    first[(n, fn)] = (d, round(v, 3))
        if k.late():
            print('time at', d); break
    print('the plate unit pushed forward: the first step at which each pair shares volume (steps 0.02, 0.1, 0.2, 0.24, 0.26, 0.28 ... 0.8)')
    for (n, fn), (d, v) in sorted(first.items(), key=lambda q: q[1][0]):
        print('   %-22s | %-16s from %.2f (%.3f mm3)' % (n, fn, d, v))
    sh = fixed['HOUSING_F_front']
    for n in ('SPK_L', 'SPK_R'):
        v = X.xv(X.move(X.tbm.copy(movers[n]), 0.0, 0.05, 0.0), sh)
        print('   seat: %s 0.05 forward shares %.4f: contact %.1f mm2' % (n, v, v / 0.05))
    shc = L['crop'](X, 'HOUSING_F_front', (-40, 40, -3, 8, 2, 6)); pl = L['crop'](X, 'FLOOR_PLATE', (-40, 40, -3, 8, 2, 6))
    gaps = []; ov = {}
    for x in (-35.0, -30.0, -25.0, 25.0, 30.0, 35.0):
        for z in (2.9, 3.3, 3.7, 4.1):
            s = ny(k, X, shc, x, z); p = ny(k, X, pl, x, z)
            lip = [a for a, b in s if a > 0.5]; pf = [b for a, b in p if b < 3.0]
            if lip and pf:
                gaps.append(round(min(lip) - max(pf), 3))
        lip_r = [a for a, b in ny(k, X, shc, x, 4.0) if a > 0.5]
        for z in (4.4, 4.6, 4.8, 5.0):
            p = ny(k, X, pl, x, z)
            if p and lip_r:
                ov.setdefault(z, []).append(round(max(b for a, b in p) - min(lip_r), 3))
    print('   tongue faces to the chin lips\' rear faces, 24 stations: least %s, most %s' % (min(gaps), max(gaps)))
    print('   noses over the lips, by height: %s' % {z: (min(v), max(v)) for z, v in sorted(ov.items())})


def st_ring(k, X):
    S = X.body('HOUSING_F_front')
    for sx, s in ((1, 'L'), (-1, 'R')):
        rg = X.cyl((sx * AX, 0.0, AZ), (sx * AX, 2.0, AZ), 18.0)
        d, p, q = dist(k, X, rg, S)
        print('ring %s (36 across, y 0.0 to 2.0) to the shell: %.4f at %s / %s' % (s, d, p, q))
        top = X.cyl((sx * AX, 1.99, AZ), (sx * AX, 2.0, AZ), 18.0)
        d, p, q = dist(k, X, top, S)
        print('   its top face (y 2.0) to the shell: %.4f at %s / %s' % (d, p, q))
        for nm, z0, z1 in (('upper half', AZ, AZ + 30), ('lower half', AZ - 30, AZ)):
            h = X.cyl((sx * AX, 0.3, AZ), (sx * AX, 2.0, AZ), 18.0); X.sec(h, X.wbox(sx * AX - 30, sx * AX + 30, -1, 3, z0, z1))
            d, p, q = dist(k, X, h, S)
            print('   its %s above y 0.3 (clear of the seat\'s plane) to the shell: %.4f at %s / %s' % (nm, d, p, q))
        cn = X.cyl((sx * AX, -0.01, AZ), (sx * AX, 0.0, AZ), 16.0)
        c2 = L['crop'](X, 'HOUSING_F_front', (sx * AX - 16.0, sx * AX + 16.0, 2.5, 8.0, AZ - 16.0, AZ + 16.0))
        d, p, q = dist(k, X, cn, c2)
        print('   the flange\'s front plane inside the ring (the cone\'s highest point lies about there) to the grille: %.4f at %s / %s' % (d, p, q))
        mg = X.cyl((sx * AX, -28.8, AZ), (sx * AX, -18.8, AZ), 16.0)
        d, p, q = dist(k, X, mg, X.body('SPKBOX_' + s))
        print('   the magnet (32 across, the last 10) to the box: %.4f at %s / %s' % (d, p, q))
        cu = X.wbox(sx * AX - 16.0, sx * AX + 16.0, -28.8, -18.8, AZ, AZ + 18.25)
        d, p, q = dist(k, X, cu, X.body('SPKBOX_' + s))
        print('   the connector\'s envelope (up) to the box: %.4f at %s / %s' % (d, p, q))


CASES = {
    'drivers': (lambda s: ['SPK_' + s, 'FOAM_spk_%s_env' % s, 'DRV_screw_heads_env'], lambda sx: [tuple(sorted((sx * 40.0, sx * 110.0))) + (-8.0, 8.0, 0.0, 62.0)], None,
                [0.5 * i for i in range(0, 125)]),
    'tongues': (lambda s: ['FLOOR_PLATE'], lambda sx: [(-100, 100, -3, 8, 0, 12)], (-100, 100, -6, 9, -1, 15), [0.25 * i for i in range(0, 17)]),
    'frame': (lambda s: ['SPKBOX_' + s], lambda sx: [tuple(sorted((sx * 30.0, sx * 110.0))) + (-58.0, -48.0, 0.0, 85.0)], None, [1.0 * i for i in range(0, 31)]),
    'boxes': (lambda s: ['SPKBOX_' + s, 'TOUCH_CLIP_' + s], lambda sx: [tuple(sorted((sx * 30.0, sx * 110.0))) + (-16.0, 8.0, 0.0, 90.0)], None, [1.0 * i for i in range(0, 63)]),
}


def st_walk(k, X, case='drivers', side='L', bs=(0.95, 1.6), s=0.0, sec=70):
    k.budget(sec)
    t0 = time.time()
    sx = 1 if side == 'L' else -1
    names, boxes, near, hs = CASES[case]
    crops = [L['crop'](X, 'HOUSING_F_front', bx) for bx in boxes(sx)]
    movers = []
    for n in names(side):
        m = X.tbm.copy(X.body(n))
        if case == 'drivers' and n == 'DRV_screw_heads_env':
            X.sec(m, X.wbox(*sorted((sx * 40.0, sx * 110.0)), -8, 8, 0, 62))
        if near:
            X.sec(m, X.wbox(*near))
        if case == 'frame':
            X.sec(m, X.wbox(-110, 110, -53.0, -47.0, -1, 85))
        if case == 'boxes':
            X.sec(m, X.wbox(-110, 110, -16.0, 8.0, -1, 90))
        movers.append(m)
    for b in bs:
        hit = []
        for h in hs:
            v = 0.0
            for m in movers:
                t = X.move(X.tbm.copy(m), s, -b, -h)
                for cr in crops:
                    v += X.xv(t, cr)
            if v > 0.0005:
                hit.append((h, round(v, 4)))
            if k.late():
                break
        print('%-8s %s, %.2f to the side, %.2f behind: %s%s' % (case, side, s, b, ('meets at lifts %s' % hit[:6]) if hit else 'clear at every lift (%d lifts to %.1f)' % (len(hs), hs[-1]),
              '  TIME: not finished' if k.late() else ''))
        if k.late():
            break
    print('   %.1f s' % (time.time() - t0))


def st_clipkey(k, X, state='build', holder=False, sides=('L', 'R')):
    C = runpy.run_path(D + 'd14_clip.py')
    y = runpy.run_path(D + 'd20_build.py')['CLIP_Y']; PZ = 38.0
    k.budget(70)
    off_ = () if holder else ('RADAR_HOLDER', 'LD2410C_env_F')
    for side in sides:
        sx = 1.0 if side == 'L' else -1.0
        xe = sx * 24.9
        zone = X.wbox(min(xe, sx * 41.0) - 6.0, max(xe, sx * 41.0) + 6.0, -120.0, 12.0, -50.0, 185.0)
        fx = []
        for b in C['hard'](k, X, state, skip=off_):
            if b.name == 'TOUCH_CLIP_' + side:
                continue
            t = X.tbm.copy(b)
            if not t.boundingBox.intersects(zone.boundingBox):
                continue
            X.sec(t, X.tbm.copy(zone))
            if t.faces.count:
                fx.append((b.name, t))

        def nearest(t):
            best = None
            for nm, f in fx:
                d, p, q = dist(k, X, t, f)
                if best is None or d < best[0]:
                    best = (d, nm, q)
            return best
        d, nm, q = nearest(X.cyl((sx * 40.5, y, PZ), (sx * 38.85, y, PZ), 2.85))
        print('clip %s, screw at y %.2f, state %s, holder and radar %s: the head (5.7 across, 1.65 high) to the nearest body: %.3f, %s at %s' % (
            side, y, state, 'on' if holder else 'off', d, nm, q))
        rows = []
        for phi in range(0, 96, 15):
            r = math.radians(phi)
            d, nm, q = nearest(X.cyl((xe, y, PZ), (xe, y - 101.0 * math.cos(r), PZ + 101.0 * math.sin(r)), 1.2))
            rows.append('%d deg: %.2f %s' % (phi, d, k.sn(nm)))
            if k.late():
                rows.append('time'); break
        print('   long arm to the nearest body: ' + '; '.join(rows))


def off(h, lh=0.2):
    q = h / lh
    return (q - round(q)) * lh


def st_grid(k, X):
    rows = []
    for name, bed, sign, boxes in (('SPKBOX_L', -52.0, 1, [(38, 102, -13.5, 0, 0, 56), (53, 58, -33, -19, 17, 23)]), ('SPKBOX_R', -52.0, 1, [(-102, -38, -13.5, 0, 0, 56)]),
                                   ('HOUSING_F_front', 6.7992, -1, [(44, 97, -1, 7, 0, 56), (-97, -44, -1, 7, 0, 56)])):
        b = X.body(name)
        seen = {}
        for f in b.faces:
            if f.geometry.surfaceType != PLN:
                continue
            ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
            n = k.wv(nv)
            if abs(abs(n[1]) - 1) > 1e-4:
                continue
            ws = [k.W(v.geometry) for v in f.vertices]
            if not ws:
                continue
            e = [fn(w[i] for w in ws) for i in range(3) for fn in (min, max)]
            if not any(e[0] <= q[1] and e[1] >= q[0] and e[2] <= q[3] and e[3] >= q[2] and e[4] <= q[5] and e[5] >= q[4] for q in boxes):
                continue
            y = k.W(f.pointOnFace)[1]
            h = sign * (y - bed)
            key = (round(y, 4), 'up' if sign * n[1] > 0 else 'down')
            a = seen.setdefault(key, [0.0, 0, h])
            a[0] += f.area * 100; a[1] += 1
        print('%s (bed y %.4f): level faces in the places this pass changed: y, looking up or down in the print, height, off the 0.2 grid, mm2, faces' % (name, bed))
        for (y, d), (ar, cnt, h) in sorted(seen.items()):
            o = off(h)
            print('   y %9.4f %-4s height %8.4f  off %+.4f  %9.2f mm2  %d%s' % (y, d, h, o, ar, cnt, '' if abs(o) < 0.002 else '   OFF'))
    for name in ('TOUCH_CLIP_L', 'TOUCH_CLIP_R'):
        b = X.body(name); zs = {}
        for f in b.faces:
            if f.geometry.surfaceType != PLN:
                continue
            ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
            n = k.wv(nv)
            if abs(abs(n[2]) - 1) > 1e-4:
                continue
            z = round(k.W(f.pointOnFace)[2], 4)
            zs[z] = zs.get(z, 0.0) + f.area * 100
        print('%s (as fitted, bed z 30.0): level faces: %s' % (name, ', '.join('z %.2f (height %.2f, off %+.2f, %.1f mm2)' % (z, z - 30.0, off(z - 30.0), a) for z, a in sorted(zs.items()))))


def st_guards(k, X):
    st = X.state(); names = X.names(); cur = k.current(X, leads=True)
    df = X.doc.dataFile
    print('version %d of %d, modified %s; bodies %d, visible %d, in the unit %d; hidden copies _v67/_v68/_v69 %d, _v79 %d; TMP_ %d' % (
        df.versionNumber, df.latestVersionNumber, X.doc.isModified, st['bodies'], st['visible'], len(cur),
        sum(1 for n in names if re.search(r'_v6[789]$', n)), sum(1 for n in names if n.endswith('_v79')), sum(1 for n in names if n.startswith('TMP_'))))
    kinds = {}
    for b in cur:
        n = b.name
        q = 'printed' if n in L['PRINTED'] else 'lead' if n.startswith('LEAD_') else 'keep-out' if n.startswith('KO_') else 'bought or envelope'
        kinds[q] = kinds.get(q, 0) + 1
    print('in the unit: %s' % kinds)
    print('%-16s %13s %13s | %13s %13s | %10s' % ('body', 'preflight', 'very high', 'v79 prefl.', 'v79 v.high', 'change'))
    for n in L['PRINTED']:
        b = X.body(n)
        vp = b.volume * 1000.0; vh = L['vhi'](b); rp, rh = L['GUARD79'][n]
        print('%-16s %13.3f %13.3f | %13.3f %13.3f | %+10.3f  lumps %d%s' % (n, vp, vh, rp, rh, vp - rp, b.lumps.count, '' if abs(vp - rp) < 0.0015 else '   changed'))
    for n in ('SPK_L', 'SPK_R', 'DRV_screw_heads_env', 'FOAM_spk_L_env', 'FOAM_spk_R_env', 'LEAD_SPK_L', 'LEAD_SPK_R'):
        b = X.body(n)
        print('%-20s %12.3f %12.3f  lumps %d  visible %s' % (n, b.volume * 1000, L['vhi'](b), b.lumps.count, b.isLightBulbOn))


def _main(stage, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    try:
        {'near': st_near, 'push': st_push, 'ring': st_ring, 'walk': st_walk, 'clipkey': st_clipkey, 'grid': st_grid, 'guards': st_guards}[stage](k, X, **kw)
    finally:
        left = [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]
        for b in left:
            b.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main(stage, tag='', **kw):
    L['out']('d27_%s%s.txt' % (stage, ('_' + tag) if tag else ''), _main, stage, **kw)
# END
