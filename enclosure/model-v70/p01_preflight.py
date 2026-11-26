# Block 0, preflight: the document's state, the counts and the 16 guard volumes, against version 69's record
# (claude/architect-log-2026-11-23.md section 4). READ-ONLY: nothing is created in the document.
# Run: runpy.run_path(D + 'p01_preflight.py')['main']()  -> p01_preflight.txt and p01_preflight.json in this folder.
import sys, runpy, re
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def body_kind(n):
    if n in L['PRINTED']:
        return 'printed'
    if n.startswith('LEAD_'):
        return 'lead'
    if n.startswith('KO_'):
        return 'keep-out'
    return 'bought or envelope'


def _main():
    k = L['load']()
    X = k.K()
    st = X.state()
    df = X.doc.dataFile
    print('read at', L['stamp']())
    print('document %r, version %d of %d, modified %s' % (X.doc.name, df.versionNumber, df.latestVersionNumber, X.doc.isModified))
    try:
        print('version description: %r' % df.description)
    except Exception as e:
        print('version description: not read (%s)' % e)
    names = X.names()
    print('bodies %d, visible %d, AUD_/NEW_/RENDER_TMP %s, duplicate names %s' % (st['bodies'], st['visible'], st['templates'], st['dups']))
    cur = k.current(X, leads=True)
    kinds = {}
    for b in cur:
        kinds.setdefault(body_kind(b.name), []).append(b.name)
    print('in the unit %d: ' % len(cur) + ', '.join('%s %d' % (q, len(v)) for q, v in sorted(kinds.items())))
    backups = sorted(n for n in names if re.search(r'_v6[789]$', n))
    print('hidden backups (_v67/_v68/_v69): %d: %s' % (len(backups), ', '.join(backups)))
    g = {}
    print('guard volumes, mm3 (record = version 69, architect log 2026-11-23 section 4):')
    for n in L['PRINTED']:
        b = X.body(n)
        v = round(b.volume * 1000.0, 3)
        d = v - L['GUARD69'][n]
        g[n] = {'volume': v, 'lumps': b.lumps.count, 'record': L['GUARD69'][n], 'diff': round(d, 3), 'visible': b.isLightBulbOn}
        print('  %-16s %12.3f  lumps %d  record %12.3f  diff %+.3f' % (n, v, b.lumps.count, L['GUARD69'][n], d))
    L['jdump']('p01_preflight.json', {'state': st, 'version': df.versionNumber, 'latest': df.latestVersionNumber,
                                       'unit': {q: sorted(v) for q, v in kinds.items()}, 'backups': backups, 'guards': g,
                                       'all_bodies': names})


def main():
    L['out']('p01_preflight.txt', _main)
