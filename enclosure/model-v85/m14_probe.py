# Block 1: small read-only probes. READ-ONLY.
#   inbox    the bodies of the unit (and leads) that share volume with a world box, and how much; the box's solid in it
#   faces    the faces of a body with their sample point in a world box (k.faces): planes and cylinders
# Run: L.checked('m14_probe.py', sha)['main'](stage, tag, **kw)  -> m14_<stage>_<tag>.txt
import runpy
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/box_margins_v85/'
L = runpy.run_path(D + 'm00_lib.py')


def st_inbox(k, X, box, sec=70):
    k.budget(sec)
    t = X.wbox(*box)
    print('world box %s, %.1f mm3' % (box, X.vol(t)))
    for b in k.current(X, leads=True, kos=True):
        if b.name.startswith(('HOUSING_F_front', 'SLAB_frame', 'HOUSING_F_door')):
            continue
        q = k.wbb(X, b)
        if q[1] < box[0] or q[0] > box[1] or q[3] < box[2] or q[2] > box[3] or q[5] < box[4] or q[4] > box[5]:
            continue
        v = X.xv(X.tbm.copy(b), t)
        if v > 0.0005:
            print('   %-24s %10.3f mm3 in the box' % (b.name, v))
        if k.late():
            print('time'); return


def st_faces(k, X, name, box, amin=0.5):
    k.budget(70)
    for r in k.faces(X, X.body(name), box, amin=amin):
        print('   %s' % (r,))


def st_needle(k, X, rows, keys=()):
    """rows: [(label, body name or cache key, p0, p1)]: the solid stretches (mm from p0) of the body on the line p0 -> p1."""
    k.budget(70)
    for lab, src, p0, p1 in rows:
        b = k.c[src] if src in k.c else k.tcopy(X, src)
        print('%-30s %-18s from %s to %s: %s' % (lab, src, p0, p1, k.needle_t(X, [b], p0, p1, 0.02)))


def _main(stage, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'inbox': st_inbox, 'faces': st_faces, 'needle': st_needle}[stage](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(stage, tag='', **kw):
    L['out']('m14_%s%s.txt' % (stage, ('_' + tag) if tag else ''), _main, stage, **kw)
# END
