# rev F rework R2c (2026-11-04): separate speaker boxes (Daniel 2026-11-03 23:41; plan of 22:54 accepted with R1).
# 1. HOUSING_F_front: cut the block-2 chamber walls (b2d boxes ∩ INNER_E): side partitions for y <= 1.2 (the cheeks at
#    y >= 1.2 keep the touch-PCB retention), back partitions (and their wire holes), ceilings for y <= 1.2.
# 2. Baffles: four 0.7 stop pads D7.5 on the baffle face (y 0.0...0.7) at the frame corners - they set the 1 mm front
#    gasket to 0.7 and take the clamp load; D2.5 pilots y -0.5...5.0 at the inboard frame holes (x_rel 52.75, z 10.25 /
#    45.75) for the M3 x 10 DIN912 clamp screws, self-tapping (R2b-2: a 5.7 Ruthex insert would leave 0.8 of chin skin
#    after the D1 recess; the pilot leaves 1.8); the old outboard D2.5 pilots filled.
# 3. SPKBOX_L (+x) / SPKBOX_R (-x) as trialled in R2b-2 with the R2b-4 fixes: rear outer face y -52.0, 3.5 x 3.5 step along
#    the bottom-outboard edge (outer z < 6.5 within 4.7 of INNER_E removed, air z < 8.0 within 6.2) clear of the floor cove.
#    Path (R2b-4, 0 mm3 throughout): lift 6, in at 37 inboard, out to the final x 1.0 behind, lower 6, forward 1.0.
# Guarded on the R1 volumes.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
SX, SZ = 70.5, 28.0
XI, WT, YF0, YF1, YR, ZB, ZT = 46.0, 1.5, -5.7, -3.7, -52.0, 3.0, 76.0
ZSO, ZSI = 6.5, 8.0
PX = {1: (45.4, 46.9), -1: (45.3, 46.8)}
EXPECT = {'HOUSING_F_front': 265.519, 'HOUSING_F_door': 55.484}


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes
    tbm = X.tbm

    def mv(t, dx, dy, dz):
        m = adsk.core.Matrix3D.create(); m.translation = V3(dx / 10, (dy * C + dz * S) / 10, (-dy * S + dz * C) / 10)
        tbm.transform(t, m); return t

    def ycyl(x, z, r, y0, y1):
        return tbm.createCylinderOrCone(Dw(x, y0, z), r / 10, Dw(x, y1, z), r / 10)
    try:
        for n, v in EXPECT.items():
            b = X.body(n)
            if b is None or abs(b.volume - v) > 0.002:
                raise RuntimeError('guard: %s volume %s, expected %s' % (n, None if b is None else round(b.volume, 3), v))
        if X.body('SPKBOX_L') is not None or X.body('SPKBOX_R') is not None:
            raise RuntimeError('boxes exist already')
        ie = X.body('INNER_E'); fb = X.body('HOUSING_F_front')
        v0 = fb.volume
        # 1. old chamber walls
        cut = None
        for s in (1, -1):
            a, b2 = PX[s]
            xs = sorted((XC + s * a, XC + s * b2)); xo = sorted((XC + s * a, XC + s * 130))
            for p in (X.wbox(xs[0], xs[1], -53.1, 1.2, 3.7, 76.0), X.wbox(xo[0], xo[1], -53.1, -51.6, 3.7, 76.0),
                      X.wbox(xo[0], xo[1], -53.1, 1.2, 74.0, 76.0)):
                cut = p if cut is None else X.union(cut, p)
        tbm.booleanOperation(cut, tbm.copy(ie), B.IntersectionBooleanType)
        X.combine(fb, [X.add(cut, 'R2C_walls_tmp')], op=CUT)
        fb = X.body('HOUSING_F_front')
        out['walls_removed_cm3'] = round(v0 - fb.volume, 3)
        out['after_cut'] = {'names': [b.name for b in X.comp.bRepBodies if b.name.startswith('HOUSING_F')], 'lumps': fb.lumps.count}
        if fb.lumps.count != 1:
            raise RuntimeError('front shell split by the wall cut: %s' % out['after_cut'])
        # 2. baffle: stop pads, clamp pilots, outboard pilot fill
        holes = None; add = None
        for s in (1, -1):
            for z in (10.25, 45.75):
                h = ycyl(XC + s * 52.75, z, 1.25, -0.5, 5.0)
                holes = h if holes is None else X.union(holes, h)
                for t in (ycyl(XC + s * 52.75, z, 3.75, 0.0, 0.9), X.union(ycyl(XC + s * 88.25, z, 3.75, 0.0, 0.9), ycyl(XC + s * 88.25, z, 1.3, 0.6, 4.1))):
                    add = t if add is None else X.union(add, t)
        v1 = fb.volume
        X.combine(fb, [X.add(add, 'R2C_pads_tmp')])
        fb = X.body('HOUSING_F_front')
        X.combine(fb, [X.add(holes, 'R2C_pilots_tmp')], op=CUT)
        fb = X.body('HOUSING_F_front')
        out['baffle_delta_mm3'] = round((fb.volume - v1) * 1000, 1)
        # 3. boxes
        cav = {1.2: tbm.copy(X.body('TOOL_cav_1p2_slide')), 2.7: tbm.copy(X.body('TOOL_cav_2p7_slide'))}   # from R2b-1
        res = {}
        for s, nm in ((1, 'SPKBOX_L'), (-1, 'SPKBOX_R')):
            xr = lambda v: XC + s * v
            o = X.wbox(xr(XI), xr(130), YR, YF1, ZB, ZT); tbm.booleanOperation(o, tbm.copy(cav[1.2]), B.IntersectionBooleanType)
            st = X.wbox(xr(XI), xr(130), YR - 1, YF1 + 1, ZB - 1, ZSO); X.diff(st, tbm.copy(X.body('TOOL_cav_4p7_slide'))); X.diff(o, st)
            i = X.wbox(xr(XI + WT), xr(130), YR + WT, YF0, ZB + WT, ZT - WT); tbm.booleanOperation(i, tbm.copy(cav[2.7]), B.IntersectionBooleanType)
            st = X.wbox(xr(XI), xr(130), YR - 1, YF1 + 1, ZB - 1, ZSI); X.diff(st, tbm.copy(X.body('TOOL_cav_6p2_slide'))); X.diff(i, st)
            sh = tbm.copy(o); tbm.booleanOperation(sh, tbm.copy(i), B.DifferenceBooleanType)
            solid_in = None
            for z in (10.25, 45.75):
                tube = ycyl(xr(52.75), z, 4.0, YF0, YR)
                solid_in = tube if solid_in is None else X.union(solid_in, tube)
            if s > 0:
                X.union(solid_in, X.wbox(xr(XI), xr(56.65), -38.45, -19.45, 8.45, 19.45))
            X.union(sh, tbm.copy(solid_in))
            for z in (10.25, 45.75):
                X.diff(sh, ycyl(xr(52.75), z, 3.1, YF0, YR - 1.0))
                X.diff(sh, ycyl(xr(52.75), z, 1.7, YF0 - 0.5, YF1 + 0.5))
                X.union(sh, ycyl(xr(88.25), z, 1.6, YF1, -0.2))
                rp = ycyl(xr(52.75), z, 3.75, YF1 - 0.2, YF1 + 0.7); X.diff(rp, ycyl(xr(52.75), z, 1.7, YF1 - 1.0, YF1 + 1.5))
                X.union(sh, rp); X.union(sh, ycyl(xr(88.25), z, 3.75, YF1 - 0.2, YF1 + 0.7))
            X.diff(sh, ycyl(xr(SX), SZ, 20.3, YF0 - 0.5, YF1 + 0.5))
            if s > 0:
                X.diff(sh, X.wbox(xr(44.0), xr(55.15), -36.95, -20.95, 9.95, 17.95))
            X.diff(sh, ycyl(xr(62.0), 30.0, 1.5, YR - 1.0, YR + WT + 1.0))
            air_up = tbm.copy(i); tbm.booleanOperation(air_up, tbm.copy(solid_in), B.DifferenceBooleanType)
            air_lo = tbm.copy(air_up); tbm.booleanOperation(air_lo, tbm.copy(X.body('SPK_L' if s > 0 else 'SPK_R')), B.DifferenceBooleanType)
            bb = X.add(sh, nm)
            res[nm] = {'cm3': round(bb.volume, 3), 'lumps': bb.lumps.count, 'air_upper_cm3': round(air_up.volume, 2), 'air_lower_cm3': round(air_lo.volume, 2)}
        out['boxes'] = res
        out['front_cm3'] = (round(v0, 3), round(fb.volume, 3))
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        pr = {}
        for s in (1, -1):
            k = '+x' if s > 0 else '-x'
            pr[k] = {'partition_gone_y-20': not X.inside(fb, XC + s * 46.0, -20.0, 30.0),
                     'cheek_kept_y3': X.inside(fb, XC + s * 46.0, 3.0, 30.0),
                     'back_partition_gone': not X.inside(fb, XC + s * 70.0, -52.3, 30.0),
                     'ceiling_gone_y-20': not X.inside(fb, XC + s * 70.0, -20.0, 75.0),
                     'pilot_open': not X.inside(fb, XC + s * 52.75, 3.0, 10.25) and not X.inside(fb, XC + s * 52.75, 3.0, 45.75),
                     'pilot_wall': X.inside(fb, XC + s * 54.5, 3.0, 10.25) and X.inside(fb, XC + s * 54.5, 3.0, 45.75),
                     'pilot_bottom_solid_y5.5': X.inside(fb, XC + s * 52.75, 5.5, 10.25) and X.inside(fb, XC + s * 52.75, 5.5, 45.75),
                     'pad_in': X.inside(fb, XC + s * 55.5, 0.4, 10.25), 'pad_out': X.inside(fb, XC + s * 88.25, 0.4, 45.75),
                     'pilot_filled': X.inside(fb, XC + s * 88.25, 2.0, 10.25)}
        out['probes'] = pr
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_r2c_build_boxes', 'build', out)
    print(json.dumps(out))
