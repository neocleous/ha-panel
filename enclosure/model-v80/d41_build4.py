# Block 4 (D467, PR48): the carrier's two pilots for the ReSpeaker's screws, and the two screws. Builds temporary bodies and
# keeps them in k.c; NOTHING IS PUT INTO THE DOCUMENT here (d21_put.py does that).
#
# Slab frame: x, d = depth behind the glass's front, zd. The carrier prints plate down, bed at d 15.2, height d - 15.2.
#   RESP_CARRIER                                                                                  key b4_carrier
#     each pilot (1.6 across, on its own axis as modelled) deepened from 4.5 to 5.6: floor at d 16.6, bed 1.4 (on the grid),
#     1.4 of plate left under it; an entry chamfer 0.3 x 45 deg at the boss top (2.2 across at the face), as version 42 had
#   SCREWS_M2x6_env                                                                               key b4_screws
#     two more screws, drawn as the seven the body has (measured on them, d40 screws): head 3.8 across with a rim 0.3 high and
#     a cone of 0.9 down to the shank 2.0 across, 6.0 long over all. Seated as that head seats on the ReSpeaker's board: the cone
#     on the rim of the board's hole, 2.2 across by the record (fastener schedule of 2026-11-06; the model's board has no holes),
#     the board's back face at d 23.71 (RESP_pcb as modelled, 1.51 thick). Head top d 24.81, tip d 18.81.
#     The ordered screws are countersunk (architect log 2026-11-16 morning, section 4.2); their head's size is not in the records.
# Stages: carrier, screws, all; diff() compares what is built with the model's bodies; tips() gives the figures.
# Run: runpy.run_path(D + 'd41_build4.py')['main'](stage)  -> d41_<stage>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')
CYL = adsk.core.SurfaceTypes.CylinderSurfaceType
BED = 15.2
D_FLOOR = 16.6                       # bed 1.4
D_TOP = 22.2                         # the boss tops, bed 7.0 (measured, d40 carrier)
CH = 0.3                             # entry chamfer
D_BOARD_BACK = 23.71                 # RESP_pcb's far face (measured, d40 resp); its near face lies on the boss tops
HOLE_R = 1.1                         # the board's hole, 2.2 across (record)
R_SH = 1.0; R_HD = 1.9; H_RIM = 0.3; H_CONE = 0.9; LEN = 6.0
KEYS = {'RESP_CARRIER': 'b4_carrier', 'SCREWS_M2x6_env': 'b4_screws'}


def pilots(k, b):
    """The two pilots' axes in the slab frame (x, zd), from the round faces themselves."""
    out = {}
    for f in b.faces:
        g = f.geometry
        if g.surfaceType != CYL or abs(g.radius * 10 - 0.8) > 0.01:
            continue
        o = k.Sf(g.origin)
        out[(round(o[0], 4), round(o[2], 4))] = 1
    return sorted(out)


def carrier(k, X):
    src = X.body('RESP_CARRIER'); t = X.cp(src)
    ps = pilots(k, src)
    if len(ps) != 2:
        raise RuntimeError('pilots found: %s' % ps)
    for (x, zd) in ps:
        v0 = X.vol(t)
        X.dif(t, X.tbm.createCylinderOrCone(k.Dp(x, D_FLOOR, zd), 0.08, k.Dp(x, D_TOP - 4.0, zd), 0.08))          # deeper: to d 16.6
        v1 = X.vol(t)
        X.dif(t, X.tbm.createCylinderOrCone(k.Dp(x, D_TOP - CH, zd), 0.08, k.Dp(x, D_TOP + 0.1, zd), (0.8 + CH + 0.1) / 10.0))   # the chamfer
        v2 = X.vol(t)
        print('pilot at slab x %.4f, zd %.4f: deepened to d %.1f (bed %.1f): %.4f removed (a 1.6 bar %.2f long is %.4f); chamfer %.1f: %.4f removed' % (
            x, zd, D_FLOOR, D_FLOOR - BED, v0 - v1, 17.7 - D_FLOOR, math.pi * 0.64 * (17.7 - D_FLOOR), CH, v1 - v2))
    return t


