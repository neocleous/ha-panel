# Checks on the bodies that v69_fixes.py makes: before they go into the document (on the temporary
# bodies) and after (on the model). Nothing in this file changes the document.
#
# Loaded into Fusion's Python as the module "v69c", after "v69". It uses the unit checks of the earlier
# audits, loaded as the namespace c3k.K4NS (v5f_k4a_unit_checks.py at 45a38e4), for the ride-in's
# pieces and for the interference table.
# Lengths in mm, volumes in mm3. Every function stops when the time set with c3k.budget() is used up
# and can be called again: results are kept in c3k.c['v69_checks'].
import sys, math
import adsk.core, adsk.fusion

f = sys.modules['v69']; v = f.v; k = f.k; sh = f.sh; G = f.G
R = k.c.setdefault('v69_checks', {})
UP = (0.0, 0.0, 1.0)
PRINTED = ['HOUSING_F_plate', 'HOUSING_F_front', 'SPKBOX_L', 'SPKBOX_R', 'FLOOR_PLATE', 'RESP_CARRIER', 'CRADLE_5807', 'HOUSING_F_door',
           'HOUSING_F_cap', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'SLAB_frame', 'GROMMET_usbc_F', 'BME_HOOD', 'MIC_CLAMP_L', 'MIC_CLAMP_R']


def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def comb(p, *terms): return tuple(p[i] + sum(s * d[i] for s, d in terms) for i in range(3))


def wext(tb, pad=0.0):
    """World box of a body from its corners: [x0, x1, y0, y1, z0, z1]."""
    ws = [k.W(q.geometry) for q in tb.vertices]
    return [f2(w[i] for w in ws) + sg * pad for i in range(3) for f2, sg in ((min, -1.0), (max, 1.0))]


# ---------- the unit's bodies as temporary pieces, without reading a big body's volume ----------
def pieces(X, name):
    """A current body as temporary pieces: the new body if the part changes here, a big body as its slabs."""
    if name in G:
        return [G[name]]
    idx = R.get('idx')
    if idx is None:
        idx = {'tc': {}, 'tile': {}}
        for q, b in k.hc().items():
            if isinstance(q, tuple) and q[0] == 'tc':
                idx['tc'][q[1]] = b
            elif isinstance(q, tuple) and q[0] == 'tile':
                idx['tile'].setdefault(q[1], []).append(b)
        R['idx'] = idx
    if name in idx['tile']:
        return [t for t in idx['tile'][name] if t.faces.count > 0]
    if name not in idx['tc']:
        idx['tc'][name] = X.tbm.copy(X.body(name))
    return [idx['tc'][name]]


def near(X, tb, lim=1.5, skip=()):
    """The unit's bodies within lim of a small temporary body: the distance, or the shared volume where they meet."""
    q = tb.boundingBox; e = lim / 10.0
    bb = adsk.core.BoundingBox3D.create(k.P3(q.minPoint.x - e, q.minPoint.y - e, q.minPoint.z - e),
                                        k.P3(q.maxPoint.x + e, q.maxPoint.y + e, q.maxPoint.z + e))
    rows = []
    for b in k.current(X, leads=True):
        n = b.name
        if n in skip:
            continue
        best = None; shared = 0.0
        for p in pieces(X, n):
            if p is tb or not bb.intersects(p.boundingBox):
                continue
            if k.late():
                rows.append((99.0, n + ': not checked, out of time')); break
            d = X.mm.measureMinimumDistance(tb, p).value * 10.0
            if d < 0.0005:
                shared += X.xv(tb, p); best = 0.0
            elif best is None or d < best:
                best = d
        if best is None:
            continue
        if best == 0.0:
            rows.append((0.0, '%s shares %.3f' % (n, shared)))
        elif best < lim:
            rows.append((round(best, 2), n))
    return sorted(rows)


