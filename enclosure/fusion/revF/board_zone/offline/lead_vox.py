"""V23b (e5): voxel occupancy of the e5b meshes (world mm, x_rel) by z-column winding, main board rev 2.1's front parts as
courtyard x MAIN_env-height boxes instead of MAIN_front_env, the old sensor leads left out; then the distance field.
Work folder (env LEAD_WORK, default the current folder) holds mesh/*.stl; writes occ_h<h>.npz, dist_h<h>.npy, vox_h<h>.json."""
import numpy as np, struct, os, sys, json, glob, time
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kpcb

D = os.environ.get('LEAD_WORK', os.getcwd())
BOARD = os.path.join(HERE, '..', '..', '..', '..', '..', 'hardware', 'main-board', 'main-board.kicad_pcb')
H = float(os.environ.get('VOX_H', '0.5'))
X0, X1, Y0, Y1, Z0, Z1 = -95.0, 25.0, -80.0, 10.0, 60.0, 190.0
NX, NY, NZ = int(round((X1 - X0) / H)), int(round((Y1 - Y0) / H)), int(round((Z1 - Z0) / H))
JX, JY = 0.01234, 0.02371          # column jitter (no exact edge hits)
SKIP = {'LEAD_BME680', 'LEAD_VEML', 'MAIN_front_env'}


def load(p):
    b = open(p, 'rb').read()
    n = struct.unpack('<I', b[80:84])[0]
    a = np.frombuffer(b[84:84 + 50 * n], dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]))
    return a['v'].astype(np.float64)


def columns(T):
    """(column flat index, z, s) for every column centre inside a triangle's xy projection; s = +1 normal up."""
    xc = lambda i: X0 + (i + 0.5) * H + JX
    yc = lambda j: Y0 + (j + 0.5) * H + JY
    mn = T[:, :, :2].min(axis=1); mx = T[:, :, :2].max(axis=1)
    i0 = np.ceil((mn[:, 0] - X0 - JX) / H - 0.5).astype(np.int64); i1 = np.floor((mx[:, 0] - X0 - JX) / H - 0.5).astype(np.int64)
    j0 = np.ceil((mn[:, 1] - Y0 - JY) / H - 0.5).astype(np.int64); j1 = np.floor((mx[:, 1] - Y0 - JY) / H - 0.5).astype(np.int64)
    i0 = np.maximum(i0, 0); j0 = np.maximum(j0, 0); i1 = np.minimum(i1, NX - 1); j1 = np.minimum(j1, NY - 1)
    ni = np.maximum(i1 - i0 + 1, 0); nj = np.maximum(j1 - j0 + 1, 0); cnt = ni * nj
    keep = cnt > 0
    T, i0, j0, ni, nj, cnt = T[keep], i0[keep], j0[keep], ni[keep], nj[keep], cnt[keep]
    if len(T) == 0:
        return np.zeros(0, np.int64), np.zeros(0), np.zeros(0)
    tid = np.repeat(np.arange(len(T)), cnt)
    off = np.arange(cnt.sum()) - np.repeat(np.cumsum(cnt) - cnt, cnt)
    ii = i0[tid] + off // nj[tid]; jj = j0[tid] + off % nj[tid]
    px = xc(ii); py = yc(jj)
    A = T[tid, 0]; B = T[tid, 1]; Cc = T[tid, 2]
    v0x = B[:, 0] - A[:, 0]; v0y = B[:, 1] - A[:, 1]; v1x = Cc[:, 0] - A[:, 0]; v1y = Cc[:, 1] - A[:, 1]
    v2x = px - A[:, 0]; v2y = py - A[:, 1]
    d = v0x * v1y - v0y * v1x
    ok = np.abs(d) > 1e-14
    ds = np.where(ok, d, 1.0)
    u = (v2x * v1y - v2y * v1x) / ds; v = (v0x * v2y - v0y * v2x) / ds
    m = ok & (u >= 0) & (v >= 0) & (u + v <= 1)
    z = A[m, 2] + u[m] * (B[m, 2] - A[m, 2]) + v[m] * (Cc[m, 2] - A[m, 2])
    return ii[m] * NY + jj[m], z, np.sign(d[m])


