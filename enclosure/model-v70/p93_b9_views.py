# Block 9: two views of the holder on the left box, for the record and for Daniel's chat. Shows a chosen set of bodies, takes the
# pictures, and puts every body's light bulb back as it was (checked by name before it returns). The two radar screws are shown
# as a temporary body cropped from SCREWS_M2x6_env and deleted again. Leaves the document's bodies and their visibility as found.
#   b9_view_back.png    from behind and above, from the middle of the unit toward the left box (the touch board behind the holder)
#   b9_view_front.png   from the screen side with the touch board and the shell taken away: the standoffs, the posts and the arm's pad
# Run: runpy.run_path(D + 'p93_b9_views.py')['main']()  -> p93_views.txt and the two pictures
import runpy
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
BACK = ('SPKBOX_L', 'SPK_L', 'TOUCH_PCB', 'TOUCH_components_env', 'TOUCH_CLIP_L', 'RADAR_HOLDER', 'LD2410C_env_F', 'LEAD_RADAR', 'PI5_F', 'PI5_F_cooler', 'FLOOR_PLATE')
FRONT = ('SPKBOX_L', 'SPK_L', 'TOUCH_CLIP_L', 'RADAR_HOLDER', 'LD2410C_env_F', 'LEAD_RADAR', 'PI5_F', 'PI5_F_cooler', 'FLOOR_PLATE')


def shot(k, X, fn, eye, target, extent):
    vp = X.app.activeViewport
    cam = vp.camera
    cam.isSmoothTransition = False
    cam.cameraType = adsk.core.CameraTypes.OrthographicCameraType
    cam.eye = k.Wp(*eye); cam.target = k.Wp(*target); cam.upVector = k.dv((0, 0, 1))
    cam.isFitView = False
    cam.viewExtents = extent / 10.0
    vp.camera = cam
    vp.refresh(); adsk.doEvents()
    ok = vp.saveAsImageFile(D + fn, 1800, 1200)
    print('%s: %s (eye %s, target %s, extent %s)' % (fn, ok, eye, target, extent))


def _main():
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    was = {}
    for b in X.root.bRepBodies:
        was[b.entityToken] = (b.name, b.isLightBulbOn)
    vis0 = sorted(n for n, v in was.values() if v)
    vp = X.app.activeViewport; cam0 = vp.camera
    s = X.wbox(18, 45, -8, 3, 27, 52); X.sec(s, X.tbm.copy(X.body('SCREWS_M2x6_env')))
    tmp = X.add(s, 'TMP_radar_screws', like=X.body('SCREWS_M2x6_env'), show=True)
    try:
        for names, fn, eye, target, ext in ((BACK, 'b9_view_back.png', (-25.0, -95.0, 95.0), (27.0, -2.0, 42.0), 78.0),
                                            (FRONT, 'b9_view_front.png', (-15.0, 95.0, 85.0), (27.0, -2.0, 42.0), 78.0)):
            for b in X.root.bRepBodies:
                b.isLightBulbOn = (b.name in names) or b.name == 'TMP_radar_screws'
            shot(k, X, fn, eye, target, ext)
    finally:
        tmp.deleteMe()
        for b in X.root.bRepBodies:
            w = was.get(b.entityToken)
            if w is not None and b.isLightBulbOn != w[1]:
                b.isLightBulbOn = w[1]
        cam0.isSmoothTransition = False
        vp.camera = cam0; vp.refresh()
    vis1 = sorted(b.name for b in X.root.bRepBodies if b.isLightBulbOn)
    print('visible before %d, after %d, the same names: %s' % (len(vis0), len(vis1), vis0 == vis1))
    if vis0 != vis1:
        raise RuntimeError('visibility not restored: %s' % sorted(set(vis0) ^ set(vis1)))
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p93_views.txt', _main)
