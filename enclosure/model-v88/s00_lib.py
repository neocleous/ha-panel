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
D70 = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
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


def prev(path, h256):
    """A script of an earlier pass, read from its folder on the Mac, refused unless its sha256 is the repo's (given). Its own
    main() writes into its own folder, so this pass calls its inner functions through out() instead."""
    src = open(path, 'rb').read()
    if hashlib.sha256(src).hexdigest() != h256:
        raise RuntimeError(path + ' is not the file in the repo')
    return runpy.run_path(path)


# earlier passes' scripts this pass reuses: (path on the Mac, sha256 of the file in the repo at ea62429)
OLD = {'d27': (D80 + 'd27_fits.py', 'edf3c824a9d4aed21ce61ba5725a4954ee95faeb3b071e422114cb8d836ab592'),
       'm10': (D85 + 'm10_screws.py', '176b32f1cbc29d87cca27ee00343bec932bd5653247cfc726eb8c711a74e9122'),
       'm11': (D85 + 'm11_holes.py', '30afa85686ceb9d5dbb9b5225b8128f5aa1bb6560bee88e2bd5c9082c59000c1'),
       'm12': (D85 + 'm12_driver.py', 'caad269ca1a739064da2d07a93008614b2177280c1d8fb751d764ad7fac09413'),
       'm17': (D85 + 'm17_checks.py', '5ba7cf78a98d04d9260df0bcbab1c5101f628f76479ecb800804d94f44887725'),
       'm18': (D85 + 'm18_inlet.py', '32dc6476a376c87f56073ba09405691f9d839fa37175a0928cc761d65ae1f2ed'),
       'm20': (D85 + 'm20_close.py', '96939aa7e5a25be7b8ac74223719f03c070dfc323a547fe1dfcdc26cf96bd0b2'),
       'd52': (D80 + 'd52_checks5.py', '2cc2322c9d9ae40b4b471b91c5e9975035f7bc4444c02482a55501b8f4da408d'),
       # the audit-fixes pass's scripts (../model-v70/), read from that pass's folder on the Mac
       'p37': (D70 + 'p37_checks.py', '5dffbd4870575a3da1ba2725a07e48c11625ad2af7cac3972e7b3bd3fc13d760'),
       'p64': (D70 + 'p64_b6_ways.py', '6cd0add027e817b6f0c5e20619a5735dfd603737c5886188ff8708c254753f8f'),
       'p71': (D70 + 'p71_b7_ways.py', '3921b03fe5a4530479708437ad78d559d5c6fefb4b49332fd5c96b936706b4df'),
       'p95': (D70 + 'p95_close_checks.py', '6287cf2284c533a12505100d43542d4408d91bc5db64d1d527f9e059d4688aa0'),
       'p97': (D70 + 'p97_close_last.py', '91541c30866f7892d71a891aafedacef41cf3a818d45a4ea685ce6a39f82093a')}


def old(key):
    return prev(*OLD[key])
# END
