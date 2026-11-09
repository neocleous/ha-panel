# rev F e5e (2026-11-09): save the J10 sensor leads (e5d) as a new version and export the f3d. Guard: the new leads and
#   their hidden old copies, the main parts unchanged. No STEP export (no printed part changed). Writes e5/e5e_status.json.
import os, traceback
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
OUT = os.path.expanduser('~/Documents/HA_panel_renders/e5/e5e_status.json')
EXPECT = {'HOUSING_F_front': 235.9107, 'HOUSING_F_door': 47.2633, 'MAIN_BRACKET': 6.5563, 'RESP_CARRIER': 10.1214,
          'CRADLE_5807': 2.1898, 'LEAD_BME680': 0.6381, 'LEAD_VEML': 0.8101, 'LEAD_BME680_e5': 0.7753,
          'LEAD_VEML_e5': 1.1381}
VERSION = ('rev F WIP 2026-11-09 e5: V23b - BME680 and VEML6030 leads re-routed to main-board J10 (columns x_rel -18.42 / '
           '-20.97, z 77.5, front face y -63.4): D3 tubes, routed 90.5 / 114.7 mm, sensor ends unchanged, >= 2.5 from every '
           'current body away from the sensor ends and J10; old leads hidden as LEAD_BME680_e5 / LEAD_VEML_e5. V26 (touch rev D '
           'back parts) and V27 (strip port) checked, no change (Claude)')
F3D = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-e5.f3d')


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
        st['after'] = [X.doc.dataFile.versionNumber, X.doc.dataFile.latestVersionNumber, X.doc.isModified]
        log('v5f_e5e_save', 'saved', dict(st))
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    st['t_s'] = round(time.time() - t0, 1)
    json.dump(st, open(OUT, 'w'), indent=1)
    print(json.dumps(st))


run(None)
