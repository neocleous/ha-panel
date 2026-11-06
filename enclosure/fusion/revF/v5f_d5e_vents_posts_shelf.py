# rev F audit-response d5e (2026-11-06): vents (finding 35, Daniel 10:27 decision 1 a: "vents about 5× larger at the floor
#   intake and behind the cloth"), exhaust bridge posts (finding 10), shelf land (finding 6). Probes: v5f_d5c / v5f_d5d.
#   HOUSING_F_front (old -> HOUSING_F_front_d5b, hidden):
#     intake: the 10 × 10 Ø2 field on 3.0 pitch (x_rel −14.25…12.75, y −36.7…−9.7) extended on the same grid to x_rel
#       −41.25…39.75, y −57.7…−6.7 (28 × 18 positions), skipping positions within 5.5 of the four Pi bosses; all inside the
#       underside's inner plate (the strip recess starts at y −4.5), the speaker boxes start at x_rel ±46.
#     posts: two 1.2-wide posts per exhaust row (x_rel ±(6.2…7.4), rows z 162.5–165.5 / 167.0–170.0), the wall's own profile
#       (REF_F_outer − 0.7 recess − (INNER_E − 0.7 layer)) -> spans 40.8 -> 13.0 / 12.4 / 13.0.
#     shelf: 0.4 vertical land at the tip (y −23.3, z 177.4 -> 177.0), 45° underside from there to the bar face (x_rel ±60).
#   HOUSING_F_door (old -> HOUSING_F_door_d5b, hidden):
#     12 vertical slots 3.0 wide, cut along y, at x_rel −24…42 (6.0 pitch; none on the BME680 side, x < −25), z 66 to
#     min(110, lip lower edge − 6) (lip edge from v5f_d5d: 116.3 at ±30, 111.5 at ±35, ≈ 102 at 42).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
F, D = 'HOUSING_F_front', 'HOUSING_F_door'
EXPECT = {F: 236.3673, D: 51.1617}
COPIES = {F: 'HOUSING_F_front_d5b', D: 'HOUSING_F_door_d5b'}
PI = ((18.35, -5.5), (-39.65, -5.5), (18.35, -54.5), (-39.65, -54.5))
GX = [-41.25 + 3.0 * i for i in range(28)]
GY = [-57.7 + 3.0 * j for j in range(18)]
OLD = (lambda x, y: -14.3 <= x <= 12.8 and -36.75 <= y <= -9.65)
ROWS = ((162.5, 165.5), (167.0, 170.0))
POSTS = ((6.2, 7.4), (-7.4, -6.2))
LIP = {-24: 120.8, -18: 123.8, -12: 125.9, -6: 127.0, 0: 127.4, 6: 127.0, 12: 125.9, 18: 123.8, 24: 120.8, 30: 116.3,
       36: 110.5, 42: 102.5}
SLOT_W, SLOT_Z0, SLOT_ZMAX = 3.0, 66.0, 110.0


