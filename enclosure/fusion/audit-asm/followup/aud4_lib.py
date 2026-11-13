# aud4_lib.py - assembly audit, follow-up (2026-11-13). Model "HA Panel v5 - tapered" version 62. READ-ONLY: temporary bodies,
# distances and booleans on copies; nothing in this file changes the design.
# Loaded into sys.modules['aud4'] inside Fusion. It uses the enclosure chat's libraries, loaded unchanged from docs commit fafa8fd under
# this audit's names (git blob hashes checked): v5f_k_lib.py as sys.modules['aud4k'] (k), v5f_m_lib.py as sys.modules['aud4m'] (m; its k
# is aud4k), and the namespaces of v5f_m1_behind_display.py and v5f_m2_rest.py in R['s1'] and R['s2']. Rebuilt from them, LEAD_DSI and
# LEAD_USB_RESP equal the model bodies to 0.000 mm3.
# World mm: x = x_rel (+x = viewer's left = left-speaker side), y + toward the screen, z up from the plate's underside.
# Board frame (u, v, w): u toward the left-speaker side, v up the board, w toward the door (w 0 = the main board's door-side face).
import adsk.core, adsk.fusion, math, sys, time
k = sys.modules['aud4k']; m = sys.modules['aud4m']
if 'R' not in globals():
    R = {}
BT = adsk.fusion.BooleanTypes
k.ST['USBA'] = ['USBA_plug_env']                      # USBA_cable_env is retired at version 62


def now(): return time.time()
def r2(q, n=2): return [round(v, n) for v in q]
def wdir(q): return m.unit((q[0], -k.C * q[1] - k.S * q[2], -k.S * q[1] + k.C * q[2]))     # slab-frame direction (x, depth, Zd) -> world


def gap(X, a, b):                                     # smallest distance between two bodies (model or temporary): mm, point on a, point on b
    r = X.mm.measureMinimumDistance(a, b)
    return r.value * 10.0, k.W(r.positionOne), k.W(r.positionTwo)


def tl(X, name):                                      # temporary pieces of a model body; big bodies as the eight slabs (k.parts)
    q = ('tl', name)
    if q not in R:
        R[q] = list(k.parts(X, name))
    return R[q]


def crop(X, name, key, box, frame='W'):               # cached crop of a model body to a world ('W'), slab ('S') or board ('B') box
    q = ('crop', key)
    if q in R:
        return R[q]
    out = []
    for p in tl(X, name):
        bx = X.wbox(*box) if frame == 'W' else (X.dbox(*box) if frame == 'S' else X.bbox(*box))
        if not bx.boundingBox.intersects(p.boundingBox):
            continue
        X.tbm.booleanOperation(bx, p, BT.IntersectionBooleanType)
        if X.vol(bx) > 0.001:
            out.append(bx)
    R[q] = out
    return out


def items(X, names=(), crops=(), temps=()):           # obstacles as (label, body, design box)
    out = []
    for n in names:
        for b in (k.st(X, n) if n in k.ST else k.present(X, [n])):
            if b.name in k.BIG:
                raise RuntimeError('use a crop for ' + b.name)
            out.append((k.sn(b.name), b, m.bb6(b)))
    for key in crops:
        out += [(key, t, m.bb6(t)) for t in R[('crop', key)]]
    out += [(lab, t, m.bb6(t)) for lab, t in temps]
    return out


def mingap(X, mb, fixed, lim=3.0):                    # (mm, label, point on mb, point on the obstacle) of the nearest obstacle within lim, or None
    q = m.bb6(mb); best = None
    for fl, fb, fq in fixed:
        if m.bgap(q, fq) > lim:
            continue
        g, a, e = gap(X, mb, fb)
        if best is None or g < best[0]:
            best = (round(g, 3), fl, r2(a), r2(e))
    return best


def vol_in(X, mb, fixed, eps=0.002):                  # {label: mm3 of mb inside it}
    out = {}
    for fl, fb, fq in fixed:
        if not mb.boundingBox.intersects(fb.boundingBox):
            continue
        v = X.xv(mb, fb)
        if abs(v) > eps:
            out[fl] = round(out.get(fl, 0.0) + v, 3)
    return out


def mv(X, tb, d):
    t = X.tbm.copy(tb); return X.move(t, d[0], d[1], d[2])


def mvn(X, tb, s):
    t = X.tbm.copy(tb); return X.move_n(t, s)


