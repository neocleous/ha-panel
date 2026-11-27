# Block 1: the radar's layout study (D411, D412). READ-ONLY: temporary bodies and measurements only.
#   env()            the radar's envelope as modelled: its faces, outward normal, thickness; the lead's ends and length
#   probe(tag, box)  every body of the unit within lim of a world box: distance, or the volume it shares with the box
#   sweep(tag, c, rays, lim)  thin rays (r 0.05) from a world point: which bodies each meets within 'length', and where first
#                    (part B's method, b27_radar_view.py, generalised: every body of the unit whose box the ray's box meets)
#   section(tag, names, axis, value, win)  outlines of bodies cut by a world plane, as polylines, for pictures drawn elsewhere
# Each writes p10_<what>_<tag>.json in this folder and prints a summary. Run with runpy.run_path(D + 'p10_radar.py')[fn](...).
import runpy, math, time, json
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
PLN = adsk.core.SurfaceTypes.PlaneSurfaceType


def _X():
    k = L['load']()
    return k, k.K()


def _bb(k, X, b):
    """World box of a model body from its own bounds (a copy turned into the world frame)."""
    return k.wbb(X, b)


def env():
    k, X = _X()
    b = X.body('LD2410C_env_F')
    out = {'volume': round(b.volume * 1000.0, 3), 'faces': []}
    for f in b.faces:
        if f.geometry.surfaceType != PLN:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
        out['faces'].append({'area': round(f.area * 100.0, 2), 'n': [round(v, 4) for v in k.wv(nv)], 'c': [round(v, 2) for v in k.W(f.centroid)]})
    out['faces'].sort(key=lambda r: -r['area'])
    a, c = out['faces'][0], out['faces'][1]
    out['thickness'] = round(abs(sum((a['c'][i] - c['c'][i]) * a['n'][i] for i in range(3))), 3)
    out['world_box'] = [round(v, 2) for v in _bb(k, X, b)]
    ld = X.body('LEAD_RADAR')
    ends = []
    for f in ld.faces:
        if f.geometry.surfaceType == PLN:
            ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
            ends.append({'area': round(f.area * 100.0, 3), 'c': [round(v, 2) for v in k.W(f.centroid)], 'n': [round(v, 3) for v in k.wv(nv)]})
    out['lead'] = {'volume': round(ld.volume * 1000.0, 3), 'faces': ld.faces.count, 'planar_faces': ends, 'lumps': ld.lumps.count,
                   'world_box': [round(v, 2) for v in _bb(k, X, ld)]}
    if ends:
        ea = max(e['area'] for e in ends)
        out['lead']['length_from_volume'] = round(out['lead']['volume'] / ea, 1)
    for nm in ('MAIN_plug_env', 'MAIN_conn', 'MAIN_pcb'):
        r = X.mm.measureMinimumDistance(ld, X.body(nm))
        out['lead']['to_' + nm] = [round(r.value * 10.0, 3), [round(v, 2) for v in k.W(r.positionOne)], [round(v, 2) for v in k.W(r.positionTwo)]]
    r = X.mm.measureMinimumDistance(ld, b)
    out['lead']['to_radar'] = [round(r.value * 10.0, 3), [round(v, 2) for v in k.W(r.positionOne)], [round(v, 2) for v in k.W(r.positionTwo)]]
    L['jdump']('p10_env.json', out)
    print(json.dumps(out, indent=1))


def probe(tag, box, lim=3.0, skip=()):
    """Bodies of the unit within lim of the world box [x0, x1, y0, y1, z0, z1]."""
    k, X = _X()
    t0 = time.time()
    tb = X.wbox(*box)
    res = []
    for b in k.current(X, leads=True):
        if b.name in skip:
            continue
        q = _bb(k, X, b)
        gap = 0.0
        for i in range(3):
            e = max(q[2 * i] - box[2 * i + 1], box[2 * i] - q[2 * i + 1], 0.0)
            gap += e * e
        if math.sqrt(gap) > lim:
            continue
        if b.name in k.BIG:
            d = min(X.mm.measureMinimumDistance(tb, p).value * 10.0 for p in k.parts(X, b.name))
        else:
            d = X.mm.measureMinimumDistance(tb, b).value * 10.0
        if d > lim:
            continue
        sh = 0.0
        if d < 0.001:
            sh = k.xparts(X, X.wbox(*box), k.parts(X, b.name)) if b.name in k.BIG else X.xv(X.wbox(*box), k.tcopy(X, b.name))
        res.append((round(d, 2), round(sh, 1), b.name, [round(v, 1) for v in q]))
    res.sort(key=lambda r: (r[0], -r[1]))
    L['jdump']('p10_probe_%s.json' % tag, {'box': box, 'lim': lim, 'rows': res})
    print('probe %s box %s (%.1f s):' % (tag, box, time.time() - t0))
    for r in res:
        print('  %6.2f  shares %9.1f  %-26s  its box %s' % r)