def crop(X, name, box):
    """The pieces of a current body inside a world box."""
    out = []
    bx = X.wbox(*box)
    for p in pieces(X, name):
        if not bx.boundingBox.intersects(p.boundingBox):
            continue
        t = X.tbm.copy(bx)
        X.sec(t, p)
        if t.faces.count > 0:
            out.append(t)
    return out


# ---------- the new material, as small bodies ----------
def boss(X, outside_wall=True):
    """The hood's boss with its pilot; with outside_wall only what stands beside or beyond the end wall's end and face."""
    a, c = f.boss_tools(X)
    X.dif(a, c)
    if outside_wall:
        X.sec(a, sh.hood_slab(X, 0.39 - f.TRIM, 12.0, -100.0, -80.0, 70.0, 110.0))
    return a


def hood_screw(X):
    vc = sys.modules['v68_commit']
    name, h, d = [r for r in f.screw_list() if r[0] == 'hood'][0]
    return vc.screw(X, h, d)


def added(X):
    if 'added' not in R:
        R['added'] = {'boss': boss(X, False), 'radar block tops': f.block_tops(X), 'hood': G['BME_HOOD'],
                      'hood screw': hood_screw(X), 'supply module pins': G['MAIN_PS1_pins']}
    return R['added']


def fit(X, lim=1.5):
    """What lies within lim of each piece of new material. The shell is left out for the pieces that become part of it."""
    out = R.setdefault('fit', {})
    skip = {'boss': ('HOUSING_F_front',), 'radar block tops': ('HOUSING_F_front',), 'hood': (), 'hood screw': ('SCREWS_M2x6_env',),
            'supply module pins': ('MAIN_PS1',)}
    for n, tb in added(X).items():
        if n in out or k.late():
            continue
        out[n] = near(X, tb, lim, skip[n])
    return out


def facts(X):
    """Volume and lumps of each new body; for the small ones also what they add to and take from the model's body."""
    out = {}
    for n in f.CHANGED:
        new = G[n]
        row = {'lumps': new.lumps.count, 'faces': new.faces.count}
        if n != 'HOUSING_F_front':
            o = X.tbm.copy(X.body(n))
            a = X.tbm.copy(new); X.dif(a, o)
            r = X.tbm.copy(o); X.dif(r, new)
            row.update(new=round(X.vol(new), 3), old=round(X.vol(o), 3),
                       added=round(X.vol(a), 3) if a.faces.count else 0.0, removed=round(X.vol(r), 3) if r.faces.count else 0.0)
        out[n] = row
    return out


def old_shell(X, box):
    """Version 68's shell inside a world box: from its backup once that exists, else from the model's own shell."""
    b = X.body('HOUSING_F_front' + f.BACKUP)
    if b is not None:
        return [X.sec(X.wbox(*box), X.tbm.copy(b))]
    keep = G.pop('HOUSING_F_front')
    try:
        return crop(X, 'HOUSING_F_front', box)
    finally:
        G['HOUSING_F_front'] = keep


def shell_diff(X):
    """What the new shell gains and loses against version 68's, inside boxes round the two places that change."""
    out = {}
    ra, rc = sh.radar_tools(X)
    for name, box in (('hood boss', wext(boss(X, False), 3.0)), ('radar', wext(X.uni(ra, rc), 2.0))):
        new = crop(X, 'HOUSING_F_front', box)[0]
        old = old_shell(X, box)
        gain = X.tbm.copy(new)
        for p in old:
            X.dif(gain, p)
        loss = 0.0; lb = []
        for p in old:
            t = X.tbm.copy(p); X.dif(t, new)
            if t.faces.count:
                loss += X.vol(t); lb += k.K.lumps(X, t)
        out[name] = {'box': [round(q, 1) for q in box], 'gain': round(X.vol(gain), 3) if gain.faces.count else 0.0,
                     'gain lumps': k.K.lumps(X, gain) if gain.faces.count else [], 'loss': round(loss, 3), 'loss lumps': lb}
    return out