def lumps(X, a, b, n=3):                              # the largest common lumps of two temporary bodies: [mm3, world box]
    t = X.tbm.copy(a); X.tbm.booleanOperation(t, b, BT.IntersectionBooleanType)
    return X.lumps(t)[:n]


# ---------- strips ----------
def sframes(s):                                       # label -> (op, d, w, n) at the op's start; n is face A's normal
    return {lab: (op, d, w, m.cross(d, w)) for lab, op, L, P, d, w in s.log}


def sclear(X, s, obs, lim=3.0, only=None, skip=()):   # per obstacle: [mm, piece, face/edge/corner (straight pieces only), point on the strip, point on it]
    fr = sframes(s); out = {}
    pcs = [(lab, p, m.bb6(p)) for lab, p in s.pieces if (only is None or lab.split('.')[0] in only) and lab.split('.')[0] not in skip]
    for name, bodies in obs:
        best = None
        for b in bodies:
            qb = m.bb6(b)
            for lab, p, qp in pcs:
                if m.bgap(qp, qb) > lim:
                    continue
                g, a, e = gap(X, p, b)
                if best is None or g < best[0]:
                    best = [g, lab, a, e]
        if best is None or best[0] > lim:
            continue
        g, lab, a, e = best; kind = ''
        f = fr.get(lab)
        if f is not None and f[0] == 'S' and g > 0.01:
            cth = abs(m.dot(m.unit(m.sub(e, a)), f[3]))
            kind = 'face' if cth > 0.8 else ('edge' if cth < 0.3 else 'corner')
        out[name] = [round(g, 2), lab, kind, r2(a, 1), r2(e, 1)]
    return out


def stable(res, n=40):
    rows = sorted(res.items(), key=lambda t: t[1][0])
    return '\n'.join('  %-24s %6.2f  %-26s %-6s strip %s  obst %s' % (k.sn(q)[:24], v[0], v[1], v[2], v[3], v[4]) for q, v in rows[:n])


def obs(X, skip=(), leads=True, kos=True):            # every current body (big ones as the strip library's crops), less skip; key paths optional
    out = m.obstacles(X, skip=skip, leads=leads)
    if out is None:
        raise RuntimeError('crops of the big bodies not finished: call again')
    if not kos:
        out = [(n, b) for n, b in out if not n.startswith('KO_')]
    return out


def piece_body(s, labels):                            # one temporary body of the strip's pieces whose base label is in labels
    X = s.X; t = None
    for lab, p in s.pieces:
        if lab.split('.')[0] in labels:
            t = X.cp(p) if t is None else X.uni(t, X.cp(p))
    return t


# ---------- ride-in of the display module ----------
STEPS = (0.5, 1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 35, 40, 50, 60)
LOW = (-60.0, 60.0, -32.9, 36.0, -14.0, -1.0)
LEADPART = {'LEAD_GPIO_A1': LOW, 'LEAD_GPIO_A2': LOW, 'LEAD_GPIO_B': LOW, 'LEAD_LCD_5V': LOW,
            'LEAD_MIC_R': (-36.0, -26.5, -36.0, 32.9, -14.0, -1.0), 'LEAD_MIC_L': (31.0, 39.0, -36.0, 32.9, -14.0, -1.0),
            'LEAD_DSI': (35.0, 52.0, -20.0, 20.0, -26.0, 32.0), 'LEAD_USB_RESP': (36.0, 52.0, -5.0, 20.0, -16.0, 36.0)}


def ride_setup(X):
    if 'ride_mov' in R:
        return
    crop(X, 'HOUSING_F_front', 'rideS', (-100, 100, 4, 80, -80, 30), 'S')
    mov = []
    for b in k.st(X, 'MODULE'):
        ps = tl(X, b.name)
        for i, p in enumerate(ps):
            mov.append((b.name if len(ps) == 1 else '%s#%d' % (b.name, i), p))
    for n in sorted(LEADPART):
        t = X.bbox(*LEADPART[n]); X.sec(t, tl(X, n)[0])
        mov.append(('part of ' + n, t))
    R['ride_mov'] = mov
    R['ride_fix'] = items(X, names=['PI', 'PIPWR', 'CRADLE', 'INLET', 'BOXES', 'USBA', 'TOUCH', 'RADAR', 'BME'], crops=['rideS'])


