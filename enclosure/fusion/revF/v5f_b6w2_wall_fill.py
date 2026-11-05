# rev F block 6w-2 (2026-11-05): Daniel's decision 1 (a) (11:18) – the wall to 2.5 normal where the shell leans, outside
#   the lap. The rev E inner loft is a 2.5 plan offset, so after D1 the plastic is 2.5·cos(lean) thick (2.32–2.49).
#   fill = TOOL_outer_skin_3p2_F (3.2 below the cloth face = 0.7 recess + 2.5) ∩ (INNER_E − TOOL_inner_skin_0p7: the cavity
#          inside the D1 surface) ∩ z 6.5…175.3 (cloth-zone walls; the floor cove is already 3.2 from the R6 fillet)
#          − slot_in (slot face / boss) − VEML / LD2410C windows − lap zone (TOOL_inner_skin_2p1 ∩ y −67…−52.5, z ≥ 5.5:
#          the door keeps its 0.2 gap over the lip and pads) − speaker bores / lattices (r 20.5 about the grille axes)
#          − clamp pilots (r 1.6).
#   front part = fill ∩ (y > −52 ∪ TOOL_seam_RF) − exhaust / BME680 slot tools;
#   door part  = fill − (y > −52) − TOOL_seam_RD − inlet cutout − grommet pin holes − door-boss insert holes.
#   The openings are taken out of the fill itself, so each part gets one JOIN and no opening is touched.
#   B6w-2a (read-only): fill 1161.6 mm³ in 2 lumps (front 877.6, door 283.7), no lump < 0.1 mm³; before the opening cuts it
#   met BME680_env (0.03, front) and KO_K5_LR / MAIN_back_env (door) – pairs already non-zero in the B6m matrix (provisional
#   envelope, lanes used with the door off, board keep-out corners) – plus the grommet / 5807 / cradle inside the inlet.
#   Gates before anything is joined: fill ∩ every current part = 0 except those three known pairs; front part ∩ door = 0;
#   door part ∩ front = 0; TemporaryBRep union of each part = 1 lump. Combine JOIN (fallback: replace the body).
#   After: volumes, lumps, front ∩ door, front–door minimum distance, walls (temporary PROBE_tmp_OUT, deleted), openings,
#   door + grommet pulled straight back against the front.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
EXPECT = {'HOUSING_F_front': 239.797, 'HOUSING_F_door': 50.601}
ZC = 20.6
DB = [(50.0, -67.0), (-50.0, -67.0), (19.0, -74.5), (-19.0, -77.0)]
PILOTS = [(52.75, 10.25), (52.75, 45.75), (-52.75, 10.25), (-52.75, 45.75)]
KNOWN = {'front_part': ('BME680_env',), 'door_part': ('KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR', 'MAIN_back_env')}
SKIP_PREFIX = ('HOUSING_F', 'HOUSING_E', 'REF_', 'INNER_', 'TOOL_', 'V11', 'RENDER_', 'sk_', 'PROBE_')
SKIP_SUFFIX = ('_b4n', '_b4d', '_b1', '_b2', '_b5', '_b6v1', '_b6s3', '_b6w', '_revE', '_revD', '_tmp', '_wip', '_r2', '_r3',
               '_fail1', '_fail3', '_fail3b', '_fail')
STALE = ('HOUSING_shell', 'DOOR_tray', 'REF_outer_hidden', 'DOOR_plate', 'DOOR_F', 'GROMMET_usbc', 'TOUCH_pcb', 'LD2410C_env',
         'SENSOR_strip_L', 'SENSOR_strip_R', 'SPK_driver_D40', 'PD_trigger_env_20V')
