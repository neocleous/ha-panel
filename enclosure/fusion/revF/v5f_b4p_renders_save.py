# rev F block 4p (2026-11-05): checkpoint-4 renders + named version + f3d (MODE per run).
# Renders (1600 × 1200 + 480 × 360 check JPEGs) into ~/Documents/HA_panel_renders/:
#   HA_v5f_b4_rear_open.png    door off, from the rear-left above: main board + bracket (envelopes), Pi, 5807 cradle, boxes,
#                              ReSpeaker carrier, BME680, every routed lead (red), USB-A plug/cable (blue)
#   HA_v5f_b4_resp.png         the ReSpeaker on its carrier behind the LCD, from the rear-right above, plug envelope blue
#   HA_v5f_b4_inlet.png        the closed housing from the rear, low: door inlet cutout with the cradle bezel and receptacle
#   HA_v5f_b4_v11.png          the Pi's rear edge from above-behind: V11 option envelopes (a_px red, b_up blue), cradle, main board
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
MODE = 'renders'
OUT = os.path.expanduser('~/Documents/HA_panel_renders')
VERSION = ('rev F WIP 2026-11-05 b4: main board + bracket, 5807 cradle + inlet bezel, ReSpeaker carrier on the LCD standoffs, '
           '+x box USB slot, BME680 spot + slots, exhaust slots, floor tie anchors, V11 envelopes, all leads routed (Claude)')
F3D = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-wip-b4.f3d')
EXPECT = {'HOUSING_F_front': 242.147, 'HOUSING_F_door': 55.102, 'SPKBOX_L': 25.623, 'SPKBOX_R': 25.071, 'CRADLE_5807': 1.827,
          'RESP_CARRIER': 10.072}


def shoot(X, path, d, up, tgt, w=1600, h=1200, ortho=False):
    vp = X.app.activeViewport
    cam = vp.camera
    n = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2)
    cam.cameraType = adsk.core.CameraTypes.OrthographicCameraType if ortho else adsk.core.CameraTypes.PerspectiveCameraType
    cam.target = Dw(*tgt); cam.eye = Dw(tgt[0] + 600 * d[0] / n, tgt[1] + 600 * d[1] / n, tgt[2] + 600 * d[2] / n)
    cam.upVector = up; cam.isSmoothTransition = False
    cam.isFitView = True
    vp.camera = cam
    vp.refresh()
    ok = vp.saveAsImageFile(path, w, h)
    vp.saveAsImageFile(path.replace('.png', '_check.jpg'), 480, 360)
    return ok


def ap(X, names):
    try:
        for i in range(X.app.materialLibraries.count):
            lib = X.app.materialLibraries.item(i)
            if 'Appearance' not in lib.name:
                continue
            for nm in names:
                a = lib.appearances.itemByName(nm)
                if a:
                    return X.des.appearances.itemByName(nm) or X.des.appearances.addByCopy(a, nm)
    except Exception:
        return None