def ride(X, t0, lim=45.0, steps=STEPS, tag='ride'):
    res = R.setdefault(tag, {}); left = 0
    fx = R['ride_fix']
    for lab, p in R['ride_mov']:
        for s in steps:
            if (lab, s) in res:
                continue
            if now() - t0 > lim:
                left += 1; continue
            t = mvn(X, p, s)
            g = mingap(X, t, fx, 3.0)
            if g is not None and g[0] < 0.005:
                g = g + (vol_in(X, t, fx, 0.0005),)
            res[(lab, s)] = g
    return left


# ---------- the left speaker box sliding on ----------
SLIDE = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 50.0)


def slide_setup(X):
    if 'slide_mov' in R:
        return
    hd = crop(X, 'DRV_screw_heads_env', 'headsL', (0, 110, -100, 30, -6, 190))
    R['slide_mov'] = [('SPKBOX_L', tl(X, 'SPKBOX_L')[0]), ('SPK_L', tl(X, 'SPK_L')[0])] + [('heads L', t) for t in hd]
    crop(X, 'LEAD_USB_RESP', 'cable_low', (40.0, 75.0, -62.0, -20.0, 5.0, 52.0))
    crop(X, 'FLOOR_PLATE', 'plateL', (30, 100, -90, 10, -1, 14))
    R['slide_fix'] = items(X, names=['USBA_plug_env', 'PI5_F', 'PI5_F_cooler', 'PIPWR_a_env'], crops=['cable_low', 'plateL'])


def slide(X, t0, lim=45.0):
    res = R.setdefault('slide', {}); left = 0
    for lab, p in R['slide_mov']:
        for s in SLIDE:
            if (lab, s) in res:
                continue
            if now() - t0 > lim:
                left += 1; continue
            t = mv(X, p, (0.0, s, 0.0))
            g = mingap(X, t, R['slide_fix'], 3.0)
            if g is not None and g[0] < 0.005:
                g = g + (vol_in(X, t, R['slide_fix'], 0.0005),)
            res[(lab, s)] = g
    return left


# ---------- reach (the standard of 2026-11-11: rounded fingertip 16 across, 60 long, six directions, blocked above 1 mm3) ----------
TGT = {'J8 speaker left': ('B', 38.75, -25.0, 9.8), 'J9 speaker right': ('B', -39.0, -25.0, 9.8), 'J1 20 V': ('B', 0.0, -25.0, 9.8),
       'J6 touch': ('B', 12.3, -22.2, 9.8), 'J2 Pi power': ('B', 21.6, -40.5, 5.0), 'Pi DSI': ('W', 13.0, -50.0, 17.0),
       'Pi 2x3 (35-40)': ('W', 10.91, -5.45, 32.0)}
DIRS = {'straight': (0, 1, 0), 'down25': (0, 0.9063, -0.4226), 'down45': (0, 0.7071, -0.7071), 'up25': (0, 0.9063, 0.4226),
        'to-x25': (-0.4226, 0.9063, 0), 'to+x25': (0.4226, 0.9063, 0)}                         # slab frame, from the tip back along the finger
PIDIRS = {'back30': (0, -0.5, 0.866), 'back45': (0, -0.7071, 0.7071), 'back60': (0, -0.866, 0.5), 'back45 to-x25': (-0.4226, -0.6409, 0.6409),
          'back45 to+x25': (0.4226, -0.6409, 0.6409)}                                           # world
PLUGB = {'J9': (-43.24, -34.76, -28.95, -22.11, 9.8), 'J1': (-4.24, 4.24, -28.95, -22.11, 9.8), 'J6': (9.41, 16.24, -28.93, -15.45, 9.8),
         'J8': (34.50, 43.00, -28.95, -22.11, 9.8), 'J5': (-43.20, -36.36, -20.60, -7.11, 9.8), 'J10': (-32.22, -28.59, -19.74, -8.49, 16.5),
         'J11': (-6.31, 4.94, -14.82, -11.18, 16.5)}                                           # rev 3.1, board frame u0, u1, v0, v1, mated height
