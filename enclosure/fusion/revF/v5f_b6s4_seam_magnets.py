# rev F block 6 / seam (b), option I (2026-11-05): the 10 lap magnets moved back after B6s-3 / 3b (points: B6s-2 →
#   v5f_seam_I.json 'mags': moved along u until the door pocket rim is 1.05 from A + 1.7 u; B6s-3b put the door face at
#   A + 1.9 u, so each point moves 0.2 further along u here and is projected back onto INNER_E by a ray along n).
#   Door:  old pockets filled (Ø8.5, s 0.1…2.6 ∩ TOOL_seam_wall − TOOL_seam_RD), new pockets Ø8.3 from s +0.2 through
#          the outer surface (as B5f).
#   Front: old pads outside the lip removed ((Ø12 s 0…−3.0 ∩ INNER_E − skin 0.9) − lip), old lip pockets filled
#          (Ø8.5 s −1.1…−3.2 ∩ lip), new pads Ø12 s −0.9…−3.0, new lip pockets Ø8.3 s −1.2…−3.1 (as B5e-2), LCD-lane
#          notches r 4.0 kept. Lip = (TOOL_inner_skin_2p1 − TOOL_inner_skin_0p9) ∩ (y −63.5…−53.5, z ≥ 6.5).
#   Checks: removed volume = the old pads' volume outside the lip, magnet probes (B5j-1 set), old pockets filled, front ∩
#   door, front / door vs every current part, door + grommet pulled back.
#   Both results are computed on TemporaryBRep copies first; the combines then run per body, and if one fails that body
#   is replaced by its TemporaryBRep result (old body → *_b6s3, hidden; appearance and material copied).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
SEAM = os.path.expanduser('~/Documents/v5f_seam_I.json')
DD = 1.9                                                            # door face A + 1.9 u (B6s-3b)


