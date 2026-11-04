# rev F block 4a (2026-11-04), read-only: interior state for block 4 (electronics mounts and cables).
#   1. World boxes (x_rel, y, z) of the placed components and keep-outs.
#   2. The cavity at the rear opening y −55.3 (door front edge): inner half-width at z 10…150 (rays from x_rel 0 along ±x).
#   3. The door's inner back wall: y of the first door hit along −y from (x_rel, −56, z) for x_rel −40…40, z 10…150.
#   4. The front shell's floor top and the door's lower inner edge near the main-board candidate (rays along −z / −y).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
NAMES = ['PI5_F', 'PI5_F_cooler', 'KO_K7_fan', 'GPIO_plugA_env', 'GPIO_plugB_env', 'PD_5807_env', 'KO_5807_pigtail', 'KO_K5_LL', 'KO_K5_LR',
         'KO_K5_UL', 'KO_K5_UR', 'SPKBOX_L', 'SPKBOX_R', 'HOUSING_F_door', 'TOUCH_PCB', 'KO_touch_back', 'LD2410C_env_F', 'VEML_env',
         'MIC_strip_L_env', 'MIC_strip_R_env', 'SPK_L', 'SPK_R']


def run(_context):
    X = Ctx(); out = {}
    comp = X.comp

    def bbw(bb):
        mn, mx = bb.minPoint, bb.maxPoint
        cs = [P3(x, y, z) for x in (mn.x, mx.x) for y in (mn.y, mx.y) for z in (mn.z, mx.z)]
        return [round(min(c.x * 10 - XC for c in cs), 1), round(max(c.x * 10 - XC for c in cs), 1), round(min(wy(c) for c in cs), 1),
                round(max(wy(c) for c in cs), 1), round(min(wz(c) for c in cs), 1), round(max(wz(c) for c in cs), 1)]

    def first_hit(o_w, d_w, bodies):
        o = Dw(*o_w); d = V3(d_w[0], d_w[1] * C + d_w[2] * S, -d_w[1] * S + d_w[2] * C); d.normalize()
        hp = adsk.core.ObjectCollection.create()
        fs = comp.findBRepUsingRay(o, d, adsk.fusion.BRepEntityTypes.BRepFaceEntityType, -1.0, False, hp)
        best = None
        for i in range(fs.count):
            if fs.item(i).body.name in bodies:
                p = hp.item(i); t = math.sqrt((p.x - o.x) ** 2 + (p.y - o.y) ** 2 + (p.z - o.z) ** 2) * 10
                if best is None or t < best[0]:
                    best = (t, p, fs.item(i).body.name)
        return best
    try:
        out['boxes'] = {n: bbw(X.body(n).boundingBox) for n in NAMES if X.body(n) is not None}
        out['missing'] = [n for n in NAMES if X.body(n) is None]
        shells = ('HOUSING_F_front', 'HOUSING_F_door')
        op = {}
        for z in (10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150):
            r = []
            for sx in (1, -1):
                h = first_hit((XC, -55.3, z), (sx, 0, 0), shells)
                r.append(None if h is None else round(h[1].x * 10 - XC, 1))
            op['z%d' % z] = r
        out['opening_y-55.3_inner_x_rel'] = op
        bw = {}
        for xr in (-40, -30, -20, -10, 0, 10, 20, 30, 40):
            row = []
            for z in (10, 20, 35, 50, 65, 84, 100, 120, 140):
                h = first_hit((XC + xr, -56.0, z), (0, -1, 0), shells)
                row.append(None if h is None else [z, round(wy(h[1]), 1), h[2][-4:]])
            bw['x%d' % xr] = row
        out['back_wall_y'] = bw
        fl = {}
        for xr in (-45, -41.5, -30, 0, 30, 41.5, 45):
            row = []
            for y in (-60, -65, -70, -75):
                h = first_hit((XC + xr, y, 30.0), (0, 0, -1), shells + ('PD_5807_env',))
                row.append(None if h is None else [y, round(wz(h[1]), 2), h[2][-6:]])
            fl['x%g' % xr] = row
        out['floor_top_z'] = fl
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b4a_probe_interior', 'probe', out)
    print(json.dumps(out))
