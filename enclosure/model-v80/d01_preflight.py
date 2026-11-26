# Block 0, preflight: the document's state, the counts and the 17 guard volumes by both readings (D425), against the
# brief's table for version 79. READ-ONLY: nothing is created in the document.
# Run: runpy.run_path(D + 'd01_preflight.py')['main'](tag)  -> d01_preflight_<tag>.txt and .json in this pass's folder.
import runpy, re
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')


def kind(n):
    if n in L['PRINTED']:
        return 'printed'
    if n.startswith('LEAD_'):
        return 'lead'
    if n.startswith('KO_'):
        return 'keep-out'
    return 'bought or envelope'


def _main(tag):
    k = L['load'](); X = k.K()
    df = X.doc.dataFile
    st = X.state()
    print('read at', L['stamp']())
    print('document %r, version %d of %d, modified %s' % (X.doc.name, df.versionNumber, df.latestVersionNumber, X.doc.isModified))
    print('version description: %r' % df.description)
    try:
        print('design type: %s (0 = direct, 1 = parametric)' % X.des.designType)
    except Exception as e:
        print('design type not read: %s' % e)
    names = X.names()
    cur = k.current(X, leads=True)
    kinds = {}
    for b in cur:
        kinds.setdefault(kind(b.name), []).append(b.name)
    hidden = sorted(n for n in names if re.search(r'_v\d+$', n))
    print('bodies %d, visible %d, in the unit %d (%s)' % (st['bodies'], st['visible'], len(cur),
          ', '.join('%s %d' % (q, len(v)) for q, v in sorted(kinds.items()))))
    print('hidden copies (_vNN) %d; TMP_ %d; AUD_/NEW_/RENDER_TMP %s; duplicate names %s' % (
        len(hidden), sum(1 for n in names if n.startswith('TMP_')), st['templates'], st['dups']))
    by = {}
    for n in hidden:
        by.setdefault(n.rsplit('_v', 1)[1], []).append(n)
    print('hidden copies by version: ' + ', '.join('_v%s %d' % (q, len(v)) for q, v in sorted(by.items())))
    g = {}; bad = 0
    print('%-16s %13s %13s | %13s %13s | %8s %8s  lumps' % ('body', 'preflight', 'very high', 'brief prefl.', 'brief v.high', 'diff', 'diff'))
    for n in L['PRINTED']:
        b = X.body(n)
        vp = b.volume * 1000.0; vh = L['vhi'](b)
        rp, rh = L['GUARD79'][n]
        g[n] = {'preflight': round(vp, 3), 'very_high': round(vh, 3), 'brief': (rp, rh), 'lumps': b.lumps.count, 'visible': b.isLightBulbOn}
        ok = abs(vp - rp) < 0.0015 and abs(vh - rh) < 0.0015
        bad += 0 if ok else 1
        print('%-16s %13.3f %13.3f | %13.3f %13.3f | %+8.3f %+8.3f  %d%s' % (n, vp, vh, rp, rh, vp - rp, vh - rh, b.lumps.count, '' if ok else '   DIFFERS'))
    print('guard volumes that differ from the brief: %d of %d' % (bad, len(L['PRINTED'])))
    L['jdump']('d01_preflight_%s.json' % tag, {'state': st, 'version': df.versionNumber, 'latest': df.latestVersionNumber,
                                               'unit': {q: sorted(v) for q, v in kinds.items()}, 'hidden': hidden, 'guards': g, 'all_bodies': names})


def main(tag='v79'):
    L['out']('d01_preflight_%s.txt' % tag, _main, tag)
# END
