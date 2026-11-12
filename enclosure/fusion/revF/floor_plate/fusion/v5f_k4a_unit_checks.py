# rev F k4a (2026-11-12): fix pass, block 4 - checks on the whole unit. Run through k.step(); the library is the global k.
#   Every check keeps its results in k.c under a tag (the model version) and stops when the call's time is used up:
#   call again until it reports nothing left. Nothing here changes the design: temporary bodies and measurements only.
#   way_in()    the plate unit lifted in from below, b behind its place (toward the door), against shell, radar board, BME680 parts
#   ride_in()   the display module, and the parts of the leads that ride with it, moved out along the screen's normal,
#               against the shell and the parts that are in the shell at that step
#   slide()     the left speaker box slid toward the screen on the plate, against the Pi, the USB plug, the lead and the plate
#   reach()     the rounded fingertip of 2026-11-11 (the audit's probe): ball of radius 8 on the mated plug's top, 60 long
#   matrix()    every current body against every other: boxes, then distance, then the overlap where they touch
#   chambers()  the air of both speaker boxes (g3a's method): closed or not, volume
import time
import adsk.core, adsk.fusion

STEPS = (0.5, 1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 35, 40, 50, 60)
LIFT = (80, 60, 40, 30, 20, 15, 10, 7, 5, 3, 2, 1, 0.5, 0)
BT = adsk.fusion.BooleanTypes


# ---------- pieces and crops, cached per tag (no volume reads of big bodies inside loops) ----------
def pieces(X, tag, name):
    q = ('k4p', tag, name)
    if q not in k.c:
        k.c[q] = list(k.parts(X, name))
    return k.c[q]


def sbox(p):                                         # slab-frame box of a temporary or model body [x0, x1, d0, d1, z0, z1]
    q = p.boundingBox; a = k.Sf(q.minPoint); e = k.Sf(q.maxPoint)
    return [min(a[0], e[0]), max(a[0], e[0]), min(a[1], e[1]), max(a[1], e[1]), min(a[2], e[2]), max(a[2], e[2])]


def crop(X, tag, name, box, frame='W'):              # the pieces of a body inside a world or slab-frame box
    q = ('k4c', tag, name, frame, tuple(round(v, 1) for v in box))
    if q not in k.c:
        bx = X.wbox(*box) if frame == 'W' else X.dbox(*box)
        out = []
        for p in pieces(X, tag, name):
            if not bx.boundingBox.intersects(p.boundingBox):
                continue
            t = X.tbm.copy(bx)
            X.tbm.booleanOperation(t, p, BT.IntersectionBooleanType)
            if t.faces.count > 0:
                out.append(t)
        k.c[q] = out
    return k.c[q]


def names_of(X, *keys):
    return [b.name for b in k.st(X, *keys)]


# ---------- 1. the plate unit's way in ----------
def way_in(X, tag, behind=(1.05, 1.3, 1.5), lift=LIFT, extra=()):
    res = k.c.setdefault(('k4way', tag), {})
    unit = names_of(X, 'UNIT', 'USBA') + list(extra)
    fixed = names_of(X, 'SHELL', 'RADAR', 'BME')
    left = 0
    for n in unit:
        for i, p in enumerate(pieces(X, tag, n)):
            todo = [(b, h) for b in behind for h in lift if (n, i, b, h) not in res]
            if not todo:
                continue
            if k.late():
                left += len(todo); continue
            qb = ('k4wb', tag, n, i)
            if qb not in k.c:
                k.c[qb] = k.wbb(X, p)
            wb = k.c[qb]
            box = (wb[0] - 1.0, wb[1] + 1.0, wb[2] - 2.6, wb[3] + 1.0, wb[4] - 81.0, wb[5] + 1.0)
            for b, h in todo:
                if k.late():
                    left += 1; continue
                t = X.move(X.tbm.copy(p), 0.0, -b, -h)
                hit = {}
                for f in fixed:
                    v = sum(X.xv(t, c) for c in crop(X, tag, f, box))
                    if abs(v) > 0.0005:
                        hit[f] = round(v, 3)
                res[(n, i, b, h)] = hit
    return res, left


