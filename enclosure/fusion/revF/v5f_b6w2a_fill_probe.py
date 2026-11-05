# rev F block 6w-2a (2026-11-05), read-only: the decision-1 (a) fill as a TemporaryBRep before anything is joined.
#   fill = TOOL_outer_skin_3p2_F ∩ (INNER_E − TOOL_inner_skin_0p7) ∩ z 6.5…175.3 − slot_in − VEML / LD windows − lap zone
#          (TOOL_inner_skin_2p1 ∩ y −67…−52.5, z ≥ 5.5) − speaker bores / lattices (r 20.5 about the grille axes, y −10…10)
#          − clamp pilots (r 1.6, y −1…6).
#   Reports: volume, lumps (largest 12 with world centre and bbox, count of lumps < 0.01 mm³), faces; front / door split;
#   what the fill crosses (exhaust / BME680 tools, door inlet + pins, door-boss insert holes, grommet, bores, pilots);
#   fill ∩ every current part.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
ZC = 20.6
DB = [(50.0, -67.0), (-50.0, -67.0), (19.0, -74.5), (-19.0, -77.0)]
PILOTS = [(52.75, 10.25), (52.75, 45.75), (-52.75, 10.25), (-52.75, 45.75)]
SKIP_PREFIX = ('HOUSING_F', 'HOUSING_E', 'REF_', 'INNER_', 'TOOL_', 'V11', 'RENDER_', 'sk_', 'PROBE_')
SKIP_SUFFIX = ('_b4n', '_b4d', '_b1', '_b2', '_b5', '_b6v1', '_b6s3', '_revE', '_revD', '_tmp', '_wip', '_r2', '_r3', '_fail1',
               '_fail3', '_fail3b', '_fail')
STALE = ('HOUSING_shell', 'DOOR_tray', 'REF_outer_hidden', 'DOOR_plate', 'DOOR_F', 'GROMMET_usbc', 'TOUCH_pcb', 'LD2410C_env',
         'SENSOR_strip_L', 'SENSOR_strip_R', 'SPK_driver_D40', 'PD_trigger_env_20V')


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
    return hits or 'all 0'


