# rev F e6d (2026-11-09): save the deeper door magnet pockets (e6b, V24) as a new version, export the f3d and the door's
#   STEP (d7d method: TemporaryBRep copy -> world frame -> new direct document -> STEP -> closed; the panel document
#   re-activated), then read the STEP back into a new document (volume, lumps, the ten D8.3 pocket floors 0.45 deeper).
#   Guard: the new door and its hidden old copy, the other printed parts. Load with a no-op run() after the exec (README
#   lesson 86). Writes e6/e6d_status.json.
import os, traceback
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
OUT = os.path.expanduser('~/Documents/HA_panel_renders/e6/e6d_status.json')
EXPECT = {'HOUSING_F_door_e6': 47.2633, 'HOUSING_F_door': 47.0198, 'HOUSING_F_front': 235.9107, 'HOUSING_F_cap': 9.9441,
          'RESP_CARRIER': 10.1214, 'CRADLE_5807': 2.1898, 'MAIN_BRACKET': 6.5563, 'GROMMET_usbc_F': 0.5062}
VERSION = ('rev F WIP 2026-11-09 e6: V24 lip magnets to AliExpress sizes - door N52 D8 x 2 in its 10 pockets, now 0.45 '
           'deeper (skin to the lap 0.9 -> 0.45, pocket 1.84-2.03 to the outer surface); lip N52 D8 x 1 in the unchanged lip '
           'pockets (1.6, CA); magnet faces 1.6 -> 1.15 apart, 3.9-4.3 N per pair ideal (designed 3.4-3.7); old door hidden '
           'as HOUSING_F_door_e6 (Claude)')
F3D = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-e6.f3d')
PARTS = [('HOUSING_F_door', 'door')]


def run(_context):
    st = {'t0': time.strftime('%H:%M:%S')}
    t0 = time.time()
    try:
        X = Ctx()
        bad = [[k, None if X.body(k) is None else round(X.body(k).volume, 4)] for k, v in EXPECT.items()
               if X.body(k) is None or abs(X.body(k).volume - v) > 0.0005]
        st['guard_bad'] = bad
        if bad:
            raise RuntimeError('GUARD %s' % bad)
        st['before'] = [X.doc.dataFile.versionNumber, X.doc.isModified]
        st['saved'] = X.doc.save(VERSION)
        st['t_save'] = round(time.time() - t0, 1)
        em = X.des.exportManager
        em.execute(em.createFusionArchiveExportOptions(F3D))
        st['f3d_mb'] = round(os.path.getsize(F3D) / 1e6, 1)
        st['t_f3d'] = round(time.time() - t0, 1)
        log('v5f_e6d_save_export', 'saved', dict(st))
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
            n415 = 0
            for b in bodies:
                for f in b.faces:
                    if f.geometry.objectType == adsk.core.Cylinder.classType() and \
                            abs(adsk.core.Cylinder.cast(f.geometry).radius * 10 - 4.15) < 0.005:
                        n415 += 1
            step[tag]['readback'] = {'n_bodies': len(bodies), 'cm3': round(sum(b.volume for b in bodies), 4),
                                     'lumps': sum(b.lumps.count for b in bodies), 'r4.15_cylinders': n415}
            rd.close(False)
            for d_ in X.app.documents:
                if d_.name == 'HA Panel v5 - tapered':
                    d_.activate(); break
            log('v5f_e6d_save_export', 'part', {tag: step[tag], 't_s': round(time.time() - t0, 1)})
        st['step'] = step
        st['active_after'] = X.app.activeDocument.name
        st['version_after'] = [X.doc.dataFile.versionNumber, X.doc.dataFile.latestVersionNumber, X.doc.isModified]
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    st['t_s'] = round(time.time() - t0, 1)
    json.dump(st, open(OUT, 'w'), indent=1)
    print(json.dumps(st))


run(None)
