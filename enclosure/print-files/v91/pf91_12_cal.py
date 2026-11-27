# Print files of version 91, block 1: the calibration plate. READ-ONLY on the design: the new block is built from temporary B-rep
# bodies (TemporaryBRepManager), never added to the document.
# The plate is version 67's (frame 120 / 108 / 5; tower 20 x 20 x 30; hole block 40 x 16 x 8 with the lug and its lying 2.7 pilot,
# printed solid; print_files_v67/_work/orient/, copied and checked by sha256) with D473's four additions on a second block,
# 40 x 16 x 8, printed solid like the first (my layout and depths, under D150; each listed in the sheet):
#   P16a, P16b  two upright pilots 1.6 across, 7.0 deep from the top (an M2 x 6 driven with its head on the top face: 1.0 of room);
#   P16L        one lying pilot 1.6 across, 7.0 deep from the front face, its axis at bed z 4.00 (the holder's pilots lie at bed 4.00);
#   P27L        one lying pilot 2.7 across, 9.0 deep from the back face, its axis at bed z 4.15 (the boxes' clip pilot lies at bed
#               42.55: the same place in the layers), for an M3 x 8 driven with its head on the face: 1.0 of room;
#   H20         one hole 2.0 across, standing, through the block from the first layer (the cap's openings);
#   H40W        one standing hole 4.0 across, 6.5 deep from the top, with 1.6 of wall to the block's end face (D472; PR47).
#   build(): the block as a temporary body, meshed at 0.01 mm and 10 deg, to stl/cal/cal_add_v91.stl; its volume and the holes' list.
#   copies(): version 67's three meshes into stl/cal/, sha256 checked; the bounding box of each.
import os, json, math, time, struct, shutil, runpy
L = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pf91_lib.py'))
CAL = os.path.join(L['W'], 'stl', 'cal')
BX, BY, BZ = 40.0, 16.0, 8.0
FEAT = [  # name, kind, axis start (mm, block frame: x 0..40, y 0..16, z 0..8), axis end, diameter
    ('P16a', 'upright pilot 1.6, 7.0 deep', (5.0, 5.0, 1.0), (5.0, 5.0, 8.5), 1.6),
    ('P16b', 'upright pilot 1.6, 7.0 deep', (5.0, 11.0, 1.0), (5.0, 11.0, 8.5), 1.6),
    ('H20', 'standing hole 2.0, through', (12.0, 8.0, -0.5), (12.0, 8.0, 8.5), 2.0),
    ('P16L', 'lying pilot 1.6, 7.0 deep from y 0', (19.0, -0.5, 4.0), (19.0, 7.0, 4.0), 1.6),
    ('P27L', 'lying pilot 2.7, 9.0 deep from y 16', (28.0, 7.0, 4.15), (28.0, 16.5, 4.15), 2.7),
    ('H40W', 'standing hole 4.0, 6.5 deep, 1.6 of wall to x 40', (36.4, 8.0, 1.5), (36.4, 8.0, 8.5), 4.0),
]


def _bbox(p):
    b = open(p, 'rb').read(); n = struct.unpack_from('<I', b, 80)[0]; lo = [1e9] * 3; hi = [-1e9] * 3
    for t in range(n):
        f = struct.unpack_from('<9f', b, 84 + 50 * t + 12)
        for k in range(9):
            i = k % 3; lo[i] = min(lo[i], f[k]); hi[i] = max(hi[i], f[k])
    return n, [round(c, 3) for c in lo], [round(c, 3) for c in hi]


def copies():
    os.makedirs(CAL, exist_ok=True)
    for f in ('cal_frame.stl', 'cal_tower.stl', 'cal_holes_v67.stl'):
        a = os.path.join(L['PF67'], 'orient', f); b = os.path.join(CAL, f); shutil.copy2(a, b)
        n, lo, hi = _bbox(b)
        print('%-18s sha256 %s same %s | %d triangles, box %s .. %s' % (f, L['sha'](b)[:16], L['sha'](a) == L['sha'](b), n, lo, hi))


def build():
    import adsk.core, adsk.fusion
    t0 = time.time(); rep, root = L['guard'](strict=True)
    tbm = adsk.fusion.TemporaryBRepManager.get()
    P = lambda x, y, z: adsk.core.Point3D.create(x / 10.0, y / 10.0, z / 10.0)
    obb = adsk.core.OrientedBoundingBox3D.create(P(BX / 2, BY / 2, BZ / 2), adsk.core.Vector3D.create(1, 0, 0), adsk.core.Vector3D.create(0, 1, 0),
                                                 BX / 10.0, BY / 10.0, BZ / 10.0)
    body = tbm.createBox(obb); v0 = body.volume * 1000.0; rec = []
    for (nm, kind, a, b, d) in FEAT:
        cyl = tbm.createCylinderOrCone(P(*a), d / 20.0, P(*b), d / 20.0)
        before = body.volume * 1000.0
        ok = tbm.booleanOperation(body, cyl, adsk.fusion.BooleanTypes.DifferenceBooleanType)
        rec.append({'name': nm, 'kind': kind, 'A': a, 'B': b, 'd': d, 'ok': ok, 'removed_mm3': round(before - body.volume * 1000.0, 3)})
    mc = body.meshManager.createMeshCalculator(); mc.surfaceTolerance = 0.001; mc.maxNormalDeviation = math.radians(10.0)
    m = mc.calculate(); c = m.nodeCoordinatesAsDouble
    Pm = [(c[i] * 10 - BX / 2, c[i + 1] * 10 - BY / 2, c[i + 2] * 10) for i in range(0, len(c), 3)]
    ix = m.nodeIndices; T = [(ix[t], ix[t + 1], ix[t + 2]) for t in range(0, len(ix), 3)]
    os.makedirs(CAL, exist_ok=True)
    n = L['write_stl'](os.path.join(CAL, 'cal_add_v91.stl'), Pm, T, 'cal_add_v91')
    out = {'block_mm': [BX, BY, BZ], 'box_mm3': round(v0, 3), 'vol_mm3': round(body.volume * 1000.0, 3), 'lumps': body.lumps.count, 'tris': n,
           'frame': 'stl x = block x - 20, y = block y - 8, z = block z', 'features': rec, 's': round(time.time() - t0, 1)}
    rep2, _ = L['guard'](strict=True); out['modified_after'] = rep2['modified']
    L['jdump']('pf91_12_cal.json', out)
    print(json.dumps(out, indent=1))
    print('bbox', _bbox(os.path.join(CAL, 'cal_add_v91.stl')))
# END pf91_12_cal.py
