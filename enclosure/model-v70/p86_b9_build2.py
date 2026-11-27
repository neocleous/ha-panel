# Block 9, the holder, the radar's two screws and the lead as changed for the three conditions of
# claude/architect-log-2026-11-26.md section 4.B and for four faults found in the first build (p82) on 2026-11-26.
# Temporary bodies only. CHANGES NOTHING IN THE DOCUMENT.
#
# The four faults of the first build:
#   a. p82 cut the whole screw (its Ø2.0 shank too) out of the holder, so the M2 x 6 had no plastic to cut a thread in;
#   b. p82 drew the screws' heads 0.6 behind the radar's 3.0 envelope. Today's two (version 69, p90_today_screws2.txt) have their
#      head's flat face 2.29 behind the board's face plane, their tip 3.71 beyond it, and a block 1.3 high beside the board's
#      edge under the outer half of the head. On a real board (0.74 to 1.6 thick by the record) p82's pilots, 2.7 deep beyond
#      the face plane, were 1.0 too shallow.
#   c. p82's arm met the holder along one edge only, a joint of no width (change 6 below).
#   d. p82 drew the holder's M3 pilot Ø2.5. The record's pilot for an M3 that cuts its own thread across the layers is Ø2.7
#      (FDM9, decided 2026-11-18; the two clips' pilots in the model are Ø2.7).
#
#   'screws'  SCREWS_M2x6_env (the model's as it stands, less whatever stands at the holder) plus the two radar screws drawn as
#             today's: countersunk M2 x 6, axis along y, 1.0 outside each long edge, head's flat face 2.29 behind the face plane
#             (y -5.19), tip at y +0.81                                                                       -> b9_screws
#   'holder'  RADAR_HOLDER, printed upright (z up, bed z 27.6, 0.20 layers). Against p82's:
#             1. the M2 posts start at a block 1.3 behind the face plane (y -4.2), as today's, and run on to y 2.3 (0.5 off the
#                touch board's back); the pilots Ø1.6 go right through; only the head's cone is cut where it meets the block;
#                -x post Ø5.6 (2.0 round the pilot), +x post Ø4.8 (1.6: the clip is 0.4 under it); the -x wall is relieved
#                round the -x screw's head
#             2. a land under the M3's head: the tab's outer face (x 36.6) relieved 0.4 either side of a land y -8.35..-6.35
#                (2.0 wide, centred on the slot), from the top plate's top (z 53.0) up; the slot, the rib and the land centred on
#                the screw's axis at y -7.35
#             3. standoff C outboard of the rib's line (x 40.0): a foot x 38.5..44.5, y -1.65..0.6, z 46.6..50.0 carries the
#                standoff x 42.3..44.5, y 0.6..2.8, z 46.6..50.0
#             4. a tie slot through the top plate, x 23.5..26.5, y -9.15..-7.75: the bar behind it (1.25) takes one tie round
#                the radar's lead, laid under the plate behind the radar
#             5. the -x wall and the ledge's plate 1.25 thick (were 1.2): the wall's outer face at x 22.05, the ledge's front
#                face at y -1.65
#             6. the arm's root runs into the -x wall and the ledge's plate (x 21.1..23.3, y -2.9..2.5): in p82 the root
#                (x 20.1..22.1, y -1.7..2.5) met the wall (x 22.1..23.3, y -5.9..-1.7) along one edge only, a joint of no
#                width; and a 45 deg gusset 1.0 in the corner between the arm's back and its root, its toe at x 20.1 (fourth
#                build: the root's face moved from x 20.1 to 21.1, so that the gusset does not shorten the spring)
#             7. the bay's roof: the top plate's underside prints on the support's interface, 0.2 over the radar's top edge in
#                p82; relieved to z 51.4 over the board and over its way in from behind (x 23.3..39.6, y -10.4..-2.9): 0.4 over
#                the board, the plate 1.6 thick there (fourth build)
#             9. the tab's rear edge at y -10.7 (p82: -10.4; the top plate's stays at -10.4): with the screw's axis 0.15 further
#                back, 1.25 of tab stands behind the slot as in front of it (sixth build)
#             8. the blocks under the M2 heads, behind the ledge's face (y -4.2..-2.9): the outer half only, as today's. In
#                the builds before, what was left of each block on the board's side touched the board's long edge (0.0) and
#                closed the pilot toward the board by a neck 0.2 thick. Now they stand 0.2 off the edges, like the -x wall,
#                and each pilot is open toward the board over the block's 1.3 (fifth build)
#             Ledge window, bottom, top plate, tab, rib, slot, standoffs A and B, the arm's beam and pad as p82. -> b9_holder
#   'box'     SPKBOX_L with the holder's block as p82 has it (x 40..46, y -11..-4, z 53.2..62, a 45 deg foot onto the wall), its
#             pilot Ø2.7 (p82: Ø2.5) at y -7.35 (p82: -7.2), x 40.0..45.35                                      -> b9_boxL
#   'radar'   LD2410C_env_F drawn square at p82's place (x 23.5..39.5, y -5.9..-2.9, z 29..51): p82's turn left it about 0.05 deg
#             off square, 0.015 into the ledge                                                               -> b9_radar
#   'lead'    LEAD_RADAR laid on the route given (default R8)                                                   -> b9_lead
# Run: runpy.run_path(D + 'p86_b9_build2.py')['main'](stage, **kw)  -> p86_<stage>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
P = runpy.run_path(D + 'p82_b9_build.py')
SCR = P['SCR']; TAB_X = P['TAB_X']; RIB_X = P['RIB_X']; TAB_Z = P['TAB_Z']
TAB_Y = (-10.7, -4.0)                 # the tab along y: 0.3 further back than p82's (-10.4), so that 1.25 stands either side of the slot
M3 = (-7.35, 57.6)                    # (y, z) of the holder's screw axis: 0.15 behind p82's, so that the Ø2.7 pilot keeps 2.0 to the block's front face
PILOT_R = 1.35                        # Ø2.7, the record's pilot for an M3 that cuts its own thread across the layers (FDM9; the clips' pilots)
BLOCK = (40.0, 46.0, -11.0, -4.0, 53.2, 62.0)
FACE_Y = -2.9                         # the radar's face plane (the ledge's rear face)
HEAD_Y = FACE_Y - 2.29                # the M2 head's flat face, as today's
BLOCK_Y = FACE_Y - 1.3                # the block under the outer half of the head, as today's
POST_END = 2.3                        # the posts' front ends, 0.5 off the touch board's back
POST_R = (2.8, 2.4)                   # -x post, +x post
X0 = 22.05                            # the -x wall's outer face
LEDGE_Y = -1.65                       # the ledge plate's front face
LAND_Y = (-8.35, -6.35)               # the land under the M3's head, 2.0 wide, centred on the slot
RELIEF_X = 37.0                       # the tab's outer face beside the land
C_FOOT = (38.5, 44.5, LEDGE_Y, 0.6, 46.6, 50.0)
C_PAD = (42.3, 44.5, 0.6, 2.8, 46.6, 50.0)
TIE = (23.5, 26.5, -9.15, -7.75)      # the tie slot through the top plate (x0, x1, y0, y1)
RADAR = (23.5, 39.5, -5.9, -2.9, 29.0, 51.0)   # the radar's board, square: face at y -2.9, 5.7 behind the touch board's back (y 2.8)
SIDE = 0.2                            # the printed faces beside the board's long edges stand this far off them
ROOF_Z = 51.4                         # the top plate's underside over the radar's bay (0.4 over the board's top edge; p82: 51.2, 0.2)
ROOT_X = 21.1                         # the arm's root block's -x face (flush with standoffs A and B); the gusset's toe then stands at
                                      # x 20.1, where the root's face stood, so the gusset does not shorten the spring
