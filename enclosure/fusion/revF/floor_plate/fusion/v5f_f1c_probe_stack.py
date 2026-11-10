# rev F f1c (2026-11-10): floor plate pass, block 1 (concept, second round) - read-only probe for Daniel's 09:10 points:
#   (1) speakers on the plate: the boxes' plan extents per height against the wall reference (lean) and the floor outline;
#       the box / baffle screw axes (cylinders parallel to world y);
#   (3) main board on the LCD's Pi standoffs: design-frame boxes of the LCD stack, the ReSpeaker carrier and board, the
#       LCD-screw and cap-key lanes (axis ends), rays from the LCD PCB's back face along the slab normal (-Y design) to the
#       shell / door / cap and every current body on the way; plan sections behind the LCD at three heights; side sections
#       at x_rel 0.3 and +-70.5; a front section (world y -29.2) through both boxes.
#   Writes ~/Documents/HA_panel_renders/fp/f1c_probe.json (compact) + f1c_status.json. Loader per README lesson 86; readOnly.
import adsk.core, adsk.fusion, json, math, os, time, traceback
C = math.cos(math.radians(12.0)); S = math.sin(math.radians(12.0)); H = 143.3; XC = -2.55
OUT = os.path.expanduser('~/Documents/HA_panel_renders/fp')
CYL = adsk.core.SurfaceTypes.CylinderSurfaceType
SHELL = {'HOUSING_F_front': 'F', 'HOUSING_F_door': 'D', 'HOUSING_F_cap': 'C'}
CUR = ['SLAB_frame', 'LCD_glass', 'RESP_CARRIER', 'RESP_pcb', 'RESP_top_env', 'RESP_mic_env', 'RESP_usbc_plug_env',
       'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'MAIN_C7_env', 'KO_C7_vent', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL',
       'KO_K5_UR', 'KO_capkey_BL', 'KO_capkey_BR', 'KO_capkey_SL', 'KO_capkey_SR', 'MIC_strip_L_env', 'MIC_strip_R_env',
       'KO_mic_L_back', 'KO_mic_R_back', 'VEML_env', 'LD2410C_env_F', 'BME_HOOD', 'BME680_env', 'FOAM_bme_env',
       'FOAM_bme_top_env', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'PI5_F', 'PI5_F_cooler', 'KO_K7_fan', 'TOUCH_PCB',
       'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'MAIN_BRACKET', 'CRADLE_5807', 'PD_5807_env', 'KO_5807_pigtail', 'GROMMET_usbc_F',
       'PIPWR_a_env', 'USBA_plug_env', 'USBA_cable_env', 'GPIO_plugA_env', 'GPIO_plugB_env', 'LEAD_GPIO_A', 'LEAD_GPIO_B',
       'LEAD_LCD_5V', 'LEAD_MIC_L', 'LEAD_MIC_R', 'LEAD_SPK_L', 'LEAD_SPK_R', 'LEAD_RADAR', 'LEAD_TOUCH', 'LEAD_VEML',
       'LEAD_BME680', 'LEAD_PIGTAIL_20V', 'LEAD_USB_RESP', 'LEAD_DSI', 'LEAD_PI_POWER']
ZLEAN = [2.6, 6.0, 12.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 76.0, 82.0, 100.0, 120.0, 140.0, 160.0, 172.0]
ZBOX = [4.5, 8.0, 12.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 75.0, 80.0]
PLAN3 = [95.0, 116.0, 135.0]
PLAN3_B = ['HOUSING_F_front', 'HOUSING_F_door', 'SLAB_frame', 'LCD_pcb_76x110', 'LCD_panel_body', 'RESP_CARRIER', 'RESP_pcb',
           'RESP_top_env', 'RESP_usbc_plug_env', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR', 'LD2410C_env_F', 'BME_HOOD',
           'LEAD_MIC_L', 'LEAD_MIC_R', 'LEAD_DSI', 'LEAD_USB_RESP', 'LEAD_LCD_5V', 'LEAD_RADAR', 'KO_capkey_BL', 'KO_capkey_BR',
           'KO_capkey_SL', 'KO_capkey_SR']
