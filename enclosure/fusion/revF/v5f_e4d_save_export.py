# rev F e4d (2026-11-08): save the M2 pilots (e4b) as a new version, export the f3d and the STEP of the ReSpeaker carrier
#   and the 5807 cradle (d7d method: TemporaryBRep copy -> world frame -> new direct document -> STEP -> closed; the panel
#   document re-activated), then read each STEP back into a new document (volume, lumps, D1.6 bores, no D3.2 bore left).
#   Guard: the new parts and their hidden old copies. Writes m2_e4/e4d_status.json.
import os, traceback
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
OUT = os.path.expanduser('~/Documents/HA_panel_renders/m2_e4/e4d_status.json')
EXPECT = {'RESP_CARRIER_e4': 10.0716, 'CRADLE_5807_e4': 2.1775, 'HOUSING_F_front': 235.9107,
          'HOUSING_F_door': 47.2633}
NEW = {'RESP_CARRIER': 10.1214, 'CRADLE_5807': 2.1898}   # e4b's result
VERSION = ('rev F WIP 2026-11-08 e4: ReSpeaker and 5807 on M2 x 6 screws for plastic (no inserts) - the four ruthex M2 '
           'holes D3.2 x 4.5 filled and re-cut as D1.6 pilots with a 0.3 x 45 deg entry chamfer: carrier bosses 5.5 deep, '
           'cradle posts through the plate; cradle bezel roof slotted 4.6 wide over both 5807 screws for a straight driver; '
           'old parts hidden as RESP_CARRIER_e4 / CRADLE_5807_e4 (Claude)')
F3D = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-e4.f3d')
PARTS = [('RESP_CARRIER', 'resp_carrier'), ('CRADLE_5807', 'cradle_5807')]


def bores(body):
    n = {}
    for f in body.faces:
        if f.geometry.objectType == adsk.core.Cylinder.classType():
            r = round(adsk.core.Cylinder.cast(f.geometry).radius * 10, 2)
            n[r] = n.get(r, 0) + 1
    return n


def run(_context):
    st = {'t0': time.strftime('%H:%M:%S')}
    t0 = time.time()
    try:
        X = Ctx()
        exp = dict(EXPECT); exp.update(NEW)
        bad = [[k, None if X.body(k) is None else round(X.body(k).volume, 4)] for k, v in exp.items()
               if X.body(k) is None or abs(X.body(k).volume - v) > 0.0005]
        if not NEW:
            bad.append('NEW not set')
        st['guard_bad'] = bad
        if bad:
            raise RuntimeError('GUARD %s' % bad)
        st['saved'] = X.doc.save(VERSION)
        st['t_save'] = round(time.time() - t0, 1)
        em = X.des.exportManager
        em.execute(em.createFusionArchiveExportOptions(F3D))
        st['f3d_mb'] = round(os.path.getsize(F3D) / 1e6, 1)
        st['t_f3d'] = round(time.time() - t0, 1)
        log('v5f_e4d_save_export', 'saved', dict(st))
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
            step[tag] = {'ok': ok, 'bytes': os.path.getsize(path) if os.path.exists(path) else None,
                         'mtime': time.strftime('%H:%M:%S', time.localtime(os.path.getmtime(path))),
                         'cm3': round(nb.volume, 4), 'lumps': nb.lumps.count,
                         'bbox_world_mm': [round(v * 10, 2) for v in (bb.minPoint.x, bb.maxPoint.x, bb.minPoint.y,
                                                                      bb.maxPoint.y, bb.minPoint.z, bb.maxPoint.z)]}
            doc.close(False)
            rd = X.app.importManager.importToNewDocument(X.app.importManager.createSTEPImportOptions(path))
            rdes = adsk.fusion.Design.cast(rd.products.itemByProductType('DesignProductType'))
            bodies = [b for c in [rdes.rootComponent] + [o.component for o in rdes.rootComponent.allOccurrences]
                      for b in c.bRepBodies]
            step[tag]['readback'] = {'n_bodies': len(bodies), 'cm3': round(sum(b.volume for b in bodies), 4),
                                     'lumps': sum(b.lumps.count for b in bodies),
                                     'bores_r_mm': bores(bodies[0]) if bodies else None}
            rd.close(False)
            for d_ in X.app.documents:
                if d_.name == 'HA Panel v5 - tapered':
                    d_.activate(); break
            log('v5f_e4d_save_export', 'part', {tag: step[tag], 't_s': round(time.time() - t0, 1)})
        st['step'] = step
        st['active_after'] = X.app.activeDocument.name
        st['version_after'] = [X.doc.dataFile.versionNumber, X.doc.dataFile.latestVersionNumber, X.doc.isModified]
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    st['t_s'] = round(time.time() - t0, 1)
    json.dump(st, open(OUT, 'w'), indent=1)
    print(json.dumps(st))


run(None)
