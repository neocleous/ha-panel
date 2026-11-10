# rev F g4c (2026-11-10): step 1, block 4 - read-only: interference of the five bodies block 4 changes (plate, inlet cradle, both speaker
# boxes, front shell) against every current body, mm3. Run before the change (TAG 'before') and after (TAG 'after'); the report is the
# difference. PART 'small' = plate, cradle, boxes against all; PART 'shell' = the shell against all (the shell is never copied per pair:
# the other body is the boolean's target). Bodies left out: backups (_v42, _v45, _<letter><digits>), legacy, REF_/TOOL_/INNER/RENDER_/AUD_.
import os, re
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
LEGACY = ('DOOR_tray', 'HOUSING_E', 'HOUSING_shell', 'HOUSING_F_wip', 'AMP_env_20x20x10', 'BUCK_20to5V_env_43x25x13', 'DOOR_plate_revE', 'GROMMET_usbc',
          'HOUSING_F_front_d10_sliver', 'HOUSING_F_front_d12a_sliver1', 'LD2410C_env', 'MAIN_BRACKET_d1split_L', 'MAIN_BRACKET_d1split_R',
          'MAIN_BRACKET_d1split_plug', 'PD_trigger_env_20V', 'PI5_board', 'SPKBOX_L_r2', 'SPK_driver_D40', 'V11a_mx', 'V11a_px', 'V11a_up', 'V11b_mx',
          'V11b_px', 'V11b_up', 'V11c_straight', 'VOICEPE_back_env', 'VOICEPE_encoder_env', 'VOICEPE_pcb', 'BME680_env_revD', 'TOUCH_pcb_100x44')
BACK = re.compile(r'(_v42|_v45|_[a-e]\d+[a-z0-9]*| \(\d+\))$')
PRE = ('REF_', 'TOOL_', 'INNER', 'RENDER_', 'AUD_')
TAG = globals().get('TAG', 'before'); PART = globals().get('PART', 'small')
SMALL = ['FLOOR_PLATE', 'CRADLE_5807', 'SPKBOX_L', 'SPKBOX_R']
SHELL = 'HOUSING_F_front'


def run(_context):
    st = {'tag': TAG, 'part': PART}
    t0 = time.time()
    name = 'g4c_%s_%s' % (TAG, PART)
    try:
        X = K()
        cur = [b for b in X.root.bRepBodies if not (b.name in LEGACY or BACK.search(b.name) or b.name.startswith(PRE))]
        st['n_current'] = len(cur)
        st['vol'] = {n: round(X.vol(X.body(n)), 1) for n in SMALL + [SHELL]}
        st['lumps'] = {n: X.body(n).lumps.count for n in SMALL + [SHELL]}
        pairs = {}
        if PART == 'small':
            for cn in SMALL:
                C = X.cp(X.body(cn))
                for b in cur:
                    if b.name == cn or b.name == SHELL or (b.name in SMALL and SMALL.index(b.name) < SMALL.index(cn)):
                        continue
                    if not C.boundingBox.intersects(b.boundingBox):
                        continue
                    t = X.cp(b)
                    try:
                        X.tbm.booleanOperation(t, C, BT.IntersectionBooleanType); v = X.vol(t)
                    except Exception:
                        v = -1.0
                    if abs(v) > 0.005:
                        pairs['%s|%s' % (cn, b.name)] = round(v, 2)
                st['pairs'] = pairs; st['t'] = round(time.time() - t0, 1); status(name, st)
        else:
            S = X.cp(X.body(SHELL))
            st['t_copy'] = round(time.time() - t0, 1)
            n = 0
            for b in cur:
                if b.name == SHELL:
                    continue
                if not S.boundingBox.intersects(b.boundingBox):
                    continue
                t = X.cp(b)
                try:
                    X.tbm.booleanOperation(t, S, BT.IntersectionBooleanType); v = X.vol(t)
                except Exception:
                    v = -1.0
                n += 1
                if abs(v) > 0.005:
                    pairs['%s|%s' % (SHELL, b.name)] = round(v, 2)
                if n % 10 == 0:
                    st['pairs'] = pairs; st['done'] = n; st['t'] = round(time.time() - t0, 1); status(name, st)
            st['pairs'] = pairs; st['done'] = n
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    st['t_end'] = round(time.time() - t0, 1)
    status(name, st)


run(None)
