# Block 9: puts the temporary bodies into the model. CHANGES THE DOCUMENT.
#   SPKBOX_L, LD2410C_env_F, SCREWS_M2x6_env, LEAD_RADAR: replaced by k.c['b9_boxL' / 'b9_radar' / 'b9_screws' / 'b9_lead'], as
#       p57_replace does it (same name, appearance, material and visibility; the old body deleted, its hidden _v69 copy stays)
#   RADAR_HOLDER: a new body, the unit's 17th printed part, from k.c['b9_holder'], shown, with the left touch clip's appearance
#       and material. If a RADAR_HOLDER is already there (a second put after a change) it is replaced.
# Then the volumes two ways (D425). Run: runpy.run_path(D + 'p88_b9_put.py')['main'](tag)  -> p88_put_<tag>.txt
import runpy
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
PAIRS = [('SPKBOX_L', 'b9_boxL'), ('LD2410C_env_F', 'b9_radar'), ('SCREWS_M2x6_env', 'b9_screws'), ('LEAD_RADAR', 'b9_lead')]


def vhi(b):
    return b.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume * 1000.0


def _main(which):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    pairs = [p for p in PAIRS if which is None or p[0] in which]
    for name, key in pairs + ([('RADAR_HOLDER', 'b9_holder')] if which is None or 'RADAR_HOLDER' in which else []):
        if k.c.get(key) is None:
            raise RuntimeError('missing ' + key)
    for name, key in pairs:
        if X.body(name + '_v69') is None:
            raise RuntimeError('no copy ' + name + '_v69')
    for name, key in pairs:
        old = X.body(name)
        was = (old.volume * 1000.0, vhi(old)); vis = old.isLightBulbOn
        nb = X.add(X.tbm.copy(k.c[key]), name + '_new', like=old, show=vis)
        old.deleteMe(); nb.name = name
        print('%-16s was %12.3f (prefl.) %12.3f (v.high) | now %12.3f %12.3f | _v69 %12.3f | lumps %d faces %d visible %s' % (
            name, was[0], was[1], nb.volume * 1000.0, vhi(nb), vhi(X.body(name + '_v69')), nb.lumps.count, nb.faces.count, vis))
    if which is None or 'RADAR_HOLDER' in which:
        old = X.body('RADAR_HOLDER')
        like = old if old is not None else X.body('TOUCH_CLIP_L')
        nb = X.add(X.tbm.copy(k.c['b9_holder']), 'RADAR_HOLDER_new', like=like, show=True)
        if old is not None:
            print('RADAR_HOLDER was %12.3f %12.3f, replaced' % (old.volume * 1000.0, vhi(old)))
            old.deleteMe()
        nb.name = 'RADAR_HOLDER'
        print('%-16s new body | now %12.3f (prefl.) %12.3f (v.high) | lumps %d faces %d visible %s' % ('RADAR_HOLDER', nb.volume * 1000.0, vhi(nb), nb.lumps.count, nb.faces.count, nb.isLightBulbOn))
    k.purge(tuple(n for n, q in PAIRS) + ('RADAR_HOLDER',))
    print(L['stamp'](), 'after', X.state())
    print('in the unit: %d bodies' % len(k.current(X, leads=True)))


def main(tag, which=None):
    L['out']('p88_put_%s.txt' % tag, _main, which)
