# rev F i4a2 (2026-11-11): step 3 repeated, block 4 - read-only: the lead slot of the BME680 tray, read from the shell's faces.
#   i4a showed the lead's last leg running in a slot between two parallel vertical faces of the tray (moulded to the rear right corner
#   wall). Tray frame, taken from those faces: t along the wall (unit vector TD in world x, y), s away from the wall (SD), z up.
#   A  every planar face of the shell (cropped to the lead's end) whose normal is along +/-TD: its t, and its ranges in s and z
#   B  the sensor's envelope, its foam and the hood in the same frame (from their vertices)
#   C  the lead's nodes in the same frame
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_i_lib.py'), encoding='utf-8').read())
TD = (0.6570, -0.7539)          # along the wall (world x, y); refined below from the faces found
ROUTE = json.load(open(os.path.join(S3, 'h3_routes.json')))['LEAD_BME680'][1]


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        c = cache()
        sh = c['crop_bme_end']
        cand = []
        for f in sh.faces:
            g = f.geometry
            if g.surfaceType != adsk.core.SurfaceTypes.PlaneSurfaceType:
                continue
            n = g.normal
            # design -> world rotation of a direction: x = x, y = y*C - z*S, z = y*S + z*C
            wx, wy, wz = n.x, n.y * C - n.z * S, n.y * S + n.z * C
            if abs(wz) > 0.05:
                continue
            dot = wx * TD[0] + wy * TD[1]
            if abs(dot) < 0.995:
                continue
            ws = [W(v.geometry) for v in f.vertices]
            if not ws:
                continue
            ts = [p[0] * wx + p[1] * wy for p in ws]
            sx, sy = -wy, wx                      # in-plane horizontal direction
            ss = [p[0] * sx + p[1] * sy for p in ws]
            zs = [p[2] for p in ws]
            cand.append([round(sum(ts) / len(ts) * (1 if dot > 0 else -1), 3), round(wx, 4), round(wy, 4), round(min(ss), 2), round(max(ss), 2),
                         round(min(zs), 2), round(max(zs), 2), round(f.area * 100.0, 1)])
        st['A'] = sorted(cand)

        def frame(p):
            return [round(p[0] * TD[0] + p[1] * TD[1], 2), round(p[0] * -TD[1] + p[1] * TD[0], 2), round(p[2], 2)]
        B = {}
        for nme in ('BME680_env', 'FOAM_bme_env', 'FOAM_bme_top_env', 'BME_HOOD'):
            b = X.body(nme)
            q = [frame(W(v.geometry)) for v in b.vertices]
            B[nme] = [min(a[0] for a in q), max(a[0] for a in q), min(a[1] for a in q), max(a[1] for a in q), min(a[2] for a in q), max(a[2] for a in q)]
        st['B'] = B
        nodes = []
        for nd in ROUTE:
            p = Bp(nd[1], nd[2], nd[3]) if nd[0] == 'B' else (Dp(nd[1], nd[2], nd[3]) if nd[0] == 'S' else Wp(nd[1], nd[2], nd[3]))
            w = W(p)
            nodes.append([[round(v, 2) for v in w], frame(w)])
        st['C'] = nodes
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('i4a2', st)


run(None)