def ray_dir(az, el):
    """az: degrees from straight ahead (+y), positive toward the viewer's right (-x); el: degrees above level."""
    a = math.radians(az); e = math.radians(el)
    return (-math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e))


def sweep(tag, c, rays, length=400.0, names=None):
    """rays: list of (label, az, el). For each ray, every body of the unit it crosses, with the distances from c (mm) at which
    it crosses that body's faces (Component.findBRepUsingRay, invisible bodies included; hidden backups and bodies outside the
    unit left out). The first figure of a body is where the ray enters it."""
    k, X = _X()
    t0 = time.time()
    unit = set(b.name for b in k.current(X, leads=True))
    if names is not None:
        unit &= set(names)
    out = []
    for lab, az, el in rays:
        u = ray_dir(az, el)
        hp = adsk.core.ObjectCollection.create()
        ents = X.root.findBRepUsingRay(k.Wp(*c), k.dv(u), adsk.fusion.BRepEntityTypes.BRepFaceEntityType, -1.0, False, hp)
        per = {}
        for i in range(ents.count):
            f = ents.item(i); nm = f.body.name
            if nm not in unit:
                continue
            w = k.W(hp.item(i))
            d = sum((w[j] - c[j]) * u[j] for j in range(3))
            if d < 0.0 or d > length:
                continue
            per.setdefault(nm, []).append(round(d, 2))
        hits = sorted(([min(v), nm, sorted(v)] for nm, v in per.items()), key=lambda r: r[0])
        out.append({'ray': lab, 'az': az, 'el': el, 'hits': hits})
        print('%-8s az %+6.1f el %+6.1f: %s' % (lab, az, el, ', '.join('%s@%.1f' % (h[1], h[0]) for h in hits) or 'nothing'))
        if time.time() - t0 > 62:
            print('time: stopped after', lab); break
    L['jdump']('p10_sweep_%s.json' % tag, {'c': c, 'length': length, 'rays': out})
    print('%.1f s' % (time.time() - t0))


def section(tag, names, axis, value, win):
    """Outlines of the named bodies cut by the world plane axis = value, clipped to win (u0, u1, v0, v1) loosely."""
    k, X = _X()
    t0 = time.time()
    o = {'x': (value, 0, 0), 'y': (0, value, 0), 'z': (0, 0, value)}[axis]
    n = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1)}[axis]
    pl = adsk.core.Plane.create(k.Wp(*o), k.dv(n))
    uv = (lambda w: (w[1], w[2])) if axis == 'x' else ((lambda w: (w[0], w[2])) if axis == 'y' else (lambda w: (w[0], w[1])))
    out = {}
    for nm in names:
        b = X.body(nm)
        if b is None:
            print('no body', nm); continue
        q = _bb(k, X, b); i = 'xyz'.index(axis)
        if not (q[2 * i] - 0.01 <= value <= q[2 * i + 1] + 0.01):
            continue                                  # the plane misses the body
        try:
            s = X.tbm.planeIntersection(X.tbm.copy(b), pl)
        except Exception as e:
            print(nm, 'no section:', str(e)[:60]); continue
        loops = []
        for w in s.wires:
            pts = []
            for ed in w.edges:
                ev = ed.evaluator
                if ev is None:
                    g = ed.geometry
                    ev = g.evaluator if g is not None else None
                if ev is None:
                    pts.append([[round(v, 2) for v in uv(k.W(ed.startVertex.geometry))], [round(v, 2) for v in uv(k.W(ed.endVertex.geometry))]])
                    continue
                ok, a, e = ev.getParameterExtents()
                ok, st = ev.getStrokes(a, e, 0.002)
                if (not ok) or len(st) < 2:
                    st = []
                    for i in range(41):
                        ok2, pp = ev.getPointAtParameter(a + (e - a) * i / 40.0)
                        if ok2:
                            st.append(pp)
                pts.append([[round(v, 2) for v in uv(k.W(p))] for p in st])
            loops.append(pts)
        out[nm] = loops
        if time.time() - t0 > 60:
            print('time: stopped after', nm); break
    L['jdump']('p10_sec_%s.json' % tag, {'axis': axis, 'value': value, 'win': win, 'bodies': out})
    print('section %s: %s at %g, %d bodies, %.1f s' % (tag, axis, value, len(out), time.time() - t0))


