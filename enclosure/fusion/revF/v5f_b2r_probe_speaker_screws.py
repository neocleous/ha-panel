# rev F block 2r (2026-11-03), read-only (run with readOnly true): speaker-screw fit and tool access, found at the
# checkpoint-2 review. DIN912 M3 heads (D5.5 x 3) behind the flange at y -6.0..-3.0 on the four frame holes
# (XC +-(70.5 +- 17.75), z 28 +- 17.75), and a straight D3.0 key path from each head back to the back partition (y -51.6),
# each intersected with HOUSING_E / DOOR_F (TemporaryBRep); free straight run behind the outer heads (centre + 4 points
# at r 1.5, 0.5 steps).
# Result 2026-11-03 (both sides alike): lower-outer heads (x_rel +-88.25, z 10.25) 37.97 mm3 inside the FL/FR door bosses
# (boss axis 2.24 from the head axis in plan), free run 0; upper-outer (z 45.75) heads clear, free run 27.5 to the side
# wall; inboard heads (x_rel +-52.75) and their paths 0 mm3 (45.6 free).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback


def run(_context):
    X = Ctx(); out = {}
    try:
        B = adsk.fusion.BooleanTypes
        hb = X.body('HOUSING_E')

        def vol(tool, body):
            t = X.tbm.copy(tool)
            X.tbm.booleanOperation(t, X.tbm.copy(body), B.IntersectionBooleanType)
            return round(t.volume * 1000, 2)
        for s in (1, -1):
            for dx in (17.75, -17.75):
                for dz in (17.75, -17.75):
                    x = XC + s * (70.5 + dx); z = 28.0 + dz
                    head = X.tbm.createCylinderOrCone(Dw(x, -6.0, z), 0.275, Dw(x, -3.0, z), 0.275)
                    path = X.tbm.createCylinderOrCone(Dw(x, -51.6, z), 0.15, Dw(x, -6.0, z), 0.15)
                    k = '%s x_rel %.2f z %.2f' % ('+x' if s > 0 else '-x', s * (70.5 + dx), z)
                    rec = {'head_vs_housing_mm3': vol(head, hb), 'path_vs_housing_mm3': vol(path, hb), 'head_vs_door': vol(head, X.body('DOOR_F'))}
                    if dx > 0:
                        hit = None
                        for i in range(92):
                            y = -6.0 - 0.5 * i
                            if any(X.inside(hb, px, y, pz) for (px, pz) in ((x, z), (x + 1.5, z), (x - 1.5, z), (x, z + 1.5), (x, z - 1.5))):
                                hit = y; break
                        rec['free_run_mm'] = None if hit is None else round(-6.0 - hit, 1)
                    out[k] = rec
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    print(json.dumps(out))
