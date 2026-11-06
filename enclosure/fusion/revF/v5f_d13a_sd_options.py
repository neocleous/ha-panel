# rev F d13a (2026-11-06), read-only: microSD access options (Daniel 18:00: card access is a requirement).
#   Card geometry (rays on PI5_F), the Pi 5 power button and USB stacks, the +x box slot, both chambers' air, then trial
#   regions vs the audit part list (+ d-round parts) and vs the chamber air: A floor hatch (pocket in SPKBOX_R's inboard-bottom
#   corner open downward + floor slot), R rear tunnel, B extender channel along the Pi's slide, sockets / reader zones behind
#   the boxes, a second USB-A plug above the ReSpeaker plug. Writes ~/Documents/HA_panel_renders/d_data/data/d13a_probe.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/HA_panel_renders/scripts_d/v5f_d0_sections.py')).read())   # sections()
import traceback
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d13a_probe.json')
AUDD = os.path.expanduser('~/Documents/audit/data')
NEWP = ['TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'BME_HOOD', 'FOAM_bme_env', 'FOAM_bme_top_env']
GUARD = {'HOUSING_F_front': 235.3238, 'SPKBOX_R': 25.6435, 'SPKBOX_L': 25.6082, 'HOUSING_F_door': 47.2694, 'MAIN_BRACKET': 5.3431}
PCIN = adsk.fusion.PointContainment.PointInsidePointContainment


def chamber(X, box, sx):
    bb = wbb(X, X.body(box)); g = 1.0
    Rb = [bb[0] - g, bb[1] + g, bb[2] - g, bb[3] + g, bb[4] - g, bb[5] + g]
    A = wbox_rel(X, Rb)
    X.diff(A, tb_copy(X, box)); X.diff(A, wbox_rel(X, [Rb[0], Rb[1], -3.7, -3.0, Rb[4], Rb[5]]))
    a = Dw(XC + sx * 62.0, -53.0, 30.0); b = Dw(XC + sx * 62.0, -49.5, 30.0)
    X.diff(A, X.tbm.createCylinderOrCone(a, 0.16, b, 0.16))
    pc = Dw(XC + sx * 70.5, -30.0, 62.0)
    for L in A.lumps:
        t = X.tbm.copy(L)
        if t.pointContainment(pc) == PCIN:
            return t
    return None


def hits(X, o, d, names=('PI5_F',)):
    return [[round(r[0], 2), r[1], round(r[2], 2), round(r[3], 2), round(r[4], 2)] for r in ray_hits(X, o, d, names)]


def lumps_bb(X, t):
    out = []
    for L in t.lumps:
        q = X.tbm.copy(L)
        out.append([round(c, 2) for c in wbb(X, q)] + [round(q.volume * 1000, 2)])
    return out


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        for k, v in GUARD.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard %s %s (expected %s)' % (k, None if b is None else round(b.volume, 4), v))
        # --- card geometry ---
        cg = {}
        for (x, y) in ((-44.5, -30.0), (-44.0, -30.0), (-40.0, -30.0), (-44.5, -34.5), (-44.5, -25.0), (-43.6, -30.0)):
            cg['z_up_%g_%g' % (x, y)] = hits(X, (XC + x, y, 0.0), (0, 0, 1))
        for z in (6.5, 6.8, 7.0, 7.2, 7.4):
            cg['x_in_y-30_z%g' % z] = hits(X, (XC - 60.0, -30.0, z), (1, 0, 0))[:4]
        for (x, z) in ((-44.5, 7.0), (-40.0, 7.0), (-44.5, 6.5)):
            cg['y_fw_%g_z%g' % (x, z)] = hits(X, (XC + x, -50.0, z), (0, 1, 0))[:6]
        out['card'] = cg
        # --- Pi corner (power button), USB stacks ---
        q = tb_copy(X, 'PI5_F'); inter(X, q, wbox_rel(X, [-44.5, -30.0, -61.0, -50.0, 9.0, 18.0])); out['pi_corner_lumps'] = lumps_bb(X, q)
        q = tb_copy(X, 'PI5_F'); inter(X, q, wbox_rel(X, [36.0, 46.0, -61.0, -2.0, 8.0, 28.0])); out['pi_usb_lumps'] = lumps_bb(X, q)
        prof = {}
        for y in (-47.0, -42.0, -33.0, -29.0, -25.0, -15.0, -11.0, -7.0):
            row = []
            for zz in range(10, 28):
                h = hits(X, (XC + 70.0, y, zz + 0.5), (-1, 0, 0))
                row.append([zz + 0.5, h[0][2] if h else None])
            prof['y%g' % y] = row
        out['pi_usb_profile'] = prof
        env = {}
        for n in ('USBA_plug_env', 'USBA_cable_env', 'LEAD_SPK_R', 'LEAD_SPK_L', 'SPK_R', 'SPK_L', 'PI5_F_cooler', 'KO_K7_fan',
                  'GPIO_plugA_env', 'GPIO_plugB_env', 'PIPWR_a_env', 'LEAD_PI_POWER', 'MAIN_BRACKET', 'FOOT_RR', 'FOOT_RL',
                  'FOOT_FR', 'FOOT_FL', 'HOUSING_F_door', 'SPKBOX_R', 'SPKBOX_L'):
            b = X.body(n)
            if b is None:
                env[n] = None; continue
            env[n] = {'bb': [round(c, 2) for c in wbb(X, b)], 'vis': b.isLightBulbOn}
        q = tb_copy(X, 'MAIN_BRACKET'); inter(X, q, wbox_rel(X, [-60.0, -30.0, -70.0, -50.0, 0.0, 20.0])); env['MAIN_BRACKET_R_low'] = lumps_bb(X, q)
        out['env'] = env
        lb = {}
        for (x, y) in ((50.0, -30.0), (50.0, -45.0), (52.0, -28.0), (46.5, -30.0), (55.0, -45.0)):
            lb['z_up_%g_%g' % (x, y)] = hits(X, (XC + x, y, 0.0), (0, 0, 1), ('SPKBOX_L',))
        for z in (12.0, 15.0, 19.0, 22.0):
            lb['y_bw_x50_z%g' % z] = hits(X, (XC + 50.0, 0.0, z), (0, -1, 0), ('SPKBOX_L',))
        out['lbox_rays'] = lb
        out['t_geo'] = round(time.time() - t0, 1)
        # --- chambers ---
        chR = chamber(X, 'SPKBOX_R', -1); chL = chamber(X, 'SPKBOX_L', 1)
        out['chamber_cm3'] = {'R': round(chR.volume, 3) if chR else None, 'L': round(chL.volume, 3) if chL else None}
        # --- parts ---
        names = json.load(open(os.path.join(AUDD, 'a2a_parts.json'))) + NEWP
        parts = []
        for n in names:
            b = X.body(n)
            if b is not None:
                try:
                    parts.append((n, b, wbb(X, b)))
                except Exception:
                    pass
        out['n_parts'] = len(parts)
        # card z from the vertical ray at (-44.0, -30): first two PI5_F hits above z 6.45 (lip below)
        zc = [h[4] for h in cg.get('z_up_-44_-30', [])]
        out['card_z_hits'] = zc
        cz0, cz1 = 6.6, 7.4
        R = {}
        def region(key, bb, ch=None, skip=()):
            try:
                t = wbox_rel(X, bb); res = {'bb': bb, 'hits': {}}
                for (n, b, pb) in parts:
                    if n in skip:
                        continue
                    if pb[0] > bb[1] or pb[1] < bb[0] or pb[2] > bb[3] or pb[3] < bb[2] or pb[4] > bb[5] or pb[5] < bb[4]:
                        continue
                    qq = X.tbm.copy(b); inter(X, qq, X.tbm.copy(t))
                    v = qq.volume * 1000
                    if v > 0.005:
                        res['hits'][n] = [round(v, 2)] + [round(c, 2) for c in wbb(X, qq)]
                if ch is not None:
                    qq = X.tbm.copy(ch); inter(X, qq, X.tbm.copy(t)); res['air_mm3'] = round(qq.volume * 1000, 1)
                R[key] = res
            except Exception as e:
                R[key] = {'bb': bb, 'FAIL': str(e)[:120]}
        # A floor hatch
        region('A_E_extract', [-60.6, -43.0, -35.7, -24.1, cz0 - 0.1, cz1 + 0.1])
        region('A_D_drop', [-60.6, -43.0, -35.7, -24.1, -0.6, cz1 + 0.1])
        region('A_P_pocket', [-61.0, -45.95, -36.2, -23.6, 3.0, 8.0], chR)
        region('A_W_pocket_walls', [-62.5, -45.95, -37.7, -22.1, 3.0, 9.5], chR)
        region('A_F_floor_slot', [-61.2, -43.0, -36.4, -23.4, -0.6, 3.0])
        region('A_C_cover_below', [-65.0, -39.0, -40.0, -20.0, -3.2, 0.0])
        region('A_T_tweezers', [-46.0, -43.2, -36.2, -23.6, -0.6, cz0 - 0.05])
        region('A_J_top_jaw', [-44.85, -43.2, -35.6, -24.2, cz1 + 0.05, cz1 + 1.3])
        # R rear tunnel (straight) and its exit behind the box
        region('R_T_tunnel', [-61.0, -45.95, -52.6, -23.6, cz0 - 0.3, cz1 + 0.6], chR)
        region('R_TW_tunnel_walls', [-62.5, -45.95, -52.6, -22.1, 5.2, cz1 + 2.1], chR)
        region('R_X_exit', [-60.6, -43.0, -66.0, -52.05, cz0 - 0.1, cz1 + 0.1])
        # B extender channel along the Pi's slide (plug 8 mm stiffener + 16 flex fold, lift 2.0) and socket zones
        region('B_CH_channel', [-69.4, -45.95, -52.6, -20.4, 6.0, 10.2], chR)
        region('B_W_channel_walls', [-70.9, -45.95, -52.6, -18.9, 4.5, 11.7], chR)
        region('B_SF_socket_floor', [-77.5, -54.0, -80.0, -55.5, 2.6, 9.0])
        region('B_SW_socket_rearface', [-77.0, -54.0, -58.5, -52.05, 8.0, 30.0])
        # C USB reader zones behind the +x box; second plug above the ReSpeaker plug
        region('C_RF_reader_floor', [54.0, 77.5, -80.0, -55.5, 2.6, 14.0])
        region('C_RW_reader_rearface', [54.0, 77.0, -58.5, -53.05, 8.0, 30.0])
        pe = X.body('USBA_plug_env')
        if pe is not None:
            pb = wbb(X, pe)
            for dz in (8.0, 8.75, 9.5):
                region('C_P2_dz%g' % dz, [pb[0], pb[1], pb[2], pb[3], pb[4] + dz, pb[5] + dz], chL)
                region('C_P2W_dz%g' % dz, [pb[0] - 1.5, pb[1] + 1.5, pb[2] - 1.5, pb[3] + 1.5, pb[4] + dz - 1.5, pb[5] + dz + 1.5], chL)
        out['regions'] = R
        out['t_regions'] = round(time.time() - t0, 1)
        NB = ['SPKBOX_R', 'HOUSING_F_front', 'PI5_F', 'MAIN_BRACKET', 'HOUSING_F_door', 'SPK_R', 'PIPWR_a_env', 'LEAD_SPK_R']
        NL = ['SPKBOX_L', 'HOUSING_F_front', 'PI5_F', 'MAIN_BRACKET', 'HOUSING_F_door', 'SPK_L', 'USBA_plug_env', 'USBA_cable_env']
        PL = {'S_y-30': ('y', -30.0, (-80.0, -30.0, -2.0, 20.0), NB), 'S_z7': ('z', 7.0, (-80.0, -30.0, -72.0, -15.0), NB),
              'S_x-52': ('x', -52.0, (-72.0, -15.0, -2.0, 20.0), NB), 'S_z4': ('z', 4.0, (-80.0, -30.0, -72.0, -15.0), NB),
              'L_x50': ('x', 50.0, (-60.0, 0.0, 0.0, 34.0), NL), 'L_y-29': ('y', -29.0, (30.0, 80.0, 0.0, 34.0), NL)}
        out['sec'] = sections(X, PL)
        out['t_s'] = round(time.time() - t0, 1)
        os.makedirs(os.path.dirname(OUTF), exist_ok=True)
        json.dump(out, open(OUTF, 'w'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
        try:
            json.dump(out, open(OUTF, 'w'))
        except Exception:
            pass
    log('v5f_d13a_sd_options', 'probe', {'t_s': out.get('t_s'), 'FAIL': out.get('FAIL'), 'chamber': out.get('chamber_cm3')})
    print(json.dumps({'t_s': out.get('t_s'), 'FAIL': out.get('FAIL'), 'chamber': out.get('chamber_cm3')}, separators=(',', ':')))
