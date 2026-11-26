# Puts temporary bodies into the model (blocks 5 on). CHANGES THE DOCUMENT: each named body replaced by the temporary body in
# k.c[key] (same name, appearance, material and visibility; the old body deleted: its hidden copy <name>_v69 was made in
# block 0, p03_backups). Then the volumes two ways (D425): the preflight's (BRepBody.volume) and at very high accuracy, beside
# the _v69 copy's. Library caches of the bodies are dropped.
# Run: runpy.run_path(D + 'p57_replace.py')['main']([('HOUSING_F_front', 'b5_shell')], 'b5')  -> p57_replace_<tag>.txt
import runpy
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def vhi(b):
    return b.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume * 1000.0


def _main(pairs):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    for name, key in pairs:
        if k.c.get(key) is None:
            raise RuntimeError('missing ' + key)
        if X.body(name + '_v69') is None:
            raise RuntimeError('no copy ' + name + '_v69')
    for name, key in pairs:
        old = X.body(name)
        was = (old.volume * 1000.0, vhi(old))
        vis = old.isLightBulbOn
        nb = X.add(X.tbm.copy(k.c[key]), name + '_new', like=old, show=vis)
        old.deleteMe()
        nb.name = name
        print('%-16s was %12.3f (prefl.) %12.3f (v.high) | now %12.3f %12.3f | _v69 %12.3f | lumps %d faces %d visible %s' % (
            name, was[0], was[1], nb.volume * 1000.0, vhi(nb), vhi(X.body(name + '_v69')), nb.lumps.count, nb.faces.count, vis))
    k.purge(tuple(n for n, q in pairs))
    print(L['stamp'](), 'after', X.state())


def main(pairs, tag):
    L['out']('p57_replace_%s.txt' % tag, _main, pairs)
