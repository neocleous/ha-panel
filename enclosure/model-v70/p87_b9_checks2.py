# Block 9: checks on the second build of the holder (p86) and on the lead as laid, before the put (put=False: temporary bodies in
# k.c) and after it (put=True: the model's bodies). READ-ONLY but for TMP_ bodies, deleted again.
#   'fits'   standoffs A, B, C and the pad on the board; the radar's face; the arm; the holder against what stands round it;
#            standoff C against the clip, the shell and the box; the tab's two lands (the rib on the block, the land under the
#            head) with the screw's head at the slot's middle and at both ends of its travel; the tie slot
#   'lead'   the laid lead against each lump of MAIN_plug_env and against the bodies along its run: shared volume and distance;
#            its lowest point over the Pi cooler's keep-out
# Run: runpy.run_path(D + 'p87_b9_checks2.py')['main'](stage, put=False)  -> p87_<stage>[_put].txt
import runpy, math
D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
NEW = {'RADAR_HOLDER': 'b9_holder', 'LD2410C_env_F': 'b9_radar', 'SCREWS_M2x6_env': 'b9_screws', 'LEAD_RADAR': 'b9_lead', 'SPKBOX_L': 'b9_boxL'}
M3 = (-7.35, 57.6)


def src(k, X, nm, put):
    if put or nm not in NEW:
        return X.tbm.copy(X.body(nm))
    return X.tbm.copy(k.c[NEW[nm]])


def dist(k, X, a, b):
    A = X.add(X.tbm.copy(a), 'TMP_a', show=False); B = X.add(X.tbm.copy(b), 'TMP_b', show=False)
    r = X.mm.measureMinimumDistance(A, B); out = (round(r.value * 10, 3), k.r2(k.W(r.positionOne)), k.r2(k.W(r.positionTwo)))
    A.deleteMe(); B.deleteMe(); return out


def crop(k, X, body, box):
    c = X.wbox(*box); X.sec(c, X.tbm.copy(body)); return c


