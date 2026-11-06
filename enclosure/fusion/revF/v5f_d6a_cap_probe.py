# rev F audit-response d6a (2026-11-06), read-only: cap package inputs (audit findings 1 (cap void), 38 (mic gasket squeeze)).
#   Writes ~/Documents/HA_panel_renders/d_data/data/d6a_probe.json: cap void shells; MIC strip envelopes; the cap's small
#   cylinders (heat-stake pins, ports) near the strips; sections through the strip pockets.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/HA_panel_renders/scripts_d/v5f_d0_sections.py')).read())   # sections()
import traceback
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d6a_probe.json')
CAP = 'HOUSING_F_cap'
MICS = ['MIC_strip_L_env', 'MIC_strip_R_env']
PL = {
    'M_x23': ('x', 23.0, (-32.0, -21.0, 175.0, 181.0), [CAP, 'HOUSING_F_front'] + MICS),
    'M_x-23': ('x', -23.0, (-32.0, -21.0, 175.0, 181.0), [CAP, 'HOUSING_F_front'] + MICS),
    'M_z177.9': ('z', 177.9, (-42.0, 42.0, -32.0, -21.0), [CAP, 'HOUSING_F_front'] + MICS),
    'M_z177.0': ('z', 177.0, (-42.0, 42.0, -32.0, -21.0), [CAP, 'HOUSING_F_front'] + MICS),
    'M_y-26.5': ('y', -26.5, (-42.0, 42.0, 174.0, 181.0), [CAP, 'HOUSING_F_front'] + MICS),
}


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        cb = X.body(CAP)
        out['cap_cm3'] = round(cb.volume, 4)
        vs = []
        for li in range(cb.lumps.count):
            L = cb.lumps.item(li)
            for si in range(L.shells.count):
                s = L.shells.item(si)
                if s.isVoid:
                    bb = s.boundingBox
                    c = P3((bb.minPoint.x + bb.maxPoint.x) / 2, (bb.minPoint.y + bb.maxPoint.y) / 2, (bb.minPoint.z + bb.maxPoint.z) / 2)
                    vs.append({'centre': [round(c.x * 10 - XC, 3), round(wy(c), 3), round(wz(c), 3)], 'faces': s.faces.count})
        out['cap_voids'] = vs
        out['mics'] = {n: {'box': [round(v, 3) for v in wbb(X, X.body(n))], 'cm3': round(X.body(n).volume, 4), 'vis': X.body(n).isLightBulbOn}
                       for n in MICS if X.body(n) is not None}
        rows = []
        for f in cb.faces:
            g = f.geometry
            if g.objectType != adsk.core.Cylinder.classType() or g.radius * 10 > 1.2:
                continue
            ax = g.axis; ax.normalize(); o = g.origin
            ts = [((v.geometry.x - o.x) * ax.x + (v.geometry.y - o.y) * ax.y + (v.geometry.z - o.z) * ax.z) * 10 for v in f.vertices] or [0.0]
            tm = (min(ts) + max(ts)) / 2; c = P3(o.x + ax.x * tm / 10, o.y + ax.y * tm / 10, o.z + ax.z * tm / 10)
            zs = [wz(v.geometry) for v in f.vertices]
            p = f.pointOnFace; ok, n = f.evaluator.getNormalAtPoint(p)
            k = (p.x - o.x) * ax.x + (p.y - o.y) * ax.y + (p.z - o.z) * ax.z
            q = P3(o.x + ax.x * k, o.y + ax.y * k, o.z + ax.z * k)
            hole = V3(p.x - q.x, p.y - q.y, p.z - q.z).dotProduct(n) < 0
            rows.append([round(2 * g.radius * 10, 3), 'hole' if hole else 'pin', [round(c.x * 10 - XC, 2), round(wy(c), 2), round(wz(c), 2)],
                         [round(min(zs), 2), round(max(zs), 2)] if zs else None])
        out['cap_small_cyl'] = rows
        out['sec'] = sections(X, PL)
        out['t_s'] = round(time.time() - t0, 1)
        os.makedirs(os.path.dirname(OUTF), exist_ok=True)
        json.dump(out, open(OUTF, 'w'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    short = {k: v for k, v in out.items() if k not in ('sec',)}
    log('v5f_d6a_cap_probe', 'probe', short)
    print(json.dumps(short, separators=(',', ':')))
