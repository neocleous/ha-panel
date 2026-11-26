# Block 9, after the last put: how the holder and the left box's new block print. READ-ONLY (temporary bodies only).
#   'grid'    RADAR_HOLDER upright (bed at its lowest face, height = world z - bed, layers 0.20): every flat face square to the
#             height, with its place on the grid, whether it looks at the bed, and its area; every round face with its axis.
#             SPKBOX_L rear face down (bed at its lowest world y, height = world y - bed, layers 0.20): the level faces and the
#             sloped faces of the new block (x 39.9..46.1, y -17.1..-3.9, z 53.1..62.1), and the pilot.
#   'walls'   the holder's sections, measured as the rule's section 3 measures a wall: a thin bar through the part.
#   'guards'  the holder's volume both ways (D425), with the unit's counts.
# Run: runpy.run_path(D + 'p91_b9_print.py')['main'](stage)  -> p91_<stage>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
LH = 0.2


def off(h):
    q = h / LH
    return (q - round(q)) * LH


def faces(k, X, body):
    flat = []; rnd = []; other = []
    for f in body.faces:
        g = f.geometry; st = g.surfaceType
        p = k.W(f.pointOnFace)
        if st == 0:
            ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
            flat.append((k.wv(nv), p, f.area * 100.0, f))
        elif st == 1:
            ax = k.wv(g.axis); o = k.W(g.origin)
            rnd.append((ax, o, g.radius * 10.0, p, f.area * 100.0))
        else:
            other.append((st, p, f.area * 100.0))
    return flat, rnd, other


def grid(k, X):
    H = X.body('RADAR_HOLDER'); bb = k.wbb(X, H); bed = bb[4]
    print('RADAR_HOLDER upright: world box %s; bed at z %.2f; %.1f tall, %d layers of %.2f' % (bb, bed, bb[5] - bed, round((bb[5] - bed) / LH), LH))
    flat, rnd, other = faces(k, X, H)
    lev = [(round(p[2], 3), 'looks at the bed' if n[2] < 0 else 'looks up', round(a, 2), k.r2(p)) for n, p, a, f in flat if abs(abs(n[2]) - 1) < 1e-4]
    print('level faces: %d (of %d flat faces; %d round; %d other)' % (len(lev), len(flat), len(rnd), len(other)))
    for z, d, a, p in sorted(lev):
        h = z - bed
        print('   z %7.3f  height %6.2f  %-16s %7.2f mm2  off the grid %+.3f  at %s' % (z, h, d, a, off(h), p))
    slo = [(k.r2(n, 3), round(a, 2), k.r2(p)) for n, p, a, f in flat if 1e-4 < abs(n[2]) < 1 - 1e-4]
    print('sloped flat faces (neither level nor upright): %s' % (slo or 'none'))
    print('round faces (axis, a point on it, radius, a point on the face, area):')
    for ax, o, r, p, a in sorted(rnd, key=lambda q: (q[3][2], q[3][0])):
        d = 'along the height' if abs(abs(ax[2]) - 1) < 1e-4 else ('lying in the layers' if abs(ax[2]) < 1e-4 else 'tilted')
        print('   r %.3f  axis %s (%s) through %s; face at %s, %.2f mm2' % (r, k.r2(ax), d, k.r2(o), k.r2(p), a))
    B = X.body('SPKBOX_L'); bb = k.wbb(X, B); bed = bb[2]
    print('SPKBOX_L rear face down: world box %s; bed at y %.3f; %.2f tall' % (bb, bed, bb[3] - bed))
    c = X.wbox(39.9, 46.1, -17.1, -3.9, 53.1, 62.1); X.sec(c, X.tbm.copy(B))
    print('the block, cropped: box %s, %.3f mm3' % (k.wbb(X, c), X.vol(c)))
    flat, rnd, other = faces(k, X, c)
    for n, p, a, f in sorted(flat, key=lambda q: (q[1][1], q[1][0])):
        if abs(abs(n[1]) - 1) < 1e-4:
            h = p[1] - bed
            print('   level: y %7.3f  height %6.2f  %-16s %7.2f mm2  off the grid %+.3f  at %s' % (p[1], h, 'looks at the bed' if n[1] < 0 else 'looks up', a, off(h), k.r2(p)))
        elif abs(n[1]) > 1e-4:
            ang = math.degrees(math.acos(min(1.0, abs(n[1]))))
            print('   sloped: normal %s, %.1f deg from level, %s, %.2f mm2 at %s' % (k.r2(n, 3), ang, 'looks at the bed' if n[1] < 0 else 'looks up', a, k.r2(p)))
    for ax, o, r, p, a in rnd:
        print('   round: r %.3f axis %s through %s, %.2f mm2' % (r, k.r2(ax), k.r2(o), a))
    for nm, y in (('the front face of the box beside the block (x 50, z 57.6)', None),):
        st = k.needle_t(X, [X.tbm.copy(B)], (50.0, -60.0, 57.6), (50.0, 0.0, 57.6), 0.01)
        print('   left box along y at (x 50.0, z 57.6): %s' % [(round(-60 + a, 2), round(-60 + b, 2)) for a, b in st])
    st = k.needle_t(X, [X.tbm.copy(B)], (48.0, -60.0, 46.0), (48.0, 0.0, 46.0), 0.01)
    print('   left box along y at (x 48.0, z 46.0): %s' % [(round(-60 + a, 2), round(-60 + b, 2)) for a, b in st])