RFIX = ['HOUSING_F_cap', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'PI5_F', 'PI5_F_cooler', 'CRADLE_5807', 'PD_5807_env', 'RESP_CARRIER', 'RESP_pcb',
        'RESP_top_env', 'RESP_usbc_plug_env', 'PIPWR_a_env', 'BME_HOOD', 'LD2410C_env_F', 'MAIN_pcb', 'MAIN_PS1', 'MAIN_PS1_tol', 'MAIN_tall', 'MAIN_low',
        'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'TOUCH_PCB', 'USBA_plug_env']


def finger(X, tip, a, r=8.0, L=60.0):                 # rounded tip at 'tip' (world); a = direction from the tip back along the finger (world)
    a = m.unit(a); cc = m.add(tip, m.mul(a, r)); end = m.add(tip, m.mul(a, L))
    t = X.cyl(cc, end, r); return X.uni(t, X.sph(cc, r))


def reach_obs(X, tn, plugs, leads=()):                # leads: [(label, temporary body)]
    tg = TGT[tn]; pi = tg[0] == 'W'
    sh = crop(X, 'HOUSING_F_front', 'reachS', (-110, 110, 18, 140, -115, 35), 'S')
    fixed = [('shell', t) for t in sh] + [('plate', t) for t in tl(X, 'FLOOR_PLATE')]
    own = None
    if not pi:
        for pn, (u0, u1, v0, v1, h) in PLUGB.items():
            if u0 <= tg[1] <= u1 and v0 <= tg[2] <= v1:
                own = pn
    for pn, (u0, u1, v0, v1, h) in PLUGB.items():
        if pn in plugs and pn != own:
            fixed.append(('plug ' + pn, X.bbox(u0, u1, v0, v1, 0.0, h)))
    names = list(RFIX)
    if 'J2' in plugs and not tn.startswith('J2'):
        names.append('MAIN_J2_plug_env')
    if 'GPIO' in plugs and not pi:
        names += ['GPIO_plugA_env', 'GPIO_plugB_env']
    fixed += [(k.sn(n).replace('MAIN_', ''), tl(X, n)[0]) for n in names]
    fixed += list(leads)
    return fixed


def reach(X, tn, plugs, leads=(), r=8.0, L=60.0, dirs=None, tip=None, skip=()):   # {direction: {obstacle: mm3}}; free = empty dict
    tg = TGT[tn]; pi = tg[0] == 'W'
    if tip is None:
        tip = tuple(tg[1:]) if pi else k.B2W(*tg[1:])
    fixed = [f for f in reach_obs(X, tn, plugs, leads) if f[0] not in skip]
    out = {}
    for dn, d in (dirs or (PIDIRS if pi else DIRS)).items():
        a = d if pi else wdir(d)
        tool = finger(X, tip, a, r, L)
        hit = {}
        for n, b in fixed:
            if not tool.boundingBox.intersects(b.boundingBox):
                continue
            v = X.xv(tool, b)
            if abs(v) > 1.0:
                hit[n] = round(hit.get(n, 0.0) + v, 1)
        out[dn] = hit
    return out


def freedirs(res): return [d for d, h in res.items() if not h]


# ---------- pliers and tweezers on the ReSpeaker's USB-C plug (service) ----------
PL = {'u0': 43.70, 'u1': 47.10, 'v0': 3.51, 'v1': 10.91, 'wtop': 4.31, 'v': 7.21}   # sleeve's middle part (7.4 across), board frame; plug seated


def jaws(X, a, th=2.5, wd=3.0, L=70.0, wtip=1.0, shift=0.0, body=None):
    # two jaws th thick (along v) and wd wide (along u), straddling the sleeve's middle part 0.2 off its narrow edges, tips at w = wtip, lying
    # along a (world, from the tips back toward the hand). body: the nose, joint and handles of long-nose pliers as an envelope behind the jaws
    uc = (PL['u0'] + PL['u1']) / 2.0 + shift
    ux = m.bdir(1, 0, 0); ay = m.unit(m.sub(ux, m.mul(a, m.dot(ux, a))))
    tool = None
    for vc in (PL['v0'] - 0.2 - th / 2.0, PL['v1'] + 0.2 + th / 2.0):
        p0 = k.B2W(uc, vc, wtip)
        j = X.obox(m.add(p0, m.mul(a, L / 2.0)), a, ay, L, wd, th)
        tool = j if tool is None else X.uni(tool, j)
    if body:
        pc = k.B2W(uc, PL['v'], wtip)
        for s0, s1, ww, tt in body:                   # (from, to, width along u, thickness along v) of the envelope behind the jaws
            q = X.obox(m.add(pc, m.mul(a, (s0 + s1) / 2.0)), a, ay, s1 - s0, ww, tt)
            tool = X.uni(tool, q)
    return tool


PLIERS = [(55.0, 75.0, 8.0, 14.0), (75.0, 95.0, 14.0, 16.0), (95.0, 165.0, 16.0, 45.0)]      # assumed: nose, joint, handles spread 45
TWEEZ = [(40.0, 120.0, 8.0, 12.0)]                                                              # assumed: the two legs behind the tips


def hits(X, tool, fixed, eps=0.05):
    out = {}
    for n, b in fixed:
        if not tool.boundingBox.intersects(b.boundingBox):
            continue
        v = X.xv(tool, b)
        if v > eps:
            out[n] = round(out.get(n, 0.0) + v, 2)
    return out


PLATE_UNIT = ['FLOOR_PLATE', 'PI5_F', 'PI5_F_cooler', 'PIPWR_a_env', 'CRADLE_5807', 'PD_5807_env', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R',
              'DRV_screw_heads_env', 'USBA_plug_env', 'LEAD_SPK_L', 'LEAD_SPK_R', 'LEAD_PIGTAIL_20V', 'LEAD_PI_POWER', 'FOOT_*']


def service_fixed(X, h, b=1.5, box=(10, 110, -100, 0, -40, 140)):
    # everything that stays with the shell (shell, door off), plus the plate unit moved b behind and h lower; crops to a world box round the
    # plug's side of the unit. The plug, its cable and the door are left out.
    key = ('svc', h, b)
    if key in R:
        return R[key]
    cur = [x for x in k.current(X, leads=True)]
    names_unit = set()
    for n in PLATE_UNIT:
        if n.endswith('*'):
            names_unit |= {x.name for x in cur if x.name.startswith(n[:-1])}
        else:
            names_unit.add(n)
    out = []
    for x in cur:
        n = x.name
        if n in ('RESP_usbc_plug_env', 'LEAD_USB_RESP', 'HOUSING_F_door', 'GROMMET_usbc_F') or n.startswith('KO_'):
            continue
        ps = crop(X, n, ('svcbox', n), box) if n in k.BIG else [k.tcopy(X, n)]
        for p in ps:
            if n in names_unit:
                if h or b:
                    p = mv(X, p, (0.0, -b, -h))
            out.append((k.sn(n), p))
    R[key] = out
    return out


# ---------- the cable's spare: three plain lanes (temporary strip) ----------
def lanes3(X, Lc, zbot=14.53, Rt=4.0, Rq=5.5, Re=4.0, gp=0.5):
    s1 = R['s1']; s2 = R['s2']; pv = s1['PV']; p2 = s2['P2']
    q = s2['lanes'](pv, p2); ct = pv['ct']
    xC = q['F']; xB = xC + 2 * Rt; xA = xB + 2 * Rt

    def build(Xb, ztop):
        s = s1['cable'](Xb, pv, full=False); s.log.pop()
        s.F(s1['DOWN'], -1, +1, pv['cgap'], 'fold down')
        zrow = ztop + Rt + ct + gp
        s.S(s.P[2] - (zrow + Rq), 'drop')
        s.B(90, Rq, 'bend outward')
        s.S((xA - Re) - s.P[0], 'row')
        s.B(-90, Re, 'into lane A')
        s.S(s.P[2] - zbot, 'lane A down')
        s.B(-180, Rt, 'turn below')
        s.S(ztop - zbot, 'lane B up')
        s.B(180, Rt, 'turn above')
        s.S(s.P[2] - p2['zport'], 'lane C down')
        turn = 1 if m.dot(s.w, (0, 1, 0)) > 0 else -1
        side = 1 if m.dot(s.n, (-1, 0, 0)) > 0 else -1
        s.F(45, turn, side, pv['cgap'], 'fold at the bottom')
        s.S((p2['yport'] - 19.73) - s.P[1], 'to the plug')
        return s.end()
    L0 = build(s2['Dry'](), 30.0).L; L1 = build(s2['Dry'](), 40.0).L
    ztop = 30.0 + (Lc - L0) * 10.0 / (L1 - L0)
    s = build(X, ztop); s.ztop = ztop; s.lanes = (xA, xB, xC)
    return s


def roll(X, Lc):                                      # the drawn roll with the lane length that makes the cable Lc long
    s2 = R['s2']; p2 = dict(s2['P2']); p2['Lc'] = Lc
    return s2['cable'](X, None, p2)
