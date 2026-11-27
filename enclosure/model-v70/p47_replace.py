# Block 4: puts p43b/p43c's and p46's bodies into the model. CHANGES THE DOCUMENT:
#   FLOOR_PLATE, HOUSING_F_door, GROMMET_usbc_F, SLAB_frame, HOUSING_F_plate replaced by k.c['b4_plate'], ['b4_door'],
#   ['b4_grommet'], ['b4_slab'], ['b4_screen'] (same name, appearance, material and visibility; the old body deleted: its hidden
#   copy <name>_v69 was made in block 0, p03_backups). Then each new body's volume two ways (D425): the preflight's way
#   (BRepBody.volume, the property the record's guard figures come from, p01) and at very high accuracy, beside its _v69 copy's.
# Run: runpy.run_path(D + 'p47_replace.py')['main']()  -> p47_replace.txt
import runpy
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
PAIRS = [('FLOOR_PLATE', 'b4_plate'), ('HOUSING_F_door', 'b4_door'), ('GROMMET_usbc_F', 'b4_grommet'), ('SLAB_frame', 'b4_slab'),
         ('HOUSING_F_plate', 'b4_screen')]


def vhi(b):
    return b.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume * 1000.0


def _main():
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    for name, key in PAIRS:
        if k.c.get(key) is None:
            raise RuntimeError('missing ' + key)
        if X.body(name + '_v69') is None:
            raise RuntimeError('no copy ' + name + '_v69')
    rows = []
    for name, key in PAIRS:
        old = X.body(name)
        was = (old.volume * 1000.0, vhi(old))
        vis = old.isLightBulbOn
        nb = X.add(X.tbm.copy(k.c[key]), name + '_new', like=old, show=vis)
        old.deleteMe()
        nb.name = name
        rows.append((name, was, nb.volume * 1000.0, vhi(nb), vhi(X.body(name + '_v69')), nb.lumps.count, nb.faces.count, vis))
    print('%-16s %12s %12s | %12s %12s | %12s  lumps faces visible' % ('body', 'was (prefl.)', 'was (v.high)', 'now (prefl.)', 'now (v.high)', '_v69 (v.high)'))
    for (name, was, vp, vh, v69, nl, nf, vis) in rows:
        print('%-16s %12.3f %12.3f | %12.3f %12.3f | %12.3f  %d %d %s' % (name, was[0], was[1], vp, vh, v69, nl, nf, vis))
    k.purge(tuple(n for n, q in PAIRS))
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p47_replace.txt', _main)
