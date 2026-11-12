# Assembly audit, second pass (2026-11-12) - library, exec'd into sys.modules['aud2'] inside Fusion (read-only use).
# World mm: x = x_rel (+x = viewer's left), y + toward the viewer, z up from the plate's underside. Slab frame (x_rel, depth, Zd).
# Board frame (u, v, w) of the site document. Nothing here changes the design: temporary bodies and measurements only.
import adsk.core, adsk.fusion, math, re, sys, time, json
C = math.cos(math.radians(12.0)); S = math.sin(math.radians(12.0)); H = 143.3; XC = -2.55
U0, V0, D0 = 2.5, -27.45, 32.7
P3 = adsk.core.Point3D.create; V3 = adsk.core.Vector3D.create
BT = adsk.fusion.BooleanTypes
CYL = adsk.core.SurfaceTypes.CylinderSurfaceType
BACK = re.compile('(_v[0-9]+|_[a-e][0-9]+[a-z0-9]*| [(][0-9]+[)])$')
LEGACY = ('DOOR_tray', 'HOUSING_E', 'HOUSING_shell', 'HOUSING_F_wip', 'AMP_env_20x20x10', 'BUCK_20to5V_env_43x25x13', 'DOOR_plate_revE', 'GROMMET_usbc',
          'HOUSING_F_front_d10_sliver', 'HOUSING_F_front_d12a_sliver1', 'LD2410C_env', 'MAIN_BRACKET_d1split_L', 'MAIN_BRACKET_d1split_R',
          'MAIN_BRACKET_d1split_plug', 'PD_trigger_env_20V', 'PI5_board', 'SPKBOX_L_r2', 'SPK_driver_D40', 'V11a_mx', 'V11a_px', 'V11a_up', 'V11b_mx',
          'V11b_px', 'V11b_up', 'V11c_straight', 'VOICEPE_back_env', 'VOICEPE_encoder_env', 'VOICEPE_pcb', 'BME680_env_revD', 'TOUCH_pcb_100x44')