# ---------- 2. the display module's ride-in ----------
LEADPART = {'LEAD_GPIO_A1': (-60.0, 60.0, -36.0, 36.0, -14.0, -1.0), 'LEAD_GPIO_A2': (-60.0, 60.0, -36.0, 36.0, -14.0, -1.0),
            'LEAD_GPIO_B': (-60.0, 60.0, -36.0, 36.0, -14.0, -1.0), 'LEAD_LCD_5V': (-60.0, 60.0, -36.0, 36.0, -14.0, -1.0),
            'LEAD_MIC_L': (-60.0, 60.0, -36.0, 36.0, -14.0, -1.0), 'LEAD_MIC_R': (-60.0, 60.0, -36.0, 36.0, -14.0, -1.0),
            'LEAD_DSI': (40.0, 62.0, -36.0, 36.0, -16.0, 10.0), 'LEAD_USB_RESP': (60.0, 95.0, -36.0, 36.0, -16.0, 6.0)}      # board frame


def leadpart(X, tag, name):
    q = ('k4lp', tag, name)
    if q not in k.c:
        t = X.bbox(*LEADPART[name])
        X.tbm.booleanOperation(t, k.tcopy(X, name), BT.IntersectionBooleanType)
        k.c[q] = t
    return k.c[q]


def ride_in(X, tag, steps=STEPS, leads=True, skip=()):
    res = k.c.setdefault(('k4ride', tag), {})
    moving = [(n, i, p) for n in names_of(X, 'MODULE') if n not in skip for i, p in enumerate(pieces(X, tag, n))]
    if leads:
        moving += [('part of ' + n, 0, leadpart(X, tag, n)) for n in sorted(LEADPART)]
    fixed = names_of(X, 'SHELL', 'UNIT', 'USBA', 'TOUCH', 'RADAR', 'BME')
    left = 0
    for n, i, p in moving:
        todo = [s for s in steps if (n, i, s) not in res]
        if not todo:
            continue
        if k.late():
            left += len(todo); continue
        if p.faces.count == 0:
            for s in todo:
                res[(n, i, s)] = {'no part in the box': 0.0}
            continue
        sb = sbox(p)
        box = (sb[0] - 1.0, sb[1] + 1.0, sb[2] - max(steps) - 1.0, sb[3] + 1.0, sb[4] - 1.0, sb[5] + 1.0)
        for s in todo:
            if k.late():
                left += 1; continue
            t = X.move_n(X.tbm.copy(p), s)
            hit = {}
            for f in fixed:
                v = sum(X.xv(t, c) for c in crop(X, tag, f, box, 'S'))
                if abs(v) > 0.0005:
                    hit[f] = round(v, 3)
            res[(n, i, s)] = hit
    return res, left


# ---------- 3. the left box sliding on ----------
def slide(X, tag, dist=(50, 45, 40, 35, 30, 25, 20, 15, 10, 8, 6, 5, 4, 3, 2, 1, 0),
          moving=('SPKBOX_L', 'SPK_L'),
          fixed=('FLOOR_PLATE', 'PI5_F', 'PI5_F_cooler', 'PIPWR_a_env', 'CRADLE_5807', 'PD_5807_env', 'USBA_plug_env', 'USBA_cable_env',
                 'LEAD_USB_RESP', 'SPKBOX_R', 'SPK_R')):
    res = k.c.setdefault(('k4slide', tag), {})
    for n in moving:
        p = k.tcopy(X, n)
        wb = k.wbb(X, p)
        box = (wb[0] - 1.0, wb[1] + 1.0, wb[2] - 1.0, wb[3] + max(dist) + 1.0, wb[4] - 1.0, wb[5] + 1.0)
        for d in dist:
            if (n, d) in res:
                continue
            t = X.move(X.tbm.copy(p), 0.0, float(d), 0.0)
            hit = {}
            for f in fixed:
                v = sum(X.xv(t, c) for c in crop(X, tag, f, box))
                if abs(v) > 0.0005:
                    hit[f] = round(v, 3)
            res[(n, d)] = hit
    return res


# ---------- 4. reach (the audit's probe, aud2_lib.py) ----------
TGT = {'J9 speaker right': ('B', -39.0, -25.0, 9.8), 'J8 speaker left': ('B', 38.75, -25.0, 9.8), 'J1 20 V': ('B', 0.0, -25.0, 9.8),
       'J6 touch': ('B', 12.3, -22.2, 9.8), 'J5 radar': ('B', -40.3, -13.85, 9.8), 'J10 BME680': ('B', -30.4, -14.11, 16.5),
       'J11 VEML6030': ('B', -0.69, -13.0, 16.5), 'J2 Pi power': ('B', 21.6, -40.5, 5.0),
       'Pi 1x3 (1-3-5)': ('W', -32.29, -6.71, 32.0), 'Pi 1x3 display': ('W', -32.29, -4.17, 32.0), 'Pi 2x5 (7-16)': ('W', -22.13, -5.45, 32.0),
       'Pi 2x3 (35-40)': ('W', 10.91, -5.45, 32.0), 'Pi DSI': ('W', 13.0, -50.0, 17.0)}
