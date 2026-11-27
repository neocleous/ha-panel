# Block 1 (change 1, D529): the two speaker boxes with the opening back to 40.6 across and the stops' flares whole, as version 85
# had them; everything else of version 88 kept. Builds temporary bodies and keeps them in the library's cache k.c; NOTHING IS PUT
# INTO THE DOCUMENT here (s21_put.py does that).
# World mm: x + = viewer's left, y + toward the screen, z up. Side 'L' x > 0. A box prints rear face down: bed = y + 52.
# The build is ../model-v85/m15_build.py's, step for step, from the hidden copies SPKBOX_<s>_v85, with one difference:
#   the aim-2 envelope E is cut off at the front wall's inner face, y -7.0 (m: s10_faces_L85_front.txt, the plane looking back at
#   y -7.0, 712.64 mm2; the wall runs from there to the box's face at y -5.0). D529: "Aim 2 does not apply to the opening the
#   driver sits in, nor to the stops; it applies behind the front wall's inner face."
# So the opening through the wall stays the copy's (20.3 from the axis) and the stops' 45 deg flares stay whole; behind the wall
# E cuts as before (each clip block's lower corner; the pockets; the room behind the driver).
#   build    both boxes -> k.c['sr_box_L'], k.c['sr_box_R']; beside each: the same build with the whole E against the model's
#            box (it must be the model's box: the proof that only the cut-off differs), and the new box against the model's
#            box and against the copy, by slabs of y
#   front    the opening and the stops on the new box: the faces round the opening, the new box against the copy inside 23.0 of
#            the axis in front of y -7.0 (must be the same), the foam's seat at mid-side (needles on the box's face, through the
#            foam and through the driver's flange, four directions)
#   drv      the driver's zones to the new box (m12's zones), E cut off inside it, the chamber (d27's method) beside the model's
#            and the copy's
#   share    what the new box shares with every body of the unit, beside what the model's box shares
#   grid     level faces (square to y) of the new box against the model's box and the copy; flat faces under 0.3 mm2 that the
#            model's box does not have
# Run: L.checked('s20_boxes.py', sha)['main'](stage, tag, **kw)  -> s20_<stage>_<tag>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/screw_margins_v88/'
L = runpy.run_path(D + 's00_lib.py')
AX = 70.5; AZ = 28.0; HALF = 17.75
Y_BACK = -3.8; Y_REAR = -28.8
Y_FACE = -5.0; Y_STOP = -4.0
Y_IN = -7.0            # the front wall's inner face (m)
Y_FLOOR = -11.6; Y_FLOOR_IL = -11.0
PLN = adsk.core.SurfaceTypes.PlaneSurfaceType


def inner_lower(px, pz):
    return abs(abs(px) - (AX - HALF)) < 0.01 and pz < AZ


def screws(sx):
    return [(sx * (AX + a * HALF), AZ + b * HALF) for a in (-1, 1) for b in (-1, 1)]


def E(k, X, sx, g=1.0, behind=2.0, cut=True):
    """m15_build.E, and (cut) only what of it lies behind the front wall's inner face."""
    cx = sx * AX
    e = X.cyl((cx, Y_BACK + 0.3, AZ), (cx, Y_REAR + 13.0, AZ), 20.0 + g + 0.05, 18.75 + g + 0.05)
    X.uni(e, X.cyl((cx, Y_REAR + 13.0, AZ), (cx, Y_REAR + 10.0 - g, AZ), 18.75 + g))
    X.uni(e, X.cyl((cx, Y_REAR + 10.0, AZ), (cx, Y_REAR - g, AZ), 16.0 + g))
    X.uni(e, X.cyl((cx, Y_REAR, AZ), (cx, Y_REAR - behind, AZ), 16.0))
    X.uni(e, X.wbox(cx - 16.0 - g, cx + 16.0 + g, Y_REAR + 10.0 + g, Y_REAR - g, AZ - g, AZ + 18.25 + g))
    X.uni(e, X.wbox(cx - 16.0, cx + 16.0, Y_REAR, Y_REAR - behind, AZ, AZ + 18.25))
    if cut:
        X.sec(e, X.wbox(cx - 45.0, cx + 45.0, Y_IN, -70.0, AZ - 45.0, AZ + 45.0))
    return e


