# Enclosure pass "the audit's fixes" (register 4f-7), version 69 -> 70 onward: helper library.
# Brief: claude/brief-enclosure-audit-fixes-2026-11-24.md (Project).
#
# Loads the earlier passes' helper libraries from the repo at commit 45a38e4, each checked by its sha256, as the
# last pass did (enclosure/model-v68/README.md):
#   c3k   enclosure/fusion/revF/floor_plate/fusion/v5f_k_lib.py      frames, temporary solids, current(), tcopy(), budget()
#   c3    enclosure/fusion/revF/split/change3/c3_lib.py              the cloth reference for the outer-skin check
#   K4NS  enclosure/fusion/revF/floor_plate/fusion/v5f_k4a_unit_checks.py, as the namespace c3k.K4NS: ride-in, matrix()
# and catches a script's printed output into a file in this folder (the connector may return no text).
#
# World mm: x + = viewer's left, y + toward the screen, z up from the base plate's underside.
# Nothing in this file changes the document.
import sys, types, io, json, contextlib, hashlib, urllib.request, time

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
SHA = '45a38e49d72cf125aab3f4aa91dd065b3bc4f7ee'
RAW = 'https://raw.githubusercontent.com/neocleous/ha-panel/%s/%s'
LIBS = [('c3k', 'enclosure/fusion/revF/floor_plate/fusion/v5f_k_lib.py', 'adc99aca2840850c63fcf4ef978681dea92b81857cf6913a6dc81f37df6d56bb'),
        ('c3', 'enclosure/fusion/revF/split/change3/c3_lib.py', '571868b598906a32bf2835b4549b9c192a1596ffc185b8cf946a021fcd60c7f0')]
K4A = ('v5f_k4a_unit_checks.py', '12006d28a01aa1b445f3175d8f5c19fd60ff7c81bc1160f551670db328db0baf')
PRINTED = ['HOUSING_F_plate', 'HOUSING_F_front', 'SPKBOX_L', 'SPKBOX_R', 'FLOOR_PLATE', 'RESP_CARRIER', 'CRADLE_5807', 'HOUSING_F_door',
           'HOUSING_F_cap', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'SLAB_frame', 'GROMMET_usbc_F', 'BME_HOOD', 'MIC_CLAMP_L', 'MIC_CLAMP_R']
# version 69's guard volumes, claude/architect-log-2026-11-23.md section 4 (mm3)
GUARD69 = {'HOUSING_F_plate': 66463.676, 'HOUSING_F_front': 111843.509, 'SPKBOX_L': 26342.557, 'SPKBOX_R': 27112.045,
           'FLOOR_PLATE': 32643.331, 'RESP_CARRIER': 13651.988, 'CRADLE_5807': 1771.219, 'HOUSING_F_door': 50613.794,
           'HOUSING_F_cap': 10164.971, 'TOUCH_CLIP_L': 580.762, 'TOUCH_CLIP_R': 580.762, 'SLAB_frame': 62932.407,
           'GROMMET_usbc_F': 634.700, 'BME_HOOD': 909.698, 'MIC_CLAMP_L': 758.320, 'MIC_CLAMP_R': 758.320}
THRESH = 0.0005   # mm3: the last pass's threshold for a pair that is "not zero" (v69_checks.matrix)


def _get(path, h256):
    src = urllib.request.urlopen(RAW % (SHA, path), timeout=25).read()
    got = hashlib.sha256(src).hexdigest()
    if got != h256:
        raise RuntimeError('sha256 of %s is %s' % (path, got))
    return src.decode('utf-8')


def load():
    """c3k, c3 and c3k.K4NS, once per Fusion session."""
    for name, path, h in LIBS:
        if name not in sys.modules:
            m = types.ModuleType(name)
            exec(compile(_get(path, h), path.split('/')[-1], 'exec'), m.__dict__)
            sys.modules[name] = m
    k = sys.modules['c3k']
    sys.modules.setdefault('v5f_k', k)          # k.step() hands the k4a script the library under this name
    if getattr(k, 'K4NS', None) is None:
        k.K4NS = k.step(SHA, K4A[0], K4A[1])
    return k


def out(fn, func, *a, **kw):
    """Run func with its printed output caught into D + fn, and printed again for the connector."""
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            r = func(*a, **kw)
    finally:
        open(D + fn, 'w').write(buf.getvalue())
    print(buf.getvalue())
    return r


def jdump(fn, obj):
    json.dump(obj, open(D + fn, 'w'), indent=1, default=str)


def stamp():
    return time.strftime('%Y-%m-%d %H:%M:%S')
