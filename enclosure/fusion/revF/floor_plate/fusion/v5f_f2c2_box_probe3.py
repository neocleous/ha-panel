# rev F f2c2 (2026-11-10): read-only probe 3 - where the inner planes of the two speaker boxes are (notches, shelves, hump).
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
MAIN = {'L': ('x+47.50', 'x-46.00', 'y+-3.70', 'y--5.70', 'y+-50.50', 'y--52.00', 'z+5.20', 'z-3.70', 'z+76.00', 'z-74.50', 'y+-3.00', 'y+-0.20'),
        'R': ('x--47.50', 'x+-46.00', 'y+-3.70', 'y--5.70', 'y+-50.50', 'y--52.00', 'z+5.20', 'z-3.70', 'z-74.50', 'y+-3.00', 'y+-0.20')}


def wv(v):
    return (v.x, v.y * C - v.z * S, v.y * S + v.z * C)


def run(_context):
    st = {}
    try:
        X = K()
        for side in 'LR':
            b = X.body('SPKBOX_' + side); out = {}
            for f in b.faces:
                g = f.geometry
                if g.surfaceType != adsk.core.SurfaceTypes.PlaneSurfaceType:
                    continue
                ok, n = f.evaluator.getNormalAtPoint(f.pointOnFace); n = wv(n); p = W(f.pointOnFace)
                for i, ax in enumerate('xyz'):
                    if abs(n[i]) > 0.9995:
                        k = '%s%s%.2f' % (ax, '+' if n[i] > 0 else '-', p[i]); break
                else:
                    continue
                vs = [W(v.geometry) for v in f.vertices]
                if k in MAIN[side] or f.area * 100 < 5 or not vs:
                    continue
                bb = [round(fn(v[j] for v in vs), 1) for j in range(3) for fn in (min, max)]
                bb = [bb[q] for q in range(6) if q // 2 != 'xyz'.index(k[0])]
                e = out.setdefault(k, bb)
                for q in range(0, 4, 2):
                    e[q] = min(e[q], bb[q]); e[q + 1] = max(e[q + 1], bb[q + 1])
            st[side] = ' '.join('%s[%s]' % (k, ','.join('%g' % q for q in v)) for k, v in sorted(out.items()))
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    status('f2c2', st)


run(None)