def outside(X):
    """mm3 of each new body outside the cloth reference (the shell: its two known lumps, D217)."""
    c3 = sys.modules['c3']
    out = R.setdefault('outside', {})
    for n in f.CHANGED:
        if n in out or k.late():
            continue
        t = X.tbm.copy(G[n]); X.dif(t, X.tbm.copy(c3.skin(X)))
        out[n] = (round(X.vol(t), 3), [round(l.volume * 1000.0, 3) for l in t.lumps]) if t.faces.count else (0.0, [])
    return out


# ---------- walls round the three pilots in the shell ----------
def wall_rows(X, plist, stations, dirs, r=0.8, far=6.0):
    """Per station (distance from the head's top face, point on the axis): the thinnest wall and the direction it lies in."""
    rows = []
    for s, p in stations:
        best = None
        for i, d in enumerate(dirs):
            p0 = comb(p, (r - 0.01, d)); p1 = comb(p0, (far, d))
            st = k.needle_t(X, plist, p0, p1)
            w = round(st[0][1] - 0.01, 2) if st and st[0][0] <= 0.06 else 0.0
            if best is None or w < best[0]:
                best = (w, i * 30)
        rows.append((s, best[0], best[1]))
    return rows


def ring(a, b):
    return [comb((0.0, 0.0, 0.0), (math.cos(math.radians(30.0 * i)), a), (math.sin(math.radians(30.0 * i)), b)) for i in range(12)]


def walls(X):
    """Hood: directions from HT (0 degrees, toward the hood's side plate) round to up (90). Radar: from EW (toward the screen) round."""
    out = R.setdefault('walls', {})
    if 'hood' not in out and not k.late():
        box = wext(boss(X, False), 7.0)
        pl = crop(X, 'HOUSING_F_front', box)
        top = f.LB + sh.H_GAP + sh.H_EAR
        st = [(s, f.hp(top - s)) for s in (2.25, 2.75, 3.25, 3.75, 4.25, 4.75, 5.25, 5.75, 6.25)]
        out['hood'] = wall_rows(X, pl, st, ring(sh.HT, UP))
    for sg, name in ((1.0, 'radar, screen side'), (-1.0, 'radar, door side')):
        if name in out or k.late():
            continue
        a = sh.raxis(sg, 0.0); b = sh.raxis(sg, 1.0)
        ax = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
        box = wext(X.cyl(sh.raxis(sg, 1.0), sh.raxis(sg, 7.0), 1.0), 7.0)
        pl = crop(X, 'HOUSING_F_front', box)
        st = [(s, sh.raxis(sg, s)) for s in (2.75, 3.25, 3.75, 4.25, 4.75, 5.25, 5.75, 6.25, 6.7)]
        out[name] = wall_rows(X, pl, st, ring(sh.EW, cross(ax, sh.EW)))
    return out


# ---------- the hood: seated, lifted off its pegs, and moved away ----------
def hood_way(X):
    out = R.setdefault('hood_way', {})
    hood = G['BME_HOOD']
    if 'crop' not in R:
        R['crop'] = crop(X, 'HOUSING_F_front', wext(hood, 10.0))
    sc = R['crop']
    bs = boss(X)
    hd, u = f.hood_head()
    if 'seated' not in out:
        m = comb(hd, (-0.5 * sh.H_EAR, u))
        ear = X.sec(X.obox((m[0], m[1], 100.225), sh.HT, UP, 6.2, 6.6, sh.H_EAR + 0.02), hood)
        web = X.sec(sh.hood_slab(X, 0.0, 2.2 + f.ALONG, sh.SIDE[0] - 0.3, sh.SIDE[1] + 0.3, 91.13, 95.78), hood)
        end = X.sec(sh.hood_slab(X, -4.0, 0.01 - f.TRIM, sh.SIDE[0] - 0.3, sh.SIDE[1] + 0.3, 79.0, 91.13), hood)
        out['seated'] = {'hood in shell': round(sum(X.xv(hood, p) for p in sc), 3),
                         'ear to boss': round(X.mm.measureMinimumDistance(ear, bs).value * 10.0, 2),
                         'plate over the boss to boss': round(X.mm.measureMinimumDistance(web, bs).value * 10.0, 2),
                         "plate's new end to boss": round(X.mm.measureMinimumDistance(end, bs).value * 10.0, 2)}
    moves = [('lift %.1f' % a, comb((0.0, 0.0, 0.0), (a, sh.HA))) for a in (1.0, 2.0, 3.0, 3.5)]
    for name, d in (('toward the middle', (1.0, 0.0, 0.0)), ('square to the side plate', sh.HN), ('straight toward the door', sh.LW)):
        for s in (0.3, 0.6, 1.0, 1.5, 2.0, 3.0, 5.0, 8.0):
            moves.append(('lift 3.5, %s %.1f' % (name, s), comb((0.0, 0.0, 0.0), (3.5, sh.HA), (s, d))))
    for name, d in moves:
        if name in out or k.late():
            continue
        t = X.move(X.tbm.copy(hood), d[0], d[1], d[2])
        out[name] = (round(sum(X.xv(t, p) for p in sc), 3), round(X.mm.measureMinimumDistance(t, bs).value * 10.0, 2))
    return out


