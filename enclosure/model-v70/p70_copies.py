# Hidden '_v69'-named copies of bodies that a block is about to change and that block 0 did not copy (brief: "Before a body changes
# that has no hidden _v69 copy yet, make one"). The copy is of the body as it stands now (version 75 or later), named <name>_v69 so
# that the library's filters keep it out of the unit, hidden. CHANGES THE DOCUMENT (adds hidden bodies).
# Run: runpy.run_path(D + 'p70_copies.py')['main'](names, tag)  -> p70_copies_<tag>.txt
import runpy

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def _main(names):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    for n in names:
        b = X.body(n)
        if X.body(n + '_v69') is not None:
            print('%s: copy exists' % n); continue
        c = X.add(X.tbm.copy(b), n + '_v69', like=b, show=False)
        print('%s: copied, %.3f / %.3f mm3, lumps %d' % (n, b.volume * 1000, c.volume * 1000, c.lumps.count))
    print(L['stamp'](), 'after', X.state())


def main(names, tag):
    L['out']('p70_copies_%s.txt' % tag, _main, names)