def walls(k, X):
    H = X.tbm.copy(X.body('RADAR_HOLDER'))

    def nd(lab, p0, p1):
        st = k.needle_t(X, [H], p0, p1, 0.01)
        ax = [i for i in range(3) if abs(p1[i] - p0[i]) > 1e-9][0]
        print('   %-66s %s' % (lab, [(round(p0[ax] + a, 2), round(p0[ax] + b, 2), round(b - a, 2)) for a, b in st]))
    print('RADAR_HOLDER, thin bars through it (from, to, thickness):')
    nd('ledge plate, along y at (x 31, z 29.0)', (31.0, -4.0, 29.0), (31.0, 0.0, 29.0))
    nd('ledge plate below its window, along z at (x 31, y -2.3)', (31.0, -2.3, 27.0), (31.0, -2.3, 31.0))
    nd('ledge plate above its window, along z at (x 31, y -2.3)', (31.0, -2.3, 49.0), (31.0, -2.3, 54.0))
    nd('ledge plate beside its window, -x, along x at (y -2.3, z 44.9)', (21.0, -2.3, 44.9), (26.0, -2.3, 44.9))
    nd('ledge plate beside its window, +x, along x at (y -2.3, z 40)', (37.0, -2.3, 40.0), (41.0, -2.3, 40.0))
    nd('-x wall, along x at (y -4.5, z 40)', (21.0, -4.5, 40.0), (25.0, -4.5, 40.0))
    nd('bottom, along z at (x 31, y -4.5)', (31.0, -4.5, 27.0), (31.0, -4.5, 30.0))
    nd('top plate over the radar, along z at (x 31, y -4.5)', (31.0, -4.5, 50.5), (31.0, -4.5, 54.0))
    nd('top plate behind the radar, along z at (x 31, y -8.5)', (31.0, -8.5, 50.5), (31.0, -8.5, 54.0))
    nd('top plate over the -x wall, along z at (x 22.7, y -4.5)', (22.7, -4.5, 50.0), (22.7, -4.5, 54.0))
    nd('tie bar, along y at (x 25, z 52.3)', (25.0, -11.0, 52.3), (25.0, -7.0, 52.3))
    nd('tie bar, along z at (x 25, y -9.8)', (25.0, -9.8, 50.5), (25.0, -9.8, 54.0))
    nd('tab beside the land, along x at (y -9.8, z 60.5)', (35.0, -9.8, 60.5), (41.0, -9.8, 60.5))
    nd('tab at the land and the rib, along x at (y -7.35, z 60.5)', (35.0, -7.35, 60.5), (41.0, -7.35, 60.5))
    nd('tab across the slot, along y at (x 38.0, z 57.6)', (38.0, -11.0, 57.6), (38.0, -3.0, 57.6))
    nd('tab across the slot, along z at (x 38.0, y -7.35)', (38.0, -7.35, 50.0), (38.0, -7.35, 63.0))
    nd('tab along y at (x 38.0, z 60.5)', (38.0, -11.0, 60.5), (38.0, -3.0, 60.5))
    nd('rib along y at (x 39.8, z 60.5)', (39.8, -11.0, 60.5), (39.8, -3.0, 60.5))
    nd('land along y at (x 36.8, z 60.5)', (36.8, -11.0, 60.5), (36.8, -3.0, 60.5))
    nd('standoff A, along x at (y 1.5, z 37)', (20.0, 1.5, 37.0), (25.0, 1.5, 37.0))
    nd('standoff A, along z at (x 22.2, y 1.5)', (22.2, 1.5, 34.0), (22.2, 1.5, 40.0))
    nd('standoff A, along y at (x 22.2, z 37)', (22.2, -3.5, 37.0), (22.2, 3.5, 37.0))
    nd('standoff B, along z at (x 22.2, y 1.5)', (22.2, 1.5, 44.5), (22.2, 1.5, 50.0))
    nd('standoff C, along x at (y 1.7, z 48.3)', (37.0, 1.7, 48.3), (46.0, 1.7, 48.3))
    nd('standoff C, along z at (x 43.4, y 1.7)', (43.4, 1.7, 45.0), (43.4, 1.7, 52.0))
    nd('standoff C and its foot, along y at (x 43.4, z 48.3)', (43.4, -3.5, 48.3), (43.4, 3.5, 48.3))
    nd('C\'s foot, along x at (y -0.5, z 49.5)', (37.0, -0.5, 49.5), (46.0, -0.5, 49.5))
    nd('arm, along y at (x 10, z 42)', (10.0, 0.0, 42.0), (10.0, 4.0, 42.0))
    nd('arm, along z at (x 10, y 1.9)', (10.0, 1.9, 39.0), (10.0, 1.9, 45.0))
    nd('arm with its pad, along y at (x 0.5, z 42)', (0.5, 0.0, 42.0), (0.5, 4.0, 42.0))
    nd('arm, along x at (y 1.9, z 42)', (-3.0, 1.9, 42.0), (25.0, 1.9, 42.0))
    nd('arm\'s root, along x at (y 0.0, z 42)', (19.0, 0.0, 42.0), (25.0, 0.0, 42.0))
    nd('arm\'s root, along z at (x 22.2, y 0.0)', (22.2, 0.0, 38.5), (22.2, 0.0, 45.5))
    nd('gusset, along x at (y 0.8, z 42)', (19.0, 0.8, 42.0), (25.0, 0.8, 42.0))
    nd('-x post, along x at (y 1.0, z 31.6)', (18.0, 1.0, 31.6), (27.0, 1.0, 31.6))
    nd('-x post, along z at (x 22.5, y 1.0)', (22.5, 1.0, 27.0), (22.5, 1.0, 36.0))
    nd('+x post, along x at (y 1.0, z 48.8)', (37.0, 1.0, 48.8), (44.0, 1.0, 48.8))
    nd('+x post, along z at (x 40.5, y 1.0)', (40.5, 1.0, 45.0), (40.5, 1.0, 53.0))
    nd('+x post behind the ledge (the block under the head), along z at (x 40.5, y -3.6)', (40.5, -3.6, 45.0), (40.5, -3.6, 53.0))
    nd('-x post behind the ledge (the block under the head), along x at (y -3.6, z 31.6)', (18.0, -3.6, 31.6), (27.0, -3.6, 31.6))
    R = X.tbm.copy(X.body('LD2410C_env_F')); rb = k.wbb(X, R)
    print('the radar\'s box %s' % rb)
    for lab, p0, p1 in (('over the radar\'s top edge, along z at (x 31, y -4.4)', (31.0, -4.4, rb[5]), (31.0, -4.4, rb[5] + 3.0)),
                        ('under its bottom edge, along z at (x 31, y -4.4)', (31.0, -4.4, rb[4] - 3.0), (31.0, -4.4, rb[4])),
                        ('beside its -x edge, along x at (y -4.4, z 40)', (rb[0] - 3.0, -4.4, 40.0), (rb[0], -4.4, 40.0))):
        st = k.needle_t(X, [H], p0, p1, 0.01)
        ax = [i for i in range(3) if abs(p1[i] - p0[i]) > 1e-9][0]
        print('   holder %-58s %s' % (lab, [(round(p0[ax] + a, 2), round(p0[ax] + b, 2)) for a, b in st]))


def guards(k, X):
    st = X.state(); cur = k.current(X, leads=True); names = X.names()
    print('bodies %d, visible %d, in the unit %d, TMP_ %d, AUD_ %d' % (st['bodies'], st['visible'], len(cur),
          sum(1 for n in names if n.startswith('TMP_')), sum(1 for n in names if n.startswith('AUD_'))))
    for n in ('RADAR_HOLDER', 'SPKBOX_L', 'LD2410C_env_F', 'SCREWS_M2x6_env', 'LEAD_RADAR'):
        b = X.body(n)
        vh = b.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume * 1000.0
        print('%-16s preflight %12.3f  very high %12.3f  lumps %d  faces %d  visible %s  box %s' % (n, b.volume * 1000.0, vh, b.lumps.count, b.faces.count, b.isLightBulbOn, k.wbb(X, b)))


def _main(stage):
    k = L['load'](); X = k.K(); k.budget(75)
    print(L['stamp'](), 'before', X.state())
    {'grid': grid, 'walls': walls, 'guards': guards}[stage](k, X)
    print(L['stamp'](), 'after', X.state())


def main(stage):
    L['out']('p91_%s.txt' % stage, _main, stage)
