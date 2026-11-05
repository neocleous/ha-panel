# rev F block 6p (2026-11-05): block-6 probes on the final state (brief 6.1). Read-only for the parts; one temporary
#   hidden body PROBE_tmp_OUT (deleted at the end) = everything outside the plastic: (box − REF_F_outer) ∪
#   (TOOL_outer_skin_0p7 − front − door), i.e. the air plus the 0.7 recess where the cloth lies.
#   1. Wall: a ray from the cavity finds the inner surface point p of the first housing body hit; wall = the minimum
#      distance from p to PROBE_tmp_OUT (MeasureManager) – 10 places, cloth and hard zones, front and door.
#   2. Top-front roll: the same at 7 x positions, rays from (x, −30, 170) forward-up (0, 0.629, 0.777) into the inner corner.
#   3. Partitions: speaker-box walls along x / y / z rays through each box's bbox centre (solid runs).
#   4. Lanes: minimum distance from each K5 lane to its neighbours (not the door: the lanes leave through the door opening).
#   5. Door: minimum distance front–door; floor-rim gap under the door's bottom edge (vertical rays).
#   6. Slab: gap from the slab's edges to the housing (design-frame rays from 0.01 outside the slab bbox).
#   7. Joint (seam b): gap to F and D and the hit faces' angle to u at 10 stations (s 0.3 / 1.5) from the gap centre
#      A + 1.05 u; the old z 132 / 150 door pockets (open to D after B6s-3) filled: door solid at old centre − 2.0 u ± 2.5 t.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
HB = ('HOUSING_F_front', 'HOUSING_F_door')
WALL = [('chin_x0_z30_cloth', (0.0, -5.0, 30.0), (0, 1, 0)), ('side+x_y-30_z60_cloth', (40.0, -30.0, 60.0), (1, 0, 0)),
        ('side-x_y-40_z120_cloth', (-30.0, -40.0, 120.0), (-1, 0, 0)), ('corner+x_y-45_z40_cloth', (40.0, -45.0, 40.0), (0.7071, -0.7071, 0)),
        ('door_back_x0_z60_cloth', (0.0, -60.0, 60.0), (0, -1, 0)), ('door_side_y-65_z100_cloth', (0.0, -65.0, 100.0), (1, 0, 0)),
        ('door_top_y-62_cloth', (0.0, -62.0, 100.0), (0, 0, 1)), ('top_x0_y-30_hard', (0.0, -30.0, 160.0), (0, 0, 1)),
        ('bottom_fillet+x_y-20_cloth', (60.0, -20.0, 10.0), (0.7071, 0, -0.7071)), ('back_band_y-50_z165_cloth', (0.0, -40.0, 165.0), (0, -1, 0))]
LANES = ('KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR')
LANE_NB = ('HOUSING_F_front', 'SPKBOX_L', 'SPKBOX_R', 'MAIN_BRACKET', 'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'RESP_CARRIER',
           'PI5_F', 'PI5_F_cooler', 'SLAB_frame')


