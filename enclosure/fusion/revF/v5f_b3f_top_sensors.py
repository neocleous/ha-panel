# rev F block 3f (2026-11-04): hard-top sensor features (brief: mics Ø1.5 at XC±35.5, lux Ø2 at XC+46, strip pockets
# 30 × 6 × 0.8 + 1 mm gasket, heat-stake pins Ø1.8; VEML6030 under the top at XC+46).
#   Port line y −26.5: 6.4 behind the slab's top-back edge (y −20.1, z 180.0); the inner top's front round ends at y −23.4,
#   so a 6.4-wide pocket cannot sit further forward.
#   Strips (MIC_strip 30 × 6 × 0.8, envelope sheet) at x_rel ±(7.5…37.5), mic centred 2.0 from the outboard end (at ±35.5):
#   the separate VEML6030 breakout (≤ 15 × 15, P) under the lux port at +46 rules out rev D's strip span ±(22…52).
#   Pocket 30.4 × 6.4 × 0.8 into the top wall (z 177.5 → 178.3, 1.7 wall left), stack below: gasket 1.0 (z 178.3–177.3),
#   strip 0.8 (177.3–176.5), back parts ≤ 4.9 mated, cable bend ≥ 10 → keep-out to z 166.5.
#   Heat-stake pins Ø1.8 × 3.5 below the pocket floor (to z 174.8: 1.7 past the strip back for the head) at x_rel ±11.5 and
#   ±30.0 on the strip centre line (3.1 clear of a 3 mm-wide mic package at ±(34…37)).
#   VEML6030 (provisional, outline and chip position unmeasured – E0 issue 8): pocket 15.4 × 15.4 × 0.8 at x_rel 38.3…53.7,
#   y −23.3…−38.7, lux port Ø2 at its centre (46, −31.0); retention after the caliper measurement.
#   Envelopes (hidden): MIC_strip_L/R_env (gasket + strip), KO_mic_L/R_back (back parts + cable bend), VEML_env 15 × 15 × 6.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
EXPECT = {'HOUSING_F_front': 240.593, 'HOUSING_F_door': 55.484}
YP = -26.5; ZI = 177.5; ZP = 178.3
SX0, SX1 = 7.5, 37.5
PINS = (11.5, 30.0)
VX0, VX1, VY0, VY1 = 38.3, 53.7, -38.7, -23.3
LUX = (46.0, -31.0)


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes; tbm = X.tbm
    try:
        for n, v in EXPECT.items():
            b = X.body(n)
            if b is None or abs(b.volume - v) > 0.003:
                raise RuntimeError('guard: %s volume %s, expected %s' % (n, None if b is None else round(b.volume, 3), v))
        for n in ('MIC_strip_L_env', 'VEML_env'):
            if X.body(n) is not None:
                raise RuntimeError('%s exists already' % n)
        fb = X.body('HOUSING_F_front'); v0 = fb.volume
        cut = None
        for s in (1, -1):
            xs = sorted((XC + s * (SX0 - 0.2), XC + s * (SX1 + 0.2)))
            p = X.wbox(xs[0], xs[1], YP + 3.2, YP - 3.2, ZI - 1.0, ZP)
            cut = p if cut is None else X.union(cut, p)
            cut = X.union(cut, X.wcyl_z(XC + s * 35.5, YP, 0.75, ZI - 1.0, 181.0))
        cut = X.union(cut, X.wbox(XC + VX0, XC + VX1, VY0, VY1, ZI - 1.0, ZP))
        cut = X.union(cut, X.wcyl_z(XC + LUX[0], LUX[1], 1.0, ZI - 1.0, 181.0))
        X.combine(fb, [X.add(cut, 'B3F_cut_tmp')], op=CUT)
        fb = X.body('HOUSING_F_front'); v1 = fb.volume
        pins = None
        for s in (1, -1):
            for px in PINS:
                c = X.wcyl_z(XC + s * px, YP, 0.9, ZP - 3.5, ZP + 0.5)
                pins = c if pins is None else X.union(pins, c)
        X.combine(fb, [X.add(pins, 'B3F_pins_tmp')])
        fb = X.body('HOUSING_F_front')
        out['front_cm3'] = [round(v0, 3), round(v1, 3), round(fb.volume, 3)]; out['front_lumps'] = fb.lumps.count
        out['names'] = [b.name for b in X.comp.bRepBodies if b.name.startswith(('HOUSING_F', 'B3F_'))]
        envs = {}
        for s, k in ((1, 'L'), (-1, 'R')):
            xs = sorted((XC + s * SX0, XC + s * SX1))
            e = X.add(X.wbox(xs[0], xs[1], YP + 3.0, YP - 3.0, ZP - 1.8, ZP), 'MIC_strip_%s_env' % k); e.isLightBulbOn = False
            ko = X.add(X.wbox(xs[0], xs[1], YP + 3.0, YP - 3.0, ZP - 1.8 - 10.0, ZP - 1.8), 'KO_mic_%s_back' % k); ko.isLightBulbOn = False
            envs[e.name] = round(e.volume * 1000, 1); envs[ko.name] = round(ko.volume * 1000, 1)
        ve = X.add(X.wbox(XC + LUX[0] - 7.5, XC + LUX[0] + 7.5, LUX[1] - 7.5, LUX[1] + 7.5, ZP - 6.0, ZP), 'VEML_env'); ve.isLightBulbOn = False
        envs['VEML_env'] = round(ve.volume * 1000, 1)
        out['envelopes_mm3'] = envs
        P = lambda x, y, z: X.inside(fb, XC + x, y, z)
        pr = {}
        for s, k in ((1, '+x'), (-1, '-x')):
            pr[k] = {'pocket_open_z178.0': not P(s * 20.0, YP, 178.0), 'pocket_floor_solid_z178.6': P(s * 20.0, YP, 178.6),
                     'mic_port_open_z179.5': not P(s * 35.5, YP, 179.5), 'wall_beside_port_z179.5': P(s * 35.5, YP + 2.0, 179.5),
                     'pin_in_solid_z176.0': P(s * 11.5, YP, 176.0), 'pin_out_solid_z175.0': P(s * 30.0, YP, 175.0),
                     'below_pin_open_z174.5': not P(s * 30.0, YP, 174.5), 'pocket_edge_solid': P(s * (SX1 + 0.6), YP, 178.0) if s < 0 else None}
        pr['veml'] = {'pocket_open': not P(46.0, -36.0, 178.0), 'lux_port_open_z179.5': not P(LUX[0], LUX[1], 179.5),
                      'rib_between_pockets_z178.0': P(38.0, YP, 178.0), 'top_solid_z179.5': P(46.0, -36.0, 179.5)}
        out['probes'] = pr
        log('v5f_b3f_top_sensors', 'built', out)
        names = [b.name for b in X.comp.bRepBodies]
        others = [X.body(n) for n in ['SLAB_frame', 'LCD_glass', 'HOUSING_F_door', 'SPKBOX_L', 'SPKBOX_R', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR',
                                     'MIC_strip_L_env', 'MIC_strip_R_env', 'KO_mic_L_back', 'KO_mic_R_back', 'VEML_env']
                  + [n for n in names if n.startswith('LCD_') and n != 'LCD_glass']]
        r = X.interference(fb, others)
        out['interference_nonzero'] = {k: v for k, v in r.items() if v > 0} or 'all 0 (%d bodies)' % len(r)
        lcd = [X.body(n) for n in names if n.startswith('LCD_')]
        r2 = {}
        for e in ('MIC_strip_L_env', 'MIC_strip_R_env', 'KO_mic_L_back', 'KO_mic_R_back', 'VEML_env'):
            rr = X.interference(X.body(e), lcd + [X.body('SLAB_frame'), X.body('KO_K5_UL'), X.body('KO_K5_UR')])
            r2[e] = {k: v for k, v in rr.items() if v > 0} or 0
        out['env_vs_lcd_lanes'] = r2
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b3f_top_sensors', 'checks', out)
    print(json.dumps(out))
