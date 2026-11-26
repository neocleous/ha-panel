# The 16 guard volumes read one way (D425, architect log 2026-11-24-d): the preflight's method (BRepBody.volume, as p01, the
# method the record's figures come from), each beside its figure at very high accuracy and beside version 69's record
# (claude/architect-log-2026-11-23.md section 4). Plus the counts. READ-ONLY.
# Also the slab's lower rim measured in its print layer (needles along Zd at d 9.1 / 10.5 / 11.95, x -90 / 0 / 90).
# Run: runpy.run_path(D + 'p51_guards.py')['main'](tag)  -> p51_guards_<tag>.txt and .json
import runpy, re
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def _main(tag):
    k = L['load'](); X = k.K()
    st = X.state()
    print(L['stamp'](), st)
    cur = k.current(X, leads=True)
    names = X.names()
    print('bodies %d, visible %d, in the unit %d, hidden _v67/_v68/_v69 copies %d, TMP_ %d' % (
        st['bodies'], st['visible'], len(cur), sum(1 for n in names if re.search(r'_v6[789]$', n)), sum(1 for n in names if n.startswith('TMP_'))))
    out = {}
    print('%-16s %13s %13s %13s %10s' % ('body', 'preflight', 'very high', 'record v69', 'pre - rec'))
    for n in L['PRINTED']:
        b = X.body(n)
        vp = b.volume * 1000.0
        vh = b.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume * 1000.0
        r = L['GUARD69'][n]
        out[n] = {'preflight': round(vp, 3), 'very_high': round(vh, 3), 'record_v69': r, 'lumps': b.lumps.count}
        print('%-16s %13.3f %13.3f %13.3f %+10.3f  lumps %d' % (n, vp, vh, r, vp - r, b.lumps.count))
    L['jdump']('p51_guards_%s.json' % tag, out)
    S = X.body('SLAB_frame')
    crop = X.dbox(-100, 100, 8.9, 12.1, -96, -88); X.sec(crop, X.tbm.copy(S))
    for d in (9.1, 10.5, 11.95):
        row = []
        for x in (-90.0, 0.0, 90.0):
            s = k.needle_t(X, [crop], k.W(k.Dp(x, d, -96.0)), k.W(k.Dp(x, d, -88.0)), 0.02)
            row.append(round(s[-1][1] - s[-1][0], 3) if s else None)
        print('slab lower rim at d %.2f, thickness along Zd at x -90/0/90: %s' % (d, row))


def main(tag):
    L['out']('p51_guards_%s.txt' % tag, _main, tag)
