# rev F block 4e (2026-11-04), read-only: tight world bounding boxes for the block-4 layout.
#   A copy of each body is rotated +12° about x and lifted by H (design → world), so its bounding box is world-aligned and
#   tight (design boxes transformed corner by corner are inflated). x is reported as x_rel = x − XC.
#   1. Every interior body, envelope and keep-out (LCD_*, SLAB_frame, PI5_*, KO_*, GPIO_*, PD_*, MAIN_*, CRADLE_*, SPK*,
#      TOUCH_*, LD2410C_env_F, MIC_*, VEML_*).
#   2. PI5_F near the CAM/DISP connectors (envelope sheet: board X 48.6 / 54.4, Y 0.5–16 → x_rel ≈ 6 / 12, y −57.5…−42):
#      lumps of PI5_F ∩ (x_rel −2…20, y −63…−36, z 9.3…24) with their world boxes; the same for PI5_F_cooler.
#   3. The 5807 holes: the envelope sheet puts them 2.54 from the RECEPTACLE edge (Eagle (2.413 / 17.653, 20.955), USB-C
#      edge Y 23.495) – b4c/b4d used the opposite edge. PD_5807_env lumps for the PCB / receptacle split.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
PREF = ('LCD_', 'SLAB_frame', 'PI5_F', 'KO_', 'GPIO_', 'PD_', 'MAIN_', 'CRADLE_', 'SPK', 'TOUCH_', 'LD2410C_env_F', 'MIC_', 'VEML_',
        'HOUSING_F_door', 'FOOT_')


def run(_context):
    X = Ctx(); out = {}
    tbm = X.tbm; B = adsk.fusion.BooleanTypes
    M = adsk.core.Matrix3D.create()
    M.setCell(1, 1, C); M.setCell(1, 2, -S); M.setCell(2, 1, S); M.setCell(2, 2, C); M.setCell(2, 3, H / 10)

    def wbb_tb(t):
        tbm.transform(t, M); bb = t.boundingBox
        return [round(bb.minPoint.x * 10 - XC, 2), round(bb.maxPoint.x * 10 - XC, 2), round(bb.minPoint.y * 10, 2),
                round(bb.maxPoint.y * 10, 2), round(bb.minPoint.z * 10, 2), round(bb.maxPoint.z * 10, 2)]

    def lumps_w(t):
        tbm.transform(t, M); res = []
        for lp in t.lumps:
            bb = lp.boundingBox
            res.append([round(bb.minPoint.x * 10 - XC, 2), round(bb.maxPoint.x * 10 - XC, 2), round(bb.minPoint.y * 10, 2),
                        round(bb.maxPoint.y * 10, 2), round(bb.minPoint.z * 10, 2), round(bb.maxPoint.z * 10, 2)])
        return sorted(res)
    try:
        boxes = {}
        for b in X.comp.bRepBodies:
            if b.name.startswith(PREF) and not b.name.endswith(('_b1', '_b2', '_revE')):
                boxes[b.name] = wbb_tb(tbm.copy(b)) + [b.isLightBulbOn]
        out['boxes'] = boxes
        log('v5f_b4e_probe_world_boxes', 'boxes', out)
        reg = X.wbox(XC - 2.0, XC + 20.0, -63.0, -36.0, 9.3, 24.0)
        for n in ('PI5_F', 'PI5_F_cooler', 'PD_5807_env'):
            t = tbm.copy(X.body(n))
            r = tbm.copy(reg) if n != 'PD_5807_env' else X.wbox(XC - 15, XC + 15, -90, -55, 0, 30)
            tbm.booleanOperation(t, r, B.IntersectionBooleanType)
            out['lumps_' + n] = lumps_w(t)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b4e_probe_world_boxes', 'probe', {k: v for k, v in out.items() if k != 'boxes'})
    print(json.dumps({k: v for k, v in out.items() if k != 'boxes'}))
