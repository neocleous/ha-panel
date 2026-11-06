# rev F d10a (2026-11-06), read-only: the lip's rear end (audit finding 4, Daniel's decision 2 a: square end faces).
#   Writes ~/Documents/HA_panel_renders/d_data/data/d10a_probe.json: the front's faces in the end plane y -63.5 (outline,
#   area), sections through the lip at x stations (y-z planes) and at z stations, front and door.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/HA_panel_renders/scripts_d/v5f_d0_sections.py')).read())   # sections()
import traceback
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d10a_probe.json')
FR = 'HOUSING_F_front'


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        fb = X.body(FR)
        ends = []
        for f in fb.faces:
            g = f.geometry
            if g.objectType != adsk.core.Plane.classType():
                continue
            c = f.centroid
            if abs(wy(c) + 63.5) > 0.05:
                continue
            n = nw_of(g.normal)
            if abs(abs(n[1]) - 1.0) > 0.01:
                continue
            bb = f.boundingBox
            lo = (bb.minPoint.x * 10 - XC, wz(bb.minPoint)); hi = (bb.maxPoint.x * 10 - XC, wz(bb.maxPoint))
            pts = []
            for lp in f.loops:
                for e in lp.edges:
                    ev = e.evaluator; ok, a, b = ev.getParameterExtents(); ok, ps = ev.getStrokes(a, b, 0.002)
                    pts.append([[round(p.x * 10 - XC, 2), round(wz(p), 2)] for p in ps])
            ends.append({'area_mm2': round(f.area * 100, 2), 'x': [round(min(lo[0], hi[0]), 2), round(max(lo[0], hi[0]), 2)],
                         'z': [round(min(lo[1], hi[1]), 2), round(max(lo[1], hi[1]), 2)], 'edges': pts})
        out['end_faces'] = ends
        NB = [FR, 'HOUSING_F_door', 'INNER_E']
        PL = {}
        for xs in (0.0, 12.0, 24.0, 36.0, 44.0, 52.0, 60.0):
            PL['L_x%g' % xs] = ('x', xs, (-70.0, -50.0, 60.0, 145.0), NB)
        for zs in (60.0, 90.0, 110.0, 125.0):
            PL['L_z%g' % zs] = ('z', zs, (-90.0, 90.0, -70.0, -50.0), NB)
        out['sec'] = sections(X, PL)
        out['t_s'] = round(time.time() - t0, 1)
        os.makedirs(os.path.dirname(OUTF), exist_ok=True)
        json.dump(out, open(OUTF, 'w'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d10a_lip_probe', 'probe', {'n_end_faces': len(out.get('end_faces', [])), 't_s': out.get('t_s'), 'FAIL': out.get('FAIL')})
    print(json.dumps({'n_end_faces': len(out.get('end_faces', [])), 't_s': out.get('t_s'), 'FAIL': out.get('FAIL'),
                      'areas': [e['area_mm2'] for e in out.get('end_faces', [])]}, separators=(',', ':')))
