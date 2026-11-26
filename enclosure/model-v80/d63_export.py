# The close: the saved version exported as a Fusion archive into ~/Documents, with its size and sha256.
# Refuses when the open document is modified, is not the version asked for, holds TMP_ or AUD_ bodies, or when the file is
# already there. The export does not change the document. Not a print file.
#   export(version, gname)   -> ~/Documents/HA Panel v5 - tapered revF-<gname>.f3d, and a line in d63_export.txt
#   sha(gname)               size and sha256 of the file again (read in pieces)
# Run: runpy.run_path(D + 'd63_export.py')['export'](85, 'g40')
import runpy, os, hashlib, time
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')
OUT = '/Users/danielneocleous/Documents/HA Panel v5 - tapered revF-%s.f3d'


def sha(gname):
    p = OUT % gname
    h = hashlib.sha256(); n = 0
    with open(p, 'rb') as f:
        while True:
            b = f.read(1 << 20)
            if not b:
                break
            h.update(b); n += len(b)
    line = '%s  %s: %d bytes (%.1f MB), sha256 %s' % (L['stamp'](), p, n, n / 1e6, h.hexdigest())
    open(D + 'd63_export.txt', 'a').write(line + '\n')
    print(line)


def export(version, gname):
    k = L['load'](); X = k.K()
    st = X.state(); p = OUT % gname
    if st['modified'] or st['version'] != version or st['latest'] != version:
        raise RuntimeError('not exported: the document is %s' % st)
    if any(n.startswith(('TMP_', 'AUD_')) for n in X.names()):
        raise RuntimeError('not exported: TMP_ or AUD_ bodies in the document')
    if os.path.exists(p):
        raise RuntimeError('not exported: the file is there already: ' + p)
    t0 = time.time()
    em = X.des.exportManager
    ok = em.execute(em.createFusionArchiveExportOptions(p))
    line = '%s  export of version %d (%s) -> %s: %s, %.1f s; after: %s' % (L['stamp'](), version, X.doc.dataFile.description[:60], p, ok, time.time() - t0, X.state())
    open(D + 'd63_export.txt', 'a').write(line + '\n')
    print(line)
    sha(gname)
# END
