# rev F d21b (2026-11-07), read-only: B-rep faces for the print-audit fixes F8 / F10 / F14 (report-print-audit-2026-11-07).
#   F8: the front's four cap pads (lobes r 5.5 round the screw axes, tops z 172.5) and the cap's four bosses (Ø8, ends z 172.5);
#   F10: the door's USB-C cutout top (z 27.9); F14: the LD2410C pocket roof (z 138.65). For every face within ZONE: type,
#   world normal, area, world bbox and, for cylinders, axis point / direction / radius. Writes d_data/data/d21b_faces.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py'), encoding='utf-8').read())
import traceback
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d21b_faces.json')
ZONES = {                                                     # name: (body, world box x_rel / y / z)
    'pad_SR': ('HOUSING_F_front', [-50.0, -36.5, -40.0, -25.5, 169.0, 173.0]),
    'pad_BR': ('HOUSING_F_front', [-32.5, -19.5, -45.0, -30.5, 169.0, 173.0]),
    'boss_SR': ('HOUSING_F_cap', [-48.5, -38.0, -38.0, -27.5, 172.0, 174.0]),
    'boss_BR': ('HOUSING_F_cap', [-31.0, -20.5, -43.0, -32.5, 172.0, 174.0]),
    'cutout_top': ('HOUSING_F_door', [-13.0, 13.0, -86.0, -79.0, 27.0, 28.5]),
    'pocket_roof': ('HOUSING_F_front', [-80.0, -60.0, -34.0, -12.0, 137.5, 139.5]),
}


def wn(v):                                                    # design vector -> world
    return (v.x, v.y * C - v.z * S, v.y * S + v.z * C)


def wp(p):
    return (p.x * 10 - XC, wy(p), wz(p))


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        for zn, (bn, bb) in ZONES.items():
            b = X.body(bn); res = []
            for f in b.faces:
                fb = f.boundingBox
                cs = [wp(P3(x_, y_, z_)) for x_ in (fb.minPoint.x, fb.maxPoint.x) for y_ in (fb.minPoint.y, fb.maxPoint.y)
                      for z_ in (fb.minPoint.z, fb.maxPoint.z)]
                fbb = [min(c[0] for c in cs), max(c[0] for c in cs), min(c[1] for c in cs), max(c[1] for c in cs),
                       min(c[2] for c in cs), max(c[2] for c in cs)]
                if fbb[0] > bb[1] or fbb[1] < bb[0] or fbb[2] > bb[3] or fbb[3] < bb[2] or fbb[4] > bb[5] or fbb[5] < bb[4]:
                    continue
                g = f.geometry; e = {'type': g.objectType.split('::')[-1], 'area_mm2': round(f.area * 100, 2)}
                pt = f.pointOnFace; e['pt'] = [round(c, 3) for c in wp(pt)]
                ok, nrm = f.evaluator.getNormalAtPoint(pt)
                if ok:
                    e['n'] = [round(c, 4) for c in wn(nrm)]
                if e['type'] == 'Cylinder':
                    e['axis_pt'] = [round(c, 3) for c in wp(g.origin)]; e['axis'] = [round(c, 4) for c in wn(g.axis)]
                    e['r'] = round(g.radius * 10, 4)
                vs = []
                for L in f.loops:
                    for ed in L.edges:
                        for v in (ed.startVertex, ed.endVertex):
                            q = wp(v.geometry); vs.append(q)
                if vs:
                    e['vbb'] = [round(min(v[0] for v in vs), 3), round(max(v[0] for v in vs), 3), round(min(v[1] for v in vs), 3),
                                round(max(v[1] for v in vs), 3), round(min(v[2] for v in vs), 3), round(max(v[2] for v in vs), 3)]
                    if e['type'] == 'Plane' and len(vs) <= 40:
                        e['verts'] = sorted(set(tuple(round(c, 3) for c in v) for v in vs))
                res.append(e)
            out[zn] = res
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    json.dump(out, open(OUTF, 'w'))
    print(json.dumps({'t_s': out.get('t_s'), 'FAIL': out.get('FAIL'), 'n': {k: len(v) for k, v in out.items() if isinstance(v, list)}}))
