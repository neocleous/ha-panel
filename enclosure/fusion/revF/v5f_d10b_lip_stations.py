# rev F d10b (2026-11-06), read-only: stations along the lip's end (plane y -63.5). For each edge of the end faces, the face
#   on its other side (outer face = normal pointing away from the arch centre, toward the door; inner face = into the room).
#   Along the outer edges, every ~1 mm: point O, the outer face's normal n, the edge tangent tau, the band's direction toward
#   its end e (= +-(tau x n), e_y < 0) and delta = how far the inner face's end runs past O along e (-1.2 n_in,y / e_y).
#   Writes ~/Documents/HA_panel_renders/d_data/data/d10b_stations.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d10b_stations.json')
FR = 'HOUSING_F_front'
SP = globals().get('SPACING', 1.0)


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        fb = X.body(FR)
        endf = [f for f in fb.faces if f.geometry.objectType == adsk.core.Plane.classType() and abs(wy(f.centroid) + 63.5) < 0.05
                and abs(abs(nw_of(f.geometry.normal)[1]) - 1.0) < 0.01]
        st = []; edges = []
        for f in endf:
            for e in f.edges:
                try:
                    oth = [g for g in e.faces if g != f]
                    if not oth:
                        continue
                    g = oth[0]
                    ev = e.evaluator; ok, a, b = ev.getParameterExtents(); ok, pts = ev.getStrokes(a, b, 0.0005)
                    P_ = [(p.x * 10 - XC, wy(p), wz(p)) for p in pts]
                    Lmm = sum(math.dist(P_[i], P_[i + 1]) for i in range(len(P_) - 1))
                    pm = pts[len(pts) // 2]
                    ok, nm = g.evaluator.getNormalAtPoint(pm); nmw = nw_of(nm)
                    rad = (pm.x * 10 - XC, wz(pm))
                    outer = nmw[0] * rad[0] + nmw[2] * rad[1] > 0
                    edges.append({'len': round(Lmm, 2), 'mid': [round(rad[0], 2), round(rad[1], 2)], 'outer': outer,
                                  'n': [round(c, 3) for c in nmw], 'face_type': g.geometry.objectType.split('::')[-1]})
                    if not outer or Lmm < 2.0:
                        continue
                    acc = [0.0]
                    for i in range(len(P_) - 1):
                        acc.append(acc[-1] + math.dist(P_[i], P_[i + 1]))
                    k = max(2, int(Lmm / SP)); j = 0
                    for i in range(k + 1):
                        sL = Lmm * i / k
                        while j < len(P_) - 2 and acc[j + 1] < sL:
                            j += 1
                        f_ = (sL - acc[j]) / max(acc[j + 1] - acc[j], 1e-9)
                        q = tuple(P_[j][c] + (P_[j + 1][c] - P_[j][c]) * f_ for c in range(3))
                        tw = tuple(P_[j + 1][c] - P_[j][c] for c in range(3)); tl = math.sqrt(sum(c * c for c in tw)); tw = tuple(c / tl for c in tw)
                        pq = Dw(XC + q[0], q[1], q[2])
                        ok, n = g.evaluator.getNormalAtPoint(pq); n.normalize()
                        nw = nw_of(n)
                        ex = (tw[1] * nw[2] - tw[2] * nw[1], tw[2] * nw[0] - tw[0] * nw[2], tw[0] * nw[1] - tw[1] * nw[0])
                        if ex[1] > 0:
                            ex = tuple(-c for c in ex)
                        nin = tuple(-c for c in nw)
                        dl = -1.2 * nin[1] / ex[1] if abs(ex[1]) > 1e-6 else 99.0
                        st.append([round(c, 3) for c in q] + [round(c, 4) for c in tw] + [round(c, 4) for c in nw] +
                                  [round(c, 4) for c in ex] + [round(dl, 3)])
                except Exception as ex_:
                    edges.append({'FAIL': str(ex_)[:80]})
        out['n_end_faces'] = len(endf); out['edges'] = edges; out['stations'] = st
        out['t_s'] = round(time.time() - t0, 1)
        os.makedirs(os.path.dirname(OUTF), exist_ok=True)
        json.dump(out, open(OUTF, 'w'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    short = {'n_end_faces': out.get('n_end_faces'), 'n_stations': len(out.get('stations', [])), 'edges': out.get('edges'),
             't_s': out.get('t_s'), 'FAIL': out.get('FAIL')}
    log('v5f_d10b_lip_stations', 'probe', short)
    print(json.dumps(short, separators=(',', ':')))
