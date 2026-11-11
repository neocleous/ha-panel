# rev F step 3 (2026-11-11) - helpers for the h scripts (new main board rev 3, carrier, leads). exec()'d by the step scripts.
# Adds to v5f_fp_lib.py: the main board's frame of claude/main-board-site-2026-11-10.md (u right as seen from the door = +x_rel,
# v up the slab, w out of the door-side face; origin x_rel 2.5, Zd -27.45, depth 32.7), the current-body filter, a cache that
# survives between MCP calls (Fusion keeps Python's modules), and small probes.
# The board frame is parallel to the design frame (u = design x, v = design z, w = -design y), so a body's design bounding box
# is its exact box in the board frame.
import os, re, sys
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
U0, V0, D0 = 2.5, -27.45, 32.7
S3 = os.path.join(FP, 'step3')
BACK = re.compile(r'(_v\d+|_[a-e]\d+[a-z0-9]*| \(\d+\))$')
LEGACY = ('DOOR_tray', 'HOUSING_E', 'HOUSING_shell', 'HOUSING_F_wip', 'AMP_env_20x20x10', 'BUCK_20to5V_env_43x25x13', 'DOOR_plate_revE', 'GROMMET_usbc',
          'HOUSING_F_front_d10_sliver', 'HOUSING_F_front_d12a_sliver1', 'LD2410C_env', 'MAIN_BRACKET_d1split_L', 'MAIN_BRACKET_d1split_R',
          'MAIN_BRACKET_d1split_plug', 'PD_trigger_env_20V', 'PI5_board', 'SPKBOX_L_r2', 'SPK_driver_D40', 'V11a_mx', 'V11a_px', 'V11a_up', 'V11b_mx',
          'V11b_px', 'V11b_up', 'V11c_straight', 'VOICEPE_back_env', 'VOICEPE_encoder_env', 'VOICEPE_pcb', 'BME680_env_revD', 'TOUCH_pcb_100x44')
NOTPART = ('REF_', 'TOOL_', 'INNER', 'RENDER_', 'AUD_')


def Bp(u, v, w):                        # board frame -> design point (cm)
    return Dp(U0 + u, D0 + w, V0 + v)


def Bf(p):                              # design point -> board frame (u, v, w) mm
    return (p.x * 10 - XC - U0, p.z * 10 - V0, -p.y * 10 - D0)


def bbb(b, nd=2):                       # body or temporary body -> [u0, u1, v0, v1, w0, w1]
    bb = b.boundingBox
    a = Bf(bb.minPoint); c = Bf(bb.maxPoint)
    return [round(q, nd) for q in (a[0], c[0], a[1], c[1], c[2], a[2])]


def bbox_b(X, u0, u1, v0, v1, w0, w1):  # box in the board frame
    return X.dbox(U0 + u0, U0 + u1, D0 + w0, D0 + w1, V0 + v0, V0 + v1)


def cyl_b(X, u, v, r, w0, w1, r1=None):  # cylinder along the board normal
    return X.cyld(U0 + u, V0 + v, r, D0 + w0, D0 + w1, r1)


def move_n(X, tb, out):                 # move a temporary body 'out' mm along the slab normal toward the viewer (depth decreases)
    m = adsk.core.Matrix3D.create(); m.translation = V3(0, out / 10.0, 0)
    X.tbm.transform(tb, m); return tb


def current(X, leads=False, kos=True):  # the bodies that make up the unit today
    out = []
    for b in X.root.bRepBodies:
        n = b.name
        if BACK.search(n) or n in LEGACY or n.startswith(NOTPART):
            continue
        if n.startswith('LEAD_') and not leads:
            continue
        if n.startswith('KO_') and not kos:
            continue
        out.append(b)
    return out


def cache():                            # dict that survives between MCP calls
    m = sys.modules.get('v5f_h_cache')
    if m is None:
        m = type(sys)('v5f_h_cache'); m.c = {}; sys.modules['v5f_h_cache'] = m
    return m.c


def tcopy(X, name):                     # cached temporary copy of a model body (key: name and volume, so a changed body is re-copied)
    b = X.body(name)
    if b is None:
        return None
    c = cache(); k = ('tc', name, round(b.volume, 6))
    if k not in c:
        c[k] = X.tbm.copy(b)
    return c[k]


def xvol(X, small, big):                # mm3 of small ∩ big; only the copy of the small body is changed (README lesson 105)
    if not small.boundingBox.intersects(big.boundingBox):
        return 0.0
    t = X.tbm.copy(small)
    try:
        X.tbm.booleanOperation(t, big, BT.IntersectionBooleanType)
    except Exception:
        return -1.0
    return X.vol(t)


def dist(X, a, b):                      # minimum distance between two model bodies, mm
    return X.app.measureManager.measureMinimumDistance(a, b).value * 10.0


def status3(name, st):
    os.makedirs(S3, exist_ok=True)
    json.dump(st, open(os.path.join(S3, name + '_status.json'), 'w'), separators=(',', ':'))
