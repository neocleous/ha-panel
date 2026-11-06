# rev F d8b (2026-11-06): VEML6030 retention to Daniel's caliper (audit finding 40; board 15.26 x 15.20, two Ø2.1 holes
#   11.0 apart at the "top corners", 5-pin header on the opposite edge).
#   The lead (LEAD_VEML, Ø3) rises into the board's rear end at (0, -39.7), so the header edge faces -y and the two holes
#   are at the front corners: x_rel ±5.5, y -28.23 (inset from the front edge taken equal to the side inset, 2.13 -
#   ASSUMED, not measured). The board stays centred on the Ø2 lux port (0, -33.7): sensor ASSUMED at the board's centre.
#   HOUSING_F_cap (old -> HOUSING_F_cap_d8, hidden):
#     two stand-off collars Ø3.2 x 1.0 under the pocket ceiling (z 177.3-178.3) round two heat-stake pins Ø1.8 down to
#     z 173.7 (2.0 below a 1.6 board), and two 1.0 x 1.0 x 1.0 seat pads at the rear corners: the board's top face sits
#     1.0 under the ceiling (the 0.85 sensor package and any 0603 parts clear it by 0.15) and 0.2 under the cap's underside.
#   VEML_env (old -> VEML_env_d8, hidden): board 15.26 x 15.20 x 1.6 (thickness ASSUMED) at z 175.7-177.3 with its two
#     Ø2.1 holes, the 2 x 2 x 0.85 sensor on top at the centre, and a 4 mm band under the header edge for the soldered
#     jumpers (z 173.1-175.7). LEAD_VEML (old -> LEAD_VEML_d8, hidden): extended 1.2 up to the board's underside.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
CAP = 'HOUSING_F_cap'
EXPECT = {CAP: 9.9227}
BW, BH, BT = 15.26, 15.20, 1.6           # board along x, along y, thickness (ASSUMED)
YC0 = -33.7                               # board centre = lux port
YF = YC0 + BH / 2; YR = YC0 - BH / 2      # front edge -26.1, rear edge -41.3
HX, HY = 5.5, YF - (BW - 11.0) / 2        # hole centres x ±5.5, y -28.23
ZB = 177.3                                # board top face
ZCEIL = 178.3


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        cb = X.body(CAP)
        if abs(cb.volume - EXPECT[CAP]) > 0.0005:
            raise RuntimeError('guard: cap %s' % round(cb.volume, 4))
        for n in ('HOUSING_F_cap_d8', 'VEML_env_d8', 'LEAD_VEML_d8'):
            if X.body(n) is not None:
                raise RuntimeError('%s exists already' % n)
        for n in ('VEML_env', 'LEAD_VEML'):
            if X.body(n) is None:
                raise RuntimeError('%s missing' % n)
        c = X.add(X.tbm.copy(cb), 'HOUSING_F_cap_d8'); c.isLightBulbOn = False
        v0 = cb.volume
        tool = None
        for s in (1, -1):
            col = X.wcyl_z(XC + s * HX, HY, 1.6, ZB, ZCEIL + 0.05)
            pin = X.wcyl_z(XC + s * HX, HY, 0.9, ZB - BT - 2.0, ZB + 0.05)
            pad = X.wbox(XC + s * (BW / 2 - 0.1), XC + s * (BW / 2 - 1.1), YR + 0.1, YR + 1.1, ZB, ZCEIL + 0.05)
            for t in (col, pin, pad):
                tool = t if tool is None else X.union(tool, t)
        tn = X.tbm.copy(tool); X.diff(tn, X.tbm.copy(cb))
        out['tool_mm3'] = [round(tool.volume * 1000, 3), round(tn.volume * 1000, 3)]
        ox = {}
        for n in ('HOUSING_F_front', 'LEAD_VEML', 'MIC_strip_L_env', 'MIC_strip_R_env', 'KO_mic_L_back', 'KO_mic_R_back'):
            if X.body(n) is not None:
                ox[n] = vol_x(X, X.tbm.copy(tool), tb_copy(X, n))
        out['tool_x'] = ox
        X.combine(cb, [X.add(tool, 'D8B_tool_tmp')]); cb = X.body(CAP)
        out['cap_cm3'] = [round(v0, 4), round(cb.volume, 4)]; out['cap_lumps'] = cb.lumps.count
        out['cap_voids'] = sum(1 for li in range(cb.lumps.count) for si in range(cb.lumps.item(li).shells.count)
                               if cb.lumps.item(li).shells.item(si).isVoid)
        # envelope
        o = X.body('VEML_env'); o.name = 'VEML_env_d8'; o.isLightBulbOn = False
        e = X.wbox(XC - BW / 2, XC + BW / 2, YR, YF, ZB - BT, ZB)
        for s in (1, -1):
            X.diff(e, X.wcyl_z(XC + s * HX, HY, 1.05, ZB - BT - 0.1, ZB + 0.1))
        X.union(e, X.wbox(XC - 1.0, XC + 1.0, YC0 - 1.0, YC0 + 1.0, ZB, ZB + 0.85))
        X.union(e, X.wbox(XC - 5.9, XC + 5.9, YR, YR + 4.0, ZB - BT - 2.6, ZB - BT))
        ne = X.add(e, 'VEML_env'); ne.isLightBulbOn = False
        # lead to the board's underside
        lo = X.body('LEAD_VEML'); lo.name = 'LEAD_VEML_d8'; lo.isLightBulbOn = False
        nl = X.tbm.copy(lo); X.union(nl, X.wcyl_z(XC + 0.0, -39.7, 1.5, 174.4, ZB - BT + 0.05))
        nlb = X.add(nl, 'LEAD_VEML'); nlb.isLightBulbOn = False
        out['env'] = {'cm3': round(ne.volume, 4), 'bb': [round(v, 2) for v in wbb(X, ne)],
                      'x_cap_mm3': vol_x(X, tb_copy(X, 'VEML_env'), tb_copy(X, CAP)),
                      'x_front_mm3': vol_x(X, tb_copy(X, 'VEML_env'), tb_copy(X, 'HOUSING_F_front')),
                      'x_lead_mm3': vol_x(X, tb_copy(X, 'VEML_env'), tb_copy(X, 'LEAD_VEML'))}
        out['lead'] = {'cm3': [round(lo.volume, 4), round(nlb.volume, 4)],
                       'x_cap_mm3': vol_x(X, tb_copy(X, 'LEAD_VEML'), tb_copy(X, CAP))}
        P = lambda b, x, y, z: X.inside(b, XC + x, y, z)
        out['probes'] = {'collar_in': P(cb, HX + 1.3, HY, 177.6), 'pin_tip_in': P(cb, -HX, HY, 173.8),
                         'pin_below_tip_free': not P(cb, -HX, HY, 173.6), 'pad_in': P(cb, BW / 2 - 0.6, YR + 0.6, 177.6),
                         'port_open': not P(cb, 0.0, YC0, 179.2), 'gap_over_sensor_free': not P(cb, 0.0, YC0 + 0.5, 178.2),
                         'board_level_free_mid': not P(cb, 3.0, -36.0, 177.0)}
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d8b_veml_pins', 'run', out)
    print(json.dumps(out, separators=(',', ':')))