FD, DO = ('HOUSING_F_front', 'HOUSING_F_door'), ('HOUSING_F_door',)
# (name, world origin (x_rel, y, z), world direction, bodies): first face hit = inner surface point; lap_* probes skip the lip
WALL = [('chin_x0_z30', (0.0, -5.0, 30.0), (0, 1, 0), FD), ('side+x_y-30_z60', (40.0, -30.0, 60.0), (1, 0, 0), FD),
        ('side-x_y-40_z120', (-30.0, -40.0, 120.0), (-1, 0, 0), FD), ('side+x_y-40_z120', (30.0, -40.0, 120.0), (1, 0, 0), FD),
        ('side+x_y-30_z150', (30.0, -30.0, 150.0), (1, 0, 0), FD), ('corner+x_door_z40', (40.0, -45.0, 40.0), (0.7071, -0.7071, 0), FD),
        ('door_back_x0_z60', (0.0, -60.0, 60.0), (0, -1, 0), FD), ('door_back_x0_z110', (0.0, -60.0, 110.0), (0, -1, 0), FD),
        ('door_back_x0_z135', (0.0, -45.0, 135.0), (0, -1, 0), DO), ('door_side+x_y-70_z100', (0.0, -70.0, 100.0), (1, 0, 0), FD),
        ('door_side-x_y-75_z60', (0.0, -75.0, 60.0), (-1, 0, 0), FD),
        ('lap_door_side+x_y-60_z100', (0.0, -60.0, 100.0), (1, 0, 0), DO), ('lap_door_side+x_y-65_z100', (0.0, -65.0, 100.0), (1, 0, 0), DO),
        ('lap_door_side-x_y-60_z140', (0.0, -60.0, 140.0), (-1, 0, 0), DO), ('lap_door_top_x0_z150', (0.0, -45.0, 150.0), (0, -1, 0), DO),
        ('lap_door_top_x0_z158', (0.0, -45.0, 158.0), (0, -1, 0), DO), ('lap_door_top_x+30_z155', (30.0, -45.0, 155.0), (0, -1, 0), DO),
        ('back_band_x0_z165', (0.0, -40.0, 165.0), (0, -1, 0), FD), ('back_band_x+45_z165', (45.0, -30.0, 165.0), (0, -1, 0), FD),
        ('back_band_x-45_z165', (-45.0, -30.0, 165.0), (0, -1, 0), FD), ('back_band_x+45_z170', (45.0, -30.0, 170.0), (0, -1, 0), FD),
        ('back_band_x0_z172', (0.0, -35.0, 172.0), (0, -1, 0), FD), ('top_x0_hard', (0.0, -30.0, 160.0), (0, 0, 1), FD)]


def current_parts(X):
    parts = []
    for b in X.comp.bRepBodies:
        n = b.name
        if n.startswith(SKIP_PREFIX) or n.endswith(SKIP_SUFFIX) or n in STALE or n.startswith(('VOICEPE_', 'BUCK_', 'AMP_', 'SPK_driver', 'SENSOR_strip')) \
                or (n.startswith('PI5_') and n not in ('PI5_F', 'PI5_F_cooler')) or (n.startswith('TOUCH_') and n != 'TOUCH_PCB'):
            continue
        parts.append(b)
    return parts


def hits_vs(X, m, parts):
    mb = m.boundingBox; hits = {}
    for o in parts:
        ob = o.boundingBox
        lo = [max(mb.minPoint.x, ob.minPoint.x), max(mb.minPoint.y, ob.minPoint.y), max(mb.minPoint.z, ob.minPoint.z)]
        hi = [min(mb.maxPoint.x, ob.maxPoint.x), min(mb.maxPoint.y, ob.maxPoint.y), min(mb.maxPoint.z, ob.maxPoint.z)]
        if any(hi[k] < lo[k] for k in range(3)):
            continue
        box = X.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(P3((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2),
                              V3(1, 0, 0), V3(0, 1, 0), hi[0] - lo[0] + 0.02, hi[1] - lo[1] + 0.02, hi[2] - lo[2] + 0.02))
        qa = X.tbm.copy(m); inter(X, qa, box)
        if qa.volume <= 0:
            continue
        qb = X.tbm.copy(o); inter(X, qb, X.tbm.copy(box)); inter(X, qa, qb)
        if qa.volume * 1000 > 0.0005:
            hits[o.name] = round(qa.volume * 1000, 4)
    return hits


def dmin(X, a, b):
    return round(X.app.measureManager.measureMinimumDistance(a, b).value * 10, 3)


