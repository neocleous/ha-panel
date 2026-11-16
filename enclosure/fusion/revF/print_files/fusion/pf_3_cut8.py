# pf_3_cut8 (block 2, the adhesion test). READ-ONLY on the design (connector readOnly: true): a temporary copy of the shell
#   (TemporaryBRepManager, never added to the design) is intersected with a box that keeps the shell's first 8.0 mm in its
#   print orientation (chin face down: bed z = 6.7992 - world y, so world y >= -1.2008). Writes exports/shell_chin8.stl (world mm,
#   0.01 chordal) and orient/shell_chin8_plan.stl (the shell's own world->bed matrix from pf_2_orient), with volume and bounds.
R2_ZCUT = 8.0


def run(_context):
    t0 = time.time(); X = R2Ctx(); r2_guard(X, strict=True)
    shell = X.body('HOUSING_F_front')
    tb = X.tbm.copy(shell)
    y0 = 6.7992 - R2_ZCUT                            # world y of bed z 8.0
    y1, x0, x1, z0, z1 = 80.0, -200.0, 200.0, -60.0, 360.0
    wc = (0.5 * (x0 + x1), 0.5 * (y0 + y1), 0.5 * (z0 + z1))
    # world -> design (cm): x = (x_rel + XC)/10; y_d = (C*y + S*(z - H))/10; z_d = (-S*y + C*(z - H))/10
    cx = (wc[0] + R2_XC) / 10.0; cy = (R2_C * wc[1] + R2_S * (wc[2] - R2_H)) / 10.0; cz = (-R2_S * wc[1] + R2_C * (wc[2] - R2_H)) / 10.0
    obb = adsk.core.OrientedBoundingBox3D.create(adsk.core.Point3D.create(cx, cy, cz), adsk.core.Vector3D.create(1, 0, 0),
                                                 adsk.core.Vector3D.create(0, R2_C, -R2_S),
                                                 (x1 - x0) / 10.0, (y1 - y0) / 10.0, (z1 - z0) / 10.0)
    box = X.tbm.createBox(obb)
    ok = X.tbm.booleanOperation(tb, box, adsk.fusion.BooleanTypes.IntersectionBooleanType)
    vol = tb.volume * 1000.0
    P, T = r2_world_mesh(tb, 0.01)
    ys = [p[1] for p in P]
    p = os.path.join(R2_DIR, 'exports', 'shell_chin8.stl')
    n = r2_write_stl(p, P, T, 'shell_chin8')
    rec = json.load(open(os.path.join(R2_DIR, 'data', 'pf_2_orient.json')))
    M = rec['shell']['M']
    b = open(p, 'rb').read(); o = bytearray(len(b)); o[0:80] = b'HA panel print files shell_chin8 bed mm'.ljust(80, b' ')
    struct.pack_into('<I', o, 80, n)
    lo = [1e9] * 3; hi = [-1e9] * 3
    for t in range(n):
        f = struct.unpack_from('<12f', b, 84 + 50 * t); v = []
        for k0 in (3, 6, 9):
            x, y, z = f[k0], f[k0 + 1], f[k0 + 2]
            q = [M[r][0] * x + M[r][1] * y + M[r][2] * z + M[r][3] for r in range(3)]
            for k in range(3):
                if q[k] < lo[k]: lo[k] = q[k]
                if q[k] > hi[k]: hi[k] = q[k]
            v += q
        N = [M[r][0] * f[0] + M[r][1] * f[1] + M[r][2] * f[2] for r in range(3)]
        struct.pack_into('<12fH', o, 84 + 50 * t, N[0], N[1], N[2], *v, 0)
    open(os.path.join(R2_DIR, 'orient', 'shell_chin8_plan.stl'), 'wb').write(o)
    out = {'bool_ok': ok, 'vol_mm3': round(vol, 3), 'lumps': tb.lumps.count, 'tris': n, 'world_y': [round(min(ys), 4), round(max(ys), 4)],
           'bed_lo': [round(c, 4) for c in lo], 'bed_hi': [round(c, 4) for c in hi], 'bytes': len(o), 's': round(time.time() - t0, 1)}
    r2_guard(X, strict=True)
    r2_out(os.path.join(R2_DIR, 'data', 'pf_3_cut8.json'), out)
    r2_log('pf_3_cut8', 'run', out)
    print(json.dumps(out))
