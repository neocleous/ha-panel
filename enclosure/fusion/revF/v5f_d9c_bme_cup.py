# rev F d9c (2026-11-06): BME680 pocket to the 20 x 15 x 6 placeholder (audit finding 37 / 40, Daniel's decision 1 b).
#   Frame (t, u, w): t along the board's 20 (0.6504, -0.7596, 0), u up the wall (0.1139, 0.0976, 0.9887), w into the room
#   (= -n_out = (0.751, 0.643, -0.15)); origin = the old envelope centre (-73.44, -42.106, 91.325) moved +4.0 along u (the
#   sensor and its two slots go 4 mm up the wall, so the cup's 45° underside stays 1.0 above the right box (z 77)).
#   HOUSING_F_front (old -> HOUSING_F_front_d9, hidden):
#     old slots filled (wall profile), slots re-cut 4.0 higher (TOOL_bme680_slots, old -> TOOL_bme680_slots_d9);
#     a cup moulded to the wall round the board: walls 1.2, cavity t ±10.5 x u -8.0…8.0 x wall…w 5.5 (0.5 round the envelope,
#     2.0 for closed-cell foam on the room side, A13), open at the top; a solid 45° underside down to z 77 (prints without
#     support); four 0.5 seat pads on the wall at the board's corners (clear of the slots); a 4 x 3.5 lead notch through the
#     floor under the header edge (the lead ends there, B4n); two heat-stake bosses Ø3.6 outside the side walls with pins
#     Ø1.8 to u 11.0.
#   BME_LID (new printed part): plate u 8.0…9.2 over the cup and the bosses, 0.2 off the wall, two Ø2.1 holes for the pins,
#     a 0.5 rib that clamps the board's top edge.
#   BME680_env (old -> BME680_env_d9) moved +4.0 along u; FOAM_bme_env (new, hidden); LEAD_BME680 (old -> LEAD_BME680_d9)
#     re-routed to rise through the floor notch to the header edge.
#   The cup goes on as one tool (walls + underside + bosses - cavity - notch + pads); the cavity is not cut from the front, so
#   the wall's own inner face inside the cup stays as it was (its 0.04 mm departure from the INNER_E skin is left alone).
#   DRY = True (set by the loader) builds every tool and reports volumes and overlaps without changing the model.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
FR = 'HOUSING_F_front'
EXPECT = {FR: 233.5514}
CE0 = (-73.44, -42.106, 91.325)
def _unit(v):
    n = math.sqrt(sum(c * c for c in v)); return tuple(c / n for c in v)


TT = _unit((0.6504, -0.7596, 0.0))
_u = (0.1139, 0.0976, 0.9887); _k = sum(_u[i] * TT[i] for i in range(3))
UU = _unit(tuple(_u[i] - _k * TT[i] for i in range(3)))            # exactly normal to TT (OrientedBoundingBox3D needs it)
NI = (-(TT[1] * UU[2] - TT[2] * UU[1]), -(TT[2] * UU[0] - TT[0] * UU[2]), -(TT[0] * UU[1] - TT[1] * UU[0]))   # -(TT x UU)
DU = 4.0
CE = tuple(CE0[i] + DU * UU[i] for i in range(3))
Z_BOX = 77.0


def P(t, u, w):
    return tuple(CE[i] + t * TT[i] + u * UU[i] + w * NI[i] for i in range(3))


def fbox(X, t0, t1, u0, u1, w0, w1):          # box in the (t, u, w) frame
    c = P((t0 + t1) / 2, (u0 + u1) / 2, (w0 + w1) / 2)
    return lbox(X, c, TT, UU, t1 - t0, u1 - u0, w1 - w0)


def fcyl_u(X, t, w, u0, u1, r0, r1=None):     # cylinder / cone along u
    a = P(t, u0, w); b = P(t, u1, w)
    return X.tbm.createCylinderOrCone(Dw(XC + a[0], a[1], a[2]), r0 / 10, Dw(XC + b[0], b[1], b[2]), (r0 if r1 is None else r1) / 10)


