# Block 3, the two microphone clamps (D525): the seat of the M2 x 6 flat head 0.7 shallower, so that the head stands 0.7 proud
# under the clamp and the screw's tip has 1.0 to the floor of the cap's pilot. Builds temporary bodies and keeps them in the
# library's cache k.c; NOTHING IS PUT INTO THE DOCUMENT here (s21_put.py does that).
# The seat as the model has it (s10_faces_clamp_L.txt): a 90 deg countersink from 2.2 radius at the clamp's underside (z 172.7)
# to 1.1 at z 173.8, then a hole of 1.1 radius to z 174.5. As built here: a countersink from 1.5 at z 172.7 to 1.1 at z 173.1,
# then the hole of 1.1 to z 174.5 (1.4 long). The same cone, 0.7 lower: the head's own cone seats on it as before.
# A clamp prints as fitted (underside down, height = z - 172.7, layers 0.20): the cone's small end is at height 0.4.
#   build    both clamps -> k.c['sr_clamp_L'], k.c['sr_clamp_R']; and the screws' drawing with the two clamp screws 0.7 lower
#            -> k.c['sr_screws'] (SCREWS_M2x6_env is not a printed part: the drawing follows its seats)
#   check    each new clamp against the model's: what comes and goes, its seat's faces, flat faces under 0.3 mm2, level faces;
#            the moved screws: each one's extent on its axis, the tip's room in the cap's pilot, the thread, what the screw
#            shares with the clamp and the cap (now and moved), and every body of the unit within 6 of the moved screw
# Run: L.checked('s41_clamps.py', sha)['main'](what, tag, s31=sha)  -> s41_<what>_<tag>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/screw_margins_v88/'
L = runpy.run_path(D + 's00_lib.py')
ST = adsk.core.SurfaceTypes
CIRC = (adsk.core.Curve3DTypes.Circle3DCurveType, adsk.core.Curve3DTypes.Arc3DCurveType)
AXES = {'L': (15.5, -35.2), 'R': (-15.5, -35.2)}
Z_UNDER = 172.7; Z_SEAT = 173.8; Z_WEB = 174.5; UP = 0.7
MODS = {}


def seat(k, b, s):
    """The clamp's seat read off its faces: the hole (r 1.1) and the countersink's two circles."""
    x, y = AXES[s]
    h = MODS['s31']['hole_geo'](k, b, (x, y, Z_SEAT), (x, y, Z_WEB), 1.1)
    cones = []
    for f in b.faces:
        g = f.geometry
        if g.surfaceType != ST.ConeSurfaceType:
            continue
        o = k.W(g.origin)
        if math.hypot(o[0] - x, o[1] - y) > 0.01 or o[2] > 174.6:
            continue
        cs = sorted((round(k.W(e.geometry.center)[2], 4), round(e.geometry.radius * 10.0, 4)) for e in f.edges if e.geometry.curveType in CIRC)
        cones.append((round(math.degrees(g.halfAngle), 2), cs, round(f.area * 100.0, 3)))
    return h, cones


def build_clamp(k, X, s):
    S31 = MODS['s31']
    b = X.body('MIC_CLAMP_' + s)
    h, cones = seat(k, b, s)
    if len(cones) != 1 or cones[0][1] != [(Z_UNDER, 2.2), (Z_SEAT, 1.1)]:
        raise RuntimeError('MIC_CLAMP_%s: the seat is not the countersink recorded: %s' % (s, cones))
    P = lambda dz: S31['shift'](h['mouth'], h['axis'], dz)         # h['mouth'] is the hole's lower end (z 173.8); + = up, into the web
    t = X.tbm.copy(b)
    X.uni(t, X.tbm.createCylinderOrCone(P(Z_UNDER - Z_SEAT), 0.22, P(0.0), 0.22))               # the old countersink filled
    X.dif(t, X.tbm.createCylinderOrCone(P(Z_UNDER - Z_SEAT - 0.2), h['r'], P(0.2), h['r']))      # the hole of 1.1 carried down through it
    z0 = Z_UNDER - Z_SEAT - 0.2                                    # 0.2 below the underside, where the same cone is 0.2 wider
    X.dif(t, X.tbm.createCylinderOrCone(P(z0), h['r'] + 0.06, P(Z_UNDER - Z_SEAT + 0.4), h['r']))   # 45 deg: 1.7 at z 172.5, 1.5 at 172.7, 1.1 at 173.1
    return t, h, cones


