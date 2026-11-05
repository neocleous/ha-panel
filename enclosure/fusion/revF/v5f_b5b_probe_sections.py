# rev F block 5b (2026-11-05), read-only: occupancy sections for the fabric details (D1/D2).
#   '#' front shell, 'D' door, 'T' TOUCH_PCB, 'B' speaker box, 'o' other listed part, '.' air (REF_F_outer inside), ' ' outside.
#   S1 chin top at x_rel 0 and 70 (y −2…10, z 42…56, 0.25 × 0.5); S2 top at x_rel 60 (y −40…−10?) – per-row ranges below;
#   S3 back top at x_rel 0 (y −52…−38, z 160…181); S4 bottom joint at x_rel 0 (y −87…−78, z −0.5…8, 0.25 × 0.25).
#   Also: body list (HOUSING_F_*, REF/INNER, TOOL_*), floor underside faces (planar z≈0 and cylinders reaching z 0.5).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
SECT = [
    ('S1_chin_x0', 0.0, (-2.0, 10.0, 0.25), (42.0, 56.0, 0.5)),
    ('S1_chin_x70', 70.0, (-2.0, 10.0, 0.25), (42.0, 56.0, 0.5)),
    ('S3_back_top_x0', 0.0, (-52.0, -38.0, 0.5), (160.0, 181.0, 0.5)),
    ('S4_bottom_joint_x0', 0.0, (-87.0, -78.0, 0.25), (-0.5, 8.0, 0.25)),
]
OTH = ['SPKBOX_L', 'SPKBOX_R', 'SLAB_frame', 'LCD_glass', 'CRADLE_5807', 'PD_5807_env', 'VEML_env', 'RESP_CARRIER']


def run(_context):
    X = Ctx(); out = {}
    try:
        out['bodies'] = [(b.name, round(b.volume, 3), b.isLightBulbOn) for b in X.comp.bRepBodies
                         if b.name.startswith(('HOUSING_F', 'REF_', 'INNER_', 'TOOL_'))]
        fb = X.body('HOUSING_F_front'); db = X.body('HOUSING_F_door'); tp = X.body('TOUCH_PCB'); ref = X.body('REF_F_outer')
        oth = [X.body(n) for n in OTH if X.body(n) is not None]
        sec = {}
        for (nm, xr, (y0, y1, ys), (z0, z1, zs)) in SECT:
            rows = []
            z = z1
            while z >= z0 - 1e-9:
                r = ''
                y = y0
                while y <= y1 + 1e-9:
                    p = Dw(XC + xr, y, z)
                    if fb.pointContainment(p) in INS: ch = '#'
                    elif db.pointContainment(p) in INS: ch = 'D'
                    elif tp.pointContainment(p) in INS: ch = 'T'
                    elif any(o.pointContainment(p) in INS for o in oth): ch = 'o'
                    elif ref.pointContainment(p) in INS: ch = '.'
                    else: ch = ' '
                    r += ch; y += ys
                rows.append('%6.2f %s' % (z, r))
                z -= zs
            sec[nm] = rows
        out['sections'] = sec
        fl = []
        for f in fb.faces:
            bb = f.boundingBox
            zmin = wz(bb.minPoint); zmax = wz(bb.maxPoint)
            g = f.geometry.objectType.split('::')[-1]
            if g == 'Plane':
                ok, n = f.evaluator.getNormalAtPoint(f.pointOnFace)
                nz = n.y * S + n.z * C
                if nz < -0.99 and wz(f.pointOnFace) < 1.0:
                    fl.append(['P', round(f.area * 100, 1), round(wz(f.pointOnFace), 2), [round(wy(bb.minPoint), 1), round(wy(bb.maxPoint), 1)],
                               [round(bb.minPoint.x * 10 - XC, 1), round(bb.maxPoint.x * 10 - XC, 1)]])
        out['floor_down_faces'] = sorted(fl, key=lambda r: -r[1])[:30]
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b5b_probe_sections', 'probe', out)
    txt = []
    for b in out.get('bodies', []):
        txt.append('BODY %s %s %s' % b)
    for k, rows in out.get('sections', {}).items():
        txt.append('== ' + k)
        txt.extend(rows)
    for r in out.get('floor_down_faces', []):
        txt.append('FLOOR %s' % r)
    if 'FAIL' in out:
        txt.append('FAIL %s' % out['FAIL'])
    print('\n'.join(txt))
