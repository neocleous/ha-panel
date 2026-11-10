# rev F f2c1 (2026-11-10): read-only probe 2 before the box rework - SPKBOX_R faces, the shell's baffle behind the +x driver.
# Lesson from f2c0: never list every body a ray hits (25 hidden backups of the front shell answer each ray) - name the bodies wanted.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())


def wv(v):
    return (v.x, v.y * C - v.z * S, v.y * S + v.z * C)


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        R = X.body('SPKBOX_R')
        pl = {}; cy = set(); oth = 0.0
        for f in R.faces:
            g = f.geometry; a = f.area * 100.0
            if g.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType:
                ok, n = f.evaluator.getNormalAtPoint(f.pointOnFace); n = wv(n); p = W(f.pointOnFace)
                for i, ax in enumerate('xyz'):
                    if abs(n[i]) > 0.9995:
                        k = '%s%s%.2f' % (ax, '+' if n[i] > 0 else '-', p[i]); pl[k] = round(pl.get(k, 0.0) + a, 0); break
                else:
                    oth += a
            elif g.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType:
                ax = wv(g.axis); o = W(g.origin); vs = [W(v.geometry) for v in f.vertices]
                for i, nm in enumerate('xyz'):
                    if abs(ax[i]) > 0.9995 and vs:
                        j = [q for q in range(3) if q != i]
                        cy.add((nm, round(o[j[0]], 2), round(o[j[1]], 2), round(g.radius * 10, 2), round(min(v[i] for v in vs), 1), round(max(v[i] for v in vs), 1)))
                        break
                else:
                    oth += a
            else:
                oth += a
        st['R'] = {'planes': ' '.join('%s:%d' % (k, v) for k, v in sorted(pl.items()) if v >= 5), 'cyl': sorted(cy), 'other_mm2': round(oth)}
        # shell baffle behind the +x driver: faces facing -y between y -0.1 and 0.8, x 40..100, z 0..60
        F = X.body('HOUSING_F_front')
        bp = []; bc = {}
        for f in F.faces:
            bb = f.boundingBox
            cx = (bb.minPoint.x + bb.maxPoint.x) * 5 - XC
            if cx < 40 or cx > 100:
                continue
            g = f.geometry
            if g.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType:
                ok, n = f.evaluator.getNormalAtPoint(f.pointOnFace); n = wv(n); p = W(f.pointOnFace)
                if n[1] < -0.9995 and -0.1 <= p[1] <= 0.8:
                    vs = [W(v.geometry) for v in f.vertices]
                    if vs and min(v[2] for v in vs) < 60:
                        bp.append([round(p[1], 2), round(f.area * 100), round(min(v[0] for v in vs), 1), round(max(v[0] for v in vs), 1),
                                   round(min(v[2] for v in vs), 1), round(max(v[2] for v in vs), 1), f.loops.count])
            elif g.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType:
                ax = wv(g.axis); o = W(g.origin)
                if abs(ax[1]) > 0.9995 and o[2] < 60:
                    vs = [W(v.geometry) for v in f.vertices]
                    if vs and min(v[1] for v in vs) < 1.0:
                        k = '%.2f' % (g.radius * 10)
                        e = bc.setdefault(k, [0, 999, -999, 999, -999, 999, -999])
                        e[0] += 1; e[1] = min(e[1], round(o[0], 1)); e[2] = max(e[2], round(o[0], 1)); e[3] = min(e[3], round(o[2], 1)); e[4] = max(e[4], round(o[2], 1))
                        e[5] = min(e[5], round(min(v[1] for v in vs), 1)); e[6] = max(e[6], round(max(v[1] for v in vs), 1))
        st['baffle_planes[y,mm2,x0,x1,z0,z1,loops]'] = sorted(bp)
        st['baffle_cyl{r:[n,x0,x1,z0,z1,y0,y1]}'] = bc
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status('f2c1', st)


run(None)