def src(X, name):
    return X.body(name + '_v85')


def build(k, X, sx, cut=True):
    """m15_build.build with E cut off at the wall's inner face (cut=True); with cut=False it is m15's build, version 88's box."""
    s = 'L' if sx > 0 else 'R'; cx = sx * AX
    t = X.tbm.copy(src(X, 'SPKBOX_' + s))
    if sx > 0:
        f = X.cyl((cx, -31.4, AZ), (cx, -20.7, AZ), 18.5)
        X.uni(f, X.cyl((cx, -35.7, AZ), (cx, -31.4, AZ), 16.4, 18.5))
        X.sec(f, X.wbox(44.0, 55.65, -52.0, -20.8, 3.8, 20.7)); X.uni(t, f)
        f2 = X.cyl((cx, -21.2, AZ), (cx, -20.7, AZ), 20.0)
        X.sec(f2, X.wbox(40.0, 55.65, -21.2, -20.8, 3.8, 20.7)); X.uni(t, f2)
    else:
        f = X.cyl((cx, -32.4, AZ), (cx, -30.9, AZ), 17.5)
        X.sec(f, X.wbox(-64.0, -46.0, -32.4, -31.0, 3.8, 16.0)); X.uni(t, f)
    for px, pz in screws(sx):
        if not inner_lower(px, pz):
            X.uni(t, X.cyl((px, -12.8, pz), (px, -12.5, pz), 4.0))
    for bx, by in ((64.0, -45.0),) if sx > 0 else ((-72.0, -38.0),):
        X.uni(t, X.cyl((bx, by, 11.1), (bx, by, 11.5), 4.0))
    if sx < 0:
        X.uni(t, X.wbox(-51.0, -50.4, -12.8, -6.1, 37.65, 44.35))
    X.dif(t, E(k, X, sx, cut=cut))
    for px, pz in screws(sx):
        X.dif(t, X.cyl((px, Y_FLOOR_IL if inner_lower(px, pz) else Y_FLOOR, pz), (px, -10.5, pz), 2.0))
    for bx, by in ((64.0, -45.0),) if sx > 0 else ((-72.0, -38.0),):
        X.dif(t, X.cyl((bx, by, 10.1), (bx, by, 10.5), 2.0))
    if sx > 0:
        X.dif(t, X.cyl((45.25, -7.35, 57.6), (46.5, -7.35, 57.6), 1.35))
        X.dif(t, X.cyl((49.15, -9.45, 35.0), (49.5, -9.45, 35.0), 1.35))
    else:
        X.dif(t, X.cyl((-49.15, -9.45, 41.0), (-50.0, -9.45, 41.0), 1.35))
    return t


def less(X, a, b):
    t = X.tbm.copy(a); X.dif(t, X.tbm.copy(b))
    return t


def slabs(k, X, t, ys):
    if not t.faces.count:
        return
    bb = k.wbb(X, t)
    for i in range(len(ys) - 1):
        s = X.tbm.copy(t)
        X.sec(s, X.wbox(bb[0] - 1, bb[1] + 1, ys[i], ys[i + 1], bb[4] - 1, bb[5] + 1))
        if s.faces.count and X.vol(s) > 1e-5:
            print('      y %7.2f to %7.2f: %9.4f mm3, world box %s' % (ys[i], ys[i + 1], X.vol(s), k.wbb(X, s)))


def show(k, X, lab, t, ys=None):
    n = t.lumps.count if t.faces.count else 0
    print('   %s: %.4f mm3 in %d lumps%s' % (lab, X.vol(t) if n else 0.0, n, (': %s' % X.lumps(t)[:12]) if n else ''))
    if ys and n:
        slabs(k, X, t, ys)


