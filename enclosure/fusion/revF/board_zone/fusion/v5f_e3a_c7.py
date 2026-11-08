# rev F e3a (2026-11-08): main board rev 2.1 (MAIN_env rev 2.1, docs @ 236be84) - C7 (Wuerth 860160572003, 22 uF 35 V,
#   D5.0 +-0.5, 12.5 max, through-hole on the front) moved to the top strip above the NID. Adds two hidden bodies:
#   MAIN_C7_env  cylinder D5.5 (max), axis world y, centre x_rel -5.67, z 86.05, y -63.4..-50.9 (12.5)
#   KO_C7_vent   cylinder D5.5, y -50.9..-47.9: the 3 mm Wuerth asks to keep free above the vent (datasheet 1.6)
#   The old place (x_rel 0.5, z 66.6) never had a body: the model's board parts are the MAIN_* envelopes. Activates the
#   design first if needed. Not saved here (e3c saves).
import os, traceback, math
import adsk.core
app0 = adsk.core.Application.get()
_prev = app0.activeDocument.name
_doc = [d for d in app0.documents if d.name == 'HA Panel v5 - tapered'][0]
if _prev != _doc.name:
    _doc.activate()
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
OUT = os.path.expanduser('~/Documents/HA_panel_renders/board_zone/e3a_status.json')
GUARD = {'HOUSING_F_front': 235.9107, 'HOUSING_F_door': 47.2633, 'MAIN_BRACKET': 6.5563, 'MAIN_pcb': 7.9192,
         'MAIN_front_env': 146.9829, 'MAIN_back_env': 14.2437}
XR, ZC, R = -5.67, 86.05, 2.75
EXPECT = {'MAIN_C7_env': math.pi * R * R * 12.5 / 1000, 'KO_C7_vent': math.pi * R * R * 3.0 / 1000}


def ycyl(tbm, x_rel, z, r, y0, y1):
    return tbm.createCylinderOrCone(Dw(XC + x_rel, y0, z), r / 10, Dw(XC + x_rel, y1, z), r / 10)


def run(_context):
    st = {'t0': time.strftime('%H:%M:%S'), 'active_before': _prev}
    try:
        X = Ctx(); tbm = X.tbm
        st['version'] = [X.doc.dataFile.versionNumber, X.doc.dataFile.latestVersionNumber]
        bad = [[k, None if X.body(k) is None else round(X.body(k).volume, 4)] for k, v in GUARD.items()
               if X.body(k) is None or abs(X.body(k).volume - v) > 0.0005]
        if X.doc.isModified:
            bad.append('document modified')
        for k in EXPECT:
            if X.body(k) is not None:
                bad.append(k + ' exists')
        st['guard_bad'] = bad
        if bad:
            raise RuntimeError('GUARD %s' % bad)
        bodies = {'MAIN_C7_env': ycyl(tbm, XR, ZC, R, -63.4, -50.9), 'KO_C7_vent': ycyl(tbm, XR, ZC, R, -50.9, -47.9)}
        st['temp_vol'] = {k: round(b.volume, 5) for k, b in bodies.items()}
        off = {k: round(bodies[k].volume - v, 5) for k, v in EXPECT.items() if abs(bodies[k].volume - v) > 0.0002}
        if off:
            raise RuntimeError('volume check %s' % off)
        c = bodies['MAIN_C7_env'].boundingBox
        xr = [round(c.minPoint.x * 10 - XC, 3), round(c.maxPoint.x * 10 - XC, 3)]
        st['C7_x_rel'] = xr
        if abs(xr[0] - (XR - R)) > 0.01 or abs(xr[1] - (XR + R)) > 0.01:
            raise RuntimeError('placement check %s' % xr)
        new = {}
        for k, tb in bodies.items():
            b = X.add(tb, k); b.isLightBulbOn = False
            new[k] = {'vol': round(b.volume, 5), 'lumps': b.lumps.count, 'faces': b.faces.count}
        st['new'] = new
        log('v5f_e3a_c7', 'done', {'new': new})
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    json.dump(st, open(OUT, 'w'), indent=1)
    print(json.dumps(st))


run(None)
