# rev F block 5f (2026-11-05): door – D1 inner layer, magnet pockets for D1, inlet cutout for the grommet, pin holes.
#   1. D1 layer (build_layer 'door'): 0.7 inside INNER_E behind y −55.3 (z ≥ 2.8), thickened floor cove.
#   2. R1 door pockets (Ø8.3, s 0.9…3.2 at the R1 points) filled (r 4.25, s 0.85…2.5 ∩ REF_F_outer); new pockets Ø8.3 from
#      s +0.2 (0.9 skin to the new inner surface at s −0.7) through the outer surface, at MAG_D1 (same points as B5e-2).
#   3. Inlet cutout for the USB-C grommet (B5i): sleeve x ±12.1, z 6.9–21.3 + 0.1 → cutout x ±12.2, z 6.8–21.4 (was x ±11.3,
#      z 7.7–20.5 around the cradle bezel x ±11.0, z 8.0–20.2); two Ø2.1 holes for the grommet's Ø1.8 heat-stake pins at
#      (x_rel ±13.6, z 14.1).
#   4. Door-boss insert holes Ø4.0, z 2.3–9.5 re-cut (the thickened cove reaches into them).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
EXPECT = {'HOUSING_F_door': 55.102}
ZC = 14.1                       # inlet centre (cradle bezel z 8.0–20.2); + 6.5 if V11 option 1 raises the 5807
DB = [(50.0, -67.0), (-50.0, -67.0), (19.0, -74.5), (-19.0, -74.5)]


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.003:
                raise RuntimeError('guard: %s volume %s, expected %s' % (k, None if b is None else round(b.volume, 3), v))
        db = X.body('HOUSING_F_door'); v0 = db.volume
        L = build_layer(X, 'door')
        out['layer_cm3'] = round(L.volume, 3)
        X.combine(db, [X.add(L, 'B5F_layer_tmp')])
        db = X.body('HOUSING_F_door'); v1 = db.volume
        fill = None
        for (s, zm), (xr, nwo) in MAG_R1.items():
            p = Dw(XC + xr, MAG_R1_Y[zm], zm); n = wv(nwo); n.normalize()
            c = cyl_pn(X, p, n, 0.85, 3.3, 4.25)
            fill = c if fill is None else X.union(fill, c)
        inter(X, fill, tb_copy(X, 'REF_F_outer'))
        inter(X, fill, X.wbox(-250, 250, -250, YJ_D, 2.8, 260))
        X.combine(db, [X.add(fill, 'B5F_fill_tmp')])
        db = X.body('HOUSING_F_door'); v2 = db.volume
        cut = None; pts = {}; pp = []
        for s in (1, -1):
            for (zm, ym) in MAG_D1:
                p, n, xr, nw = magnet_point(X, s, zm, ym)
                pts['%+d,%g' % (s, zm)] = {'x_rel': round(xr, 2), 'n_world': nw}
                pp.append((p, n))
                c = cyl_pn(X, p, n, 0.2, 3.2, 4.15)
                cut = c if cut is None else X.union(cut, c)
        out['magnets'] = pts
        X.union(cut, X.wbox(XC - 12.2, XC + 12.2, -88.0, -79.0, ZC - 7.3, ZC + 7.3))
        for sx in (1, -1):
            X.union(cut, X.tbm.createCylinderOrCone(Dw(XC + sx * 13.6, -88.0, ZC), 0.105, Dw(XC + sx * 13.6, -79.0, ZC), 0.105))
        for (xr, y) in DB:
            X.union(cut, X.wcyl_z(XC + xr, y, 2.0, 2.3, 9.5))
        X.combine(db, [X.add(cut, 'B5F_cut_tmp')], op=CUT)
        db = X.body('HOUSING_F_door')
        out['cm3'] = [round(v0, 3), round(v1, 3), round(v2, 3), round(db.volume, 3)]
        out['lumps'] = db.lumps.count
        out['names'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('HOUSING_F')]
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        mp = []
        for (p, n) in pp:
            ins = lambda k: db.pointContainment(qpt(p, n, k)) in INS
            mp.append([not ins(1.0), ins(-0.2), ins(-0.6), not ins(-0.8)])
        out['magnet_probes_open1.0_skin-0.2_skin-0.6_air-0.8'] = mp
        out['inlet_open'] = not X.inside(db, XC, -83.5, ZC) and not X.inside(db, XC + 11.9, -83.5, ZC) and not X.inside(db, XC, -83.5, ZC + 7.1)
        out['pin_holes_open'] = [not X.inside(db, XC + sx * 13.6, -83.5, ZC) for sx in (1, -1)]
        out['insert_holes_open_z4'] = [not X.inside(db, XC + xr, y, 4.0) for (xr, y) in DB]
        h = [r for r in ray_hits(X, (XC, -40.0, 60.0), (0, -1, 0), ('HOUSING_F_door',))]
        out['back_wall_x0_z60_y'] = [round(r[3], 2) for r in h[:2]]
        out['door_x'] = X.interference(db, [X.body(n) for n in ('HOUSING_F_front', 'CRADLE_5807', 'PD_5807_env', 'MAIN_BRACKET',
                                                               'MAIN_back_env', 'PI5_F_cooler', 'SPKBOX_L', 'SPKBOX_R')])
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b5f_door_layer', 'door', out)
    print(json.dumps(out))
