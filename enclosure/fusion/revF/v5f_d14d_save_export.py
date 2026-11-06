# rev F d14d (2026-11-06): version, f3d and STEP after d14 (microSD floor hatch). STEP only for the parts that changed (front,
#   right box) and the new cover and sled, the d7d method (TemporaryBRep copy -> world frame -> new direct document ->
#   STEP -> closed; the panel document re-activated by name after every part, each part logged as it is written).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
VERSION = ('rev F WIP 2026-11-06 d14: microSD floor hatch (option 1, Daniel 19:22) - pocket in SPKBOX_R, floor slot + rebate, '
           'snap cover, card sled (Claude)')
F3D = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-d14.f3d')
PARTS = [('HOUSING_F_front', 'front'), ('SPKBOX_R', 'spkbox_R'), ('HATCH_COVER', 'hatch_cover'), ('SD_SLED', 'sd_sled')]


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        exp = {'HOUSING_F_front': 234.701, 'HOUSING_F_cap': 9.9591, 'BME_HOOD': 0.8029, 'HATCH_COVER': 0.586, 'SD_SLED': 1.1956,
               'HOUSING_F_door': 47.2694, 'SPKBOX_R': 25.5694, 'SPKBOX_L': 25.6082}
        for k, v in exp.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard: %s %s, expected %s' % (k, None if b is None else round(b.volume, 4), v))
        bad = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp') or ('(' in b.name and b.isLightBulbOn)]
        if bad:
            raise RuntimeError('leftover bodies: %s' % bad)
        inv = [(b.name, round(b.volume, 4), b.isLightBulbOn) for b in X.comp.bRepBodies]
        out['n_bodies'] = len(inv); out['n_visible'] = sum(1 for i in inv if i[2])
        log('v5f_d14d_save_export', 'inventory', {'bodies': inv})
        out['saved'] = X.doc.save(VERSION); out['version'] = VERSION
        em = X.des.exportManager
        out['f3d'] = em.execute(em.createFusionArchiveExportOptions(F3D))
        out['f3d_bytes'] = os.path.getsize(F3D) if os.path.exists(F3D) else None
        log('v5f_d14d_save_export', 'saved', dict(out))
        M = adsk.core.Matrix3D.create()
        M.setCell(1, 1, C); M.setCell(1, 2, -S); M.setCell(2, 1, S); M.setCell(2, 2, C); M.setCell(2, 3, H / 10)
        step = {}
        for (bn, tag) in PARTS:
            t = X.tbm.copy(X.body(bn)); X.tbm.transform(t, M)
            doc = X.app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
            des = adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
            des.designType = adsk.fusion.DesignTypes.DirectDesignType
            nb = des.rootComponent.bRepBodies.add(t); nb.name = 'HA_v5f_' + tag
            bb = nb.boundingBox
            path = os.path.expanduser('~/Documents/HA_v5f_%s.step' % tag)
            ok = des.exportManager.execute(des.exportManager.createSTEPExportOptions(path, des.rootComponent))
            step[tag] = {'ok': ok, 'bytes': os.path.getsize(path) if os.path.exists(path) else None, 'cm3': round(nb.volume, 4),
                         'lumps': nb.lumps.count,
                         'bbox_world_mm': [round(v * 10, 1) for v in (bb.minPoint.x, bb.maxPoint.x, bb.minPoint.y, bb.maxPoint.y, bb.minPoint.z, bb.maxPoint.z)]}
            doc.close(False)
            for d_ in X.app.documents:
                if d_.name == 'HA Panel v5 - tapered':
                    d_.activate(); break
            log('v5f_d14d_save_export', 'part', {tag: step[tag], 't_s': round(time.time() - t0, 1)})
        out['step'] = step
        out['active_after'] = X.app.activeDocument.name
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d14d_save_export', 'done', out)
    print(json.dumps(out, separators=(',', ':')))
