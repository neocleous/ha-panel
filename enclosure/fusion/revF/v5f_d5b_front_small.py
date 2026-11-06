# rev F audit-response d5b (2026-11-06): front-shell small fixes (audit findings 1, 3, 14). Probe: v5f_d5a_probe.
#   1  the two closed void shells at the top of the Ø40 speaker bores (x_rel ±70.5, y 4.66, z 47.98, ≈ 0.23 mm³ each) filled
#      with exactly that air: (design box round each void shell + 0.002) − front, joined.
#   3  the 10 magnet pockets (Ø8.3 × 1.8, floor toward the door, skin 0.29 on the axis / p10 0.21–0.26 per the audit): floor
#      moved 0.2 toward the cavity (Ø8.4 disc, 0.05 into the floor) -> skin 0.49 on the axis (p10 ≈ 0.41–0.46), pocket 1.6
#      deep for the 1.5 magnets; magnet faces 1.4 -> 1.6 apart.
#   14 Pi bosses (18.35 / −39.65, −5.5 / −54.5): seat Ø6.0 -> Ø6.8 (z 7.5–8.0; ring round the Ø4.0 insert hole 1.0 -> 1.4;
#      the Pi has nothing below its PCB within r 3.8 of the holes); rear pair hole bottom z 0.8 -> 1.5 (floor skin 1.5); holes
#      Ø4.0 re-cut z 1.5–8.1 (6.5 deep for the 5.7 insert).
#   HOUSING_F_front (old -> HOUSING_F_front_d5a, hidden).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
F = 'HOUSING_F_front'
EXPECT = {F: 236.2249}
PI_HOLES = ((18.35, -5.5), (-39.65, -5.5), (18.35, -54.5), (-39.65, -54.5))
REAR = ((18.35, -54.5), (-39.65, -54.5))


def pockets(b):
    res = []
    for f in b.faces:
        g = f.geometry
        if g.objectType != adsk.core.Cylinder.classType() or abs(g.radius * 10 - 4.15) > 0.02:
            continue
        ax = g.axis; ax.normalize(); o = g.origin
        ts = [((v.geometry.x - o.x) * ax.x + (v.geometry.y - o.y) * ax.y + (v.geometry.z - o.z) * ax.z) * 10 for v in f.vertices]
        res.append((ax, o, min(ts), max(ts)))
    return res