def run(_context):
    X = Ctx(); out = {'mode': MODE}
    vis0 = {b.name: b.isLightBulbOn for b in X.comp.bRepBodies}
    vs0 = X.app.activeViewport.visualStyle
    tmp = []
    try:
        out['doc'] = X.doc.name
        for n, v in EXPECT.items():
            b = X.body(n)
            if b is None or abs(b.volume - v) > 0.002:
                raise RuntimeError('guard: %s volume %s, expected %s' % (n, None if b is None else round(b.volume, 3), v))
        names = [b.name for b in X.comp.bRepBodies]
        if MODE == 'renders':
            os.makedirs(OUT, exist_ok=True)
            X.app.activeViewport.visualStyle = adsk.core.VisualStyles.ShadedWithVisibleEdgesOnlyVisualStyle
            red = ap(X, ('Paint - Enamel Glossy (Red)', 'Plastic - Glossy (Red)'))
            blue = ap(X, ('Paint - Enamel Glossy (Blue)', 'Plastic - Glossy (Blue)'))
            show = lambda keep: [setattr(b, 'isLightBulbOn', b.name in keep) for b in X.comp.bRepBodies]

            def dup(n, col):
                e = X.add(X.tbm.copy(X.body(n)), 'RENDER_tmp_' + n); tmp.append(e)
                if col is not None:
                    e.appearance = col
                return e.name
            leads = [n for n in names if n.startswith('LEAD_') and not n.endswith('_b4n')]
            base = ['HOUSING_F_front', 'SLAB_frame', 'LCD_glass', 'SPKBOX_L', 'SPKBOX_R', 'PI5_F', 'PI5_F_cooler', 'MAIN_BRACKET', 'CRADLE_5807',
                    'RESP_CARRIER', 'TOUCH_PCB']
            keep = base + [dup(n, red) for n in leads] + [dup(n, blue) for n in ('USBA_plug_env', 'USBA_cable_env', 'RESP_pcb', 'MAIN_pcb',
                                                                                  'PD_5807_env', 'BME680_env')]
            show(keep)
            out['rear_open'] = shoot(X, os.path.join(OUT, 'HA_v5f_b4_rear_open.png'), (0.55, -1.0, 0.75), UP, tgt=(XC, -35.0, 80.0))
            keep2 = ['HOUSING_F_front', 'SLAB_frame', 'LCD_glass', 'RESP_CARRIER'] + [n for n in names if n.startswith('LCD_')] + \
                    [t.name for t in tmp if t.name.endswith(('RESP_pcb', 'LEAD_MIC_L', 'LEAD_MIC_R', 'LEAD_DSI', 'LEAD_USB_RESP', 'LEAD_LCD_5V'))] + \
                    [dup('RESP_usbc_plug_env', blue), dup('RESP_top_env', None)]
            show(keep2)
            out['resp'] = shoot(X, os.path.join(OUT, 'HA_v5f_b4_resp.png'), (-0.6, -1.0, 0.45), UP, tgt=(XC + 5.0, -18.0, 112.0))
            show(['HOUSING_F_front', 'HOUSING_F_door', 'SLAB_frame', 'CRADLE_5807', 'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR',
                  dup('PD_5807_env', blue)])
            out['inlet'] = shoot(X, os.path.join(OUT, 'HA_v5f_b4_inlet.png'), (0.25, -1.0, 0.12), UP, tgt=(XC, -84.0, 16.0))
            show(['HOUSING_F_front', 'PI5_F', 'PI5_F_cooler', 'CRADLE_5807', 'MAIN_BRACKET', dup('MAIN_pcb', None), dup('PD_5807_env', None),
                  dup('V11a_px', red), dup('V11b_up', blue)])
            out['v11'] = shoot(X, os.path.join(OUT, 'HA_v5f_b4_v11.png'), (-0.35, -1.0, 0.9), UP, tgt=(XC - 20.0, -66.0, 20.0))
        else:
            inv = [(b.name, round(b.volume, 3), b.isLightBulbOn) for b in X.comp.bRepBodies]
            out['n_bodies'] = len(inv); out['n_visible'] = sum(1 for i in inv if i[2])
            out['key_cm3'] = {n: v for (n, v, _) in inv if n.startswith(('HOUSING_F', 'SPKBOX', 'CRADLE', 'RESP_CARRIER', 'MAIN_BRACKET'))}
            out['unexpected'] = [n for (n, _, _) in inv if n.startswith('RENDER_tmp_') or n.endswith('_tmp') or ('(' in n and n.startswith(('HOUSING', 'SPKBOX')))]
            log('v5f_b4p_renders_save', 'inventory', {'bodies': inv})
            em = X.des.exportManager
            out['f3d'] = em.execute(em.createFusionArchiveExportOptions(F3D))
            out['f3d_bytes'] = os.path.getsize(F3D) if os.path.exists(F3D) else None
            out['saved'] = X.doc.save(VERSION)
            out['version'] = VERSION
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    finally:
        for t in tmp:
            try: t.deleteMe()
            except Exception: pass
        for b in X.comp.bRepBodies:
            if b.name in vis0: b.isLightBulbOn = vis0[b.name]
        X.app.activeViewport.visualStyle = vs0
    if MODE == 'renders':
        out['files'] = sorted(f for f in os.listdir(OUT) if f.startswith('HA_v5f_b4_'))
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('RENDER_tmp_')]
    log('v5f_b4p_renders_save', MODE, out)
    print(json.dumps(out))
