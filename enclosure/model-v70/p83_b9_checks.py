# Block 9: checks on the temporary bodies before the put (and after it, put=True: the model's bodies). READ-ONLY but for
# TMP_ bodies, deleted again.
#   'pairs'  each new or moved body (holder, radar, screws, lead, left box) against every body of the unit near it:
#            shared volume and the smallest distance
#   'fits'   the holder's own fits: standoffs and pad on the board, radar to the board's back, arm to the parts and the touch
#            lead, the +x post and the frame to the clip, the frame to the Pi, the tab on the block, the slot either way
# Run: runpy.run_path(D + 'p83_b9_checks.py')['main'](stage, put=False)  -> p83_<stage>.txt
import runpy
D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
NEW = {'RADAR_HOLDER': 'b9_holder', 'LD2410C_env_F': 'b9_radar', 'SCREWS_M2x6_env': 'b9_screws', 'LEAD_RADAR': 'b9_lead', 'SPKBOX_L': 'b9_boxL'}


def src(k, X, nm, put):
    if put or nm not in NEW:
        return X.tbm.copy(X.body(nm))
    return X.tbm.copy(k.c[NEW[nm]])


def dist(k, X, a, b):
    A = X.add(X.tbm.copy(a), 'TMP_a', show=False); B = X.add(X.tbm.copy(b), 'TMP_b', show=False)
    r = X.mm.measureMinimumDistance(A, B); out = (round(r.value * 10, 3), k.r2(k.W(r.positionOne)), k.r2(k.W(r.positionTwo)))
    A.deleteMe(); B.deleteMe(); return out


def near(a, b, m):
    a0 = a.minPoint.asArray(); a1 = a.maxPoint.asArray(); b0 = b.minPoint.asArray(); b1 = b.maxPoint.asArray()
    return all(a0[i] - m <= b1[i] and b0[i] - m <= a1[i] for i in range(3))


def pairs(k, X, put):
    names = [b.name for b in k.current(X, leads=True)]
    for nm in ('RADAR_HOLDER', 'LD2410C_env_F', 'LEAD_RADAR', 'SPKBOX_L', 'SCREWS_M2x6_env'):
        a = src(k, X, nm, put)
        if nm == 'SCREWS_M2x6_env':                   # only the two radar screws
            X.sec(a, X.wbox(18, 45, -8, 3, 27, 52))
        rows = []
        for o in names:
            if o == nm or k.late():
                continue
            b = src(k, X, o, put)
            if not near(a.boundingBox, b.boundingBox, 0.25):
                continue
            sh = X.xv(a, b)
            d = dist(k, X, a, b) if sh < 0.0005 else (0.0,)
            if sh >= 0.0005 or d[0] < 2.0:
                rows.append((round(sh, 3), d[0], o, d[1:] if len(d) > 1 else ''))
        rows.sort(key=lambda r: (-r[0], r[1]))
        print('%s:' % nm)
        for r in rows:
            print('   %-28s shared %9.3f  dist %6.3f %s' % (r[2], r[0], r[1], r[3]))
        if 'RADAR_HOLDER' not in names and nm != 'RADAR_HOLDER' and not put:
            h = src(k, X, 'RADAR_HOLDER', put)
            if near(a.boundingBox, h.boundingBox, 0.25):
                print('   %-28s shared %9.3f  dist %s' % ('RADAR_HOLDER', X.xv(a, h), dist(k, X, a, h)))


def fits(k, X, put):
    H = src(k, X, 'RADAR_HOLDER', put); R = src(k, X, 'LD2410C_env_F', put); B = src(k, X, 'SPKBOX_L', put)
    P = X.tbm.copy(X.body('TOUCH_PCB'))
    for lab, box in (('standoff A', (21.1, 23.3, -1.8, 2.9, 36, 38)), ('standoff B', (21.1, 23.3, -1.8, 2.9, 46, 48)),
                     ('standoff C (+x post)', (38.4, 42.6, -1.8, 2.9, 46.7, 50.9)), ('pad', (-2.1, 3.1, 2.4, 3.5, 40.1, 43.9))):
        c = X.wbox(*box); X.sec(c, X.tbm.copy(H))
        print('%-22s to the board: shared %.4f, front face y %s' % (lab, X.xv(c, P), round(k.wbb(X, c)[3], 3)))
    print('radar to the board\'s back: %s' % (dist(k, X, R, P),))
    arm = X.wbox(-2.0, 20.1, 1.2, 2.6, 40.1, 43.9); X.sec(arm, X.tbm.copy(H))
    for o in ('TOUCH_components_env', 'LEAD_TOUCH', 'TOUCH_PCB', 'LEAD_GPIO_B'):
        print('arm (x -2..20.1) to %s: %s' % (o, dist(k, X, arm, X.tbm.copy(X.body(o)))))
    for o in ('TOUCH_CLIP_L', 'PI5_F', 'PI5_F_cooler', 'HOUSING_F_front', 'LEAD_PI_POWER', 'LEAD_DSI', 'MAIN_J2_plug_env', 'SPK_L', 'HOUSING_F_plate'):
        print('holder to %s: %s' % (o, dist(k, X, H, X.tbm.copy(X.body(o)))))
    print('radar to TOUCH_CLIP_L: %s' % (dist(k, X, R, X.tbm.copy(X.body('TOUCH_CLIP_L'))),))
    print('holder to the left box (the tab on its block): %s; shared %.4f' % (dist(k, X, H, B), X.xv(H, B)))
    for dy in (-0.4, 0.4, -0.45, 0.45):
        t = X.move(X.tbm.copy(H), 0, dy, 0)
        print('holder moved %+.2f in y: shares %.4f with the box, %.4f with the board' % (dy, X.xv(t, B), X.xv(t, P)))
    # the pilot in the block, the wall to the chamber, the foot
    print('left box along the pilot axis (y -7.2, z 57.6), x 38..50: %s' % [(round(38 + a, 2), round(38 + b, 2)) for a, b in k.needle_t(X, [B], (38.0, -7.2, 57.6), (50.0, -7.2, 57.6), 0.01)])
    print('left box beside the pilot (y -9.5, z 57.6), x 38..50: %s' % [(round(38 + a, 2), round(38 + b, 2)) for a, b in k.needle_t(X, [B], (38.0, -9.5, 57.6), (50.0, -9.5, 57.6), 0.01)])
    for x in (40.5, 43.0, 45.5):
        print('left box at x %.1f, z 57.6, along y -20..-2: %s' % (x, [(round(-20 + a, 2), round(-20 + b, 2)) for a, b in k.needle_t(X, [B], (x, -20.0, 57.6), (x, -2.0, 57.6), 0.01)]))


def _main(stage, put):
    k = L['load'](); X = k.K(); k.budget(78)
    print(L['stamp'](), 'before', X.state())
    {'pairs': pairs, 'fits': fits}[stage](k, X, put)
    print(L['stamp'](), 'after', X.state())


def main(stage, put=False):
    L['out']('p83_%s%s.txt' % (stage, '_put' if put else ''), _main, stage, put)
