# rev F d3 (2026-11-06; audit finding 24 + decision 2a, finding 36 + decision 1a).
# Touch PCB: B2h's top tabs and bottom lips both sat behind the PCB with zero clearance, so no rigid path to the seat exists
#   (audit 24). A rib fixed to the speaker boxes (decision 2a) cannot work either: in the box's insertion path (sideways at
#   dy -1, rear face 0.5 in front of the lip root band) a rib reaching the PCB crosses the PCB's component zone, and with
#   the boxes in first a rib blocks the PCB. So the boxes hold the PCB through two small clips screwed to them afterwards:
#   - HOUSING_F_front: top tabs removed (x_rel +-(44.0...45.4), y 1.5...2.7, z 43.5...47.5); lips opened 0.3 (y 2.4...2.7
#     removed at z 6.0...6.85) -> bottom channel 1.9 for the 1.6 PCB, which goes in tilted (bottom first) and rotates upright.
#   - SPKBOX_L / _R: solid block on the inboard front corner, x_rel +-(43.5...49.3), y -8.5...-3.7, z 30...46, with a
#     D2.5 x 5.5 pilot along x at (y -6.1, z 38) for an M3 x 8 DIN912 (self-tapping, as the box clamp screws); the block's
#     part inside the box displaces ~70 mm3 of air and keeps the chamber closed.
#   - TOUCH_CLIP_L / _R (new printed parts): base x +-(40.5...43.5), y -8.5...-3.7, z 30...46 (D3.4 hole), arm forward to
#     y 2.0 over x +-(43.6...45.0) (0.25 from the cheek, 0.6 outside the PCB's component zone), z 30...46; a 1 mm CR foam strip
#     (order line A12) on the arm face squeezes to 0.7 against the PCB's 2 mm free edge band.
#   Order: touch PCB -> speaker boxes -> clips (key along x from the empty middle) -> Pi ...
# Cooler exhaust (36): SPKBOX_R's inboard wall 3.55 from the Active Cooler's -x fin face (z 13.6...23.1, y -50.1...-7.6).
#   Recess ("deflector") in that wall with 45-degree lower and upper faces (no downward ceiling): behind the speaker
#   (y -50.1...-33.0) 6.0 deep (z 13.0 / 19.0 / 25.0 / 31.0), alongside the speaker (y -33.0...-7.6) 2.5 deep (z 13.0 / 15.5 /
#   26.5 / 29.0) so the wall stays >= 0.5 off the D40 basket envelope. Wall 1.5 kept (recess pushed into the chamber).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
EXPECT = {'HOUSING_F_front': 236.1819, 'SPKBOX_L': 25.3206, 'SPKBOX_R': 25.0709}
CF = {1: 45.4, -1: 45.3}


def _unused_prism_x(X, s, poly, y0, y1):
    """Solid from an (x_rel_abs, z) polygon (x measured outboard from 0, i.e. |x_rel|), extruded along world y y0..y1, on side s,
    built as a union of thin boxes (polygon is convex per band: list of (z0, z1, xin0, xout0, xin1, xout1) linear bands)."""
    t = None
    for (z0, z1, xa0, xb0, xa1, xb1) in poly:
        n = max(1, int(round((z1 - z0) / 0.25)))
        for i in range(n):
            za = z0 + (z1 - z0) * i / n; zb = z0 + (z1 - z0) * (i + 1) / n; f = (i + 0.5) / n
            xa = xa0 + (xa1 - xa0) * f; xb = xb0 + (xb1 - xb0) * f
            xs = sorted((XC + s * xa, XC + s * xb))
            b = X.wbox(xs[0], xs[1], y0, y1, za, zb)
            t = b if t is None else X.union(t, b)
    return t