def _cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def pose(tag, c, n, ldir, w=16.0, l=22.0, t=3.0, lim=2.0, extra=()):
    """The radar's envelope placed with its outward face centred at c, facing n, its long side (l) along ldir: every body of
    the unit within lim of it, with the volume it shares. extra = (label, centre, axisL, axisW, L, W, T) boxes (a holder) checked too."""
    k, X = _X()
    t0 = time.time()
    nn = L_norm(n); ll = L_norm(ldir); ww = _cross(nn, ll)
    cen = tuple(c[i] - nn[i] * t / 2.0 for i in range(3))
    boxes = [('radar', cen, ll, ww, l, w, t)] + list(extra)
    res = {}
    for lab, cc, a1, a2, s1, s2, s3 in boxes:
        ob = adsk.core.OrientedBoundingBox3D.create(k.Wp(*cc), k.dv(L_norm(a1)), k.dv(L_norm(a2)), s1 / 10.0, s2 / 10.0, s3 / 10.0)
        tb = X.tbm.createBox(ob)
        rows = []
        for b in k.current(X, leads=True):
            if b.name == 'LD2410C_env_F' and tag != 'today':
                continue
            bx = _bb(k, X, b)
            far = False
            for i in range(3):
                lo = cc[i] - 0.5 * (abs(a1[i]) * s1 + abs(a2[i]) * s2 + abs(_cross(L_norm(a1), L_norm(a2))[i]) * s3) - lim
                hi = cc[i] + 0.5 * (abs(a1[i]) * s1 + abs(a2[i]) * s2 + abs(_cross(L_norm(a1), L_norm(a2))[i]) * s3) + lim
                if bx[2 * i] > hi or bx[2 * i + 1] < lo:
                    far = True
            if far:
                continue
            plist = k.parts(X, b.name) if b.name in k.BIG else [b]
            d = min(X.mm.measureMinimumDistance(tb, p).value * 10.0 for p in plist)
            if d > lim:
                continue
            sh = 0.0
            if d < 0.001:
                sh = sum(X.xv(X.tbm.copy(tb), p if b.name in k.BIG else k.tcopy(X, b.name)) for p in (plist if b.name in k.BIG else [None]))
            rows.append((round(d, 2), round(sh, 2), b.name))
        rows.sort()
        res[lab] = rows
        print('%s / %s:' % (tag, lab), '; '.join('%s %.2f%s' % (r[2], r[0], (' shares %.2f' % r[1]) if r[1] else '') for r in rows) or 'nothing within %.1f' % lim)
    L['jdump']('p10_pose_%s.json' % tag, {'c': c, 'n': n, 'ldir': ldir, 'res': res})
    print('%.1f s' % (time.time() - t0))


def L_norm(a):
    s = math.sqrt(sum(v * v for v in a)); return tuple(v / s for v in a)


METAL = ['LCD_panel_body', 'LCD_glass', 'LCD_pcb_76x110', 'LCD_components_env_d8.8', 'SPK_L', 'SPK_R', 'DRV_screw_heads_env', 'PI5_F',
         'PI5_F_cooler', 'USBA_plug_env', 'MAIN_pcb', 'MAIN_PS1', 'MAIN_conn', 'RESP_pcb', 'TOUCH_PCB', 'TOUCH_components_env',
         'SCREWS_M2x6_env', 'BME680_env', 'VEML_env', 'MIC_strip_L_env', 'MIC_strip_R_env', 'PD_5807_env']


def metal(tag, c, n, ldir, w=16.0, l=22.0, t=3.0):
    """Distances from the radar's envelope (placed as in pose(); tag 'today' = the model's own envelope) to the metal and the
    boards of the unit, and to the twenty magnet pockets (cylindrical faces of radius 4.15 in the shell and the door)."""
    k, X = _X()
    t0 = time.time()
    if tag == 'today':
        tb = X.tbm.copy(X.body('LD2410C_env_F'))
    else:
        nn = L_norm(n); ll = L_norm(ldir); ww = _cross(nn, ll)
        cen = tuple(c[i] - nn[i] * t / 2.0 for i in range(3))
        tb = X.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(k.Wp(*cen), k.dv(ll), k.dv(ww), l / 10.0, w / 10.0, t / 10.0))
    rows = []
    for nm in METAL:
        b = X.body(nm)
        r = X.mm.measureMinimumDistance(tb, b)
        rows.append((round(r.value * 10.0, 1), nm, [round(v, 1) for v in k.W(r.positionTwo)]))
    mags = []
    for host in ('HOUSING_F_front', 'HOUSING_F_door'):
        for f in X.body(host).faces:
            g = f.geometry
            if g.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType and abs(g.radius * 10.0 - 4.15) < 0.02:
                r = X.mm.measureMinimumDistance(tb, f)
                mags.append((round(r.value * 10.0, 1), host, [round(v, 1) for v in k.W(r.positionTwo)]))
    rows.sort(); mags.sort()
    L['jdump']('p10_metal_%s.json' % tag, {'rows': rows, 'magnet_pockets': mags})
    print('%s: ' % tag + '; '.join('%s %.1f' % (r[1], r[0]) for r in rows[:9]))
    print('   magnet pockets (%d): nearest %s' % (len(mags), '; '.join('%.1f %s at %s' % (m[0], m[1], m[2]) for m in mags[:3])))
    print('   %.1f s' % (time.time() - t0))
