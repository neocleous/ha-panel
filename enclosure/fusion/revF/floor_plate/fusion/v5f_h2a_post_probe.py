# rev F h2a (2026-11-11): step 3, block 2 - read-only: the four posts of the rev 3 board before the carrier is rebuilt.
#   Holes (u, v): H1 (-37.0, 22.0), H2 (30.0, 25.0), H3 (-31.0, -25.25), H4 (31.0, -25.25). Post = cylinder along the board normal from the
#   carrier plate's display side (depth 15.2) to the board's back face (31.1).
#   A  post dia 8 and dia 9 (0.5 clear) against every current body and lead except the board and the present carrier
#   B  how much of the present plate (depth 15.2..17.2) lies under each post's foot (dia 8 = 100.5 mm3)
#   C  the present carrier: cylinder faces (axis u, v; radius; depth range), box
#   D  boxes of the display's parts behind the carrier (board frame u, v, depth)
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_h_lib.py'), encoding='utf-8').read())
HOLES = {'H1': (-37.0, 22.0), 'H2': (30.0, 25.0), 'H3': (-31.0, -25.25), 'H4': (31.0, -25.25)}


def dbb(b):                      # box as u0, u1, v0, v1, depth0, depth1
    q = bbb(b, 2)
    return q[:4] + [round(D0 + q[4], 2), round(D0 + q[5], 2)]


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        others = [b for b in current(X, leads=True) if not b.name.startswith('MAIN_') and b.name != 'RESP_CARRIER']
        A = {}
        for h, (u, v) in HOLES.items():
            for r in (4.0, 4.5):
                cyl = X.cyld(U0 + u, V0 + v, r, 15.2, 31.1)
                row = {}
                for b in others:
                    if not cyl.boundingBox.intersects(b.boundingBox):
                        continue
                    a = xvol(X, cyl, tcopy(X, b.name))
                    if abs(a) > 0.005:
                        row[b.name] = round(a, 2)
                A['%s r%.1f' % (h, r)] = row
        st['A'] = A
        car = X.body('RESP_CARRIER')
        st['B'] = {h: round(xvol(X, X.cyld(U0 + u, V0 + v, 4.0, 15.2, 17.2), tcopy(X, 'RESP_CARRIER')), 1) for h, (u, v) in HOLES.items()}
        cyls = []
        for f in car.faces:
            g = f.geometry
            if g.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType:
                o = Bf(g.origin); bb = f.boundingBox
                cyls.append([round(o[0], 2), round(o[1], 2), round(g.radius * 10, 2), round(-bb.maxPoint.y * 10, 2), round(-bb.minPoint.y * 10, 2)])
        st['C'] = {'box': dbb(car), 'vol': round(X.vol(car), 1), 'faces': car.faces.count, 'cyl': sorted(cyls)}
        st['D'] = {b.name: dbb(b) for b in X.root.bRepBodies if b.name.startswith(('LCD_', 'RESP_')) and not BACK.search(b.name) and b.name != 'RESP_CARRIER'}
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('h2a', st)


run(None)
