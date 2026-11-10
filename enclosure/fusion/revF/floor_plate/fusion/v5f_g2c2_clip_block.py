# rev F g2c2 (2026-11-10): step 1, block 2 - read-only: the touch clip (+x side) and the block on the speaker box it is screwed to, as
# sections (bounding boxes of thin slices), and what else sits near them.
import os, re
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
LEGACY = ('DOOR_tray', 'HOUSING_E', 'HOUSING_shell', 'HOUSING_F_wip', 'AMP_env_20x20x10', 'BUCK_20to5V_env_43x25x13', 'DOOR_plate_revE', 'GROMMET_usbc',
          'HOUSING_F_front_d10_sliver', 'HOUSING_F_front_d12a_sliver1', 'LD2410C_env', 'MAIN_BRACKET_d1split_L', 'MAIN_BRACKET_d1split_R',
          'MAIN_BRACKET_d1split_plug', 'PD_trigger_env_20V', 'PI5_board', 'SPKBOX_L_r2', 'SPK_driver_D40', 'V11a_mx', 'V11a_px', 'V11a_up', 'V11b_mx',
          'V11b_px', 'V11b_up', 'V11c_straight', 'VOICEPE_back_env', 'VOICEPE_encoder_env', 'VOICEPE_pcb', 'BME680_env_revD', 'TOUCH_pcb_100x44')
BACK = re.compile(r'(_v42|_[a-e]\d+[a-z0-9]*| \(\d+\))$')
PRE = ('REF_', 'TOOL_', 'INNER', 'RENDER_', 'AUD_')


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        L = X.cp(X.body('SPKBOX_L')); X.sec(L, X.wbox(40.0, 60.0, -20.0, 2.0, 24.0, 52.0))
        c = X.cp(X.body('TOUCH_CLIP_L'))
        sec = {}
        for x in (43.6, 44.5, 45.5, 45.9, 46.1, 46.5, 47.5, 48.5, 49.5, 50.3, 50.7, 51.5, 53.0):
            t = X.cp(L); X.sec(t, X.wbox(x - 0.05, x + 0.05, -20.0, 2.0, 24.0, 52.0))
            sec['box x%.1f' % x] = [[round(v * 10, 1), bb] for v, bb in X.lumps(t, 3000)]
        for y in (-13.0, -10.0, -8.0, -6.1, -4.0, -3.2):
            t = X.cp(L); X.sec(t, X.wbox(40.0, 60.0, y - 0.05, y + 0.05, 24.0, 52.0))
            sec['box y%.1f' % y] = [[round(v * 10, 1), bb] for v, bb in X.lumps(t, 3000)]
        for x in (40.6, 42.0, 43.4, 43.6, 44.9):
            t = X.cp(c); X.sec(t, X.wbox(x - 0.05, x + 0.05, -20.0, 5.0, 24.0, 52.0))
            sec['clip x%.1f' % x] = [[round(v * 10, 1), bb] for v, bb in X.lumps(t, 3000)]
        for y in (-8.0, -6.1, -4.0, -2.0, 0.0, 1.5):
            t = X.cp(c); X.sec(t, X.wbox(38.0, 48.0, y - 0.05, y + 0.05, 24.0, 52.0))
            sec['clip y%.1f' % y] = [[round(v * 10, 1), bb] for v, bb in X.lumps(t, 3000)]
        for z in (31.0, 34.0, 38.0, 42.0, 45.0):
            t = X.cp(c); X.sec(t, X.wbox(38.0, 48.0, -20.0, 5.0, z - 0.05, z + 0.05))
            sec['clip z%.1f' % z] = [[round(v * 10, 1), bb] for v, bb in X.lumps(t, 3000)]
        st['sec'] = sec; status('g2c2', st)
        # what else is near: zone round the clip screw and the lever side of it
        zones = {'beside the clip toward the back (x 38..46, y -14..-8.5, z 30..46)': X.wbox(38.0, 46.0, -14.0, -8.5, 30.0, 46.0),
                 'head side (x 30..40.5, y -12..0, z 32..44)': X.wbox(30.0, 40.5, -12.0, 0.0, 32.0, 44.0),
                 'block front (x 43.5..47.5, y -3.0..-2.0, z 30..46)': X.wbox(43.5, 47.5, -3.0, -2.0, 30.0, 46.0)}
        near = {}
        for zn, zb in zones.items():
            hits = {}
            for b in X.root.bRepBodies:
                n = b.name
                if n in LEGACY or BACK.search(n) or n.startswith(PRE):
                    continue
                if not zb.boundingBox.intersects(b.boundingBox):
                    continue
                v = X.clash(zb, b)
                if abs(v) > 0.01:
                    hits[n] = round(v, 1)
            near[zn] = hits
        st['near'] = near
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    st['t_end'] = round(time.time() - t0, 1)
    status('g2c2', st)


run(None)