def fits(k, X, put):
    H = src(k, X, 'RADAR_HOLDER', put); R = src(k, X, 'LD2410C_env_F', put); B = src(k, X, 'SPKBOX_L', put)
    P = X.tbm.copy(X.body('TOUCH_PCB'))
    print('RADAR_HOLDER %.3f mm3, lumps %d, faces %d, box %s' % (X.vol(H), H.lumps.count, H.faces.count, k.wbb(X, H)))
    for lab, box in (('standoff A', (21.0, 23.4, -1.6, 2.9, 35.9, 38.1)), ('standoff B', (21.0, 23.4, -1.6, 2.9, 45.9, 48.1)),
                     ('standoff C', (42.2, 44.6, 0.7, 2.9, 46.5, 50.1)), ('pad', (-2.1, 3.1, 2.6, 3.5, 40.1, 43.9))):
        c = crop(k, X, H, box)
        print('%-12s box %s: shared with the board %.4f; to the board %s' % (lab, k.wbb(X, c), X.xv(c, P), dist(k, X, c, P)[0]))
    print('the +x post\'s end (crop x 38..43, y 0..3, z 50.05..51): %s' % (k.wbb(X, crop(k, X, H, (38.0, 43.0, 0.0, 3.0, 50.05, 51.0))) if X.vol(crop(k, X, H, (38.0, 43.0, 0.0, 3.0, 50.05, 51.0))) > 0 else 'nothing above z 50.05 in front of y 0'))
    S = src(k, X, 'SCREWS_M2x6_env', put)
    for lab, (x, z), rr in (('-x', (22.5, 31.6), 2.8), ('+x', (40.5, 48.8), 2.4)):
        post = crop(k, X, H, (x - rr - 0.05, x + rr + 0.05, -4.3, 2.4, z - rr - 0.05, z + rr + 0.05))
        sc = X.wbox(x - 2.0, x + 2.0, -6.0, 1.0, z - 2.0, z + 2.0); X.sec(sc, X.tbm.copy(S))
        front = crop(k, X, H, (x - rr, x + rr, 1.5, 2.5, z - rr, z + rr))
        print('M2 %s at (x %.1f, z %.1f): screw along y %s; its thread in the holder %.3f mm3; the post\'s front end to the board %s' % (
            lab, x, z, k.wbb(X, sc)[2:4], X.xv(sc, H), dist(k, X, front, P)[0]))
        for nm, dx, dz in (('on the axis', 0, 0), ('0.9 toward the radar', 0.9 if lab == '-x' else -0.9, 0), ('0.9 away from the radar', -0.9 if lab == '-x' else 0.9, 0),
                           ('0.9 up', 0, 0.9), ('0.9 down', 0, -0.9)):
            st = k.needle_t(X, [H], (x + dx, -7.0, z + dz), (x + dx, 3.0, z + dz), 0.01)
            print('      holder along y, %-24s %s' % (nm, [(round(-7 + a, 2), round(-7 + b, 2)) for a, b in st]))
        for nm, dx, dz in (('toward the radar', 1 if lab == '-x' else -1, 0), ('away from the radar', -1 if lab == '-x' else 1, 0), ('up', 0, 1), ('down', 0, -1)):
            row = []
            for y in (-3.5, -2.0, -0.5, 1.0, 2.0):
                st = k.needle_t(X, [H], (x, y, z), (x + 4.0 * dx, y, z + 4.0 * dz), 0.01)
                w = [round(b - max(a, 0.8), 2) for a, b in st if b > 0.8 and a < 1.2]
                row.append((y, w[0] if w else 0.0))
            print('      wall round the pilot %-20s at y: %s' % (nm, row))
    print('the head of the +x screw to the holder (crop behind y -4.2): %s' % (dist(k, X, crop(k, X, H, (36.0, 45.0, -11.0, -4.2001, 44.0, 62.5)), X.cyl((40.5, -5.19, 48.8), (40.5, -4.89, 48.8), 1.9)),))
    print('the head of the -x screw to the holder (crop behind y -4.2): %s' % (dist(k, X, crop(k, X, H, (18.0, 28.0, -11.0, -4.2001, 27.0, 40.0)), X.cyl((22.5, -5.19, 31.6), (22.5, -4.89, 31.6), 1.9)),))
    print('radar to the board\'s back: %s' % (dist(k, X, R, P),))
    arm = crop(k, X, H, (-2.0, 20.1, 1.2, 2.6, 40.1, 43.9))
    print('arm\'s root, along y at (x 22.0, z 42.0): %s; along x at (y 0.0, z 42.0): %s; gusset along x at (y 1.0, z 42.0): %s' % (
        [(round(-6.5 + a, 2), round(-6.5 + b, 2)) for a, b in k.needle_t(X, [H], (22.0, -6.5, 42.0), (22.0, 3.0, 42.0), 0.01)],
        [(round(17 + a, 2), round(17 + b, 2)) for a, b in k.needle_t(X, [H], (17.0, 0.0, 42.0), (25.0, 0.0, 42.0), 0.01)],
        [(round(17 + a, 2), round(17 + b, 2)) for a, b in k.needle_t(X, [H], (17.0, 1.0, 42.0), (25.0, 1.0, 42.0), 0.01)]))
    for o in ('TOUCH_components_env', 'LEAD_TOUCH', 'TOUCH_PCB', 'LEAD_GPIO_B'):
        print('arm (x -2..20.1) to %s: %s' % (o, dist(k, X, arm, X.tbm.copy(X.body(o)))))
    for o in ('TOUCH_CLIP_L', 'PI5_F', 'PI5_F_cooler', 'HOUSING_F_front', 'LEAD_PI_POWER', 'LEAD_DSI', 'MAIN_J2_plug_env', 'SPK_L', 'HOUSING_F_plate',
              'KO_K7_fan', 'LEAD_LCD_5V', 'GPIO_plugB_env', 'DRV_screw_heads_env', 'LEAD_USB_RESP'):
        print('holder to %s: %s' % (o, dist(k, X, H, X.tbm.copy(X.body(o)))))
    cp = crop(k, X, H, (38.4, 44.6, -1.8, 2.9, 46.5, 50.1))
    for o in ('TOUCH_CLIP_L', 'HOUSING_F_front', 'SPK_L', 'TOUCH_PCB'):
        print('standoff C and its foot to %s: %s' % (o, dist(k, X, cp, X.tbm.copy(X.body(o)))))
    print('standoff C and its foot to the left box: %s' % (dist(k, X, cp, B),))
    print('standoff C and its foot to the radar\'s screws: %s' % (dist(k, X, cp, src(k, X, 'SCREWS_M2x6_env', put)),))
    print('radar to TOUCH_CLIP_L: %s' % (dist(k, X, R, X.tbm.copy(X.body('TOUCH_CLIP_L'))),))
    print('holder to the left box (the rib on its block): %s; shared %.4f' % (dist(k, X, H, B), X.xv(H, B)))
    for dy in (-0.4, 0.4, -0.45, 0.45):
        t = X.move(X.tbm.copy(H), 0, dy, 0)
        print('holder moved %+.2f in y: shares %.4f with the box, %.4f with the board, %.4f with the clip, %.4f with the shell' % (
            dy, X.xv(t, B), X.xv(t, P), X.xv(t, X.tbm.copy(X.body('TOUCH_CLIP_L'))), k.xvol(X, t, 'HOUSING_F_front')))
    # the two lands
    rib = crop(k, X, H, (39.6001, 40.1, -11.0, -3.0, 51.0, 62.1))
    print('rib (beyond x 39.6): box %s, %.3f mm3' % (k.wbb(X, rib), X.vol(rib)))
    t = X.move(X.tbm.copy(rib), 0.01, 0, 0)
    print('   its bearing on the block\'s face: %.2f mm2' % (X.xv(t, B) / 0.01))
    land = crop(k, X, H, (36.5, 36.9999, -11.0, -3.0, 53.0, 62.1))
    print('land under the head (x below 37.0): box %s, %.3f mm3 (%.2f mm2 of face)' % (k.wbb(X, land), X.vol(land), X.vol(land) / 0.4))
    for e in (-0.4, 0.0, 0.4):
        y = M3[0] + e
        ring = X.cyl((36.6, y, M3[1]), (36.7, y, M3[1]), 2.85)
        X.dif(ring, X.cyl((36.5, y, M3[1]), (36.8, y, M3[1]), 1.5))
        b = X.xv(ring, H) / 0.1
        rr = crop(k, X, H, (36.6, 36.7, y - 2.9, y + 2.9, M3[1] - 2.9, M3[1] + 2.9)); X.sec(rr, ring)
        print('   screw %+.1f from the slot\'s middle (axis y %.1f): the head (Ø5.7) bears on %.2f mm2, over y %s; the axis stands %.2f from the rib\'s nearer edge and %.2f from the land\'s' % (
            e, y, b, k.wbb(X, rr)[2:4] if X.vol(rr) > 0 else None, 0.6 - abs(e), 1.0 - abs(e)))
    print('tab beside the lands, along x at (y -9.5, z 60): %s' % k.needle_t(X, [H], (35.0, -9.5, 60.0), (41.0, -9.5, 60.0), 0.01))
    print('tab at the lands, along x at (y %.2f, z 60.5): %s' % (M3[0], k.needle_t(X, [H], (35.0, M3[0], 60.5), (41.0, M3[0], 60.5), 0.01)))
    # the tie slot
    print('top plate along y at (x 25.0, z 52.1), from y -11: %s' % k.needle_t(X, [H], (25.0, -11.0, 52.1), (25.0, -1.0, 52.1), 0.01))
    print('top plate along x at (y -8.5, z 52.1), from x 21: %s' % k.needle_t(X, [H], (21.0, -8.5, 52.1), (41.0, -8.5, 52.1), 0.01))
    print('top plate along z at (x 25.0, y -9.8), from z 50: %s' % k.needle_t(X, [H], (25.0, -9.8, 50.0), (25.0, -9.8, 54.0), 0.01))
    # the block's pilot, as before
    print('left box along the pilot axis (y %.2f, z 57.6), x 38..50: %s' % (M3[0], [(round(38 + a, 2), round(38 + b, 2)) for a, b in k.needle_t(X, [B], (38.0, M3[0], 57.6), (50.0, M3[0], 57.6), 0.01)]))
    print('left box across the pilot at x 43.0: along y at z 57.6 %s; along z at y %.2f %s' % (
        [(round(-18 + a, 2), round(-18 + b, 2)) for a, b in k.needle_t(X, [B], (43.0, -18.0, 57.6), (43.0, -2.0, 57.6), 0.01)], M3[0],
        [(round(50 + a, 2), round(50 + b, 2)) for a, b in k.needle_t(X, [B], (43.0, M3[0], 50.0), (43.0, M3[0], 66.0), 0.01)]))
    print('left box at x 41.0, z 57.6, along y -20..-2 (the foot): %s' % [(round(-20 + a, 2), round(-20 + b, 2)) for a, b in k.needle_t(X, [B], (41.0, -20.0, 57.6), (41.0, -2.0, 57.6), 0.01)])


