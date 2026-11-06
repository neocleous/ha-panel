# rev F d19d (2026-11-06): printability fixes (Daniel 21:49), hidden material only - nothing seen from outside changes.
#   A (evaluated, not applied). A 2.0 rib under the LD2410C cradle's floor (d19a: 329 mm² flat at z 114.35, a ~112 mm support
#      tower floor down) from the right side wall (1.0 into it) to the floor's free edge, its underside at 46°. Candidates
#      RIB_CANDS (y0, back to front) vs every part and keep-out at rest and the BME680 board's and hood's paths (along -w,
#      d9g / d12a, here from 14 out), the LD2410C's (run 26) and the right box's B5j-3 (its top from z 79, the only part that
#      reaches z 85 lifted). The floor is a 31° rotated pad joined to the side wall only at y -26.5…-21 and to the front wall
#      at its front corner; the hood slides in under its back half, so ribs behind y -20 block the hood and ribs in front of
#      it leave the back half and its tall support as they are.
#   B (applied). MAIN_BRACKET, both halves: a 46° gusset under each lower board-boss arm (z 33.5) over the column's y range,
#      from 0.5 inside the column to x ±38.0 and up to z 35.7 (MAIN_front_env starts at 35.8), minus the Ø4.0 insert hole.
#      Checked: parts at rest, the half's own path (runs 17 / 18), the main board's (19), the Pi adapter's (27), the door's (31).
#   Every check is on the added material (new solid minus old). Old bracket -> MAIN_BRACKET_d19 (hidden). DRY (default True)
#   reports only. Writes ~/Documents/HA_panel_renders/d_data/data/d19d_{dry,run}.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py'), encoding='utf-8').read())
import traceback
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d19d_%s.json')
AUDD = os.path.expanduser('~/Documents/audit/data')
NEWP = ['TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'BME_HOOD', 'FOAM_bme_env', 'FOAM_bme_top_env', 'HOUSING_F_door']
EXP = {'HOUSING_F_front': 235.2269, 'MAIN_BRACKET': 6.2403}
K46 = math.tan(math.radians(46.0))
FT = (0.6504, -0.7596, 0.0); FU = (0.1139, 0.0976, 0.9887); FW = (0.751, 0.643, -0.15)   # BME680 tray frame t, u, w (d9c)
RIB_CANDS = [-24.5, -23.0, -21.5, -20.0, -18.5, -17.0]
RIB_T = 2.0
CROP_A = [-100.0, -55.0, -36.0, -4.0, 70.0, 120.0]
BOXR_PATH = [(42, -70, 6), (42, -1, 6), (1, -1, 6), (1, -1, 0), (0, -1, 0), (0, 0, 0)]
BRK_PATH = {1: [(-1.5, -30, 0.5), (-1.5, 0, 0.5), (0, 0, 0.5), (0, 0, 0)], -1: [(1.5, -30, 0.5), (1.5, 0, 0.5), (0, 0, 0.5), (0, 0, 0)]}
BRK_FIXED = {1: ['HOUSING_F_front', 'PI5_F', 'PI5_F_cooler', 'USBA_plug_env', 'USBA_cable_env', 'SPKBOX_L', 'SPK_L', 'TOUCH_PCB',
                 'GPIO_plugA_env', 'GPIO_plugB_env'],
             -1: ['HOUSING_F_front', 'PI5_F', 'PI5_F_cooler', 'SPKBOX_R', 'SPK_R', 'TOUCH_PCB', 'GPIO_plugA_env', 'GPIO_plugB_env',
                  'PIPWR_a_env', 'LEAD_PI_POWER']}


def unit(v):
    n = math.sqrt(sum(c * c for c in v)); return tuple(c / n for c in v)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def hs(X, p0, n, L=300.0):                                   # half-space n·(p - p0) <= 0 (p0 in x_rel) as a box of side L
    n = unit(n); a2 = unit(cross(n, (0.0, 0.0, 1.0)) if abs(n[2]) < 0.9 else cross(n, (1.0, 0.0, 0.0)))
    return lbox(X, tuple(p0[i] - n[i] * L / 2 for i in range(3)), n, a2, L, L, L)


def steps_of(path, st=0.5):
    pts = [tuple(float(c) for c in path[0])]
    for a, b in zip(path[:-1], path[1:]):
        L = math.sqrt(sum((b[i] - a[i]) ** 2 for i in range(3))); n = max(1, int(math.ceil(L / st - 1e-9)))
        pts += [tuple(a[i] + (b[i] - a[i]) * k / n for i in range(3)) for k in range(1, n + 1)]
    return pts


def ovl(a, b, m=0.0):
    return not (a[1] < b[0] - m or b[1] < a[0] - m or a[3] < b[2] - m or b[3] < a[2] - m or a[5] < b[4] - m or b[5] < a[4] - m)


def lsq_plane(pts):                                          # x = a + b z + c y through [(x, y, z)]
    A = [[0.0] * 3 for _ in range(3)]; r = [0.0] * 3
    for (x, y, z) in pts:
        v = (1.0, z, y)
        for i in range(3):
            r[i] += v[i] * x
            for j in range(3):
                A[i][j] += v[i] * v[j]
    for i in range(3):                                       # Gauss-Jordan
        p = max(range(i, 3), key=lambda k: abs(A[k][i])); A[i], A[p] = A[p], A[i]; r[i], r[p] = r[p], r[i]
        for k in range(3):
            if k != i:
                f = A[k][i] / A[i][i]
                for j in range(3):
                    A[k][j] -= f * A[i][j]
                r[k] -= f * r[i]
    return tuple(r[i] / A[i][i] for i in range(3))


def run(_context):
    X = Ctx(); out = {}; t0 = time.time(); dry = globals().get('DRY', True); mode = 'dry' if dry else 'run'
    R2 = lambda v: [round(c, 2) for c in v]
    try:
        for k, v in EXP.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard: %s %s' % (k, None if b is None else round(b.volume, 4)))
        if X.body('MAIN_BRACKET_d19') is not None:
            raise RuntimeError('MAIN_BRACKET_d19 exists already')
        names = json.load(open(os.path.join(AUDD, 'a2a_parts.json'), encoding='utf-8')) + NEWP
        ko = [b.name for b in X.comp.bRepBodies if b.name.startswith('KO_')]
        allb = [(n, X.body(n), wbb(X, X.body(n))) for n in list(dict.fromkeys(names + ko)) if X.body(n) is not None]

        def static_hits(d, skip):
            db = wbb(X, d); res = {}
            for (n, b, pb) in allb:
                if n in skip or not ovl(db, pb, 0.1):
                    continue
                v = vol_x(X, d, b)
                if v > 0.005:
                    res[n] = v
            return res

        def moving_hits(movers, path, targets, st=0.5):        # [(label, tb)] moved along path vs [(label, tb)] at rest
            pts = steps_of(path, st)
            mb = [(lab, X.tbm.copy(tb), wbb(X, tb)) for lab, tb in movers]
            tg = [(lab, tb, wbb(X, tb)) for lab, tb in targets]
            res = {}; cur = (0.0, 0.0, 0.0)
            for k, p in enumerate(pts):
                dl = tuple(p[i] - cur[i] for i in range(3)); cur = p
                for (ml, b, bb0) in mb:
                    mvw(X, b, *dl)
                    bb = [bb0[0] + p[0], bb0[1] + p[0], bb0[2] + p[1], bb0[3] + p[1], bb0[4] + p[2], bb0[5] + p[2]]
                    for (tl, t, tbb) in tg:
                        if not ovl(bb, tbb, 0.1):
                            continue
                        v = vol_x(X, b, t)
                        if v > 0.005:
                            e = res.setdefault(ml + ' | ' + tl, [0, 0.0, None, k, k])
                            e[0] += 1; e[4] = k
                            if v > e[1]:
                                e[1] = v; e[2] = R2(p)
            return {'n_steps': len(pts), 'hits': res}

        def crop_to(names_, movers, path, m=2.0):              # fixed bodies cropped to the movers' swept box (lesson 24)
            pts = steps_of(path, 0.5); bbs = [wbb(X, tb) for _, tb in movers]
            sw = [min(bb[0] + p[0] for bb in bbs for p in pts), max(bb[1] + p[0] for bb in bbs for p in pts),
                  min(bb[2] + p[1] for bb in bbs for p in pts), max(bb[3] + p[1] for bb in bbs for p in pts),
                  min(bb[4] + p[2] for bb in bbs for p in pts), max(bb[5] + p[2] for bb in bbs for p in pts)]
            res = []
            for n in names_:
                if X.body(n) is None:
                    continue
                q = tb_copy(X, n); inter(X, q, wbox_rel(X, sw, m))
                if q.volume > 0:
                    res.append((n, q))
            return res

        # ---------------- A: the rib under the LD2410C cradle floor ----------------
        FC = tb_copy(X, 'HOUSING_F_front'); inter(X, FC, wbox_rel(X, CROP_A))
        plan = []
        for i in range(51):
            y = -33.0 + 0.5 * i
            q = X.tbm.copy(FC); inter(X, q, wbox_rel(X, [-97.0, -55.0, y - 0.05, y + 0.05, 114.45, 114.55]))
            plan.append([y, [R2(wbb(X, X.tbm.copy(l))[0:2]) for l in q.lumps] if q.volume > 0 else []])
        out['floor_plan_z114.5'] = plan
        zu = {}
        for (x, y) in ((-70.0, -16.0), (-75.0, -20.0), (-80.0, -14.0), (-78.0, -24.0), (-68.0, -12.0)):
            q = X.tbm.copy(FC); inter(X, q, wbox_rel(X, [x - 0.05, x + 0.05, y - 0.05, y + 0.05, 100.0, 119.0]))
            zu['%g,%g' % (x, y)] = [R2(wbb(X, X.tbm.copy(l))[4:6]) for l in q.lumps] if q.volume > 0 else []
        out['floor_z_runs'] = zu
        z0s = [r[0] for v in zu.values() for r in v if 110.0 < r[0] < 116.0]
        ZU = round(min(z0s), 3); out['ZU'] = ZU
        if max(z0s) - ZU > 0.05:
            raise RuntimeError('floor underside not flat: %s' % z0s)
        ribs = {}; A = {}
        for y0 in RIB_CANDS:
            y1 = y0 + RIB_T; ym = y0 + RIB_T / 2
            ed = []
            for (y, ls) in plan:
                if y0 - 0.01 <= y <= y1 + 0.01:
                    js = [l for l in ls if l[0] < -84.0]
                    ed.append(max(l[1] for l in js) if js else None)
            if not ed or None in ed:
                A[str(y0)] = {'edge': ed}; continue
            xo = min(ed)
            wp = []
            for yy in (y0 + 0.1, y1 - 0.1):
                for z in (90.0, 98.0, 106.0, 113.0):
                    q = X.tbm.copy(FC); inter(X, q, wbox_rel(X, [-97.0, -70.0, yy - 0.05, yy + 0.05, z - 0.05, z + 0.05]))
                    js = [wbb(X, X.tbm.copy(l))[0:2] for l in q.lumps] if q.volume > 0 else []
                    js = [l for l in js if l[0] < -84.0]
                    if js:
                        wp.append((max(l[1] for l in js), yy, z))
            a, bz, cy = lsq_plane(wp)
            res_ = max(abs(a + bz * z + cy * y - x) for (x, y, z) in wp)
            r = wbox_rel(X, [-97.0, xo, y0, y1, 80.0, ZU + 0.3])
            inter(X, r, hs(X, (xo, ym, ZU), (K46, 0.0, -1.0)))
            inter(X, r, hs(X, (a - 1.0 + bz * 100.0 + cy * ym, ym, 100.0), (-1.0, cy, bz)))
            d = X.tbm.copy(r); X.diff(d, X.tbm.copy(FC))
            ribs[y0] = (r, d)
            A[str(y0)] = {'edge': ed, 'x_edge': xo, 'wall_plane': [round(a, 3), round(bz, 4), round(cy, 4), round(res_, 3)],
                          'rib_mm3': round(r.volume * 1000, 1), 'added_mm3': round(d.volume * 1000, 1), 'added_lumps': d.lumps.count,
                          'added_bb': R2(wbb(X, d)), 'static': static_hits(d, ('HOUSING_F_front',))}
        out['A'] = A
        tg = [('rib%g' % y0, ribs[y0][1]) for y0 in RIB_CANDS if y0 in ribs]
        o35 = tuple(3.5 * c for c in FU)
        hood = [(n, tb_copy(X, n)) for n in ('BME_HOOD', 'FOAM_bme_top_env') if X.body(n) is not None]
        out['A_hood_path'] = moving_hits(hood, [tuple(o35[i] + 14.0 * FW[i] for i in range(3)), o35, (0.0, 0.0, 0.0)], tg)
        out['A_board_path'] = moving_hits([('BME680_env', tb_copy(X, 'BME680_env'))], [tuple(14.0 * c for c in FW), (0.0, 0.0, 0.0)], tg)
        out['A_ld2410c_path'] = moving_hits([('LD2410C_env_F', tb_copy(X, 'LD2410C_env_F'))], [(8.572, -5.150, 0.0), (0.0, 0.0, 0.0)], tg)
        bx = tb_copy(X, 'SPKBOX_R'); bbx = wbb(X, bx); inter(X, bx, wbox_rel(X, [bbx[0], bbx[1], bbx[2], bbx[3], 80.0, bbx[5]], 1.0))
        out['A_boxR_top_from_z80_mm3'] = round(bx.volume * 1000, 1)
        out['A_boxR_path'] = moving_hits([('SPKBOX_R_top', bx)], BOXR_PATH, tg)

        # ---------------- B: gussets under the bracket's lower board-boss arms ----------------
        brt = tb_copy(X, 'MAIN_BRACKET'); Bm = {}; gus = {}
        for s in (1, -1):
            sd = 'L' if s > 0 else 'R'
            mm = {}
            q = X.tbm.copy(brt); inter(X, q, wbox_rel(X, sorted([30.0 * s, 58.0 * s]) + [-60.55, -60.45, 29.95, 30.05]))
            mm['x_runs_z30'] = [R2(wbb(X, X.tbm.copy(l))[0:2]) for l in q.lumps] if q.volume > 0 else []
            q = X.tbm.copy(brt); inter(X, q, wbox_rel(X, sorted([47.45 * s, 47.55 * s]) + [-70.0, -50.0, 29.95, 30.05]))
            mm['col_y_runs'] = [R2(wbb(X, X.tbm.copy(l))[2:4]) for l in q.lumps] if q.volume > 0 else []
            q = X.tbm.copy(brt); inter(X, q, wbox_rel(X, sorted([43.95 * s, 44.05 * s]) + [-60.55, -60.45, 20.0, 45.0]))
            mm['arm_z_runs_x44'] = [R2(wbb(X, X.tbm.copy(l))[4:6]) for l in q.lumps] if q.volume > 0 else []
            q = X.tbm.copy(brt); inter(X, q, wbox_rel(X, sorted([43.95 * s, 44.05 * s]) + [-70.0, -50.0, 34.45, 34.55]))
            mm['arm_y_runs'] = [R2(wbb(X, X.tbm.copy(l))[2:4]) for l in q.lumps] if q.volume > 0 else []
            Bm[sd] = mm
            cx = [r for r in mm['x_runs_z30'] if (r[1] if s < 0 else -r[0]) < -44.0]   # the column's run (outboard of ±44)
            face = max(r[1] for r in cx) if s < 0 else min(r[0] for r in cx)
            cy_ = [r for r in mm['col_y_runs'] if r[0] < -60.5 < r[1]][0]
            az = [r for r in mm['arm_z_runs_x44'] if r[0] > 30.0][0]
            mm['face_x'] = face; mm['gy'] = cy_; mm['arm_z0'] = az[0]
            if abs(abs(face) - 46.5) > 0.3 or abs(az[0] - 33.5) > 0.05:
                raise RuntimeError('bracket %s not as measured in d17a: face %s arm %s' % (sd, face, az))
            g = wbox_rel(X, sorted([(abs(face) + 0.5) * s, 38.0 * s]) + [cy_[0], cy_[1], 20.0, 35.7])
            inter(X, g, hs(X, (38.0 * s, -60.5, az[0]), (-K46 * s, 0.0, -1.0)))
            X.diff(g, X.tbm.createCylinderOrCone(Dw(XC + 41.5 * s, -64.0, 37.5), 0.2, Dw(XC + 41.5 * s, -57.0, 37.5), 0.2))
            d = X.tbm.copy(g); X.diff(d, X.tbm.copy(brt))
            gus[s] = (g, d)
            mm.update({'gusset_mm3': round(g.volume * 1000, 1), 'added_mm3': round(d.volume * 1000, 1), 'added_lumps': d.lumps.count,
                       'added_bb': R2(wbb(X, d)), 'static': static_hits(d, ('MAIN_BRACKET',))})
            mv = [('gusset_' + sd, d)]
            mm['own_path'] = moving_hits(mv, BRK_PATH[s], crop_to(BRK_FIXED[s], mv, BRK_PATH[s]))
        out['B'] = Bm
        gt = [('gusset_L', gus[1][1]), ('gusset_R', gus[-1][1])]
        out['B_mainboard_path'] = moving_hits([(n, tb_copy(X, n)) for n in ('MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env')],
                                              [(0.0, -40.0, 0.0), (0.0, 0.0, 0.0)], gt)
        pw = tb_copy(X, 'PIPWR_a_env'); inter(X, pw, wbox_rel(X, [-40.0, 0.0, -75.0, -55.0, 0.0, 40.0]))
        out['B_pipwr_path'] = moving_hits([('PIPWR_a_env', pw)], [(0.0, -15.0, 0.0), (0.0, 0.0, 0.0)], gt)
        dm = []
        for s in (1, -1):
            gb = wbb(X, gus[s][1]); q = tb_copy(X, 'HOUSING_F_door')
            inter(X, q, wbox_rel(X, [gb[0], gb[1], gb[2], gb[3] + 80.0, gb[4], gb[5]], 2.0))   # door points that reach D on the way in
            if q.volume > 0:
                dm.append(('door_' + ('L' if s > 0 else 'R'), q))
        out['B_door_path'] = moving_hits(dm, [(0.0, -80.0, 0.0), (0.0, 0.0, 0.0)], gt) if dm else 'door not near'

        # ---------------- apply (B only) ----------------
        if not dry:
            br = tb_copy(X, 'MAIN_BRACKET'); v0b = br.volume; dv = gus[1][1].volume + gus[-1][1].volume
            for s in (1, -1):
                X.union(br, gus[s][0])
            if abs(br.volume - v0b - dv) > 0.0005:
                raise RuntimeError('bracket: union added %.4f cm3, expected %.4f' % (br.volume - v0b, dv))
            o = X.body('MAIN_BRACKET'); app = o.appearance; mat = o.material
            o.name = 'MAIN_BRACKET_d19'; o.isLightBulbOn = False
            nb = X.add(br, 'MAIN_BRACKET')
            for attr, val in (('material', mat), ('appearance', app)):
                try:
                    setattr(nb, attr, val)
                except Exception:
                    pass
            out['applied'] = {'MAIN_BRACKET': [round(nb.volume, 4), nb.lumps.count], 'added_mm3': round(dv * 1000, 1)}
            I = lambda b_, x, y, z: X.inside(b_, XC + x, y, z)
            pr = {}
            for s in (1, -1):
                sd = 'L' if s > 0 else 'R'
                pr.update({'gusset_' + sd: I(nb, 44.0 * s, -60.5, 30.0), 'below_gusset_open_' + sd: not I(nb, 40.0 * s, -60.5, 29.0),
                           'gusset_under_round_' + sd: I(nb, 38.2 * s, -60.5, 34.6), 'arm_end_unchanged_' + sd: not I(nb, 37.8 * s, -60.5, 35.0),
                           'insert_hole_open_' + sd: not I(nb, 41.5 * s, -60.5, 37.4), 'hole_bottom_open_' + sd: not I(nb, 41.5 * s, -60.5, 35.6),
                           'column_y_face_kept_' + sd: not I(nb, 44.0 * s, -62.7, 30.0) and not I(nb, 44.0 * s, -58.3, 30.0),
                           'column_kept_' + sd: I(nb, 49.5 * s, -60.5, 30.0)})
            out['probes'] = pr
        out['dry'] = dry
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    try:
        json.dump(out, open(OUTF % mode, 'w'))
    except Exception:
        pass
    log('v5f_d19d_print_fixes', mode, {'t_s': out.get('t_s'), 'FAIL': out.get('FAIL'), 'applied': out.get('applied'), 'probes': out.get('probes')})
    print(json.dumps({'t_s': out.get('t_s'), 'FAIL': out.get('FAIL'), 'applied': out.get('applied'), 'probes': out.get('probes')}, separators=(',', ':')))
