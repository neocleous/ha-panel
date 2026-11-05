# rev F block 6w-2c (2026-11-05), read-only: B6w-2b found the door's union fine (50.889 cm³, 1 lump) and the front's failing
#   in two regions: chin (y > −3: 3.36 mm³ over ≈ 14 000 mm², i.e. a sheet ≈ 0.0002 thick where the wall is vertical) and
#   z 60–160 (464.4 mm³); z < 60 and z > 160 join.
#   Variant V2 (no boundary of the fill coplanar with an earlier cut of the same part): slot_in grown 0.05 (d < 15.65, Z >
#   −94.35), VEML window m 0.55, exhaust / BME680 slot tools grown 0.05 per side, top at z 175.2; chin masked (y > −3).
#   Tests: V2 front whole; V2 z 60–160 region; if that fails, its 12 sub-boxes (x ±, y −3…−20 / −20…−40 / −40…−52.5,
#   z 60–110 / 110–160), each with the body cropped (3 mm margin).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
PILOTS = [(52.75, 10.25), (52.75, 45.75), (-52.75, 10.25), (-52.75, 45.75)]
G = 0.05
P0 = (-76.82, -45.0, 92.0); NW = (0.751, 0.643, -0.150)


def bme_tool(X, grow):
    n = NW; L = math.sqrt(sum(c * c for c in n)); n = tuple(c / L for c in n)
    th = math.hypot(n[0], n[1]); t = (n[1] / th, -n[0] / th, 0.0)
    u = (t[1] * n[2] - t[2] * n[1], t[2] * n[0] - t[0] * n[2], t[0] * n[1] - t[1] * n[0])
    if u[2] < 0:
        u = tuple(-c for c in u)
    sl = None
    for s in (-3.0, 3.0):
        c = tuple(P0[k] + u[k] * s - n[k] * 2.25 for k in range(3))
        bx = lbox(X, c, t, u, 14.0 + 2 * grow, 3.0 + 2 * grow, 7.5)
        sl = bx if sl is None else X.union(sl, bx)
    return sl


def front_fill_v2(X, out):
    fill = tb_copy(X, 'TOOL_outer_skin_3p2_F')
    inter(X, fill, X.wbox(-250, 250, -250, 250, 6.5, TOP_Z - 0.1))
    cav = tb_copy(X, 'INNER_E'); X.diff(cav, tb_copy(X, 'TOOL_inner_skin_0p7'))
    inter(X, fill, cav)
    spk = None
    for s in (1, -1):
        c = X.tbm.createCylinderOrCone(Dw(XC + s * 70.5, -10.0, 28.0), 2.05, Dw(XC + s * 70.5, 10.0, 28.0), 2.05)
        spk = c if spk is None else X.union(spk, c)
    pil = None
    for (xr, z) in PILOTS:
        c = X.tbm.createCylinderOrCone(Dw(XC + xr, -1.0, z), 0.16, Dw(XC + xr, 6.0, z), 0.16)
        pil = c if pil is None else X.union(pil, c)
    lap = tb_copy(X, 'TOOL_inner_skin_2p1'); inter(X, lap, X.wbox(-250, 250, -67.0, -52.5, 5.5, 260))
    sin = dbox(X, -250, 250, -15.6 - G, 60.0, -94.3 - G, 260.0)
    for v in (sin, veml_excl(X, 0.5 + G), ld_excl(X), lap, spk, pil, X.wbox(-250, 250, -3.0, 250, -20, 260)):
        X.diff(fill, v)
    fs = X.wbox(-250, 250, -52.0, 250, -20, 260); X.union(fs, tb_copy(X, 'TOOL_seam_RF'))
    inter(X, fill, fs)
    ex = X.union(X.wbox(XC - 45 - G, XC + 45 + G, -62, -40, 167.0 - G, 170.0 + G), X.wbox(XC - 45 - G, XC + 45 + G, -62, -40, 171.5 - G, 174.5 + G))
    X.diff(fill, ex); X.diff(fill, bme_tool(X, G))
    out['v2_front_mm3_lumps'] = [round(fill.volume * 1000, 2), fill.lumps.count]
    return fill


def utest(X, body, piece, box=None):
    pc = X.tbm.copy(piece)
    if box is not None:
        inter(X, pc, X.wbox(-250, 250, box[0], box[1], box[2], box[3]) if len(box) == 4 else X.wbox(XC + box[0], XC + box[1], box[2], box[3], box[4], box[5]))
    if pc.volume <= 0:
        return 'empty'
    row = [round(pc.volume * 1000, 3), pc.lumps.count]
    bc = X.tbm.copy(body)
    if box is not None:
        b6 = box if len(box) == 6 else (-250, 250) + tuple(box)
        inter(X, bc, X.wbox(XC + b6[0] - 3, XC + b6[1] + 3, b6[2] - 3, b6[3] + 3, b6[4] - 3, b6[5] + 3))
    try:
        X.union(bc, pc); row += ['ok', bc.lumps.count]
    except Exception as e:
        row += ['fail', str(e)[:40]]
    return row


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        fb = X.body('HOUSING_F_front')
        f2 = front_fill_v2(X, out)
        out['t_fill_s'] = round(time.time() - t0, 1)
        out['v2_whole'] = utest(X, fb, f2)
        out['t_whole_s'] = round(time.time() - t0, 1)
        log('v5f_b6w2c_union_diag2', 'whole', {k: out[k] for k in out})
        if out['v2_whole'][2:3] != ['ok']:
            out['v2_mid'] = utest(X, fb, f2, (-250.0, -3.0, 60.0, 160.0))
            if out['v2_mid'][2:3] != ['ok']:
                sub = {}
                for xs, (x0, x1) in (('+x', (0.0, 250.0)), ('-x', (-250.0, 0.0))):
                    for (y0, y1) in ((-20.0, -3.0), (-40.0, -20.0), (-52.5, -40.0)):
                        for (z0, z1) in ((60.0, 110.0), (110.0, 160.0)):
                            sub['%s_y%g..%g_z%g..%g' % (xs, y0, y1, z0, z1)] = utest(X, fb, f2, (x0, x1, y0, y1, z0, z1))
                out['v2_mid_sub_[mm3, lumps, union, lumps]'] = sub
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b6w2c_union_diag2', 'diag', out)
    print(json.dumps(out, separators=(',', ':')))
