# rev F rework R1f (2026-11-04): the save run of R1e as sent (save branch only; logs under 'v5f_r1e_renders_save', step 'save').
# Guard on the front/door volumes, body inventory -> v5f_log.json, f3d export, named version.
# rev F rework R1e (2026-11-04): checkpoint renders for the rear-door block + named version + f3d.
# MODE 'renders' or 'save' (one per run).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
MODE = 'save'
OUT = os.path.expanduser('~/Documents/HA_panel_renders')
VERSION = 'rev F WIP 2026-11-04 R1: rear door split y -55, solid floor, 10 edge magnet pairs, 4 x M3 from below, USB-C bottom centre (Claude)'
F3D = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-wip-r1.f3d')
EXPECT = {'HOUSING_F_front': 265.519, 'HOUSING_F_door': 55.484}   # cm3 after R1c-2 (checked by R1d)


def run(_context):
    X = Ctx(); out = {'mode': MODE}
    try:
        out['doc'] = X.doc.name
        for n, v in EXPECT.items():
            b = X.body(n)
            if b is None or abs(b.volume - v) > 0.002:
                raise RuntimeError('guard: %s volume %s, expected %s' % (n, None if b is None else round(b.volume, 3), v))
        inv = [(b.name, round(b.volume, 3), b.isLightBulbOn) for b in X.comp.bRepBodies]
        out['n_bodies'] = len(inv); out['n_visible'] = sum(1 for i in inv if i[2])
        out['key_cm3'] = {n: v for (n, v, _) in inv if n.startswith('HOUSING_F') or n in ('PD_5807_env', 'KO_5807_pigtail', 'HOUSING_E', 'DOOR_F_b2')
                          or n.startswith('FOOT_') or n.startswith('TOOL_inner_skin')}
        out['unexpected'] = [n for (n, _, _) in inv if n.startswith('RENDER_tmp_') or n.endswith('_tmp') or '(' in n and n.startswith('HOUSING')]
        log('v5f_r1e_renders_save', 'inventory', {'bodies': inv})
        em = X.des.exportManager
        out['f3d'] = em.execute(em.createFusionArchiveExportOptions(F3D))
        out['f3d_bytes'] = os.path.getsize(F3D) if os.path.exists(F3D) else None
        out['saved'] = X.doc.save(VERSION)
        out['version'] = VERSION
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_r1e_renders_save', MODE, out)
    print(json.dumps(out))