def run(_context):
    X = Ctx(); out = {}
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard: %s %s (expected %s)' % (k, None if b is None else round(b.volume, 4), v))
        for n in ('HOUSING_F_front_d2', 'SPKBOX_L_d2', 'SPKBOX_R_d0', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R'):
            if X.body(n) is not None:
                raise RuntimeError('%s exists' % n)
        fb = X.body('HOUSING_F_front')
        for n, k in (('HOUSING_F_front', 'HOUSING_F_front_d2'), ('SPKBOX_L', 'SPKBOX_L_d2'), ('SPKBOX_R', 'SPKBOX_R_d0')):
            c = X.add(X.tbm.copy(X.body(n)), k); c.isLightBulbOn = False
        # --- front: tabs off, lips opened
        cut = None
        for s in (1, -1):
            xs = sorted((XC + s * 43.9, XC + s * CF[s]))
            t = X.wbox(xs[0], xs[1], 1.4, 2.75, 43.4, 47.6)
            xl = sorted((XC + s * 42.9, XC + s * CF[s]))
            l = X.wbox(xl[0], xl[1], 2.4, 2.75, 6.0, 6.85)
            for p in (t, l):
                cut = p if cut is None else X.union(cut, p)
        v0 = fb.volume
        rem = round(vol_x(X, cut, fb), 2)
        X.combine(fb, [X.add(cut, 'D3_tabs_tmp')], op=CUT); fb = X.body('HOUSING_F_front')
        out['front'] = {'cm3': [round(v0, 4), round(fb.volume, 4)], 'removed_mm3': rem, 'lumps': fb.lumps.count}
        # --- boxes: corner blocks + pilots; clips
        res = {}
        for s, bn, cn in ((1, 'SPKBOX_L', 'TOUCH_CLIP_L'), (-1, 'SPKBOX_R', 'TOUCH_CLIP_R')):
            bx = X.body(bn); vb = bx.volume
            xs = sorted((XC + s * 43.5, XC + s * 50.5))
            blk = X.wbox(xs[0], xs[1], -8.5, -3.7, 30.0, 46.0)
            X.diff(blk, X.tbm.createCylinderOrCone(Dw(XC + s * 52.75, -6.0, 45.75), 0.31, Dw(XC + s * 52.75, -53.0, 45.75), 0.31))
            X.combine(bx, [X.add(blk, 'D3_blk_tmp')]); bx = X.body(bn)
            pil = X.tbm.createCylinderOrCone(Dw(XC + s * 43.3, -6.1, 38.0), 0.125, Dw(XC + s * 49.0, -6.1, 38.0), 0.125)
            X.combine(bx, [X.add(pil, 'D3_pil_tmp')], op=CUT); bx = X.body(bn)
            xb = sorted((XC + s * 40.5, XC + s * 43.5)); xa1 = sorted((XC + s * 40.5, XC + s * 45.0)); xa2 = sorted((XC + s * 43.6, XC + s * 45.0))
            clip = X.wbox(xb[0], xb[1], -8.5, -3.7, 30.0, 46.0)
            X.union(clip, X.wbox(xa1[0], xa1[1], -3.7, -0.5, 30.0, 46.0))
            X.union(clip, X.wbox(xa2[0], xa2[1], -0.5, 2.0, 30.0, 46.0))
            X.diff(clip, X.tbm.createCylinderOrCone(Dw(XC + s * 40.0, -6.1, 38.0), 0.17, Dw(XC + s * 44.0, -6.1, 38.0), 0.17))
            cb = X.add(clip, cn)
            res[bn] = {'cm3': [round(vb, 4), round(bx.volume, 4)], 'lumps': bx.lumps.count, 'shells': [l.shells.count for l in bx.lumps]}
            res[cn] = {'cm3': round(cb.volume, 4), 'lumps': cb.lumps.count}
        # --- deflector recess in SPKBOX_R's inboard wall: pocket (outer face |x| 46.0 -> 46+d, flat floor z 13.0, 45-degree
        #     top back to the wall), wall = pocket shifted 1.5 outboard / up / down / along y (union) minus the pocket
        bR = X.body('SPKBOX_R'); vR = bR.volume

        def pocket(d, z_top, y0, y1):
            t = X.wbox(XC - 45.99, XC - (46.0 + d), y0, y1, 13.0, z_top)
            n = int(round(d / 0.5))
            for i in range(n):
                u1 = 46.0 + d - 0.5 * i                      # 45 degrees: each 0.5 slice narrower by 0.5
                X.union(t, X.wbox(XC - 45.99, XC - u1, y0, y1, z_top + 0.5 * i, z_top + 0.5 * (i + 1)))
            return t
        rec = X.union(pocket(6.0, 25.0, -50.1, -33.0), pocket(2.5, 26.5, -33.0, -7.6))
        wall = None
        for (dx, dy, dz) in ((-1.5, 0, 0), (0, 0, 1.5), (0, 0, -1.5), (-1.06, 0, 1.06), (-1.06, 0, -1.06), (0, 1.5, 0), (0, -1.5, 0),
                             (-1.06, 1.06, 0), (-1.06, -1.06, 0)):
            c = mvw(X, X.tbm.copy(rec), dx, dy, dz)
            wall = c if wall is None else X.union(wall, c)
        X.diff(wall, X.tbm.copy(rec))
        inter(X, wall, X.wbox(XC - 46.0, XC - 70.0, -51.9, -5.0, 10.0, 34.0))
        X.combine(bR, [X.add(wall, 'D3_wall_tmp')]); bR = X.body('SPKBOX_R')
        X.combine(bR, [X.add(rec, 'D3_rec_tmp')], op=CUT); bR = X.body('SPKBOX_R')
        res['SPKBOX_R_deflector'] = {'cm3': [round(vR, 4), round(bR.volume, 4)], 'lumps': bR.lumps.count,
                                     'shells': [l.shells.count for l in bR.lumps]}
        out['res'] = res
        out['names'] = sorted(b.name for b in X.comp.bRepBodies if b.name.startswith(('SPKBOX', 'TOUCH_CLIP', 'HOUSING_F_front')) or (' (' in b.name and b.name.startswith(('SPKBOX', 'HOUSING'))))
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        log('v5f_d3_touch_clips_deflector', 'built', out)
        # --- checks
        names = ['HOUSING_F_front', 'TOUCH_PCB', 'KO_touch_back', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'PI5_F', 'PI5_F_cooler',
                 'GPIO_plugA_env', 'GPIO_plugB_env', 'USBA_plug_env', 'USBA_cable_env', 'LCD_panel_body', 'LCD_pcb_76x110',
                 'LCD_components_env_d8.8', 'RESP_CARRIER', 'MAIN_BRACKET', 'MAIN_front_env', 'SLAB_frame', 'KO_K5_LL', 'KO_K5_LR',
                 'KO_K7_fan', 'BME680_env'] + [b.name for b in X.comp.bRepBodies if b.name.startswith('LEAD_') and not b.name.endswith(('_b4n', '_c1', '_b5', '_c1v1'))]
        cx = {}
        for cn in ('TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'SPKBOX_L', 'SPKBOX_R'):
            c = X.body(cn); hit = {}
            for n in names + ['TOUCH_CLIP_L', 'TOUCH_CLIP_R']:
                o = X.body(n)
                if o is None or n == cn:
                    continue
                v = vol_x(X, X.tbm.copy(c), X.tbm.copy(o))
                if v > 0:
                    hit[n] = v
            cx[cn] = hit or 'all 0'
        out['x'] = cx
        P = lambda b, x, y, z: X.inside(X.body(b), XC + x, y, z)
        out['probes'] = {'tabL_gone': not P('HOUSING_F_front', 44.5, 2.1, 45.5), 'tabR_gone': not P('HOUSING_F_front', -44.5, 2.1, 45.5),
                         'cheekL_kept': P('HOUSING_F_front', 46.2, 3.0, 45.5), 'cheekR_kept': P('HOUSING_F_front', -46.0, 3.0, 45.5),
                         'lipL_open_y2.55': not P('HOUSING_F_front', 44.0, 2.55, 6.4), 'lipL_kept_y2.2': P('HOUSING_F_front', 44.0, 2.2, 6.4),
                         'lipR_open_y2.55': not P('HOUSING_F_front', -44.0, 2.55, 6.4), 'ledgeL_kept': P('HOUSING_F_front', 44.0, 3.5, 5.5),
                         'pilotL_open': not P('SPKBOX_L', 46.0, -6.1, 38.0), 'pilotL_wall': P('SPKBOX_L', 46.0, -6.1 + 2.1, 38.0),
                         'pilotR_open': not P('SPKBOX_R', -46.0, -6.1, 38.0), 'boxL_air_x50_y-20_z38': not P('SPKBOX_L', 50.0, -20.0, 38.0),
                         'deflA_open_x-50_z22': not P('SPKBOX_R', -50.0, -40.0, 22.0), 'deflA_wall_x-52.8_z22': P('SPKBOX_R', -52.8, -40.0, 22.0),
                         'deflA_air_x-54_z22': not P('SPKBOX_R', -54.0, -40.0, 22.0), 'deflB_open_x-48_z20': not P('SPKBOX_R', -48.0, -20.0, 20.0),
                         'deflB_wall_x-49.3_z20': P('SPKBOX_R', -49.3, -20.0, 20.0)}
        d = {}
        for n in ('SPK_R', 'PI5_F_cooler'):
            r = X.app.measureManager.measureMinimumDistance(X.body('SPKBOX_R'), X.body(n)); d[n] = round(r.value * 10, 3)
        out['min_dist_boxR'] = d
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d3_touch_clips_deflector', 'run', out)
    print(json.dumps(out, separators=(',', ':')))
