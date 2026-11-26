# Block 9: the radar's lead laid on candidate routes, each a chain of Ø2.6 pieces from the radar's pins to J5's end; for each:
# its length along the axis and the volume it shares with every body of the unit (the old lead and the radar excluded).
# READ-ONLY (temporary bodies only). Run: runpy.run_path(D + 'p84_b9_lead.py')['main'](routes)  -> p84_b9_lead.txt
import runpy, math
D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
R = 1.3


def chain(k, X, pts):
    t = None; n = 0.0
    for a, b in zip(pts[:-1], pts[1:]):
        c = X.cyl(a, b, R); t = c if t is None else X.uni(t, c)
        n += math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))
    for p in pts[1:-1]:
        X.uni(t, X.sph(p, R))
    return t, n


def _main(routes):
    k = L['load'](); X = k.K(); k.budget(78)
    print(L['stamp'](), 'before', X.state())
    others = [b for b in k.current(X, leads=True) if b.name not in ('LEAD_RADAR', 'LD2410C_env_F')]
    if 'b9_holder' in k.c:
        others = others + [('RADAR_HOLDER', k.c['b9_holder'])]
    for tag, pts in routes:
        t, n = chain(k, X, pts)
        rows = []
        for o in others:
            nm, b = (o if isinstance(o, tuple) else (o.name, o))
            if not t.boundingBox.intersects(b.boundingBox):
                continue
            v = X.xv(t, b if isinstance(o, tuple) else X.tbm.copy(b))
            if v > 0.0005:
                rows.append((round(v, 3), nm))
        print('%s: %.1f along the axis; shares: %s' % (tag, n, sorted(rows, reverse=True)))
        k.c['b9_lead_' + tag] = t; k.c['b9_lead_len_' + tag] = n
    print(L['stamp'](), 'after', X.state())


def main(routes):
    L['out']('p84_b9_lead.txt', _main, routes)