SIDE = [(0.3, ['HOUSING_F_front', 'HOUSING_F_door', 'HOUSING_F_cap', 'SLAB_frame', 'LCD_glass', 'LCD_pcb_76x110',
               'LCD_panel_body', 'RESP_CARRIER', 'RESP_pcb', 'RESP_top_env', 'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env',
               'PI5_F', 'PI5_F_cooler', 'KO_K7_fan', 'CRADLE_5807', 'PD_5807_env', 'TOUCH_PCB', 'GROMMET_usbc_F']),
        (70.5, ['HOUSING_F_front', 'HOUSING_F_door', 'SPKBOX_L', 'SPK_L', 'SLAB_frame', 'LCD_glass']),
        (-70.5, ['HOUSING_F_front', 'HOUSING_F_door', 'SPKBOX_R', 'SPK_R', 'SLAB_frame', 'BME_HOOD', 'LD2410C_env_F'])]
FRONT = (-29.2, ['HOUSING_F_front', 'SPKBOX_L', 'SPKBOX_R', 'REF_F_outer', 'INNER_E', 'SPK_L', 'SPK_R', 'PI5_F', 'PI5_F_cooler'])


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


def strokes(tbm, body, org, nrm, proj):
    try:
        wire = tbm.planeIntersection(body, adsk.core.Plane.create(org, nrm))
    except Exception:
        return None
    if wire is None:
        return []
    out = []
    for e in wire.edges:
        ev = e.evaluator
        ok, p0, p1 = ev.getParameterExtents()
        ok, pts = ev.getStrokes(p0, p1, 0.002)
        out.append([proj(W(p)) for p in pts])
    return out


def plan(tbm, body, z):
    return strokes(tbm, body, adsk.core.Point3D.create(0.0, ((z - H) * S) / 10.0, ((z - H) * C) / 10.0),
                   adsk.core.Vector3D.create(0.0, S, C), lambda w: (w[0], w[1]))


def side(tbm, body, xr):
    return strokes(tbm, body, adsk.core.Point3D.create((xr + XC) / 10.0, 0.0, 0.0), adsk.core.Vector3D.create(1.0, 0.0, 0.0),
                   lambda w: (w[1], w[2]))


def front(tbm, body, y0):
    return strokes(tbm, body, adsk.core.Point3D.create(0.0, y0 * C / 10.0, -y0 * S / 10.0),
                   adsk.core.Vector3D.create(0.0, C, -S), lambda w: (w[0], w[2]))


def pack(polys, tol=0.1):
    if polys is None:
        return 'err'
    return [[round(v, 1) for xy in dp(q, tol) for v in xy] for q in polys]


def cross(polys, idx, val):
    out = []
    for q in polys or []:
        for a, b in zip(q, q[1:]):
            da, db = a[idx] - val, b[idx] - val
            if da == 0.0:
                out.append(a[1 - idx])
            elif da * db < 0.0:
                t = da / (da - db)
                out.append(a[1 - idx] + t * (b[1 - idx] - a[1 - idx]))
    return out


def ext(polys):
    xs = [p[0] for q in polys or [] for p in q]; ys = [p[1] for q in polys or [] for p in q]
    return [round(min(xs), 2), round(max(xs), 2), round(min(ys), 2), round(max(ys), 2)] if xs else None


def hull(pts):
    pts = sorted(set((round(p[0], 2), round(p[1], 2)) for p in pts))
    if len(pts) < 3:
        return pts

    def half(seq):
        h = []
        for p in seq:
            while len(h) >= 2 and (h[-1][0] - h[-2][0]) * (p[1] - h[-2][1]) - (h[-1][1] - h[-2][1]) * (p[0] - h[-2][0]) <= 0:
                h.pop()
            h.append(p)
        return h
    lo = half(pts); up = half(pts[::-1])
    return lo[:-1] + up[:-1]