def st_build(k, X, sides=('L', 'R')):
    k.budget(70)
    ys = [-13.0 + 0.5 * i for i in range(20)]
    for sx, s in ((1, 'L'), (-1, 'R')):
        if s not in sides:
            continue
        m = X.body('SPKBOX_' + s); o = src(X, 'SPKBOX_' + s)
        full = build(k, X, sx, cut=False)
        print('SPKBOX_%s: the model\'s box %.3f mm3, lumps %d, faces %d; the copy %s %.3f mm3, faces %d' % (
            s, m.volume * 1000.0, m.lumps.count, m.faces.count, o.name, o.volume * 1000.0, o.faces.count))
        print('  m15\'s build again (the whole E): %.3f mm3, lumps %d, faces %d' % (X.vol(full), full.lumps.count, full.faces.count))
        show(k, X, 'it less the model\'s box', less(X, full, m)); show(k, X, 'the model\'s box less it', less(X, m, full))
        t = build(k, X, sx, cut=True)
        k.c['sr_box_' + s] = t
        print('  sr_box_%s (E cut off at y %.1f): %.3f mm3, lumps %d, faces %d; %+.3f against the model\'s box, %+.3f against the copy' % (
            s, Y_IN, X.vol(t), t.lumps.count, t.faces.count, X.vol(t) - m.volume * 1000.0, X.vol(t) - o.volume * 1000.0))
        show(k, X, 'the model\'s box less sr_box (must be nothing)', less(X, m, t))
        show(k, X, 'sr_box less the model\'s box (what comes back)', less(X, t, m), ys)
        show(k, X, 'the copy less sr_box', less(X, o, t), ys)
        show(k, X, 'sr_box less the copy', less(X, t, o), ys)
        back = less(X, t, m)
        far = X.tbm.copy(back)
        z = X.cyl((sx * AX, Y_IN, AZ), (sx * AX, Y_STOP, AZ), 21.06)
        X.dif(far, z)
        print('   what comes back outside 21.06 of the axis or outside y %.1f to %.1f: %.5f mm3' % (Y_IN, Y_STOP, X.vol(far) if far.faces.count else 0.0))


def radial(k, X, plist, cx, y, ang, r0=15.0, r1=30.0):
    a = math.radians(ang); d = (math.cos(a), 0.0, math.sin(a))
    st = k.needle_t(X, plist, (cx + r0 * d[0], y, AZ + r0 * d[2]), (cx + r1 * d[0], y, AZ + r1 * d[2]), 0.02)
    return [(round(r0 + p, 2), round(r0 + q, 2)) for p, q in st]


