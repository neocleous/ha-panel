# rev F j5a (2026-11-12): close, block 5.1 - read-only: the open area of every air opening, measured on the model, and the free
#   cross-section of the air's way from the intake to the exhaust. MODE (global): 'probe', 'intake', 'rows', 'slots', 'path'.
#   Open area = the smallest area left open in a thin slice (0.2) across the opening, the slice moved through the wall in steps of 0.25
#   along the direction the opening was cut in (world y for the back wall's rows and the door's slots, world z for the plate's field).
#   A slice that lies wholly inside the wall gives the opening's own cross-section; the smallest value over the wall is its throat.
#   probe   needles along y through the back wall round the rows and through the door round the slots: where the material is
#   intake  the plate's field under the Pi (x -42..41, y -59..-6): slice z 1.0..1.5; number of dia 2.0 holes
#   rows    back wall, two rows (z 162.5..165.5 and 167.0..170.0, d5e): per row in 1.0 strips along x
#   slots   door, twelve slots (x_rel -24..42 on a 6.0 pitch, 3.0 wide, from z 66, d5e): per slot in 1.0 strips along z
#   path    horizontal slices (0.4) of the interior at HEIGHTS: the unit's solid parts and the cloth taken out of a box round the unit;
#           every pocket of air that does not reach the box's edge: area and extent. Plug envelopes and key paths are not solid.
#   Results are kept in the cache and a call stops after BUDGET seconds: call until 'left' is 0.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_j_lib.py'), encoding='utf-8').read())
MODE = globals().get('MODE', 'probe')
BUDGET = globals().get('BUDGET', 35.0)
ROWS = ((162.5, 165.5), (167.0, 170.0))
SLOTS = [-24.0 + 6.0 * i for i in range(12)]
HEIGHTS = globals().get('HEIGHTS', (20, 30, 45, 60, 75, 85, 95, 105, 115, 125, 135, 145, 155, 161))
NOT_SOLID = ('MAIN_plug_env', 'MAIN_PS1_tol', 'PI5_components_env', 'TOUCH_components_env', 'USBA_cable_env')
PCIN = adsk.fusion.PointContainment.PointInsidePointContainment


