# Enclosure pass "the drivers' seat" (register 4f-8), version 79 -> 80 onward: helper library.
# Brief: claude/brief-enclosure-drivers-seat-2026-11-26.md (Project).
#
# Loads the earlier passes' helper libraries from the repo at commit 45a38e4, each checked by its sha256, as
# ../model-v70/v70_lib.py did:
#   c3k   enclosure/fusion/revF/floor_plate/fusion/v5f_k_lib.py      frames, temporary solids, current(), tcopy(), budget()
#   c3    enclosure/fusion/revF/split/change3/c3_lib.py              the cloth reference for the outer-skin check
#   K4NS  enclosure/fusion/revF/floor_plate/fusion/v5f_k4a_unit_checks.py, as the namespace c3k.K4NS: ride-in, matrix()
# and catches a script's printed output into a file in this pass's folder on the Mac.
#
# World mm: x + = viewer's left, y + toward the screen, z up from the base plate's underside.
# Nothing in this file changes the document.
import sys, types, io, json, contextlib, hashlib, urllib.request, time, os

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
D70 = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
SHA = '45a38e49d72cf125aab3f4aa91dd065b3bc4f7ee'
RAW = 'https://raw.githubusercontent.com/neocleous/ha-panel/%s/%s'
LIBS = [('c3k', 'enclosure/fusion/revF/floor_plate/fusion/v5f_k_lib.py', 'adc99aca2840850c63fcf4ef978681dea92b81857cf6913a6dc81f37df6d56bb'),
        ('c3', 'enclosure/fusion/revF/split/change3/c3_lib.py', '571868b598906a32bf2835b4549b9c192a1596ffc185b8cf946a021fcd60c7f0')]
K4A = ('v5f_k4a_unit_checks.py', '12006d28a01aa1b445f3175d8f5c19fd60ff7c81bc1160f551670db328db0baf')
PRINTED = ['HOUSING_F_front', 'HOUSING_F_plate', 'SLAB_frame', 'HOUSING_F_door', 'FLOOR_PLATE', 'SPKBOX_R', 'SPKBOX_L', 'RESP_CARRIER',
           'HOUSING_F_cap', 'CRADLE_5807', 'RADAR_HOLDER', 'BME_HOOD', 'GROMMET_usbc_F', 'MIC_CLAMP_L', 'MIC_CLAMP_R', 'TOUCH_CLIP_L',
           'TOUCH_CLIP_R']
# version 79's guard volumes, the brief's table (mm3): (preflight method BRepBody.volume, very high accuracy), D425
GUARD79 = {'HOUSING_F_front': (111201.678, 111223.396), 'HOUSING_F_plate': (66415.924, 66415.279), 'SLAB_frame': (63006.012, 63005.760),
           'HOUSING_F_door': (50698.932, 50700.679), 'FLOOR_PLATE': (32512.467, 32515.227), 'SPKBOX_R': (27109.529, 27108.806),
           'SPKBOX_L': (26862.872, 26862.894), 'RESP_CARRIER': (13593.266, 13593.266), 'HOUSING_F_cap': (10131.026, 10129.650),
           'CRADLE_5807': (1771.219, 1771.228), 'RADAR_HOLDER': (1120.921, 1120.921), 'BME_HOOD': (946.741, 946.544),
           'GROMMET_usbc_F': (863.410, 863.403), 'MIC_CLAMP_L': (738.136, 738.136), 'MIC_CLAMP_R': (738.136, 738.136),
           'TOUCH_CLIP_L': (580.562, 580.562), 'TOUCH_CLIP_R': (580.562, 580.562)}
THRESH = 0.0005   # mm3: a pair is "not zero" above this (v69_checks.matrix, as the last two passes)


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


def vhi(b):
    import adsk.fusion
    return b.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume * 1000.0


def crop(X, src, box):
    """A temporary copy of a model body (by name) or of a temporary body, cut to a world box (x0, x1, y0, y1, z0, z1)."""
    b = X.body(src) if isinstance(src, str) else src
    t = X.wbox(*box)
    X.sec(t, X.tbm.copy(b))
    return t
# END