def wbbox(body, tol_mm=0.1):
    mc = body.meshManager.createMeshCalculator()
    mc.surfaceTolerance = tol_mm / 10.0
    c = mc.calculate().nodeCoordinatesAsDouble
    xs = []; ys = []; zs = []
    for i in range(0, len(c), 3):
        xs.append(c[i] * 10 - XC); ys.append((c[i + 1] * C - c[i + 2] * S) * 10); zs.append(H + (c[i + 1] * S + c[i + 2] * C) * 10)
    return [round(min(xs), 2), round(max(xs), 2), round(min(ys), 2), round(max(ys), 2), round(min(zs), 2), round(max(zs), 2)]


def dbox(b):
    bb = b.boundingBox; mn, mx = bb.minPoint, bb.maxPoint
    return [round(mn.x * 10 - XC, 2), round(mx.x * 10 - XC, 2), round(mn.y * 10, 2), round(mx.y * 10, 2), round(mn.z * 10, 2),
            round(mx.z * 10, 2)]


def ycyls(body, rmin, rmax, keep=None):
    out = {}
    for f in body.faces:
        g = f.geometry
        if g.surfaceType != CYL:
            continue
        r = g.radius * 10
        if r < rmin or r > rmax:
            continue
        a = g.axis
        n = math.sqrt(a.x * a.x + a.y * a.y + a.z * a.z)
        if abs((a.y * C - a.z * S) / n) < 0.999:
            continue
        o = W(g.origin)
        if keep is not None and not keep(o):
            continue
        ys = [W(v.geometry)[1] for v in f.vertices]
        if not ys:
            continue
        k = (round(r, 2), round(o[0], 1), round(o[2], 1))
        cur = out.get(k)
        out[k] = [min(ys + ([cur[0]] if cur else [])), max(ys + ([cur[1]] if cur else []))]
    return [[k[0], k[1], k[2], round(v[0], 1), round(v[1], 1)] for k, v in sorted(out.items())]


def lane(body):
    best = None
    for f in body.faces:
        g = f.geometry
        if g.surfaceType == CYL and (best is None or f.area > best[0]):
            best = (f.area, g)
    if best is None:
        return None
    g = best[1]; o = g.origin; a = g.axis
    n = math.sqrt(a.x * a.x + a.y * a.y + a.z * a.z)
    ax, ay, az = a.x / n, a.y / n, a.z / n
    ts = [(v.geometry.x - o.x) * ax + (v.geometry.y - o.y) * ay + (v.geometry.z - o.z) * az for v in body.vertices]
    e = []
    for t in (min(ts), max(ts)):
        e.append([round(v, 2) for v in W(adsk.core.Point3D.create(o.x + ax * t, o.y + ay * t, o.z + az * t))])
    return {'r': round(g.radius * 10, 2), 'ends': e}


