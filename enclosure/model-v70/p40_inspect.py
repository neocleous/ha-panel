# Block 4, before the block (architect log 2026-11-24-d, section 6, points 1 to 4): what the model holds at the three places.
# READ-ONLY for the model: temporary bodies 'TMP_*' may be added for measuring and are deleted again.
#   stage 'plate'   the base plate's eight counterbores, now and at version 69 (FLOOR_PLATE_v69): level faces and holes
#   stage 'bosses'  the door's four insert bosses: top faces, hole roofs, and every current body near the box the raised top
#                   would sweep on the door's way on (straight along y, 0 to 60 back, as block 3's 'slide')
#   stage 'cradle'  the cradle's leg boss on the base plate at (6.5, -72.5): its faces and holes; the grommet's +x ear and the
#                   door's +x seat beside it; the cradle and any screw or insert body there; the smallest distances
# Run: runpy.run_path(D + 'p40_inspect.py')['main']('plate')  -> p40_<stage>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
CB = [(-19.0, -77.0), (19.0, -74.5), (50.0, -67.0), (-50.0, -67.0), (64.0, -45.0), (-72.0, -38.0), (51.0, -14.0), (-51.0, -14.0)]
BOSS = [(-19.0, -77.0), (19.0, -74.5), (50.0, -67.0), (-50.0, -67.0)]
k_ = None


def dist(X, a, b):
    r = X.mm.measureMinimumDistance(a, b)
    return round(r.value * 10.0, 3), [round(v, 2) for v in k_.W(r.positionOne)], [round(v, 2) for v in k_.W(r.positionTwo)]


def lvl(k, X, b, box):
    out = []
    for f in b.faces:
        if f.geometry.surfaceType != k.PLN:
            continue
        p = k.W(f.pointOnFace)
        if not (box[0] <= p[0] <= box[1] and box[2] <= p[1] <= box[3] and box[4] <= p[2] <= box[5]):
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
        n = k.wv(nv)
        if abs(n[2]) < 0.999:
            continue
        ws = [k.W(v.geometry) for v in f.vertices]
        ext = [round(fn(w[i] for w in ws), 2) for i in range(2) for fn in (min, max)] if ws else None
        out.append((round(p[2], 3), 'up' if n[2] > 0 else 'down', round(f.area * 100.0, 2), ext))
    return sorted(out)


def plate(k, X):
    for name in ('FLOOR_PLATE', 'FLOOR_PLATE_v69'):
        b = X.body(name)
        print('%s: volume %.3f' % (name, b.volume * 1000.0))
        for (x, y) in CB:
            rows = lvl(k, X, b, (x - 4.0, x + 4.0, y - 4.0, y + 4.0, -0.1, 3.0))
            hs = [h for h in k.holes_of(b, 1.5, 4.0) if abs(h['A'][0] - x) < 0.2 and abs(h['A'][1] - y) < 0.2]
            print('  (%+.1f, %+.1f) level faces (z, dir, mm2, [x0,x1,y0,y1]): %s' % (x, y, rows))
            print('      holes: %s' % [(h['k'], h['r'], h['A'][2], h['B'][2]) for h in hs])


def bosses(k, X):
    door = X.body('HOUSING_F_door')
    cur = [b for b in k.current(X, leads=True) if b.name not in ('HOUSING_F_door', 'RENDER_FABRIC_door') and not b.name.startswith('TMP_')]
    for (bx, by) in BOSS:
        rows = lvl(k, X, door, (bx - 7.0, bx + 7.0, by - 9.0, by + 9.0, 8.0, 12.0))
        print('boss (%+.1f, %+.1f): door level faces z 8-12: %s' % (bx, by, rows))
        hs = [h for h in k.holes_of(door, 1.5, 3.0) if abs(h['A'][0] - bx) < 0.3 and abs(h['A'][1] - by) < 0.3]
        print('   holes: %s' % [(h['k'], h['r'], h['A'][2], h['B'][2]) for h in hs])
        # the boss's top as a crop of the door (z 9.6 to 11.5 round the boss), and the box its raised top would sweep
        top = [r for r in rows if r[1] == 'up' and abs(r[0] - 10.6) < 0.01]
        if not top:
            print('   no top face at 10.6'); continue
        e = top[0][3]
        sw = (e[0] - 0.3, e[1] + 0.3, e[2] - 60.3, e[3] + 0.3, 10.3, 11.1)
        print('   top face extents %s; swept and grown box %s' % (e, [round(v, 2) for v in sw]))
        swb = X.wbox(*sw)
        hits = []
        for b in cur:
            if not b.boundingBox.intersects(swb.boundingBox):
                continue
            v = k.xvol(X, X.tbm.copy(swb), b.name) if b.name in k.BIG else X.xv(X.tbm.copy(swb), X.tbm.copy(b))
            if abs(v) > 0.0005:
                hits.append((b.name, round(v, 4)))
        print('   bodies inside the swept box: %s' % (hits if hits else 'none'))
        # seated, the top's crop to its neighbours
        t = X.wbox(e[0] - 0.01, e[1] + 0.01, e[2] - 0.01, e[3] + 0.01, 9.6, 10.61); X.sec(t, X.tbm.copy(door))
        tb = X.add(t, 'TMP_boss', show=False)
        near = []
        grow = (e[0] - 8, e[1] + 8, e[2] - 8, e[3] + 8, 4.0, 20.0)
        gb = X.wbox(*grow)
        for b in cur:
            if not b.boundingBox.intersects(gb.boundingBox):
                continue
            d = dist(X, tb, b)
            if d[0] < 6.0:
                near.append((d[0], b.name, d[1], d[2]))
        near.sort()
        print('   seated, nearest to the boss top (z 9.6-10.6): %s' % near[:6])
        tb.deleteMe()


