# Puts temporary bodies into the model, after ../model-v70/p70_copies.py and p57_replace.py. CHANGES THE DOCUMENT.
#   copies(names, tag)    a hidden copy <name>_v79 of each named body as it stands (version 79's state), unless one exists. The
#                         library's filters keep a name ending in _vNN out of the unit.
#   put(pairs, tag)       each named body replaced by the temporary body k.c[key]: same name, appearance, material and
#                         visibility; the old body deleted (its _v79 copy must exist). Volumes by both readings (D425),
#                         beside the copy's. The library's cached copies of the bodies are dropped.
#   add(rows, tag)        new bodies: (name, key, like, show) - the temporary body k.c[key] added under 'name' with the
#                         appearance and material of the body 'like'
# Run: runpy.run_path(D + 'd21_put.py')['copies'](names, tag) etc.  -> d21_<what>_<tag>.txt
import runpy
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')
SUF = '_v79'


def _copies(names):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    for n in names:
        b = X.body(n)
        if b is None:
            raise RuntimeError('no body ' + n)
        if X.body(n + SUF) is not None:
            print('%s: copy exists' % n); continue
        c = X.add(X.tbm.copy(b), n + SUF, like=b, show=False)
        print('%-20s copied as %s: %.3f / %.3f mm3, lumps %d, visible %s' % (n, n + SUF, b.volume * 1000, c.volume * 1000, c.lumps.count, c.isLightBulbOn))
    print(L['stamp'](), 'after', X.state())


def _put(pairs):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    for name, key in pairs:
        if k.c.get(key) is None:
            raise RuntimeError('missing ' + key)
        if X.body(name + SUF) is None:
            raise RuntimeError('no copy ' + name + SUF)
        if X.body(name) is None:
            raise RuntimeError('no body ' + name)
    for name, key in pairs:
        old = X.body(name)
        was = (old.volume * 1000.0, L['vhi'](old)); vis = old.isLightBulbOn
        nb = X.add(X.tbm.copy(k.c[key]), name + '_new', like=old, show=vis)
        old.deleteMe()
        nb.name = name
        print('%-20s was %12.3f (prefl.) %12.3f (v.high) | now %12.3f %12.3f | %s %12.3f | lumps %d faces %d visible %s' % (
            name, was[0], was[1], nb.volume * 1000.0, L['vhi'](nb), SUF, L['vhi'](X.body(name + SUF)), nb.lumps.count, nb.faces.count, vis))
    k.purge(tuple(n for n, q in pairs))
    print(L['stamp'](), 'after', X.state())


def _add(rows):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    for name, key, like, show in rows:
        if X.body(name) is not None:
            raise RuntimeError('there is a body ' + name)
        nb = X.add(X.tbm.copy(k.c[key]), name, like=X.body(like), show=show)
        print('%-20s added: %.3f mm3, lumps %d, faces %d, visible %s (appearance as %s)' % (name, nb.volume * 1000, nb.lumps.count, nb.faces.count, nb.isLightBulbOn, like))
    print(L['stamp'](), 'after', X.state())


def copies(names, tag):
    L['out']('d21_copies_%s.txt' % tag, _copies, names)


def put(pairs, tag):
    L['out']('d21_put_%s.txt' % tag, _put, pairs)


def add(rows, tag):
    L['out']('d21_add_%s.txt' % tag, _add, rows)


def save(desc):
    k = L['load'](); X = k.K()
    before = X.state()
    names = X.names()
    if any(n.startswith(('TMP_', 'AUD_')) for n in names):
        raise RuntimeError('TMP_ or AUD_ bodies in the document: not saved')
    ok = X.doc.save(desc)
    line = '%s  save(%r) -> %s; before %s' % (L['stamp'](), desc, ok, before)
    open(D + 'd21_save.txt', 'a').write(line + '\n')
    print(line)


def check():
    k = L['load'](); X = k.K()
    df = X.doc.dataFile
    line = '%s  check: version %d of %d, modified %s, %s, description %r' % (L['stamp'](), df.versionNumber, df.latestVersionNumber, X.doc.isModified, X.state(), df.description)
    open(D + 'd21_save.txt', 'a').write(line + '\n')
    print(line)
# END