def run(_context):
    st = {'mode': MODE}
    t0 = time.time()
    try:
        X = K()
        c = cache()
        if MODE == 'probe':
            sh = crop(X, 'exh', 'HOUSING_F_front', (-62, 62, -80, -10, 156, 178))
            A = {}
            for z in (160.0, 161.8, 164.0, 166.25, 168.5, 170.6, 172.0):
                for x in (-47.0, -45.5, -44.0, -40.0, -20.0, -7.0, -6.0, 0.0, 6.0, 7.0, 20.0, 40.0, 44.0, 45.5, 47.0):
                    A['z%g x%g' % (z, x)] = ivals(X, X.wbox(x - 0.02, x + 0.02, -80, -10, z - 0.02, z + 0.02), sh, 1)
            st['back wall, y of material'] = A
            st['door box'] = wext(X.body('HOUSING_F_door'))
            dr = crop(X, 'door_mid', 'HOUSING_F_door', (-32, 50, -100, -30, 60, 116))
            B = {}
            for z in (63.0, 65.0, 67.0, 80.0, 95.0, 103.0, 107.0, 109.0, 111.0, 113.0):
                for x in (-27.0, -24.0, -21.0, 0.0, 3.0, 36.0, 39.0, 42.0, 45.0):
                    B['z%g x%g' % (z, x)] = ivals(X, X.wbox(x - 0.02, x + 0.02, -100, -30, z - 0.02, z + 0.02), dr, 1)
            st['door, y of material'] = B
            fb = {}
            for n in ('RENDER_FABRIC_front', 'RENDER_FABRIC_door'):
                b = X.body(n)
                fb[n] = None if b is None else [round(X.vol(b), 1), b.lumps.count]
            st['cloth bodies'] = fb
        elif MODE == 'intake':
            P = tcopy(X, 'FLOOR_PLATE')
            fld = X.wbox(-42.0, 41.0, -59.0, -6.0, 1.0, 1.5)
            full = X.vol(fld)
            st['open area mm2'] = round((full - solid(X, fld, P)) / 0.5, 1)
            for (za, zb) in ((0.1, 0.3), (0.6, 0.8), (1.6, 1.8), (2.2, 2.4)):
                s = X.wbox(-42.0, 41.0, -59.0, -6.0, za, zb)
                st['open area mm2 at z %.1f..%.1f' % (za, zb)] = round((X.vol(s) - solid(X, s, P)) / (zb - za), 1)
            n = 0
            for fc in X.body('FLOOR_PLATE').faces:
                g = fc.geometry
                if g.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType and abs(g.radius * 10 - 1.0) < 0.02:
                    n += 1
            st['cylinder faces r 1.0'] = n
            st['475 x dia 2.0 by arithmetic'] = round(475 * math.pi, 1)
        elif MODE == 'rows':
            sh = crop(X, 'exh', 'HOUSING_F_front', (-62, 62, -80, -10, 156, 178))
            # VAR 'low' (j5a, 2026-11-12): the wall is read under the row only and the slice ends at the row's top edge, so that the
            #   roof above the upper row (from z 170.3) is not taken for part of the opening
            VAR = globals().get('VAR', '')
            res = c.setdefault('j5a_rows' + VAR, {})
            left = 0
            for ri, (z0, z1) in enumerate(ROWS):
                for i in range(-50, 50):
                    k = '%d|%d' % (ri, i)
                    if k in res:
                        continue
                    if time.time() - t0 > BUDGET:
                        left += 1; continue
                    xm = i + 0.5
                    ys = []
                    for zz in ((z0 - 0.6,) if VAR == 'low' else (z0 - 0.6, z1 + 0.6)):
                        iv = ivals(X, X.wbox(xm - 0.02, xm + 0.02, -80, -10, zz - 0.02, zz + 0.02), sh, 1)
                        if iv:
                            ys += iv[0]
                    if not ys:
                        res[k] = None; continue
                    ya, yb = min(ys), max(ys)
                    best = None
                    y = ya - 0.25
                    while y <= yb + 0.05:
                        s = X.wbox(i, i + 1.0, y, y + 0.2, z0 - 0.4, z1 + (0.0 if VAR == 'low' else 0.4))
                        full = X.vol(s); sv = solid(X, s, sh)
                        if sv > (0.1 if VAR == 'low' else 0.2) * full:
                            a = (full - sv) / 0.2
                            if best is None or a < best[0]:
                                best = [round(a, 3), round(y, 2)]
                        y += 0.25
                    res[k] = [best, round(ya, 2), round(yb, 2)]
            st['left'] = left
            out = {}
            for ri, (z0, z1) in enumerate(ROWS):
                tot = 0.0; strips = []
                for i in range(-50, 50):
                    r = res.get('%d|%d' % (ri, i))
                    if r is None or r[0] is None:
                        continue
                    tot += r[0][0]
                    strips.append([i, r[0][0], r[0][1]])
                opn = [s for s in strips if s[1] > 0.05]
                out['row z %.1f..%.1f' % (z0, z1)] = {'open mm2': round(tot, 1), 'x from': opn[0][0] if opn else None, 'x to': opn[-1][0] + 1 if opn else None,
                                                     'strips (x, open mm2 per 1.0, y of the slice)': strips}
            st['rows'] = out
        elif MODE == 'slots':
            res = c.setdefault('j5a_slots', {})
            left = 0
            for xc in SLOTS:
                if time.time() - t0 > BUDGET:
                    left += sum(1 for j in range(62, 114) if '%g|%d' % (xc, j) not in res); continue
                dr = crop(X, 'slot%g' % xc, 'HOUSING_F_door', (xc - 3.4, xc + 3.4, -100, -30, 60, 116))
                for j in range(62, 114):
                    k = '%g|%d' % (xc, j)
                    if k in res:
                        continue
                    if time.time() - t0 > BUDGET:
                        left += 1; continue
                    zm = j + 0.5
                    iv = None
                    for xn in (xc + 3.0, xc - 3.0):
                        iv = ivals(X, X.wbox(xn - 0.02, xn + 0.02, -100, -30, zm - 0.02, zm + 0.02), dr, 1)
                        if iv:
                            break
                    if not iv:
                        res[k] = None; continue
                    ya, yb = iv[0]
                    best = None
                    y = ya
                    while y <= yb - 0.2 + 0.001:
                        s = X.wbox(xc - 2.0, xc + 2.0, y, y + 0.2, j, j + 1.0)
                        full = X.vol(s); sv = solid(X, s, dr)
                        a = (full - sv) / 0.2
                        if best is None or a < best[0]:
                            best = [round(a, 3), round(y, 2)]
                        y += 0.25
                    res[k] = [best, ya, yb]
            st['left'] = left
            out = {}; total = 0.0
            for xc in SLOTS:
                tot = 0.0; zs = []
                for j in range(62, 114):
                    r = res.get('%g|%d' % (xc, j))
                    if r is None or r[0] is None:
                        continue
                    tot += r[0][0]
                    if r[0][0] > 0.05:
                        zs.append([j, r[0][0]])
                out['slot x %g' % xc] = {'open mm2': round(tot, 1), 'z from': zs[0][0] if zs else None, 'z to': zs[-1][0] + 1 if zs else None,
                                         'widest strip mm2 per 1.0': max(z[1] for z in zs) if zs else None,
                                         'first / last strip': [zs[0][1], zs[-1][1]] if zs else None}
                total += tot
            st['slots'] = out; st['door slots total mm2'] = round(total, 1)
        elif MODE == 'path':
            res = c.setdefault('j5a_path', {})
            tools = [b.name for b in current(X, leads=False, kos=False) if b.name not in NOT_SOLID]
            tools += [n for n in ('RENDER_FABRIC_front', 'RENDER_FABRIC_door') if X.body(n) is not None]
            st['solid bodies'] = len(tools)
            left = 0
            for z in HEIGHTS:
                k = 'z%g' % z
                if k in res:
                    continue
                if time.time() - t0 > BUDGET:
                    left += 1; continue
                box = (-112.0, 112.0, -100.0, 14.0)
                s = X.wbox(box[0], box[1], box[2], box[3], z, z + 0.4)
                for n in tools:
                    b = X.body(n)
                    if not s.boundingBox.intersects(b.boundingBox):
                        continue
                    try:
                        X.tbm.booleanOperation(s, tcopy(X, n), BT.DifferenceBooleanType)
                    except Exception:
                        st.setdefault('boolean failed', []).append([k, n])
                rows = []
                for l in s.lumps:
                    if l.vertices.count > 3000:
                        e = None
                    else:
                        q = [W(v.geometry) for v in l.vertices]
                        e = [round(f(p[i] for p in q), 1) for i in range(2) for f in (min, max)]
                    a = l.volume * 1000.0 / 0.4
                    outer = e is None or e[0] < box[0] + 0.2 or e[1] > box[1] - 0.2 or e[2] < box[2] + 0.2 or e[3] > box[3] - 0.2
                    if outer or a < 3.0:
                        continue
                    main = False
                    for py in (-45.0, -50.0, -55.0, -60.0, -40.0, -35.0):
                        try:
                            if l.pointContainment(Wp(2.5, py, z + 0.2)) == PCIN:
                                main = True; break
                        except Exception:
                            pass
                    rows.append([round(a, 1), e, main])
                res[k] = sorted(rows, key=lambda r: -r[0])
            st['left'] = left
            st['path'] = {k: res[k] for k in ('z%g' % z for z in HEIGHTS) if k in res}
        elif MODE == 'path2':
            # as 'path', but the slice is first cut to the unit's outer form (REF_F_outer), so the door's joint and the cloth's seams no
            #   longer make the cavity part of the outside. Per height: every pocket of air between the boxes (it holds at least one point of
            #   a grid x -30..30, y -75..-10), its area and box; for the largest, the share on the door's side of the board's door-side face
            #   (depth 32.7), on the display's side of its back face (31.1) and in between.
            res = c.setdefault('j5a_path2', {})
            tools = [b.name for b in current(X, leads=False, kos=False) if b.name not in NOT_SOLID]
            tools += [n for n in ('RENDER_FABRIC_front', 'RENDER_FABRIC_door') if X.body(n) is not None]
            st['solid bodies'] = len(tools)
            H2 = globals().get('HEIGHTS2', (4, 8, 12, 20, 28, 35, 45, 55, 65, 75, 82, 90, 100, 110, 120, 130, 137, 140, 145, 150, 155, 160, 164, 168.5))
            grid = [(gx, gy) for gx in (-30.0, -15.0, 0.0, 2.5, 15.0, 30.0) for gy in range(-75, -9, 5)]
            left = 0
            for z in H2:
                k = 'z%g' % z
                if k in res:
                    continue
                if time.time() - t0 > BUDGET:
                    left += 1; continue
                s = X.wbox(-112.0, 112.0, -100.0, 14.0, z, z + 0.4)
                X.tbm.booleanOperation(s, tcopy(X, 'REF_F_outer'), BT.IntersectionBooleanType)
                for n in tools:
                    b = X.body(n)
                    if not s.boundingBox.intersects(b.boundingBox):
                        continue
                    try:
                        X.tbm.booleanOperation(s, tcopy(X, n), BT.DifferenceBooleanType)
                    except Exception:
                        st.setdefault('boolean failed', []).append([k, n])
                rows = []
                for l in s.lumps:
                    a = l.volume * 1000.0 / 0.4
                    if a < 3.0:
                        continue
                    bb = l.boundingBox
                    q = [W(bb.minPoint), W(bb.maxPoint)]
                    e = [round(f(p[i] for p in q), 1) for i in range(2) for f in (min, max)]
                    hits = 0
                    for (gx, gy) in grid:
                        if gx < e[0] or gx > e[1] or gy < e[2] or gy > e[3]:
                            continue
                        try:
                            if l.pointContainment(Wp(gx, gy, z + 0.2)) == PCIN:
                                hits += 1
                        except Exception:
                            pass
                    if hits:
                        rows.append([round(a, 1), e, hits, l])
                rows.sort(key=lambda r: -r[0])
                out = []
                for i, r in enumerate(rows):
                    row = {'area mm2': r[0], 'box x0 x1 y0 y1': r[1], 'grid points': r[2]}
                    if i == 0:
                        try:
                            for (nm, d0, d1) in (('door side of the board', 32.7, 300.0), ('display side of the board', -60.0, 31.1), ('in the board\'s thickness', 31.1, 32.7)):
                                t = X.tbm.copy(r[3])
                                X.tbm.booleanOperation(t, X.dbox(-150.0, 150.0, d0, d1, -150.0, 350.0), BT.IntersectionBooleanType)
                                row[nm] = round(t.volume * 1000.0 / 0.4, 1)
                        except Exception:
                            row['split failed'] = traceback.format_exc().splitlines()[-1]
                    out.append(row)
                res[k] = out
            st['left'] = left
            st['path'] = {k: res[k] for k in ('z%g' % z for z in H2) if k in res}
            und = {}
            P = tcopy(X, 'FLOOR_PLATE'); PI = tcopy(X, 'PI5_F')
            for (ux, uy) in ((-30.0, -50.0), (0.0, -50.0), (30.0, -50.0), (-30.0, -30.0), (0.0, -30.0), (30.0, -30.0), (-30.0, -12.0), (0.0, -12.0), (30.0, -12.0)):
                nd = X.wbox(ux - 0.02, ux + 0.02, uy - 0.02, uy + 0.02, -1.0, 40.0)
                und['x%g y%g' % (ux, uy)] = {'plate z': ivals(X, nd, P, 2), 'Pi z': ivals(X, nd, PI, 2)}
            st['under the Pi (needles along z)'] = und
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('j5a_' + MODE + globals().get('VAR', ''), st)


run(None)
