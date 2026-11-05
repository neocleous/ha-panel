# rev F block 6x (2026-11-05): final named version + f3d + per-part STEP (brief 6.4).
#   1. Guards (front / door volumes, no *_tmp / RENDER_tmp / PROBE_tmp bodies), inventory to the log.
#   2. Named version 'rev F 2026-11-03 final (Claude)'; f3d ~/Documents/HA Panel v5 - tapered revF-final.f3d.
#   3. STEP per printed part ~/Documents/HA_v5f_<part>.step: the body copied as TemporaryBRep, transformed design → world
#      (floor horizontal, z up from the floor, y toward the viewer, x as in the design: x_rel = x + 2.55), added to a new
#      unsaved direct-modelling document, exported (root component), document closed without saving.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
VERSION = 'rev F 2026-11-03 final (Claude)'
F3D = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-final.f3d')
EXPECT = {'HOUSING_F_front': 239.797, 'HOUSING_F_door': 50.601}
PARTS = [('HOUSING_F_front', 'front'), ('HOUSING_F_door', 'door'), ('SLAB_frame', 'slab'), ('SPKBOX_L', 'spkbox_L'),
         ('SPKBOX_R', 'spkbox_R'), ('MAIN_BRACKET', 'main_bracket'), ('RESP_CARRIER', 'resp_carrier'), ('CRADLE_5807', 'cradle_5807'),
         ('GROMMET_usbc_F', 'grommet_usbc')]


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.002:
                raise RuntimeError('guard: %s volume %s, expected %s' % (k, None if b is None else round(b.volume, 3), v))
        bad = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp') or b.name.startswith(('RENDER_tmp', 'PROBE_tmp'))
               or (b.name.startswith('HOUSING_F_') and '(' in b.name)]
        if bad:
            raise RuntimeError('leftover bodies: %s' % bad)
        inv = [(b.name, round(b.volume, 4), b.isLightBulbOn) for b in X.comp.bRepBodies]
        out['n_bodies'] = len(inv); out['n_visible'] = sum(1 for i in inv if i[2])
        log('v5f_b6x_final_save_export', 'inventory', {'bodies': inv})
        out['saved'] = X.doc.save(VERSION); out['version'] = VERSION
        em = X.des.exportManager
        out['f3d'] = em.execute(em.createFusionArchiveExportOptions(F3D))
        out['f3d_bytes'] = os.path.getsize(F3D) if os.path.exists(F3D) else None
        M = adsk.core.Matrix3D.create()
        M.setCell(1, 1, C); M.setCell(1, 2, -S); M.setCell(2, 1, S); M.setCell(2, 2, C); M.setCell(2, 3, H / 10)
        panel = X.doc; step = {}
        for (bn, tag) in PARTS:
            t = X.tbm.copy(X.body(bn)); X.tbm.transform(t, M)
            doc = X.app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
            des = adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
            des.designType = adsk.fusion.DesignTypes.DirectDesignType
            nb = des.rootComponent.bRepBodies.add(t); nb.name = 'HA_v5f_' + tag
            bb = nb.boundingBox
            path = os.path.expanduser('~/Documents/HA_v5f_%s.step' % tag)
            ok = des.exportManager.execute(des.exportManager.createSTEPExportOptions(path, des.rootComponent))
            step[tag] = {'ok': ok, 'bytes': os.path.getsize(path) if os.path.exists(path) else None, 'cm3': round(nb.volume, 3),
                         'lumps': nb.lumps.count,
                         'bbox_world_mm': [round(v * 10, 1) for v in (bb.minPoint.x, bb.maxPoint.x, bb.minPoint.y, bb.maxPoint.y, bb.minPoint.z, bb.maxPoint.z)]}
            doc.close(False)
            if X.app.activeDocument != panel:
                panel.activate()
        out['step'] = step
        out['active_after'] = X.app.activeDocument.name
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b6x_final_save_export', 'save', out)
    print(json.dumps(out))
