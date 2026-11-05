# HA panel model audit (2026-11-05): shared helpers for the v5f_a* scripts.
#   exec() after ~/Documents/v5f_common.py (+ v5f_b5_common.py); the Mac copy is ~/Documents/audit/scripts/v5f_audit_common.py
#   (fetched from this repo by commit SHA). Sets LOG to the audit log so the design log stays untouched.
#   Mesh files: binary STL in WORLD mm with x_rel = x - XC (x_rel, y_w, z_w), written by write_stl().
import struct, re, traceback
LOG = os.path.expanduser('~/Documents/v5f_audit_log.json')
AUD = os.path.expanduser('~/Documents/audit')
GUARD = {'HOUSING_F_front': (236.6852, 0.0005), 'HOUSING_F_cap': (9.9147, 0.0005), 'HOUSING_F_door': (51.101, 0.0005),
         'SLAB_frame': (62.93, 0.006), 'SPKBOX_L': (25.62, 0.006), 'SPKBOX_R': (25.07, 0.006),
         'MAIN_BRACKET': (4.90, 0.006), 'RESP_CARRIER': (10.07, 0.006), 'CRADLE_5807': (2.16, 0.006),
         'GROMMET_usbc_F': (0.49, 0.006)}
PRINTED = list(GUARD)
N_BODIES = 214
START_VISIBLE = ['CRADLE_5807', 'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR', 'GPIO_plugA_env', 'GPIO_plugB_env', 'GROMMET_usbc_F',
                 'HOUSING_F_cap', 'HOUSING_F_front', 'LCD_glass', 'MAIN_BRACKET', 'PD_5807_env', 'PI5_F', 'PI5_F_cooler',
                 'RENDER_FABRIC_front', 'RESP_CARRIER', 'SLAB_frame', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'TOUCH_PCB']


def guard(X):
    """Abort unless the model is in the audited state: guards, body count, document unmodified, no AUDIT_tmp_ bodies."""
    bad = {}
    for k, (v, tol) in GUARD.items():
        b = X.body(k)
        if b is None or abs(b.volume - v) > tol:
            bad[k] = None if b is None else round(b.volume, 4)
    if bad:
        raise RuntimeError('GUARD: printed-part volumes changed %s - someone else is editing; stop' % bad)
    if X.comp.bRepBodies.count != N_BODIES:
        raise RuntimeError('GUARD: %d bodies (expected %d)' % (X.comp.bRepBodies.count, N_BODIES))
    if X.doc.isModified:
        raise RuntimeError('GUARD: the design document has unsaved modifications')
    left = [b.name for b in X.comp.bRepBodies if b.name.startswith('AUDIT_tmp_')]
    if left:
        raise RuntimeError('GUARD: AUDIT_tmp_ bodies present %s' % left)
    return True


def end_state(X):
    """Facts for the end-state check (compared against block 0)."""
    return {'n': X.comp.bRepBodies.count, 'modified': X.doc.isModified, 'version': X.doc.dataFile.versionNumber,
            'latest': X.doc.dataFile.latestVersionNumber,
            'visible_same': sorted(b.name for b in X.comp.bRepBodies if b.isLightBulbOn) == START_VISIBLE,
            'audit_tmp': [b.name for b in X.comp.bRepBodies if b.name.startswith('AUDIT_tmp_')]}


def wpt(p):                                   # design Point3D (cm) -> world (x_rel, y, z) mm
    return (p.x * 10 - XC, wy(p), wz(p))


def world_mesh(body, tol_mm=None, quality=None):
    """Body triangle mesh in world mm (x_rel, y, z). tol_mm sets surfaceTolerance; otherwise a quality option."""
    mc = body.meshManager.createMeshCalculator()
    if tol_mm is not None:
        mc.surfaceTolerance = tol_mm / 10.0
    else:
        mc.setQuality(quality if quality is not None else adsk.fusion.TriangleMeshQualityOptions.NormalQualityTriangleMesh)
    m = mc.calculate()
    c = m.nodeCoordinatesAsDouble
    P = [(c[i] * 10 - XC, (c[i + 1] * C - c[i + 2] * S) * 10, H + (c[i + 1] * S + c[i + 2] * C) * 10) for i in range(0, len(c), 3)]
    ix = m.nodeIndices
    return P, [(ix[t], ix[t + 1], ix[t + 2]) for t in range(0, len(ix), 3)]


def write_stl(path, P, T, name='mesh'):
    """Binary STL (float32), facet normals from the vertex order (right-hand rule)."""
    buf = bytearray(84 + 50 * len(T))
    hdr = ('HA panel audit %s world mm x_rel' % name).encode()[:80]
    buf[0:len(hdr)] = hdr
    struct.pack_into('<I', buf, 80, len(T))
    off = 84
    for (a, b, c) in T:
        pa, pb, pc = P[a], P[b], P[c]
        u = (pb[0] - pa[0], pb[1] - pa[1], pb[2] - pa[2]); v = (pc[0] - pa[0], pc[1] - pa[1], pc[2] - pa[2])
        n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
        L = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2) or 1.0
        struct.pack_into('<12fH', buf, off, n[0] / L, n[1] / L, n[2] / L, pa[0], pa[1], pa[2], pb[0], pb[1], pb[2],
                         pc[0], pc[1], pc[2], 0)
        off += 50
    with open(path, 'wb') as f:
        f.write(buf)
    return len(T)


def mindist(X, a, b):
    """measureMinimumDistance between two existing bodies (cm -> mm) with the point pair in world mm."""
    r = X.app.measureManager.measureMinimumDistance(a, b)
    return round(r.value * 10, 3), [round(v, 2) for v in wpt(r.positionOne)], [round(v, 2) for v in wpt(r.positionTwo)]
