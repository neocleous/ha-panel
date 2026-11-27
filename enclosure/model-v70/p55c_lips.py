# Block 5, AA-A19 / AA-C13 continued: the chin lips' rear faces (y 1.3, normal -y, about 14.6 mm2 each, x 84.25..92.25 and its
# mirror, z 5.0..8.97) lie at bed height 5.4992, a half layer (the shell's bed is y 6.7992), and carry a fit: the base plate's
# tongues come up behind them on the way down (the stop at 1.05 behind). Put on the grid on the side that opens the fit:
# y 1.4 (where they print today, PR14). Offset Face -0.1 on a hidden temporary copy of the model's shell.
# CHANGES NOTHING IN THE DOCUMENT except 'TMP_shell', deleted again. Result in k.c['b5_shell2'].
# Run: runpy.run_path(D + 'p55c_lips.py')['main']()  -> p55c_lips.txt
import runpy
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def _main():
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    S = X.body('HOUSING_F_front')
    tb = X.add(X.tbm.copy(S), 'TMP_shell', show=False)
    lips = []
    for f in tb.faces:
        if f.geometry.surfaceType != 0:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
        n = k.wv(nv); p = k.W(f.pointOnFace)
        if n[1] < -0.9999 and abs(p[1] - 1.3) < 0.002 and 80 < abs(p[0]) < 96 and 4 < p[2] < 10:
            lips.append(f)
    print('lips\' rear faces: %d, areas %s, at %s' % (len(lips), [round(f.area * 100, 2) for f in lips], [k.r2(k.W(f.pointOnFace)) for f in lips]))
    if len(lips) != 2:
        tb.deleteMe(); raise RuntimeError('lips')
    inp = X.root.features.offsetFacesFeatures.createInput(lips, adsk.core.ValueInput.createByReal(-0.01))
    X.root.features.offsetFacesFeatures.add(inp)
    tb = X.body('TMP_shell')
    k.c['b5_shell2'] = X.tbm.copy(tb)
    tb.deleteMe()
    print('done; lumps %d solid %s' % (k.c['b5_shell2'].lumps.count, k.c['b5_shell2'].isSolid))
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p55c_lips.txt', _main)
