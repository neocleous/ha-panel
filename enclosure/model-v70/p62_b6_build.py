# Block 6 (brief claude/brief-enclosure-audit-fixes-rest-2026-11-25.md): the cap, the clamps, the strip envelopes and the keep-outs
# behind the strips, built as temporary bodies. CHANGES NOTHING IN THE DOCUMENT. Results in k.c:
#   b6_cap, b6_clampL, b6_clampR, b6_stripL, b6_stripR, b6_koL, b6_koR
# World mm, as fitted. The clamp prints as fitted, underside down (K1, D388), 0.20 layers; the cap top face down at 0.10 (D399).
#
# The design (my figures under D150 and D280; the foam gap marked for the Architect):
#  Clamp (each; L at +x, R its mirror):
#   - height seat-to-underside 4.8 (was 4.9, a half layer): the clamp moved up 0.1 so that its seat stays on the roof (z 177.5);
#     underside z 172.7 (was 172.6), 0.1 above the cap's lowest plane
#   - toes 0.4 below the seat (was 0.7): bed 4.4, z 177.1; the ledges beside them stay 0.4 below the toes: bed 4.0, z 176.7
#   - lug top bed 3.8 (z 176.5, as before in the world); floor round the boss bed 1.8 (z 174.5)
#   - the VEML6030 finger's post top bed 3.2 (z 175.9): preload on the board 0.14 (was 0.20), the side that opens the fit
#   - AA-A4: the slot 3.8 wide (was 3.3), centred on the peg; the lug's outer wall grown 0.2 outward to keep 1.25;
#     the lug's top edge (the rail's end beside the peg) broken 0.6 x 45 deg
#  Cap:
#   - the four strip pins Ø1.5 (were 1.8), tips at z 177.4 (bed 2.6; were 177.0): 0.3 above the toes
#   - the eight strip pads 0.4 tall (were 0.7): face z 177.9 (bed 2.1)
#   - the two clamp bosses 0.1 shorter: end z 174.7 (bed 5.3): thread 4.0 with the clamp 0.1 higher; floor gap 0.2
#  Strip envelopes: 28 long (x 9.5..37.5), strip 0.8 on the pads (z 177.1..177.9), foam 0.4 to the ceiling (178.3)
#  Keep-outs behind the strips: the strip's footprint, z 166.5 to 0.3 under its back face (176.8), less the clamp.
# Run: runpy.run_path(D + 'p62_b6_build.py')['main']()  -> p62_b6_build.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def xs(sx, a, b):
    return sorted((sx * a, sx * b))


def bx(X, sx, x0, x1, y0, y1, z0, z1):
    a, b = xs(sx, x0, x1); return X.wbox(a, b, y0, y1, z0, z1)


def clamp(k, X, sx):
    name = 'MIC_CLAMP_L' if sx > 0 else 'MIC_CLAMP_R'
    t = X.tbm.copy(X.body(name)); v0 = X.vol(t)
    X.move(t, 0, 0, 0.1)
    X.dif(t, bx(X, sx, 9.7, 31.1, -40.0, -29.8, 177.5, 177.7))                 # seat back to the roof
    for a, b in ((9.8, 11.8), (29.0, 31.0)):
        X.uni(t, bx(X, sx, a, b, -28.5, -24.5, 176.85, 177.1))                 # toes up 0.2
        X.uni(t, bx(X, sx, a, b, -29.9, -28.5, 176.45, 176.7))                 # ledges up 0.2
    X.dif(t, bx(X, sx, 30.9, 36.3, -36.5, -31.6, 176.5, 176.7))                # lug top back to 176.5
    X.dif(t, bx(X, sx, 31.0, 36.3, -31.6, -29.85, 176.5, 176.7))
    X.dif(t, X.cyl((sx * 15.5, -35.2, 174.5), (sx * 15.5, -35.2, 174.6), 3.4))   # floor round the boss to 174.5
    X.dif(t, bx(X, sx, 6.55, 8.45, -38.45, -36.55, 175.9, 176.2))              # VEML post top 175.9
    X.dif(t, bx(X, sx, 30.9, 34.9, -35.15, -31.35, 175.1, 178.0))              # slot 3.8 wide
    X.uni(t, bx(X, sx, 30.9, 36.2, -36.4, -36.15, 173.3, 176.5))               # lug's outer wall 0.2 outward
    # chamfer 0.6 x 45 on the rail's end beside the peg: remove sx*x + z >= 31.0 + 177.5 - 0.6
    n = (sx / math.sqrt(2), 0.0, 1 / math.sqrt(2)); a2 = (sx / math.sqrt(2), 0.0, -1 / math.sqrt(2))
    p0 = (sx * 30.7, -30.75, 177.2)
    cen = (p0[0] + n[0] * 1.0, p0[1], p0[2] + n[2] * 1.0)
    w = X.obox(cen, (0, 1, 0), a2, 1.9, 3.0, 2.0)
    # obox height axis = (0,1,0) x a2; make sure it is +-n (a box is symmetric about its centre, so either sign does)
    X.sec(w, bx(X, sx, 29.0, 33.0, -31.7, -29.8, 176.55, 178.0))
    vw = X.vol(w)
    X.dif(t, w)
    print('%s: %.3f -> %.3f mm3, lumps %d, faces %d (chamfer wedge %.3f mm3)' % (name, v0, X.vol(t), t.lumps.count, t.faces.count, vw))
    return t


