# rev F rework R2b-2 (2026-11-04), read-only: trial speaker boxes in temporary geometry from the R2b-1 tools
# (TOOL_cav_1p2_slide / TOOL_cav_2p7_slide): air volumes, seat checks, interference with every neighbour, insertion sweep.
# Box (per side, +x shown; -x mirrored about XC):
#   outer = world box (x_rel 46.0...130, y -52.5...-3.7, z 3.0...76.0) ∩ cavity offset 1.2 (D1 0.7 + 0.5) ∩ the same cavity
#           moved +1.0 in y (the box slides sideways 1.0 behind its final position, the housing tapers backwards);
#   inner = (x_rel 47.5..., y -51.0...-5.7, z 4.5...74.5) ∩ cavity offset 2.7 ∩ moved copy -> walls 1.5, front wall 2.0.
#   Front wall y -5.7...-3.7: D40.6 basket hole, 2 x D3.4 clamp holes at the inboard frame holes (x_rel 52.75, z 10.25 /
#   45.75), 2 x D3.2 pegs 3.5 long at the outboard frame holes (88.25) for the bench fit of the speaker; four 0.7 stop pads
#   (D7.5) at the frame corners set the 1 mm rear foam to 0.7. Frame y -3.0...0.0 (envelope SPK_L/R unchanged).
#   Clamp tubes D8 (bore D6.2) from the front wall back through the rear wall: DIN912 M3 x 12 from behind with the 2.5 ball-end
#   key, through wall + foam + frame + front gasket into Ruthex M3 in the baffle (y 0.7...7.4).
#   +x only: USB-A plug pocket (void x_rel 45.15...55.15, y -36.95...-20.95, z 9.95...17.95, 1.5 walls) at the rear stack's
#   lower port. Wire hole D3 through the rear wall at x_rel 62, z 30.
# Planned shell cut (R2c, simulated here): b2d side partitions for y <= 1.2 (cheeks with the touch retention stay), back
# partitions, ceilings for y <= 1.2, all ∩ INNER_E.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
SX, SZ = 70.5, 28.0
XI, WT, YF0, YF1, YR, ZB, ZT = 46.0, 1.5, -5.7, -3.7, -52.5, 3.0, 76.0
BACK = 1.0
SLIDE = {1: 22.0, -1: 22.0}
LIFT = {1: 0.0, -1: 6.0}
PX = {1: (45.4, 46.9), -1: (45.3, 46.8)}


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes
    tbm = X.tbm

    def mv(t, dx, dy, dz):
        m = adsk.core.Matrix3D.create(); m.translation = V3(dx / 10, (dy * C + dz * S) / 10, (-dy * S + dz * C) / 10)
        tbm.transform(t, m); return t

    def ycyl(x, z, r, y0, y1):
        return tbm.createCylinderOrCone(Dw(x, y0, z), r / 10, Dw(x, y1, z), r / 10)

    def isect(a, b):
        t = tbm.copy(a); tbm.booleanOperation(t, tbm.copy(b), B.IntersectionBooleanType); return t

    def vol(t): return round(t.volume * 1000, 1)
    try:
        ie = X.body('INNER_E')
        cav = {1.2: tbm.copy(X.body('TOOL_cav_1p2_slide')), 2.7: tbm.copy(X.body('TOOL_cav_2p7_slide'))}   # from R2b-1
        fb = X.body('HOUSING_F_front')
        cut = None
        for s in (1, -1):
            a, b2 = PX[s]
            xs = sorted((XC + s * a, XC + s * b2)); xo = sorted((XC + s * a, XC + s * 130))
            for p in (X.wbox(xs[0], xs[1], -53.1, 1.2, 3.7, 76.0), X.wbox(xo[0], xo[1], -53.1, -51.6, 3.7, 76.0),
                      X.wbox(xo[0], xo[1], -53.1, 1.2, 74.0, 76.0)):
                cut = p if cut is None else X.union(cut, p)
        tbm.booleanOperation(cut, tbm.copy(ie), B.IntersectionBooleanType)
        fcut = tbm.copy(fb); tbm.booleanOperation(fcut, tbm.copy(cut), B.DifferenceBooleanType)
        out['shell_cut_mm3'] = round((fb.volume - fcut.volume) * 1000, 1)
        boxes = {}; air = {}
        for s in (1, -1):
            xr = lambda v: XC + s * v
            o = X.wbox(xr(XI), xr(130), YR, YF1, ZB, ZT); tbm.booleanOperation(o, tbm.copy(cav[1.2]), B.IntersectionBooleanType)
            i = X.wbox(xr(XI + WT), xr(130), YR + WT, YF0, ZB + WT, ZT - WT); tbm.booleanOperation(i, tbm.copy(cav[2.7]), B.IntersectionBooleanType)
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
            boxes[s] = sh
            chk = {'lumps': sh.lumps.count}
            ring = ycyl(xr(SX), SZ, 23.0, YF1 - 0.5, YF1); X.diff(ring, ycyl(xr(SX), SZ, 20.3, YF1 - 1.0, YF1 + 0.5))
            chk['rear_foam_ring_backed'] = round(isect(ring, sh).volume / ring.volume, 3)
            for z in (10.25, 45.75):                         # (the old D2.5 pilots y 0.7...4.0 are left out of these solids)
                h = ycyl(xr(52.75), z, 2.0, 4.1, 8.4)
                chk['insert_D4_y4.1-8.4_in_shell_z%g' % z] = round(isect(h, fcut).volume / h.volume, 3)
                h = ycyl(xr(52.75), z, 2.0, 0.7, 4.1); X.diff(h, ycyl(xr(52.75), z, 1.3, 0.0, 5.0))
                chk['insert_annulus_y0.7-4.1_z%g' % z] = round(isect(h, fcut).volume / h.volume, 3)
                for xx in (52.75, 88.25):
                    p = ycyl(xr(xx), z, 3.75, 0.7, 1.7); X.diff(p, ycyl(xr(xx), z, 1.3, 0.0, 2.0))
                    chk['pad_seat_x%g_z%g' % (xx, z)] = round(isect(p, fcut).volume / p.volume, 3)
            air_chk = chk
            a_up = tbm.copy(i); tbm.booleanOperation(a_up, solid_in, B.DifferenceBooleanType)
            spk = X.body('SPK_L' if s > 0 else 'SPK_R')
            a_lo = tbm.copy(a_up); tbm.booleanOperation(a_lo, tbm.copy(spk), B.DifferenceBooleanType)
            air[s] = {'box_cm3': round(sh.volume, 3), 'air_upper_cm3': round(a_up.volume, 2), 'air_lower_cm3': round(a_lo.volume, 2),
                      'outer_cm3': round(o.volume, 2), 'checks': air_chk}
        out['air'] = {('+x' if s > 0 else '-x'): v for s, v in air.items()}
        log('v5f_r2b2_trial_boxes', 'boxes', out)
        names = [b.name for b in X.comp.bRepBodies]
        nb = ['TOUCH_PCB', 'KO_touch_back', 'PI5_F', 'PI5_F_cooler', 'GPIO_plugA_env', 'GPIO_plugB_env', 'KO_K7_fan', 'KO_K5_LL', 'KO_K5_LR',
              'KO_K5_UL', 'KO_K5_UR', 'SLAB_frame', 'PD_5807_env', 'KO_5807_pigtail', 'HOUSING_F_door', 'SPK_L', 'SPK_R'] + [n for n in names if n.startswith('LCD_')]
        fin = {}
        for s, sh in boxes.items():
            r = {'front_shell_after_cut': vol(isect(sh, fcut))}
            for n in nb:
                b = X.body(n)
                if b is None: continue
                v = vol(isect(sh, b))
                if v > 0: r[n] = v
            fin['+x' if s > 0 else '-x'] = r
        out['final_interference_mm3'] = fin
        log('v5f_r2b2_trial_boxes', 'final', fin)
        lcd = None                                           # the LCD and slab are fitted before the boxes
        for n in [n for n in names if n.startswith('LCD_')] + ['SLAB_frame']:
            b = X.body(n)
            if b is None: continue
            lcd = tbm.copy(b) if lcd is None else X.union(lcd, tbm.copy(b))
        sweep = {}
        for s, sh in boxes.items():
            spk = X.body('SPK_L' if s > 0 else 'SPK_R')
            mod = X.union(tbm.copy(sh), tbm.copy(spk))
            L, H = SLIDE[s], LIFT[s]
            path = [('fwd', 0, -0.5, 0), ('fwd', 0, -BACK, 0)]
            if H > 0:
                path += [('lift', 0, -BACK, h) for h in (2.0, 4.0, H)]
            path += [('side', -s * t, -BACK, H) for t in (2.0, 5.0, 10.0, 15.0, L)]
            path += [('in', -s * L, -BACK - u, H) for u in (5.0, 15.0, 30.0, 45.0, 60.0, 80.0)]
            r = []
            for (k, dx, dy, dz) in path:
                t = mv(tbm.copy(mod), dx, dy, dz)
                r.append([k, dx, dy, dz, vol(isect(t, fcut)), vol(isect(t, lcd))])
            sweep['+x' if s > 0 else '-x'] = r
        out['sweep_mm3'] = sweep
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_r2b2_trial_boxes', 'trial', out)
    print(json.dumps(out))
