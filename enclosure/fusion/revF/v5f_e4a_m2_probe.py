# rev F e4a (2026-11-08): read-only probe of the four M2 holes before they become pilots for M2 x 6 screws for plastic
#   (Daniel 2026-11-08: no inserts for the ReSpeaker and the 5807). Per body: cylinder faces (radius, axis, axial extent,
#   hole or boss), the material along each hole axis (solid / void at r 0 and r 0.8 in four directions, 0.1 mm steps,
#   transitions bisected to 0.001) and the other bodies on the axis within 12 mm beyond the hole bottom.
#   Writes ~/Documents/HA_panel_renders/m2_e4/e4a_status.json.
import os, traceback
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
OUT_DIR = os.path.expanduser('~/Documents/HA_panel_renders/m2_e4')
GUARD = {'RESP_CARRIER': 10.0716, 'CRADLE_5807': 2.1775}
SKIP = ('TOOL_', 'REF_', 'INNER_', 'RENDER_', 'sk_', 'HOUSING_E', 'V11')


def w(p):                                   # design Point3D (cm) -> world [x_rel, y, z] mm
    return [round(p.x * 10 - XC, 3), round(wy(p), 3), round(wz(p), 3)]


def wv(v):                                  # design vector -> world vector
    return [round(v.x, 5), round(v.y * C - v.z * S, 5), round(v.y * S + v.z * C, 5)]


def at(o, a, t):                            # o + t a (t in mm) as a design Point3D
    return P3(o.x + a.x * t / 10, o.y + a.y * t / 10, o.z + a.z * t / 10)


def perp(a):
    r = V3(1, 0, 0) if abs(a.x) < 0.9 else V3(0, 1, 0)
    u = a.crossProduct(r); u.normalize(); v = a.crossProduct(u); v.normalize()
    return u, v


def cyl_faces(body):
    res = []
    for f in body.faces:
        g = f.geometry
        if g.objectType != adsk.core.Cylinder.classType():
            continue
        cy = adsk.core.Cylinder.cast(g)
        if not (0.05 <= cy.radius <= 0.5):
            continue
        a = cy.axis.copy(); a.normalize(); o = cy.origin
        ts = []
        for e in f.edges:
            for vx in (e.startVertex, e.endVertex):
                q = vx.geometry
                ts.append(((q.x - o.x) * a.x + (q.y - o.y) * a.y + (q.z - o.z) * a.z) * 10)
        p = f.pointOnFace
        ok, n = f.evaluator.getNormalAtPoint(p)
        d = V3(p.x - o.x, p.y - o.y, p.z - o.z); t = d.dotProduct(a)
        rad = V3(d.x - a.x * t, d.y - a.y * t, d.z - a.z * t)
        kind = 'boss' if n.dotProduct(rad) > 0 else 'hole'
        res.append({'f': f, 'r': cy.radius * 10, 'a': a, 'o': o, 't0': min(ts), 't1': max(ts), 'kind': kind,
                    'area': f.area * 100})
    return res


def profile(body, o, a, t_from, t_to, offs, step=0.1):
    """solid/void along lines parallel to a, offset by offs (design vectors in mm); returns transitions per line."""
    out = []
    n = int(round((t_from - t_to) / step))
    for off in offs:
        base = P3(o.x + off.x / 10, o.y + off.y / 10, o.z + off.z / 10)
        inside = lambda t: body.pointContainment(at(base, a, t)) in INS
        prev = inside(t_from); tr = []
        for i in range(1, n + 1):
            t = t_from - i * step; cur = inside(t)
            if cur != prev:
                lo, hi = t, t + step              # transition between t (cur) and t + step (prev)
                for _ in range(10):
                    mid = (lo + hi) / 2
                    if inside(mid) == cur:
                        lo = mid
                    else:
                        hi = mid
                tr.append([round((lo + hi) / 2, 3), 'solid' if cur else 'void'])
            prev = cur
        out.append({'start': 'solid' if inside(t_from) else 'void', 'transitions': tr})
    return out


