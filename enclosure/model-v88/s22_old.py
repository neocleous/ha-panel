# Runs a read-only check of an earlier pass on the model as it stands, with its output caught into THIS pass's folder.
# The earlier script is read from its folder on the Mac and refused unless its sha256 is the repo's (s00_lib.OLD).
#   m17 (../model-v85/m17_checks.py): st_walls, st_small, st_grid, st_chamber, st_plug   (the boxes against their _v85 copies)
#   m12 (../model-v85/m12_driver.py): st_room, st_faces                                  (each driver's room in its box)
#   d27 (../model-v80/d27_fits.py):   st_near, st_push, st_ring, st_walk, st_clipkey, st_where, ...
#   m20 (../model-v85/m20_close.py), m10, m11, m18: see those files
# READ-ONLY: those functions work on temporary bodies; nothing is created in the document.
# Run: L.checked('s22_old.py', sha)['main'](key, func, tag, **kw)  -> s22_<key>_<func>_<tag>.txt
import runpy

D = '/Users/danielneocleous/Documents/HA_panel_renders/screw_margins_v88/'
L = runpy.run_path(D + 's00_lib.py')


def _main(key, func, **kw):
    M = L['old'](key)
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    print('%s.%s(%s)' % (key, func, ', '.join('%s=%r' % q for q in sorted(kw.items()))))
    M[func](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(key, func, tag='', **kw):
    L['out']('s22_%s_%s%s.txt' % (key, func.replace('st_', ''), ('_' + tag) if tag else ''), _main, key, func, **kw)
# END
