# rev F d9b (2026-11-06), read-only: the polylines of the leads near the BME680 cup and behind the right box (sphere / plane
#   faces of each lead tube = its joints and ends), and SPKBOX_R's small holes. Prints the result and logs it.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
LEADS = ['LEAD_BME680', 'LEAD_RADAR', 'LEAD_SPK_R', 'LEAD_VEML']


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        for n in LEADS:
            b = X.body(n)
            if b is None:
                out[n] = None; continue
            pts = []
            for f in b.faces:
                tn = f.geometry.objectType.split('::')[-1]
                if tn in ('Sphere', 'Plane'):
                    c = f.geometry.origin if tn == 'Sphere' else f.centroid
                    pts.append([tn[0], round(c.x * 10 - XC, 2), round(wy(c), 2), round(wz(c), 2),
                                round((f.geometry.radius * 10) if tn == 'Sphere' else 0.0, 2)])
            out[n] = pts
        holes = []
        sb = X.body('SPKBOX_R')
        for f in sb.faces:
            g = f.geometry
            if g.objectType != adsk.core.Cylinder.classType() or g.radius * 10 > 2.0:
                continue
            c = f.centroid
            ax = g.axis
            holes.append([round(2 * g.radius * 10, 2), [round(c.x * 10 - XC, 2), round(wy(c), 2), round(wz(c), 2)],
                          [round(v, 2) for v in nw_of(ax)]])
        out['spkbox_r_small_cyl'] = holes
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d9b_lead_probe', 'probe', out)
    print(json.dumps(out, separators=(',', ':')))