def run(_context):
    st = {'t0': time.strftime('%Y-%m-%d %H:%M:%S'), 'missing': [], 'fail': {}}
    t0 = time.time()
    res = {}
    sf = os.path.join(OUT, 'f1c_status.json')

    def mark(k):
        st[k] = round(time.time() - t0, 1)
        json.dump(st, open(sf, 'w'))
    try:
        app = adsk.core.Application.get()
        doc = [d for d in app.documents if d.name == 'HA Panel v5 - tapered'][0]
        des = adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
        root = des.rootComponent
        tbm = adsk.fusion.TemporaryBRepManager.get()
        byname = {}
        for b in root.bRepBodies:
            byname.setdefault(b.name, b)
        st['bodies'] = root.bRepBodies.count
        st['aud'] = sorted(n for n in byname if n.startswith('AUD_'))
        st['modified'] = doc.isModified
        st['version'] = doc.dataFile.versionNumber if doc.dataFile else None

        def get(nm):
            b = byname.get(nm)
            if b is None and nm not in st['missing']:
                st['missing'].append(nm)
            return b
        # 1 design-frame and world boxes of the LCD stack, carrier, ReSpeaker, lanes
        try:
            res['dbox'] = {}; res['wbox'] = {}
            for b in root.bRepBodies:
                n = b.name
                if n.startswith('LCD_') or n in ('RESP_CARRIER', 'RESP_pcb', 'RESP_top_env', 'RESP_mic_env', 'RESP_usbc_plug_env',
                                                 'SLAB_frame', 'MIC_strip_L_env', 'MIC_strip_R_env', 'VEML_env', 'KO_K5_LL',
                                                 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR'):
                    res['dbox'][n] = dbox(b)
                if n.startswith('LCD_') or n in ('RESP_CARRIER', 'RESP_pcb', 'RESP_top_env', 'RESP_mic_env', 'SLAB_frame',
                                                 'HOUSING_F_cap', 'MIC_strip_L_env', 'MIC_strip_R_env', 'VEML_env', 'LEAD_MIC_L',
                                                 'LEAD_MIC_R', 'LEAD_VEML', 'LEAD_BME680', 'MAIN_C7_env', 'KO_C7_vent', 'KO_K5_LL',
                                                 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR', 'KO_capkey_BL', 'KO_capkey_BR', 'KO_capkey_SL',
                                                 'KO_capkey_SR', 'FOAM_bme_env', 'FOAM_bme_top_env'):
                    res['wbox'][n] = wbbox(b, 0.2 if n in ('SLAB_frame', 'HOUSING_F_cap') else 0.1)
            res['lanes'] = {}
            for n in ('KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR', 'KO_capkey_BL', 'KO_capkey_BR', 'KO_capkey_SL', 'KO_capkey_SR'):
                b = get(n)
                if b:
                    res['lanes'][n] = lane(b)
        except Exception:
            st['fail']['boxes'] = traceback.format_exc().splitlines()[-3:]
        mark('boxes')
        # 2 wall reference per height, boxes per height
        try:
            inner = get('INNER_E'); lean = {}
            for z in ZLEAN:
                q = plan(tbm, inner, z)
                row = {}
                for y0 in (-5.0, -30.0, -50.0):
                    xs = cross(q, 1, y0)
                    row['x@y%g' % y0] = [round(min(xs), 2), round(max(xs), 2)] if xs else None
                for x0 in (0.0, 30.0, 45.0, 60.0, 70.5, -45.0):
                    ys = cross(q, 0, x0)
                    row['y@x%g' % x0] = [round(min(ys), 2), round(max(ys), 2)] if ys else None
                lean[str(z)] = row
            res['lean'] = lean
            res['box'] = {}
            for nm in ('SPKBOX_L', 'SPKBOX_R'):
                b = get(nm); rows = {}; allp = []
                for z in ZBOX:
                    q = plan(tbm, b, z)
                    if not q:
                        rows[str(z)] = None; continue
                    row = {'ext': ext(q)}
                    for y0 in (-5.0, -30.0, -50.0):
                        xs = cross(q, 1, y0)
                        row['x@y%g' % y0] = [round(min(xs), 2), round(max(xs), 2)] if xs else None
                    rows[str(z)] = row
                    allp += [p for s in q for p in s]
                hp = hull(allp)
                rows['hull'] = [round(v, 1) for xy in dp(hp + hp[:1], 0.1) for v in xy]
                res['box'][nm] = rows
        except Exception:
            st['fail']['lean'] = traceback.format_exc().splitlines()[-3:]
        mark('lean')
        # 3 screw axes parallel to world y
        try:
            res['ycyl'] = {}
            for nm in ('SPKBOX_L', 'SPKBOX_R'):
                res['ycyl'][nm] = ycyls(get(nm), 0.9, 6.0)
            res['ycyl']['HOUSING_F_front'] = ycyls(get('HOUSING_F_front'), 1.0, 4.6,
                                                    lambda o: 44.0 <= abs(o[0]) <= 98.0 and o[2] < 90.0)
        except Exception:
            st['fail']['ycyl'] = traceback.format_exc().splitlines()[-3:]
        mark('ycyl')
        # 4 rays from the LCD PCB's back face along -Y (design)
        try:
            pcb = get('LCD_pcb_76x110'); bb = pcb.boundingBox
            y0 = bb.minPoint.y; zlo = bb.minPoint.z * 10; zhi = bb.maxPoint.z * 10
            names = set(CUR) | set(SHELL)
            rows = []
            zd = zlo - 45.0
            zs = []
            while zd <= zhi + 10.01:
                zs.append(zd); zd += 9.0
            for zd in zs:
                for xr in (-50.0, -40.0, -30.0, -20.0, -10.0, 0.0, 10.0, 20.0, 30.0, 40.0, 50.0):
                    hp = adsk.core.ObjectCollection.create()
                    ents = root.findBRepUsingRay(adsk.core.Point3D.create((xr + XC) / 10.0, y0, zd / 10.0),
                                                 adsk.core.Vector3D.create(0.0, -1.0, 0.0),
                                                 adsk.fusion.BRepEntityTypes.BRepFaceEntityType, -1.0, False, hp)
                    sh = []; oth = {}
                    for i in range(ents.count):
                        n = ents.item(i).body.name
                        if n not in names and not n.startswith('LCD_'):
                            continue
                        d = round((y0 - hp.item(i).y) * 10, 1)
                        if n in SHELL:
                            sh.append([SHELL[n], d])
                        elif n not in oth or d < oth[n]:
                            oth[n] = d
                    sh.sort(key=lambda t: t[1])
                    rows.append([xr, round(zd, 1), sh[:3], oth])
            res['rays'] = {'Y0': round(y0 * 10, 2), 'pcb_z': [round(zlo, 2), round(zhi, 2)], 'rows': rows}
        except Exception:
            st['fail']['rays'] = traceback.format_exc().splitlines()[-3:]
        mark('rays')
        # 5 sections
        try:
            res['plan3'] = {}
            for z in PLAN3:
                d = {}
                for nm in PLAN3_B:
                    b = get(nm)
                    if b is None:
                        continue
                    q = plan(tbm, b, z)
                    if q:
                        d[nm] = pack(q)
                res['plan3'][str(z)] = d
            mark('plan3')
            res['side'] = {}
            for xr, names2 in SIDE:
                d = {}
                for nm in names2:
                    b = get(nm)
                    if b is None:
                        continue
                    q = side(tbm, b, xr)
                    if q:
                        d[nm] = pack(q)
                res['side'][str(xr)] = d
            mark('side')
            d = {}
            for nm in FRONT[1]:
                b = get(nm)
                if b is None:
                    continue
                q = front(tbm, b, FRONT[0])
                if q:
                    d[nm] = pack(q)
            res['front'] = {str(FRONT[0]): d}
        except Exception:
            st['fail']['sections'] = traceback.format_exc().splitlines()[-3:]
        mark('sections')
        pf = os.path.join(OUT, 'f1c_probe.json')
        json.dump(res, open(pf, 'w'), separators=(',', ':'))
        st['bytes'] = os.path.getsize(pf)
        st['sizes'] = {k: len(json.dumps(v, separators=(',', ':'))) for k, v in res.items()}
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    st['t_end'] = round(time.time() - t0, 1)
    json.dump(st, open(sf, 'w'))
    print(json.dumps({k: st.get(k) for k in ('missing', 'fail', 'bytes', 'sizes', 'FAIL', 't_end', 'aud', 'modified', 'version')}))


run(None)