def run(_context):
    st = {'t0': time.strftime('%H:%M:%S')}
    t00 = time.time()
    try:
        os.makedirs(OUT_DIR, exist_ok=True)
        X = Ctx()
        st['version'] = [X.doc.dataFile.versionNumber, X.doc.dataFile.latestVersionNumber, X.doc.isModified]
        bad = [[k, None if X.body(k) is None else round(X.body(k).volume, 4)] for k, v in GUARD.items()
               if X.body(k) is None or abs(X.body(k).volume - v) > 0.0005]
        st['guard_bad'] = bad
        if bad:
            raise RuntimeError('GUARD %s' % bad)
        st['e4_names'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_e4') or b.name.startswith('TOOL_e4')]
        others = [b for b in X.comp.bRepBodies if b.name not in GUARD and not b.name.startswith(SKIP)]
        for name in GUARD:
            body = X.body(name)
            info = {'vol': round(body.volume, 4), 'faces': body.faces.count, 'lumps': body.lumps.count,
                    'visible': body.isLightBulbOn}
            cf = cyl_faces(body)
            info['cyl'] = [{'r': round(c['r'], 4), 'kind': c['kind'], 'axis_w': wv(c['a']),
                            'end0_w': w(at(c['o'], c['a'], c['t0'])), 'end1_w': w(at(c['o'], c['a'], c['t1'])),
                            'len': round(c['t1'] - c['t0'], 3), 'area': round(c['area'], 3)} for c in cf]
            holes = [c for c in cf if c['kind'] == 'hole' and abs(c['r'] - 1.6) < 0.01]
            hl = []
            for c in holes:
                a = c['a']; o = c['o']
                # open end: air just beyond it on the axis
                beyond1 = body.pointContainment(at(o, a, c['t1'] + 0.05)) in INS
                if beyond1:                       # t1 end is closed -> flip so +a points out of the hole
                    a = V3(-a.x, -a.y, -a.z); t_top, t_bot = -c['t0'], -c['t1']
                else:
                    t_top, t_bot = c['t1'], c['t0']
                u, v = perp(a)
                offs = [V3(0, 0, 0)] + [V3(q.x * 0.8, q.y * 0.8, q.z * 0.8) for q in (u, v)] + \
                       [V3(-q.x * 0.8, -q.y * 0.8, -q.z * 0.8) for q in (u, v)]
                prof = profile(body, o, a, t_top + 2.0, t_bot - 12.0, offs)
                axis_hits = {}
                seg0 = at(o, a, t_bot); seg1 = at(o, a, t_bot - 12.0)
                for ob in others:
                    bb = ob.boundingBox
                    lo = [min(seg0.x, seg1.x) - 0.11, min(seg0.y, seg1.y) - 0.11, min(seg0.z, seg1.z) - 0.11]
                    hi = [max(seg0.x, seg1.x) + 0.11, max(seg0.y, seg1.y) + 0.11, max(seg0.z, seg1.z) + 0.11]
                    if bb.maxPoint.x < lo[0] or bb.minPoint.x > hi[0] or bb.maxPoint.y < lo[1] or bb.minPoint.y > hi[1] \
                            or bb.maxPoint.z < lo[2] or bb.minPoint.z > hi[2]:
                        continue
                    first = None
                    for i in range(0, 121):
                        tt = t_bot - i * 0.1
                        if any(ob.pointContainment(at(P3(o.x + off.x / 10, o.y + off.y / 10, o.z + off.z / 10), a, tt))
                               in INS for off in offs):
                            first = round(t_bot - tt, 2); break
                    if first is not None:
                        axis_hits[ob.name] = first
                hl.append({'top_w': w(at(o, a, t_top)), 'bottom_w': w(at(o, a, t_bot)), 'axis_out_w': wv(a),
                           'depth': round(t_top - t_bot, 3), 't_top': round(t_top, 4), 't_bot': round(t_bot, 4),
                           'profile_lines': 'r0, +u, +v, -u, -v at 0.8', 'profile': prof,
                           'others_on_axis_within_12_below_bottom': axis_hits})
            info['holes'] = hl
            st[name] = info
        st['t_s'] = round(time.time() - t00, 1)
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    json.dump(st, open(os.path.join(OUT_DIR, 'e4a_status.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in st.items() if k not in GUARD}))


run(None)
