# rev F block 4k (2026-11-04), read-only: wall geometry for the BME680 spot and the exhaust slots.
#   1. −x side wall above the −x speaker box: rays from (x_rel −40, y, z) toward −x for y −25…−55, z 80…110 → first front-shell
#      hit (inner surface x), wall thickness along the ray, face normal (world).
#   2. Back wall above the door joint: rays from (x_rel, −30, z) toward −y for x_rel −40…40, z 160…178 → inner / outer y and
#      which body is hit (front shell or door).
#   3. The lip and magnet pads near the −x back: rays toward −x at y −54…−62, z 80…110.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback


def run(_context):
    X = Ctx(); out = {}
    comp = X.comp

    def hits(o_w, d_w, names):
        o = Dw(*o_w); d = V3(d_w[0], d_w[1] * C + d_w[2] * S, -d_w[1] * S + d_w[2] * C); d.normalize()
        hp = adsk.core.ObjectCollection.create()
        fs = comp.findBRepUsingRay(o, d, adsk.fusion.BRepEntityTypes.BRepFaceEntityType, -1.0, False, hp)
        res = []
        for i in range(fs.count):
            f = fs.item(i)
            if f.body.name in names:
                p = hp.item(i); t = math.sqrt((p.x - o.x) ** 2 + (p.y - o.y) ** 2 + (p.z - o.z) ** 2) * 10
                ok, n = f.evaluator.getNormalAtPoint(p)
                nw = (round(n.x, 2), round(n.y * C - n.z * S, 2), round(n.y * S + n.z * C, 2))
                res.append([round(t, 2), f.body.name[-5:], round(p.x * 10 - XC, 2), round(wy(p), 2), round(wz(p), 2), nw])
        return sorted(res)[:3]
    try:
        sh = ('HOUSING_F_front', 'HOUSING_F_door')
        side = {}
        for y in (-25, -30, -35, -40, -45, -50, -55, -58, -62):
            for z in (80, 85, 90, 95, 100, 105, 110):
                h = hits((XC - 40.0, y, z), (-1, 0, 0), sh)
                side['y%d_z%d' % (y, z)] = [[r[0] + 40.0 if False else r[2], r[1], r[5]] for r in h[:2]]
        out['side_mx_inner_x_body_normal'] = side
        back = {}
        for xr in (-40, -30, -20, 0, 20, 30, 40):
            for z in (160, 163, 166, 168, 170, 172, 174, 176, 178):
                h = hits((XC + xr, -30.0, z), (0, -1, 0), sh)
                back['x%d_z%d' % (xr, z)] = [[r[3], r[1], r[5]] for r in h[:2]]
        out['back_y_body_normal'] = back
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b4k_probe_walls', 'probe', out)
    print(json.dumps({'n_side': len(out.get('side_mx_inner_x_body_normal', {})), 'n_back': len(out.get('back_y_body_normal', {})), 'FAIL': out.get('FAIL')}))