def cap(k, X):
    t = X.tbm.copy(X.body('HOUSING_F_cap')); v0 = X.vol(t)
    for sx in (1, -1):
        for xp in (11.5, 30.0):
            X.dif(t, X.cyl((sx * xp, -26.5, 176.95), (sx * xp, -26.5, 178.3), 0.95))
            X.uni(t, X.cyl((sx * xp, -26.5, 177.4), (sx * xp, -26.5, 178.35), 0.75))
        for a, b in ((8.3, 9.9), (36.1, 37.7)):
            for y0, y1 in ((-29.7, -28.1), (-24.9, -23.3)):
                X.dif(t, bx(X, sx, a, b, y0, y1, 177.5, 177.9))
        X.dif(t, X.cyl((sx * 15.5, -35.2, 174.5), (sx * 15.5, -35.2, 174.7), 3.1))
    print('HOUSING_F_cap: %.3f -> %.3f mm3, lumps %d, faces %d' % (v0, X.vol(t), t.lumps.count, t.faces.count))
    return t


def strip(k, X, sx):
    name = 'MIC_strip_L_env' if sx > 0 else 'MIC_strip_R_env'
    t = X.tbm.copy(X.body(name)); v0 = X.vol(t)
    X.sec(t, bx(X, sx, 9.5, 40.0, -31.0, -22.0, 170.0, 182.0))
    X.move(t, 0, 0, 0.3)
    X.sec(t, bx(X, sx, 0.0, 40.0, -31.0, -22.0, 170.0, 178.3))
    print('%s: %.3f -> %.3f mm3, lumps %d, faces %d, world box %s' % (name, v0, X.vol(t), t.lumps.count, t.faces.count, k.wbb(X, t)))
    return t


def ko(k, X, sx, cl):
    t = bx(X, sx, 9.5, 37.5, -29.5, -23.5, 166.5, 176.8)
    X.dif(t, X.tbm.copy(cl))
    print('KO_mic_%s_back: %.3f mm3 (was %.3f), lumps %d, faces %d' % ('L' if sx > 0 else 'R', X.vol(t),
          X.body('KO_mic_%s_back' % ('L' if sx > 0 else 'R')).volume * 1000, t.lumps.count, t.faces.count))
    return t


def _main():
    k = L['load'](); X = k.K(); k.budget(75)
    print(L['stamp'](), 'before', X.state())
    k.c['b6_clampL'] = clamp(k, X, 1); k.c['b6_clampR'] = clamp(k, X, -1)
    k.c['b6_cap'] = cap(k, X)
    k.c['b6_stripL'] = strip(k, X, 1); k.c['b6_stripR'] = strip(k, X, -1)
    k.c['b6_koL'] = ko(k, X, 1, k.c['b6_clampL']); k.c['b6_koR'] = ko(k, X, -1, k.c['b6_clampR'])
    print('clamp L vs R volume: %.4f / %.4f' % (X.vol(k.c['b6_clampL']), X.vol(k.c['b6_clampR'])))
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p62_b6_build.txt', _main)
