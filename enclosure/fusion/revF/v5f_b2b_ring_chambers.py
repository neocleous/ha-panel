# rev F block 2b (2026-11-03): floor ring narrowed from 6.5 to 5.6 along both speaker chambers' outer walls (Daniel 22:35:
# decision 1 option 1 + decision 2 option 1, built as one ring change; the door stays as built at inset 6.8).
# Gives the 1.2 mm door gap for the 2 mm CR foam on the door edge, and the DMA45-4 frame (x_rel 47.5..93.5) a passage
# between the partition (46.8) and the ring opening (~94.1). Region per side: |x_rel| >= 45.3 (partition cavity face),
# y >= -51.5 (back partition back face). Tool = (outline OFF 5.6, z -1..2.6) - TOOL_ring_opening_6p5, cut to z 2.6 so the
# cove between u 5.6 and 6.0 (z <= 2.523) goes too and no sliver remains. TOOL_ring_opening_5p6 kept hidden.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
XP, YB = 45.3, -51.5


def run(_context):
    X = Ctx()
    out = {}
    try:
        hb = X.body('HOUSING_E'); door = X.body('DOOR_F'); o65 = X.body('TOOL_ring_opening_6p5')
        o56, YC, rc = outline_body(X, 5.6, -1.0, 2.6, 'TOOL_ring_opening_5p6')
        o56.isLightBulbOn = False
        band = X.tbm.copy(o56); X.diff(band, X.tbm.copy(o65))
        reg = X.wbox(XC + XP, XC + 130, YB, 30, -2, 3)
        X.union(reg, X.wbox(XC - 130, XC - XP, YB, 30, -2, 3))
        X.tbm.booleanOperation(band, reg, adsk.fusion.BooleanTypes.IntersectionBooleanType)
        cut = X.add(band, 'RING_narrow_tmp')
        out['tool_cm3'] = round(cut.volume, 4)
        v0 = hb.volume
        X.combine(hb, [cut], op=CUT)
        hb = X.body('HOUSING_E')
        out['housing_cm3'] = (round(v0, 3), round(hb.volume, 3))
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name == 'RING_narrow_tmp']

        def segs(b, p, d, t0, t1, step=0.05):               # solid intervals along a ray
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
            pr[k] = {
                'x_rel_y-4.5_z1.25': segs(hb, (XC + s * 85, -4.5, 1.25), (s, 0, 0), 0, 14),
                'x_rel_y-30_z1.25': segs(hb, (XC + s * 80, -30, 1.25), (s, 0, 0), 0, 17),
                'x_rel_y-60_z1.25_unchanged': segs(hb, (XC + s * 65, -60, 1.25), (s, 0, 0), 0, 17),
                'y_chin_x70.5_z1.25': segs(hb, (XC + s * 70.5, -2, 1.25), (0, 1, 0), 0, 10),
                'y_chin_x30_z1.25_unchanged': segs(hb, (XC + s * 30, -2, 1.25), (0, 1, 0), 0, 10),
                'door_y_x70.5': segs(door, (XC + s * 70.5, -3, 1.25), (0, 1, 0), 0, 5),
                'door_x_y-30': segs(door, (XC + s * 85, -30, 1.25), (s, 0, 0), 0, 6)}
        out['probes_intervals'] = pr
        sec = {}
        for z in (0.5, 1.25, 2.0, 2.45, 2.55, 3.0, 4.0):
            sec[z] = segs(hb, (XC + 87, -30, z), (1, 0, 0), 0, 10)
        out['side_y-30_x_rel_solid_by_z_from87'] = sec
        out['interf'] = X.interference(door, [hb])
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b2b_ring_chambers', 'ring 5.6 along chambers', out)
    print(json.dumps(out))
