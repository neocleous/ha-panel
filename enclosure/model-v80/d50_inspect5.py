# Block 5 (D471, PR44): the gap at the hood's boss in the shell, as it stands. READ-ONLY.
# World mm: x + = viewer's left, y + toward the screen, z up. The shell prints chin down: bed at y 6.7992, height = 6.7992 - y,
# so "up" in its print is toward -y (the back).
#   gap    needles along y through the shell (cut to a box round the place) on a grid in x and z: wherever two solid stretches
#          of the shell have air between them, the air's y range; with what of the hood, its screw and the sensor's envelope
#          lies in that air. Then the shell's faces that bound the place.
#   faces  the shell's faces inside a box: kind, area, world box; a flat face's normal, a round face's radius and axis
#   map    a picture in letters of a section: plane 'z' (columns x, rows y) or plane 'x' (columns z, rows y), from needles
#          along y: # shell, H hood, S screw, e the sensor's envelope, f foam, D door, . air; 'extra' adds temporary bodies
#          kept in k.c under the given keys, drawn as +
#   near   the hood, its screw and the neighbours against the shell round the place: smallest distances, and where
# Run: runpy.run_path(D + 'd50_inspect5.py')['main'](stage)  -> d50_<stage>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')
PLN = adsk.core.SurfaceTypes.PlaneSurfaceType
CYL = adsk.core.SurfaceTypes.CylinderSurfaceType
CON = adsk.core.SurfaceTypes.ConeSurfaceType
BEDY = 6.7992
BOX = (-64.0, -53.0, -60.0, -42.0, 95.0, 105.0)
OTHERS = ('BME_HOOD', 'SCREWS_M2x6_env', 'BME680_env', 'FOAM_bme_env', 'FOAM_bme_top_env', 'LEAD_BME680', 'HOUSING_F_door', 'HOUSING_F_cap')


def fbox(k, f):
    pts = [k.W(v.geometry) for v in f.vertices]
    for e in f.edges:
        ev = e.evaluator; ok, t0, t1 = ev.getParameterExtents(); ok, sp = ev.getStrokes(t0, t1, 0.01)
        pts += [k.W(q) for q in sp]
    return [round(fn(p[i] for p in pts), 2) for i in range(3) for fn in (min, max)] if pts else []


def st_gap(k, X, x0=-61.0, x1=-56.0, dx=0.25, z0=97.5, z1=102.5, dz=0.5, y0=-42.0, y1=-60.0, wmax=4.0, name='HOUSING_F_front'):
    sh = L['crop'](X, name, BOX)
    oth = [(n, L['crop'](X, n, BOX)) for n in OTHERS if X.body(n) is not None]
    oth = [(n, t) for n, t in oth if t.faces.count]
    print('%s cut to %s: %.3f mm3, lumps %d; others in the box: %s' % (name, BOX, X.vol(sh), sh.lumps.count, [n for n, t in oth]))
    print('air between two solid stretches of the shell along y (from y %.1f toward the back), narrower than %.1f: x: y front..y back (height in the print of the gap\'s floor .. roof)' % (y0, wmax))
    nz = int(round((z1 - z0) / dz)) + 1; nx = int(round((x1 - x0) / dx)) + 1
    for j in range(nz):
        z = z0 + j * dz; row = []
        for i in range(nx):
            x = x0 + i * dx
            sg = k.needle_t(X, [sh], (x, y0, z), (x, y1, z), 0.02)
            for a, b in zip(sg[:-1], sg[1:]):
                w = b[0] - a[1]
                if 0.02 < w < wmax:
                    ya = y0 - a[1]; yb = y0 - b[0]
                    inside = []
                    for n, t in oth:
                        so = k.needle_t(X, [t], (x, ya, z), (x, yb, z), 0.02)
                        if so:
                            inside.append('%s %.2f' % (n[:8], sum(q[1] - q[0] for q in so)))
                    row.append('%.2f: %.2f..%.2f (%.2f%s)' % (x, ya, yb, w, (' ' + ' '.join(inside)) if inside else ''))
        print('z %6.2f | %s' % (z, ' ; '.join(row) or '-'))


