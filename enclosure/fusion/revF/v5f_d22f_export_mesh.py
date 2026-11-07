# rev F d22f (2026-11-07), read-only: the d22 front as a binary STL in world mm (x_rel), with the print audit's mesh settings
#   (0.01 mm chordal tolerance, 10 deg normal deviation), so the built solid is what gets sliced:
#   ~/Documents/HA_panel_renders/print_audit/exports/front_d22.stl (the audit's front.stl, d19, stays as it is).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/HA_panel_renders/print_audit/scripts/pa_common.py'), encoding='utf-8').read())
LOG = os.path.expanduser('~/Documents/v5f_log.json')          # pa_common points LOG at the audit's log; keep the design log
OUTS = os.path.join(PA_DIR, 'exports', 'front_d22.stl')
FRONT_D22 = 235.9107


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        b = X.body('HOUSING_F_front')
        if b is None or abs(b.volume - FRONT_D22) > 0.0005:
            raise RuntimeError('guard: HOUSING_F_front %s' % (None if b is None else round(b.volume, 4)))
        P, T = pa_world_mesh(b, 0.01)
        out['tris'] = pa_write_stl(OUTS, P, T, 'front_d22'); out['bytes'] = os.path.getsize(OUTS)
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d22f_export_mesh', 'run', out)
    print(json.dumps(out, separators=(',', ':')))