# Route R8: R2's end at J5 kept; the start goes up behind the radar to the tie under the top plate's bar (0.2 under the plate),
# out at the holder's -x end; the fifth point moved from (-31, -40, 77) to (-24.5, -40, 77.5) so that the piece up to J5 passes
# between the allowed spaces of J9's and J10's plugs and shares only J5's own.
R8 = [(24.8, -7.2, 40.0), (25.0, -8.4, 46.0), (25.0, -9.8, 49.7), (22.0, -9.8, 49.7), (-24.5, -40.0, 77.5), (-37.6, -40.6, 92.5), (-37.8, -32.98, 94.07)]
LEAD_R = 1.3


def m2(k, X, x, z, head_only=False):
    h = X.cyl((x, HEAD_Y, z), (x, HEAD_Y + 0.3, z), 1.9)
    X.uni(h, X.cyl((x, HEAD_Y + 0.3, z), (x, HEAD_Y + 1.2, z), 1.9, 1.0))
    if not head_only:
        X.uni(h, X.cyl((x, HEAD_Y + 1.2, z), (x, HEAD_Y + 6.0, z), 1.0))
    return h


def radar(k, X, **kw):
    # p82 turned today's envelope into place from face centroids read to 0.01: the box (16 x 22 x 3.0, 1056.000) came out about 0.05 deg
    # off square (its world box 16.01 x 3.02), its face 0.015 in front of the ledge. Here it is drawn square at p82's own place.
    r = X.wbox(*RADAR)
    old = X.body('LD2410C_env_F')
    print('LD2410C_env_F drawn square: world box %s, %.3f mm3, faces %d; the model\'s: %s, %.3f; in both %.3f' % (
        k.wbb(X, r), X.vol(r), r.faces.count, k.wbb(X, old), old.volume * 1000.0, X.xv(r, X.tbm.copy(old))))
    k.c['b9_radar'] = r