def st_faces(k, X, box=(-60.5, -56.5, -58.0, -44.0, 98.0, 102.0), name='HOUSING_F_front', amin=0.0):
    b = X.body(name); n = 0
    print('%s: faces whose boxes cross %s' % (name, box))
    for f in b.faces:
        bb = f.boundingBox
        w0 = k.W(bb.minPoint); w1 = k.W(bb.maxPoint)
        lo = [min(w0[i], w1[i]) - 3.0 for i in range(3)]; hi = [max(w0[i], w1[i]) + 3.0 for i in range(3)]
        if lo[0] > box[1] or hi[0] < box[0] or lo[1] > box[3] or hi[1] < box[2] or lo[2] > box[5] or hi[2] < box[4]:
            continue
        e = fbox(k, f)
        if not e or e[0] > box[1] or e[1] < box[0] or e[2] > box[3] or e[3] < box[2] or e[4] > box[5] or e[5] < box[4]:
            continue
        if f.area * 100 < amin:
            continue
        g = f.geometry; st = g.surfaceType
        if st == PLN:
            ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); nn = k.r2(k.wv(nv), 3)
            d = 'flat, normal %s' % (nn,)
        elif st == CYL:
            d = 'round r %.3f, axis %s through %s' % (g.radius * 10, k.r2(k.unit(k.wv(g.axis)), 3), k.r2(k.W(g.origin), 2))
        elif st == CON:
            d = 'cone %.1f deg, r %.3f at %s, axis %s' % (math.degrees(g.halfAngle), g.radius * 10, k.r2(k.W(g.origin), 2), k.r2(k.unit(k.wv(g.axis)), 3))
        else:
            d = 'other (%d)' % st
        n += 1
        print('   %8.3f mm2  box %s  %s' % (f.area * 100, e, d))
    print('faces: %d' % n)


def st_map(k, X, plane='z', at=100.0, c0=-64.0, c1=-54.0, dc=0.2, y0=-44.0, y1=-58.0, dy=0.2, name='HOUSING_F_front', extra=(), shell_key=None):
    sh = L['crop'](X, k.c[shell_key] if shell_key else name, BOX)
    oth = [(n, L['crop'](X, n, BOX)) for n in OTHERS if X.body(n) is not None]
    oth = [(n, t) for n, t in oth if t.faces.count]
    ch = {'BME_HOOD': 'H', 'SCREWS_M2x6_env': 'S', 'BME680_env': 'e', 'FOAM_bme_env': 'f', 'FOAM_bme_top_env': 'f', 'LEAD_BME680': 'l', 'HOUSING_F_door': 'D', 'HOUSING_F_cap': 'C'}
    lay = [('#', sh)] + [('+', X.tbm.copy(k.c[q])) for q in extra] + [(ch[n], t) for n, t in oth]
    nc = int(round((c1 - c0) / dc)) + 1; nr = int(round((y0 - y1) / dy)) + 1
    grid = [['.'] * nc for _ in range(nr)]
    for i in range(nc):
        c = c0 + i * dc
        p0 = (c, y0 + dy / 2, at) if plane == 'z' else (at, y0 + dy / 2, c)
        p1 = (c, y1 - dy / 2, at) if plane == 'z' else (at, y1 - dy / 2, c)
        for sym, t in lay:
            for a, b in k.needle_t(X, [t], p0, p1, 0.02):
                for j in range(nr):
                    yy = j * dy + dy / 2                       # distance from p0 of the row's middle
                    if a - 1e-6 <= yy <= b + 1e-6:
                        grid[j][i] = sym
    print('section at %s %.2f: columns %s from %.1f to %.1f every %.2f; rows y from %.1f to %.1f every %.2f (down the page = toward the back = up in the shell\'s print)' % (
        plane, at, 'x' if plane == 'z' else 'z', c0, c1, dc, y0, y1, dy))
    for j in range(nr):
        print('%7.1f %s' % (y0 - j * dy, ''.join(grid[j])))


def st_near(k, X):
    sh = L['crop'](X, 'HOUSING_F_front', (-90.0, -50.0, -60.0, -20.0, 86.0, 116.0))
    for n in OTHERS:
        b = X.body(n)
        if b is None:
            continue
        r = X.mm.measureMinimumDistance(sh, b)
        p = k.W(r.positionOne); q = k.W(r.positionTwo)
        print('%-18s to the shell (cut to the hood\'s corner): %.4f at %s / %s' % (n, r.value * 10, k.r2(p, 2), k.r2(q, 2)))


def _main(stage, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'gap': st_gap, 'faces': st_faces, 'near': st_near, 'map': st_map}[stage](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(stage, tag='', **kw):
    L['out']('d50_%s%s.txt' % (stage, ('_' + tag) if tag else ''), _main, stage, **kw)
# END
