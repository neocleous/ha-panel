# Block 4: level faces in each part's print, in the places block 4 changed, against the part's layer grid. READ-ONLY.
# A face is "level" when it is square to the part's print height. Offset = (height - first) - nearest whole number of layers.
#   FLOOR_PLATE      underside down, height z, layers 0.20 from 0.20       (counterbores, the relieved cradle boss)
#   HOUSING_F_door   standing on its bed at z 2.8, height z - 2.8, 0.20    (the four boss tops and holes, the +x seat)
#   GROMMET_usbc_F   on its side at z 10.0, height z - 10.0, 0.20 then 0.12 (the tab's back, the ears)
#   SLAB_frame       glass side down, height d, 0.10 (first layer taken as 0.10; a 0.20 first layer changes nothing above 0.2)
#   HOUSING_F_plate  back down, height 12.8 - d, 0.20                      (all its level faces)
# Run: runpy.run_path(D + 'p50_grid.py')['main']()  -> p50_grid.txt
import runpy

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
CB = [(-19.0, -77.0), (19.0, -74.5), (50.0, -67.0), (-50.0, -67.0), (64.0, -45.0), (-72.0, -38.0), (51.0, -14.0), (-51.0, -14.0)]
BOSS = [(-19.0, -77.0), (19.0, -74.5), (50.0, -67.0), (-50.0, -67.0)]


def off(h, first, lh):
    if abs(h) < 1e-6 or abs(h - first) < 1e-4:
        return 0.0
    q = (h - first) / lh
    return (q - round(q)) * lh


def world(k, X, name, boxes, bed, first, lh):
    b = X.body(name)
    rows = []
    for f in b.faces:
        if f.geometry.surfaceType != 0:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
        n = k.wv(nv); p = k.W(f.pointOnFace)
        if abs(abs(n[2]) - 1) > 1e-4:
            continue
        if not any(q[0] <= p[0] <= q[1] and q[2] <= p[1] <= q[3] and q[4] <= p[2] <= q[5] for q in boxes):
            continue
        h = p[2] - bed
        rows.append((round(p[2], 3), 'up' if n[2] > 0 else 'down', round(f.area * 100, 2), round(off(h, first, lh), 4), k.r2(p)))
    print('%s (bed %.2f, first %.2f, then %.2f): %d level faces in the places changed' % (name, bed, first, lh, len(rows)))
    for r in sorted(rows):
        print('   z %8.3f %-4s %8.2f mm2  off the grid %+.4f  at %s' % r)


def slabframe(k, X, name, h_of_d, first, lh):
    b = X.body(name)
    rows = []
    for f in b.faces:
        if f.geometry.surfaceType != 0:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
        if abs(abs(nv.y) - 1) > 1e-4:
            continue
        p = k.Sf(f.pointOnFace)
        h = h_of_d(p[1])
        rows.append((round(p[1], 3), round(h, 3), round(f.area * 100, 2), round(off(h, first, lh), 4)))
    print('%s: level faces in its print (d, height, mm2, off the grid):' % name)
    for r in sorted(rows):
        print('   d %7.3f  height %7.3f  %9.2f  %+.4f' % r)


def _main():
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    world(k, X, 'FLOOR_PLATE', [(x - 4, x + 4, y - 4, y + 4, -0.1, 3.0) for (x, y) in CB] + [(1.0, 13.0, -82.0, -70.0, 8.0, 13.5)], 0.0, 0.2, 0.2)
    world(k, X, 'HOUSING_F_door', [(x - 7, x + 7, y - 9, y + 9, 9.0, 11.5) for (x, y) in BOSS] + [(4.0, 13.0, -82.0, -76.4, 3.0, 10.5)], 2.8, 0.2, 0.2)
    world(k, X, 'GROMMET_usbc_F', [(-4.0, 12.5, -80.0, -76.0, 9.9, 12.0)], 10.0, 0.2, 0.12)
    slabframe(k, X, 'SLAB_frame', lambda d: d, 0.1, 0.1)
    slabframe(k, X, 'HOUSING_F_plate', lambda d: 12.8 - d, 0.2, 0.2)
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p50_grid.txt', _main)