def st_build(k, X):
    for s in ('L', 'R'):
        b = X.body('MIC_CLAMP_' + s)
        t, h, cones = build_clamp(k, X, s)
        k.c['sr_clamp_' + s] = t
        h2, c2 = seat(k, t, s)
        print('MIC_CLAMP_%s: %.3f mm3, lumps %d, faces %d -> sr_clamp_%s %.3f mm3 (%+.4f), lumps %d, faces %d' % (
            s, b.volume * 1000.0, b.lumps.count, b.faces.count, s, X.vol(t), X.vol(t) - b.volume * 1000.0, t.lumps.count, t.faces.count))
        print('   seat before: hole r %.4f, %.4f long, axis at %s; countersink (half angle, circles (z, r), mm2) %s' % (
            h['r'] * 10.0, h['depth'], k.r2(k.W(h['mouth']), 4), cones))
        print('   seat after:  hole r %.4f, %.4f long; countersink %s' % (h2['r'] * 10.0, h2['depth'], c2))
        for lab, a, c in (('what comes', t, b), ('what goes', b, t)):
            q = X.tbm.copy(a); X.dif(q, X.tbm.copy(c)); n = q.lumps.count if q.faces.count else 0
            print('   %s: %.4f mm3 in %d lumps %s' % (lab, X.vol(q) if n else 0.0, n, X.lumps(q)[:4] if n else ''))
    sc = X.body('SCREWS_M2x6_env'); t = None; moved = 0
    for l in sc.lumps:
        c = X.tbm.copy(l)
        ws = [k.W(v.geometry) for v in l.vertices]
        cx = sum(w[0] for w in ws) / len(ws); cy = sum(w[1] for w in ws) / len(ws); zs = [w[2] for w in ws]
        on = [s for s in ('L', 'R') if math.hypot(cx - AXES[s][0], cy - AXES[s][1]) < 1.6 and min(zs) > 172.0]
        if on:
            X.move(c, 0.0, 0.0, -UP); moved += 1
            print('   the drawn screw at the %s clamp: z %.3f to %.3f -> %.3f to %.3f' % (on[0], min(zs), max(zs), min(zs) - UP, max(zs) - UP))
        t = c if t is None else X.uni(t, c)
    if moved != 2:
        raise RuntimeError('%d drawn screws on the clamps\' axes, not 2' % moved)
    k.c['sr_screws'] = t
    print('SCREWS_M2x6_env: %.3f mm3, lumps %d -> sr_screws %.3f mm3, lumps %d' % (sc.volume * 1000.0, sc.lumps.count, X.vol(t), t.lumps.count))


