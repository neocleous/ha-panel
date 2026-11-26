# Block 9: three read-only probes behind the holder's second build. They were first run on 2026-11-26 as one-off calls that were
# not saved as files (p90_today_screws.txt, p90_clip_pilot.txt, p90_arm_joint.txt); this file is those probes written down, and it
# was run again after the last put. READ-ONLY: temporary bodies only.
#   'today'   today's two radar screws in the shell's pocket, read on the hidden copies of version 69 (LD2410C_env_F_v69,
#             SCREWS_M2x6_env_v69) and on the shell: where each screw's head and tip stand along its axis from the radar's face
#             plane, its tilt to the face's normal, and where the shell is solid round it. The holder's screws copy these figures.
#   'pilot'   the self-cut M3 pilots in the two boxes (holes lying along x, r 1.2 to 1.4), the left clip's slot, and the left box's
#             walls round its clip pilot: the record the holder's pilot follows (FDM9: 2.7 across).
#   'joint'   the arm's joint to the holder at z 42: p82's first build (k.c['b9_holder_v1'], if it is still held) beside the
#             model's holder.
# Run: runpy.run_path(D + 'p90_b9_probes.py')['main'](stage)  -> p90_<stage>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
OLD = ((-82.25, -72.21, -33.59, -25.18, 115.35, 122.94), (-72.98, -62.94, -18.16, -9.75, 115.35, 122.94))   # today's two screws


def dot(a, b):
    return sum(a[i] * b[i] for i in range(3))


def today(k, X):
    R = X.body('LD2410C_env_F_v69'); S = X.body('SCREWS_M2x6_env_v69')
    fs = []
    for f in R.faces:
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
        fs.append((round(f.area * 100.0, 1), k.wv(nv), k.W(f.pointOnFace)))
    for a, n, p in fs:
        print('radar envelope (version 69): face %.1f mm2, normal %s, at %s' % (a, k.r2(n, 3), k.r2(p)))
    big = sorted(fs, key=lambda q: -q[0])[:2]
    front = [q for q in big if q[1][1] > 0][0]                       # the face toward the wall (its normal leans toward the screen)
    n = front[1]; p0 = front[2]
    print('the face toward the wall: normal %s through %s' % (k.r2(n, 3), k.r2(p0)))
    sh = X.wbox(-90.0, -55.0, -40.0, -2.0, 108.0, 146.0); X.sec(sh, X.tbm.copy(X.body('HOUSING_F_front')))
    rv = X.tbm.copy(R)
    for box in OLD:
        c = X.wbox(*box); X.sec(c, X.tbm.copy(S))
        if not c.faces.count:
            print('no screw in %s' % (box,)); continue
        cyl = max((f for f in c.faces if f.geometry.surfaceType == 1), key=lambda f: f.area)
        a = k.unit(k.wv(cyl.geometry.axis)); o = k.W(cyl.geometry.origin)
        if dot(a, n) < 0:
            a = tuple(-w for w in a)
        ts = []
        for e in c.edges:
            ev = e.evaluator; ok, t0, t1 = ev.getParameterExtents(); ok, pts = ev.getStrokes(t0, t1, 0.001)
            ts += [dot(tuple(k.W(p)[i] - o[i] for i in range(3)), a) for p in pts]
        tp = dot(tuple(p0[i] - o[i] for i in range(3)), n) / dot(a, n)       # where the axis crosses the face plane
        q = tuple(o[i] + tp * a[i] for i in range(3))
        print('screw %.3f mm3: axis %s through the face plane at %s; %.2f deg to the normal; along its axis from the face plane: %.3f (head\'s flat face) .. %.3f (tip)' % (
            X.vol(c), k.r2(a, 3), k.r2(q), math.degrees(math.acos(min(1.0, abs(dot(a, n))))), min(ts) - tp, max(ts) - tp))
        side = k.unit((n[1], -n[0], 0.0))                                      # along the face, level
        for lab, d in (('on the axis', (0, 0, 0)), ('1.5 to one side', tuple(1.5 * w for w in side)), ('1.5 to the other', tuple(-1.5 * w for w in side)),
                       ('1.5 up', (0, 0, 1.5)), ('1.5 down', (0, 0, -1.5))):
            A = tuple(q[i] + d[i] - 4.0 * a[i] for i in range(3)); B = tuple(q[i] + d[i] + 8.0 * a[i] for i in range(3))
            print('   bar %-17s shell solid %s; radar envelope %s   (0 = the face plane, + toward the wall)' % (
                lab, [(round(u - 4.0, 2), round(v - 4.0, 2)) for u, v in k.needle_t(X, [sh], A, B, 0.01)],
                [(round(u - 4.0, 2), round(v - 4.0, 2)) for u, v in k.needle_t(X, [rv], A, B, 0.01)]))


