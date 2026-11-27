# Enclosure pass "the screws' room" (register 4f-10), version 88 onward: helper library.
# Brief: claude/brief-enclosure-screw-margins-2026-11-27.md (Project). Log: claude/architect-log-2026-11-27-b.md (D520 to D531).
# Loads the boxes' margins pass's library (../box_margins_v85/m00_lib.py, which loads the earlier passes' libraries, each checked
# by its sha256), fetches this pass's scripts from the repo at a named commit and catches a script's printed output into a file
# in THIS pass's folder on the Mac.
# World mm: x + = viewer's left, y + toward the screen, z up from the base plate's underside.
# Nothing in this file changes the document.
import runpy, io, contextlib, json, time, hashlib, urllib.request

D = '/Users/danielneocleous/Documents/HA_panel_renders/screw_margins_v88/'
D85 = '/Users/danielneocleous/Documents/HA_panel_renders/box_margins_v85/'
D80 = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
M85 = runpy.run_path(D85 + 'm00_lib.py')
load = M85['load']; vhi = M85['vhi']; stamp = M85['stamp']; crop = M85['crop']
PRINTED = M85['PRINTED']
RAW = 'https://raw.githubusercontent.com/neocleous/ha-panel/%s/enclosure/model-v88/%s'
# version 88's guard volumes (mm3): (preflight BRepBody.volume, very high accuracy). The two boxes as the brief gives them
# (D520); the other fifteen as claude/brief-enclosure-box-margins-2026-11-27.md lists them for version 85.
GUARD88 = dict(M85['GUARD85'])
GUARD88['SPKBOX_L'] = (26472.215, 26471.906)
GUARD88['SPKBOX_R'] = (26796.485, 26793.443)
MAY_CHANGE = ('SPKBOX_L', 'SPKBOX_R', 'HOUSING_F_front', 'HOUSING_F_door', 'MIC_CLAMP_L', 'MIC_CLAMP_R')
SUF = '_v88'


def get(fn, commit, h256):
    """A script of this pass fetched from the repo at a commit, refused unless its sha256 and END line match; saved in D."""
    src = urllib.request.urlopen(RAW % (commit, fn), timeout=25).read()
    got = hashlib.sha256(src).hexdigest()
    if got != h256 or not src.rstrip().endswith(b'# END'):
        raise RuntimeError('%s at %s: sha256 %s, not the file checked' % (fn, commit, got))
    open(D + fn, 'wb').write(src)
    return len(src)


def out(fn, func, *a, **kw):
    """Run func with its printed output caught into D + fn (written even if func raises), and printed again."""
    buf = io.StringIO(); t0 = time.time()
    try:
        with contextlib.redirect_stdout(buf):
            r = func(*a, **kw)
    except Exception:
        import traceback
        buf.write('\nERROR\n' + traceback.format_exc())
        raise
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