def hood_out(X, across=(0.5, 1, 2, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60), back=(5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60),
             at=(48.0, 56.0, 60.0), lift=3.5):
    """Step 18 backwards with the display module out: the hood lifted off its pegs, moved toward the middle,
    then drawn back out through the door opening. Per position: mm3 shared with anything, and the nearest body."""
    out = R.setdefault('hood_out', {})
    hood = G['BME_HOOD']
    N = k.K4NS; vc = sys.modules['v68_commit']
    gone = set(N['names_of'](X, 'MODULE')) | {'HOUSING_F_door', 'GROMMET_usbc_F', 'BME_HOOD', 'SCREWS_M2x6_env'}
    gone |= set(k.ST['PLUGS_MB'])                           # the main board's plugs come out with the module's leads
    items = []
    for b in k.current(X, leads=False, kos=False):
        if b.name not in gone:
            items += [(b.name, p) for p in pieces(X, b.name)]
    items += [('screw: ' + n, vc.screw(X, h, d)) for n, h, d in f.screw_list() if n != 'hood']      # the hood's own screw is out
    pos = [('across %g' % s, (s, 0.0)) for s in across] + [('across %g, back %g' % (s, b), (s, b)) for s in at for b in back]
    for name, (s, b) in pos:
        if name in out or k.late():
            continue
        d = comb((0.0, 0.0, 0.0), (lift, sh.HA), (s, (1.0, 0.0, 0.0)), (b, (0.0, -1.0, 0.0)))
        t = X.move(X.tbm.copy(hood), d[0], d[1], d[2])
        q = t.boundingBox; e = 0.6
        bb = adsk.core.BoundingBox3D.create(k.P3(q.minPoint.x - e, q.minPoint.y - e, q.minPoint.z - e),
                                            k.P3(q.maxPoint.x + e, q.maxPoint.y + e, q.maxPoint.z + e))
        best = None; shared = 0.0
        for n, p in items:
            if not bb.intersects(p.boundingBox):
                continue
            dd = X.mm.measureMinimumDistance(t, p).value * 10.0
            if dd < 0.0005:
                shared += X.xv(t, p)
            if best is None or dd < best[0]:
                best = (round(dd, 2), n)
        out[name] = (round(shared, 3), best)
    return out


# ---------- the driver on the hood's screw ----------
def profile(X, o, u, secs, items, st0=2.0, step=5.0, head=7.0):
    """Smallest room beside a tool on the line from o along u: in the head zone and beyond it, with the body and the place."""
    worst = {'head': None, 'beyond': None}
    boxes = [(n, p, k.bbd(p)) for n, p in items]
    total = sum(L for d, L in secs)
    s = st0
    while s <= total + 1e-6:
        r = k.rad_at(secs, s)
        p = k.Wp(o[0] + u[0] * s, o[1] + u[1] * s, o[2] + u[2] * s)
        for n, b, bx in boxes:
            if k.pbox(p, bx) * 10.0 > r + 12.0:
                continue
            mg = X.mm.measureMinimumDistance(p, b).value * 10.0 - r
            q = 'head' if s <= head else 'beyond'
            if worst[q] is None or mg < worst[q][0]:
                worst[q] = (round(mg, 2), s, n)
        s += step
    return worst


