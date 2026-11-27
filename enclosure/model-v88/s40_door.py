# Block 3, the door: the four bosses for the base plate's screws (D528) read, then made taller with deeper holes; the grommet's
# two pilots deeper (D527). The reads are READ-ONLY (temporary bodies only). build() keeps a temporary body in the library's
# cache k.c; NOTHING IS PUT INTO THE DOCUMENT here (s21_put.py does that).
# World mm: x + = viewer's left, y + toward the screen, z up. The door prints standing: height = z - 2.8, layers 0.20.
#   tops    each boss: its top face (level, looking up, over the hole's axis): height, area, outline (edges with their kind,
#           ends, centre and radius); every body of the unit within 6 of that face, with the two nearest points
#   build   the door with (a) each boss's block taller by 'taller': a column over the top face made of the block's own outline
#           (the faces that bound the top face, carried up; its rear end buried in the door's wall), (b) the four boss holes
#           deeper by 'deeper', (c) the grommet's two pilots deeper by s30_holes.HOLES' figure -> k.c[key]
#   added   what the new door has that the model's lacks (the taller bosses): lumps, each lump's height range and volume beside
#           its top face's area x taller; its least distance to every body of the unit at home; and moved back along -y (the
#           door's way off and on, as ../model-v70/p37_checks.slide) by 17 steps to 60: what it shares with any body there;
#           then the same way with the door 0.5 and 1.0 high and 0.5 to either side (a margin on the record's way)
# Run: L.checked('s40_door.py', sha)['main'](what, tag, **kw)  -> s40_<what>_<tag>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/screw_margins_v88/'
L = runpy.run_path(D + 's00_lib.py')
ST = adsk.core.SurfaceTypes; CT = adsk.core.Curve3DTypes
BOSS = {'door_1': (50.0, -67.0), 'door_2': (19.0, -74.5), 'door_3': (-19.0, -77.0), 'door_4': (-50.0, -67.0)}
PART = 'HOUSING_F_door'
MODS = {}


def top_face(k, b, xy, zmin=10.0, zmax=13.0):
    """The level face looking up that lies over the hole's axis (a point on the axis is inside its outline's box and on it)."""
    best = None
    for f in b.faces:
        if f.geometry.surfaceType != ST.PlaneSurfaceType:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); n = k.wv(nv)
        if n[2] < 0.9999:
            continue
        z = k.W(f.pointOnFace)[2]
        if not (zmin < z < zmax):
            continue
        ok, prm = f.evaluator.getParameterAtPoint(k.Wp(xy[0], xy[1], z))
        if ok and f.evaluator.isParameterOnFace(prm):
            if best is None or z < best[0]:
                best = (z, f)
    if best is None:
        raise RuntimeError('no top face over %s' % (xy,))
    return best


def outline(k, f):
    rows = []
    for lp in f.loops:
        for e in lp.edges:
            g = e.geometry; ty = g.curveType
            a = k.r2(k.W(e.startVertex.geometry), 3); c = k.r2(k.W(e.endVertex.geometry), 3)
            if ty == CT.Line3DCurveType:
                rows.append(('line', a, c, round(e.length * 10.0, 3)))
            elif ty in (CT.Arc3DCurveType, CT.Circle3DCurveType):
                rows.append(('arc' if ty == CT.Arc3DCurveType else 'circle', a, c, round(e.length * 10.0, 3), 'centre', k.r2(k.W(g.center), 3), 'r', round(g.radius * 10.0, 3)))
            else:
                rows.append(('curve %d' % ty, a, c, round(e.length * 10.0, 3)))
            other = [q for q in e.faces if q != f]
            if other:
                og = other[0].geometry; ok, nv = other[0].evaluator.getNormalAtPoint(other[0].pointOnFace)
                rows[-1] = rows[-1] + ('next face: type %d, normal %s, %.2f mm2' % (og.surfaceType, k.r2(k.wv(nv), 4), other[0].area * 100.0),)
    return rows


