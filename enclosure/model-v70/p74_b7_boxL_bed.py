# Block 7: does the left box's added pocket-wall block (world x 55.65..57.15, y -37.5..-35.95, z 9.7..20.7) stand on the box's
# print bed (rear face down)? Finds the rear face (largest plane facing rearward), then the block's corners' heights above it.
# READ-ONLY.  Run: runpy.run_path(D + 'p74_b7_boxL_bed.py')['main']()  -> p74_boxL_bed.txt
import runpy
D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def _main():
    k = L['load'](); X = k.K(); k.budget(60)
    print(L['stamp'](), 'before', X.state())
    B = X.body('SPKBOX_L')
    best = None
    for f in B.faces:
        if f.geometry.surfaceType != k.PLN:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); n = k.unit(k.wv(nv)); p = k.W(f.pointOnFace)
        if f.area * 100 > 300:
            print('plane %.1f mm2 normal %s at %s' % (f.area * 100, k.r2(n), k.r2(p)))
        if n[1] < -0.9 and (best is None or f.area > best[0].area):
            best = (f, n, p)
    f, n, p = best
    print('bed face: %.1f mm2, normal %s, at %s' % (f.area * 100, k.r2(n), k.r2(p)))
    def h(q):
        return sum((q[i] - p[i]) * -n[i] for i in range(3))
    for x in (55.65, 57.15):
        for y in (-37.5, -35.95):
            for z in (9.7, 20.7):
                print('block corner (%.2f, %.2f, %.1f): %.3f above the bed' % (x, y, z, h((x, y, z))))
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p74_boxL_bed.txt', _main)
