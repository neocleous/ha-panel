# rev F block 6w (2026-11-05): shared fill definition for decision 1 (a), exec'd by v5f_b6w2* (copy at ~/Documents/).
#   Needs v5f_common.py and v5f_b5_common.py first.
#   fill = TOOL_outer_skin_3p2_F ∩ (INNER_E − TOOL_inner_skin_0p7) ∩ z 6.5…175.3 − slot_in − VEML / LD2410C windows
#          − lap zone (TOOL_inner_skin_2p1 ∩ y −67…−52.5, z ≥ 5.5) − speaker bores / lattices (r 20.5) − clamp pilots (r 1.6)
#          − MASK (extra exclusion boxes, world [x_rel0, x_rel1, y0, y1, z0, z1]; empty by default)
#   front part = fill ∩ (y > −52 ∪ TOOL_seam_RF) − exhaust / BME680 slot tools
#   door part  = fill − (y > −52) − TOOL_seam_RD − inlet cutout − grommet pin holes − door-boss insert holes
ZC = 20.6
DB = [(50.0, -67.0), (-50.0, -67.0), (19.0, -74.5), (-19.0, -77.0)]
PILOTS = [(52.75, 10.25), (52.75, 45.75), (-52.75, 10.25), (-52.75, 45.75)]
try:
    MASK
except NameError:
    MASK = []


def build_fill(X, out):
    fill = tb_copy(X, 'TOOL_outer_skin_3p2_F')
    inter(X, fill, X.wbox(-250, 250, -250, 250, 6.5, TOP_Z))
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
    for v in (slot_in(X), veml_excl(X), ld_excl(X), lap, spk, pil):
        X.diff(fill, v)
    for m in MASK:
        X.diff(fill, X.wbox(XC + m[0], XC + m[1], m[2], m[3], m[4], m[5]))
    fs = X.wbox(-250, 250, -52.0, 250, -20, 260); X.union(fs, tb_copy(X, 'TOOL_seam_RF'))
    fpart = X.tbm.copy(fill); inter(X, fpart, X.tbm.copy(fs))
    X.diff(fpart, tb_copy(X, 'TOOL_exhaust_slots')); X.diff(fpart, tb_copy(X, 'TOOL_bme680_slots'))
    dpart = X.tbm.copy(fill); X.diff(dpart, X.tbm.copy(fs)); X.diff(dpart, tb_copy(X, 'TOOL_seam_RD'))
    X.diff(dpart, X.wbox(XC - 12.2, XC + 12.2, -88.0, -79.0, ZC - 7.3, ZC + 7.3))
    for sx in (1, -1):
        X.diff(dpart, X.tbm.createCylinderOrCone(Dw(XC + sx * 13.6, -88.0, ZC), 0.105, Dw(XC + sx * 13.6, -79.0, ZC), 0.105))
    for (xr, y) in DB:
        X.diff(dpart, X.wcyl_z(XC + xr, y, 2.0, 2.3, 9.5))
    out['fill_mm3_lumps'] = [round(fill.volume * 1000, 2), fill.lumps.count]
    out['parts_mm3_lumps'] = {'front': [round(fpart.volume * 1000, 2), fpart.lumps.count], 'door': [round(dpart.volume * 1000, 2), dpart.lumps.count]}
    return fpart, dpart
