# Block 4 (D467, PR48): the carrier's two pilots for the ReSpeaker's screws, as they stand. READ-ONLY.
#   carrier  RESP_CARRIER in the slab frame (x, d = depth behind the glass's front, zd): its box; its level faces in its print
#            (square to d; bed at d 15.2, height d - 15.2); every hole and pin (radius, slab place, from d to d)
#   resp     the ReSpeaker's bodies in the slab frame: boxes, and the board's holes
#   screws   SCREWS_M2x6_env lump by lump: box, round faces (radius, axis), cones
#   pilots   the two pilots 1.6 across: what stands round them (the boss, by needles outward from the axis every 30 deg at
#            three depths), what lies under their floors, and what stands in front of the boss tops
# Run: runpy.run_path(D + 'd40_inspect4.py')['main'](stage)  -> d40_<stage>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')
PLN = adsk.core.SurfaceTypes.PlaneSurfaceType
CYL = adsk.core.SurfaceTypes.CylinderSurfaceType
CON = adsk.core.SurfaceTypes.ConeSurfaceType
BED = 15.2


def sbox(k, b):
    """Slab-frame box of a body from its faces' vertices and edge strokes."""
    pts = []
    for e in b.edges:
        ev = e.evaluator; ok, t0, t1 = ev.getParameterExtents(); ok, sp = ev.getStrokes(t0, t1, 0.005)
        pts += [k.Sf(q) for q in sp]
    return [round(fn(q[i] for q in pts), 3) for i in range(3) for fn in (min, max)]


def holes(k, b, rmin=0.4, rmax=6.0):
    rows = []
    for h in k.holes_of(b, rmin, rmax):
        A = k.Sf(k.Wp(*h['A'])); B = k.Sf(k.Wp(*h['B']))
        rows.append((h['k'], h['r'], round((A[0] + B[0]) / 2, 2), round((A[2] + B[2]) / 2, 2), round(min(A[1], B[1]), 3), round(max(A[1], B[1]), 3), h['L'], h['cov'], h['a']))
    return rows


def st_carrier(k, X):
    b = X.body('RESP_CARRIER')
    print('RESP_CARRIER slab box [x0, x1, d0, d1, zd0, zd1] %s; volume %.3f' % (sbox(k, b), b.volume * 1000))
    g = {}
    for f in b.faces:
        if f.geometry.surfaceType != PLN:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
        if abs(abs(nv.y) - 1) > 1e-4:
            continue
        d = k.Sf(f.pointOnFace)[1]
        key = (round(d, 4), 'up' if nv.y < 0 else 'down')                 # the slab frame's d grows along -y of the design
        a = g.setdefault(key, [0.0, 0]); a[0] += f.area * 100; a[1] += 1
    print('level faces in its print: d, bed height, looks, mm2, faces, off the 0.2 grid')
    for (d, s), (ar, n) in sorted(g.items()):
        h = d - BED; o = h - round(h / 0.2) * 0.2
        print('   d %8.4f  height %7.4f %-4s %9.2f %3d %s' % (d, h, s, ar, n, '' if abs(o) < 0.004 else 'OFF %+.3f' % o))
    print('holes (h) and pins (p): radius, slab x, zd, from d to d, length, cover, axis (world)')
    for r in sorted(holes(k, b), key=lambda r: (r[1], r[2], r[3])):
        print('   %s r %5.2f at x %7.2f zd %7.2f  d %7.3f .. %7.3f  L %5.2f cover %.2f axis %s' % r)
    for f in b.faces:
        if f.geometry.surfaceType == CON:
            gm = f.geometry; o = k.Sf(gm.origin)
            print('   cone: half angle %.1f, radius at origin %.3f, origin slab (%.2f, d %.3f, %.2f), %.2f mm2' % (math.degrees(gm.halfAngle), gm.radius * 10, o[0], o[1], o[2], f.area * 100))


def st_resp(k, X):
    for b in k.current(X, leads=True):
        if b.name.startswith('RESP_') and b.name != 'RESP_CARRIER':
            print('%-22s slab box %s volume %.3f' % (b.name, sbox(k, b), b.volume * 1000))
            if b.name == 'RESP_pcb':
                for r in sorted(holes(k, b), key=lambda r: (r[1], r[2], r[3])):
                    print('   %s r %5.2f at x %7.2f zd %7.2f  d %7.3f .. %7.3f  L %5.2f cover %.2f' % r[:8])


