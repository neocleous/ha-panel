# Block 1a: every screw into a printed part, read on the model. READ-ONLY: temporary bodies only.
#   holes   every round hole of radius 0.7 to 2.1 in each of the 17 printed parts: axis, its two ends (world), which end is
#           closed (a point 0.05 beyond the end, on the axis and at 0.75 of the radius, inside the part), length, the closed
#           end's height in the part's print and how it lands on the layer grid (mid-layer rule), its face's way in the print
#   stack   for named holes: what stands outside the mouth along the axis (needles parallel to the axis at an offset, four sides,
#           through every body of the unit but leads, keep-outs and the screws' own envelopes): the stretches of each body, in mm
#           from the mouth outward; and the plastic behind the closed end, on the axis, in the part itself
#   m2      each lump of SCREWS_M2x6_env: its extent along the axis of the coaxial pilot (radius 0.8) of a printed part, from the
#           pilot's mouth; the pilot's length and closed end
# The print orientations are the record's (../model-v70/p95_close_checks.py grid17; the boxes' bed y + 52 as the brief has it).
# Run: L.checked('m10_screws.py', sha)['main'](stage, tag, **kw)  -> m10_<stage>_<tag>.txt
import runpy, math, time
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/box_margins_v85/'
L = runpy.run_path(D + 'm00_lib.py')
HN = (0.11394, 0.09756, 0.98869); HP0 = (-69.8829, -39.0603, 110.0342)
# name: (how it prints, height of a world point p / slab point q, the print's up direction ('S' = slab frame +d), layer)
PRINT = {'HOUSING_F_front': ('chin down', lambda p, q: 6.7992 - p[1], (0.0, -1.0, 0.0), 0.2),
         'HOUSING_F_plate': ('back down', lambda p, q: 12.8 - q[1], 'S-', 0.2),
         'SLAB_frame': ('glass side down', lambda p, q: q[1], 'S+', 0.1),
         'RESP_CARRIER': ('plate down', lambda p, q: q[1] - 15.2, 'S+', 0.2),
         'HOUSING_F_door': ('standing', lambda p, q: p[2] - 2.8, (0.0, 0.0, 1.0), 0.2),
         'HOUSING_F_cap': ('top face down', lambda p, q: 180.0 - p[2], (0.0, 0.0, -1.0), 0.1),
         'FLOOR_PLATE': ('underside down', lambda p, q: p[2], (0.0, 0.0, 1.0), 0.2),
         'SPKBOX_L': ('rear face down', lambda p, q: p[1] + 52.0, (0.0, 1.0, 0.0), 0.2),
         'SPKBOX_R': ('rear face down', lambda p, q: p[1] + 52.0, (0.0, 1.0, 0.0), 0.2),
         'CRADLE_5807': ('rear face down', lambda p, q: p[1] + 84.6, (0.0, 1.0, 0.0), 0.2),
         'TOUCH_CLIP_L': ('as fitted', lambda p, q: p[2] - 30.0, (0.0, 0.0, 1.0), 0.2),
         'TOUCH_CLIP_R': ('turned top for bottom', lambda p, q: 46.0 - p[2], (0.0, 0.0, -1.0), 0.2),
         'GROMMET_usbc_F': ('on its side', lambda p, q: p[2] - 10.0, (0.0, 0.0, 1.0), 0.12),
         'BME_HOOD': ('top plate down', lambda p, q: sum((HP0[i] - p[i]) * HN[i] for i in range(3)), tuple(-w for w in HN), 0.2),
         'MIC_CLAMP_L': ('as fitted', lambda p, q: p[2] - 172.7, (0.0, 0.0, 1.0), 0.2),
         'MIC_CLAMP_R': ('as fitted', lambda p, q: p[2] - 172.7, (0.0, 0.0, 1.0), 0.2),
         'RADAR_HOLDER': ('upright', lambda p, q: p[2] - 27.6, (0.0, 0.0, 1.0), 0.2)}
PIN = (adsk.fusion.PointContainment.PointInsidePointContainment, adsk.fusion.PointContainment.PointOnPointContainment)
SKIP = ('DRV_screw_heads_env', 'SCREWS_M2x6_env')


