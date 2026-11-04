# rev F block 3j (2026-11-04), read-only: what a radar near the viewer's-right front corner would look through.
#   B3i stopped: a 16-wide board with its antenna normal at the brief's 40° cannot sit in the corner with 2.0 air (the inner
#   corner between the slot face and the side wall is acute, ≈ 72°, and the side wall curves inboard behind it).
#   Rays in plan at z 127.5 from three points 2.5 inside the inner surface near the corner, at 0…150° from +y toward −x:
#   the ordered bodies hit (housing wall, SLAB_frame = printed, LCD_* = panel/glass/PCB) and the distances.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
PTS = {'corner': (-86.5, -14.5), 'side_front': (-84.5, -19.5), 'side_mid': (-80.0, -28.0)}


def run(_context):
    X = Ctx(); out = {}
    comp = X.comp
    try:
        for k, (xr, y) in PTS.items():
            o = Dw(XC + xr, y, 127.5); rows = []
            for th in range(0, 151, 15):
                a = math.radians(th); dx, dy = -math.sin(a), math.cos(a)
                d = V3(dx, dy * C, -dy * S); d.normalize()
                hp = adsk.core.ObjectCollection.create()
                fs = comp.findBRepUsingRay(o, d, adsk.fusion.BRepEntityTypes.BRepFaceEntityType, -1.0, False, hp)
                hits = []
                for i in range(fs.count):
                    nm = fs.item(i).body.name
                    if nm in ('HOUSING_F_front', 'SLAB_frame') or nm.startswith('LCD_'):
                        p = hp.item(i)
                        hits.append((round(math.sqrt((p.x - o.x) ** 2 + (p.y - o.y) ** 2 + (p.z - o.z) ** 2) * 10, 1), nm.replace('HOUSING_F_front', 'H').replace('SLAB_frame', 'SLAB')))
                hits.sort()
                rows.append([th, hits[:6]])
            out[k] = {'pt': [xr, y, 127.5], 'inside_front': X.inside(X.body('HOUSING_F_front'), XC + xr, y, 127.5), 'rays': rows}
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b3j_probe_ld_view', 'rays', out)
    print(json.dumps(out))
