# HA panel print files (2026-11-16): shared helpers for the pf_* Fusion calls. READ-ONLY on the design.
#   Brief: claude/brief-print-files-2026-11-16.md. Model "HA Panel v5 - tapered", version 65 (g20).
#   Derived from print_audit/recheck2/lib/r2lib.py (docs 89d06d7): same frames, guard, unit count and mesh export;
#   only the folders differ, so the re-check's records are never overwritten.
#   Frames: world mm (x_rel = x*10 - XC, +x = viewer's left; y + toward the viewer; z up from the base plate's underside).
import adsk.core, adsk.fusion, os, sys, re, json, math, time, struct, hashlib, traceback

R2_C = math.cos(math.radians(12.0)); R2_S = math.sin(math.radians(12.0)); R2_H = 143.3; R2_XC = -2.55
R2_DIR = os.path.expanduser('~/Documents/HA_panel_renders/print_files/_work')        # this session's work folder
R2_RC2 = os.path.expanduser('~/Documents/HA_panel_renders/print_audit_recheck2')      # re-check of 2026-11-15 (read only)
R2_RC1 = os.path.expanduser('~/Documents/HA_panel_renders/print_audit_recheck')       # re-check of 2026-11-14 (read only)
R2_OUTDIR = os.path.expanduser('~/Documents/HA_panel_renders/print_files')           # the print files
R2_LOG = os.path.join(R2_DIR, 'pf_log.json')
R2_DOC = 'HA Panel v5 - tapered'
R2_VERSION = 65
R2_GUARD = {'HOUSING_F_plate': 68247.71, 'HOUSING_F_front': 104433.98, 'SPKBOX_L': 26088.32, 'SPKBOX_R': 26809.82,
            'FLOOR_PLATE': 32450.31, 'RESP_CARRIER': 12404.26, 'CRADLE_5807': 1770.95, 'HOUSING_F_door': 47019.77,
            'HOUSING_F_cap': 9944.06}
R2_TOL = 0.01                        # mm3
R2_PRINTS = [('screen', 'HOUSING_F_plate'), ('shell', 'HOUSING_F_front'), ('spkbox_L', 'SPKBOX_L'), ('spkbox_R', 'SPKBOX_R'),
             ('base', 'FLOOR_PLATE'),
             ('carrier', 'RESP_CARRIER'), ('cradle', 'CRADLE_5807'), ('door', 'HOUSING_F_door'), ('cap', 'HOUSING_F_cap'),
             ('slab', 'SLAB_frame'), ('grommet', 'GROMMET_usbc_F'), ('clip_L', 'TOUCH_CLIP_L'), ('clip_R', 'TOUCH_CLIP_R'),
             ('bme_hood', 'BME_HOOD')]
R2_SCOPE_B = {'SLAB_frame': 62932.41, 'GROMMET_usbc_F': 506.18, 'TOUCH_CLIP_L': 489.56, 'TOUCH_CLIP_R': 489.56, 'BME_HOOD': 802.88}

R2_BACK = re.compile(r'(_v\d+|_[a-e]\d+[a-z0-9]*| \(\d+\))$')
R2_LEGACY = ('DOOR_tray', 'HOUSING_E', 'HOUSING_shell', 'HOUSING_F_wip', 'AMP_env_20x20x10', 'BUCK_20to5V_env_43x25x13', 'DOOR_plate_revE',
             'GROMMET_usbc', 'HOUSING_F_front_d10_sliver', 'HOUSING_F_front_d12a_sliver1', 'LD2410C_env', 'MAIN_BRACKET_d1split_L',
             'MAIN_BRACKET_d1split_R', 'MAIN_BRACKET_d1split_plug', 'PD_trigger_env_20V', 'PI5_board', 'SPKBOX_L_r2', 'SPK_driver_D40',
             'V11a_mx', 'V11a_px', 'V11a_up', 'V11b_mx', 'V11b_px', 'V11b_up', 'V11c_straight', 'VOICEPE_back_env', 'VOICEPE_encoder_env',
             'VOICEPE_pcb', 'BME680_env_revD', 'TOUCH_pcb_100x44')