def screws(k, X, **kw):
    s = X.tbm.copy(X.body('SCREWS_M2x6_env')); v0 = X.vol(s)
    # today's two at the old pocket, if they are still there, and whatever stands at the holder
    for box in ((-82.25, -72.21, -33.59, -25.18, 115.35, 122.94), (-72.98, -62.94, -18.16, -9.75, 115.35, 122.94), (18.0, 45.0, -9.0, 3.0, 27.0, 52.0)):
        X.dif(s, X.wbox(*box))
    v1 = X.vol(s)
    for x, z in SCR:
        X.uni(s, m2(k, X, x, z))
    print('SCREWS_M2x6_env: %.3f -> without the radar\'s two %.3f -> %.3f (each new %.3f), lumps %d; head flat y %.2f, tip y %.2f' % (
        v0, v1, X.vol(s), X.vol(m2(k, X, 0, 0)), s.lumps.count, HEAD_Y, HEAD_Y + 6.0))
    k.c['b9_screws'] = s


def holder(k, X, **kw):
    for q in ('b9_holder_v1', 'b9_holder_v2'):
        if q not in k.c and 'b9_holder' in k.c:
            k.c[q] = k.c['b9_holder']; break
    H = X.wbox(X0, 40.2, FACE_Y, LEDGE_Y, 27.6, 53.0)                             # the ledge's plate, 1.25
    X.dif(H, X.wbox(24.3, 38.7, FACE_Y - 0.1, LEDGE_Y + 0.1, 29.8, 50.2))         # its window, 0.8 over each edge
    for b in (X.wbox(X0, 23.3, -5.9, LEDGE_Y, 27.6, 53.0),                        # -x wall, 1.25, 0.2 to the radar
              X.wbox(X0, 40.2, -5.9, LEDGE_Y, 27.6, 28.8),                        # bottom, 0.2 under the radar
              X.wbox(X0, 40.0, -10.4, LEDGE_Y, 51.2, 53.0),                       # top plate, 0.2 over the radar
              X.wbox(TAB_X[0], TAB_X[1], TAB_Y[0], TAB_Y[1], TAB_Z[0], TAB_Z[1]),  # tab
              X.wbox(RIB_X[0], RIB_X[1], M3[0] - 0.6, M3[0] + 0.6, TAB_Z[0], TAB_Z[1]),  # bearing rib along z, on the block's side, 1.2 wide
              X.cyl((SCR[0][0], BLOCK_Y, SCR[0][1]), (SCR[0][0], POST_END, SCR[0][1]), POST_R[0]),   # -x post with its block
              X.cyl((SCR[1][0], BLOCK_Y, SCR[1][1]), (SCR[1][0], POST_END, SCR[1][1]), POST_R[1]),   # +x post with its block
              X.wbox(*C_FOOT),                                                    # standoff C's foot, on the ledge and the +x post
              X.wbox(*C_PAD),                                                     # standoff C, outboard of the rib's line
              X.wbox(21.1, 23.3, -1.7, 2.8, 36.0, 38.0),                          # standoff A
              X.wbox(21.1, 23.3, -1.7, 2.8, 46.0, 48.0),                          # standoff B
              X.wbox(ROOT_X, 23.3, FACE_Y, 2.5, 40.2, 43.8),                      # the arm's root, into the -x wall and the ledge's plate
              X.wbox(-2.0, ROOT_X, 1.3, 2.5, 40.2, 43.8),                         # the arm, 1.2 thick
              X.wbox(-2.0, 3.0, 2.5, 3.4, 40.2, 43.8)):                           # its pad, 0.6 into the board's back
        X.uni(H, b)
    # a 45 deg gusset 1.0 in the corner between the arm's back and its root
    g = X.wbox(ROOT_X - 1.0, ROOT_X, 0.3, 1.3, 40.2, 43.8)
    u = k.unit((1, 1, 0)); v = k.unit((-1, 1, 0))
    X.sec(g, X.obox((ROOT_X - 0.5 + 2.0 * u[0], 0.8 + 2.0 * u[1], 42.0), u, v, 4.0, 6.0, 3.6))
    X.uni(H, g)
    # the bay's roof (the top plate's underside, which prints on the support's interface) relieved 0.2 over the radar and over its
    # way in from behind: 0.4 over the board's top edge, the plate 1.6 there
    X.dif(H, X.wbox(23.3, TAB_X[1], TAB_Y[0] - 0.1, FACE_Y, 51.1, ROOF_Z))
    # the land under the M3's head: the tab's outer face relieved either side of it
    X.dif(H, X.wbox(TAB_X[0] - 0.1, RELIEF_X, TAB_Y[0] - 0.1, LAND_Y[0], 53.0, TAB_Z[1] + 0.1))
    X.dif(H, X.wbox(TAB_X[0] - 0.1, RELIEF_X, LAND_Y[1], TAB_Y[1] + 0.1, 53.0, TAB_Z[1] + 0.1))
    # the tie slot through the top plate
    X.dif(H, X.wbox(TIE[0], TIE[1], TIE[2], TIE[3], 51.1, 53.1))
    # the slot for the holder's M3 (Ø3.4), 0.4 either way along y
    for yy in (M3[0] - 0.4, M3[0] + 0.4):
        X.dif(H, X.cyl((TAB_X[0] - 0.5, yy, M3[1]), (RIB_X[1] + 0.5, yy, M3[1]), 1.7))
    X.dif(H, X.wbox(TAB_X[0] - 0.5, RIB_X[1] + 0.5, M3[0] - 0.4, M3[0] + 0.4, M3[1] - 1.7, M3[1] + 1.7))
    # the M2s: pilot Ø1.6 right through; the head's rim and cone cut where they meet the block; room for the head and the driver
    # behind the block (0.2 round the Ø3.8 head)
    for x, z in SCR:
        X.dif(H, X.cyl((x, BLOCK_Y - 0.1, z), (x, POST_END + 0.1, z), 0.8))
        X.dif(H, m2(k, X, x, z, head_only=True))
        X.dif(H, X.cyl((x, -12.0, z), (x, BLOCK_Y, z), 2.1))
    # the blocks under the heads, behind the ledge's face: the outer half only, as today's. Beside the board's long edges they stand
    # SIDE off, like the -x wall; between each pilot and the board the pilot is open (the screw's shank lies against the edge)
    X.dif(H, X.wbox(RADAR[0] - SIDE, RADAR[1] + SIDE, BLOCK_Y - 0.1, FACE_Y, 28.8, 51.2))
    X.dif(H, X.wbox(SCR[0][0], RADAR[0], BLOCK_Y - 0.1, FACE_Y, SCR[0][1] - 0.8, SCR[0][1] + 0.8))
    X.dif(H, X.wbox(RADAR[1], SCR[1][0], BLOCK_Y - 0.1, FACE_Y, SCR[1][1] - 0.8, SCR[1][1] + 0.8))
    X.dif(H, X.tbm.copy(k.c['b9_radar']))
    print('RADAR_HOLDER (sixth build): %.3f mm3, lumps %d, faces %d, world box %s' % (X.vol(H), H.lumps.count, H.faces.count, [round(v, 2) for v in k.wbb(X, H)]))
    for q in ('b9_holder_v1', 'b9_holder_v2'):
        if q in k.c:
            a = k.c[q]
            print('against %s (%.3f): in both %.3f, new only %.3f, gone %.3f' % (q, X.vol(a), X.xv(H, a), X.vol(H) - X.xv(H, a), X.vol(a) - X.xv(a, H)))
    if 'b9_screws' in k.c:
        print('the radar\'s screws in the holder (their thread): %.3f mm3' % X.xv(H, k.c['b9_screws']))
    k.c['b9_holder'] = H