def reach(X):
    """Precision driver (shaft 3 x 60, handle 13 x 97) and a hand of 40 round the handle, everything in but the door."""
    out = R.setdefault('reach', {})
    h, u = f.hood_head()
    hard = []; leads = []
    for b in k.current(X, leads=True, kos=False):
        n = b.name
        if n in ('HOUSING_F_door', 'GROMMET_usbc_F', 'SCREWS_M2x6_env'):
            continue
        (leads if n.startswith('LEAD_') else hard).extend((n, p) for p in pieces(X, n))
    for name, secs, items in (('tool', k.MICRO, hard), ('hand', k.MICROG, hard), ('tool to leads', k.MICRO, leads)):
        if name in out or k.late():
            continue
        out[name] = profile(X, h, u, secs, items)
    return out


# ---------- the display module riding in (step 20): only what is new can newly be met ----------
def ride(X):
    """mm3 met by (a) every riding piece in the new fixed material and (b) the supply module's moved pins in every fixed part."""
    N = k.K4NS
    out = R.setdefault('ride', {})
    ad = added(X)
    fixed_new = [(n, ad[n]) for n in ('boss', 'radar block tops', 'hood', 'hood screw')]
    moving = []
    for n in N['names_of'](X, 'MODULE'):
        ps = [G[n]] if n in G else N['pieces'](X, 'v68', n)
        moving += [(n, i, p) for i, p in enumerate(ps)]
    moving += [('part of ' + n, 0, N['leadpart'](X, 'v68', n)) for n in sorted(N['LEADPART'])]
    for n, i, p in moving:
        if (n, i) in out or k.late() or p.faces.count == 0:
            continue
        hit = {}
        for s in N['STEPS']:
            t = X.move_n(X.tbm.copy(p), s)
            for fn, fb in fixed_new:
                q = X.xv(t, fb)
                if abs(q) > 0.0005:
                    hit[(s, fn)] = round(q, 3)
        out[(n, i)] = hit
    pins = ad['supply module pins']
    far = X.move_n(X.tbm.copy(pins), max(N['STEPS']))
    e0 = wext(pins, 1.0); e1 = wext(far, 1.0)
    box = [min(e0[i], e1[i]) if i % 2 == 0 else max(e0[i], e1[i]) for i in range(6)]
    fixed = N['names_of'](X, 'SHELL', 'UNIT', 'USBA', 'TOUCH', 'RADAR', 'BME')
    way = R.setdefault('pins way', {})
    for fn in fixed:
        if fn not in way and not k.late():
            way[fn] = crop(X, fn, box)
    ps = out.setdefault('pins', {})
    for s in N['STEPS']:
        if s in ps or k.late() or len(way) < len(fixed):
            continue
        t = X.move_n(X.tbm.copy(pins), s)
        ps[s] = {fn: round(q, 3) for fn, q in ((fn, sum(X.xv(t, p) for p in way[fn])) for fn in fixed) if abs(q) > 0.0005}
    done = sum(1 for q in out if q != 'pins')
    return {'pieces done': done, 'of': len([m for m in moving if m[2].faces.count]), 'steps': len(N['STEPS']),
            'met': {str(q): h for q, h in out.items() if q != 'pins' and h},
            'pins: steps done': len(ps), 'pins met': {s: h for s, h in ps.items() if h}}


