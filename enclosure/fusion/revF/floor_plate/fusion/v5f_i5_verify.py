# rev F i5 (2026-11-11): step 3 repeated, close of part 1 - read-only: the saved model read back.
#   A  version, modified flag, bodies, visible bodies, template bodies left, the backups of this pass
#   B  the board's eight bodies and the carrier against every current body, leads included (the front shell as its crop to the site):
#      every pair that is not 0 mm3
#   C  the carrier: volume, lumps, the posts read from its cylinder faces (u, v, radius, depth from .. to)
#   D  the board's holes read from MAIN_pcb's cylinder faces; the 16 leads' lengths from their volumes
#   Results are kept in the cache and a call stops after BUDGET seconds: call until 'left' is 0.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_i_lib.py'), encoding='utf-8').read())
BUDGET = globals().get('BUDGET', 35.0)
MINE = ['MAIN_pcb', 'MAIN_PS1', 'MAIN_PS1_tol', 'MAIN_conn', 'MAIN_tall', 'MAIN_low', 'MAIN_plug_env', 'MAIN_J2_plug_env', 'RESP_CARRIER']
RAD = {'LEAD_PIGTAIL_20V': 1.6, 'LEAD_SPK_L': 1.6, 'LEAD_SPK_R': 1.6, 'LEAD_RADAR': 1.3, 'LEAD_TOUCH': 1.2, 'LEAD_BME680': 1.5, 'LEAD_VEML': 1.5, 'LEAD_GPIO_A1': 1.5,
       'LEAD_GPIO_A2': 2.0, 'LEAD_GPIO_B': 1.7, 'LEAD_LCD_5V': 1.5, 'LEAD_MIC_L': 1.0, 'LEAD_MIC_R': 1.0, 'LEAD_DSI': 1.5, 'LEAD_PI_POWER': 2.5, 'LEAD_USB_RESP': 1.7}


def cyls(b, rr=None):
    out = []
    for f in b.faces:
        g = f.geometry
        if g.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType and (rr is None or abs(g.radius * 10 - rr) < 0.01):
            o = Bf(g.origin); bb = f.boundingBox
            out.append([round(o[0], 2), round(o[1], 2), round(g.radius * 10, 2), round(-bb.maxPoint.y * 10, 2), round(-bb.minPoint.y * 10, 2)])
    return sorted(out)


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        c = cache()
        df = X.doc.dataFile
        nm = X.names()
        st['A'] = {'version': [df.versionNumber, df.latestVersionNumber], 'modified': X.doc.isModified, 'bodies': len(nm),
                   'visible': sum(1 for b in X.root.bRepBodies if b.isLightBulbOn), 'templates': [n for n in nm if n.startswith(('AUD_', 'NEW_', 'RENDER_tmp_'))],
                   'dups': X.dups(), 'backups _v50': sorted(n for n in nm if n.endswith('_v50')), 'current': len(current(X, leads=True))}
        if 'crop_front_site' not in c:
            t = X.cp(tcopy(X, 'HOUSING_F_front')); X.sec(t, X.dbox(U0 - 62, U0 + 62, -30, 75, V0 - 47, V0 + 47)); c['crop_front_site'] = t
        res = c.setdefault('i5', {})
        left = 0
        others = current(X, leads=True)
        for a in MINE:
            src = tcopy(X, a)
            for b in others:
                if b.name == a or (b.name in MINE and MINE.index(b.name) < MINE.index(a)):
                    continue
                k = a + '~' + b.name
                if k in res:
                    continue
                if time.time() - t0 > BUDGET:
                    left += 1; continue
                if not src.boundingBox.intersects(b.boundingBox):
                    res[k] = 0.0; continue
                big = c['crop_front_site'] if b.name == 'HOUSING_F_front' else tcopy(X, b.name)
                res[k] = round(xvol(X, src, big), 2)
        st['B'] = {'pairs': len(res), 'left': left, 'not zero': {k: v for k, v in res.items() if abs(v) > 0.005}}
        car = X.body('RESP_CARRIER')
        st['C'] = {'vol': round(X.vol(car), 1), 'lumps': car.lumps.count, 'posts': [q for q in cyls(car) if q[2] in (2.0, 4.0)]}
        st['D'] = {'holes': sorted(set((q[0], q[1]) for q in cyls(X.body('MAIN_pcb'), 1.6))),
                   'lead lengths': {b.name[5:]: round(X.vol(b) / (math.pi * RAD[b.name] ** 2), 1) for b in others if b.name.startswith('LEAD_')}}
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('i5', st)


run(None)
