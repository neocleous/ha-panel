# rev F audit-response d7d (2026-11-06): the remaining per-part STEP exports after d7c stopped behind the cap's temporary
#   document (front, door, cap were written; f3d and the version were done). Same method as b6x / d7c; the panel document is
#   re-activated by name after every part and each part is logged as it is written. PARTS can be set by the loader.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
REST = [('SLAB_frame', 'slab'), ('SPKBOX_L', 'spkbox_L'), ('SPKBOX_R', 'spkbox_R'), ('MAIN_BRACKET', 'main_bracket'),
        ('RESP_CARRIER', 'resp_carrier'), ('CRADLE_5807', 'cradle_5807'), ('GROMMET_usbc_F', 'grommet_usbc'),
        ('TOUCH_CLIP_L', 'touch_clip_L'), ('TOUCH_CLIP_R', 'touch_clip_R')]


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    parts = globals().get('PARTS') or REST
    try:
        M = adsk.core.Matrix3D.create()
        M.setCell(1, 1, C); M.setCell(1, 2, -S); M.setCell(2, 1, S); M.setCell(2, 2, C); M.setCell(2, 3, H / 10)
        step = {}
        for (bn, tag) in parts:
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
            for d in X.app.documents:
                if d.name == 'HA Panel v5 - tapered':
                    d.activate(); break
            log('v5f_d7d_step_rest', 'part', {tag: step[tag], 't_s': round(time.time() - t0, 1)})
        out['step'] = step
        out['active_after'] = X.app.activeDocument.name
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d7d_step_rest', 'done', out)
    print(json.dumps(out, separators=(',', ':')))
