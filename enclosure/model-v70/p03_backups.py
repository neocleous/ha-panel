# Block 0: the hidden "_v69" copies of the bodies this pass changes (brief: "Before a body changes, keep a hidden _v69
# copy of it"). CHANGES THE DOCUMENT: adds one hidden body per name, a copy of the body as it stands at version 69.
# A body that comes to change later in the pass and is not in this list gets its copy then, before it changes.
# Run: runpy.run_path(D + 'p03_backups.py')['main']()  -> p03_backups.txt
import runpy

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
SUFFIX = '_v69'
# Printed parts the merge's section 4 names as changing in this pass (all but the cradle), and the bodies that are not
# printed which the brief changes: the strip envelopes (29.0 -> 28), the keep-outs behind the strips, the screw body
# (the grommet's two screws follow its new tab).
NAMES = ['GROMMET_usbc_F', 'HOUSING_F_door', 'FLOOR_PLATE', 'SLAB_frame', 'HOUSING_F_plate', 'HOUSING_F_front',
         'HOUSING_F_cap', 'MIC_CLAMP_L', 'MIC_CLAMP_R', 'RESP_CARRIER', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'BME_HOOD',
         'SPKBOX_L', 'SPKBOX_R',
         'MIC_strip_L_env', 'MIC_strip_R_env', 'KO_mic_L_back', 'KO_mic_R_back', 'SCREWS_M2x6_env']


def _main():
    k = L['load']()
    X = k.K()
    print('before:', X.state())
    for n in NAMES:
        if X.body(n) is None:
            raise RuntimeError('no body ' + n)
    for n in NAMES:
        if X.body(n + SUFFIX) is not None:
            print('  %-18s copy exists already' % n); continue   # a second call goes on where the first stopped
        b = X.body(n)
        t = X.tbm.copy(b)
        nb = X.add(t, n + SUFFIX, like=b, show=False)
        v0 = b.volume * 1000.0; v1 = nb.volume * 1000.0
        print('  %-18s -> %-22s %12.3f  %12.3f  lumps %d/%d  %s' % (n, nb.name, v0, v1, b.lumps.count, nb.lumps.count,
                                                                  'same' if abs(v0 - v1) < 0.001 else 'DIFFERS'))
    print('after:', X.state())


def main():
    L['out']('p03_backups.txt', _main)