def pt(o, ax, t):
    return P3(o.x + ax.x * t / 10, o.y + ax.y * t / 10, o.z + ax.z * t / 10)


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        fb = X.body(F)
        if abs(fb.volume - EXPECT[F]) > 0.0005:
            raise RuntimeError('guard: front %s' % round(fb.volume, 4))
        if X.body('HOUSING_F_front_d5a') is not None:
            raise RuntimeError('HOUSING_F_front_d5a exists already')
        c = X.add(X.tbm.copy(fb), 'HOUSING_F_front_d5a'); c.isLightBulbOn = False
        v0 = fb.volume
        # 1. voids
        boxes = []
        for li in range(fb.lumps.count):
            L = fb.lumps.item(li)
            for si in range(L.shells.count):
                s = L.shells.item(si)
                if s.isVoid:
                    bb = s.boundingBox; m = 0.0002
                    boxes.append(dbox(X, (bb.minPoint.x - m) * 10, (bb.maxPoint.x + m) * 10, (bb.minPoint.y - m) * 10, (bb.maxPoint.y + m) * 10,
                                      (bb.minPoint.z - m) * 10, (bb.maxPoint.z + m) * 10))
        vf = None
        for bx in boxes:
            X.diff(bx, X.tbm.copy(fb))
            vf = bx if vf is None else X.union(vf, bx)
        out['void_fill_mm3'] = None if vf is None else round(vf.volume * 1000, 4)
        if vf is not None:
            if vf.volume * 1000 > 1.0:
                raise RuntimeError('void fill too large: %s mm3' % round(vf.volume * 1000, 3))
            X.combine(fb, [X.add(vf, 'D5B_void_tmp')]); fb = X.body(F)
        out['after_voids'] = round(fb.volume, 4)
        # 3. magnet pocket floors
        P = pockets(fb); out['pockets'] = len(P)
        disc = None; fl = []
        for ax, o, t_lo, t_hi in P:
            lo_solid = fb.pointContainment(pt(o, ax, t_lo - 0.05)) in INS; hi_solid = fb.pointContainment(pt(o, ax, t_hi + 0.05)) in INS
            if lo_solid == hi_solid:
                raise RuntimeError('pocket floor end ambiguous at %s' % [round(v, 2) for v in (o.x * 10 - XC, wy(o), wz(o))])
            if lo_solid:
                a, b = pt(o, ax, t_lo - 0.05), pt(o, ax, t_lo + 0.2)
            else:
                a, b = pt(o, ax, t_hi + 0.05), pt(o, ax, t_hi - 0.2)
            d = X.tbm.createCylinderOrCone(a, 0.42, b, 0.42); disc = d if disc is None else X.union(disc, d)
            fl.append('lo' if lo_solid else 'hi')
        out['floor_ends'] = fl
        X.combine(fb, [X.add(disc, 'D5B_disc_tmp')]); fb = X.body(F)
        out['after_pockets'] = round(fb.volume, 4)
        # 14. Pi seats and rear hole bottoms
        add = None; holes = None
        for (x, y) in PI_HOLES:
            s_ = X.wcyl_z(XC + x, y, 3.4, 7.5, 8.0); add = s_ if add is None else X.union(add, s_)
            h_ = X.wcyl_z(XC + x, y, 2.0, 1.5, 8.1); holes = h_ if holes is None else X.union(holes, h_)
        for (x, y) in REAR:
            X.union(add, X.wcyl_z(XC + x, y, 2.0, 0.7, 1.55))
        X.combine(fb, [X.add(add, 'D5B_seat_tmp')]); fb = X.body(F)
        X.combine(fb, [X.add(holes, 'D5B_hole_tmp')], op=CUT); fb = X.body(F)
        out['front_cm3'] = [round(v0, 4), round(fb.volume, 4)]; out['front_lumps'] = fb.lumps.count
        out['void_shells_left'] = sum(1 for li in range(fb.lumps.count) for si in range(fb.lumps.item(li).shells.count)
                                      if fb.lumps.item(li).shells.item(si).isVoid)
        # probes
        Pp = lambda x, y, z: X.inside(fb, XC + x, y, z)
        pr = {}
        for (x, y) in PI_HOLES:
            pr['%g,%g' % (x, y)] = {'seat_r3.2_z7.8': Pp(x + 3.2, y, 7.8), 'no_seat_r3.6': not Pp(x + 3.6, y, 7.8),
                                    'hole_open_z1.6': not Pp(x, y, 1.6) and not Pp(x, y, 7.9),
                                    'skin_z1.4': Pp(x, y, 1.4)}
        sk = []
        for ax, o, t_lo, t_hi in pockets(fb):
            lo_solid = fb.pointContainment(pt(o, ax, t_lo - 0.05)) in INS
            t_f, sg = (t_lo, -1.0) if lo_solid else (t_hi, 1.0)
            k = 0.0
            while k < 3.0 and fb.pointContainment(pt(o, ax, t_f + sg * (k + 0.01))) in INS:
                k += 0.01
            sk.append([round(abs(t_hi - t_lo), 3), round(k, 2)])
        out['pockets_after_len_skin'] = sk
        out['probes'] = pr
        out['all_probes_ok'] = all(all(v.values()) for v in pr.values()) and out['void_shells_left'] == 0 and \
            all(abs(s[0] - 1.6) < 0.01 and s[1] > 0.45 for s in sk)
        reg = None
        for (x, y) in PI_HOLES:
            r_ = X.wcyl_z(XC + x, y, 3.6, 7.0, 8.2); reg = r_ if reg is None else X.union(reg, r_)
        seats = tb_copy(X, F); inter(X, seats, reg)
        out['seats_x_pi_mm3'] = vol_x(X, seats, tb_copy(X, 'PI5_F'))
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        out['split'] = [b.name for b in X.comp.bRepBodies if ' (' in b.name and b.name.startswith('HOUSING')]
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d5b_front_small', 'run', out)
    print(json.dumps(out, separators=(',', ':')))