def air(X, skin='TOOL_inner_skin_0p7'):        # room air inside the wall's inner surface
    a = tb_copy(X, 'INNER_E'); X.diff(a, tb_copy(X, skin)); return a


def run(_context):
    X = Ctx(); out = {}; t0 = time.time(); dry = globals().get('DRY', True)
    try:
        fb = X.body(FR)
        if abs(fb.volume - EXPECT[FR]) > 0.0005:
            raise RuntimeError('guard: front %s' % round(fb.volume, 4))
        olds = ('HOUSING_F_front_d9', 'TOOL_bme680_slots_d9', 'BME680_env_d9', 'LEAD_BME680_d9', 'BME_LID', 'FOAM_bme_env')
        for n in olds:
            if X.body(n) is not None:
                raise RuntimeError('%s exists already' % n)
        AIR = air(X)
        region = fbox(X, -16, 16, -26, 16, -12, 12)         # everything happens inside this
        inter(X, AIR, region)
        outer = tb_copy(X, 'REF_F_outer'); X.diff(outer, tb_copy(X, 'TOOL_outer_skin_0p7')); inter(X, outer, X.tbm.copy(region))
        wallp = X.tbm.copy(outer); X.diff(wallp, X.tbm.copy(AIR))
        # slots
        so = tb_copy(X, 'TOOL_bme680_slots')
        sf = X.tbm.copy(wallp); inter(X, sf, X.tbm.copy(so))            # wall material to put back in the old slots
        sn = X.tbm.copy(so); mvw(X, sn, DU * UU[0], DU * UU[1], DU * UU[2])
        out['slots_fill_mm3'] = round(sf.volume * 1000, 2); out['slots_new_mm3'] = round(sn.volume * 1000, 2)
        # cup solid: walls box + 45° underside, inside the outer limit, above the box
        wb = fbox(X, -11.7, 11.7, -9.2, 8.0, -12.0, 6.7)
        d = tuple((UU[i] - NI[i]) / math.sqrt(2) for i in range(3))   # s = (u - w)/√2 ≥ (-9.2 - 6.7)/√2 below the floor
        s0 = (-9.2 - 6.7) / math.sqrt(2); L = 120.0
        cc = tuple(CE[i] + d[i] * (s0 + L / 2) for i in range(3))
        half = lbox(X, cc, TT, d, L, L, L)
        wg = fbox(X, -11.7, 11.7, -30.0, -9.2, -12.0, 6.7); inter(X, wg, half)
        cup = X.union(wb, wg)
        inter(X, cup, X.tbm.copy(outer)); inter(X, cup, X.wbox(-250, 250, -250, 250, Z_BOX, 260))
        # bosses (outside the side walls) with 45° cones under them, pins on top
        for s in (1, -1):
            X.union(cup, fcyl_u(X, s * 12.6, 1.5, 2.0, 8.0, 1.8))
            X.union(cup, fcyl_u(X, s * 12.6, 1.5, 0.4, 2.0, 0.2, 1.8))
            X.union(cup, fcyl_u(X, s * 12.6, 1.5, 7.9, 11.0, 0.9))
        cav = fbox(X, -10.5, 10.5, -8.0, 8.6, -12.0, 5.5); inter(X, cav, X.tbm.copy(AIR))
        notch = fbox(X, -2.0, 2.0, -30.0, -7.9, 0.0, 3.5); inter(X, notch, X.tbm.copy(AIR))
        pads = None
        for tc in (9.25, -9.25):
            for uc in (6.75, -6.75):
                p_ = fbox(X, tc - 0.75, tc + 0.75, uc - 0.75, uc + 0.75, -12.0, -3.0); inter(X, p_, X.tbm.copy(AIR))
                pads = p_ if pads is None else X.union(pads, p_)
        # what the cup would take from the front and what it meets
        fc = tb_copy(X, FR); inter(X, fc, X.tbm.copy(cav)); out['front_in_cavity_mm3'] = round(fc.volume * 1000, 2)
        fn = tb_copy(X, FR); inter(X, fn, X.tbm.copy(notch)); out['front_in_notch_mm3'] = round(fn.volume * 1000, 2)
        add = X.tbm.copy(cup); X.diff(add, X.tbm.copy(cav)); X.diff(add, X.tbm.copy(notch)); X.union(add, X.tbm.copy(pads))
        newm = X.tbm.copy(add); X.diff(newm, tb_copy(X, FR))
        out['cup_mm3'] = [round(add.volume * 1000, 1), round(newm.volume * 1000, 1)]
        out['newm_in_wall_mm3'] = vol_x(X, X.tbm.copy(newm), X.tbm.copy(wallp))
        ox = {}
        for n in ('SPKBOX_R', 'LEAD_RADAR', 'LEAD_BME680', 'HOUSING_F_door', 'MAIN_BRACKET', 'KO_K5_LR', 'KO_K5_UR', 'KO_capkey_SR',
                  'LD2410C_env_F', 'SPK_R', 'PI5_F', 'MAIN_front_env', 'MAIN_back_env'):
            if X.body(n) is not None:
                v = vol_x(X, X.tbm.copy(newm), tb_copy(X, n))
                if v > 0.0:
                    ox[n] = v
        out['cup_x'] = ox
        # lid
        lair = air(X, 'TOOL_inner_skin_0p9'); inter(X, lair, X.tbm.copy(region))
        lid = fbox(X, -14.4, 14.4, 8.0, 9.2, -12.0, 6.7); inter(X, lid, lair)
        for s in (1, -1):
            X.diff(lid, fcyl_u(X, s * 12.6, 1.5, 7.5, 9.7, 1.05))
        X.union(lid, fbox(X, -9.5, 9.5, 7.5, 8.05, -1.0, 1.0))
        out['lid_mm3'] = round(lid.volume * 1000, 1); out['lid_lumps'] = lid.lumps.count
        out['lid_x_front_mm3'] = vol_x(X, X.tbm.copy(lid), tb_copy(X, FR))
        out['lid_x_cupnew_mm3'] = vol_x(X, X.tbm.copy(lid), X.tbm.copy(add))
        # envelopes
        env = tb_copy(X, 'BME680_env'); mvw(X, env, DU * UU[0], DU * UU[1], DU * UU[2])
        foam = fbox(X, -10.5, 10.5, -8.0, 8.0, 3.5, 5.5)
        out['env_x_add_mm3'] = vol_x(X, X.tbm.copy(env), X.tbm.copy(add))
        out['env_x_front_mm3'] = vol_x(X, X.tbm.copy(env), tb_copy(X, FR))
        out['env_x_lid_mm3'] = vol_x(X, X.tbm.copy(env), X.tbm.copy(lid))
        out['foam_x_add_mm3'] = vol_x(X, X.tbm.copy(foam), X.tbm.copy(add))
        # lead: B4n joints up to (-38, -22, 92), then down beside the room-side wall to under the notch and up to the header
        hd = P(0.0, -7.5, 1.75); bl = P(0.0, -15.5, 1.75); bo = P(0.0, -15.5, 10.0)
        pts = [(-36.0, 2.0, 46.0), (-36.0, 0.5, 52.0), (-38.0, -8.0, 60.0), (-38.0, -22.0, 92.0), (-50.0, -26.0, 96.0), (-60.0, -32.0, 94.0),
               bo, bl, hd]
        lead = None
        for a, b in zip(pts[:-1], pts[1:]):
            c_ = X.tbm.createCylinderOrCone(Dw(XC + a[0], a[1], a[2]), 0.15, Dw(XC + b[0], b[1], b[2]), 0.15)
            lead = c_ if lead is None else X.union(lead, c_)
        for q in pts[1:-1]:
            X.union(lead, X.tbm.createSphere(Dw(XC + q[0], q[1], q[2]), 0.15))
        lx = {}
        for n in ('SPKBOX_R', 'LEAD_RADAR', 'MAIN_front_env', 'KO_K5_LR', 'PI5_F_cooler', 'SPK_R', 'MAIN_BRACKET'):
            if X.body(n) is not None:
                v = vol_x(X, X.tbm.copy(lead), tb_copy(X, n))
                if v > 0.0:
                    lx[n] = v
        nf = X.tbm.copy(add); X.union(nf, tb_copy(X, FR))
        lx['front_after'] = vol_x(X, X.tbm.copy(lead), nf)
        out['lead_x'] = lx
        out['lead_pts'] = [[round(c, 2) for c in q] for q in pts[5:]]
        out['lead_len_mm'] = round(sum(math.dist(a, b) for a, b in zip(pts[:-1], pts[1:])), 1)
        if not dry:
            c0 = X.add(tb_copy(X, FR), 'HOUSING_F_front_d9'); c0.isLightBulbOn = False
            v0 = fb.volume
            X.combine(fb, [X.add(sf, 'D9C_fill_tmp')]); fb = X.body(FR)
            X.combine(fb, [X.add(add, 'D9C_cup_tmp')]); fb = X.body(FR)
            X.combine(fb, [X.add(X.tbm.copy(sn), 'D9C_slots_tmp')], op=CUT); fb = X.body(FR)
            out['front_cm3'] = [round(v0, 4), round(fb.volume, 4)]; out['front_lumps'] = fb.lumps.count
            out['front_voids'] = sum(1 for li in range(fb.lumps.count) for si in range(fb.lumps.item(li).shells.count)
                                     if fb.lumps.item(li).shells.item(si).isVoid)
            o = X.body('TOOL_bme680_slots'); o.name = 'TOOL_bme680_slots_d9'; o.isLightBulbOn = False
            X.add(sn, 'TOOL_bme680_slots').isLightBulbOn = False
            o = X.body('BME680_env'); o.name = 'BME680_env_d9'; o.isLightBulbOn = False
            X.add(env, 'BME680_env').isLightBulbOn = False
            X.add(foam, 'FOAM_bme_env').isLightBulbOn = False
            o = X.body('LEAD_BME680'); o.name = 'LEAD_BME680_d9'; o.isLightBulbOn = False
            X.add(lead, 'LEAD_BME680').isLightBulbOn = False
            lb = X.add(lid, 'BME_LID')
            out['lid_cm3'] = round(lb.volume, 4)
            PR = lambda b, t, u, w: X.inside(b, XC + P(t, u, w)[0], P(t, u, w)[1], P(t, u, w)[2])
            out['probes'] = {'cavity_free': not PR(fb, 0, 0, 0), 'foam_zone_free': not PR(fb, 0, 0, 4.5),
                             'back_wall': PR(fb, 0, 0, 6.1), 'side_wall_rear': PR(fb, 11.1, 0, 2.0), 'side_wall_front': PR(fb, -11.1, 0, 2.0),
                             'floor': PR(fb, 0, -8.6, 4.5), 'wedge': PR(fb, 0, -12.0, 0.0), 'notch_free': not PR(fb, 0, -8.6, 1.75),
                             'pin': PR(fb, 12.6, 10.0, 1.5), 'boss': PR(fb, -12.6, 5.0, 2.9), 'top_open': not PR(fb, 0, 8.3, 2.0),
                             'old_slot_filled': PR(fb, 0, -7.0, -4.75), 'new_slot1_open': not PR(fb, 0, -3.0, -4.75), 'new_slot2_open': not PR(fb, 0, 3.0, -4.75),
                             'pad': PR(fb, 9.25, 6.75, -3.2), 'lid_hole': not PR(lb, 12.6, 8.6, 1.5), 'lid_plate': PR(lb, 0, 8.6, 3.0)}
        out['dry'] = dry
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d9c_bme_cup', 'dry' if globals().get('DRY', True) else 'run', out)
    print(json.dumps(out, separators=(',', ':')))