def st_screws(k, X):
    b = X.body('SCREWS_M2x6_env')
    print('SCREWS_M2x6_env: volume %.3f, lumps %d, visible %s' % (b.volume * 1000, b.lumps.count, b.isLightBulbOn))
    for i, lump in enumerate(b.lumps):
        t = X.tbm.copy(lump)
        rows = []
        for f in t.faces:
            gm = f.geometry
            if gm.surfaceType == CYL:
                rows.append('cyl r %.3f axis %s origin %s' % (gm.radius * 10, k.r2(k.unit(k.wv(gm.axis)), 3), k.r2(k.W(gm.origin), 2)))
            elif gm.surfaceType == CON:
                rows.append('cone %.1f deg r %.3f' % (math.degrees(gm.halfAngle), gm.radius * 10))
            elif gm.surfaceType == PLN:
                rows.append('flat %.2f mm2 at %s' % (f.area * 100, k.r2(k.W(f.pointOnFace), 2)))
        print('   lump %d: %.3f mm3, world box %s, slab box %s' % (i, X.vol(t), k.r2(k.wbb(X, t), 2), sbox(k, t)))
        for r in rows:
            print('        ' + r)


def st_pilots(k, X):
    b = X.body('RESP_CARRIER')
    n = (0.0, k.C, k.S)                                                   # the slab normal toward the viewer, in the world (d falls along it)
    ps = [r for r in holes(k, b) if r[0] == 'h' and abs(r[1] - 0.8) < 0.02]
    print('pilots 1.6 across: %d' % len(ps))
    for r in ps:
        x, zd, d0, d1 = r[2], r[3], r[4], r[5]
        print('pilot at slab x %.2f, zd %.2f: from d %.3f (bed %.3f) to d %.3f (bed %.3f), %.3f deep' % (x, zd, d0, d0 - BED, d1, d1 - BED, d1 - d0))
        for dd in (d1 - 0.3, (d0 + d1) / 2.0, d0 + 0.3, d0 - 0.5, d0 - 1.0, d0 - 1.6):
            p = k.W(k.Dp(x, dd, zd))
            row = []
            for j in range(12):
                a = math.radians(30 * j)
                u = (math.cos(a), -math.sin(a) * k.S, math.sin(a) * k.C)   # in the slab's plane: x, and the slab's up
                sg = k.needle_t(X, [X.tbm.copy(b)], p, k.along(p, u, 7.0), 0.02)
                row.append('%d:%s' % (30 * j, [(round(s0, 2), round(s1, 2)) for s0, s1 in sg][:2]))
            print('   at d %.2f (bed %.2f), solid outward from the axis: %s' % (dd, dd - BED, ' '.join(row)))
        p0 = k.W(k.Dp(x, d1 + 3.0, zd)); p1 = k.W(k.Dp(x, d0 - 4.0, zd))
        sg = k.needle_t(X, [X.tbm.copy(b)], p0, p1, 0.02)
        print('   on the axis from d %.2f to d %.2f, solid stretches (as d): %s' % (d1 + 3.0, d0 - 4.0, [(round(d1 + 3.0 - s0, 3), round(d1 + 3.0 - s1, 3)) for s0, s1 in sg]))
        tube = X.tbm.createCylinderOrCone(k.Dp(x, d1 + 8.0, zd), 0.25, k.Dp(x, d0 - 6.0, zd), 0.25)
        near = []
        for ob in k.current(X, leads=True):
            if ob.name == 'RESP_CARRIER' or not ob.boundingBox.intersects(tube.boundingBox):
                continue
            c = X.tbm.copy(ob); X.sec(c, X.tbm.copy(tube))
            if c.faces.count:
                sb = sbox(k, c)
                near.append('%s d %.3f..%.3f' % (ob.name, sb[2], sb[3]))
        print('   on the axis (a bar 5 across, d %.1f to %.1f), other bodies: %s' % (d0 - 6.0, d1 + 8.0, near))


def _main(stage, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'carrier': st_carrier, 'resp': st_resp, 'screws': st_screws, 'pilots': st_pilots}[stage](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(stage, tag='', **kw):
    L['out']('d40_%s%s.txt' % (stage, ('_' + tag) if tag else ''), _main, stage, **kw)
# END
