# rev F f2a (2026-11-10): floor plate pass, block 2 - read-only inventory before the first cut.
#   state: document version / modified / AUD_* / body count / volumes of the parts that change
#   floor: every vertical cylinder of the front shell below z 12 (bosses, holes, recesses); intake centres to a file
#   carrier: section of RESP_CARRIER at mid-plate (design Y -16.2) and its cylinders along design Y
#   LCD opening: section of the front shell's slot-face wall at design Y -12.0, |x_rel| <= 75, Zd -80..20
#   door opening at the tab screws' height: plan sections of the front shell and the door at z 79.5 (y < -40)
#   -x box hump: plan section of SPKBOX_R at z 79.5; both boxes at z 38 (ears), clips at z 38
#   wall behind the screen at the tab bosses: side sections of the front shell at x_rel +-57.5, z 68..92
# Writes ~/Documents/HA_panel_renders/fp/f2a_inventory.json (compact) and f2a_intake.json. Loader per README lesson 86.
import adsk.core, adsk.fusion, json, math, os, time, traceback
C = math.cos(math.radians(12.0)); S = math.sin(math.radians(12.0)); H = 143.3; XC = -2.55
OUT = os.path.expanduser('~/Documents/HA_panel_renders/fp')
CYL = adsk.core.SurfaceTypes.CylinderSurfaceType
VOL = ['HOUSING_F_front', 'HOUSING_F_door', 'SPKBOX_L', 'SPKBOX_R', 'MAIN_BRACKET', 'RESP_CARRIER', 'CRADLE_5807', 'REF_F_outer',
       'INNER_E', 'TOOL_inner_skin_0p7', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R']


def W(p):
    return (p.x * 10 - XC, (p.y * C - p.z * S) * 10, H + (p.y * S + p.z * C) * 10)


def DZ(p):                                    # design point -> (x_rel, depth -Y, Zd) mm
    return (p.x * 10 - XC, -p.y * 10, p.z * 10)


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


def strokes(tbm, body, org, nrm, proj, keep=None):
    try:
        wire = tbm.planeIntersection(body, adsk.core.Plane.create(org, nrm))
    except Exception:
        return 'err'
    out = []
    for e in wire.edges:
        ev = e.evaluator
        ok, p0, p1 = ev.getParameterExtents()
        ok, pts = ev.getStrokes(p0, p1, 0.002)
        q = [proj(p) for p in pts]
        if keep is not None and not any(keep(t) for t in q):
            continue
        out.append([round(v, 2) for xy in dp(q, 0.05) for v in xy])
    return out


def plan(tbm, body, z, keep=None):
    return strokes(tbm, body, adsk.core.Point3D.create(0.0, ((z - H) * S) / 10.0, ((z - H) * C) / 10.0),
                   adsk.core.Vector3D.create(0.0, S, C), lambda p: W(p)[:2], keep)


def side(tbm, body, xr, keep=None):
    return strokes(tbm, body, adsk.core.Point3D.create((xr + XC) / 10.0, 0.0, 0.0), adsk.core.Vector3D.create(1.0, 0.0, 0.0),
                   lambda p: W(p)[1:], keep)


def slabsec(tbm, body, Y, keep=None):         # plane parallel to the LCD at design Y (mm): (x_rel, Zd)
    return strokes(tbm, body, adsk.core.Point3D.create(0.0, Y / 10.0, 0.0), adsk.core.Vector3D.create(0.0, 1.0, 0.0),
                   lambda p: (p.x * 10 - XC, p.z * 10), keep)


def run(_context):
    st = {'t0': time.strftime('%Y-%m-%d %H:%M:%S'), 'missing': [], 'fail': {}}
    t0 = time.time(); res = {}
    try:
        app = adsk.core.Application.get()
        doc = [d for d in app.documents if d.name == 'HA Panel v5 - tapered'][0]
        des = adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
        root = des.rootComponent
        tbm = adsk.fusion.TemporaryBRepManager.get()
        byname = {}
        for b in root.bRepBodies:
            byname.setdefault(b.name, b)
        res['state'] = {'version': doc.dataFile.versionNumber if doc.dataFile else None, 'modified': doc.isModified,
                        'bodies': root.bRepBodies.count, 'aud': sorted(n for n in byname if n.startswith('AUD_')),
                        'active': app.activeDocument.name, 'dup': sorted(n for n in byname if n.endswith(')'))[:20]}
        res['vol'] = {n: [round(byname[n].volume, 4), byname[n].lumps.count, byname[n].isLightBulbOn] for n in VOL if n in byname}
        st['missing'] = [n for n in VOL if n not in byname]
        fr = byname['HOUSING_F_front']
        # floor cylinders
        try:
            cyl = {}; intake = set()
            for f in fr.faces:
                g = f.geometry
                if g.surfaceType != CYL:
                    continue
                a = g.axis
                n = math.sqrt(a.x * a.x + a.y * a.y + a.z * a.z)
                if abs((a.y * S + a.z * C) / n) < 0.999:
                    continue
                zs = [W(v.geometry)[2] for v in f.vertices]
                if not zs or min(zs) > 12.0:
                    continue
                o = W(g.origin); r = round(g.radius * 10, 2)
                if abs(r - 1.0) < 0.02 and max(zs) < 2.6:
                    intake.add((round(o[0], 2), round(o[1], 2)))
                    continue
                k = (r, round(o[0], 2), round(o[1], 2))
                c = cyl.get(k)
                cyl[k] = [min(zs + ([c[0]] if c else [])), max(zs + ([c[1]] if c else []))]
            res['floor_cyl'] = [[k[0], k[1], k[2], round(v[0], 2), round(v[1], 2)] for k, v in sorted(cyl.items(), key=lambda t: (t[0][2], t[0][1]))]
            json.dump(sorted(intake), open(os.path.join(OUT, 'f2a_intake.json'), 'w'))
            res['intake_n'] = len(intake)
        except Exception:
            st['fail']['floor'] = traceback.format_exc().splitlines()[-3:]
        # carrier
        try:
            ca = byname['RESP_CARRIER']; cc = {}
            for f in ca.faces:
                g = f.geometry
                if g.surfaceType != CYL:
                    continue
                a = g.axis
                if abs(a.y) / math.sqrt(a.x * a.x + a.y * a.y + a.z * a.z) < 0.999:
                    continue
                o = DZ(g.origin); ds = [DZ(v.geometry)[1] for v in f.vertices]
                if not ds:
                    continue
                k = (round(g.radius * 10, 2), round(o[0], 2), round(o[2], 2))
                c = cc.get(k)
                cc[k] = [min(ds + ([c[0]] if c else [])), max(ds + ([c[1]] if c else []))]
            res['carrier_cyl'] = [[k[0], k[1], k[2], round(v[0], 2), round(v[1], 2)] for k, v in sorted(cc.items())]
            res['carrier_plate'] = slabsec(tbm, ca, -16.2)
            res['carrier_boss'] = slabsec(tbm, ca, -20.0)
            for n in ('RESP_pcb', 'RESP_top_env', 'RESP_mic_env'):
                bb = byname[n].boundingBox
                res.setdefault('resp', {})[n] = [round(v, 2) for v in (bb.minPoint.x * 10 - XC, bb.maxPoint.x * 10 - XC, -bb.maxPoint.y * 10,
                                                                        -bb.minPoint.y * 10, bb.minPoint.z * 10, bb.maxPoint.z * 10)]
        except Exception:
            st['fail']['carrier'] = traceback.format_exc().splitlines()[-3:]
        # LCD opening in the wall behind the screen
        try:
            res['lcd_opening'] = slabsec(tbm, fr, -12.0, lambda t: abs(t[0]) <= 75.0 and -80.0 <= t[1] <= 20.0)
        except Exception:
            st['fail']['opening'] = traceback.format_exc().splitlines()[-3:]
        # door opening at z 79.5 and the boxes / clips
        try:
            res['z79p5'] = {'front': plan(tbm, fr, 79.5, lambda t: t[1] < -40.0 and abs(t[0]) < 75.0),
                            'door': plan(tbm, byname['HOUSING_F_door'], 79.5, lambda t: abs(t[0]) < 75.0),
                            'box_R': plan(tbm, byname['SPKBOX_R'], 79.5), 'box_L': plan(tbm, byname['SPKBOX_L'], 75.3)}
            res['z38'] = {n: plan(tbm, byname[n], 38.0, lambda t: abs(t[0]) < 50.0 and t[1] > -14.0)
                          for n in ('SPKBOX_L', 'SPKBOX_R', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R') if n in byname}
            res['side57'] = {str(x): side(tbm, fr, x, lambda t: 68.0 <= t[1] <= 92.0 and t[0] > -12.0) for x in (57.5, -57.5)}
        except Exception:
            st['fail']['sections'] = traceback.format_exc().splitlines()[-3:]
        pf = os.path.join(OUT, 'f2a_inventory.json')
        json.dump(res, open(pf, 'w'), separators=(',', ':'))
        st['bytes'] = os.path.getsize(pf); st['sizes'] = {k: len(json.dumps(v, separators=(',', ':'))) for k, v in res.items()}
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-4:]
    st['t_end'] = round(time.time() - t0, 1)
    json.dump(st, open(os.path.join(OUT, 'f2a_status.json'), 'w'))
    print(json.dumps(st))


run(None)
