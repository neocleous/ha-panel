# rev F block 5d (2026-11-05), read-only: the D1 inner layer (built as TemporaryBRep, not added) against every part.
#   Layer = TOOL_inner_skin_0p7 ∩ z 2.5…175.3 ∪ (TOOL_outer_skin_3p2 ∩ z 2.5…6.2 − TOOL_floor_off6)  [thickened floor cove]
#           − slot/boss zone (d < 15.6 above design Z −94.3) − LD2410C window − VEML6030 envelope + 0.5;
#   split at the R1 joint planes: front y ≥ −55.0, door y ≤ −55.3 (z ≥ 2.8).
#   Reports: layer volumes; layer ∩ each part (bbox pre-filter, PI5_F cropped) in mm³ with the overlap's world box;
#   also the layer without the LD / VEML exclusions vs LD2410C_env_F / VEML_env (to show why they are there).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
PARTS = ['SLAB_frame', 'LCD_glass', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'PI5_F', 'PI5_F_cooler', 'KO_K7_fan', 'KO_K5_LL',
         'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR', 'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'MAIN_BRACKET', 'CRADLE_5807',
         'PD_5807_env', 'KO_5807_pigtail', 'RESP_CARRIER', 'RESP_pcb', 'RESP_top_env', 'RESP_mic_env', 'RESP_usbc_plug_env',
         'LD2410C_env_F', 'MIC_strip_L_env', 'MIC_strip_R_env', 'KO_mic_L_back', 'KO_mic_R_back', 'VEML_env', 'BME680_env',
         'TOUCH_PCB', 'KO_touch_back', 'GPIO_plugA_env', 'GPIO_plugB_env', 'USBA_plug_env', 'USBA_cable_env',
         'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR']


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        names = [b.name for b in X.comp.bRepBodies]
        parts = PARTS + [n for n in names if n.startswith('LCD_') and n != 'LCD_glass'] + \
            [n for n in names if n.startswith('LEAD_') and not n.endswith('_b4n')]
        layers = {}
        for part in ('front', 'door'):
            L = build_layer(X, part)
            layers[part] = L
            out['layer_%s_cm3' % part] = round(L.volume, 3)
        out['t_build_s'] = round(time.time() - t0, 1)
        res = {}
        for part, L in layers.items():
            lb = L.boundingBox
            hits = {}
            for pn in parts:
                o = X.body(pn)
                if o is None:
                    continue
                ob = o.boundingBox
                if ob.maxPoint.x < lb.minPoint.x or ob.minPoint.x > lb.maxPoint.x or ob.maxPoint.y < lb.minPoint.y or \
                        ob.minPoint.y > lb.maxPoint.y or ob.maxPoint.z < lb.minPoint.z or ob.minPoint.z > lb.maxPoint.z:
                    continue
                q = X.tbm.copy(o)
                if pn == 'PI5_F':
                    inter(X, q, X.wbox(-150, 150, -70, 5, 0, 40))
                inter(X, q, X.tbm.copy(L))
                v = q.volume * 1000
                if v > 0.005:
                    hits[pn] = [round(v, 2), [round(c, 1) for c in wbb(X, q)]]
            res[part] = hits or 'all 0'
        out['layer_x_parts_mm3'] = res
        # why the exclusions: the layer without them vs the LD2410C board and the VEML envelope
        Lf = build_layer(X, 'front', excl_ld=False, excl_veml=False)
        out['no_excl_vs'] = {n: vol_x(X, Lf, X.body(n)) for n in ('LD2410C_env_F', 'VEML_env')}
        out['ld_excl_x_layer_mm3'] = vol_x(X, Lf, ld_excl(X))
        out['veml_excl_x_layer_mm3'] = vol_x(X, Lf, veml_excl(X))
        # air in front of the antenna (16 x 22 face): layer volume inside boxes 0...k mm in front of the face
        a = math.radians(LD_A); n = (-math.sin(a), math.cos(a), 0.0); t = (math.cos(a), math.sin(a), 0.0)
        air = {}
        for k in (1.0, 1.5, 2.0, 2.5, 3.0, 4.0):
            c = (LD_F[0] + n[0] * k / 2, LD_F[1] + n[1] * k / 2, LD_F[2])
            air['0-%g' % k] = vol_x(X, Lf, lbox(X, c, n, t, k, 16.0, 22.0))
        out['ld_air_layer_mm3'] = air
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b5d_layer_conflicts', 'checks', out)
    print(json.dumps(out))