def st_front(k, X, sides=('L', 'R')):
    k.budget(70)
    for sx, s in ((1, 'L'), (-1, 'R')):
        if s not in sides:
            continue
        cx = sx * AX; t = k.c['sr_box_' + s]; o = src(X, 'SPKBOX_' + s); m = X.body('SPKBOX_' + s)
        print('sr_box_%s: the opening and the stops' % s)
        for lab, body in (('sr_box', t), ('the copy _v85', o), ('the model\'s box (version 88)', m)):
            rows = []
            for f in body.faces:
                g = f.geometry; ty = g.surfaceType
                if ty == adsk.core.SurfaceTypes.CylinderSurfaceType:
                    og = k.W(g.origin); a = k.unit(k.wv(g.axis))
                    if abs(abs(a[1]) - 1) < 1e-6 and abs(og[0] - cx) < 0.01 and abs(og[2] - AZ) < 0.01:
                        ws = [k.W(v.geometry)[1] for v in f.vertices]
                        rows.append('cylinder about the axis r %.3f, y %.2f to %.2f, %.2f mm2' % (g.radius * 10.0, min(ws), max(ws), f.area * 100.0))
                elif ty == adsk.core.SurfaceTypes.ConeSurfaceType:
                    og = k.W(g.origin); a = k.unit(k.wv(g.axis))
                    if abs(abs(a[1]) - 1) < 1e-6 and og[1] > -8.0:
                        d = math.hypot(og[0] - cx, og[2] - AZ)
                        cs = sorted((round(e.geometry.radius * 10.0, 3), round(k.W(e.geometry.center)[1], 3)) for e in f.edges
                                    if e.geometry.curveType in (adsk.core.Curve3DTypes.Circle3DCurveType, adsk.core.Curve3DTypes.Arc3DCurveType))
                        rows.append('cone at (%.2f, %.2f), %.2f from the axis, half angle %.1f, %.3f mm2, circles (r, y) %s' % (
                            og[0], og[2], d, math.degrees(g.halfAngle), f.area * 100.0, cs))
            print('   %s:' % lab)
            for r in sorted(rows):
                print('      ' + r)
        zf = X.cyl((cx, Y_IN, AZ), (cx, -3.0, AZ), 23.0)
        a = X.tbm.copy(t); X.sec(a, X.tbm.copy(zf)); b = X.tbm.copy(o); X.sec(b, X.tbm.copy(zf))
        print('   inside 23.0 of the axis, y %.1f to -3.0: sr_box %.4f mm3, the copy %.4f mm3' % (Y_IN, X.vol(a), X.vol(b)))
        show(k, X, 'there, sr_box less the copy', less(X, a, b)); show(k, X, 'there, the copy less sr_box', less(X, b, a))
        fo = X.body('FOAM_spk_%s_env' % s); dr = X.body('SPK_' + s)
        print('   FOAM_spk_%s_env world box %s; SPK_%s world box %s' % (s, k.wbb(X, fo), s, k.wbb(X, dr)))
        fb = k.wbb(X, fo); yfo = (fb[2] + fb[3]) / 2.0
        print('   the foam\'s seat: radial needles from the axis (mm from the axis that are solid)')
        for ang in (0, 90, 180, 270, 45, 135, 225, 315):
            bn = radial(k, X, [t], cx, Y_FACE - 0.02, ang); bo = radial(k, X, [X.tbm.copy(o)], cx, Y_FACE - 0.02, ang)
            bm = radial(k, X, [X.tbm.copy(m)], cx, Y_FACE - 0.02, ang)
            fn = radial(k, X, [X.tbm.copy(fo)], cx, yfo, ang); dn = radial(k, X, [X.tbm.copy(dr)], cx, -1.9, ang)
            seat = None
            if bn and fn:
                seat = round(min(bn[0][1], fn[-1][1]) - max(bn[0][0], fn[0][0]), 2)
            print('      at %3d deg: box face (y %.2f) sr_box %s, copy %s, version 88 %s | foam (y %.2f) %s | flange (y -1.9) %s | foam on the face %s' % (
                ang, Y_FACE - 0.02, bn, bo, bm, yfo, fn, dn, seat))
        d = X.mm.measureMinimumDistance(fo, m)
        print('   FOAM_spk_%s_env to the model\'s box %.4f' % (s, d.value * 10.0))
        print('   the foam shares with sr_box %.4f mm3, with the model\'s box %.4f, with the copy %.4f' % (
            X.xv(X.tbm.copy(fo), X.tbm.copy(t)), X.xv(X.tbm.copy(fo), X.tbm.copy(m)), X.xv(X.tbm.copy(fo), X.tbm.copy(o))))


def dist(k, X, a, b):
    r = X.mm.measureMinimumDistance(a, b)
    return r.value * 10.0, k.r2(k.W(r.positionOne), 2), k.r2(k.W(r.positionTwo), 2)


