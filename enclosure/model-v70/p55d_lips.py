# Block 5, AA-A19 / AA-C13 continued, corrected: p55c took the faces at y 1.3 beside the lower outer driver heads (x +-88), not
# the chin lips; its result (k.c['b5_shell2']) is not used. The tongue stop on the way down is at the chin lips over the base
# plate's noses: x +-24.5..35.5, y 1.3, z 3.2..4.05 (p52_where_b5lip.txt). Their rear faces (normal -y, y 1.3: bed height
# 5.4992, a half layer) carry that fit: put on the grid on the side that opens it, y 1.4 (where they print today, PR14).
# Offset Face -0.1 on a hidden temporary copy of the model's shell. CHANGES NOTHING IN THE DOCUMENT except 'TMP_shell',
# deleted again. Result in k.c['b5_shell3'].
# Run: runpy.run_path(D + 'p55d_lips.py')['main']()  -> p55d_lips.txt
import runpy
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def _main():
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    k.c.pop('b5_shell2', None)
    S = X.body('HOUSING_F_front')
    tb = X.add(X.tbm.copy(S), 'TMP_shell', show=False)
    lips = []
    for f in tb.faces:
        if f.geometry.surfaceType != 0:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
        n = k.wv(nv); p = k.W(f.pointOnFace)
        ws = [k.W(v.geometry) for v in f.vertices]
        if n[1] < -0.9999 and abs(p[1] - 1.3) < 0.002 and 15 < abs(p[0]) < 45 and 2 < p[2] < 7:
            lips.append(f)
            print('   face %.2f mm2 at %s, x %.2f..%.2f z %.2f..%.2f' % (f.area * 100, k.r2(p), min(w[0] for w in ws), max(w[0] for w in ws),
                                                                  min(w[2] for w in ws), max(w[2] for w in ws)))
    if len(lips) != 2:
        tb.deleteMe(); raise RuntimeError('lips: %d' % len(lips))
    inp = X.root.features.offsetFacesFeatures.createInput(lips, adsk.core.ValueInput.createByReal(-0.01))
    X.root.features.offsetFacesFeatures.add(inp)
    tb = X.body('TMP_shell')
    k.c['b5_shell3'] = X.tbm.copy(tb)
    tb.deleteMe()
    print('done; lumps %d solid %s' % (k.c['b5_shell3'].lumps.count, k.c['b5_shell3'].isSolid))
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p55d_lips.txt', _main)
