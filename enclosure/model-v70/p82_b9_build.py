# Block 9 (brief claude/brief-enclosure-audit-fixes-rest-2026-11-25.md, as claude/architect-log-2026-11-25-b.md D442 and §4.B
# amend it): the radar's holder behind the touch board, built as temporary bodies. CHANGES NOTHING IN THE DOCUMENT.
# Plan: claude/note-enclosure-audit-fixes-block9-plan-2026-11-25.md, with log B's conditions. World mm.
# Stages (results in k.c):
#   'radar'   LD2410C_env_F (from its _v69 copy) turned and moved: x 23.5..39.5, y -5.9..-2.9 (face toward +y, 5.7 behind the
#             board's back at y 2.8), z 29..51                                                               -> b9_radar
#   'screws'  SCREWS_M2x6_env (the model's, version 78) less today's two radar screws, plus two at the holder: countersunk M2 x 6
#             (head Ø3.8, 90 deg; the shape of today's lumps), axes along y, 1.0 outside each long edge: -x at (22.5, z 31.6),
#             +x at (40.5, z 48.8) above the clip; head's flat face y -6.5, the cone bearing on the board's back edge
#                                                                                                            -> b9_screws
#   'holder'  RADAR_HOLDER, printed upright (z up, bed z 27.6, 0.20 layers):
#             ledge round the face y -2.9..-1.7 (window 0.8 over each edge); -x wall (0.2 to the radar); bottom 0.2 under it;
#             top plate 0.2 over it, back to y -10.4; tab x 36.6..39.6 with a bearing rib x 39.6..40.0 along z at y -7.8..-6.6
#             (a line contact: the tab does not set the turn about z); the hole a slot along y, 0.4 either way (log B §4.B.1);
#             posts round the M2 pilots (Ø1.6), the +x post carried to the board's back as standoff C; standoffs A and B on the
#             -x side; the arm 1.2 thick, its pad 0.6 into the board's back as modelled                     -> b9_holder
#   'box'     SPKBOX_L with the holder's block on its inner face: x 40.0..46.0, y -11.0..-4.0, z 53.2..62.0, its bed-side
#             face (toward y -) turned into a 45 deg foot onto the wall; pilot Ø2.5 along x from x 40.0 to 45.35   -> b9_boxL
#   'lead'    LEAD_RADAR laid again: Ø2.6 pieces through the points below, to J5's end as today                -> b9_lead
# Run: runpy.run_path(D + 'p82_b9_build.py')['main'](stage)  -> p82_<stage>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
R0_FRONT = (-72.53, -22.05, 127.5); R0_BACK = (-69.96, -23.6, 127.5)      # today's face centroids (p75_b9_inspect.txt)
RC = (31.5, -4.4, 40.0)                                                    # the radar's new centre
SCR = ((22.5, 31.6), (40.5, 48.8))                                         # (x, z) of the two M2 axes
HEAD_Y = -6.5                                                              # the countersunk head's flat face
PIL_Y = (-5.6, -0.2)                                                       # the M2 pilots, Ø1.6
TAB_X = (36.6, 39.6); RIB_X = (39.6, 40.0); TAB_Y = (-10.4, -4.0); TAB_Z = (51.2, 62.0)
M3 = (-7.2, 57.6)                                                          # (y, z) of the holder's screw axis
# Route R2 (p84_b9_lead.txt, 2026-11-25 13:16; taken by D448). The plan's route R1 crossed LEAD_SPK_R. This line was edited again on
# 2026-11-26: the edit of 2026-11-25 never reached the Mac (the file's sha256 was dffd96e8..., not ecafbc506f15...).
LEAD_PTS = [(24.8, -7.2, 40.0), (22.0, -11.5, 42.5), (-31.0, -40.0, 77.0), (-37.6, -40.6, 92.5), (-37.8, -32.98, 94.07)]
LEAD_R = 1.3