def screw(k, x, zd, d_back):
    """One M2 x 6 as the body's other screws are drawn, its cone seated on the rim of a hole 2.2 across in a face at d_back."""
    d_c0 = d_back - (HOLE_R - R_SH)                    # where the cone begins (shank's radius), inside the hole
    d_c1 = d_c0 + H_CONE; d_top = d_c1 + H_RIM; d_tip = d_top - LEN
    tb = adsk.fusion.TemporaryBRepManager.get()
    s = tb.createCylinderOrCone(k.Dp(x, d_tip, zd), R_SH / 10.0, k.Dp(x, d_c0, zd), R_SH / 10.0)
    c = tb.createCylinderOrCone(k.Dp(x, d_c0, zd), R_SH / 10.0, k.Dp(x, d_c1, zd), R_HD / 10.0)
    r = tb.createCylinderOrCone(k.Dp(x, d_c1, zd), R_HD / 10.0, k.Dp(x, d_top, zd), R_HD / 10.0)
    tb.booleanOperation(s, c, adsk.fusion.BooleanTypes.UnionBooleanType)
    tb.booleanOperation(s, r, adsk.fusion.BooleanTypes.UnionBooleanType)
    return s, d_tip, d_top


def screws(k, X):
    t = X.cp(X.body('SCREWS_M2x6_env'))
    for (x, zd) in pilots(k, X.body('RESP_CARRIER')):
        s, d_tip, d_top = screw(k, x, zd, D_BOARD_BACK)
        print('screw at slab x %.4f, zd %.4f: head top d %.3f, tip d %.3f; %.3f mm3' % (x, zd, d_top, d_tip, X.vol(s)))
        X.uni(t, s)
    return t


def tips():
    """Computed from the figures above: the thread in the boss and the tip's room over the new floor, for a board of 1.51
    and of 1.6, with the head seated as drawn (cone on the hole's rim) and with the whole 6.0 under the board's back face
    (a pan head; D467's reading)."""
    rows = []
    for tb in (1.51, 1.6):
        back = D_TOP + tb
        for nm, tip in (('countersunk, as drawn', back - (HOLE_R - R_SH) + H_CONE + H_RIM - LEN), ('6.0 under the board\'s back face', back - LEN)):
            rows.append('board %.2f, %-32s tip at d %.3f (bed %.3f): in the boss %.2f, below the chamfer %.2f; room over the floor %.2f; over the old floor (d 17.7) %.2f' % (
                tb, nm + ':', tip, tip - BED, D_TOP - tip, D_TOP - CH - tip, tip - D_FLOOR, tip - 17.7))
    return rows


def say(k, X, key, t, ref):
    k.c[key] = t
    r = X.body(ref)
    print('%-12s %12.3f mm3, lumps %d, faces %d | %s in the model %.3f, lumps %d, faces %d' % (key, X.vol(t), t.lumps.count, t.faces.count, ref, r.volume * 1000, r.lumps.count, r.faces.count))


def _main(stage):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    if stage in ('carrier', 'all'):
        say(k, X, 'b4_carrier', carrier(k, X), 'RESP_CARRIER')
    if stage in ('screws', 'all'):
        say(k, X, 'b4_screws', screws(k, X), 'SCREWS_M2x6_env')
    for r in tips():
        print(r)
    print(L['stamp'](), 'after', X.state())


def main(stage='all'):
    L['out']('d41_%s.txt' % stage, _main, stage)


def _diff(names):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'what is built against the model\'s bodies as they stand')
    for n in names:
        if k.c.get(KEYS[n]) is None:
            print('%-18s not built in this session' % n); continue
        a = X.tbm.copy(k.c[KEYS[n]]); b = X.tbm.copy(X.body(n))
        add = X.tbm.copy(a); X.dif(add, X.tbm.copy(b))
        rem = X.tbm.copy(b); X.dif(rem, X.tbm.copy(a))
        la = X.lumps(add) if add.faces.count else []; lr = X.lumps(rem) if rem.faces.count else []
        print('%-18s new %.3f, old %.3f; added %.3f in %d lumps, removed %.3f in %d lumps' % (n, X.vol(a), X.vol(b), sum(q[0] or 0 for q in la), len(la), sum(q[0] or 0 for q in lr), len(lr)))
        for tag, ls in (('+', la), ('-', lr)):
            for v, bb in ls[:8]:
                print('      %s %9.4f  %s' % (tag, v, bb))


def diff(names, tag=''):
    L['out']('d41_diff%s.txt' % (('_' + tag) if tag else ''), _diff, names)
# END