def st_check(k, X):
    M10 = L['old']('m10')
    cap = X.body('HOUSING_F_cap'); sc = X.body('SCREWS_M2x6_env'); new = k.c['sr_screws']
    for s in ('L', 'R'):
        x, y = AXES[s]; b = X.body('MIC_CLAMP_' + s); t = k.c['sr_clamp_' + s]
        res = []
        for body in (t, b):
            res.append([(round(f.area * 100.0, 4), tuple(k.r2(k.W(f.pointOnFace), 1))) for f in body.faces if f.area * 100.0 < 0.3])
        was = set(q[1] for q in res[1])
        print('MIC_CLAMP_%s: faces under 0.3 mm2: new %d, the model\'s %d; not at a place of the model\'s: %s' % (s, len(res[0]), len(res[1]), [q for q in res[0] if q[1] not in was]))
        lv = []
        for body in (t, b):
            d = {}
            for f in body.faces:
                if f.geometry.surfaceType != ST.PlaneSurfaceType:
                    continue
                ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); n = k.wv(nv)
                if abs(abs(n[2]) - 1) < 1e-4:
                    q = (round(k.W(f.pointOnFace)[2] - Z_UNDER, 3), 'up' if n[2] > 0 else 'down'); d[q] = d.get(q, 0.0) + f.area * 100.0
            lv.append(d)
        diff = [(q, round(lv[0].get(q, 0.0), 3), round(lv[1].get(q, 0.0), 3)) for q in sorted(set(lv[0]) | set(lv[1])) if abs(lv[0].get(q, 0.0) - lv[1].get(q, 0.0)) > 0.005]
        print('   level faces that differ ((height, looks), mm2 new, mm2 the model\'s): %s' % (diff or 'none but the underside\'s opening'))
        for lab, body in (('new', t), ('the model\'s', b)):
            st = k.needle_t(X, [X.tbm.copy(body)], (x + 1.3, y, 171.0), (x + 1.3, y, 176.0), 0.02)
            st2 = k.needle_t(X, [X.tbm.copy(body)], (x + 1.8, y, 171.0), (x + 1.8, y, 176.0), 0.02)
            print('   %s clamp, solid on lines up from z 171 at 1.3 and 1.8 off the axis: %s; %s' % (lab, [(round(171 + a, 2), round(171 + c, 2)) for a, c in st], [(round(171 + a, 2), round(171 + c, 2)) for a, c in st2]))
        box = X.wbox(x - 2.6, x + 2.6, y - 2.6, y + 2.6, 170.0, 180.5)
        for lab, body, cl in (('as drawn now, in the model\'s clamp', sc, b), ('moved, in the new clamp', new, t)):
            q = X.tbm.copy(body); X.sec(q, X.tbm.copy(box))
            bb = k.wbb(X, q)
            pf = [f for f in cap.faces if f.geometry.surfaceType == ST.PlaneSurfaceType and abs(k.W(f.pointOnFace)[0] - x) < 0.9 and abs(k.W(f.pointOnFace)[1] - y) < 0.9 and k.W(f.pointOnFace)[2] > 178.0]
            zf = min(k.W(f.pointOnFace)[2] for f in pf) if pf else None
            print('   the screw %s: z %.3f to %.3f; head below the clamp\'s underside %.3f; tip to the pilot\'s floor (z %s) %.3f; thread above the pilot\'s mouth at z 174.9: %.3f; '
                  'shares %.4f mm3 with that clamp, %.4f with the cap' % (lab, bb[4], bb[5], Z_UNDER - bb[4], zf, (zf - bb[5]) if zf else -1, bb[5] - 174.9,
                                                                         X.xv(X.tbm.copy(q), X.tbm.copy(cl)), X.xv(X.tbm.copy(q), X.tbm.copy(cap))))
        q = X.tbm.copy(new); X.sec(q, X.tbm.copy(box)); qb = k.wbb(X, q); near = []
        for o in k.current(X, leads=True, kos=True):
            if o.name in ('SCREWS_M2x6_env', 'MIC_CLAMP_' + s, 'HOUSING_F_cap'):
                continue
            ob = k.wbb(X, o)
            if ob[0] > qb[1] + 6 or ob[1] < qb[0] - 6 or ob[2] > qb[3] + 6 or ob[3] < qb[2] - 6 or ob[4] > qb[5] + 6 or ob[5] < qb[4] - 6:
                continue
            r = X.mm.measureMinimumDistance(q, o)
            if r.value * 10.0 <= 6.0:
                near.append((round(r.value * 10.0, 3), o.name, k.r2(k.W(r.positionOne), 2), k.r2(k.W(r.positionTwo), 2)))
        print('   bodies within 6 of the moved screw (clamp and cap left out): %s' % sorted(near))
        u = X.wbox(x - 6.0, x + 6.0, y - 6.0, y + 6.0, Z_UNDER - 3.0, Z_UNDER - 0.001); hit = []
        for o in k.current(X, leads=True, kos=True):
            if o.name in ('SCREWS_M2x6_env',):
                continue
            v = sum(X.xv(X.tbm.copy(u), p) for p in k.parts(X, o.name)) if k.wbb(X, o)[5] > Z_UNDER - 3.0 and k.wbb(X, o)[4] < Z_UNDER else 0.0
            if v > 0.0005:
                hit.append((o.name, round(v, 3)))
        print('   bodies in the 3.0 under the clamp\'s underside, 6 round the axis: %s' % (hit or 'none'))


def _main(what, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'build': st_build, 'check': st_check}[what](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(what, tag='', s31=None, **kw):
    MODS['s31'] = L['checked']('s31_deepen.py', s31)
    L['out']('s41_%s%s.txt' % (what, ('_' + tag) if tag else ''), _main, what, **kw)
# END
