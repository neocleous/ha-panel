# Block 1, read-only: candidate joint bosses, screw heads and box-tab extensions against the bodies of the unit (no model change).
import adsk.core, adsk.fusion, sys, time, json


def run(_context):
    t0 = time.time()
    k = sys.modules['v5f_k']; X = k.K(); k.budget(55)
    cur = [b for b in k.current(X, leads=True) if b.name != 'HOUSING_F_front' and not b.name.startswith('KO_')]
    kos = [b for b in k.current(X, leads=True) if b.name.startswith('KO_')]
    out = {}
    # four joint bosses, axis along the screen normal, land at d 12.8 (thin plate) - candidate places (x, up)
    for tag, (x, up) in {'TL': (70.0, 27.0), 'TR': (-70.0, 27.0), 'BL': (85.0, -82.0), 'BR': (-85.0, -82.0)}.items():
        boss = X.cyld(x, up, 4.0, 13.1, 19.4)                      # 0.3 behind the plate's back
        head = X.cyld(x, up, 2.85, 7.35, 9.0)                      # button head in front of the plate
        r = {'boss': {}, 'head': {}}
        for b in cur:
            for key, tb in (('boss', boss), ('head', head)):
                if not tb.boundingBox.intersects(b.boundingBox):
                    continue
                v = X.xv(tb, b)
                if abs(v) > 0.005:
                    r[key][b.name] = round(v, 2)
        for b in kos:
            if boss.boundingBox.intersects(b.boundingBox):
                v = X.xv(boss, b)
                if abs(v) > 0.005:
                    r['boss']['KO:' + b.name] = round(v, 2)
        out[tag] = r
        if k.late():
            break
    # box-tab extension regions (world boxes) in front of each box top
    for tag, (x0, x1) in {'tabL': (54.6, 62.6), 'tabR': (-62.6, -54.6)}.items():
        tb = X.wbox(x0, x1, -3.7, -0.8, 76.0, 84.0)
        X.uni(tb, X.wbox(x0, x1, -0.8, 0.9, 76.0, 80.0))
        r = {}
        for b in cur + kos:
            if b.name.startswith('SPKBOX'):
                continue
            if tb.boundingBox.intersects(b.boundingBox):
                v = X.xv(tb, b)
                if abs(v) > 0.005:
                    r[b.name] = round(v, 2)
        out[tag] = r
    print(json.dumps({'t': round(time.time() - t0, 1), 'res': out}))
