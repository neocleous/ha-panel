# r2_3_orient (block 2 prep): world STL (exports/<tag>.stl) -> oriented STL on the bed (slicer/orient/<tag>_<okey>.stl) with a
#   4x4 world->bed matrix computed in the session (offline/orient2.py). Pure Python (struct). Touches no Fusion object.
#   R2_ARGS: {'jobs': [[tag, okey, [16 numbers row-major]], ...]}. Stops before 70 s.
import struct


def run(_context):
    t0 = time.time(); out = {}
    for tag, okey, M in R2_ARGS['jobs']:
        if time.time() - t0 > 70:
            out[tag] = 'not done (time)'; continue
        src = os.path.join(R2_DIR, 'exports', tag + '.stl'); dst = os.path.join(R2_DIR, 'slicer', 'orient', '%s_%s.stl' % (tag, okey))
        b = open(src, 'rb').read(); n = struct.unpack_from('<I', b, 80)[0]
        a = M; o = bytearray(84 + 50 * n); o[0:80] = ('recheck2 %s %s bed mm' % (tag, okey)).encode().ljust(80, b' ')[:80]
        struct.pack_into('<I', o, 80, n)
        zmin = 1e9; zmax = -1e9; xmin = ymin = 1e9; xmax = ymax = -1e9
        for t in range(n):
            f = struct.unpack_from('<12f', b, 84 + 50 * t)
            v = []
            for k in (3, 6, 9):
                x, y, z = f[k], f[k + 1], f[k + 2]
                X = a[0] * x + a[1] * y + a[2] * z + a[3]; Y = a[4] * x + a[5] * y + a[6] * z + a[7]; Z = a[8] * x + a[9] * y + a[10] * z + a[11]
                v += [X, Y, Z]
                if Z < zmin: zmin = Z
                if Z > zmax: zmax = Z
                if X < xmin: xmin = X
                if X > xmax: xmax = X
                if Y < ymin: ymin = Y
                if Y > ymax: ymax = Y
            nx, ny, nz = f[0], f[1], f[2]
            N = (a[0] * nx + a[1] * ny + a[2] * nz, a[4] * nx + a[5] * ny + a[6] * nz, a[8] * nx + a[9] * ny + a[10] * nz)
            struct.pack_into('<12fH', o, 84 + 50 * t, N[0], N[1], N[2], *v, 0)
        open(dst, 'wb').write(o)
        out[tag] = {'tris': n, 'bed': [round(xmin, 3), round(xmax, 3), round(ymin, 3), round(ymax, 3), round(zmin, 4), round(zmax, 3)],
                    's': round(time.time() - t0, 1)}
    r2_log('r2_3_orient', 'run', out)
    print(json.dumps(out))