# ---------- after the bodies are in the document ----------
def state(X):
    st = X.state()
    cur = k.current(X, leads=True)
    names = [b.name for b in cur]
    st['unit'] = len(names)
    st['printed'] = sum(1 for n in names if n in PRINTED)
    st['leads'] = sum(1 for n in names if n.startswith('LEAD_'))
    st['keep-outs'] = sum(1 for n in names if n.startswith('KO_'))
    st['backups ' + f.BACKUP] = sorted(n for n in X.names() if n.endswith(f.BACKUP))
    return st


def guards(X):
    """Volume and lumps of the sixteen printed parts (a big body's volume takes several seconds to read)."""
    out = R.setdefault('guards', {})
    for n in PRINTED:
        if n in out or k.late():
            continue
        b = X.body(n)
        out[n] = (round(b.volume * 1000.0, 3), b.lumps.count)
    return out


def matrix(X, tag='v69'):
    """The audits' interference table for the unit as it stands. Pairs of two unchanged bodies are taken over from version 68's table."""
    N = k.K4NS
    old = k.c[('k4m', 'v68')]; new = k.c.setdefault(('k4m', tag), {})
    ch = set(f.CHANGED)
    if not new:
        h = k.hc()                                           # the library keeps copies by name and volume: a changed body of the same volume would be read as it was
        for q in list(h.keys()):
            if isinstance(q, tuple) and q[0] == 'tc' and q[1] in ch:
                del h[q]
        for q, val in old.items():
            if q[0] not in ch and q[1] not in ch:
                new[q] = val
        for q in list(k.c.keys()):
            if isinstance(q, tuple) and len(q) == 3 and q[0] == 'k4p' and q[1] == 'v68' and q[2] not in ch:
                k.c.setdefault(('k4p', tag, q[2]), k.c[q])
    res, left, n = N['matrix'](X, tag)
    if left:
        return {'left': left}
    was = {frozenset(q): val for q, val in old.items()}
    rows = []
    for q, val in res.items():
        if q[0] in ch or q[1] in ch:
            o = was.get(frozenset(q), 0.0)
            if abs(val) > 0.0005 or abs(o) > 0.0005:
                rows.append((q[0], q[1], o, val))
    return {'bodies': n, 'pairs': len(res), 'not zero': sum(1 for val in res.values() if abs(val) > 0.0005),
            'not zero at version 68': sum(1 for val in old.values() if abs(val) > 0.0005), 'rows with a changed body': sorted(rows)}


def bed_faces(X, name, box, down=(0.0, 1.0, 0.0), deg=45.0):
    """mm2 of a model body's faces inside a world box that look at the bed by more than deg from upright.
    The shell prints lying on its chin: the bed is toward +y."""
    b = X.body(name)
    dn = k.dv(down); lim = math.cos(math.radians(deg)); area = 0.0; nf = 0
    bx = X.wbox(*box).boundingBox
    for fc in b.faces:
        q = fc.boundingBox
        if not (bx.contains(q.minPoint) and bx.contains(q.maxPoint)):
            continue
        nf += 1
        calc = fc.meshManager.createMeshCalculator()
        calc.setQuality(adsk.fusion.TriangleMeshQualityOptions.NormalQualityTriangleMesh)
        m = calc.calculate()
        co = m.nodeCoordinatesAsDouble; nr = m.normalVectorsAsDouble; ix = m.nodeIndices
        for j in range(0, len(ix), 3):
            a, c, d = ix[j] * 3, ix[j + 1] * 3, ix[j + 2] * 3
            e1 = (co[c] - co[a], co[c + 1] - co[a + 1], co[c + 2] - co[a + 2]); e2 = (co[d] - co[a], co[d + 1] - co[a + 1], co[d + 2] - co[a + 2])
            cr = cross(e1, e2); ar = 0.5 * math.sqrt(dot(cr, cr)) * 100.0
            nn = tuple((nr[a + i] + nr[c + i] + nr[d + i]) / 3.0 for i in range(3))
            ln = math.sqrt(dot(nn, nn)) or 1.0
            if (nn[0] * dn.x + nn[1] * dn.y + nn[2] * dn.z) / ln > lim:
                area += ar
    return round(area, 1), nf