def build_fill(X, out):
    fill = tb_copy(X, 'TOOL_outer_skin_3p2_F')
    inter(X, fill, X.wbox(-250, 250, -250, 250, 6.5, TOP_Z))
    cav = tb_copy(X, 'INNER_E'); X.diff(cav, tb_copy(X, 'TOOL_inner_skin_0p7'))
    inter(X, fill, cav)
    spk = None
    for s in (1, -1):
        c = X.tbm.createCylinderOrCone(Dw(XC + s * 70.5, -10.0, 28.0), 2.05, Dw(XC + s * 70.5, 10.0, 28.0), 2.05)
        spk = c if spk is None else X.union(spk, c)
    pil = None
    for (xr, z) in PILOTS:
        c = X.tbm.createCylinderOrCone(Dw(XC + xr, -1.0, z), 0.16, Dw(XC + xr, 6.0, z), 0.16)
        pil = c if pil is None else X.union(pil, c)
    lap = tb_copy(X, 'TOOL_inner_skin_2p1'); inter(X, lap, X.wbox(-250, 250, -67.0, -52.5, 5.5, 260))
    for v in (slot_in(X), veml_excl(X), ld_excl(X), lap, spk, pil):
        X.diff(fill, v)
    fs = X.wbox(-250, 250, -52.0, 250, -20, 260); X.union(fs, tb_copy(X, 'TOOL_seam_RF'))
    fpart = X.tbm.copy(fill); inter(X, fpart, X.tbm.copy(fs))
    X.diff(fpart, tb_copy(X, 'TOOL_exhaust_slots')); X.diff(fpart, tb_copy(X, 'TOOL_bme680_slots'))
    dpart = X.tbm.copy(fill); X.diff(dpart, X.tbm.copy(fs)); X.diff(dpart, tb_copy(X, 'TOOL_seam_RD'))
    X.diff(dpart, X.wbox(XC - 12.2, XC + 12.2, -88.0, -79.0, ZC - 7.3, ZC + 7.3))
    for sx in (1, -1):
        X.diff(dpart, X.tbm.createCylinderOrCone(Dw(XC + sx * 13.6, -88.0, ZC), 0.105, Dw(XC + sx * 13.6, -79.0, ZC), 0.105))
    for (xr, y) in DB:
        X.diff(dpart, X.wcyl_z(XC + xr, y, 2.0, 2.3, 9.5))
    out['fill_mm3_lumps'] = [round(fill.volume * 1000, 2), fill.lumps.count]
    out['parts_mm3_lumps'] = {'front': [round(fpart.volume * 1000, 2), fpart.lumps.count], 'door': [round(dpart.volume * 1000, 2), dpart.lumps.count]}
    return fpart, dpart


