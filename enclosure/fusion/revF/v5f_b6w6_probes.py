# rev F block 6w-6 (2026-11-05): follow-up probes after the B6w-4 scan (temporary PROBE_tmp_OUT, deleted).
#   1. Where the speaker boxes are 0.20 from the front shell (B6w-3): minimum distance with both points (world x_rel, y, z).
#   2. Back band away from the slot edges (the scan's z 170 row lies on the lower slot's top edge, inside the 0.05 band the
#      fill keeps from the slot faces): rays −y from y −30 at z 166.0 / 170.75 (web) / 175.0, x_rel 0, ±20, ±40.
#   3. Lap band, door only (the scan's rays hit the lip first there): rays −y from y −45 at z 135…162, x_rel 0, ±20, ±40,
#      and +x / −x from x_rel 0 at y −56…−66, z 40…140.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
FD, DO = ('HOUSING_F_front', 'HOUSING_F_door'), ('HOUSING_F_door',)


def wpt(p):
    return [round(p.x * 10 - XC, 2), round(wy(p), 2), round(wz(p), 2)]


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time(); tmp = []
    try:
        fb = X.body('HOUSING_F_front'); db = X.body('HOUSING_F_door'); mm = X.app.measureManager
        for bn in ('SPKBOX_L', 'SPKBOX_R'):
            r = mm.measureMinimumDistance(X.body(bn), fb)
            out[bn] = {'mm': round(r.value * 10, 3), 'box_pt': wpt(r.positionOne), 'front_pt': wpt(r.positionTwo)}
        o = X.wbox(-250, 250, -250, 250, -20, 260); X.diff(o, tb_copy(X, 'REF_F_outer'))
        sk = tb_copy(X, 'TOOL_outer_skin_0p7'); X.diff(sk, X.tbm.copy(fb)); X.diff(sk, X.tbm.copy(db))
        X.union(o, sk)
        ob = X.add(o, 'PROBE_tmp_OUT'); ob.isLightBulbOn = False; tmp.append(ob)

        def wall(o_w, d_w, names):
            hs = ray_hits(X, (XC + o_w[0], o_w[1], o_w[2]), d_w, names)
            if not hs:
                return None
            h = hs[0]
            return [h[1][10:], round(h[2], 1), round(h[3], 1), round(h[4], 1), round(mm.measureMinimumDistance(h[7], ob).value * 10, 3)]
        bb = {}
        for z in (166.0, 170.75, 175.0):
            for xr in (0.0, 20.0, -20.0, 40.0, -40.0):
                bb['x%g_z%g' % (xr, z)] = wall((xr, -30.0, z), (0, -1, 0), FD)
        out['back_band_[body, x, y, z, mm]'] = bb
        lap = {}
        for z in (135.0, 140.0, 145.0, 150.0, 155.0, 158.0, 162.0):
            for xr in (0.0, 20.0, -20.0, 40.0, -40.0):
                lap['top_x%g_z%g' % (xr, z)] = wall((xr, -45.0, z), (0, -1, 0), DO)
        for y in (-56.0, -58.0, -60.0, -62.0, -64.0, -66.0):
            for z in (40.0, 80.0, 120.0, 140.0):
                for sx in (1, -1):
                    lap['side%+d_y%g_z%g' % (sx, y, z)] = wall((0.0, y, z), (sx, 0, 0), DO)
        vals = [v for v in lap.values() if v]
        out['lap_min_max_n'] = [min(v[4] for v in vals), max(v[4] for v in vals), len(vals)] if vals else None
        out['lap_lowest10'] = sorted([[k] + v for k, v in lap.items() if v], key=lambda r: r[5])[:10]
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
    log('v5f_b6w6_probes', 'probes', out)
    print(json.dumps(out, separators=(',', ':'))[:7000])
