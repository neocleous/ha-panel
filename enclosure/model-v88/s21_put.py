# Puts built bodies into the model, after ../model-v85/m16_put.py. CHANGES THE DOCUMENT (copies, put, save).
#   copies(names, tag)  a hidden copy <name>_v88 of each named body as it stands (version 88's state), unless one exists
#   put(pairs, tag)     each named body replaced by the temporary body k.c[key]: same name, appearance, material and visibility;
#                       the old body deleted (its _v88 copy must exist); volumes by both readings beside the copy's
#   save(desc)          a new version with this description, refused if a TMP_ or AUD_ body is in the document or the description
#                       does not say "not for print"; logged
#   check()             the version, its description and the document's state, logged
# Only the six bodies the brief names may change: SPKBOX_L, SPKBOX_R, HOUSING_F_front, HOUSING_F_door, MIC_CLAMP_L, MIC_CLAMP_R.
# Run: L.checked('s21_put.py', sha)[...](...)  -> s21_<what>_<tag>.txt, s21_save.txt
import runpy
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/screw_margins_v88/'
L = runpy.run_path(D + 's00_lib.py')
SUF = L['SUF']
MAY = tuple(L['MAY_CHANGE']) + ('SCREWS_M2x6_env',)     # and the screws' drawing, which follows its seats (block 3; not a printed part)


def _copies(names):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    for n in names:
        if n not in MAY:
            raise RuntimeError('not a body this pass may change: ' + n)
        b = X.body(n)
        if b is None:
            raise RuntimeError('no body ' + n)
        if X.body(n + SUF) is not None:
            print('%s: copy exists' % n); continue
        c = X.add(X.tbm.copy(b), n + SUF, like=b, show=False)
        print('%-16s copied as %s: %.3f / %.3f mm3 (very high %.3f / %.3f), lumps %d, faces %d / %d, visible %s' % (
            n, n + SUF, b.volume * 1000, c.volume * 1000, L['vhi'](b), L['vhi'](c), c.lumps.count, b.faces.count, c.faces.count, c.isLightBulbOn))
    print(L['stamp'](), 'after', X.state())


def _put(pairs):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    for name, key in pairs:
        if name not in MAY:
            raise RuntimeError('not a body this pass may change: ' + name)
        if k.c.get(key) is None:
            raise RuntimeError('missing ' + key)
        if X.body(name + SUF) is None:
            raise RuntimeError('no copy ' + name + SUF)
    for name, key in pairs:
        old = X.body(name)
        was = (old.volume * 1000.0, L['vhi'](old)); vis = old.isLightBulbOn
        nb = X.add(X.tbm.copy(k.c[key]), name + '_new', like=old, show=vis)
        old.deleteMe()
        nb.name = name
        print('%-16s was %12.3f (prefl.) %12.3f (v.high) | now %12.3f %12.3f | %s %12.3f | lumps %d faces %d visible %s' % (
            name, was[0], was[1], nb.volume * 1000.0, L['vhi'](nb), SUF, L['vhi'](X.body(name + SUF)), nb.lumps.count, nb.faces.count, vis))
    k.purge(tuple(n for n, q in pairs))
    print(L['stamp'](), 'after', X.state())


def copies(names, tag):
    L['out']('s21_copies_%s.txt' % tag, _copies, names)


def put(pairs, tag):
    L['out']('s21_put_%s.txt' % tag, _put, pairs)


def save(desc):
    k = L['load'](); X = k.K()
    before = X.state()
    if any(n.startswith(('TMP_', 'AUD_')) for n in X.names()):
        raise RuntimeError('TMP_ or AUD_ bodies in the document: not saved')
    if 'not for print' not in desc:
        raise RuntimeError('the description must say not for print')
    ok = X.doc.save(desc)
    line = '%s  save(%r) -> %s; before %s' % (L['stamp'](), desc, ok, before)
    open(D + 's21_save.txt', 'a').write(line + '\n')
    print(line)


def check():
    k = L['load'](); X = k.K()
    df = X.doc.dataFile
    line = '%s  check: version %d of %d, modified %s, %s, description %r' % (L['stamp'](), df.versionNumber, df.latestVersionNumber, X.doc.isModified, X.state(), df.description)
    open(D + 's21_save.txt', 'a').write(line + '\n')
    print(line)
# END
