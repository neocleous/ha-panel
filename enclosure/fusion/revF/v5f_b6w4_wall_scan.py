# rev F block 6w-4 (2026-11-05): normal-wall scan after the decision-1 (a) fill (B6w-2d). Temporary PROBE_tmp_OUT (deleted):
#   (box − REF_F_outer) ∪ (TOOL_outer_skin_0p7 − front − door) = everything outside the plastic, cloth layer included.
#   Rays in plan from (x_rel 0, y −38) every 15° at z 10, 20, 35, 50, 65, 80, 95, 110, 125, 140, 150, 158, 165, 170, 174 to the
#   first front / door face; normal wall = minimum distance from that point to PROBE_tmp_OUT. Each hit is classed: lap
#   (y −67…−52.5), chin (y > −3), slot (d < 15.65 above Z −94.35, hard face), cove (z < 6.5), or fill zone. Reports per
#   class min / max / count and every fill-zone hit below 2.50 or above 2.60 (bosses, rail, baffles show as thick).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
ZS = (10.0, 20.0, 35.0, 50.0, 65.0, 80.0, 95.0, 110.0, 125.0, 140.0, 150.0, 158.0, 165.0, 170.0, 174.0)
FD = ('HOUSING_F_front', 'HOUSING_F_door')


def zone(p, y, z):
    d = -p.y * 10; Z = p.z * 10
    if -67.0 <= y <= -52.5:
        return 'lap'
    if y > -3.0:
        return 'chin'
    if d < 15.65 and Z > -94.35:
        return 'slot'
    if z < 6.5:
        return 'cove'
    return 'fill'


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time(); tmp = []
    try:
        fb = X.body('HOUSING_F_front'); db = X.body('HOUSING_F_door')
        out['cm3'] = {'front': round(fb.volume, 4), 'door': round(db.volume, 4)}
        o = X.wbox(-250, 250, -250, 250, -20, 260); X.diff(o, tb_copy(X, 'REF_F_outer'))
        sk = tb_copy(X, 'TOOL_outer_skin_0p7'); X.diff(sk, X.tbm.copy(fb)); X.diff(sk, X.tbm.copy(db))
        X.union(o, sk)
        ob = X.add(o, 'PROBE_tmp_OUT'); ob.isLightBulbOn = False; tmp.append(ob)
        mm = X.app.measureManager
        rows = []; stats = {}
        for z in ZS:
            for k in range(24):
                a = math.radians(15.0 * k)
                hs = ray_hits(X, (XC, -38.0, z), (math.cos(a), math.sin(a), 0.0), FD)
                if not hs:
                    continue
                h = hs[0]
                w = round(mm.measureMinimumDistance(h[7], ob).value * 10, 3)
                zn = zone(h[7], h[3], h[4])
                rows.append([z, 15 * k, h[1][10:], round(h[2], 1), round(h[3], 1), round(h[4], 1), w, zn])
                s = stats.setdefault(zn, [99.0, 0.0, 0])
                s[0] = min(s[0], w); s[1] = max(s[1], w); s[2] += 1
        out['stats_[min, max, n]'] = stats
        out['fill_below_2.50'] = [r for r in rows if r[7] == 'fill' and r[6] < 2.50]
        out['fill_above_2.60'] = [r for r in rows if r[7] == 'fill' and r[6] > 2.60]
        out['lap_rows'] = [r for r in rows if r[7] == 'lap']
        out['n_rays_hit'] = len(rows)
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    finally:
        for t in tmp:
            try:
                t.deleteMe()
            except Exception:
                pass
    out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('PROBE_tmp')]
    log('v5f_b6w4_wall_scan', 'scan', out)
    print(json.dumps({k: out[k] for k in out if k != 'lap_rows'}, separators=(',', ':'))[:6000])