def st_drv(k, X, sides=('L', 'R')):
    """Distances are measured to model bodies only, so the driver's zones are read by growing them (what a zone grown by g shares
    with the new box), as m12 does beside its distances."""
    k.budget(70)
    F27 = L['old']('d27')
    for sx, s in ((1, 'L'), (-1, 'R')):
        if s not in sides:
            continue
        cx = sx * AX; t = k.c['sr_box_' + s]; o = src(X, 'SPKBOX_' + s); m = X.body('SPKBOX_' + s)
        print('sr_box_%s: E cut off at y %.1f inside it %.5f mm3; the whole E inside it %.4f mm3 (the model\'s box: %.4f; the copy: %.4f)' % (
            s, Y_IN, X.xv(E(k, X, sx), X.tbm.copy(t)), X.xv(E(k, X, sx, cut=False), X.tbm.copy(t)),
            X.xv(E(k, X, sx, cut=False), X.tbm.copy(m)), X.xv(E(k, X, sx, cut=False), X.tbm.copy(o))))
        for nm in ('basket', 'basket behind the wall', 'band 37.5', 'magnet', 'connector'):
            row = []
            for g in (0.2, 0.3, 0.35, 0.4, 0.45, 0.5, 0.7, 1.0, 1.02, 1.5, 2.0):
                if nm == 'connector':
                    z = X.wbox(cx - 16.0 - g, cx + 16.0 + g, Y_REAR + 10.0 + g, Y_REAR - g, AZ - g, AZ + 18.25 + g)
                elif nm == 'magnet':
                    z = X.cyl((cx, Y_REAR + 10.0, AZ), (cx, Y_REAR - g, AZ), 16.0 + g)
                elif nm.startswith('basket'):
                    z = X.cyl((cx, Y_BACK - 0.05, AZ), (cx, Y_REAR + 13.0, AZ), 20.0 + g, 18.75 + g)
                    if nm != 'basket':
                        X.sec(z, X.wbox(cx - 45.0, cx + 45.0, Y_IN, -70.0, AZ - 45.0, AZ + 45.0))
                else:
                    z = X.cyl((cx, Y_REAR + 13.0, AZ), (cx, Y_REAR + 10.0, AZ), 18.75 + g)
                row.append('%.2f: %.3f' % (g, X.xv(z, X.tbm.copy(t))))
            print('   %-22s grown all round, shares with sr_box: %s' % (nm, '; '.join(row)))
        rr = X.cyl((cx, Y_REAR + 0.01, AZ), (cx, Y_REAR, AZ), 16.0); X.uni(rr, X.wbox(cx - 16.0, cx + 16.0, Y_REAR + 0.01, Y_REAR, AZ, AZ + 18.25))
        for dy in (1.99, 2.0, 2.1):
            mv = X.tbm.copy(rr); X.move(mv, 0.0, -dy, 0.0)
            print('   the rear face (magnet and connector) moved %.2f back: shares %.4f with sr_box' % (dy, X.xv(mv, X.tbm.copy(t))))
        print('   the model\'s driver SPK_%s shares %.4f mm3 with sr_box; the foam %.4f' % (
            s, X.xv(X.tbm.copy(X.body('SPK_' + s)), X.tbm.copy(t)), X.xv(X.tbm.copy(X.body('FOAM_spk_%s_env' % s)), X.tbm.copy(t))))
        for lab, body in (('sr_box', t), ('the model\'s box (version 88)', X.tbm.copy(m)), ('the copy _v85', X.tbm.copy(o))):
            a, bb, n = F27['chamber'](k, X, body, sx, Y_FACE, Y_STOP, 52.2)
            if a is None:
                print('   chamber of %s: no lump (%d lumps)' % (lab, n)); continue
            va = X.vol(a) / 1000.0; dv = X.xv(X.tbm.copy(X.body('SPK_' + s)), a) / 1000.0; ld = X.xv(X.tbm.copy(X.body('LEAD_SPK_' + s)), a) / 1000.0
            print('   chamber of %-28s air %.3f cm3 (%d lumps); the driver in it %.3f; the lead %.3f; less the driver %.3f; less both %.3f' % (
                lab + ':', va, n, dv, ld, va - dv, va - dv - ld))
        if k.late():
            print('time'); return


