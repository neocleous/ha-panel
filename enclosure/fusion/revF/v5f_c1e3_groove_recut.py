# rev F cap block c1e3 (2026-11-05): groove re-cut after the posts.
#   c1f's sections showed c1d's order (groove cut, then posts) let the posts / webs fill parts of the groove: at x 28 the
#   BL/BR web (z 171.8…173.1, back to y −47.1) raised the groove floor 172.8 → 173.1 over ≈ 3 of its 2.8 + width, and at
#   y −30 the FL post's face stands up to 0.5 into the groove's inner upper corner. The same groove tool (TOOL_cap_off4p7 −
#   TOOL_cap_off1p9, z 172.8…175.5, y < −22.5) is cut again: gate on a TemporaryBRep copy (1 lump, volume drop small),
#   then a combine CUT with the tool added as a hidden body (consumed). Fillets of c1e / c1e2 lie outside the tool.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
V_FRONT = 235.6355


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        F = X.body('HOUSING_F_front')
        out['guard'] = round(F.volume, 4)
        if abs(F.volume - V_FRONT) > 0.001:
            raise RuntimeError('volume guard: front %.4f' % F.volume)
        G = tb_copy(X, 'TOOL_cap_off4p7'); inter(X, G, X.wbox(-250, 250, -250, -22.5, 172.8, 175.5))
        X.diff(G, tb_copy(X, 'TOOL_cap_off1p9'))
        out['groove_cm3'] = round(G.volume, 4)
        T = tb_copy(X, 'HOUSING_F_front'); v0 = T.volume
        out['groove_x_front_mm3'] = vol_x(X, T, G)
        X.diff(T, X.tbm.copy(G))
        out['tb'] = {'cm3': round(T.volume, 4), 'drop_mm3': round((v0 - T.volume) * 1000, 3), 'lumps': T.lumps.count}
        if T.lumps.count != 1 or (v0 - T.volume) * 1000 > 200:
            raise RuntimeError('gate failed: %s' % out['tb'])
        gb = X.add(G, 'TOOL_cap_groove_c1'); gb.isLightBulbOn = False
        X.combine(F, [gb], CUT, keep=False)
        F = X.body('HOUSING_F_front')
        out['after'] = {'front': round(F.volume, 4), 'lumps': F.lumps.count, 'faces': F.faces.count,
                        'dupes': [b.name for b in X.comp.bRepBodies if b.name.startswith(('HOUSING_F_front (', 'HOUSING_F_cap ('))],
                        'tool_left': X.body('TOOL_cap_groove_c1') is not None}
        out['x'] = {'front_cap': vol_x(X, tb_copy(X, 'HOUSING_F_front'), tb_copy(X, 'HOUSING_F_cap'))}
        rows = []
        for (xr, y0, d) in ((28.0, -40.0, (0, -1, 0)), (-28.0, -40.0, (0, -1, 0)), (0.0, -40.0, (0, -1, 0))):
            hs = ray_hits(X, (XC + xr, y0, 172.95), d, ('HOUSING_F_front',))
            rows.append([xr, [round(h[3], 2) for h in hs[:4]]])
        out['z172.95_rays_y'] = rows
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_c1e3_groove_recut', 'run', out)
    print(json.dumps(out, separators=(',', ':')))