def rigid(k):
    c0 = tuple((R0_FRONT[i] + R0_BACK[i]) / 2.0 for i in range(3))
    n0 = k.unit(tuple(R0_FRONT[i] - R0_BACK[i] for i in range(3)))
    th = math.pi / 2.0 - math.atan2(n0[1], n0[0])
    m = adsk.core.Matrix3D.create(); m.setToRotation(th, k.dv((0, 0, 1)), k.Wp(*c0))
    t = adsk.core.Matrix3D.create(); t.translation = k.dv(tuple(RC[i] - c0[i] for i in range(3)))
    # dv gives a direction in design cm-free units; translation needs cm: scale
    tv = k.dv(tuple((RC[i] - c0[i]) / 10.0 for i in range(3)))
    t.translation = tv
    m.transformBy(t)
    return m, th


def radar(k, X):
    m, th = rigid(k)
    t = X.tbm.copy(X.body('LD2410C_env_F_v69')); X.tbm.transform(t, m)
    print('radar turned %.3f deg about z and moved: world box %s, volume %.3f' % (math.degrees(th), [round(v, 3) for v in k.wbb(X, t)], X.vol(t)))
    k.c['b9_radar'] = t


def m2(k, X, x, z):
    h = X.cyl((x, HEAD_Y, z), (x, HEAD_Y + 0.3, z), 1.9)
    X.uni(h, X.cyl((x, HEAD_Y + 0.3, z), (x, HEAD_Y + 1.2, z), 1.9, 1.0))
    X.uni(h, X.cyl((x, HEAD_Y + 1.2, z), (x, HEAD_Y + 6.0, z), 1.0))
    return h


def screws(k, X):
    s = X.tbm.copy(X.body('SCREWS_M2x6_env')); v0 = X.vol(s)   # the model's own (its _v69 copy is version 69's, before blocks 3 and 6)
    for lo, hi in (((-80.25, -31.59, 117.35), (-74.21, -27.18, 120.94)), ((-70.98, -16.16, 117.35), (-64.94, -11.75, 120.94))):
        X.dif(s, X.wbox(lo[0] - 2.0, hi[0] + 2.0, lo[1] - 2.0, hi[1] + 2.0, lo[2] - 2.0, hi[2] + 2.0))
    v1 = X.vol(s)
    for x, z in SCR:
        X.uni(s, m2(k, X, x, z))
    print('SCREWS_M2x6_env: %.3f -> less today\'s two %.3f -> %.3f (each new %.3f), lumps %d' % (v0, v1, X.vol(s), X.vol(m2(k, X, 0, 0)), s.lumps.count))
    k.c['b9_screws'] = s


