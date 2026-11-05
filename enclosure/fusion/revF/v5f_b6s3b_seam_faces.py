# rev F block 6 / seam (b), option I – B6s-3b (2026-11-05): finishes B6s-3.
#   B6s-3 run 3 (10:19) cut the door with D = A + 1.7 u (53.536 → 50.799 cm³, 1 lump) but the front JOIN of the gain
#   (wall ∩ RF ∩ y < −54.9) failed (ASM_BAD_CONTAINMENT: the 0.1 overlap shares the wall's inner and outer surfaces with
#   the front). Its leftover B6S3_gain_tmp → TOOL_seam_gain_fail3 (hidden); TOOL_seam_RF / _RD → *_r3 (hidden).
#   Here: front face F = A + 0.2 u (so F meets y −55.0 inside the cavity, not on the s −0.7 surface: no zero-thickness
#   wedge, the gain touches the front's end face y −55.0 face to face), door face D = A + 1.9 u (gap 1.7 kept: a 0.2
#   slice comes off the door). Wall profile from z 2.4 so the gain overlaps the floor rim by 0.1 instead of touching it.
#   New hidden tools TOOL_seam_RF (A + 0.2 u), TOOL_seam_RD (A + 1.9 u). Magnets (B6s-4) move 0.2 further along u.
#   The front + gain union is tried as TemporaryBRep first (before the door slice); if the JOIN feature still fails, that
#   union replaces the body (old → HOUSING_F_front_b6s3, hidden).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
Y0 = -55.0
SEAM = os.path.expanduser('~/Documents/v5f_seam_I.json')
EXPECT = {'HOUSING_F_front': 237.930, 'HOUSING_F_door': 50.799}
DF, DD = 0.2, 1.9                  # front face A + 0.2 u, door face A + 1.9 u (gap 1.7)
SKIP_PREFIX = ('HOUSING_F', 'HOUSING_E', 'REF_', 'INNER_', 'TOOL_', 'V11', 'RENDER_', 'sk_')
SKIP_SUFFIX = ('_b4n', '_b4d', '_b1', '_b2', '_b5', '_b6v1', '_revE', '_revD', '_tmp', '_wip', '_r2', '_fail1', '_fail3', '_r3')
STALE = ('HOUSING_shell', 'DOOR_tray', 'REF_outer_hidden', 'DOOR_plate', 'DOOR_F', 'GROMMET_usbc', 'TOUCH_pcb', 'LD2410C_env',
         'SENSOR_strip_L', 'SENSOR_strip_R', 'SPK_driver_D40', 'PD_trigger_env_20V')


def vsub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def vadd(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def vmul(a, k): return (a[0] * k, a[1] * k, a[2] * k)
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def unit(a):
    l = math.sqrt(dot(a, a)); return (a[0] / l, a[1] / l, a[2] / l)
def dist(a, b): return math.sqrt(dot(vsub(a, b), vsub(a, b)))


def load_stations(min_gap=2.0):
    raw = json.load(open(SEAM))['raw']
    for s in raw:
        for k in ('P', 'n', 'A', 'Q', 'B'):
            s[k] = tuple(s[k])
    st = [raw[0]]
    for s in raw[1:-1]:
        if dist(s['P'], st[-1]['P']) >= min_gap:
            st.append(s)
    if dist(raw[-1]['P'], st[-1]['P']) < 1.0:
        st.pop()
    st.append(raw[-1])
    for k, s in enumerate(st):
        a = st[max(k - 1, 0)]['P']; b = st[min(k + 1, len(st) - 1)]['P']
        t = unit(vsub(b, a)); n = s['n']
        u = unit(cross(t, n))
        if u[1] > 0:
            u = vmul(u, -1.0)
        tp = unit(cross(n, u))
        if dot(tp, t) < 0:
            tp = vmul(tp, -1.0)
        s['u'] = u; s['t'] = tp
        s['a'] = 8.0 if k == 0 else dist(s['P'], st[k - 1]['P']) / 2 + 0.4
        s['b'] = 8.0 if k == len(st) - 1 else dist(s['P'], st[k + 1]['P']) / 2 + 0.4
        s['odd'] = k % 2
    return st


def half_box(X, O, s):
    u, t, n = s['u'], s['t'], s['n']
    L, s0, s1 = (21.0, -3.9, 5.4) if s['odd'] else (20.0, -3.5, 5.0)
    c = vadd(vadd(vadd(O, vmul(u, -L / 2)), vmul(t, (s['b'] - s['a']) / 2)), vmul(n, (s0 + s1) / 2))
    return X.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(Dw(XC + c[0], c[1], c[2]), wv(u), wv(t),
                                                                  L / 10, (s['a'] + s['b']) / 10, (s1 - s0) / 10))