def st_tops(k, X, names=('door_1', 'door_2', 'door_3', 'door_4'), within=6.0, body=None):
    b = X.body(body or PART)
    others = [q for q in k.current(X, leads=True, kos=True) if q.name not in (PART,)]
    for nm in names:
        z, f = top_face(k, b, BOSS[nm])
        ws = [k.W(v.geometry) for v in f.vertices]
        ext = [round(fn(w[i] for w in ws), 3) for i in range(3) for fn in (min, max)]
        print('%s at %s: top face at z %.3f (height %.3f in the print), %.3f mm2, box %s, %d edges' % (nm, BOSS[nm], z, z - 2.8, f.area * 100.0, ext, f.edges.count))
        for r in outline(k, f):
            print('      %s' % (r,))
        near = []
        for q in others:
            bb = k.wbb(X, q)
            if bb[0] > ext[1] + within or bb[1] < ext[0] - within or bb[2] > ext[3] + within or bb[3] < ext[2] - within or bb[4] > ext[5] + within or bb[5] < ext[4] - within:
                continue
            r = X.mm.measureMinimumDistance(f, q)
            if r.value * 10.0 <= within:
                near.append((round(r.value * 10.0, 3), q.name, k.r2(k.W(r.positionOne), 2), k.r2(k.W(r.positionTwo), 2)))
        print('   bodies within %.1f of the top face: %s' % (within, sorted(near)))


def column(k, X, b, nm, taller, bury=1.2, lap=0.2):
    """A column over a boss's top face: the block's own outline carried up by 'taller', from 'lap' under the top face.
    The outline is the hole's boss (a cylinder of radius 4.0 about the axis) and a bar 8.0 wide running from the axis to the
    door's wall along the block's two flat sides (read from the top face's straight edges); the bar ends 'bury' inside the wall."""
    z, f = top_face(k, b, BOSS[nm]); cx, cy = BOSS[nm]
    lines = []
    for lp in f.loops:
        for e in lp.edges:
            if e.geometry.curveType == CT.Line3DCurveType and e.length * 10.0 > 1.0:
                a = k.W(e.startVertex.geometry); c = k.W(e.endVertex.geometry)
                lines.append((a, c))
    if len(lines) != 2:
        raise RuntimeError('%s: %d straight edges on the top face, not 2' % (nm, len(lines)))
    dirs = []; reach = []
    for a, c in lines:
        da = math.hypot(a[0] - cx, a[1] - cy); dc = math.hypot(c[0] - cx, c[1] - cy)
        near, far = (a, c) if da < dc else (c, a)
        d = k.unit((far[0] - near[0], far[1] - near[1], 0.0)); dirs.append(d)
        off = abs((near[0] - cx) * (-d[1]) + (near[1] - cy) * d[0])
        if abs(off - 4.0) > 0.002:
            raise RuntimeError('%s: a flat side lies %.4f from the axis, not 4.0' % (nm, off))
        reach.append((far[0] - cx) * d[0] + (far[1] - cy) * d[1])
    if abs(dirs[0][0] - dirs[1][0]) > 1e-4 or abs(dirs[0][1] - dirs[1][1]) > 1e-4:
        raise RuntimeError('%s: the two flat sides are not parallel' % nm)
    d = dirs[0]; n = (-d[1], d[0], 0.0); Lb = max(reach) + bury
    z0 = z - lap; z1 = z + taller
    t = X.cyl((cx, cy, z0), (cx, cy, z1), 4.0)
    cen = (cx + d[0] * Lb / 2.0, cy + d[1] * Lb / 2.0, (z0 + z1) / 2.0)
    X.uni(t, X.obox(cen, d, n, Lb, 8.0, z1 - z0))
    return t, {'z': z, 'area': f.area * 100.0, 'dir': k.r2(d, 4), 'reach': [round(q, 3) for q in reach], 'bar': round(Lb, 3)}