def lead(k, X, put):
    T = src(k, X, 'LEAD_RADAR', put); H = src(k, X, 'RADAR_HOLDER', put)
    print('lead %.3f mm3, box %s' % (X.vol(T), k.wbb(X, T)))
    b = X.body('MAIN_plug_env')
    for l in b.lumps:
        lt = X.tbm.copy(l)
        sh = X.xv(T, lt)
        print('MAIN_plug_env lump %-50s shared %8.3f  dist %s' % (k.wbb(X, lt), sh, dist(k, X, T, lt) if sh < 0.0005 else 0.0))
    for l in X.body('MAIN_conn').lumps:
        lt = X.tbm.copy(l)
        if lt.boundingBox.maxPoint.x * 10 - k.XC < -20:
            print('MAIN_conn lump %-50s dist %s' % (k.wbb(X, lt), dist(k, X, T, lt)))
    for o in ('KO_K7_fan', 'PI5_F_cooler', 'PI5_F', 'LEAD_PI_POWER', 'MAIN_J2_plug_env', 'LEAD_TOUCH', 'LEAD_GPIO_B', 'LEAD_GPIO_A1', 'LEAD_GPIO_A2', 'LEAD_LCD_5V',
              'LEAD_PIGTAIL_20V', 'LEAD_SPK_R', 'LEAD_SPK_L', 'LEAD_BME680', 'LEAD_VEML', 'LEAD_DSI', 'KO_capkey_BR', 'KO_capkey_SR', 'KO_capkey_BL', 'KO_capkey_SL', 'KO_K5_LR',
              'MAIN_pcb', 'MAIN_tall', 'MAIN_low', 'RESP_CARRIER', 'HOUSING_F_plate', 'HOUSING_F_front', 'SPKBOX_R', 'GPIO_plugA_env', 'GPIO_plugB_env', 'TOUCH_CLIP_L', 'SPKBOX_L'):
        if k.late():
            print('time'); break
        ob = src(k, X, o, put) if o in NEW else X.tbm.copy(X.body(o))
        sh = X.xv(T, ob)
        print('lead to %-18s shared %8.3f  dist %s' % (o, sh, dist(k, X, T, ob) if sh < 0.0005 else 0.0))
    print('lead to the holder: shared %.4f, dist %s' % (X.xv(T, H), dist(k, X, T, H)))
    print('lead to the radar: %s' % (dist(k, X, T, src(k, X, 'LD2410C_env_F', put)),))
    # over the keep-out's plan (x -15.75..14.25, y -38.7..-7.6): the lead's lowest point there
    over = X.wbox(-15.75, 14.25, -38.7, -7.6, 20.0, 120.0); X.sec(over, T)
    if X.vol(over) > 0:
        bb = k.wbb(X, over)
        print('over the fan keep-out\'s plan the lead runs z %.2f..%.2f (the keep-out\'s top is z 35.8): %.2f above it at its lowest' % (bb[4], bb[5], bb[4] - 35.8))


def _main(stage, put):
    k = L['load'](); X = k.K(); k.budget(78)
    print(L['stamp'](), 'before', X.state())
    {'fits': fits, 'lead': lead}[stage](k, X, put)
    print(L['stamp'](), 'after', X.state())


def main(stage, put=False):
    L['out']('p87_%s%s.txt' % (stage, '_put' if put else ''), _main, stage, put)