def box(k, X, **kw):
    B = X.tbm.copy(X.body('SPKBOX_L')); v0 = X.vol(B)
    blk = X.wbox(*BLOCK)
    # 45 deg foot: the half-space x + y >= 29.0 (through (40, -11) and (46, -17)), in x 40..46, y -17..-11
    u = k.unit((1, 1, 0)); v = k.unit((-1, 1, 0))
    c = (40.0 + 20.0 * u[0], -11.0 + 20.0 * u[1], 57.6)
    foot = X.obox(c, u, v, 40.0, 60.0, 8.8)
    X.sec(foot, X.wbox(40.0, 46.0, -17.0, -11.0, 53.2, 62.0))
    X.uni(blk, foot)
    add = X.vol(blk) - X.xv(blk, B)
    X.uni(B, blk)                                    # fills an earlier pilot too, if the block is already there
    X.dif(B, X.cyl((39.9, M3[0], M3[1]), (45.35, M3[0], M3[1]), PILOT_R))
    print('SPKBOX_L: %.3f -> %.3f (block and foot %.3f, of it new %.3f), lumps %d, faces %d; pilot Ø%.1f at (y %.2f, z %.1f), x 40.0..45.35' % (
        v0, X.vol(B), X.vol(blk), add, B.lumps.count, B.faces.count, 2 * PILOT_R, M3[0], M3[1]))
    k.c['b9_boxL'] = B


def lead(k, X, pts=None, **kw):
    pts = pts or R8
    t = None; L_ = 0.0; rows = []
    for a, b in zip(pts[:-1], pts[1:]):
        c = X.cyl(a, b, LEAD_R); t = c if t is None else X.uni(t, c)
        n = math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3))); L_ += n; rows.append(round(n, 2))
    for p in pts[1:-1]:
        X.uni(t, X.sph(p, LEAD_R))
    print('LEAD_RADAR laid: %d pieces %s, %.1f long along its axis, %.3f mm3, lumps %d' % (len(pts) - 1, rows, L_, X.vol(t), t.lumps.count))
    k.c['b9_lead'] = t; k.c['b9_lead_len'] = L_; k.c['b9_lead_pts'] = pts


def _main(stage, kw):
    k = L['load'](); X = k.K(); k.budget(75)
    print(L['stamp'](), 'before', X.state())
    {'radar': radar, 'screws': screws, 'holder': holder, 'box': box, 'lead': lead}[stage](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(stage, **kw):
    L['out']('p86_%s.txt' % stage, _main, stage, kw)