def lump_rows(t):
    rows = []
    for i in range(t.lumps.count):
        lu = t.lumps.item(i); bb = lu.boundingBox
        c = P3((bb.minPoint.x + bb.maxPoint.x) / 2, (bb.minPoint.y + bb.maxPoint.y) / 2, (bb.minPoint.z + bb.maxPoint.z) / 2)
        rows.append([round(lu.volume * 1000, 4), round(c.x * 10 - XC, 1), round(wy(c), 1), round(wz(c), 1),
                     round((bb.maxPoint.x - bb.minPoint.x) * 10, 1), round((bb.maxPoint.y - bb.minPoint.y) * 10, 1),
                     round((bb.maxPoint.z - bb.minPoint.z) * 10, 1)])
    return sorted(rows, key=lambda r: -r[0])


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        out['cm3'] = {'front': round(X.body('HOUSING_F_front').volume, 4), 'door': round(X.body('HOUSING_F_door').volume, 4)}
        fill = tb_copy(X, 'TOOL_outer_skin_3p2_F')
        inter(X, fill, X.wbox(-250, 250, -250, 250, 6.5, TOP_Z))
        cav = tb_copy(X, 'INNER_E'); X.diff(cav, tb_copy(X, 'TOOL_inner_skin_0p7'))
        inter(X, fill, cav)
        out['raw'] = {'mm3': round(fill.volume * 1000, 2), 'lumps': fill.lumps.count, 'faces': fill.faces.count, 't_s': round(time.time() - t0, 1)}
        spk = None
        for s in (1, -1):
            c = X.tbm.createCylinderOrCone(Dw(XC + s * 70.5, -10.0, 28.0), 2.05, Dw(XC + s * 70.5, 10.0, 28.0), 2.05)
            spk = c if spk is None else X.union(spk, c)
        pil = None
        for (xr, z) in PILOTS:
            c = X.tbm.createCylinderOrCone(Dw(XC + xr, -1.0, z), 0.16, Dw(XC + xr, 6.0, z), 0.16)
            pil = c if pil is None else X.union(pil, c)
        lap = tb_copy(X, 'TOOL_inner_skin_2p1'); inter(X, lap, X.wbox(-250, 250, -67.0, -52.5, 5.5, 260))
        ex = {'slot_in': slot_in(X), 'veml': veml_excl(X), 'ld': ld_excl(X), 'lap': lap, 'spk_bores': spk, 'pilots': pil}
        out['x_excl_mm3'] = {k: vol_x(X, fill, v) for k, v in ex.items()}
        for v in ex.values():
            X.diff(fill, X.tbm.copy(v))
        rows = lump_rows(fill)
        out['fill'] = {'mm3': round(fill.volume * 1000, 2), 'lumps': fill.lumps.count, 'faces': fill.faces.count,
                       'lumps_lt_0.01mm3': sum(1 for r in rows if r[0] < 0.01), 'lumps_lt_0.1mm3': sum(1 for r in rows if r[0] < 0.1),
                       'largest_[mm3, xr, y, z, dx, dy, dz]': rows[:12], 'bbox_world': [round(v, 1) for v in wbb(X, fill)]}
        out['t_fill_s'] = round(time.time() - t0, 1)
        fs = X.wbox(-250, 250, -52.0, 250, -20, 260); X.union(fs, tb_copy(X, 'TOOL_seam_RF'))
        fpart = X.tbm.copy(fill); inter(X, fpart, X.tbm.copy(fs))
        dpart = X.tbm.copy(fill); X.diff(dpart, X.tbm.copy(fs)); X.diff(dpart, tb_copy(X, 'TOOL_seam_RD'))
        out['split_mm3_lumps'] = {'front': [round(fpart.volume * 1000, 2), fpart.lumps.count], 'door': [round(dpart.volume * 1000, 2), dpart.lumps.count],
                                  'rest': round((fill.volume - fpart.volume - dpart.volume) * 1000, 3)}
        fb = X.body('HOUSING_F_front'); db = X.body('HOUSING_F_door')
        out['overlap_existing_mm3'] = {'front_part_x_front': vol_x(X, fpart, fb), 'door_part_x_door': vol_x(X, dpart, db),
                                       'front_part_x_door': vol_x(X, fpart, db), 'door_part_x_front': vol_x(X, dpart, fb)}
        inlet = X.wbox(XC - 12.2, XC + 12.2, -88.0, -79.0, ZC - 7.3, ZC + 7.3)
        pins = None
        for sx in (1, -1):
            c = X.tbm.createCylinderOrCone(Dw(XC + sx * 13.6, -88.0, ZC), 0.105, Dw(XC + sx * 13.6, -79.0, ZC), 0.105)
            pins = c if pins is None else X.union(pins, c)
        holes = None
        for (xr, y) in DB:
            t = X.wcyl_z(XC + xr, y, 2.0, 2.3, 9.5); holes = t if holes is None else X.union(holes, t)
        out['x_openings_mm3'] = {'exhaust_front': vol_x(X, fpart, X.body('TOOL_exhaust_slots')),
                                 'bme680_front': vol_x(X, fpart, X.body('TOOL_bme680_slots')),
                                 'inlet_door': vol_x(X, dpart, inlet), 'pins_door': vol_x(X, dpart, pins),
                                 'insert_holes_door': vol_x(X, dpart, holes), 'grommet_door': vol_x(X, dpart, X.body('GROMMET_usbc_F'))}
        parts = current_parts(X)
        out['n_parts'] = len(parts)
        out['fill_vs_parts_mm3'] = {'front_part': hits_vs(X, fpart, parts), 'door_part': hits_vs(X, dpart, parts)}
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b6w2a_fill_probe', 'probe', out)
    print(json.dumps(out, separators=(',', ':')))