DIRS = {'straight': (0, 1, 0), 'down25': (0, 0.9063, -0.4226), 'down45': (0, 0.7071, -0.7071), 'up25': (0, 0.9063, 0.4226),
        'to-x25': (-0.4226, 0.9063, 0), 'to+x25': (0.4226, 0.9063, 0)}                                   # slab frame
PIDIRS = {'back30': (0, -0.5, 0.866), 'back45': (0, -0.7071, 0.7071), 'back60': (0, -0.866, 0.5), 'back45 to-x25': (-0.4226, -0.6409, 0.6409),
          'back45 to+x25': (0.4226, -0.6409, 0.6409)}                                                    # world
PLUGB = {'J9': (-43.24, -34.76, -28.95, -22.11, 9.8), 'J1': (-4.24, 4.24, -28.95, -22.11, 9.8), 'J6': (9.41, 16.24, -28.93, -15.45, 9.8),
         'J8': (34.50, 43.00, -28.95, -22.11, 9.8), 'J5': (-43.20, -36.36, -20.60, -7.11, 9.8), 'J10': (-32.22, -28.59, -19.74, -8.49, 16.5),
         'J11': (-6.31, 4.94, -14.82, -11.18, 16.5)}                     # rev 3.1, board frame u0, u1, v0, v1, mated height
