# Block 0, preflight: the document's state, the counts and the 17 guard volumes by both readings against version 88's table.
# READ-ONLY: nothing is created in the document. After ../model-v85/m01_preflight.py.
# Run: L.checked('s01_preflight.py', sha)['main'](tag)  -> s01_preflight_<tag>.txt, .json
import runpy, re
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/screw_margins_v88/'
L = runpy.run_path(D + 's00_lib.py')


def kind(n):
    if n in L['PRINTED']:
        return 'printed'
    if n.startswith('LEAD_'):
        return 'lead'
    if n.startswith('KO_'):
        return 'keep-out'
    return 'bought or envelope'


def _main(tag, guard=None):
    k = L['load'](); X = k.K()
    app = adsk.core.Application.get()
    G = guard or L['GUARD88']
    print('read at', L['stamp']())
    print('open documents: %s' % [(d.name, d.isModified, d == app.activeDocument) for d in app.documents])
    df = X.doc.dataFile; st = X.state()
    print('document %r, version %d of %d, modified %s' % (X.doc.name, df.versionNumber, df.latestVersionNumber, X.doc.isModified))
    print('version description: %r' % df.description)
    names = X.names(); cur = k.current(X, leads=True)
    kinds = {}
    for b in cur:
        kinds.setdefault(kind(b.name), []).append(b.name)
    hidden = sorted(n for n in names if re.search(r'_v\d+$', n))
    by = {}
    for n in hidden:
        by.setdefault(n.rsplit('_v', 1)[1], []).append(n)
    print('bodies %d, visible %d, in the unit %d (%s)' % (st['bodies'], st['visible'], len(cur), ', '.join('%s %d' % (q, len(v)) for q, v in sorted(kinds.items()))))
    print('hidden copies by version: ' + ', '.join('_v%s %d' % (q, len(v)) for q, v in sorted(by.items())))
    print('_v85 copies: %s' % by.get('85'))
    print('_v88 copies: %s' % by.get('88'))
    print('TMP_ %d; templates %s; duplicate names %s' % (sum(1 for n in names if n.startswith('TMP_')), st['templates'], st['dups']))
    bad = []
    print('%-16s %13s %13s | %13s %13s | %8s %8s  lumps faces' % ('body', 'preflight', 'very high', 'table prefl.', 'table v.high', 'diff', 'diff'))
    vols = {}
    for n in L['PRINTED']:
        b = X.body(n); vp = b.volume * 1000.0; vh = L['vhi'](b); rp, rh = G[n]
        ok = abs(vp - rp) < 0.0015 and abs(vh - rh) < 0.0015
        if not ok:
            bad.append(n)
        vols[n] = (round(vp, 3), round(vh, 3), b.lumps.count, b.faces.count)
        print('%-16s %13.3f %13.3f | %13.3f %13.3f | %+8.3f %+8.3f  %d %d%s' % (n, vp, vh, rp, rh, vp - rp, vh - rh, b.lumps.count, b.faces.count, '' if ok else '   DIFFERS'))
    print('guard volumes that differ from the table: %d of %d %s' % (len(bad), len(L['PRINTED']), bad))
    sc = X.body('SCREWS_M2x6_env')
    print('not guarded: SCREWS_M2x6_env %.3f, lumps %d' % (sc.volume * 1000.0, sc.lumps.count))
    L['jdump']('s01_preflight_%s.json' % tag, {'state': st, 'version': df.versionNumber, 'unit': {q: sorted(v) for q, v in kinds.items()}, 'hidden': hidden,
                                               'vols': vols, 'all': names})


def main(tag='v88', guard=None):
    L['out']('s01_preflight_%s.txt' % tag, _main, tag, guard)
# END
