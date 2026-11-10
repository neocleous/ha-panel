# rev F f3b (2026-11-10): floor plate pass, block 3 - audit finding F3 and the cable-tie anchor.
#   F3: the ReSpeaker's USB-C plug cannot be pushed in in place (6.8 mm of travel to the shell at its new height, and 7 mm between
#       plug and wall for fingers), so it rides in with the display module, already plugged: notch in the wall beside the LCD
#       opening, x 55.55 (opening edge) .. 79.0, Zd -29.3 .. -11.2, through the wall (d 9.0 .. 14.8). Plug envelope after the 4 mm move:
#       x 45.28..77.28, Zd -26.44..-14.04. Nothing else is in the notch (probe f3a).
#   Anchor: the old floor's cable-tie anchor at (58.5, -56.5) rebuilt on the plate (legs 1.8 x 4.0, tunnel 3.0 wide to z 6.5, top z 8.0).
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
APPLY = globals().get('APPLY', False)


def run(_context):
    st = {'apply': APPLY}
    t0 = time.time()
    try:
        X = K()
        front = X.body('HOUSING_F_front'); plate = X.body('FLOOR_PLATE')
        s = X.cp(front); v0 = X.vol(s)
        X.dif(s, X.dbox(55.0, 79.0, 8.5, 15.3, -29.3, -11.2))
        st['shell'] = [round(v0, 1), round(X.vol(s) - v0, 1), len(X.lumps(s))]
        p = X.cp(plate); v0 = X.vol(p)
        anchor = X.wbox(55.2, 57.0, -58.5, -54.5, 2.0, 8.0)
        X.uni(anchor, X.wbox(60.0, 61.8, -58.5, -54.5, 2.0, 8.0)); X.uni(anchor, X.wbox(55.2, 61.8, -58.5, -54.5, 6.5, 8.0))
        X.uni(p, X.cp(anchor))
        st['plate'] = [round(v0, 1), round(X.vol(p) - v0, 1), len(X.lumps(p))]
        cl = {}
        for n in ('HOUSING_F_door', 'SPKBOX_L', 'USBA_plug_env', 'USBA_cable_env', 'PI5_F', 'CRADLE_5807', 'DOOR_tray', 'HOUSING_F_front'):
            b = X.body(n)
            v = X.clash(anchor, b) if b is not None else 'missing'
            if v:
                cl[n] = v if isinstance(v, str) else round(v, 2)
        st['anchor_clash'] = cl
        if APPLY:
            like = X.body('HOUSING_F_front_v42')
            front.deleteMe(); plate.deleteMe()
            a = X.add(s, 'HOUSING_F_front', like=like); b = X.add(p, 'FLOOR_PLATE', like=like)
            st['added'] = [round(a.volume * 1000, 1), a.lumps.count, round(b.volume * 1000, 1), b.lumps.count, X.dups(), X.root.bRepBodies.count]
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status('f3b', st)


run(None)
