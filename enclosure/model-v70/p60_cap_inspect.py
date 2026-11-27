# Block 6 (brief claude/brief-enclosure-audit-fixes-rest-2026-11-25.md): the cap and the clamps as they stand at version 74.
# READ-ONLY (temporary bodies only). Lists planar and cylindrical faces of MIC_CLAMP_L / _R and of HOUSING_F_cap round the left
# strip, the world boxes of the strip envelopes, the keep-outs behind the strips, the VEML board and the microphone leads, and the
# cylinders of the cap's pegs and the clamp's slot. Run: runpy.run_path(D + 'p60_cap_inspect.py')['main'](stage) -> p60_<stage>.txt
import runpy, json

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def clamp(k, X):
    for n in ('MIC_CLAMP_L', 'MIC_CLAMP_R'):
        b = X.body(n)
        print('%s world box %s, faces %d, volume %.3f' % (n, k.wbb(X, b), b.faces.count, b.volume * 1000))
        for r in sorted(k.faces(X, b, (-200, 200, -200, 200, -10, 400), amin=0.05), key=lambda r: (r[0], str(r[1]))):
            print('   ', r)


def cap(k, X):
    b = X.body('HOUSING_F_cap')
    print('cap world box %s, faces %d' % (k.wbb(X, b), b.faces.count))
    rows = k.faces(X, b, (-1, 45, -45, -15, 170, 182), amin=0.05)
    for r in sorted(rows, key=lambda r: (r[0], str(r[1]), r[2][2] if r[0] == 'p' else 0)):
        print('   ', r)


def capz(k, X):
    b = X.body('HOUSING_F_cap'); zs = {}
    for f in b.faces:
        if f.geometry.surfaceType != k.PLN:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); n = k.wv(nv)
        if abs(abs(n[2]) - 1) < 1e-4:
            z = round(k.W(f.pointOnFace)[2], 4); key = (z, int(round(n[2])))
            zs.setdefault(key, [0.0, 0]); zs[key][0] += f.area * 100; zs[key][1] += 1
    print('cap level faces (world z, normal z): area mm2, count')
    for (z, s), (a, c) in sorted(zs.items()):
        print('   z %9.4f n %+d  %9.2f mm2  %3d faces   cap bed height (top face down) from z 180.0: %.4f' % (z, s, a, c, 180.0 - z))


def envs(k, X):
    for n in ('MIC_strip_L_env', 'MIC_strip_R_env', 'MIC_strip_L_env_v69', 'KO_mic_L_back', 'KO_mic_R_back', 'VEML_env', 'LEAD_MIC_L',
              'LEAD_MIC_R', 'FOAM_mic_L_env', 'FOAM_mic_R_env'):
        b = X.body(n)
        if b is None:
            print('%s: none' % n); continue
        print('%s world box %s vol %.3f faces %d visible %s' % (n, k.wbb(X, b), b.volume * 1000, b.faces.count, b.isLightBulbOn))
    print([n for n in X.names() if 'MIC' in n.upper() or 'GASK' in n.upper() or 'FOAM' in n.upper()])


def holes(k, X):
    for n in ('HOUSING_F_cap', 'MIC_CLAMP_L', 'MIC_CLAMP_R'):
        for r in k.holes_of(X.body(n), rmin=0.5, rmax=4.0):
            if n != 'HOUSING_F_cap' or (r['A'][2] > 170):
                print(n, r)


def _main(stage):
    k = L['load'](); X = k.K(); k.budget(75)
    print(L['stamp'](), 'before', X.state())
    {'clamp': clamp, 'cap': cap, 'capz': capz, 'envs': envs, 'holes': holes}[stage](k, X)
    print(L['stamp'](), 'after', X.state())


def main(stage):
    L['out']('p60_%s.txt' % stage, _main, stage)
