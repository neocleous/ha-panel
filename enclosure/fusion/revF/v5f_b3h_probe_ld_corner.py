# rev F block 3h (2026-11-04), read-only: the viewer's-right front corner (−x) at z 115 / 127.5 / 140 for the LD2410C cradle
# (brief: z 115–140, antenna face parallel to the corner surface ≈ 40° from +y toward −x, 2.5 wall + ≥ 2 air).
#   Rays in plan from an interior point (x_rel −60, y −25) at angles θ from +y toward −x (0…150°, 10° steps): first and last
#   HOUSING_F_front hits (inner / outer surface), the outward normal at the inner hit (angle from +y toward −x), wall along
#   the ray. Also the slab's −x edge and the LCD bodies' extents near that corner.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback


def run(_context):
    X = Ctx(); out = {}
    try:
        fb = X.body('HOUSING_F_front'); comp = X.comp
        res = {}
        for z in (115.0, 127.5, 140.0):
            o = Dw(XC - 60.0, -25.0, z); rows = []
            for th in range(0, 151, 10):
                a = math.radians(th); dx, dy = -math.sin(a), math.cos(a)
                d = V3(dx / 10, (dy * C) / 10, (-dy * S) / 10); d.normalize()
                hp = adsk.core.ObjectCollection.create()
                fs = comp.findBRepUsingRay(o, d, adsk.fusion.BRepEntityTypes.BRepFaceEntityType, -1.0, True, hp)
                hits = []
                for i in range(fs.count):
                    f = fs.item(i)
                    if f.body.name != 'HOUSING_F_front':
                        continue
                    p = hp.item(i)
                    hits.append((math.hypot(p.x - o.x, math.hypot(p.y - o.y, p.z - o.z)), f, p))
                if not hits:
                    rows.append([th, None]); continue
                hits.sort(key=lambda h: h[0])
                t0, f0, p0 = hits[0]; t1, f1, p1 = hits[-1] if len(hits) > 1 else hits[0]
                ok, nrm = f0.evaluator.getNormalAtPoint(p0)
                nx, ny = nrm.x, nrm.y * C - nrm.z * S      # world plan components
                if nx * dx + ny * dy < 0:                  # outward = along the ray (from the cavity into the wall)
                    nx, ny = -nx, -ny
                ang = math.degrees(math.atan2(-nx, ny))    # from +y toward -x
                rows.append([th, [round(p0.x * 10 - XC, 1), round(wy(p0), 1)], round(ang, 1), [round(p1.x * 10 - XC, 1), round(wy(p1), 1)], round((t1 - t0) * 10, 2) if len(hits) > 1 else None, len(hits)])
            res['z%g' % z] = rows
        out['rays'] = res
        sb = X.body('SLAB_frame').boundingBox
        out['slab_x_rel'] = [round(sb.minPoint.x * 10 - XC, 2), round(sb.maxPoint.x * 10 - XC, 2)]
        lcd = {}
        for b in X.comp.bRepBodies:
            if b.name.startswith('LCD_'):
                bb = b.boundingBox
                cs = [P3(x, y, z) for x in (bb.minPoint.x, bb.maxPoint.x) for y in (bb.minPoint.y, bb.maxPoint.y) for z in (bb.minPoint.z, bb.maxPoint.z)]
                lcd[b.name] = [round(min(c.x * 10 - XC for c in cs), 1), round(max(c.x * 10 - XC for c in cs), 1), round(min(wy(c) for c in cs), 1),
                               round(max(wy(c) for c in cs), 1), round(min(wz(c) for c in cs), 1), round(max(wz(c) for c in cs), 1)]
        out['lcd_world_boxes'] = lcd
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b3h_probe_ld_corner', 'probe', out)
    print(json.dumps(out))