def stadium_y(X, x, z0, z1, r=1.5, y0=-95.0, y1=-60.0):
    t = X.wbox(XC + x - r, XC + x + r, y0, y1, z0 + r, z1 - r)
    for z in (z0 + r, z1 - r):
        X.union(t, X.tbm.createCylinderOrCone(Dw(XC + x, y0, z), r / 10, Dw(XC + x, y1, z), r / 10))
    return t


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard: %s %s (expected %s)' % (k, None if b is None else round(b.volume, 4), v))
        for n in COPIES.values():
            if X.body(n) is not None:
                raise RuntimeError('%s exists already' % n)
        for k, n in COPIES.items():
            c = X.add(X.tbm.copy(X.body(k)), n); c.isLightBulbOn = False
        fb = X.body(F); db = X.body(D)
        v0f, v0d = fb.volume, db.volume
        # ---- intake holes
        pts = []
        for x in GX:
            for y in GY:
                if OLD(x, y):
                    continue
                if min(math.hypot(x - px, y - py) for px, py in PI) < 5.5:
                    continue
                pts.append((x, y))
        out['new_holes'] = len(pts)
        holes = None
        for (x, y) in pts:
            h = X.wcyl_z(XC + x, y, 1.0, -0.5, 3.0); holes = h if holes is None else X.union(holes, h)
        out['t_union'] = round(time.time() - t0, 1)
        exp = len(pts) * math.pi * 1.0 * 2.5
        cutv = vol_x(X, holes, X.tbm.copy(fb))
        out['holes_cut_mm3'] = [round(cutv, 1), round(exp, 1)]
        if abs(cutv - exp) > 0.02 * exp:
            raise RuntimeError('intake holes cut %s mm3, expected %s (a hole meets a feature)' % (round(cutv, 1), round(exp, 1)))
        X.combine(fb, [X.add(holes, 'D5E_holes_tmp')], op=CUT); fb = X.body(F)
        out['after_holes'] = round(fb.volume, 4)
        # ---- exhaust posts
        wallp = tb_copy(X, 'REF_F_outer'); X.diff(wallp, tb_copy(X, 'TOOL_outer_skin_0p7'))
        cav = tb_copy(X, 'INNER_E'); X.diff(cav, tb_copy(X, 'TOOL_inner_skin_0p7')); X.diff(wallp, cav)
        po = None
        for (z0, z1) in ROWS:
            for (x0, x1) in POSTS:
                p = X.wbox(XC + x0, XC + x1, -62.0, -44.0, z0, z1); inter(X, p, X.tbm.copy(wallp))
                po = p if po is None else X.union(po, p)
        pnew = X.tbm.copy(po); X.diff(pnew, X.tbm.copy(fb))
        out['posts_mm3'] = [round(po.volume * 1000, 2), round(pnew.volume * 1000, 2)]
        out['posts_box'] = [round(v, 2) for v in wbb(X, po)]
        X.combine(fb, [X.add(po, 'D5E_posts_tmp')]); fb = X.body(F)
        # ---- shelf land
        sb = X.wbox(XC - 60.0, XC + 60.0, -23.3, -21.4, 175.6, 177.4)
        n45 = (0.0, 1.0 / math.sqrt(2), 1.0 / math.sqrt(2)); a2 = (0.0, 1.0 / math.sqrt(2), -1.0 / math.sqrt(2))
        hs = lbox(X, (0.0, -23.3 + 5.0 * n45[1], 177.0 + 5.0 * n45[2]), (1, 0, 0), a2, 130.0, 20.0, 10.0)
        inter(X, sb, hs)
        snew = X.tbm.copy(sb); X.diff(snew, X.tbm.copy(fb))
        out['shelf_add_mm3'] = round(snew.volume * 1000, 2)
        X.combine(fb, [X.add(sb, 'D5E_shelf_tmp')]); fb = X.body(F)
        out['front_cm3'] = [round(v0f, 4), round(fb.volume, 4)]; out['front_lumps'] = fb.lumps.count
        out['t_front'] = round(time.time() - t0, 1)
        # ---- door slots
        sl = None; sinfo = []
        for x, lip in sorted(LIP.items()):
            z1 = min(SLOT_ZMAX, lip - 6.0)
            s = stadium_y(X, float(x), SLOT_Z0, z1)
            cv = vol_x(X, s, X.tbm.copy(db))
            sinfo.append([x, round(z1, 1), round(cv, 1), round(SLOT_W * (z1 - SLOT_Z0 - 3.0) + math.pi * 2.25, 1)])
            sl = s if sl is None else X.union(sl, s)
        out['slots_x_ztop_cut_area'] = sinfo
        out['slot_area_mm2'] = round(sum(r[3] for r in sinfo), 1)
        X.combine(db, [X.add(sl, 'D5E_slots_tmp')], op=CUT); db = X.body(D)
        out['door_cm3'] = [round(v0d, 4), round(db.volume, 4)]; out['door_lumps'] = db.lumps.count
        # ---- probes
        P = lambda b, x, y, z: X.inside(b, XC + x, y, z)
        pr = {'hole_new_open': not P(fb, -41.25, -57.7, 1.2) and not P(fb, 39.75, -6.7, 1.2) and not P(fb, 27.75, -30.7, 1.2),
              'web_between': P(fb, -39.75, -57.7, 1.2),
              'pi_boss_intact': P(fb, 18.35 + 3.0, -5.5, 5.0) and P(fb, -39.65 + 3.0, -54.5, 5.0),
              'post_solid': P(fb, 6.8, -53.3, 164.0) or P(fb, 6.8, -53.8, 164.0),
              'slot_beside_post_open': not P(fb, 3.0, -53.3, 164.0) and not P(fb, 3.0, -53.8, 164.0),
              'shelf_land': P(fb, 0.0, -23.2, 177.1) and P(fb, 40.0, -23.2, 177.1) and not P(fb, 0.0, -23.4, 177.1),
              'shelf_45': P(fb, 0.0, -22.5, 176.4) and not P(fb, 0.0, -22.9, 176.4),
              'door_slot_open': not P(db, 0.0, -75.0, 90.0) or not P(db, 0.0, -76.0, 90.0),
              'door_web': P(db, 3.0, -75.4, 90.0) or P(db, 3.0, -76.4, 90.0)}
        out['probes'] = pr
        out['all_probes_ok'] = all(pr.values())
        out['front_x_cap'] = vol_x(X, X.tbm.copy(sb), tb_copy(X, 'HOUSING_F_cap'))
        mic = {}
        for n in ('MIC_strip_L_env', 'MIC_strip_R_env'):
            if X.body(n) is not None:
                mic[n] = vol_x(X, X.tbm.copy(sb), tb_copy(X, n))
        out['shelf_x_mic'] = mic
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        out['split'] = [b.name for b in X.comp.bRepBodies if ' (' in b.name and b.name.startswith('HOUSING')]
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d5e_vents_posts_shelf', 'run', out)
    print(json.dumps(out, separators=(',', ':')))