RFIX = ['HOUSING_F_cap', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'PI5_F', 'PI5_F_cooler', 'CRADLE_5807', 'PD_5807_env', 'RESP_CARRIER', 'RESP_pcb',
        'RESP_top_env', 'RESP_usbc_plug_env', 'PIPWR_a_env', 'BME_HOOD', 'LD2410C_env_F', 'MAIN_pcb', 'MAIN_PS1', 'MAIN_PS1_tol', 'MAIN_tall', 'MAIN_low',
        'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'TOUCH_PCB', 'USBA_plug_env']
ORDER = [('Pi 1x3 (1-3-5)', []), ('Pi 2x5 (7-16)', []), ('Pi 2x3 (35-40)', []), ('Pi 1x3 display', []), ('Pi DSI', []),
         ('J9 speaker right', ['GPIO']), ('J8 speaker left', ['GPIO', 'J9']), ('J1 20 V', ['GPIO', 'J9', 'J8']),
         ('J6 touch', ['GPIO', 'J9', 'J8', 'J1']), ('J5 radar', ['GPIO', 'J9', 'J8', 'J1', 'J6']),
         ('J10 BME680', ['GPIO', 'J9', 'J8', 'J1', 'J6', 'J5']), ('J11 VEML6030', ['GPIO', 'J9', 'J8', 'J1', 'J6', 'J5', 'J10']),
         ('J2 Pi power', ['GPIO', 'J9', 'J8', 'J1', 'J6', 'J5', 'J10', 'J11'])]
ALLP = ['J9', 'J1', 'J6', 'J8', 'J5', 'J10', 'J11', 'J2', 'GPIO']


def finger(X, tipd, a, r, L=60.0):                   # rounded fingertip: ball of radius r at the tip, cylinder behind it (design frame)
    cc = k.P3(tipd.x + r / 10.0 * a.x, tipd.y + r / 10.0 * a.y, tipd.z + r / 10.0 * a.z)
    end = k.P3(tipd.x + L / 10.0 * a.x, tipd.y + L / 10.0 * a.y, tipd.z + L / 10.0 * a.z)
    tool = X.tbm.createCylinderOrCone(cc, r / 10.0, end, r / 10.0)
    X.tbm.booleanOperation(tool, X.tbm.createSphere(cc, r / 10.0), BT.UnionBooleanType)
    return tool


def reach(X, tag, tn, plugs, extra=(), r=8.0):       # {direction: {obstacle: mm3}}; a direction is free when its dict is empty
    res = k.c.setdefault(('k4reach', tag), {})
    key = (tn, tuple(sorted(plugs)), tuple(sorted(extra)), r)
    if key in res:
        return res[key]
    tg = TGT[tn]; pi = tg[0] == 'W'
    tip = k.Wp(*tg[1:]) if pi else k.Bp(*tg[1:])
    shell = crop(X, tag, 'HOUSING_F_front', (-110.0, 110.0, 18.0, 140.0, -115.0, 35.0), 'S')
    own = None
    if not pi:
        for pn, (u0, u1, v0, v1, h) in PLUGB.items():
            if u0 <= tg[1] <= u1 and v0 <= tg[2] <= v1:
                own = pn
    blocks = {}
    for pn, (u0, u1, v0, v1, h) in PLUGB.items():
        if pn in plugs and pn != own:
            blocks['plug ' + pn] = X.bbox(u0, u1, v0, v1, 0.0, h)
    names = list(RFIX) + list(extra)
    if 'J2' in plugs and not tn.startswith('J2'):
        names.append('MAIN_J2_plug_env')
    if 'GPIO' in plugs and not pi:
        names += ['GPIO_plugA_env', 'GPIO_plugB_env']
    out = {}
    for dn, d in (PIDIRS if pi else DIRS).items():
        if k.late():
            return None
        a = k.dv(d) if pi else k.V3(d[0], -d[1], d[2])
        tool = finger(X, tip, a, r)
        hit = {}
        v = sum(X.xv(tool, c) for c in shell)
        if abs(v) > 1.0:
            hit['shell'] = round(v)
        v = sum(X.xv(tool, c) for c in pieces(X, tag, 'FLOOR_PLATE'))
        if abs(v) > 1.0:
            hit['plate'] = round(v)
        for n in names:
            v = X.xv(tool, k.tcopy(X, n))
            if abs(v) > 1.0:
                hit[k.sn(n).replace('MAIN_', '')] = round(v)
        for n, b in blocks.items():
            v = X.xv(tool, b)
            if v > 1.0:
                hit[n] = round(v)
        out[dn] = hit
    res[key] = out
    return out


# ---------- 5. interference, every current body against every other ----------
def overlap(X, tag, a, b):
    A = pieces(X, tag, a.name) if a.name in k.BIG else [k.tcopy(X, a.name)]
    B = pieces(X, tag, b.name) if b.name in k.BIG else [k.tcopy(X, b.name)]
    if len(A) > 1 and len(B) == 1:
        A, B = B, A
    return sum(X.xv(p, q) for p in A for q in B)


def matrix(X, tag):
    B = k.current(X, leads=True)
    res = k.c.setdefault(('k4m', tag), {})
    e = 0.002
    left = 0
    for i, a in enumerate(B):
        qa = a.boundingBox
        box = adsk.core.BoundingBox3D.create(k.P3(qa.minPoint.x - e, qa.minPoint.y - e, qa.minPoint.z - e),
                                             k.P3(qa.maxPoint.x + e, qa.maxPoint.y + e, qa.maxPoint.z + e))
        for b in B[i + 1:]:
            q = (a.name, b.name)
            if q in res:
                continue
            if not box.intersects(b.boundingBox):
                res[q] = 0.0; continue
            if k.late():
                left += 1; continue
            d = X.mm.measureMinimumDistance(a, b).value * 10.0
            if d > 0.0005:
                res[q] = 0.0; continue
            if k.late():
                left += 1; continue
            res[q] = round(overlap(X, tag, a, b), 3)
    return res, left, len(B)


# ---------- 6. chambers (g3a's method) ----------
def chambers(X, boxes=(('SPKBOX_L', 'SPK_L', 1), ('SPKBOX_R', 'SPK_R', -1))):
    PCIN = adsk.fusion.PointContainment.PointInsidePointContainment
    out = {}
    for box, spk, sx in boxes:
        x0, x1 = sorted((sx * 40.0, sx * 101.0))
        Rb = [x0, x1, -60.0, 3.0, 1.0, 92.0]
        A = X.wbox(*Rb)
        X.dif(A, X.cp(X.body(box)))
        X.dif(A, X.wbox(Rb[0], Rb[1], -3.7, -3.0, Rb[4], Rb[5]))
        X.dif(A, X.cyl((sx * 62.0, -53.5, 30.0), (sx * 62.0, -49.0, 30.0), 2.2))
        pc = k.Wp(sx * 70.5, -30.0, 62.0)
        got = None
        for L in A.lumps:
            if L.pointContainment(pc) == PCIN:
                got = L; break
        if got is None:
            out[box] = 'no lump at the test point (%d lumps)' % A.lumps.count; continue
        t = X.cp(got)
        bb = k.wbb(X, t)
        s = X.cp(X.body(spk)); X.sec(s, X.cp(t))
        closed = all(abs(bb[j] - Rb[j]) > 0.05 for j in range(6))
        out[box] = {'upper cm3': round(X.vol(t) / 1000.0, 3), 'lower cm3': round((X.vol(t) - X.vol(s)) / 1000.0, 3), 'air box': bb, 'closed': closed,
                    'lumps': A.lumps.count}
    return out