def holder(k, X):
    H = X.wbox(22.1, 40.2, -2.9, -1.7, 27.6, 53.0)                               # the ledge's plate
    X.dif(H, X.wbox(24.3, 38.7, -3.0, -1.6, 29.8, 50.2))                          # its window, 0.8 over each edge
    for b in (X.wbox(22.1, 23.3, -5.9, -1.7, 27.6, 53.0),                         # -x wall, 0.2 to the radar
              X.wbox(22.1, 40.2, -5.9, -1.7, 27.6, 28.8),                         # bottom, 0.2 under the radar
              X.wbox(22.1, 40.0, -10.4, -1.7, 51.2, 53.0),                        # top plate, 0.2 over the radar
              X.wbox(TAB_X[0], TAB_X[1], TAB_Y[0], TAB_Y[1], TAB_Z[0], TAB_Z[1]),  # tab
              X.wbox(RIB_X[0], RIB_X[1], -7.8, -6.6, TAB_Z[0], TAB_Z[1]),         # bearing rib along z
              X.cyl((SCR[0][0], -5.6, SCR[0][1]), (SCR[0][0], 0.6, SCR[0][1]), 2.0),  # -x post
              X.cyl((SCR[1][0], -5.6, SCR[1][1]), (SCR[1][0], 2.8, SCR[1][1]), 2.0),  # +x post, to the board: standoff C
              X.wbox(21.1, 23.3, -1.7, 2.8, 36.0, 38.0),                          # standoff A
              X.wbox(21.1, 23.3, -1.7, 2.8, 46.0, 48.0),                          # standoff B
              X.wbox(20.1, 22.1, -1.7, 2.5, 40.2, 43.8),                          # the arm's root
              X.wbox(-2.0, 20.1, 1.3, 2.5, 40.2, 43.8),                           # the arm, 1.2 thick
              X.wbox(-2.0, 3.0, 2.5, 3.4, 40.2, 43.8)):                           # its pad, 0.6 into the board's back
        X.uni(H, b)
    # the slot for the holder's M3 (Ø3.4), 0.4 either way along y
    for yy in (M3[0] - 0.4, M3[0] + 0.4):
        X.dif(H, X.cyl((TAB_X[0] - 0.5, yy, M3[1]), (RIB_X[1] + 0.5, yy, M3[1]), 1.7))
    X.dif(H, X.wbox(TAB_X[0] - 0.5, RIB_X[1] + 0.5, M3[0] - 0.4, M3[0] + 0.4, M3[1] - 1.7, M3[1] + 1.7))
    # the M2 pilots, the screws' heads and a counterbore behind each head for the driver
    for x, z in SCR:
        X.dif(H, X.cyl((x, PIL_Y[0] - 0.1, z), (x, PIL_Y[1], z), 0.8))
        X.dif(H, m2(k, X, x, z))
        X.dif(H, X.cyl((x, -12.0, z), (x, HEAD_Y + 0.001, z), 2.0))
    X.dif(H, X.tbm.copy(k.c['b9_radar']))
    print('RADAR_HOLDER: %.3f mm3, lumps %d, faces %d, world box %s' % (X.vol(H), H.lumps.count, H.faces.count, [round(v, 2) for v in k.wbb(X, H)]))
    k.c['b9_holder'] = H


def box(k, X):
    B = X.tbm.copy(X.body('SPKBOX_L')); v0 = X.vol(B)
    blk = X.wbox(40.0, 46.0, -11.0, -4.0, 53.2, 62.0)
    # 45 deg foot: the half-space x + y >= 29.0 (through (40, -11) and (46, -17)), in x 40..46, y -17..-11
    u = k.unit((1, 1, 0)); v = k.unit((-1, 1, 0))
    c = (40.0 + 20.0 * u[0], -11.0 + 20.0 * u[1], 57.6)
    foot = X.obox(c, u, v, 40.0, 60.0, 8.8)
    X.sec(foot, X.wbox(40.0, 46.0, -17.0, -11.0, 53.2, 62.0))
    X.uni(blk, foot)
    add = X.vol(blk) - X.xv(blk, B)
    X.uni(B, blk)
    X.dif(B, X.cyl((39.9, M3[0], M3[1]), (45.35, M3[0], M3[1]), 1.25))
    print('SPKBOX_L: %.3f -> %.3f (block and foot %.3f, of it new %.3f), lumps %d, faces %d' % (v0, X.vol(B), X.vol(blk), add, B.lumps.count, B.faces.count))
    k.c['b9_boxL'] = B


def lead(k, X):
    t = None; L_ = 0.0
    for a, b in zip(LEAD_PTS[:-1], LEAD_PTS[1:]):
        c = X.cyl(a, b, LEAD_R); t = c if t is None else X.uni(t, c)
        L_ += math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))
    for p in LEAD_PTS[1:-1]:
        X.uni(t, X.sph(p, LEAD_R))
    print('LEAD_RADAR laid: %d pieces, %.1f long along its axis, %.3f mm3, lumps %d' % (len(LEAD_PTS) - 1, L_, X.vol(t), t.lumps.count))
    k.c['b9_lead'] = t; k.c['b9_lead_len'] = L_


def _main(stage):
    k = L['load'](); X = k.K(); k.budget(75)
    print(L['stamp'](), 'before', X.state())
    {'radar': radar, 'screws': screws, 'holder': holder, 'box': box, 'lead': lead}[stage](k, X)
    print(L['stamp'](), 'after', X.state())


def main(stage):
    L['out']('p82_%s.txt' % stage, _main, stage)
