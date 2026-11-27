# Block 0, preflight: the document's state, the counts and the 17 guard volumes by both readings against the brief's table
# for version 85. READ-ONLY: nothing is created in the document.
# Run: L.checked('m01_preflight.py', sha)['main']()  -> m01_preflight.txt
import runpy, re
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/box_margins_v85/'
L = runpy.run_path(D + 'm00_lib.py')


def kind(n):
    if n in L['PRINTED']:
        return 'printed'
    if n.startswith('LEAD_'):
        return 'lead'
    if n.startswith('KO_'):
        return 'keep-out'
    return 'bought or envelope'


def _main():
    k = L['load'](); X = k.K()
    app = adsk.core.Application.get()
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
    print('_v79 copies: %s' % by.get('79'))
    print('_v85 copies: %s' % by.get('85'))
    print('TMP_ %d; templates %s; duplicate names %s' % (sum(1 for n in names if n.startswith('TMP_')), st['templates'], st['dups']))
    bad = 0
    print('%-16s %13s %13s | %13s %13s | %8s %8s  lumps' % ('body', 'preflight', 'very high', 'brief prefl.', 'brief v.high', 'diff', 'diff'))
    for n in L['PRINTED']:
        b = X.body(n); vp = b.volume * 1000.0; vh = L['vhi'](b); rp, rh = L['GUARD85'][n]
        ok = abs(vp - rp) < 0.0015 and abs(vh - rh) < 0.0015
        bad += 0 if ok else 1
        print('%-16s %13.3f %13.3f | %13.3f %13.3f | %+8.3f %+8.3f  %d%s' % (n, vp, vh, rp, rh, vp - rp, vh - rh, b.lumps.count, '' if ok else '   DIFFERS'))
    print('guard volumes that differ from the brief: %d of %d' % (bad, len(L['PRINTED'])))
    L['jdump']('m01_preflight.json', {'state': st, 'version': df.versionNumber, 'unit': {q: sorted(v) for q, v in kinds.items()}, 'hidden': hidden, 'all': names})


def main():
    L['out']('m01_preflight.txt', _main)
# END
