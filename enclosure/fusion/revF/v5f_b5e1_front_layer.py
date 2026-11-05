# rev F block 5e-1 (2026-11-05): front shell – R1 lip out, D1 inner layer in.
#   1. The R1 lip (cavity layer 0.2…1.4), its root band (y −55.0…−53.5) and the ten lip pads (s −0.2…−2.3) are removed:
#      TOOL_inner_skin_2p5 ∩ (y −64.5…−53.4, z ≥ 6.0). They are rebuilt 0.7 deeper in B5e-2 (the door's new inner surface
#      lies at s −0.7).
#   2. D1 layer (v5f_b5_common.build_layer 'front'): 0.7 inside INNER_E over the fabric zone below the top groove (z 175.3),
#      thickened floor cove (R2.8, concentric with the R6 edge fillet), none on the flat floor, none behind the slot face /
#      boss (d < 15.6 above Z −94.3), none at the VEML6030 envelope (+0.5; provisional board, B3f); y ≥ −55.0.
#      (LD2410C: B5d found the layer > 4.0 from the antenna face over 16 × 22, so no window exclusion: 2.5 wall + > 3 air.)
#   Openings closed by the layer (lattices, pilots, exhaust, BME680 slots) are re-cut in B5e-3.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
EXPECT = {'HOUSING_F_front': 242.147, 'HOUSING_F_door': 55.102}


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.003:
                raise RuntimeError('guard: %s volume %s, expected %s' % (k, None if b is None else round(b.volume, 3), v))
        for n in ('TOOL_inner_skin_0p7', 'TOOL_inner_skin_2p5', 'TOOL_outer_skin_3p2', 'TOOL_floor_off6'):
            if X.body(n) is None:
                raise RuntimeError('missing tool %s' % n)
        # stale rev D BME680_env (door tray, y −81…−69) shares its name with B4l's envelope: rename it so name lookups hit B4l's
        bme = [b for b in X.comp.bRepBodies if b.name.startswith('BME680_env') and not b.name.endswith('_revD')]
        out['bme680_bodies_before'] = [[b.name] + [round(c, 1) for c in wbb(X, b)] for b in bme]
        for b in bme:
            if wbb(X, b)[3] < -60.0:
                b.name = 'BME680_env_revD'; b.isLightBulbOn = False
        for b in X.comp.bRepBodies:
            if b.name.startswith('BME680_env') and not b.name.endswith('_revD') and b.name != 'BME680_env':
                b.name = 'BME680_env'
        out['bme680_env'] = [[round(c, 1) for c in wbb(X, b)] for b in X.comp.bRepBodies if b.name == 'BME680_env']
        fb = X.body('HOUSING_F_front'); v0 = fb.volume
        R = tb_copy(X, 'TOOL_inner_skin_2p5'); inter(X, R, X.wbox(-250, 250, -64.5, -53.4, 6.0, 260))
        out['old_lip_mm3'] = vol_x(X, R, fb)
        X.combine(fb, [X.add(R, 'B5E1_oldlip_tmp')], op=CUT)
        fb = X.body('HOUSING_F_front'); v1 = fb.volume
        out['lumps_after_lip_cut'] = fb.lumps.count
        L = build_layer(X, 'front')
        out['layer_cm3'] = round(L.volume, 3)
        X.combine(fb, [X.add(L, 'B5E1_layer_tmp')])
        fb = X.body('HOUSING_F_front')
        out['cm3'] = [round(v0, 3), round(v1, 3), round(fb.volume, 3)]
        out['lumps'] = fb.lumps.count
        out['names'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('HOUSING_F')]
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        out['probes'] = {
            'chin_layer_y4.65_z25': X.inside(fb, XC, 4.65, 25.0), 'chin_air_y4.15_z25': not X.inside(fb, XC, 4.15, 25.0),
            'side_layer_+x_z100_y-20': None, 'old_lip_gone_+x_z60_y-58': None,
        }
        # side layer: first inner hit along +x at (y −20, z 100), check 0.35 inside it
        h = [r for r in ray_hits(X, (XC, -20.0, 100.0), (1, 0, 0), ('HOUSING_F_front',))]
        if h:
            xr = h[0][2]
            out['probes']['side_inner_x_rel'] = round(xr, 2)
            out['probes']['side_layer_+x_z100_y-20'] = X.inside(fb, XC + xr + 0.35, -20.0, 100.0)
        out['probes']['old_lip_gone_+x_z60_y-58'] = not [r for r in ray_hits(X, (XC, -58.0, 60.0), (1, 0, 0), ('HOUSING_F_front',))
                                                          if r[0] < 100.0]
        out['touch_pcb_mm3'] = vol_x(X, X.tbm.copy(fb), X.body('TOUCH_PCB'))
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b5e1_front_layer', 'lip out + layer', out)
    print(json.dumps(out))