def union_all(X, bs):
    while len(bs) > 1:
        nb = []
        for i in range(0, len(bs) - 1, 2):
            X.tbm.booleanOperation(bs[i], bs[i + 1], B.UnionBooleanType); nb.append(bs[i])
        if len(bs) % 2:
            nb.append(bs[-1])
        bs = nb
    return bs[0]


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
        if qa.volume * 1000 > 0.005:
            hits[o.name] = round(qa.volume * 1000, 2)
    return hits or 'all 0'


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.002:
                raise RuntimeError('guard: %s volume %s, expected %s' % (k, None if b is None else round(b.volume, 3), v))
        if X.body('TOOL_seam_RD_r3') is not None:
            raise RuntimeError('B6s-3b ran already')
        g3 = X.body('B6S3_gain_tmp')
        if g3 is not None:
            g3.name = 'TOOL_seam_gain_fail3'; g3.isLightBulbOn = False
        for nm in ('TOOL_seam_RF', 'TOOL_seam_RD'):
            b = X.body(nm)
            if b is not None:
                b.name = nm + '_r3'; b.isLightBulbOn = False
        out['step'] = 'regions'
        st = load_stations()
        out['n_stations'] = len(st)
        RF = union_all(X, [half_box(X, vadd(s['A'], vmul(s['u'], DF)), s) for s in st])
        RD = union_all(X, [half_box(X, vadd(s['A'], vmul(s['u'], DD)), s) for s in st])
        out['regions_cm3_lumps'] = [round(RF.volume, 3), RF.lumps.count, round(RD.volume, 3), RD.lumps.count]
        if RF.lumps.count != 1 or RD.lumps.count != 1:
            raise RuntimeError('RF / RD not one lump: %s' % out['regions_cm3_lumps'])
        out['step'] = 'wall'
        LB = X.wbox(-250, 250, -64.0, -50.0, 2.4, 260)
        crop = lambda nm: inter(X, tb_copy(X, nm), X.wbox(-250, 250, -66.0, -48.0, 0.0, 260))
        W = tb_copy(X, 'REF_F_outer'); inter(X, W, X.tbm.copy(LB)); X.diff(W, crop('INNER_E'))
        Li = tb_copy(X, 'TOOL_inner_skin_0p7'); inter(X, Li, X.wbox(-250, 250, -64.0, -50.0, 2.5, TOP_Z))
        Lc = tb_copy(X, 'TOOL_outer_skin_3p2'); inter(X, Lc, X.wbox(-250, 250, -64.0, -50.0, 2.5, 6.2))
        X.diff(Lc, crop('TOOL_floor_off6'))
        X.union(W, Li); X.union(W, Lc); X.diff(W, crop('TOOL_outer_skin_0p7'))
        out['wall_cm3'] = round(W.volume, 3)
        out['step'] = 'gain'
        gain = X.tbm.copy(W); inter(X, gain, X.tbm.copy(RF)); inter(X, gain, X.wbox(-250, 250, -64.0, Y0, 2.4, 260))
        out['gain_cm3'] = round(gain.volume, 3); out['gain_lumps'] = gain.lumps.count
        out['step'] = 'front_test'
        fb = X.body('HOUSING_F_front')
        ft = X.tbm.copy(fb); X.tbm.booleanOperation(ft, X.tbm.copy(gain), B.UnionBooleanType)
        out['front_test_cm3_lumps'] = [round(ft.volume, 4), ft.lumps.count]
        out['step'] = 'slice'
        cut = X.tbm.copy(RD); inter(X, cut, X.wbox(-250, 250, -64.0, -50.0, -10.0, 260))
        out['step'] = 'tools'
        for nm, tb in (('TOOL_seam_RF', RF), ('TOOL_seam_RD', RD)):
            hb = X.add(X.tbm.copy(tb), nm); hb.isLightBulbOn = False
        out['step'] = 'door'
        fb = X.body('HOUSING_F_front'); db = X.body('HOUSING_F_door')
        v0 = {'front': round(fb.volume, 4), 'door': round(db.volume, 4)}
        out['slice_mm3'] = vol_x(X, cut, db)
        X.combine(db, [X.add(cut, 'B6S3B_cut_tmp')], op=CUT); db = X.body('HOUSING_F_door')
        out['gain_x_door_mm3'] = vol_x(X, gain, db)
        out['gain_x_front_mm3'] = vol_x(X, gain, fb)
        gb = X.add(gain, 'B6S3B_gain_tmp')
        out['gain_vs_parts_mm3'] = hits_vs(X, gb, current_parts(X) + [db])
        out['step'] = 'front'
        try:
            X.combine(fb, [gb]); fb = X.body('HOUSING_F_front'); out['front_mode'] = 'combine'
        except Exception as e:                 # fallback: the TemporaryBRep union replaces the body (old one kept hidden)
            out['combine_err'] = str(e)[:160]
            tb_ = X.body('B6S3B_gain_tmp')
            if tb_ is not None:
                tb_.name = 'TOOL_seam_gain_fail3b'; tb_.isLightBulbOn = False
            fb.name = 'HOUSING_F_front_b6s3'; fb.isLightBulbOn = False
            fb = X.add(ft, 'HOUSING_F_front'); out['front_mode'] = 'replaced'
        out['cm3'] = {'front': [v0['front'], round(fb.volume, 4)], 'door': [v0['door'], round(db.volume, 4)]}
        out['lumps'] = {'front': fb.lumps.count, 'door': db.lumps.count}
        out['front_x_door'] = vol_x(X, fb, db)
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        out['step'] = 'checks'
        probes = []
        idx = [int(round(i * (len(st) - 1) / 9.0)) for i in range(10)]
        mid = (DF + DD) / 2
        for k in idx:
            s = st[k]
            row = [round(s['P'][0], 1), round(s['P'][2], 1)]
            for sd in (0.3, 1.5):
                m = vadd(vadd(s['A'], vmul(s['u'], mid)), vmul(s['n'], sd + 0.7))
                hf = [h for h in ray_hits(X, (XC + m[0], m[1], m[2]), vmul(s['u'], -1.0), ('HOUSING_F_front',))]
                hd = [h for h in ray_hits(X, (XC + m[0], m[1], m[2]), s['u'], ('HOUSING_F_door',))]
                f = hf[0] if hf else None; d = hd[0] if hd else None
                ang = lambda h: round(math.degrees(math.acos(min(1.0, abs(dot(unit(h[5]), s['u']))))), 1)
                row += [round(f[0], 2) if f else None, ang(f) if f else None, round(d[0], 2) if d else None, ang(d) if d else None]
            probes.append(row)
        out['gap_probes_xrel_z__s0.3_tF_angF_tD_angD__s1.5_tF_angF_tD_angD'] = probes
        g = X.body('GROMMET_usbc_F'); sweep = {}
        for dy in (1.0, 3.0, 10.0, 30.0, 80.0):
            q = X.tbm.copy(db); X.union(q, X.tbm.copy(g)); mvw(X, q, 0.0, -dy, 0.0)
            sweep[str(dy)] = vol_x(X, q, fb)
        out['door_sweep_vs_front_mm3'] = sweep
        out['step'] = 'done'
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b6s3b_seam_faces', 'build', out)
    print(json.dumps(out, separators=(',', ':')))
