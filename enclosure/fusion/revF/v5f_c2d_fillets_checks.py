# rev F cap block c2d (2026-11-05): fillets on the rebuilt front shell (c2c) with c1e4's edge classes, + checks.
#   Fillets (edges of the planar z-175.3 faces behind the joint, other face non-planar):
#     A  ledge outer edge (cloth turns over it): outward + up, inside TOOL_cap_off1p9 → R0.8
#     B  groove outer top edge: inward + down, inside TOOL_cap_off4p1 → R0.3
#     C  groove inner top edge: outward + up, outside TOOL_cap_off1p9, inside TOOL_cap_off5 → R0.3
#   Checks: volumes, lumps, duplicates; front ∩ cap / door, cap ∩ door (top region); per screw a ray up at r 3.0 from the axis
#   (pad underside 169.5, pad top 172.5 = boss bottom), a ray up on the axis (clearance hole → insert hole end 178.5) and down
#   on the axis (top surface 180); key lanes KO_capkey_* against every solid part and lead (door off); moved / trimmed
#   bodies against the cap and front; exhaust rows: open length per row at mid-wall (REF surface by containment bisection
#   along −y, point 2.4 inside, 0.25 steps – c2d2's measure; run 1 used rays from inside, 0.5 steps, lesson 61).
#   Run 1 on c2c's front (237.2926 → 237.2748); run 2 on c2i's front (single outer rib at SL/SR).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
V_FRONT, V_CAP = 236.7029, None        # run 1: 237.2926 (c2c); run 2: c2i's commit
SCREWS = {'BL': (25.91, -37.80), 'BR': (-25.91, -37.80), 'SL': (43.36, -32.85), 'SR': (-43.36, -32.85)}
SKIP_PREFIX = ('HOUSING_E', 'REF_', 'INNER_', 'TOOL_', 'V11', 'RENDER_', 'sk_', 'KO_', 'PROBE_')
SKIP_SUFFIX = ('_b4n', '_b4d', '_b1', '_b2', '_b5', '_b6v1', '_b6s3', '_revE', '_revD', '_tmp', '_wip', '_r2', '_r3', '_fail1',
               '_fail3', '_fail3b', '_c0', '_c1v1', '_v1', '_fail', '_c1')
STALE = ('HOUSING_shell', 'DOOR_tray', 'REF_outer_hidden', 'DOOR_plate', 'DOOR_F', 'GROMMET_usbc', 'TOUCH_pcb', 'LD2410C_env',
         'SENSOR_strip_L', 'SENSOR_strip_R', 'SPK_driver_D40', 'PD_trigger_env_20V', 'GROMMET_usbc_F', 'HOUSING_F_door')


def classify(X, b):
    sets = {'A': adsk.core.ObjectCollection.create(), 'B': adsk.core.ObjectCollection.create(),
            'C': adsk.core.ObjectCollection.create()}
    info = {'A': [], 'B': [], 'C': []}
    t19, t41, t50 = X.body('TOOL_cap_off1p9'), X.body('TOOL_cap_off4p1'), X.body('TOOL_cap_off5')
    for f in b.faces:
        if not f.geometry.objectType.endswith('Plane'):
            continue
        p = f.pointOnFace; ok, n = f.evaluator.getNormalAtPoint(p)
        if (n.y * S + n.z * C) < 0.999 or abs(wz(p) - 175.3) > 0.01:
            continue
        for e in f.edges:
            o = [g for g in e.faces if g != f]
            if not o or o[0].geometry.objectType.endswith('Plane'):
                continue
            ok, t0, t1 = e.evaluator.getParameterExtents(); ok, m = e.evaluator.getPointAtParameter((t0 + t1) / 2)
            if wy(m) > -22.55:
                continue
            ok, no = o[0].evaluator.getNormalAtPoint(m); nw = nw_of(no)
            ox, oy = m.x * 10 - XC, wy(m) + 35.0; L = math.hypot(ox, oy) or 1.0
            radial = (nw[0] * ox + nw[1] * oy) / L
            in19 = t19.pointContainment(m) in INS
            k = None
            if radial > 0.2 and nw[2] > 0.05:
                if in19:
                    k = 'A'
                elif t50.pointContainment(m) in INS:
                    k = 'C'
            elif radial < -0.2 and nw[2] < -0.05 and t41.pointContainment(m) in INS:
                k = 'B'
            if k:
                sets[k].add(e); info[k].append([round(m.x * 10 - XC, 1), round(wy(m), 1)])
    return sets, info