def dmin(X, a, b):
    r = X.app.measureManager.measureMinimumDistance(a, b)
    return round(r.value * 10, 3)


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
        out['t_out_s'] = round(time.time() - t0, 1)
        wall = {}
        for (nm, p, d) in WALL:
            hs = ray_hits(X, (XC + p[0], p[1], p[2]), d, HB)
            if not hs:
                wall[nm] = None; continue
            h = hs[0]
            wall[nm] = [h[1][10:], [round(h[2], 1), round(h[3], 1), round(h[4], 1)], dmin(X, h[7], ob)]
        out['wall_[body, p_in, mm]'] = wall
        roll = {}
        for xr in (-90.0, -60.0, -30.0, 0.0, 30.0, 60.0, 90.0):
            hs = ray_hits(X, (XC + xr, -30.0, 170.0), (0, 0.629, 0.777), HB)
            roll[str(xr)] = [round(hs[0][3], 1), round(hs[0][4], 1), dmin(X, hs[0][7], ob)] if hs else None
        out['top_front_roll_[y, z, wall]'] = roll
        part = {}
        for bn in ('SPKBOX_L', 'SPKBOX_R'):
            b = X.body(bn); bb = wbb(X, b); c = ((bb[0] + bb[1]) / 2, (bb[2] + bb[3]) / 2, (bb[4] + bb[5]) / 2)
            r = {}
            for ax, d in (('x', (1, 0, 0)), ('y', (0, 1, 0)), ('z', (0, 0, 1))):
                st = (c[0] - 150 * d[0], c[1] - 150 * d[1], c[2] - 150 * d[2])
                r[ax] = [rr[2] for rr in solid_runs(X, (XC + st[0], st[1], st[2]), d, bn, 300.0)]
            part[bn] = r
        out['box_wall_runs_mm'] = part
        lanes = {}
        for ln in LANES:
            L = X.body(ln)
            if L is None:
                lanes[ln] = 'missing'; continue
            lanes[ln] = {nb: dmin(X, L, X.body(nb)) for nb in LANE_NB if X.body(nb) is not None}
        out['lane_min_dist_mm'] = lanes
        out['front_door_min_dist_mm'] = dmin(X, fb, db)
        rim = {}
        for xr in (0.0, 40.0, -40.0):
            hh = solid_runs(X, (XC + xr, -40.0, 4.0), (0, -1, 0), 'HOUSING_F_door', 80.0)
            if not hh:
                rim[str(xr)] = None; continue
            ym = -40.0 - (hh[-1][0] + hh[-1][1]) / 2
            up = ray_hits(X, (XC + xr, ym, 2.65), (0, 0, 1), ('HOUSING_F_door',)); dn = ray_hits(X, (XC + xr, ym, 2.65), (0, 0, -1), ('HOUSING_F_front',))
            rim[str(xr)] = [round(ym, 2), round(up[0][0] + dn[0][0], 3) if up and dn else None]
        out['rim_gap_[y, gap]'] = rim
        sb = X.body('SLAB_frame').boundingBox
        cx = (sb.minPoint.x + sb.maxPoint.x) / 2; cz = (sb.minPoint.z + sb.maxPoint.z) / 2; yy = (sb.minPoint.y + sb.maxPoint.y) / 2
        rays = {'+x': (P3(sb.maxPoint.x + 0.001, yy, cz), V3(1, 0, 0)), '-x': (P3(sb.minPoint.x - 0.001, yy, cz), V3(-1, 0, 0)),
                'top': (P3(cx, yy, sb.maxPoint.z + 0.001), V3(0, 0, 1)), 'bottom': (P3(cx + 3.0, yy, sb.minPoint.z - 0.001), V3(0, 0, -1)),
                'back_x+80': (P3(cx + 8.0, sb.minPoint.y - 0.001, cz), V3(0, -1, 0)), 'back_x-80': (P3(cx - 8.0, sb.minPoint.y - 0.001, cz), V3(0, -1, 0))}
        slab = {}
        for k, (pt, d) in rays.items():
            hp = adsk.core.ObjectCollection.create()
            fs = X.comp.findBRepUsingRay(pt, d, adsk.fusion.BRepEntityTypes.BRepFaceEntityType, -1.0, False, hp)
            best = None
            for i in range(fs.count):
                if fs.item(i).body.name == 'HOUSING_F_front':
                    q = hp.item(i); t = math.sqrt((q.x - pt.x) ** 2 + (q.y - pt.y) ** 2 + (q.z - pt.z) ** 2) * 10 + 0.01
                    best = t if best is None or t < best else best
            slab[k] = round(best, 3) if best is not None else None
        out['slab_gap_mm'] = slab
        raw = json.load(open(os.path.expanduser('~/Documents/v5f_seam_I.json')))['raw']
        idx = [int(round(i * (len(raw) - 1) / 9.0)) for i in range(10)]
        jg = []
        for k in idx:
            sr = raw[k]; A, u, n = sr['A'], sr['u'], sr['n']
            row = [round(sr['P'][0], 1), round(sr['P'][2], 1)]
            for sd in (0.3, 1.5):
                m = [A[i] + u[i] * 1.05 + n[i] * (sd + 0.7) for i in range(3)]
                hf = ray_hits(X, (XC + m[0], m[1], m[2]), (-u[0], -u[1], -u[2]), ('HOUSING_F_front',))
                hd = ray_hits(X, (XC + m[0], m[1], m[2]), tuple(u), ('HOUSING_F_door',))
                ang = lambda h: round(math.degrees(math.acos(min(1.0, abs(sum(h[5][i] * u[i] for i in range(3)))))), 1)
                row += [round(hf[0][0], 2) if hf else None, ang(hf[0]) if hf else None, round(hd[0][0], 2) if hd else None,
                        ang(hd[0]) if hd else None]
            jg.append(row)
        out['joint_gap_[xr, z, s0.3: tF angF tD angD, s1.5: ...]'] = jg
        fill = {}
        for sx in (1, -1):
            for (zm, ym) in MAG_D1[3:]:
                pp, nn, xr, nw = magnet_point(X, sx, zm, ym)
                pw = (xr, wy(pp), wz(pp))
                sr = min(raw, key=lambda r: sum((r['P'][i] - pw[i]) ** 2 for i in range(3)))
                t = wv(sr['t']); t.normalize(); uu = wv(sr['u']); uu.normalize(); res = []
                for sg in (1, -1):              # old centre − 2.0 u ± 2.5 t: in the old pocket, outside the new, behind D
                    q = P3(pp.x - uu.x * 0.2 + sg * t.x * 0.25, pp.y - uu.y * 0.2 + sg * t.y * 0.25, pp.z - uu.z * 0.2 + sg * t.z * 0.25)
                    res.append(db.pointContainment(qpt(q, nn, 1.0)) in INS)
                fill['%+d,%g' % (sx, zm)] = res
        out['old_door_pockets_z132_150_filled'] = fill
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
    log('v5f_b6p_probes', 'probes', out)
    print(json.dumps(out, separators=(',', ':')))
