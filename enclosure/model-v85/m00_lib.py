# Enclosure pass "the boxes' margins" (register 4f-9), version 85 onward: helper library.
# Brief: claude/brief-enclosure-box-margins-2026-11-27.md (Project).
# Loads the drivers' seat pass's library (../drivers_seat_v80/v80_lib.py, which loads the earlier passes' libraries from the
# repo at commit 45a38e4, each checked by its sha256) and catches a script's printed output into a file in THIS pass's folder.
# World mm: x + = viewer's left, y + toward the screen, z up from the base plate's underside.
# Nothing in this file changes the document.
import runpy, io, contextlib, json, time, hashlib

D = '/Users/danielneocleous/Documents/HA_panel_renders/box_margins_v85/'
D80 = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
V80 = runpy.run_path(D80 + 'v80_lib.py')
load = V80['load']; vhi = V80['vhi']; stamp = V80['stamp']; crop = V80['crop']
PRINTED = V80['PRINTED']
# version 85's guard volumes, the brief's table (mm3): (preflight BRepBody.volume, very high accuracy)
GUARD85 = {'HOUSING_F_front': (111285.885, 111296.152), 'HOUSING_F_plate': (66415.924, 66415.279), 'SLAB_frame': (63006.012, 63005.760),
           'HOUSING_F_door': (50698.932, 50700.679), 'FLOOR_PLATE': (31504.631, 31507.029), 'SPKBOX_R': (26918.247, 26914.341),
           'SPKBOX_L': (26612.119, 26610.934), 'RESP_CARRIER': (13588.334, 13588.334), 'HOUSING_F_cap': (10131.026, 10129.650),
           'CRADLE_5807': (1771.219, 1771.228), 'RADAR_HOLDER': (1120.921, 1120.921), 'BME_HOOD': (946.741, 946.544),
           'GROMMET_usbc_F': (863.410, 863.403), 'MIC_CLAMP_L': (738.136, 738.136), 'MIC_CLAMP_R': (738.136, 738.136),
           'TOUCH_CLIP_L': (727.322, 727.322), 'TOUCH_CLIP_R': (727.322, 727.322)}
MAY_CHANGE = ('SPKBOX_L', 'SPKBOX_R')


def out(fn, func, *a, **kw):
    """Run func with its printed output caught into D + fn (written even if func raises), and printed again."""
    buf = io.StringIO(); t0 = time.time()
    try:
        with contextlib.redirect_stdout(buf):
            r = func(*a, **kw)
    finally:
        buf.write('[%.1f s]\n' % (time.time() - t0))
        open(D + fn, 'w').write(buf.getvalue())
    print(buf.getvalue())
    return r


def jdump(fn, obj):
    json.dump(obj, open(D + fn, 'w'), indent=1, default=str)


def checked(fn, h256):
    """A script of this pass, refused unless its sha256 is the one given and it ends with its END line."""
    src = open(D + fn, 'rb').read()
    if hashlib.sha256(src).hexdigest() != h256 or not src.rstrip().endswith(b'# END'):
        raise RuntimeError(fn + ' is not the file checked')
    return runpy.run_path(D + fn)
# END