def solids(X):
    out = []
    for b in X.comp.bRepBodies:
        n = b.name
        if n.startswith(SKIP_PREFIX) or n.endswith(SKIP_SUFFIX) or n in STALE \
                or n.startswith(('VOICEPE_', 'BUCK_', 'AMP_', 'SPK_driver', 'SENSOR_strip')) \
                or (n.startswith('PI5_') and n not in ('PI5_F', 'PI5_F_cooler')) or (n.startswith('TOUCH_') and n != 'TOUCH_PCB'):
            continue
        out.append(b)
    return out


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        F, Cp, D = X.body('HOUSING_F_front'), X.body('HOUSING_F_cap'), X.body('HOUSING_F_door')
        out['guard'] = [round(F.volume, 4), round(Cp.volume, 4)]
        if abs(F.volume - V_FRONT) > 0.001:
            raise RuntimeError('volume guard: front %.4f' % F.volume)
        sets, info = classify(X, F)
        out['edges'] = {k: {'n': sets[k].count, 'mid': info[k]} for k in sets}
        R = {'A': 0.08, 'B': 0.03, 'C': 0.03}
        try:
            fi = X.feats.filletFeatures.createInput()
            for k in ('A', 'B', 'C'):
                if sets[k].count:
                    fi.edgeSetInputs.addConstantRadiusEdgeSet(sets[k], VI(R[k]), True)
            X.feats.filletFeatures.add(fi); out['fillet'] = 'one feature'
        except Exception as e:
            out['fillet_one'] = 'FAILED ' + str(e)[:80]; done = []
            for k in ('A', 'B', 'C'):
                F = X.body('HOUSING_F_front'); sets, info = classify(X, F)
                if not sets[k].count:
                    continue
                try:
                    fi = X.feats.filletFeatures.createInput()
                    fi.edgeSetInputs.addConstantRadiusEdgeSet(sets[k], VI(R[k]), True)
                    X.feats.filletFeatures.add(fi); done.append(k)
                except Exception as e2:
                    out['fillet_' + k] = 'FAILED ' + str(e2)[:80]
            out['fillet'] = done
        F = X.body('HOUSING_F_front')
        out['after'] = {'front': round(F.volume, 4), 'cap': round(Cp.volume, 4), 'door': round(D.volume, 4),
                        'lumps': [F.lumps.count, Cp.lumps.count], 'faces_front': F.faces.count,
                        'dupes': [b.name for b in X.comp.bRepBodies if ' (' in b.name]}
        log('v5f_c2d_fillets_checks', 'progress', {'edges': out['edges'], 'after': out['after'], 't_s': round(time.time() - t0, 1)})
        top = lambda: X.wbox(-250, 250, -250, 250, 150.0, 260.0)
        FT = tb_copy(X, 'HOUSING_F_front'); inter(X, FT, top())
        DT = tb_copy(X, 'HOUSING_F_door'); inter(X, DT, top())
        out['x'] = {'front_cap': vol_x(X, FT, tb_copy(X, 'HOUSING_F_cap')), 'front_door': vol_x(X, FT, DT),
                    'cap_door': vol_x(X, tb_copy(X, 'HOUSING_F_cap'), DT)}
        sc = {}
        for k, (cx, cy) in SCREWS.items():
            ax = (XC + cx, cy)
            o3 = (XC + cx + 3.0, cy, 165.0)
            hf = [round(h[4], 3) for h in ray_hits(X, o3, (0, 0, 1), ('HOUSING_F_front',))][:2]
            hc = [round(h[4], 3) for h in ray_hits(X, o3, (0, 0, 1), ('HOUSING_F_cap',))][:1]
            hu = [(h[1][10:], round(h[4], 3)) for h in ray_hits(X, (ax[0], ax[1], 165.0), (0, 0, 1), ('HOUSING_F_front', 'HOUSING_F_cap'))][:2]
            hd = [round(h[4], 3) for h in ray_hits(X, (ax[0], ax[1], 190.0), (0, 0, -1), ('HOUSING_F_cap',))][:2]
            sc[k] = {'r3_front_z': hf, 'r3_cap_z': hc, 'axis_up_first': hu, 'axis_down_cap_z': hd}
        out['screws'] = sc
        lanes = {'KO_capkey_' + k: X.body('KO_capkey_' + k) for k in SCREWS}
        ln = {}
        for kn, kb in lanes.items():
            lb = wbb(X, kb); hit = {}
            for b in solids(X):
                bb = wbb(X, b)
                if bb[1] < lb[0] or bb[0] > lb[1] or bb[3] < lb[2] or bb[2] > lb[3] or bb[5] < lb[4] or bb[4] > lb[5]:
                    continue
                v = vol_x(X, X.tbm.copy(kb), X.tbm.copy(b))
                if v > 0:
                    hit[b.name] = v
            ln[kn] = {'len_mm3': round(kb.volume * 1000, 1), 'hits': hit}
        out['lanes'] = ln
        log('v5f_c2d_fillets_checks', 'progress', {'screws': sc, 'lanes': ln, 't_s': round(time.time() - t0, 1)})
        nb = {}
        for n in ('VEML_env', 'MIC_strip_L_env', 'MIC_strip_R_env', 'KO_mic_L_back', 'KO_mic_R_back', 'LEAD_VEML', 'LEAD_MIC_L',
                  'LEAD_MIC_R'):
            b = X.body(n)
            nb[n] = {'cap': vol_x(X, tb_copy(X, 'HOUSING_F_cap'), X.tbm.copy(b)), 'front': vol_x(X, FT, X.tbm.copy(b))}
        out['bodies'] = nb
        ex = {}
        REFb = X.body('REF_F_outer'); Fb = X.body('HOUSING_F_front')
        for (lab, z) in (('row_162.5-165.5', 164.0), ('row_167.0-170.0', 168.5)):
            n_open = 0; blocked = []
            for i in range(0, 361):
                xr = -45.0 + i * 0.25
                yi, yo = -30.0, -80.0                    # REF surface along -y by bisection (containment only)
                for _ in range(16):
                    ym = (yi + yo) / 2
                    if REFb.pointContainment(Dw(XC + xr, ym, z)) in INS:
                        yi = ym
                    else:
                        yo = ym
                if Fb.pointContainment(Dw(XC + xr, yi + 2.4, z)) in INS:
                    blocked.append(xr)
                else:
                    n_open += 1
            runs = []
            for xr in blocked:
                if runs and abs(xr - runs[-1][1] - 0.25) < 1e-6:
                    runs[-1][1] = xr
                else:
                    runs.append([xr, xr])
            ex[lab] = {'open_mm': n_open * 0.25, 'open_mm2': round(n_open * 0.75, 1), 'blocked_runs': runs}
        out['exhaust'] = ex
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_c2d_fillets_checks', 'run', out)
    print(json.dumps({k: out.get(k) for k in ('guard', 'fillet', 'after', 'x', 't_s', 'FAIL')}, separators=(',', ':')))
