# rev F block 2d (2026-11-03): speaker-chamber walls (K5/K6/K8 as amended 2026-11-03 22:35).
# Side partitions 1.5: +x x_rel 45.4..46.9 (after the Pi move), -x x_rel -45.3..-46.8. Back partitions 1.5 at
# y -51.6..-53.1 (behind the middle door boss and its pad, which reaches y -51.13), partition to side wall. Ceilings 2.0 at
# z 74.0..76.0 (top <= 76.3: the lower K5 lanes now start at z 79.7). Partition / back-partition bottoms at z 3.7 = door
# top 2.5 + 2 mm CR foam compressed to 1.2. All as world boxes ∩ INNER_E, NEW body, interference, combine JOIN.
# Also: ring narrowing (u 5.6, v5f_b2b) extended to y -53.1 so the door-edge foam runs under the back partition; Ø5
# speaker-wire holes through the back partitions at x_rel ±75, z 18 (sealed after assembly).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
PX = {1: (45.4, 46.9), -1: (45.3, 46.8)}
YB0, YB1, ZB, ZC0, ZC1 = -51.6, -53.1, 3.7, 74.0, 76.0


def run(_context):
    X = Ctx()
    out = {}
    try:
        hb = X.body('HOUSING_E'); inner = X.body('INNER_E')
        # 1. ring narrowing extension
        band = X.tbm.copy(X.body('TOOL_ring_opening_5p6')); X.diff(band, X.tbm.copy(X.body('TOOL_ring_opening_6p5')))
        reg = X.wbox(XC + 45.3, XC + 130, YB1, -51.5, -2, 3); X.union(reg, X.wbox(XC - 130, XC - 45.3, YB1, -51.5, -2, 3))
        X.tbm.booleanOperation(band, reg, adsk.fusion.BooleanTypes.IntersectionBooleanType)
        if band.volume > 1e-6:
            X.combine(hb, [X.add(band, 'RING_narrow2_tmp')], op=CUT)
        hb = X.body('HOUSING_E')
        out['housing_after_ring_ext'] = round(hb.volume, 3)
        # 2. walls
        tb = None
        for s in (1, -1):
            a, b = PX[s]
            xs = sorted((XC + s * a, XC + s * b)); xo = sorted((XC + s * a, XC + s * 130))
            parts = [X.wbox(xs[0], xs[1], YB1, 12, ZB, ZC1),                   # side partition
                     X.wbox(xo[0], xo[1], YB1, YB0, ZB, ZC1),                  # back partition
                     X.wbox(xo[0], xo[1], YB1, 12, ZC0, ZC1)]                  # ceiling
            for p in parts:
                tb = p if tb is None else X.union(tb, p)
        X.tbm.booleanOperation(tb, X.tbm.copy(inner), adsk.fusion.BooleanTypes.IntersectionBooleanType)
        walls = X.add(tb, 'CHAMBER_walls_tmp')
        out['walls_cm3'] = round(walls.volume, 3)
        names = [b.name for b in X.comp.bRepBodies]
        others = [X.body(n) for n in names if n.startswith('LCD_')] + [X.body(n) for n in ('SLAB_frame', 'DOOR_F', 'PI5_F', 'PI5_F_cooler', 'GPIO_plugA_env', 'GPIO_plugB_env', 'KO_K7_fan')]
        r = X.interference(walls, others)
        out['walls_interf_nonzero'] = {k: v for k, v in r.items() if v > 0} or 'all 0 (%d)' % len(r)
        if any(v > 0 for v in r.values()):
            walls.isLightBulbOn = False
            raise RuntimeError('wall interference %s' % out['walls_interf_nonzero'])
        v0 = hb.volume
        X.combine(hb, [walls])
        hb = X.body('HOUSING_E')
        # 3. wire holes along y through the back partitions
        wh = None
        for s in (1, -1):
            c = X.tbm.createCylinderOrCone(Dw(XC + s * 75, YB0 + 1.0, 18), 0.25, Dw(XC + s * 75, YB1 - 1.0, 18), 0.25)
            wh = c if wh is None else X.union(wh, c)
        X.combine(hb, [X.add(wh, 'WIREHOLE_tmp')], op=CUT)
        hb = X.body('HOUSING_E')
        out['housing_cm3'] = (round(v0, 3), round(hb.volume, 3))
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]

        def segs(b, p, d, t0, t1, step=0.05):
            res = []; cur = None; n = int(round((t1 - t0) / step))
            for i in range(n + 1):
                t = t0 + i * step
                ins = X.inside(b, p[0] + d[0] * t, p[1] + d[1] * t, p[2] + d[2] * t)
                if ins and cur is None: cur = t
                if not ins and cur is not None: res.append((round(cur, 2), round(t - step, 2))); cur = None
            if cur is not None: res.append((round(cur, 2), round(t1, 2)))
            return res
        pr = {}
        for s in (1, -1):
            k = '+x' if s > 0 else '-x'
            pr[k] = {'partition_x_y-20_z30': segs(hb, (XC + s * 44.0, -20, 30), (s, 0, 0), 0, 4),
                     'back_y_x70_z30': segs(hb, (XC + s * 70, -50.0, 30), (0, -1, 0), 0, 4.5),
                     'ceiling_z_x70_y-20': segs(hb, (XC + s * 70, -20, 72.0), (0, 0, 1), 0, 5),
                     'partition_bottom_z_y-20': segs(hb, (XC + s * 46.0, -20, 2.0), (0, 0, 1), 0, 3),
                     'wirehole_open': not X.inside(hb, XC + s * 75, -52.35, 18) and X.inside(hb, XC + s * 75, -52.35, 21)}
        out['probes'] = pr
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b2d_partitions_ceilings', 'chamber walls', out)
    print(json.dumps(out))