def pilot(k, X):
    for nm in ('SPKBOX_L', 'SPKBOX_R'):
        for h in k.holes_of(X.body(nm), 1.2, 1.4):
            print('%s hole/pin %s r %.3f from %s to %s, L %.2f, cov %.2f' % (nm, h['k'], h['r'], h['A'], h['B'], h['L'], h['cov']))
    c = X.body('TOUCH_CLIP_L')
    print('TOUCH_CLIP_L box %s' % k.wbb(X, c))
    for h in k.holes_of(c, 1.6, 1.8):
        print('TOUCH_CLIP_L hole/pin %s r %.3f from %s to %s, L %.2f' % (h['k'], h['r'], h['A'], h['B'], h['L']))
    B = X.tbm.copy(X.body('SPKBOX_L'))
    for lab, p0, p1, ax in (('along z at (x 45.0, y -7.05)', (45.0, -7.05, 28.0), (45.0, -7.05, 48.0), 2), ('along y at (x 45.0, z 38.0)', (45.0, -12.0, 38.0), (45.0, -2.0, 38.0), 1),
                            ('along x at (y -7.05, z 38.0)', (42.0, -7.05, 38.0), (52.0, -7.05, 38.0), 0)):
        print('left box at the clip\'s pilot, %s: %s' % (lab, [(round(p0[ax] + u, 2), round(p0[ax] + v, 2)) for u, v in k.needle_t(X, [B], p0, p1, 0.01)]))
    for lab, p0, p1, ax in (('along z at (x 43.0, y -7.35)', (43.0, -7.35, 50.0), (43.0, -7.35, 66.0), 2), ('along y at (x 43.0, z 57.6)', (43.0, -18.0, 57.6), (43.0, -2.0, 57.6), 1),
                            ('along x at (y -7.35, z 57.6)', (38.0, -7.35, 57.6), (50.0, -7.35, 57.6), 0)):
        print('left box at the holder\'s pilot, %s: %s' % (lab, [(round(p0[ax] + u, 2), round(p0[ax] + v, 2)) for u, v in k.needle_t(X, [B], p0, p1, 0.01)]))


def joint(k, X):
    print('The arm\'s joint to the holder at z 42.0: solid stretches of thin bars (0.01 square) through the root.')
    for lab, H in (('p82\'s first build (k.c b9_holder_v1)', k.c.get('b9_holder_v1')), ('the model\'s holder', X.tbm.copy(X.body('RADAR_HOLDER')))):
        if H is None:
            print('%s: not held any more' % lab); continue
        print('%s:' % lab)
        for y in (-2.5, -1.75, -1.705, -1.695, -1.6, 0.0):
            print('   along x at y %+.3f, from x 19: %s' % (y, [(round(19 + u, 2), round(19 + v, 2)) for u, v in k.needle_t(X, [H], (19.0, y, 42.0), (24.0, y, 42.0), 0.01)]))
        for x in (21.0, 21.5, 22.0, 22.095, 22.105, 22.2):
            print('   along y at x %.3f, from y -6.5: %s' % (x, [(round(-6.5 + u, 2), round(-6.5 + v, 2)) for u, v in k.needle_t(X, [H], (x, -6.5, 42.0), (x, 3.0, 42.0), 0.01)]))
        for x in (22.10, 21.50):
            s = X.wbox(x - 0.005, x + 0.005, -7.0, 3.0, 40.2, 43.8); X.sec(s, X.tbm.copy(H))
            print('   section at x %.2f (z 40.2..43.8): %.3f mm2' % (x, X.vol(s) / 0.01))


def _main(stage):
    k = L['load'](); X = k.K(); k.budget(75)
    print(L['stamp'](), 'before', X.state())
    {'today': today, 'pilot': pilot, 'joint': joint}[stage](k, X)
    print(L['stamp'](), 'after', X.state())


def main(stage):
    L['out']('p90_%s.txt' % stage, _main, stage)
