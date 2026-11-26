# Block 6: faces of HOUSING_F_cap in the left strip's pocket and round the left peg and boss (READ-ONLY).
# Run: runpy.run_path(D + 'p61_cap_faces.py')['main']() -> p61_cap_faces.txt
import runpy

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def _main():
    k = L['load'](); X = k.K(); k.budget(75)
    print(L['stamp'](), 'before', X.state())
    b = X.body('HOUSING_F_cap')
    print('-- pocket and pads, x 5..40, y -32..-21, z 176..179.5')
    for r in sorted(k.faces(X, b, (5, 40, -32, -21, 176, 179.5), kinds=('p', 'c'), amin=0.01), key=lambda r: (r[0], str(r[1]))):
        print('   ', r)
    print('-- peg and boss, x 12..37, y -40..-29, z 174..178')
    for r in sorted(k.faces(X, b, (12, 37, -40, -29, 174, 178), kinds=('p', 'c'), amin=0.01), key=lambda r: (r[0], str(r[1]))):
        print('   ', r)
    print('-- other surface types near the peg (cones):')
    for f in b.faces:
        p = k.W(f.pointOnFace)
        if 28 < p[0] < 37 and -38 < p[1] < -29 and 175 < p[2] < 178 and f.geometry.surfaceType not in (k.PLN, k.CYL):
            print('    type %d at %s area %.3f' % (f.geometry.surfaceType, k.r2(p, 3), f.area * 100))
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p61_cap_faces.txt', _main)