def vsub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def vadd(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def vmul(a, k): return (a[0] * k, a[1] * k, a[2] * k)
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def unit(a):
    l = math.sqrt(dot(a, a)); return (a[0] / l, a[1] / l, a[2] / l)


def near(raw, pw):
    return min(raw, key=lambda s: dot(vsub(tuple(s['P']), pw), vsub(tuple(s['P']), pw)))


def clearance(pw, nm, s):
    u = tuple(s['u']); D = vadd(tuple(s['A']), vmul(u, DD))
    w = unit(vadd(vmul(u, -1.0), vmul(nm, dot(u, nm))))
    return min(dot(vsub(vadd(vadd(pw, vmul(nm, sd)), vmul(w, 4.15)), D), u) for sd in (0.2, 1.0, 1.8))
EXPECT = {'HOUSING_F_front': 239.800, 'HOUSING_F_door': 50.601}      # after B6s-3b
SKIP_PREFIX = ('HOUSING_F', 'HOUSING_E', 'REF_', 'INNER_', 'TOOL_', 'V11', 'RENDER_', 'sk_')
SKIP_SUFFIX = ('_b4n', '_b4d', '_b1', '_b2', '_b5', '_b6v1', '_b6s3', '_revE', '_revD', '_tmp', '_wip', '_r2', '_r3', '_fail1',
               '_fail3', '_fail3b')
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
        if o.name == m.name:
            continue
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
        if qa.volume * 1000 > 0.005:
            hits[o.name] = round(qa.volume * 1000, 2)
    return hits or 'all 0'


def ucat(X, bodies):
    r = None
    for b in bodies:
        r = b if r is None else X.union(r, b)
    return r


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if v is None or b is None or abs(b.volume - v) > 0.002:
                raise RuntimeError('guard: %s volume %s, expected %s' % (k, None if b is None else round(b.volume, 3), v))
        if X.body('TOOL_seam_RD') is None or X.body('TOOL_seam_wall') is None:
            raise RuntimeError('B6s-3 tools missing')
        data = json.load(open(SEAM)); mg = data['mags']; raw = data['raw']
        old, new, pts = [], [], {}
        for s in (1, -1):
            for (zm, ym) in MAG_D1:
                p, n, xr, nw = magnet_point(X, s, zm, ym)
                old.append((p, n))
                m = mg['%+d,%g' % (s, zm)]
                pw = tuple(m['new_xr_y_z']); nm = unit(tuple(m['n']))
                u = tuple(near(raw, pw)['u'])
                o = vsub(vadd(pw, vmul(u, DD - 1.7)), vmul(nm, 1.5))
                h = ray_hits(X, (XC + o[0], o[1], o[2]), nm, ('INNER_E',))[0]
                pw2 = (h[2], h[3], h[4]); nm2 = unit(h[5])
                pts['%+d,%g' % (s, zm)] = {'old': [round(xr, 2), ym, zm], 'new': [round(c, 2) for c in pw2],
                                           'rim_to_D': round(clearance(pw2, nm2, near(raw, pw2)), 3)}
                pn = Dw(XC + pw2[0], pw2[1], pw2[2]); nn = wv(nm2); nn.normalize()
                new.append((pn, nn))
        out['magnets'] = pts
        out['step'] = 'tools'
        loc = X.wbox(-250, 250, -70.0, -48.0, 0.0, 260)
        lip = tb_copy(X, 'TOOL_inner_skin_2p1'); inter(X, lip, X.tbm.copy(loc))
        X.diff(lip, inter(X, tb_copy(X, 'TOOL_inner_skin_0p9'), X.tbm.copy(loc)))
        inter(X, lip, X.wbox(-250, 250, -63.5, -53.5, 6.5, 260))
        notch = None
        for (a, b) in LANES_UP + LANES_LO:
            t = X.tbm.createCylinderOrCone(Dw(*a), 0.40, Dw(*b), 0.40)
            inter(X, t, X.wbox(-250, 250, -64.0, -53.4, 0, 260))
            notch = t if notch is None else X.union(notch, t)
        X.diff(lip, X.tbm.copy(notch))
        keep = tb_copy(X, 'INNER_E'); inter(X, keep, X.tbm.copy(loc))
        X.diff(keep, inter(X, tb_copy(X, 'TOOL_inner_skin_0p9'), X.tbm.copy(loc)))
        old_cyl = ucat(X, [cyl_pn(X, p, n, 0.0, -3.0, 6.0) for (p, n) in old])
        t_rem = X.tbm.copy(old_cyl); inter(X, t_rem, X.tbm.copy(keep)); X.diff(t_rem, X.tbm.copy(lip))
        exp_rem = X.tbm.copy(t_rem); X.diff(exp_rem, X.tbm.copy(notch))
        X.diff(exp_rem, ucat(X, [cyl_pn(X, p, n, -1.2, -3.1, 4.15) for (p, n) in old]))     # the old lip pockets
        fill_lip = ucat(X, [cyl_pn(X, p, n, -1.1, -3.2, 4.25) for (p, n) in old]); inter(X, fill_lip, X.tbm.copy(lip))
        pads = ucat(X, [cyl_pn(X, p, n, 0.0, -3.0, 6.0) for (p, n) in new]); inter(X, pads, X.tbm.copy(keep))
        X.diff(pads, X.tbm.copy(notch))
        add_f = X.union(fill_lip, pads)
        cut_f = ucat(X, [cyl_pn(X, p, n, -1.2, -3.1, 4.15) for (p, n) in new])
        fill_d = ucat(X, [cyl_pn(X, p, n, 0.1, 2.6, 4.25) for (p, n) in old])
        inter(X, fill_d, tb_copy(X, 'TOOL_seam_wall')); X.diff(fill_d, tb_copy(X, 'TOOL_seam_RD'))
        cut_d = ucat(X, [cyl_pn(X, p, n, 0.2, 3.2, 4.15) for (p, n) in new])
        out['tool_cm3'] = {'t_rem': round(t_rem.volume, 4), 'fill_lip': round(fill_lip.volume, 4), 'pads': round(pads.volume, 4),
                           'fill_door': round(fill_d.volume, 4)}
        out['step'] = 'temp'
        fb = X.body('HOUSING_F_front'); db = X.body('HOUSING_F_door')
        v0 = {'front': round(fb.volume, 4), 'door': round(db.volume, 4)}
        out['removed_vs_expected_mm3'] = [vol_x(X, t_rem, fb), round(exp_rem.volume * 1000, 2)]
        fq = X.tbm.copy(fb); X.diff(fq, X.tbm.copy(t_rem)); X.union(fq, X.tbm.copy(add_f)); X.diff(fq, X.tbm.copy(cut_f))
        dq = X.tbm.copy(db); X.union(dq, X.tbm.copy(fill_d)); X.diff(dq, X.tbm.copy(cut_d))
        out['temp_cm3_lumps'] = {'front': [round(fq.volume, 4), fq.lumps.count], 'door': [round(dq.volume, 4), dq.lumps.count]}
        if fq.lumps.count != 1 or dq.lumps.count != 1:
            raise RuntimeError('temp result not one lump: %s' % out['temp_cm3_lumps'])
        out['step'] = 'combine'
        mode = {}

        def apply(name, ops, tq):
            b = X.body(name)
            try:
                for i, (tool, op) in enumerate(ops):
                    X.combine(b, [X.add(X.tbm.copy(tool), 'B6S4_%s%d_tmp' % (name[-4:], i))], op=op); b = X.body(name)
                mode[name] = 'combine'
            except Exception as e:
                for bb in [x for x in X.comp.bRepBodies if x.name.startswith('B6S4_') and x.name.endswith('_tmp')]:
                    bb.name = bb.name[:-4] + '_fail'; bb.isLightBulbOn = False
                b = X.body(name); app_, mat_ = b.appearance, b.material
                b.name = name + '_b6s3'; b.isLightBulbOn = False
                nb = X.add(tq, name)
                try:
                    nb.appearance = app_; nb.material = mat_
                except Exception:
                    pass
                mode[name] = 'replaced (%s)' % str(e)[:100]
        apply('HOUSING_F_front', [(t_rem, CUT), (add_f, JOIN), (cut_f, CUT)], fq)
        apply('HOUSING_F_door', [(fill_d, JOIN), (cut_d, CUT)], dq)
        out['mode'] = mode
        fb = X.body('HOUSING_F_front'); db = X.body('HOUSING_F_door')
        out['cm3'] = {'front': [v0['front'], round(fb.volume, 4)], 'door': [v0['door'], round(db.volume, 4)]}
        out['lumps'] = {'front': fb.lumps.count, 'door': db.lumps.count}
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        out['step'] = 'checks'
        out['front_x_door'] = vol_x(X, fb, db)
        ins = lambda b, p, n, k: b.pointContainment(qpt(p, n, k)) in INS
        mp = []
        for (p, n) in new:
            mp.append([not ins(db, p, n, 1.0), ins(db, p, n, -0.2), ins(db, p, n, -0.6), not ins(db, p, n, -0.8) and not ins(fb, p, n, -0.8),
                       ins(fb, p, n, -1.05), not ins(fb, p, n, -2.0)])
        out['magnet_probes_doorOpen1.0_skin-0.2_skin-0.6_gap-0.8_padSkin-1.05_lipOpen-2.0'] = mp
        out['magnet_probes_all_true'] = all(all(r) for r in mp)
        of = []
        for i, (p, n) in enumerate(old):
            pn, nn = new[i]
            v = adsk.core.Vector3D.create(p.x - pn.x, p.y - pn.y, p.z - pn.z)
            d = v.length * 10
            k = v.dotProduct(n); v = adsk.core.Vector3D.create(v.x - n.x * k, v.y - n.y * k, v.z - n.z * k); v.normalize()
            q = adsk.core.Point3D.create(p.x + v.x * 0.39, p.y + v.y * 0.39, p.z + v.z * 0.39)   # 3.9 from the old centre, away from the new
            of.append([round(d, 2), ins(db, q, n, 1.0), ins(fb, q, n, -1.6)])
        out['old_pockets_filled_[shift_mm, door_s1.0, lip_s-1.6]'] = of
        parts = current_parts(X)
        out['interference_mm3'] = {'HOUSING_F_front': hits_vs(X, fb, parts + [db]), 'HOUSING_F_door': hits_vs(X, db, parts)}
        g = X.body('GROMMET_usbc_F'); sweep = {}
        for dy in (1.0, 3.0, 10.0, 30.0, 80.0):
            q = X.tbm.copy(db); X.union(q, X.tbm.copy(g)); mvw(X, q, 0.0, -dy, 0.0)
            sweep[str(dy)] = vol_x(X, q, fb)
        out['door_sweep_vs_front_mm3'] = sweep
        out['step'] = 'done'
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b6s4_seam_magnets', 'build', out)
    print(json.dumps(out, separators=(',', ':')))