def walls(X, ob):
    res = {}
    for (nm, p, d, names) in WALL:
        hs = ray_hits(X, (XC + p[0], p[1], p[2]), d, names)
        res[nm] = [hs[0][1][10:], [round(hs[0][2], 1), round(hs[0][3], 1), round(hs[0][4], 1)], dmin(X, hs[0][7], ob)] if hs else None
    return res


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time(); tmp = []
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.002:
                raise RuntimeError('guard: %s volume %s, expected %s' % (k, None if b is None else round(b.volume, 3), v))
        if X.body('TOOL_outer_skin_3p2_F') is None:
            raise RuntimeError('B6w-1 tool missing')
        out['step'] = 'fill'
        fpart, dpart = build_fill(X, out)
        out['t_fill_s'] = round(time.time() - t0, 1)
        fb = X.body('HOUSING_F_front'); db = X.body('HOUSING_F_door')
        out['step'] = 'gates'
        cross = {'front_part_x_door': vol_x(X, fpart, db), 'door_part_x_front': vol_x(X, dpart, fb)}
        out['cross_mm3'] = cross
        parts = current_parts(X); out['n_parts'] = len(parts)
        hv = {'front_part': hits_vs(X, fpart, parts), 'door_part': hits_vs(X, dpart, parts)}
        out['fill_vs_parts_mm3'] = hv
        new = {k: [n for n in v if n not in KNOWN[k]] for k, v in hv.items()}
        if any(v > 0 for v in cross.values()) or new['front_part'] or new['door_part']:
            raise RuntimeError('gate: fill crosses %s / %s – nothing joined' % (cross, new))
        fq = X.tbm.copy(fb); X.union(fq, X.tbm.copy(fpart))
        dq = X.tbm.copy(db); X.union(dq, X.tbm.copy(dpart))
        out['temp_cm3_lumps'] = {'front': [round(fq.volume, 4), fq.lumps.count], 'door': [round(dq.volume, 4), dq.lumps.count]}
        if fq.lumps.count != 1 or dq.lumps.count != 1:
            raise RuntimeError('gate: temp union not one lump – nothing joined')
        out['added_mm3'] = {'front': round((fq.volume - fb.volume) * 1000, 2), 'door': round((dq.volume - db.volume) * 1000, 2)}
        out['t_gates_s'] = round(time.time() - t0, 1)
        out['step'] = 'combine'
        mode = {}
        for name, part, tq in (('HOUSING_F_front', fpart, fq), ('HOUSING_F_door', dpart, dq)):
            b = X.body(name)
            try:
                X.combine(b, [X.add(X.tbm.copy(part), 'B6W2_%s_tmp' % name[-4:])], op=JOIN)
                mode[name] = 'combine'
            except Exception as e:
                for bb in [x for x in X.comp.bRepBodies if x.name.startswith('B6W2_') and x.name.endswith('_tmp')]:
                    bb.name = bb.name[:-4] + '_fail'; bb.isLightBulbOn = False
                b = X.body(name); app_, mat_ = b.appearance, b.material
                b.name = name + '_b6w'; b.isLightBulbOn = False
                nb = X.add(tq, name)
                try:
                    nb.material = mat_; nb.appearance = app_
                except Exception:
                    pass
                mode[name] = 'replaced (%s)' % str(e)[:100]
        out['mode'] = mode
        fb = X.body('HOUSING_F_front'); db = X.body('HOUSING_F_door')
        out['cm3'] = {'front': [239.797, round(fb.volume, 4)], 'door': [50.601, round(db.volume, 4)]}
        out['lumps'] = {'front': fb.lumps.count, 'door': db.lumps.count}
        out['stray'] = [[b.name, b.volume] for b in X.comp.bRepBodies if b.name.endswith('_tmp') or (b.name.startswith('HOUSING_F_') and '(' in b.name)]
        for b in [b for b in X.comp.bRepBodies if b.name.startswith('HOUSING_F_') and '(' in b.name and b.volume < 1e-6]:
            b.deleteMe()
        out['step'] = 'checks_after'
        out['front_x_door_mm3'] = vol_x(X, fb, db)
        out['front_door_min_mm'] = dmin(X, fb, db)
        o = X.wbox(-250, 250, -250, 250, -20, 260); X.diff(o, tb_copy(X, 'REF_F_outer'))
        sk = tb_copy(X, 'TOOL_outer_skin_0p7'); X.diff(sk, X.tbm.copy(fb)); X.diff(sk, X.tbm.copy(db))
        X.union(o, sk)
        ob = X.add(o, 'PROBE_tmp_OUT'); ob.isLightBulbOn = False; tmp.append(ob)
        out['walls_[body, p_in, mm]'] = walls(X, ob)
        # openings by rays: a clear opening gives no face hit of that part over the stated span
        def ys(x, y0, z, names, y_lo, y_hi):
            return [round(h[3], 2) for h in ray_hits(X, (XC + x, y0, z), (0, -1, 0), names) if y_lo <= h[3] <= y_hi]
        n0 = (0.751, 0.643, -0.150); L = math.sqrt(sum(c * c for c in n0)); n = tuple(c / L for c in n0)
        th = math.hypot(n[0], n[1]); t = (n[1] / th, -n[0] / th, 0.0)
        u = (t[1] * n[2] - t[2] * n[1], t[2] * n[0] - t[0] * n[2], t[0] * n[1] - t[1] * n[0])
        if u[2] < 0:
            u = tuple(-c for c in u)
        P0 = (-76.82, -45.0, 92.0)

        def bme(s):
            o = tuple(P0[k] + u[k] * s + n[k] * 3.0 for k in range(3))
            return [round(h[0], 2) for h in ray_hits(X, (XC + o[0], o[1], o[2]), tuple(-c for c in n), ('HOUSING_F_front',)) if h[0] < 9.0]
        out['openings_hits'] = {'exhaust_x0_z168.5': ys(0.0, -30.0, 168.5, ('HOUSING_F_front',), -65.0, -30.0),
                                'exhaust_x0_z173': ys(0.0, -30.0, 173.0, ('HOUSING_F_front',), -65.0, -30.0),
                                'exhaust_x+40_z168.5': ys(40.0, -30.0, 168.5, ('HOUSING_F_front',), -65.0, -30.0),
                                'exhaust_x-44_z173': ys(-44.0, -30.0, 173.0, ('HOUSING_F_front',), -65.0, -30.0),
                                'web_x0_z170.75_(hit)': ys(0.0, -30.0, 170.75, ('HOUSING_F_front',), -65.0, -30.0),
                                'bme_slot_-3': bme(-3.0), 'bme_slot_+3': bme(3.0), 'bme_web_0_(hit)': bme(0.0),
                                'inlet_x0': ys(0.0, -60.0, ZC, DO, -90.0, -70.0), 'inlet_x+11.9': ys(11.9, -60.0, ZC, DO, -90.0, -70.0),
                                'inlet_x0_z+7.1': ys(0.0, -60.0, ZC + 7.1, DO, -90.0, -70.0),
                                'pin+x': ys(13.6, -60.0, ZC, DO, -90.0, -70.0), 'pin-x': ys(-13.6, -60.0, ZC, DO, -90.0, -70.0)}
        out['inserts_open_z8'] = [not X.inside(db, XC + xr, y, 8.0) for (xr, y) in DB]
        out['lanes_to_front_min_mm'] = {k: dmin(X, X.body(k), fb) for k in ('KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR')}
        g = X.body('GROMMET_usbc_F'); sweep = {}
        for dy in (1.0, 3.0, 10.0, 30.0, 80.0):
            q = X.tbm.copy(db); X.union(q, X.tbm.copy(g)); mvw(X, q, 0.0, -dy, 0.0)
            sweep[str(dy)] = vol_x(X, q, fb)
        out['door_sweep_vs_front_mm3'] = sweep
        out['step'] = 'done'
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
    log('v5f_b6w2_wall_fill', 'build', out)
    print(json.dumps(out, separators=(',', ':')))
