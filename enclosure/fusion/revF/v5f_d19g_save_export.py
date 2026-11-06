# rev F d19g (2026-11-06): version, f3d and STEP after d19 (46° gussets under the main-board bracket's lower board-boss arms,
#   printability). STEP for the bracket, the d7d method (TemporaryBRep copy -> world frame -> new direct document -> STEP ->
#   closed; the panel document re-activated by name, each part logged as it is written).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py'), encoding='utf-8').read())
import traceback
VERSION = ('rev F WIP 2026-11-06 d19: printability - 46 deg gussets under both main-board bracket halves\' lower board-boss arms '
           '(no support under them printed upright), insert holes kept (Claude)')
F3D = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-d19.f3d')
F3D_NEW = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-d19 new.f3d')
PARTS = [('MAIN_BRACKET', 'main_bracket')]


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        exp = {'HOUSING_F_front': 235.2269, 'MAIN_BRACKET': 6.5563, 'HOUSING_F_cap': 9.9591, 'BME_HOOD': 0.8029,
               'HOUSING_F_door': 47.2694, 'SPKBOX_R': 26.3874, 'SPKBOX_L': 25.6082}
        for k, v in exp.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard: %s %s, expected %s' % (k, None if b is None else round(b.volume, 4), v))
        bad = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp') or ('(' in b.name and b.isLightBulbOn)]
        if bad:
            raise RuntimeError('leftover bodies: %s' % bad)
        inv = [(b.name, round(b.volume, 4), b.isLightBulbOn) for b in X.comp.bRepBodies]
        out['n_bodies'] = len(inv); out['n_visible'] = sum(1 for i in inv if i[2])
        log('v5f_d19g_save_export', 'inventory', {'bodies': inv})
        out['saved'] = X.doc.save(VERSION); out['version'] = VERSION
        em = X.des.exportManager
        ok = em.execute(em.createFusionArchiveExportOptions(F3D_NEW))
        if ok and os.path.exists(F3D_NEW) and os.path.getsize(F3D_NEW) > 50e6:
            os.replace(F3D_NEW, F3D)
        out['f3d'] = ok; out['f3d_bytes'] = os.path.getsize(F3D) if os.path.exists(F3D) else None
        out['f3d_new_left'] = os.path.exists(F3D_NEW)
        log('v5f_d19g_save_export', 'saved', dict(out))
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
            log('v5f_d19g_save_export', 'part', {tag: step[tag], 't_s': round(time.time() - t0, 1)})
        out['step'] = step
        out['active_after'] = X.app.activeDocument.name
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d19g_save_export', 'done', out)
    print(json.dumps(out, separators=(',', ':')))
