# Block 0, read-only: the finding's two numbers on the B-rep's own mesh (the auditor's method, split_study.py at aa9abe4).
import adsk.core, adsk.fusion, sys, time, math


def run(_context):
    t0 = time.time()
    k = sys.modules['v5f_k']; X = k.K()
    C, S, H = k.C, k.S, k.H
    fr = X.body('HOUSING_F_front')
    mc = fr.meshManager.createMeshCalculator()
    mc.surfaceTolerance = 0.001                     # cm: 0.01 mm chordal, as the auditor's export
    ms = mc.calculate()
    P = ms.nodeCoordinatesAsDouble; I = ms.nodeIndices
    nn = len(P) // 3; nt = len(I) // 3
    # nodes to world mm
    xs = [0.0] * nn; ys = [0.0] * nn; zs = [0.0] * nn
    for i in range(nn):
        X_, Y_, Z_ = P[3 * i], P[3 * i + 1], P[3 * i + 2]
        xs[i] = X_ * 10 - k.XC; ys[i] = (Y_ * C - Z_ * S) * 10; zs[i] = H + (Y_ * S + Z_ * C) * 10
    gcut = H * S - 14.8
    chin_a = 0.0; cz = []; cx = []; cy = []
    plate_nodes = set(); n_pl = 0
    for t in range(nt):
        a, b, c = I[3 * t], I[3 * t + 1], I[3 * t + 2]
        ux, uy, uz = xs[b] - xs[a], ys[b] - ys[a], zs[b] - zs[a]
        vx, vy, vz = xs[c] - xs[a], ys[c] - ys[a], zs[c] - zs[a]
        nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
        L = math.sqrt(nx * nx + ny * ny + nz * nz)
        if L <= 0:
            continue
        ar = L / 2.0
        cxx = (xs[a] + xs[b] + xs[c]) / 3.0; cyy = (ys[a] + ys[b] + ys[c]) / 3.0; czz = (zs[a] + zs[b] + zs[c]) / 3.0
        if ny / L > 0.99 and czz < 48.5 and cyy > 6.0:
            chin_a += ar; cz.append(czz); cx.append(cxx); cy.append(cyy)
        if cyy * C + czz * S > gcut and czz > 47.5:
            plate_nodes.update((a, b, c)); n_pl += 1
    print('mesh nodes', nn, 'triangles', nt)
    print('chin (N_y > 0.99, z < 48.5, y > 6): %.0f mm2, y %.2f..%.2f, x %.1f..%.1f, z %.1f..%.1f' % (chin_a, min(cy), max(cy), min(cx), max(cx), min(cz), max(cz)))
    px = [xs[i] for i in plate_nodes]; pt = [-ys[i] * S + (zs[i] - H) * C for i in plate_nodes]
    print('plate (in front of d 14.8, z > 47.5): %d triangles; x %.2f..%.2f (%.1f wide); in-plane up %.2f..%.2f (%.1f tall)' % (
        n_pl, min(px), max(px), max(px) - min(px), min(pt), max(pt), max(pt) - min(pt)))
    print('t', round(time.time() - t0, 1))