def cradle(k, X):
    P, G, Dr, Cr = X.body('FLOOR_PLATE'), X.body('GROMMET_usbc_F'), X.body('HOUSING_F_door'), X.body('CRADLE_5807')
    box = (1.0, 13.0, -80.0, -66.0, 2.4, 18.0)
    print('FLOOR_PLATE faces in %s:' % (box,))
    for r in k.faces(X, P, box, amin=0.05):
        print('   ', r)
    print('FLOOR_PLATE holes near (6.5, -72.5): %s' % [h for h in k.holes_of(P, 0.7, 5.0) if abs(h['A'][0] - 6.5) < 3 and abs(h['A'][1] + 72.5) < 3])
    print('GROMMET_usbc_F faces x 4..14, y -82..-75, z 9.9..14.1:')
    for r in k.faces(X, G, (4.0, 14.0, -82.0, -75.0, 9.9, 14.1), amin=0.05):
        print('   ', r)
    print('HOUSING_F_door faces x 4..13, y -82..-76, z 3.5..10.1:')
    for r in k.faces(X, Dr, (4.0, 13.0, -82.0, -76.0, 3.5, 10.1), amin=0.05):
        print('   ', r)
    print('CRADLE_5807 world box %s' % k.wbb(X, Cr))
    sw = X.wbox(1.0, 13.0, -80.0, -66.0, 2.4, 18.0)
    print('current bodies in that box:')
    for b in k.current(X, leads=True):
        if b.boundingBox.intersects(sw.boundingBox):
            v = X.xv(X.tbm.copy(sw), X.tbm.copy(b)) if b.name not in k.BIG else k.xvol(X, X.tbm.copy(sw), b.name)
            if abs(v) > 0.0005:
                print('    %-24s %.3f mm3 in the box, world box %s' % (b.name, v, k.wbb(X, b)))
    for a, b in ((G, P), (Dr, P), (G, Cr), (Dr, Cr)):
        print('%-16s to %-16s %s' % (a.name, b.name, dist(X, a, b)))
    # the door's two seats as crops
    for nm, bx in (('seat +x', (4.4, 12.4, -81.8, -76.8, 3.6, 10.01)), ('seat -x', (-12.4, -4.4, -81.8, -76.8, 3.6, 10.01))):
        t = X.wbox(*bx); X.sec(t, X.tbm.copy(Dr)); tb = X.add(t, 'TMP_s', show=False)
        print('door %s to FLOOR_PLATE %s' % (nm, dist(X, tb, P)))
        tb.deleteMe()
    for nm, bx in (('ear +x', (6.0, 13.0, -79.0, -75.5, 9.9, 12.5)), ('ear -x', (-13.0, -6.0, -79.0, -75.5, 9.9, 12.5))):
        t = X.wbox(*bx); X.sec(t, X.tbm.copy(G)); tb = X.add(t, 'TMP_e', show=False)
        print('grommet %s to FLOOR_PLATE %s' % (nm, dist(X, tb, P)))
        tb.deleteMe()


def _main(stage):
    global k_
    k = L['load'](); X = k.K(); k_ = k
    k.budget(70)
    print(L['stamp'](), 'before', X.state())
    {'plate': plate, 'bosses': bosses, 'cradle': cradle}[stage](k, X)
    for b in [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]:
        b.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main(stage):
    L['out']('p40_%s.txt' % stage, _main, stage)
