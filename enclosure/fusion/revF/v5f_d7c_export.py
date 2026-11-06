# rev F audit-response d7c (2026-11-06): exports after the d-round (audit finding 42: stale STEP / f3d, no cap STEP;
#   RENDER_FABRIC_front was the pre-cap cloth). 1. guards, no leftovers; RENDER_FABRIC_front hidden (kept); inventory to the log.
#   2. named version + f3d ~/Documents/HA Panel v5 - tapered revF-d7.f3d. 3. STEP per printed part ~/Documents/HA_v5f_<part>.step
#   (now incl. the cap and the two touch clips), the b6x method: TemporaryBRep copy -> world frame (floor horizontal, z up,
#   y toward the viewer, x_rel = x + 2.55) -> new unsaved direct-modelling document -> STEP -> closed without saving.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
VERSION = 'rev F WIP 2026-11-06 d7: audit-response checks (matrix 433 pairs = audit + designed changes, sweeps 0) and exports (Claude)'
F3D = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-d7.f3d')
EXPECT = {'HOUSING_F_door': 47.2694, 'GROMMET_usbc_F': 0.5062, 'CRADLE_5807': 2.1775, 'HOUSING_F_front': 233.5514,
          'SPKBOX_L': 25.6082, 'SPKBOX_R': 25.6435, 'MAIN_BRACKET': 5.3431, 'TOUCH_CLIP_L': 0.4896, 'TOUCH_CLIP_R': 0.4896,
          'HOUSING_F_cap': 9.9227, 'SLAB_frame': 62.9324, 'RESP_CARRIER': 10.0716}
PARTS = [('HOUSING_F_front', 'front'), ('HOUSING_F_door', 'door'), ('HOUSING_F_cap', 'cap'), ('SLAB_frame', 'slab'),
         ('SPKBOX_L', 'spkbox_L'), ('SPKBOX_R', 'spkbox_R'), ('MAIN_BRACKET', 'main_bracket'), ('RESP_CARRIER', 'resp_carrier'),
         ('CRADLE_5807', 'cradle_5807'), ('GROMMET_usbc_F', 'grommet_usbc'), ('TOUCH_CLIP_L', 'touch_clip_L'),
         ('TOUCH_CLIP_R', 'touch_clip_R')]


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard: %s volume %s, expected %s' % (k, None if b is None else round(b.volume, 3), v))
        bad = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp') or b.name.startswith(('RENDER_tmp', 'PROBE_tmp'))
               or (b.name.startswith('HOUSING_F_') and '(' in b.name)]
        if bad:
            raise RuntimeError('leftover bodies: %s' % bad)
        rf = X.body('RENDER_FABRIC_front')
        if rf is not None and rf.isLightBulbOn:
            rf.isLightBulbOn = False; out['hidden'] = ['RENDER_FABRIC_front']
        inv = [(b.name, round(b.volume, 4), b.isLightBulbOn) for b in X.comp.bRepBodies]
        out['n_bodies'] = len(inv); out['n_visible'] = sum(1 for i in inv if i[2])
        log('v5f_d7c_export', 'inventory', {'bodies': inv})
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
    log('v5f_d7c_export', 'save', out)
    print(json.dumps(out, separators=(',', ':')))
