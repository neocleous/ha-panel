# Part A of log 2026-11-25-b (block 7b): inspection. READ-ONLY.
#  - the left clamp's level faces (z, area, centroid);  - the cap's level faces round the left strip pocket;
#  - needles along z through the cap and the shell at the lip over the shell's shelf; - VEML_env's box.
# Run: runpy.run_path(D + 'p78_7b_probe.py')['main']()  -> p78_7b_probe.txt
import runpy
D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def lev(k, X, b, box=None):
    rows = []
    for f in b.faces:
        if f.geometry.surfaceType != k.PLN:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); n = k.wv(nv)
        if abs(n[2]) < 0.99:
            continue
        c = k.W(f.centroid)
        if box and not all(box[2 * i] <= c[i] <= box[2 * i + 1] for i in range(3)):
            continue
        rows.append((round(c[2], 3), '+z' if n[2] > 0 else '-z', round(f.area * 100, 2), k.r2(c)))
    for r in sorted(rows):
        print('   z %.3f %s %8.2f mm2 at %s' % r)


def _main():
    k = L['load'](); X = k.K(); k.budget(70)
    print(L['stamp'](), 'before', X.state())
    print('MIC_CLAMP_L level faces:'); lev(k, X, X.body('MIC_CLAMP_L'))
    print('HOUSING_F_cap level faces, x 0..40, y -40..-20, z 170..180:'); lev(k, X, X.body('HOUSING_F_cap'), (0, 40, -40, -20, 170, 180))
    print('VEML_env world box', [round(v, 2) for v in k.wbb(X, X.body('VEML_env'))])
    cap = X.tbm.copy(X.body('HOUSING_F_cap')); sh = X.tbm.copy(X.body('HOUSING_F_front'))
    for x in (-60.0, -40.0, 0.0, 40.0, 60.0):
        for y in (-24.0, -23.6, -23.4, -23.2, -23.0, -22.8, -22.6, -22.4, -22.2):
            a = [(round(175 + p, 3), round(175 + q, 3)) for p, q in k.needle_t(X, [cap], (x, y, 175.0), (x, y, 181.0), 0.01)]
            b = [(round(175 + p, 3), round(175 + q, 3)) for p, q in k.needle_t(X, [sh], (x, y, 175.0), (x, y, 181.0), 0.01)]
            print('x %+.0f y %.1f: cap %s | shell %s' % (x, y, a, b))
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p78_7b_probe.txt', _main)
