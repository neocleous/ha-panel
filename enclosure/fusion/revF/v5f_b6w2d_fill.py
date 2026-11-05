# rev F block 6w-2d (2026-11-05): fill definition V3 for decision 1 (a), exec'd by v5f_b6w2d_wall_fill.py (copy at
#   ~/Documents/). Needs v5f_common.py and v5f_b5_common.py first.
#   Why V3: with the exact 3.2 skin the fill is a sheet ≈ 0.0002 thick where the wall is vertical, and boundaries of the fill
#   that lie in the planes of earlier cuts of the same part (slot zone, VEML window, exhaust / BME680 slots) make the front's
#   union fail (B6w-2b: chin and z 60–160 regions ASM_INCONS_FACE; B6w-2c: the offsets fix z 60–160, the whole still fails,
#   ASM_BODY_VERTEX_CRUMBLE, at the thin sheet's cut edges).
#   fill = TOOL_outer_skin_3p22_F (3.22 below the cloth face: wall 2.52 normal, sheet ≥ 0.02 thick) ∩ (INNER_E −
#          TOOL_inner_skin_0p7) ∩ z 6.5…175.2 − slot zone grown 0.05 (d < 15.65, Z > −94.35) − VEML window (m 0.55)
#          − LD2410C window − lap zone (TOOL_inner_skin_2p1 ∩ y −67…−52.5, z ≥ 5.5) − speaker bores / lattices (r 20.5)
#          − clamp pilots (r 1.6) − chin (y > −3: vertical, already 2.50; the touch PCB lies on it)
#   front part = fill ∩ (y ≥ −52.5) − exhaust slots grown 0.05 − BME680 slots grown 0.05
#   door part  = fill ∩ (y ≤ −67.0) − inlet cutout grown 0.05 − pin holes r 1.10 − door-boss insert holes
SKIN = 'TOOL_outer_skin_3p22_F'
G = 0.05
ZC = 20.6
DB = [(50.0, -67.0), (-50.0, -67.0), (19.0, -74.5), (-19.0, -77.0)]
PILOTS = [(52.75, 10.25), (52.75, 45.75), (-52.75, 10.25), (-52.75, 45.75)]
BME_P0 = (-76.82, -45.0, 92.0); BME_NW = (0.751, 0.643, -0.150)


def bme_slots(X, grow):
    n = BME_NW; L = math.sqrt(sum(c * c for c in n)); n = tuple(c / L for c in n)
    th = math.hypot(n[0], n[1]); t = (n[1] / th, -n[0] / th, 0.0)
    u = (t[1] * n[2] - t[2] * n[1], t[2] * n[0] - t[0] * n[2], t[0] * n[1] - t[1] * n[0])
    if u[2] < 0:
        u = tuple(-c for c in u)
    sl = None
    for s in (-3.0, 3.0):
        c = tuple(BME_P0[k] + u[k] * s - n[k] * 2.25 for k in range(3))
        bx = lbox(X, c, t, u, 14.0 + 2 * grow, 3.0 + 2 * grow, 7.5)
        sl = bx if sl is None else X.union(sl, bx)
    return sl


def build_fill(X, out):
    fill = tb_copy(X, SKIN)
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
    for v in (dbox(X, -250, 250, -15.6 - G, 60.0, -94.3 - G, 260.0), veml_excl(X, 0.5 + G), ld_excl(X), lap, spk, pil,
              X.wbox(-250, 250, -3.0, 250, -20, 260)):
        X.diff(fill, v)
    fpart = X.tbm.copy(fill); inter(X, fpart, X.wbox(-250, 250, -52.5, 250, -20, 260))
    X.diff(fpart, X.union(X.wbox(XC - 45 - G, XC + 45 + G, -62, -40, 167.0 - G, 170.0 + G),
                          X.wbox(XC - 45 - G, XC + 45 + G, -62, -40, 171.5 - G, 174.5 + G)))
    X.diff(fpart, bme_slots(X, G))
    dpart = X.tbm.copy(fill); inter(X, dpart, X.wbox(-250, 250, -250, -67.0, -20, 260))
    X.diff(dpart, X.wbox(XC - 12.2 - G, XC + 12.2 + G, -88.0, -79.0, ZC - 7.3 - G, ZC + 7.3 + G))
    for sx in (1, -1):
        X.diff(dpart, X.tbm.createCylinderOrCone(Dw(XC + sx * 13.6, -88.0, ZC), 0.11, Dw(XC + sx * 13.6, -79.0, ZC), 0.11))
    for (xr, y) in DB:
        X.diff(dpart, X.wcyl_z(XC + xr, y, 2.0, 2.3, 9.5))
    out['fill_mm3_lumps'] = [round(fill.volume * 1000, 2), fill.lumps.count]
    out['parts_mm3_lumps'] = {'front': [round(fpart.volume * 1000, 2), fpart.lumps.count], 'door': [round(dpart.volume * 1000, 2), dpart.lumps.count]}
    rest = X.tbm.copy(fill); X.diff(rest, X.wbox(-250, 250, -52.5, 250, -20, 260)); X.diff(rest, X.wbox(-250, 250, -250, -67.0, -20, 260))
    out['rest_mm3'] = round(rest.volume * 1000, 3)
    return fpart, dpart