def up_dir(k, name):
    u = PRINT[name][2]
    if isinstance(u, str):                                    # the slab frame's d axis is design -y; world direction of design (0, -1, 0)
        w = k.wv(adsk.core.Vector3D.create(0, -1, 0))
        return tuple(w) if u == 'S+' else tuple(-v for v in w)
    return k.unit(u)


def height(k, name, p):
    return PRINT[name][1](p, k.Sf(k.Wp(*p)))


def land(h, lh, looks):
    """Where a level face at print height h lands by the mid-layer rule: looks 'up' (solid below) or 'down' (solid above)."""
    if looks == 'up':
        n = math.floor((h - lh / 2.0) / lh + 1e-9) + 1
        g = n * lh; tie = abs((h - lh / 2.0) / lh - round((h - lh / 2.0) / lh)) < 1e-4
    else:
        n = math.ceil((h - lh / 2.0) / lh - 1e-9)
        g = n * lh; tie = abs((h - lh / 2.0) / lh - round((h - lh / 2.0) / lh)) < 1e-4
    return round(g, 3), tie


def perp(a):
    r = (0.0, 0.0, 1.0) if abs(a[2]) < 0.9 else (1.0, 0.0, 0.0)
    u = (a[1] * r[2] - a[2] * r[1], a[2] * r[0] - a[0] * r[2], a[0] * r[1] - a[1] * r[0])
    n = math.sqrt(sum(q * q for q in u)); u = tuple(w / n for w in u)
    v = (a[1] * u[2] - a[2] * u[1], a[2] * u[0] - a[0] * u[2], a[0] * u[1] - a[1] * u[0])
    return u, v


def ends(k, b, h):
    """For a hole row of holes_of: which ends are closed. Returns [(end point, outward axis, closed?, at axis, at 0.75 r)]."""
    a = h['a']; A = h['A']; B = h['B']; r = h['r']; u, v = perp(a)
    out = []
    for P, s in ((A, -1.0), (B, 1.0)):
        o = tuple(s * w for w in a)
        p0 = tuple(P[i] + o[i] * 0.05 for i in range(3))
        c0 = b.pointContainment(k.Wp(*p0)) in PIN
        c1 = sum(1 for w in (u, v, tuple(-q for q in u), tuple(-q for q in v)) if b.pointContainment(k.Wp(*[p0[i] + w[i] * 0.75 * r for i in range(3)])) in PIN)
        out.append((P, o, c0, c1))
    return out


def st_holes(k, X, only=None, rmin=0.7, rmax=2.1):
    for name in L['PRINTED']:
        if only and name not in only:
            continue
        b = X.body(name); how, hf, upd, lh = PRINT[name]; up = up_dir(k, name)
        rows = sorted(k.holes_of(b, rmin, rmax), key=lambda h: (h['r'], h['A']))
        rows = [h for h in rows if h['k'] == 'h']
        print('%s (prints %s, layers %.2f): %d round holes of radius %.1f to %.1f' % (name, how, lh, len(rows), rmin, rmax))
        for h in rows:
            e = ends(k, b, h)
            tags = []
            for P, o, c0, c1 in e:
                ht = height(k, name, P)
                dd = sum(o[i] * up[i] for i in range(3))          # the outward axis beyond this end, along the print's up
                if c0 or c1:
                    # closed end: its face looks back into the hole, i.e. along -o
                    if abs(dd) < 0.02:
                        looks = 'upright'; g = None
                    else:
                        looks = 'down' if dd > 0 else 'up'      # face normal -o: up if -o has +up
                        g = land(ht, lh, looks)
                    tags.append('closed (axis %s, ring %d/4) at %s, height %.3f, face looks %s%s' % (c0, c1, k.r2(P, 2), ht, looks, '' if g is None else ', lands %.2f%s' % (g[0], ' (tie)' if g[1] else '')))
                else:
                    tags.append('open at %s, height %.3f' % (k.r2(P, 2), ht))
            print('   r %.3f  axis %s  L %.2f  cov %.2f | %s | %s' % (h['r'], h['a'], h['L'], h['cov'], tags[0], tags[1]))
        if k.late():
            print('time'); break


