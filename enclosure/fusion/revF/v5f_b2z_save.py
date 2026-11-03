# rev F block 2 save (2026-11-03): body inventory -> v5f_log.json, f3d export, named version (block 2 without the USB pocket).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
VERSION = 'rev F WIP 2026-11-03 b2: chambers, speakers + baffles, lattices, touch PCB retention, K5 lanes; USB pocket open (Claude)'
F3D = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-wip-b2.f3d')
KEY = ['HOUSING_E', 'SLAB_frame', 'LCD_glass', 'DOOR_F', 'SPK_L', 'SPK_R', 'TOUCH_PCB', 'KO_touch_back', 'TOOL_ring_opening_5p6', 'PI5_F', 'PI5_F_cooler', 'KO_K7_fan',
       'GPIO_plugA_env', 'GPIO_plugB_env', 'INNER_E', 'REF_E_outer']


def run(_context):
    X = Ctx()
    out = {}
    try:
        inv = [(b.name, round(b.volume, 3), b.isLightBulbOn) for b in X.comp.bRepBodies]
        out['n_bodies'] = len(inv)
        out['n_visible'] = sum(1 for i in inv if i[2])
        out['key_cm3'] = {n: v for (n, v, _) in inv if n in KEY or n.startswith('KO_K5_')}
        out['unexpected'] = [n for (n, _, _) in inv if n.startswith('RENDER_tmp_') or n.startswith('Body') or n.endswith('_tmp') or n.startswith('DBOSS_')]
        log('v5f_b2z_save', 'inventory', {'bodies': inv})
        em = X.des.exportManager
        out['f3d'] = em.execute(em.createFusionArchiveExportOptions(F3D))
        out['f3d_bytes'] = os.path.getsize(F3D) if os.path.exists(F3D) else None
        out['saved'] = X.doc.save(VERSION)
        out['version'] = VERSION
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-1]
    log('v5f_b2z_save', 'export + save', out)
    print(json.dumps(out))