def less(X, a, b):
    t = X.tbm.copy(a); X.dif(t, X.tbm.copy(b))
    return t


def st_build(k, X, key='sr_door', taller=0.6, deeper=0.6, pilots=True, bosses=True):
    S31 = MODS['s31']; H = dict(MODS['s30']['HOLES'])
    b = X.body(PART); t = X.tbm.copy(b)
    print('%s: the model\'s body %.3f mm3, lumps %d, faces %d' % (PART, b.volume * 1000.0, b.lumps.count, b.faces.count))
    if bosses:
        for nm in ('door_1', 'door_2', 'door_3', 'door_4'):
            c, info = column(k, X, b, nm, taller)
            add = less(X, c, b)
            print('   %s: top face z %.3f, %.3f mm2; the block runs %s from the axis, its flat sides reach %s, the bar %.3f long; column %.3f mm3, '
                  'of it new %.4f mm3 in %d lumps (top area x %.2f = %.4f)' % (nm, info['z'], info['area'], info['dir'], info['reach'], info['bar'], X.vol(c),
                                                                               X.vol(add) if add.faces.count else 0.0, add.lumps.count if add.faces.count else 0,
                                                                               taller, info['area'] * taller))
            X.uni(t, c)
        print('   after the columns: %.3f mm3, lumps %d, faces %d' % (X.vol(t), t.lumps.count, t.faces.count))
        for nm in ('door_1', 'door_2', 'door_3', 'door_4'):
            p, M, F, r, d0 = H[nm]
            h = S31['deepen'](k, X, t, b, M, F, r, deeper)
            h2 = S31['hole_geo'](k, t, M, F, r)
            print('   %s hole: %.4f deep -> %.4f deep; wall faces %d -> %d' % (nm, h['depth'], h2['depth'], h['faces'], h2['faces']))
    if pilots:
        for nm in ('grom_L', 'grom_R'):
            p, M, F, r, d0 = H[nm]
            h = S31['deepen'](k, X, t, b, M, F, r, d0)
            h2 = S31['hole_geo'](k, t, M, F, r)
            print('   %s pilot: %.4f deep -> %.4f deep; wall faces %d -> %d' % (nm, h['depth'], h2['depth'], h['faces'], h2['faces']))
    k.c[key] = t
    print('   %s: %.3f mm3 (%+.3f), lumps %d, faces %d' % (key, X.vol(t), X.vol(t) - b.volume * 1000.0, t.lumps.count, t.faces.count))
    for lab, q in (('what goes', less(X, b, t)), ('what comes', less(X, t, b))):
        n = q.lumps.count if q.faces.count else 0
        print('   %s: %.4f mm3 in %d lumps: %s' % (lab, X.vol(q) if n else 0.0, n, X.lumps(q)[:12] if n else ''))


