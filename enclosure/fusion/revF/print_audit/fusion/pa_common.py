# HA panel print audit (2026-11-06/07): shared helpers for the pa* Fusion scripts. Read-only on the design.
#   exec() after ~/Documents/v5f_common.py and ~/Documents/v5f_b5_common.py. Sets LOG to the print-audit log, so the design
#   log (~/Documents/v5f_log.json) and the model-audit log stay untouched. Every name defined here starts with PA_ / pa_
#   (lessons 63, 75: C, S, T, H, XC, UP, WY, WZ, INS, B and the helper names stay free).
#   Mac copy: ~/Documents/HA_panel_renders/print_audit/scripts/pa_common.py; repo enclosure/fusion/revF/print_audit/.
import struct, re, hashlib, traceback
PA_DIR = os.path.expanduser('~/Documents/HA_panel_renders/print_audit')
LOG = os.path.join(PA_DIR, 'pa_log.json')
PA_DOC = 'HA Panel v5 - tapered'
PA_EXPL = 'HA Panel v5 - exploded prints (d19)'
PA_VERSION = ("rev F WIP 2026-11-06 d19: printability - 46 deg gussets under both main-board bracket halves' lower "
              "board-boss arms (no support under them printed upright), insert holes kept (Claude)")
PA_GUARD = {'HOUSING_F_front': 235.2269, 'HOUSING_F_cap': 9.9591, 'SLAB_frame': 62.9324, 'RESP_CARRIER': 10.0716,
            'HOUSING_F_door': 47.2694, 'GROMMET_usbc_F': 0.5062, 'MAIN_BRACKET': 6.5563, 'BME_HOOD': 0.8029,
            'SPKBOX_L': 25.6082, 'SPKBOX_R': 26.3874, 'TOUCH_CLIP_L': 0.4896, 'TOUCH_CLIP_R': 0.4896,
            'CRADLE_5807': 2.1775}
PA_TOL = 0.0005
PA_PRINTS = [                      # (tag, body, lump side: +1 = x_rel > 0 = viewer's left, -1 = right, None = whole body)
    ('front', 'HOUSING_F_front', None), ('cap', 'HOUSING_F_cap', None), ('slab', 'SLAB_frame', None),
    ('resp_carrier', 'RESP_CARRIER', None), ('door', 'HOUSING_F_door', None), ('grommet', 'GROMMET_usbc_F', None),
    ('cradle', 'CRADLE_5807', None), ('bracket_L', 'MAIN_BRACKET', 1), ('bracket_R', 'MAIN_BRACKET', -1),
    ('bme_hood', 'BME_HOOD', None), ('spkbox_L', 'SPKBOX_L', None), ('spkbox_R', 'SPKBOX_R', None),
    ('clip_L', 'TOUCH_CLIP_L', None), ('clip_R', 'TOUCH_CLIP_R', None)]


def pa_guard(X, strict=True):
    """Guard volumes (cm3, +-0.0005), MAIN_BRACKET 2 lumps, document unmodified. Raises on a mismatch when strict."""
    rep = {}; bad = []
    for k, v in PA_GUARD.items():
        b = X.body(k)
        if b is None:
            rep[k] = None; bad.append(k); continue
        rep[k] = [round(b.volume, 4), b.lumps.count, round(b.volume - v, 5)]
        if abs(b.volume - v) > PA_TOL:
            bad.append(k)
    if rep.get('MAIN_BRACKET') and rep['MAIN_BRACKET'][1] != 2:
        bad.append('MAIN_BRACKET lumps')
    if X.doc.isModified:
        bad.append('document modified')
    if bad and strict:
        raise RuntimeError('GUARD: %s - someone else is editing or the state differs; stop' % bad)
    return rep, bad


def pa_view(app):
    vp = app.activeViewport; c = vp.camera
    pt = lambda p: [round(p.x, 4), round(p.y, 4), round(p.z, 4)]
    return {'eye': pt(c.eye), 'target': pt(c.target), 'up': [round(c.upVector.x, 4), round(c.upVector.y, 4), round(c.upVector.z, 4)],
            'type': c.cameraType, 'extents': round(c.viewExtents, 4), 'fit': c.isFitView, 'style': vp.visualStyle}


def pa_wpt(p):                     # design Point3D (cm) -> world (x_rel, y, z) mm
    return (p.x * 10 - XC, wy(p), wz(p))


def pa_world_mesh(body, tol_mm=0.01, max_dev_deg=10.0):
    """Triangle mesh of a body in world mm (x_rel, y, z): (points, triangles)."""
    mc = body.meshManager.createMeshCalculator()
    mc.surfaceTolerance = tol_mm / 10.0
    try:
        mc.maxNormalDeviation = math.radians(max_dev_deg)
    except Exception:
        pass
    m = mc.calculate()
    c = m.nodeCoordinatesAsDouble
    P = [(c[i] * 10 - XC, (c[i + 1] * C - c[i + 2] * S) * 10, H + (c[i + 1] * S + c[i + 2] * C) * 10) for i in range(0, len(c), 3)]
    ix = m.nodeIndices
    return P, [(ix[t], ix[t + 1], ix[t + 2]) for t in range(0, len(ix), 3)]


def pa_write_stl(path, P, T, name='mesh'):
    """Binary STL (float32, mm, world frame with x_rel); facet normals from the vertex order (right-hand rule)."""
    buf = bytearray(84 + 50 * len(T))
    hdr = ('HA panel print audit %s world mm x_rel' % name).encode()[:80]
    buf[0:len(hdr)] = hdr
    struct.pack_into('<I', buf, 80, len(T))
    off = 84
    for (a, b_, c_) in T:
        pa, pb, pc = P[a], P[b_], P[c_]
        u = (pb[0] - pa[0], pb[1] - pa[1], pb[2] - pa[2]); v = (pc[0] - pa[0], pc[1] - pa[1], pc[2] - pa[2])
        n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
        L = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2) or 1.0
        struct.pack_into('<12fH', buf, off, n[0] / L, n[1] / L, n[2] / L, pa[0], pa[1], pa[2], pb[0], pb[1], pb[2],
                         pc[0], pc[1], pc[2], 0)
        off += 50
    with open(path, 'wb') as f:
        f.write(buf)
    return len(T)


def pa_out(path, out):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(out, open(path, 'w'), indent=1)