R2_NOTPART = ('REF_', 'TOOL_', 'INNER', 'RENDER_', 'AUD_')


class R2Ctx:
    def __init__(self):
        self.app = adsk.core.Application.get()
        self.doc = self.app.activeDocument
        if self.doc.name != R2_DOC:
            raise RuntimeError('active document is %r' % self.doc.name)
        self.des = adsk.fusion.Design.cast(self.app.activeProduct)
        self.root = self.des.rootComponent
        self.tbm = adsk.fusion.TemporaryBRepManager.get()
        self.mm = self.app.measureManager

    def body(self, n):
        return self.root.bRepBodies.itemByName(n)


def r2_unit(X):
    out = []
    for b in X.root.bRepBodies:
        n = b.name
        if n.startswith('LCD_'):
            if re.search(r'(_v\d+|_[a-e]\d+[a-z0-9]*)$', n):
                continue
            out.append(b); continue
        if R2_BACK.search(n) or n in R2_LEGACY or n.startswith(R2_NOTPART):
            continue
        out.append(b)
    return out


def r2_guard(X, strict=True):
    """Document, version 65 (latest), unmodified; the 9 guard volumes within R2_TOL mm3, one lump each. Raises when strict."""
    df = X.doc.dataFile; rep = {'version': [df.versionNumber, df.latestVersionNumber], 'modified': X.doc.isModified}; bad = []
    if df.versionNumber != R2_VERSION or df.latestVersionNumber != R2_VERSION:
        bad.append('version %s of %s' % (df.versionNumber, df.latestVersionNumber))
    if X.doc.isModified:
        bad.append('document modified')
    for n, v in R2_GUARD.items():
        b = X.body(n)
        if b is None:
            bad.append(n + ' missing'); continue
        vol = b.volume * 1000.0
        rep[n] = [round(vol, 3), b.lumps.count]
        if abs(vol - v) > R2_TOL or b.lumps.count != 1:
            bad.append(n)
    if bad and strict:
        raise RuntimeError('GUARD: %s - stop: someone else is editing or the state differs' % bad)
    return rep, bad


def r2_wpt(p):                       # design Point3D (cm) -> world (x_rel, y, z) mm
    return (p.x * 10 - R2_XC, (p.y * R2_C - p.z * R2_S) * 10, R2_H + (p.y * R2_S + p.z * R2_C) * 10)


def r2_wvec(v):                      # design Vector3D -> world unit direction
    w = (v.x, v.y * R2_C - v.z * R2_S, v.y * R2_S + v.z * R2_C); L = math.sqrt(sum(c * c for c in w)) or 1.0
    return tuple(c / L for c in w)


def r2_world_mesh(body, tol_mm=0.01, max_dev_deg=10.0):
    mc = body.meshManager.createMeshCalculator()
    mc.surfaceTolerance = tol_mm / 10.0
    mc.maxNormalDeviation = math.radians(max_dev_deg)
    m = mc.calculate()
    c = m.nodeCoordinatesAsDouble
    P = [(c[i] * 10 - R2_XC, (c[i + 1] * R2_C - c[i + 2] * R2_S) * 10, R2_H + (c[i + 1] * R2_S + c[i + 2] * R2_C) * 10)
         for i in range(0, len(c), 3)]
    ix = m.nodeIndices
    return P, [(ix[t], ix[t + 1], ix[t + 2]) for t in range(0, len(ix), 3)]


def r2_write_stl(path, P, T, name='mesh'):
    buf = bytearray(84 + 50 * len(T))
    hdr = ('HA panel print files %s world mm x_rel' % name).encode()[:80]
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


def r2_sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest() if os.path.exists(p) else None


def r2_log(script, step, data):
    os.makedirs(R2_DIR, exist_ok=True)
    try:
        L = json.load(open(R2_LOG))
    except Exception:
        L = []
    L.append({'t': time.strftime('%Y-%m-%d %H:%M:%S'), 'script': script, 'step': step, 'data': data})
    json.dump(L, open(R2_LOG, 'w'), indent=1)


def r2_out(path, out):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(out, open(path, 'w'), indent=1)