def st_added(k, X, key='sr_door', steps=(0.0, 0.2, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 15.0, 20.0, 30.0, 40.0, 60.0), sec=70,
             offs=((0.5, 0.0), (1.0, 0.0), (0.0, 0.5), (0.0, -0.5), (1.0, 0.5), (1.0, -0.5))):
    k.budget(sec)
    b = X.body(PART); t = k.c[key]
    add = less(X, t, b)
    if not add.faces.count:
        print('nothing added'); return
    print('added: %.4f mm3 in %d lumps' % (X.vol(add), add.lumps.count))
    bb = k.wbb(X, add)
    print('   world box of all of it %s' % bb)
    lumps = [X.tbm.copy(l) for l in add.lumps]
    for l in lumps:
        print('   lump %.4f mm3, world box %s' % (X.vol(l), k.wbb(X, l)))
    others = [q for q in k.current(X, leads=True, kos=True) if q.name != PART]
    print('at home, each added lump to the bodies of the unit within 8 (least distance, body, point on the lump, point on the body):')
    for l in lumps:
        lb = k.wbb(X, l); near = []
        for q in others:
            qb = k.wbb(X, q)
            if qb[0] > lb[1] + 8 or qb[1] < lb[0] - 8 or qb[2] > lb[3] + 8 or qb[3] < lb[2] - 8 or qb[4] > lb[5] + 8 or qb[5] < lb[4] - 8:
                continue
            r = X.mm.measureMinimumDistance(l, q)
            if r.value * 10.0 <= 8.0:
                near.append((round(r.value * 10.0, 3), q.name, k.r2(k.W(r.positionOne), 2), k.r2(k.W(r.positionTwo), 2)))
        print('   lump at %s: %s' % (lb, sorted(near)[:8]))
    sweep = (bb[0] - 1.0, bb[1] + 1.0, bb[2] - max(steps) - 1.0, bb[3] + 1.0, bb[4] - 1.0, bb[5] + 1.0)
    sw = X.wbox(*sweep); fixed = []
    for q in others:
        if q.name in ('GROMMET_usbc_F', 'SCREWS_M2x6_env') or q.name.startswith('RENDER_'):
            continue                                       # the grommet and its screws ride with the door
        qb = k.wbb(X, q)
        if qb[0] > sweep[1] or qb[1] < sweep[0] or qb[2] > sweep[3] or qb[3] < sweep[2] or qb[4] > sweep[5] or qb[5] < sweep[4]:
            continue
        c = X.tbm.copy(q); X.sec(c, X.tbm.copy(sw))
        if c.faces.count:
            fixed.append((q.name, c))
    print('the door\'s way: the added lumps moved back along -y; bodies of the unit in the sweep %s: %s' % (list(sweep), [n for n, c in fixed]))
    for d in steps:
        hit = {}
        m = X.tbm.copy(add); X.move(m, 0.0, -d, 0.0)
        for n, c in fixed:
            v = X.xv(m, c)
            if abs(v) > 0.0005:
                hit[n] = round(v, 4)
        print('   back %5.1f: %s' % (d, hit if hit else 'clear'))
        if k.late():
            print('time'); return
    # the same way with the door held a little high or to one side (not the record's way: a margin on it)
    for dz, dx in offs:
        sw2 = X.wbox(sweep[0] - abs(dx) - 0.1, sweep[1] + abs(dx) + 0.1, sweep[2], sweep[3], sweep[4], sweep[5] + dz + 0.1); fx = []
        for q in others:
            if q.name in ('GROMMET_usbc_F', 'SCREWS_M2x6_env') or q.name.startswith('RENDER_'):
                continue
            c = X.tbm.copy(q)
            if not c.boundingBox.intersects(sw2.boundingBox):
                continue
            X.sec(c, X.tbm.copy(sw2))
            if c.faces.count:
                fx.append((q.name, c))
        bad = []
        for d in steps:
            m = X.tbm.copy(add); X.move(m, dx, -d, dz)
            hit = dict((n, round(X.xv(m, c), 4)) for n, c in fx)
            hit = dict((n, v) for n, v in hit.items() if abs(v) > 0.0005)
            if hit:
                bad.append((d, hit))
        print('   %.1f high, %+.1f to the side, back 0 to %.0f in %d steps: %s' % (dz, dx, max(steps), len(steps), bad if bad else 'clear at every step'))
        if k.late():
            print('time'); return
    g = X.body('GROMMET_usbc_F')
    print('the grommet, which rides with the door: shares %.4f mm3 with the added lumps' % X.xv(X.tbm.copy(add), X.tbm.copy(g)))


def _main(what, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'tops': st_tops, 'build': st_build, 'added': st_added}[what](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(what, tag='', s30=None, s31=None, **kw):
    if s30:
        MODS['s30'] = L['checked']('s30_holes.py', s30)
    if s31:
        MODS['s31'] = L['checked']('s31_deepen.py', s31)
    L['out']('s40_%s%s.txt' % (what, ('_' + tag) if tag else ''), _main, what, **kw)
# END
