# rev F f1a (2026-11-09): floor plate pass, block 1 (concept) - read-only plan sections and world extents.
#   World-horizontal plane sections (TemporaryBRepManager.planeIntersection) of the shell, door, references and the parts
#   near the floor at chosen heights; circles kept as (x_rel, y, r), other edges stroked and simplified to 0.1 mm;
#   intake-size circles (r < 1.1) summarised. World extents (x_rel, y, z) of the envelopes from a 0.1 mm mesh.
#   All body names (compact). Writes ~/Documents/HA_panel_renders/fp/f1a_sections.json (compact) + f1a_status.json.
#   Loader per README lesson 86; readOnly.
import adsk.core, adsk.fusion, json, math, os, time, traceback
C = math.cos(math.radians(12.0)); S = math.sin(math.radians(12.0)); H = 143.3; XC = -2.55
OUT = os.path.expanduser('~/Documents/HA_panel_renders/fp')
SECS = [('REF_F_outer', [0.05, 1.0, 2.5, 6.0]), ('INNER_E', [2.6, 5.0, 10.0]),
        ('HOUSING_F_front', [0.35, 1.25, 2.6, 4.0, 7.0, 10.0]), ('HOUSING_F_door', [2.9, 3.4, 5.0, 9.0]),
        ('SPKBOX_L', [4.0, 10.25]), ('SPKBOX_R', [4.0, 10.25]), ('MAIN_BRACKET', [3.0, 6.0, 10.0, 20.0]),
        ('CRADLE_5807', [9.0, 13.0, 20.0]), ('GROMMET_usbc_F', [20.0]), ('TOUCH_PCB', [10.0]),
        ('TOUCH_CLIP_L', [38.0]), ('TOUCH_CLIP_R', [38.0])]
BOXES = ['PI5_F_cooler', 'KO_K7_fan', 'USBA_plug_env', 'USBA_cable_env', 'PIPWR_a_env', 'LEAD_PI_POWER', 'PD_5807_env',
         'KO_5807_pigtail', 'LEAD_PIGTAIL_20V', 'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR', 'MAIN_pcb', 'MAIN_front_env',
         'MAIN_back_env', 'LEAD_SPK_L', 'LEAD_SPK_R', 'LEAD_TOUCH', 'LEAD_DSI', 'LEAD_GPIO_A', 'LEAD_GPIO_B',
         'GPIO_plugA_env', 'GPIO_plugB_env', 'SPK_L', 'SPK_R', 'KO_touch_back', 'LEAD_USB_RESP', 'LEAD_RADAR',
         'LEAD_LCD_5V', 'TOUCH_PCB', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'CRADLE_5807', 'MAIN_BRACKET', 'SPKBOX_L',
         'SPKBOX_R', 'GROMMET_usbc_F', 'BME680_env', 'BME_HOOD', 'LD2410C_env_F', 'RESP_usbc_plug_env']


def W(p):
    return (p.x * 10 - XC, (p.y * C - p.z * S) * 10, H + (p.y * S + p.z * C) * 10)


def dp(pts, tol):
    if len(pts) < 3:
        return pts
    a, b = pts[0], pts[-1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    best, bi = -1.0, 0
    for i in range(1, len(pts) - 1):
        p = pts[i]
        d = abs(dx * (a[1] - p[1]) - dy * (a[0] - p[0])) / L if L > 1e-9 else math.hypot(p[0] - a[0], p[1] - a[1])
        if d > best:
            best, bi = d, i
    if best <= tol:
        return [a, b]
    return dp(pts[:bi + 1], tol)[:-1] + dp(pts[bi:], tol)


def section(tbm, body, z):
    up = adsk.core.Vector3D.create(0.0, S, C)
    org = adsk.core.Point3D.create(0.0, ((z - H) * S) / 10.0, ((z - H) * C) / 10.0)
    wire = tbm.planeIntersection(body, adsk.core.Plane.create(org, up))
    out = {'c': [], 'pl': [], 'small': {'n': 0, 'r': [], 'bb': [1e9, -1e9, 1e9, -1e9]}}
    if wire is None:
        return out
    for e in wire.edges:
        g = e.geometry
        if g.objectType == adsk.core.Circle3D.classType():
            cc = W(g.center); r = g.radius * 10
            if r < 1.1:
                s = out['small']; s['n'] += 1
                if round(r, 2) not in s['r']:
                    s['r'].append(round(r, 2))
                bb = s['bb']; bb[0] = min(bb[0], cc[0]); bb[1] = max(bb[1], cc[0]); bb[2] = min(bb[2], cc[1]); bb[3] = max(bb[3], cc[1])
            else:
                out['c'].append([round(cc[0], 2), round(cc[1], 2), round(r, 2)])
            continue
        ev = e.evaluator
        ok, p0, p1 = ev.getParameterExtents()
        ok, pts = ev.getStrokes(p0, p1, 0.002)
        q = [(W(p)[0], W(p)[1]) for p in pts]
        q = dp(q, 0.08)
        out['pl'].append([round(v, 1) for xy in q for v in xy])
    s = out['small']
    s['bb'] = [round(v, 1) for v in s['bb']] if s['n'] else None
    return out


def wbbox(body, tol_mm=0.1):
    mc = body.meshManager.createMeshCalculator()
    mc.surfaceTolerance = tol_mm / 10.0
    m = mc.calculate()
    c = m.nodeCoordinatesAsDouble
    xs = []; ys = []; zs = []
    for i in range(0, len(c), 3):
        x = c[i] * 10 - XC; y = (c[i + 1] * C - c[i + 2] * S) * 10; z = H + (c[i + 1] * S + c[i + 2] * C) * 10
        xs.append(x); ys.append(y); zs.append(z)
    return [round(min(xs), 2), round(max(xs), 2), round(min(ys), 2), round(max(ys), 2), round(min(zs), 2), round(max(zs), 2)]


def run(_context):
    st = {'t0': time.strftime('%Y-%m-%d %H:%M:%S')}
    t0 = time.time()
    res = {'sec': {}, 'bbox': {}, 'names': []}
    try:
        app = adsk.core.Application.get()
        doc = [d for d in app.documents if d.name == 'HA Panel v5 - tapered'][0]
        des = adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
        root = des.rootComponent
        tbm = adsk.fusion.TemporaryBRepManager.get()
        byname = {}
        for b in root.bRepBodies:
            byname.setdefault(b.name, b)
            res['names'].append(b.name + ('*' if b.isLightBulbOn else ''))
        st['missing'] = []
        for nm, zs in SECS:
            b = byname.get(nm)
            if b is None:
                st['missing'].append(nm); continue
            res['sec'][nm] = {}
            for z in zs:
                res['sec'][nm][str(z)] = section(tbm, b, z)
            st[nm] = round(time.time() - t0, 1)
        for nm in BOXES:
            b = byname.get(nm)
            if b is None:
                st['missing'].append(nm); continue
            res['bbox'][nm] = wbbox(b)
        st['t_s'] = round(time.time() - t0, 1)
        json.dump(res, open(os.path.join(OUT, 'f1a_sections.json'), 'w'), separators=(',', ':'))
        st['bytes'] = os.path.getsize(os.path.join(OUT, 'f1a_sections.json'))
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    st['t_end'] = round(time.time() - t0, 1)
    json.dump(st, open(os.path.join(OUT, 'f1a_status.json'), 'w'))
    print(json.dumps({k: st.get(k) for k in ('missing', 't_s', 'bytes', 'FAIL', 't_end')}))


run(None)