def add_mesh(diff, T):
    col, z, s = columns(T)
    if len(col) == 0:
        return 0
    o = np.lexsort((z, col)); col, z, s = col[o], z[o], s[o]
    # winding after each crossing, restarted per column (entering face: normal down, s = -1, winding +1)
    dlt = -s
    cs = np.cumsum(dlt)
    first = np.r_[True, col[1:] != col[:-1]]
    base = np.maximum.accumulate(np.where(first, np.arange(len(col)), 0))
    w = cs - (cs[base] - dlt[base])
    nxt_same = np.r_[col[1:] == col[:-1], False]
    inside = (w > 0) & nxt_same
    za = z[inside]; zb = z[np.nonzero(inside)[0] + 1]; cc = col[inside]
    ka = np.clip(np.ceil((za - Z0) / H - 0.5), 0, NZ).astype(np.int64)
    kb = np.clip(np.floor((zb - Z0) / H - 0.5) + 1, 0, NZ).astype(np.int64)
    g = kb > ka
    np.add.at(diff, (cc[g], ka[g]), 1)
    np.add.at(diff, (cc[g], kb[g]), -1)
    return int(g.sum())


def box_tris(x0, x1, y0, y1, z0, z1):
    P = np.array([[x, y, z] for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)], float)
    # outward triangles of an axis box (vertex index = 4*ix + 2*iy + iz)
    F = [(0, 1, 3), (0, 3, 2), (4, 6, 7), (4, 7, 5), (0, 4, 5), (0, 5, 1), (2, 3, 7), (2, 7, 6), (0, 2, 6), (0, 6, 4),
         (1, 5, 7), (1, 7, 3)]
    T = np.array([[P[a], P[b], P[c]] for (a, b, c) in F])
    # make every triangle outward (normal away from the centre)
    ctr = P.mean(axis=0)
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); cen = T.mean(axis=1)
    flip = (n * (cen - ctr)).sum(axis=1) < 0
    T[flip] = T[flip][:, [0, 2, 1]]
    return T


def board_parts():
    """front parts of main board rev 2.1 as boxes: courtyard x heights above the front face (y -63.4)."""
    t = kpcb.parse(open(BOARD).read())
    hmap = [('MeanWell_NID100', 27.5), ('CP_Radial_D10.0mm', 16.0), ('CP_Radial_D5.0mm', 12.5), ('JST_XH', 9.8),
            ('L_Bourns_SRR1260', 6.5), ('L_Codaca_CSBA0850', 5.4), ('NANO2', 2.94), ('D_SMB', 2.7), ('Fuse_2920', 1.8),
            ('PinHeader', 2.0), ('MountingHole', 0.0)]
    out = []
    for fp in kpcb.footprints(t):
        if fp['layer'] != 'F.Cu' or not fp['crt'] or fp['ref'] == 'J10':
            continue
        h = 1.8
        for k, v in hmap:
            if k in fp['name']:
                h = v; break
        if h <= 0:
            continue
        xs = [45 - p[0] for p in fp['crt']]; zs = [84 - p[1] for p in fp['crt']]
        out.append((fp['ref'], min(xs), max(xs), -63.4, -63.4 + h, min(zs), max(zs)))
    return out


if __name__ == '__main__':
    t0 = time.time()
    diff = np.zeros((NX * NY, NZ + 1), np.int32)
    rows = {}
    for p in sorted(glob.glob(os.path.join(D, 'mesh', '*.stl'))):
        nm = os.path.basename(p)[:-4]
        if nm in SKIP:
            continue
        T = load(p)
        bb = (T[:, :, 0].min(), T[:, :, 0].max(), T[:, :, 1].min(), T[:, :, 1].max(), T[:, :, 2].min(), T[:, :, 2].max())
        if bb[1] < X0 or bb[0] > X1 or bb[3] < Y0 or bb[2] > Y1 or bb[5] < Z0 or bb[4] > Z1:
            continue
        rows[nm] = add_mesh(diff, T)
    parts = board_parts()
    for (ref, x0, x1, y0, y1, z0, z1) in parts:
        rows['MAINPART_' + ref] = add_mesh(diff, box_tris(x0, x1, y0, y1, z0, z1))
    occ = (np.cumsum(diff, axis=1)[:, :NZ] > 0).reshape(NX, NY, NZ)
    np.savez_compressed(os.path.join(D, 'occ_h%.2f.npz' % H), occ=occ, origin=np.array([X0, Y0, Z0]), h=H)
    np.save(os.path.join(D, 'dist_h%.2f.npy' % H), (ndimage.distance_transform_edt(~occ) * H).astype(np.float32))
    json.dump({'rows': rows, 'parts': parts, 'shape': [NX, NY, NZ], 'occupied': int(occ.sum()), 't_s': round(time.time() - t0, 1)},
              open(os.path.join(D, 'vox_h%.2f.json' % H), 'w'), indent=0)
    print('shape', occ.shape, 'occupied', int(occ.sum()), 't', round(time.time() - t0, 1))