def bodies(k, X):
    q = k.c.get('m10_bodies')
    if q is None:
        q = [(b.name, k.wbb(X, b)) for b in k.current(X, leads=False, kos=False) if b.name not in SKIP]
        k.c['m10_bodies'] = q
    return q


def st_stack(k, X, holes, off=2.3, reach=14.0, behind=10.0, sec=70):
    """holes: [(part, mouth (x, y, z), outward axis (unit), closed end (x, y, z) or None)]."""
    k.budget(sec)
    bl = bodies(k, X)
    for part, M, o, F in holes:
        o = k.unit(o); u, v = perp(o)
        E = tuple(M[i] + o[i] * reach for i in range(3))
        lo = [min(M[i], E[i]) - off - 0.5 for i in range(3)]; hi = [max(M[i], E[i]) + off + 0.5 for i in range(3)]
        near = [n for n, bb in bl if bb[0] <= hi[0] and bb[1] >= lo[0] and bb[2] <= hi[1] and bb[3] >= lo[1] and bb[4] <= hi[2] and bb[5] >= lo[2]]
        print('%s, mouth %s, outward %s: bodies near the axis %s' % (part, k.r2(M, 2), k.r2(o, 3), near))
        for n in near:
            pl = k.parts(X, n); seg = []
            for w in (u, v, tuple(-q for q in u), tuple(-q for q in v)):
                p0 = tuple(M[i] - o[i] * 1.0 + w[i] * off for i in range(3)); p1 = tuple(E[i] + w[i] * off for i in range(3))
                seg.append([(round(a - 1.0, 2), round(b - 1.0, 2)) for a, b in k.needle_t(X, pl, p0, p1, 0.02)])
            if any(seg):
                print('   %-22s at %.1f off the axis, four sides: %s' % (n, off, seg))
            if k.late():
                print('   time'); return
        if F is not None:
            pl = k.parts(X, part)
            st = k.needle_t(X, pl, F, tuple(F[i] + o[i] * -behind for i in range(3)), 0.02)
            print('   behind the closed end, on the axis, in %s: %s (from the end, %.1f long needle)' % (part, st, behind))


def lv(l):
    try:
        return l.volume * 1000.0
    except Exception:
        return -1.0


def st_m2(k, X):
    S = X.body('SCREWS_M2x6_env')
    piles = []
    for name in L['PRINTED']:
        b = X.body(name)
        for h in k.holes_of(b, 0.75, 0.85):
            if h['k'] == 'h':
                piles.append((name, h, ends(k, b, h)))
    print('pilots of radius 0.75 to 0.85: %d' % len(piles))
    for i, l in enumerate(S.lumps):
        ws = [k.W(vx.geometry) for vx in l.vertices]
        cen = tuple(sum(w[j] for w in ws) / len(ws) for j in range(3))
        best = None
        for name, h, e in piles:
            a = h['a']; A = h['A']
            d = [cen[j] - A[j] for j in range(3)]; t0 = sum(d[j] * a[j] for j in range(3))
            off = math.sqrt(max(sum(q * q for q in d) - t0 * t0, 0.0))
            if best is None or off < best[0]:
                best = (off, name, h, e)
        off, name, h, e = best
        a = h['a']
        ts = [sum((w[j] - h['A'][j]) * a[j] for j in range(3)) for w in ws]
        print('lump %d, %.3f mm3, centre %s: nearest pilot axis %.2f away, in %s, r %.3f, from %s to %s (L %.2f)' % (i, lv(l), k.r2(cen, 2), off, name, h['r'], h['A'], h['B'], h['L']))
        for P, o, c0, c1 in e:
            print('      end %s: %s' % (k.r2(P, 2), 'closed' if (c0 or c1) else 'open'))
        print('      the lump along that axis (from end A): %.2f to %.2f' % (min(ts), max(ts)))


def _main(stage, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'holes': st_holes, 'stack': st_stack, 'm2': st_m2}[stage](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(stage, tag='', **kw):
    L['out']('m10_%s%s.txt' % (stage, ('_' + tag) if tag else ''), _main, stage, **kw)
# END