NOTPART = ('REF_', 'TOOL_', 'INNER', 'RENDER_', 'AUD_')
BIG = ('HOUSING_F_front', 'HOUSING_F_door', 'FLOOR_PLATE', 'SLAB_frame')
PRINTED = ['HOUSING_F_front', 'HOUSING_F_door', 'HOUSING_F_cap', 'FLOOR_PLATE', 'SLAB_frame', 'SPKBOX_L', 'SPKBOX_R', 'RESP_CARRIER', 'CRADLE_5807',
           'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'BME_HOOD', 'GROMMET_usbc_F']
c = {}                                   # cache: results and temporary bodies, kept between connector calls
DEAD = [0.0]
NS = (0.0, -C, -S)                       # slab normal toward the door, world

# tools: [(diameter, length), ...] from the working end
IRON = [(6.0, 10.0), (10.0, 65.0), (16.8, 98.0)]; IRONG = [(6.0, 10.0), (10.0, 65.0), (40.0, 98.0)]
KEY20 = [(2.4, 101.0), (34.4, 4.0)]; KEY20G = [(2.4, 101.0), (55.0, 4.0)]; KEY20L = [(2.4, 101.0)]
KEY25 = [(3.0, 112.0), (39.0, 4.0)]; KEY25G = [(3.0, 112.0), (60.0, 4.0)]; KEY25L = [(3.0, 112.0)]
MICRO = [(3.0, 60.0), (13.0, 97.0)]; MICROG = [(3.0, 60.0), (40.0, 97.0)]
DRILL = [(1.7, 25.0), (9.0, 80.0)]       # pin vise: assumed
FINGER = [(16.0, 60.0)]

# bodies present, by group
ST = {'SHELL': ['HOUSING_F_front'], 'PLATE': ['FLOOR_PLATE'], 'PI': ['PI5_F', 'PI5_F_cooler'], 'PIPWR': ['PIPWR_a_env'], 'CRADLE': ['CRADLE_5807'],
      'INLET': ['PD_5807_env'], 'BOXES': ['SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'DRV_screw_heads_env'],
      'TOUCH': ['TOUCH_PCB', 'TOUCH_components_env', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R'], 'DISP': ['SLAB_frame', 'LCD_*'],
      'RESP': ['RESP_pcb', 'RESP_top_env', 'RESP_mic_env', 'RESP_usbc_plug_env'],
      'MAIN': ['MAIN_pcb', 'MAIN_PS1', 'MAIN_PS1_tol', 'MAIN_conn', 'MAIN_tall', 'MAIN_low'], 'USBA': ['USBA_plug_env', 'USBA_cable_env'],
      'CAP': ['HOUSING_F_cap', 'MIC_strip_L_env', 'MIC_strip_R_env', 'VEML_env'], 'PLUGS_PI': ['GPIO_plugA_env', 'GPIO_plugB_env'],
      'PLUGS_MB': ['MAIN_plug_env', 'MAIN_J2_plug_env'], 'RADAR': ['LD2410C_env_F'],
      'BME': ['BME680_env', 'FOAM_bme_env', 'FOAM_bme_top_env', 'BME_HOOD'], 'DOOR': ['HOUSING_F_door', 'GROMMET_usbc_F'], 'FEET': ['FOOT_*']}
ST['UNIT'] = ST['PLATE'] + ST['PI'] + ST['PIPWR'] + ST['CRADLE'] + ST['INLET'] + ST['BOXES']
ST['MODULE'] = ST['DISP'] + ['RESP_CARRIER'] + ST['RESP'] + ST['MAIN']
LEADS_D4 = ['LEAD_BME680', 'LEAD_PIGTAIL_20V', 'LEAD_SPK_L', 'LEAD_SPK_R', 'LEAD_PI_POWER', 'LEAD_RADAR']

# reach probe
TGT = {'J9 speaker right': ('B', -39.0, -25.0, 9.8), 'J8 speaker left': ('B', 38.75, -25.0, 9.8), 'J1 20 V': ('B', 0.0, -25.0, 9.8), 'J6 touch': ('B', 12.3, -22.2, 9.8),
       'J5 radar': ('B', -40.3, -13.85, 9.8), 'J10 BME680': ('B', -30.4, -14.11, 16.5), 'J11 VEML6030': ('B', -0.69, -13.0, 16.5), 'J2 Pi power': ('B', 21.6, -40.5, 5.0),
       'Pi 1x3 (1-3-5)': ('W', -32.29, -6.71, 32.0), 'Pi 1x3 display': ('W', -32.29, -4.17, 32.0), 'Pi 2x5 (7-16)': ('W', -22.13, -5.45, 32.0),
       'Pi 2x3 (35-40)': ('W', 10.91, -5.45, 32.0), 'Pi DSI': ('W', 13.0, -50.0, 17.0)}
DIRS = {'straight': (0, 1, 0), 'down25': (0, 0.9063, -0.4226), 'down45': (0, 0.7071, -0.7071), 'up25': (0, 0.9063, 0.4226), 'to-x25': (-0.4226, 0.9063, 0),
        'to+x25': (0.4226, 0.9063, 0)}                                   # slab frame
PIDIRS = {'back30': (0, -0.5, 0.866), 'back45': (0, -0.7071, 0.7071), 'back60': (0, -0.866, 0.5), 'back45 to-x25': (-0.4226, -0.6409, 0.6409),
          'back45 to+x25': (0.4226, -0.6409, 0.6409)}                    # world
PLUGB = {'J9': (-43.24, -34.76, -28.95, -22.11, 9.8), 'J1': (-4.24, 4.24, -28.95, -22.11, 9.8), 'J6': (9.41, 16.24, -28.93, -15.45, 9.8),
         'J8': (34.50, 43.00, -28.95, -22.11, 9.8), 'J5': (-43.20, -36.36, -20.60, -7.11, 9.8), 'J10': (-32.22, -28.59, -19.74, -8.49, 16.5),
         'J11': (-6.31, 4.94, -14.82, -11.18, 16.5)}                     # rev 3.1, board frame u0, u1, v0, v1, mated height
RFIX = ['HOUSING_F_cap', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'PI5_F', 'PI5_F_cooler', 'CRADLE_5807', 'PD_5807_env', 'RESP_CARRIER', 'RESP_pcb',
        'RESP_top_env', 'RESP_usbc_plug_env', 'PIPWR_a_env', 'BME_HOOD', 'LD2410C_env_F', 'MAIN_pcb', 'MAIN_PS1', 'MAIN_PS1_tol', 'MAIN_tall', 'MAIN_low',
        'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'TOUCH_PCB', 'USBA_plug_env']
ALLP = ['J9', 'J1', 'J6', 'J8', 'J5', 'J10', 'J11', 'J2', 'GPIO']
ORDER = [('Pi 1x3 (1-3-5)', []), ('Pi 2x5 (7-16)', []), ('Pi 2x3 (35-40)', []), ('Pi 1x3 display', []), ('J9 speaker right', ['GPIO']),
         ('J8 speaker left', ['GPIO', 'J9']), ('J1 20 V', ['GPIO', 'J9', 'J8']), ('J6 touch', ['GPIO', 'J9', 'J8', 'J1']),
         ('J5 radar', ['GPIO', 'J9', 'J8', 'J1', 'J6']), ('J10 BME680', ['GPIO', 'J9', 'J8', 'J1', 'J6', 'J5']),
         ('J11 VEML6030', ['GPIO', 'J9', 'J8', 'J1', 'J6', 'J5', 'J10']), ('J2 Pi power', ['GPIO', 'J9', 'J8', 'J1', 'J6', 'J5', 'J10', 'J11'])]


def Wp(x, y, z): return P3((x + XC) / 10.0, (y * C + (z - H) * S) / 10.0, (-y * S + (z - H) * C) / 10.0)      # world -> design point (cm)
def Dp(x, d, zd): return P3((x + XC) / 10.0, -d / 10.0, zd / 10.0)                                           # slab frame -> design
def Bp(u, v, w): return Dp(U0 + u, D0 + w, V0 + v)                                                           # board frame -> design
def W(p): return (p.x * 10 - XC, (p.y * C - p.z * S) * 10, H + (p.y * S + p.z * C) * 10)                      # design -> world
def Bf(p): return (p.x * 10 - XC - U0, p.z * 10 - V0, -p.y * 10 - D0)
def wv(v): return (v.x, v.y * C - v.z * S, v.y * S + v.z * C)                                                # design vector -> world
def dv(w): return V3(w[0], w[1] * C + w[2] * S, -w[1] * S + w[2] * C)                                        # world direction -> design


def unit(u):
    n = math.sqrt(sum(q * q for q in u)); return tuple(q / n for q in u)


def budget(sec): DEAD[0] = time.time() + sec


def say(*a):
    s = ' '.join(str(q) for q in a)
    c.setdefault('log', []).append(s); print(s)


class K:
    def __init__(self):
        self.app = adsk.core.Application.get()
        self.doc = self.app.activeDocument
        if self.doc.name != 'HA Panel v5 - tapered':
            raise RuntimeError('active document is %r' % self.doc.name)
        self.des = adsk.fusion.Design.cast(self.app.activeProduct)
        self.root = self.des.rootComponent
        self.tbm = adsk.fusion.TemporaryBRepManager.get()
        self.mm = self.app.measureManager
        self.by = {}
        for b in self.root.bRepBodies:
            self.by.setdefault(b.name, b)

    def body(self, name): return self.by.get(name)

    def state(self):
        df = self.doc.dataFile
        return {'version': df.versionNumber, 'latest': df.latestVersionNumber, 'modified': self.doc.isModified, 'bodies': self.root.bRepBodies.count,
                'visible': sum(1 for b in self.root.bRepBodies if b.isVisible), 'AUD': [b.name for b in self.root.bRepBodies if b.name.upper().startswith('AUD_')]}

    def wbox(self, x0, x1, y0, y1, z0, z1):
        x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
        obb = adsk.core.OrientedBoundingBox3D.create(Wp((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0), V3(1, 0, 0), V3(0, C, -S),
                                                     (x1 - x0) / 10.0, (y1 - y0) / 10.0, (z1 - z0) / 10.0)
        return self.tbm.createBox(obb)

    def dbox(self, x0, x1, d0, d1, z0, z1):
        x0, x1 = sorted((x0, x1)); d0, d1 = sorted((d0, d1)); z0, z1 = sorted((z0, z1))
        obb = adsk.core.OrientedBoundingBox3D.create(Dp((x0 + x1) / 2.0, (d0 + d1) / 2.0, (z0 + z1) / 2.0), V3(1, 0, 0), V3(0, 1, 0),
                                                     (x1 - x0) / 10.0, (d1 - d0) / 10.0, (z1 - z0) / 10.0)
        return self.tbm.createBox(obb)

    def move(self, tb, dx=0.0, dy=0.0, dz=0.0):                           # world translation
        m = adsk.core.Matrix3D.create()
        m.translation = V3(dx / 10.0, (dy * C + dz * S) / 10.0, (-dy * S + dz * C) / 10.0)
        self.tbm.transform(tb, m); return tb

    def vol(self, tb):
        try: return tb.volume * 1000.0
        except Exception: return 0.0


def current(X, leads=False, kos=True):                                   # the 98 bodies of the unit as it stands
    out = []
    for b in X.root.bRepBodies:
        n = b.name
        if n.startswith('LCD_'):
            if re.search('(_v[0-9]+|_[a-e][0-9]+[a-z0-9]*)$', n): continue
            out.append(b); continue
        if BACK.search(n) or n in LEGACY or n.startswith(NOTPART): continue
        if n.startswith('LEAD_') and not leads: continue
        if n.startswith('KO_') and not kos: continue
        out.append(b)
    return out


def present(X, names):
    cur = {}
    for b in current(X, leads=True): cur.setdefault(b.name, b)
    out = []
    for n in names:
        if n.endswith('*'): out += [b for k, b in cur.items() if k.startswith(n[:-1])]
        elif n in cur: out.append(cur[n])
        elif X.body(n) is not None: out.append(X.body(n))
        else: raise RuntimeError('no body ' + n)
    return out


def st(X, *keys):
    names = []
    for k in keys: names += ST[k] if k in ST else [k]
    return present(X, names)


def holes_of(b, rmin=0.7, rmax=7.0):                                    # cylinder faces grouped per axis: k 'h' hole / 'p' pin, r, ends A and B (world), coverage
    groups = {}
    for f in b.faces:
        g = f.geometry
        if g.surfaceType != CYL: continue
        r = g.radius * 10.0
        if r < rmin or r > rmax: continue
        o = W(g.origin); a = unit(wv(g.axis))
        k = max(range(3), key=lambda i: abs(a[i]))
        if a[k] < 0: a = tuple(-q for q in a)
        p = f.pointOnFace
        ok, nv = f.evaluator.getNormalAtPoint(p)
        pw = W(p); nw = wv(nv)
        t = sum((pw[i] - o[i]) * a[i] for i in range(3))
        rad = tuple(pw[i] - (o[i] + t * a[i]) for i in range(3))
        kind = 'p' if sum(rad[i] * nw[i] for i in range(3)) > 0 else 'h'
        s = -o[k] / a[k]
        q = tuple(o[i] + s * a[i] for i in range(3))
        key = (kind, round(r, 2), tuple(round(v, 1) for v in q), tuple(round(v, 3) for v in a))
        ts = [sum((W(v.geometry)[i] - q[i]) * a[i] for i in range(3)) for v in f.vertices]
        gq = groups.setdefault(key, {'t': [], 'area': 0.0, 'q': q, 'a': a})
        gq['t'] += ts; gq['area'] += f.area * 100.0
    rows = []
    for (kind, r, qq, aa), gq in groups.items():
        if not gq['t']: continue
        t0, t1 = min(gq['t']), max(gq['t']); L = t1 - t0
        cov = gq['area'] / (2 * math.pi * r * L) if L > 0.05 else 0.0
        q = gq['q']; a = gq['a']
        rows.append({'k': kind, 'r': r, 'A': [round(q[i] + t0 * a[i], 2) for i in range(3)], 'B': [round(q[i] + t1 * a[i], 2) for i in range(3)],
                     'a': [round(v, 3) for v in a], 'L': round(L, 2), 'cov': round(cov, 2)})
    return rows


# --- tool on its axis: stations, point-to-body distance less the tool's radius ---
def bbd(b):
    q = b.boundingBox; return (q.minPoint.x, q.minPoint.y, q.minPoint.z, q.maxPoint.x, q.maxPoint.y, q.maxPoint.z)


def pbox(p, q):
    dx = max(q[0] - p.x, 0.0, p.x - q[3]); dy = max(q[1] - p.y, 0.0, p.y - q[4]); dz = max(q[2] - p.z, 0.0, p.z - q[5])
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def rad_at(secs, s):
    a = 0.0
    for dia, L in secs:
        if s <= a + L + 1e-6: return dia / 2.0
        a += L
    return secs[-1][0] / 2.0


def line(X, o, u, secs, bodies, st0=2.0, step=5.0, rng=12.0, head=7.0):
    u = unit(u); total = sum(L for d, L in secs)
    best = {}; hb = {}; free = None
    bx = c.setdefault('bbd', {})
    s = st0
    while s <= total + 1e-6:
        if DEAD[0] and time.time() > DEAD[0]: raise RuntimeError('time budget')
        r = rad_at(secs, s)
        p = Wp(o[0] + u[0] * s, o[1] + u[1] * s, o[2] + u[2] * s)
        for b in bodies:
            q = bx.get(b.name)
            if q is None: q = bbd(b); bx[b.name] = q
            if pbox(p, q) * 10.0 > r + rng: continue
            mg = X.mm.measureMinimumDistance(p, b).value * 10.0 - r
            tgt = hb if s <= head else best
            if b.name not in tgt or mg < tgt[b.name][0]: tgt[b.name] = (mg, s)
            if mg < 0 and free is None: free = s
        s += step
    rows = sorted([round(v[0], 1), round(v[1], 0), k] for k, v in best.items())
    hrows = sorted([round(v[0], 1), round(v[1], 0), k] for k, v in hb.items())
    return {'min': rows[0] if rows else None, 'rows': rows[:3], 'head': hrows[0] if hrows else None, 'free': 'free' if free is None else free}


def sn(n): return n.replace('HOUSING_F_', '').replace('_env', '')
def cm(r): return 99.0 if r['min'] is None else r['min'][0]
def short(r): return '>12' if r['min'] is None else '%+.1f@%d %s' % (r['min'][0], r['min'][1], sn(r['min'][2]))
def fm(r): return 'head %s, beyond %s' % ('>12' if r['head'] is None else '%+.1f %s' % (r['head'][0], sn(r['head'][2])), short(r))


def probe(X, o, u, tool, hand, hard, leads=None, st0=2.0, step=5.0):
    out = 'tool: ' + fm(line(X, o, u, tool, hard, st0, step))
    if hand: out += ' | hand: ' + short(line(X, o, u, hand, hard, st0, step))
    if leads: out += ' | lead: ' + short(line(X, o, u, tool, leads, st0, step, head=0.0))
    return out


def tilt(d0, toward, deg):                                              # direction d0 turned by deg toward 'toward'
    d0 = unit(d0); t = unit(toward)
    k = sum(d0[i] * t[i] for i in range(3)); t = unit(tuple(t[i] - k * d0[i] for i in range(3)))
    ca = math.cos(math.radians(deg)); sa = math.sin(math.radians(deg))
    return tuple(d0[i] * ca + t[i] * sa for i in range(3))


def near(X, p, b):                                                      # distance from a world point to a body, and the body's point
    r = X.mm.measureMinimumDistance(Wp(*p), b)
    a = W(r.positionOne); e = W(r.positionTwo)
    q = a if (abs(a[0] - p[0]) + abs(a[1] - p[1]) + abs(a[2] - p[2])) > (abs(e[0] - p[0]) + abs(e[1] - p[1]) + abs(e[2] - p[2])) else e
    return round(r.value * 10.0, 2), [round(v, 1) for v in q]


def capscan(X, t0, tmax, state, B, sides, ths, pss, tool, hand, z0, tag):   # cap screws: th off the vertical, ps toward the middle
    res = c.setdefault('d7', {}); left = 0
    for name, x, y, sgn in sides:
        for th in ths:
            for ps in pss:
                k = (tag, state, name, th, ps)
                if k in res: continue
                if time.time() - t0 > tmax: left += 1; continue
                u = (sgn * math.sin(math.radians(th)) * math.sin(math.radians(ps)), -math.sin(math.radians(th)) * math.cos(math.radians(ps)), -math.cos(math.radians(th)))
                r = line(X, (x, y, z0), u, tool, B); g = line(X, (x, y, z0), u, hand, B)
                res[k] = (cm(r), r['min'][1] if r['min'] else 0, sn(r['min'][2]) if r['min'] else '', cm(g), g['min'][1] if g['min'] else 0,
                          sn(g['min'][2]) if g['min'] else '', r['head'][0] if r['head'] else 99)
    return left


# --- temporary bodies: copies, crops, intersections ---
def parts(X, name):                                                     # a big body as its eight cached slabs, any other as one temporary copy
    k = ('parts', name)
    if k in c: return c[k]
    b = X.body(name); out = None
    if name in BIG:
        tc = sys.modules.get('v5f_h_cache')
        if tc is not None:
            v = round(b.volume, 6)
            tl = [tc.c.get(('tile', name, v, i)) for i in range(8)]
            if all(t is not None for t in tl): out = [t for t in tl if t.faces.count > 0]
        if out is None: raise RuntimeError('no tiles for ' + name)
    else:
        out = [X.tbm.copy(b)]
    c[k] = out; return out


def xparts(X, tb, plist):                                               # mm3 of tb inside a list of temporary bodies
    v = 0.0
    for p in plist:
        if not tb.boundingBox.intersects(p.boundingBox): continue
        t = X.tbm.copy(tb)
        try:
            X.tbm.booleanOperation(t, p, BT.IntersectionBooleanType); v += X.vol(t)
        except Exception: v += -1000.0
    return v


def xvol(X, tb, name): return xparts(X, tb, parts(X, name))


def clash(X, tb, names, eps=0.005):
    out = {}
    for n in names:
        v = xvol(X, tb, n)
        if abs(v) > eps: out[sn(n)] = round(v, 2)
    return out


def mcopy(X, name, d):                                                  # a copy of a (small) model body moved by d (world)
    t = X.tbm.copy(parts(X, name)[0]); X.move(t, d[0], d[1], d[2]); return t


def region(X, name, key, box, frame='W'):                               # cached crop of a body to a world or slab-frame box
    k = ('region', name, key)
    if k in c: return c[k]
    bx = X.wbox(*box) if frame == 'W' else X.dbox(*box); out = []
    for p in parts(X, name):
        if not bx.boundingBox.intersects(p.boundingBox): continue
        t = X.tbm.copy(bx)
        X.tbm.booleanOperation(t, p, BT.IntersectionBooleanType)
        if X.vol(t) > 0.001: out.append(t)
    c[k] = out; return out


def needle_d(X, name, a, b, w=0.04):                                    # solid stretches of a thin bar between two design points, mm from a
    d = V3(b.x - a.x, b.y - a.y, b.z - a.z); L = d.length; d.normalize()
    ref = V3(0, 0, 1) if abs(d.z) < 0.9 else V3(1, 0, 0)
    wd = d.crossProduct(ref); wd.normalize()
    cen = P3((a.x + b.x) / 2.0, (a.y + b.y) / 2.0, (a.z + b.z) / 2.0)
    out = []
    for prt in parts(X, name):
        nd = X.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(cen, d, wd, L, w / 10.0, w / 10.0))
        if not nd.boundingBox.intersects(prt.boundingBox): continue
        try: X.tbm.booleanOperation(nd, prt, BT.IntersectionBooleanType)
        except Exception: continue
        for l in nd.lumps:
            ts = [((v.geometry.x - a.x) * d.x + (v.geometry.y - a.y) * d.y + (v.geometry.z - a.z) * d.z) * 10.0 for v in l.vertices]
            out.append([round(min(ts), 2), round(max(ts), 2)])
    out.sort(); mg = []
    for s in out:
        if mg and s[0] <= mg[-1][1] + 0.03: mg[-1][1] = max(mg[-1][1], s[1])
        else: mg.append(s)
    return mg


def needle(X, name, p0, p1, w=0.04): return needle_d(X, name, Wp(*p0), Wp(*p1), w)


def bbox_b(X, u0, u1, v0, v1, w0, w1): return X.dbox(U0 + u0, U0 + u1, D0 + w0, D0 + w1, V0 + v0, V0 + v1)


def finger(X, tipd, a, r, L=60.0):                                      # rounded fingertip: ball of radius r at the tip, cylinder behind it
    cc = P3(tipd.x + r / 10.0 * a.x, tipd.y + r / 10.0 * a.y, tipd.z + r / 10.0 * a.z)
    end = P3(tipd.x + L / 10.0 * a.x, tipd.y + L / 10.0 * a.y, tipd.z + L / 10.0 * a.z)
    tool = X.tbm.createCylinderOrCone(cc, r / 10.0, end, r / 10.0)
    X.tbm.booleanOperation(tool, X.tbm.createSphere(cc, r / 10.0), BT.UnionBooleanType)
    return tool


def reach(X, tn, plugs, r=8.0, hood=True):                              # {direction: {obstacle: mm3}}; a direction is free when its dict is empty
    res = c.setdefault('reach', {})
    key = (tn, tuple(sorted(plugs)), r, hood)
    if key in res: return res[key]
    tg = TGT[tn]; pi = tg[0] == 'W'
    tip = Wp(*tg[1:]) if pi else Bp(*tg[1:])
    shell = region(X, 'HOUSING_F_front', 'reach', (-110, 110, 18, 140, -115, 35), 'S')
    own = None
    if not pi:
        for pn, (u0, u1, v0, v1, h) in PLUGB.items():
            if u0 <= tg[1] <= u1 and v0 <= tg[2] <= v1: own = pn
    blocks = {}
    for pn, (u0, u1, v0, v1, h) in PLUGB.items():
        if pn in plugs and pn != own: blocks['plug ' + pn] = bbox_b(X, u0, u1, v0, v1, 0.0, h)
    names = [n for n in RFIX if hood or n != 'BME_HOOD']
    if 'J2' in plugs and not tn.startswith('J2'): names.append('MAIN_J2_plug_env')
    if 'GPIO' in plugs and not pi: names += ['GPIO_plugA_env', 'GPIO_plugB_env']
    out = {}
    for dn, d in (PIDIRS if pi else DIRS).items():
        if DEAD[0] and time.time() > DEAD[0]: return None
        a = dv(d) if pi else V3(d[0], -d[1], d[2])
        tool = finger(X, tip, a, r)
        hit = {}
        v = xparts(X, tool, shell)
        if abs(v) > 1.0: hit['shell'] = round(v)
        v = xvol(X, tool, 'FLOOR_PLATE')
        if abs(v) > 1.0: hit['plate'] = round(v)
        for n in names:
            v = xvol(X, tool, n)
            if abs(v) > 1.0: hit[sn(n).replace('MAIN_', '')] = round(v)
        for n, b in blocks.items():
            if not tool.boundingBox.intersects(b.boundingBox): continue
            t = X.tbm.copy(tool); X.tbm.booleanOperation(t, b, BT.IntersectionBooleanType); v = X.vol(t)
            if v > 1.0: hit[n] = round(v)
        out[dn] = hit
    res[key] = out
    return out


def capbar(X, th, yq, x0, u, Hh=8.0, Wd=19.2):                          # the cap as a bar, th deg back from vertical through (x0, yq, 172), top end u above it
    a = (0.0, -math.sin(math.radians(th)), -math.cos(math.radians(th)))
    cen = (x0, yq + a[1] * (77.0 - u), 172.0 + a[2] * (77.0 - u))
    return X.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(Wp(*cen), dv(unit(a)), dv((1, 0, 0)), 15.4, Wd / 10.0, Hh / 10.0))


# loader used in every call (the connector runs run()):
#   import sys, types
#   def run(_context):
#       m = sys.modules.get('aud2')            # first call: m = types.ModuleType('aud2'); exec(SRC, m.__dict__); sys.modules['aud2'] = m
#       X = m.K(); m.budget(50)
#       ...                                    # e.g. print(m.probe(X, (58.0, -8.25, 79.5), (0, -1, 0), m.KEY20, m.KEY20G, m.st(X, 'SHELL', 'RADAR', 'UNIT')))
# at the end: sys.modules.pop('aud2', None)
