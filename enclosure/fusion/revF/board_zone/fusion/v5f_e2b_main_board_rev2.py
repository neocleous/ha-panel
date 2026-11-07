# rev F e2b (2026-11-08): main board rev 2 (electronics MAIN_env rev 2, docs @ 733cb5a) - every SMD part on the front,
#   outline = base of outline T: 90 x 55, x_rel +-45, z 34-89, -x top corner cut (-43, 89) -> (-45, 88.5).
#   MAIN_pcb      y -65.0..-63.4 on that outline.
#   MAIN_front_env  y -63.4..-33.4 (30) for z 35.8-89, y -63.4..-39.2 (24.2, K7) for z 34-35.8; the K5 corner
#                 (x_rel < -41.5, z > 83.5) left out (no parts there).
#   MAIN_back_env y -65.0..-67.9 (2.9, through-hole joints) without the bare top corners (x_rel < -38 or > 43.5, z > 82),
#                 plus J2's courtyard x_rel 19.72-30.28, z 34-43.67 at 3.5 (y -68.5).
#   The old bodies are kept hidden as MAIN_pcb_e2 / MAIN_front_env_e2 / MAIN_back_env_e2. Not saved here (e2d saves).
#   x below is x_rel; Ctx.wbox / Dw take design x = x_rel + XC (the first run missed that; undone by e2b0).
import os, traceback, math
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
GUARD = {'HOUSING_F_front': 235.9107, 'HOUSING_F_door': 47.2633, 'MAIN_BRACKET': 6.5563, 'MAIN_pcb': 7.2,
         'MAIN_front_env': 130.14, 'MAIN_back_env': 15.75}
EXPECT = {'MAIN_pcb': 7.9192, 'MAIN_front_env': 146.9829, 'MAIN_back_env': 14.2437}
OUT = os.path.expanduser('~/Documents/HA_panel_renders/board_zone/e2b_status.json')


def wbb(b):
    bb = b.boundingBox
    pts = [(x, y, z) for x in (bb.minPoint.x, bb.maxPoint.x) for y in (bb.minPoint.y, bb.maxPoint.y) for z in (bb.minPoint.z, bb.maxPoint.z)]
    w = [(p[0] * 10 - XC, (p[1] * C - p[2] * S) * 10, H + (p[1] * S + p[2] * C) * 10) for p in pts]
    return [round(min(q[k] for q in w), 2) for k in range(3)] + [round(max(q[k] for q in w), 2) for k in range(3)]


def run(_context):
    st = {'t0': time.strftime('%H:%M:%S')}
    try:
        X = Ctx(); tbm = X.tbm
        dfile = X.doc.dataFile
        st['version'] = [dfile.versionNumber, dfile.latestVersionNumber]
        bad = []
        for k, v in GUARD.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                bad.append([k, None if b is None else round(b.volume, 4)])
        st['modified_at_start'] = X.doc.isModified          # True after e2b0 (names restored); volumes and names are the guard
        for k in ('MAIN_pcb_e2', 'MAIN_front_env_e2', 'MAIN_back_env_e2'):
            if X.body(k) is not None:
                bad.append(k + ' exists')
        st['guard_bad'] = bad
        if bad:
            raise RuntimeError('GUARD %s' % bad)
        # corner cut: box whose base lies on the line A(-43, 89) - B(-45, 88.5), on the corner's side
        ax, az, bx, bz_ = -43.0, 89.0, -45.0, 88.5
        L = math.hypot(bx - ax, bz_ - az); ux, uz = (bx - ax) / L, (bz_ - az) / L
        nx, nz = -uz, ux                                   # (-0.2425, 0.9701): toward the corner (-45, 89)
        if (-45 - ax) * nx + (89 - az) * nz < 0:
            nx, nz = -nx, -nz
        mx, mz = (ax + bx) / 2, (az + bz_) / 2
        cut = tbm.createBox(adsk.core.OrientedBoundingBox3D.create(
            Dw(XC + mx + nx * 5, -64.2, mz + nz * 5), V3(ux, uz * S, uz * C), WY, 2.0, 1.0, 1.0))
        wb = lambda x0, x1, y0, y1, z0, z1: X.wbox(XC + x0, XC + x1, y0, y1, z0, z1)
        pcb = X.diff(wb(-45, 45, -65.0, -63.4, 34, 89), cut)
        front = X.union(wb(-45, 45, -63.4, -39.2, 34, 35.8), wb(-45, 45, -63.4, -33.4, 35.8, 89))
        front = X.diff(front, wb(-46, -41.5, -64, -33, 83.5, 90))
        back = wb(-45, 45, -67.9, -65.0, 34, 89)
        back = X.diff(back, wb(-46, -38, -68, -64.9, 82, 90))
        back = X.diff(back, wb(43.5, 46, -68, -64.9, 82, 90))
        back = X.union(back, wb(19.72, 30.28, -68.5, -65.0, 34, 43.67))
        xr = [round(pcb.boundingBox.minPoint.x * 10 - XC, 3), round(pcb.boundingBox.maxPoint.x * 10 - XC, 3)]
        st['pcb_x_rel'] = xr
        if abs(xr[0] + 45) > 0.01 or abs(xr[1] - 45) > 0.01:
            raise RuntimeError('placement check: MAIN_pcb x_rel %s' % xr)
        vols = {'MAIN_pcb': pcb.volume, 'MAIN_front_env': front.volume, 'MAIN_back_env': back.volume}
        st['temp_vol'] = {k: round(v, 4) for k, v in vols.items()}
        off = {k: round(vols[k] - EXPECT[k], 4) for k in EXPECT if abs(vols[k] - EXPECT[k]) > 0.002}
        if off:
            raise RuntimeError('volume check %s' % off)
        st['lumps'] = {'MAIN_pcb': pcb.lumps.count if hasattr(pcb, 'lumps') else None}
        renamed = {}
        for k in ('MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env'):
            b = X.body(k); b.name = k + '_e2'; b.isLightBulbOn = False; renamed[k] = b.name
        st['renamed'] = renamed
        new = {}
        for k, tb in (('MAIN_pcb', pcb), ('MAIN_front_env', front), ('MAIN_back_env', back)):
            b = X.add(tb, k); b.isLightBulbOn = False
            new[k] = {'vol': round(b.volume, 4), 'lumps': b.lumps.count, 'faces': b.faces.count, 'world_bb': wbb(b)}
        st['new'] = new
        log('v5f_e2b_main_board_rev2', 'done', {'renamed': renamed, 'new': new})
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    json.dump(st, open(OUT, 'w'), indent=1)
    print(json.dumps(st))


run(None)