def st_share(k, X, sides=('L', 'R')):
    k.budget(72)
    for sx, s in ((1, 'L'), (-1, 'R')):
        if s not in sides:
            continue
        t = k.c['sr_box_' + s]; o = X.body('SPKBOX_' + s); tb = k.wbb(X, o); n = 0
        for b in k.current(X, leads=True, kos=True):
            if b.name.startswith('SPKBOX_'):
                continue
            q = k.wbb(X, b)
            if q[1] < tb[0] - 1 or q[0] > tb[1] + 1 or q[3] < tb[2] - 1 or q[2] > tb[3] + 1 or q[5] < tb[4] - 1 or q[4] > tb[5] + 1:
                continue
            parts = k.parts(X, b.name); n += 1
            vn = sum(X.xv(X.tbm.copy(t), p) for p in parts); vo = sum(X.xv(X.tbm.copy(o), p) for p in parts)
            if abs(vn) > 0.0005 or abs(vo) > 0.0005:
                print('   sr_box_%s | %-22s %10.4f  (the model\'s box: %10.4f)' % (s, b.name, vn, vo))
            if k.late():
                print('time at %s' % b.name); return
        print('   sr_box_%s: %d bodies near it read; done' % (s, n))


def levels(k, body):
    out = {}
    for f in body.faces:
        if f.geometry.surfaceType != PLN:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); n = k.wv(nv)
        if abs(abs(n[1]) - 1) > 1e-4:
            continue
        y = round(k.W(f.pointOnFace)[1], 3); key = (y, 'up' if n[1] > 0 else 'down')
        out[key] = out.get(key, 0.0) + f.area * 100
    return out


def st_grid(k, X, sides=('L', 'R')):
    for sx, s in ((1, 'L'), (-1, 'R')):
        if s not in sides:
            continue
        t = k.c['sr_box_' + s]; m = X.body('SPKBOX_' + s); o = src(X, 'SPKBOX_' + s)
        a = levels(k, t); b = levels(k, m); c = levels(k, o)
        print('sr_box_%s: level faces that differ from the model\'s box or the copy (y, looks, bed = y + 52, off the grid, mm2 sr_box / version 88 / copy _v85):' % s)
        for key in sorted(set(a) | set(b) | set(c)):
            na = a.get(key, 0.0); nb = b.get(key, 0.0); nc = c.get(key, 0.0)
            if abs(na - nb) < 0.005 and abs(na - nc) < 0.005:
                continue
            h = key[0] + 52.0; off = h - round(h / 0.2) * 0.2
            print('   y %8.3f %-4s bed %7.3f off %+.3f   %9.3f / %9.3f / %9.3f%s' % (key[0], key[1], h, off, na, nb, nc, '   OFF' if abs(off) > 0.002 and na > 0 else ''))
        res = []
        for body in (t, m, o):
            res.append([(round(f.area * 100.0, 4), tuple(k.r2(k.W(f.pointOnFace), 1))) for f in body.faces if f.area * 100.0 < 0.3])
        was = set(q[1] for q in res[1]); was85 = set(q[1] for q in res[2])
        print('   faces under 0.3 mm2: sr_box %d, version 88 %d, copy %d; not at a place of version 88\'s: %s; not at a place of the copy\'s: %s' % (
            len(res[0]), len(res[1]), len(res[2]), [q for q in res[0] if q[1] not in was][:20], [q for q in res[0] if q[1] not in was85][:20]))
        print('   faces: sr_box %d, version 88 %d, copy %d' % (t.faces.count, m.faces.count, o.faces.count))


def _main(stage, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'build': st_build, 'front': st_front, 'drv': st_drv, 'share': st_share, 'grid': st_grid}[stage](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(stage, tag='', **kw):
    L['out']('s20_%s%s.txt' % (stage, ('_' + tag) if tag else ''), _main, stage, **kw)
# END
