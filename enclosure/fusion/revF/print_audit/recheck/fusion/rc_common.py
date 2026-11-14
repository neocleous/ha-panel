# HA panel print audit re-check (2026-11-14): shared helpers for the rc* Fusion calls. READ-ONLY on the design.
#   Each connector call = this file + one rcN_*.py, joined by build.py (no exec of Mac copies, no stale module state).
#   Frames as pa_common / v5f_common: world mm (x_rel = x*10 - XC, +x = viewer's left; y + toward the viewer; z up from the
#   plate's underside), design cm. Every module-level name starts with RC_ / rc_ (lessons 63, 75).
import adsk.core, adsk.fusion, os, sys, re, json, math, time, struct, hashlib, traceback

RC_C = math.cos(math.radians(12.0)); RC_S = math.sin(math.radians(12.0)); RC_H = 143.3; RC_XC = -2.55
RC_DIR = os.path.expanduser('~/Documents/HA_panel_renders/print_audit_recheck')
RC_LOG = os.path.join(RC_DIR, 'rc_log.json')
RC_DOC = 'HA Panel v5 - tapered'
RC_VERSION = 63
RC_GUARD = {'HOUSING_F_front': 200363.57, 'SPKBOX_L': 26051.89, 'SPKBOX_R': 26769.41, 'RESP_CARRIER': 12404.26,
            'FLOOR_PLATE': 32452.33, 'CRADLE_5807': 1770.95, 'HOUSING_F_door': 47019.77, 'HOUSING_F_cap': 9944.06}
RC_TOL = 0.01                        # mm3; the brief gives the guard volumes to 0.01 mm3
RC_PRINTS = [('front', 'HOUSING_F_front'), ('plate', 'FLOOR_PLATE'), ('spkbox_L', 'SPKBOX_L'), ('spkbox_R', 'SPKBOX_R'),
             ('carrier', 'RESP_CARRIER'), ('cradle', 'CRADLE_5807'), ('door', 'HOUSING_F_door'),       # scope A
             ('cap', 'HOUSING_F_cap'), ('slab', 'SLAB_frame'), ('grommet', 'GROMMET_usbc_F'), ('clip_L', 'TOUCH_CLIP_L'),
             ('clip_R', 'TOUCH_CLIP_R'), ('bme_hood', 'BME_HOOD')]                                        # scope B


class RcCtx:
    def __init__(self):
        self.app = adsk.core.Application.get()
        self.doc = self.app.activeDocument
        if self.doc.name != RC_DOC:
            raise RuntimeError('active document is %r' % self.doc.name)
        self.des = adsk.fusion.Design.cast(self.app.activeProduct)
        self.root = self.des.rootComponent
        self.tbm = adsk.fusion.TemporaryBRepManager.get()
        self.byname = {b.name: b for b in self.root.bRepBodies}

    def body(self, n):
        return self.byname.get(n)


def rc_guard(X, strict=True):
    """Document, version 63 (latest), unmodified; the 8 guard volumes within RC_TOL mm3, one lump each. Raises when strict."""
    df = X.doc.dataFile; rep = {'version': [df.versionNumber, df.latestVersionNumber], 'modified': X.doc.isModified}; bad = []
    if df.versionNumber != RC_VERSION or df.latestVersionNumber != RC_VERSION:
        bad.append('version %s of %s' % (df.versionNumber, df.latestVersionNumber))
    if X.doc.isModified:
        bad.append('document modified')
    for n, v in RC_GUARD.items():
        b = X.body(n)
        if b is None:
            bad.append(n + ' missing'); continue
        vol = b.volume * 1000.0
        rep[n] = [round(vol, 3), b.lumps.count]
        if abs(vol - v) > RC_TOL or b.lumps.count != 1:
            bad.append(n)
    if bad and strict:
        raise RuntimeError('GUARD: %s - stop: someone else is editing or the state differs' % bad)
    return rep, bad


def rc_wpt(p):                       # design Point3D (cm) -> world (x_rel, y, z) mm
    return (p.x * 10 - RC_XC, (p.y * RC_C - p.z * RC_S) * 10, RC_H + (p.y * RC_S + p.z * RC_C) * 10)


def rc_wvec(v):                      # design Vector3D -> world unit direction
    w = (v.x, v.y * RC_C - v.z * RC_S, v.y * RC_S + v.z * RC_C); L = math.sqrt(sum(c * c for c in w)) or 1.0
    return tuple(c / L for c in w)


def rc_world_mesh(body, tol_mm=0.01, max_dev_deg=10.0):
    mc = body.meshManager.createMeshCalculator()
    mc.surfaceTolerance = tol_mm / 10.0
    mc.maxNormalDeviation = math.radians(max_dev_deg)
    m = mc.calculate()
    c = m.nodeCoordinatesAsDouble
    P = [(c[i] * 10 - RC_XC, (c[i + 1] * RC_C - c[i + 2] * RC_S) * 10, RC_H + (c[i + 1] * RC_S + c[i + 2] * RC_C) * 10)
         for i in range(0, len(c), 3)]
    ix = m.nodeIndices
    return P, [(ix[t], ix[t + 1], ix[t + 2]) for t in range(0, len(ix), 3)]


def rc_write_stl(path, P, T, name='mesh'):
    buf = bytearray(84 + 50 * len(T))
    hdr = ('HA panel print recheck %s world mm x_rel' % name).encode()[:80]
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


def rc_log(script, step, data):
    os.makedirs(RC_DIR, exist_ok=True)
    try:
        L = json.load(open(RC_LOG))
    except Exception:
        L = []
    L.append({'t': time.strftime('%Y-%m-%d %H:%M:%S'), 'script': script, 'step': step, 'data': data})
    json.dump(L, open(RC_LOG, 'w'), indent=1)


def rc_out(path, out):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(out, open(path, 'w'), indent=1)
