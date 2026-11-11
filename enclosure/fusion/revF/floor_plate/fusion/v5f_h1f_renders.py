# rev F h1f (2026-11-11): step 3, block 1 - pictures of the rev 3 main board in place (door off). Visibility, opacity, style and
#   camera are restored at the end; nothing is added to the model. Files: fp/step3/h1_<shot>.png (1600 x 1200) + _check.jpg (800 x 600).
#   Shots: door = the open back, eye on the board's normal 450 mm behind it; board = the same eye, narrow lens; plugs = with the plug
#   envelopes; keys = with the cap-screw and display-screw key paths and the supply module's top tolerance; left34 / right34 = from behind
#   and above; stack = display module alone from the side (+u), with the nearest cap-screw key path.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_h_lib.py'), encoding='utf-8').read())
PRE = globals().get('PRE', 'h1')
KEYS = ['KO_capkey_BL', 'KO_capkey_BR', 'KO_capkey_SL', 'KO_capkey_SR', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR']
STACK = ['SLAB_frame', 'LCD_glass', 'LCD_panel_body', 'LCD_pcb_76x110', 'LCD_Pi_standoff_d15.2', 'RESP_CARRIER', 'RESP_pcb', 'RESP_top_env', 'RESP_mic_env',
         'RESP_usbc_plug_env', 'MAIN_pcb', 'MAIN_PS1', 'MAIN_conn', 'MAIN_tall', 'MAIN_low', 'MAIN_J2_plug_env', 'KO_capkey_SR', 'KO_capkey_SL']
SHOTS = globals().get('SHOTS', [
    ('door', ('B', 0, -12, 450), ('B', 0, -12, 0), 0.50, 'v', [], None),
    ('board', ('B', 0, -12, 450), ('B', 0, -6, 0), 0.26, 'v', [], None),
    ('plugs', ('B', 0, -12, 450), ('B', 0, -6, 0), 0.26, 'v', ['MAIN_plug_env'], None),
    ('keys', ('B', 0, -12, 450), ('B', 0, -6, 0), 0.26, 'v', KEYS + ['MAIN_PS1_tol'], None),
    ('left34', ('W', 250, -330, 250), ('W', 2.5, -30, 100), 0.42, 'z', [], None),
    ('right34', ('W', -250, -330, 250), ('W', 2.5, -30, 100), 0.42, 'z', [], None),
    ('stack', ('B', 420, 0, 5), ('B', 0, 0, 5), 0.30, 'v', [], STACK)])
GHOST = globals().get('GHOST', {'MAIN_plug_env': 0.45, 'MAIN_PS1_tol': 0.6})


def run(_context):
    st = {}
    t0 = time.time()
    X = K()
    vp = X.app.activeViewport
    cam0 = vp.camera; style0 = vp.visualStyle
    vis0 = [(b, b.isLightBulbOn, b.opacity) for b in X.root.bRepBodies]
    base = set(b.name for b, v, o in vis0 if v)
    try:
        os.makedirs(S3, exist_ok=True)
        vp.visualStyle = adsk.core.VisualStyles.ShadedWithVisibleEdgesOnlyVisualStyle
        shots = {}
        for nm, eye, tgt, ang, upk, extra, only in SHOTS:
            show = set(only) if only else base | set(extra)
            for b, v, o in vis0:
                want = b.name in show
                if b.isLightBulbOn != want:
                    b.isLightBulbOn = want
                op = GHOST.get(b.name, 0.3 if b.name.startswith('KO_') else o)
                if want and abs(b.opacity - op) > 1e-6:
                    b.opacity = op
            pe = Bp(*eye[1:]) if eye[0] == 'B' else Wp(*eye[1:])
            pt = Bp(*tgt[1:]) if tgt[0] == 'B' else Wp(*tgt[1:])
            for _ in range(2):
                cam = vp.camera
                cam.cameraType = adsk.core.CameraTypes.PerspectiveCameraType
                cam.isSmoothTransition = False
                cam.isFitView = False
                cam.target = pt; cam.eye = pe; cam.upVector = V3(0, 0, 1) if upk == 'v' else V3(0, S, C)
                cam.perspectiveAngle = ang
                vp.camera = cam
                adsk.doEvents(); vp.refresh()
            p = os.path.join(S3, '%s_%s.png' % (PRE, nm))
            ok = vp.saveAsImageFile(p, 1600, 1200)
            vp.saveAsImageFile(p.replace('.png', '_check.jpg'), 800, 600)
            shots[nm] = bool(ok)
            st['shots'] = shots; status3(PRE + '_renders', st)
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    try:
        for b, v, o in vis0:
            if b.isLightBulbOn != v:
                b.isLightBulbOn = v
            if abs(b.opacity - o) > 1e-6:
                b.opacity = o
        vp.visualStyle = style0
        cam0.isSmoothTransition = False
        vp.camera = cam0
        adsk.doEvents(); vp.refresh()
        st['restored'] = [sum(1 for b in X.root.bRepBodies if b.isLightBulbOn), X.root.bRepBodies.count]
    except Exception:
        st['CLEANUP_FAIL'] = traceback.format_exc().splitlines()[-6:]
    st['t_end'] = round(time.time() - t0, 1)
    status3(PRE + '_renders', st)


run(None)
