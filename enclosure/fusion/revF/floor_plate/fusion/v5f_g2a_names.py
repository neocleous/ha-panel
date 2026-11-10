# rev F g2a (2026-11-10): step 1, block 2 - read-only: document state and the names of the current bodies (no backups, no legacy).
import os, re
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
LEGACY = ('DOOR_tray', 'HOUSING_E', 'HOUSING_shell', 'HOUSING_F_wip', 'AMP_env_20x20x10', 'BUCK_20to5V_env_43x25x13', 'DOOR_plate_revE', 'GROMMET_usbc',
          'HOUSING_F_front_d10_sliver', 'HOUSING_F_front_d12a_sliver1', 'LD2410C_env', 'MAIN_BRACKET_d1split_L', 'MAIN_BRACKET_d1split_R',
          'MAIN_BRACKET_d1split_plug', 'PD_trigger_env_20V', 'PI5_board', 'SPKBOX_L_r2', 'SPK_driver_D40', 'V11a_mx', 'V11a_px', 'V11a_up', 'V11b_mx',
          'V11b_px', 'V11b_up', 'V11c_straight', 'VOICEPE_back_env', 'VOICEPE_encoder_env', 'VOICEPE_pcb', 'BME680_env_revD', 'TOUCH_pcb_100x44')
BACK = re.compile(r'(_v42|_[a-e]\d+[a-z0-9]*| \(\d+\))$')
PRE = ('REF_', 'TOOL_', 'INNER', 'RENDER_', 'LEAD_')


def run(_context):
    st = {}
    try:
        X = K()
        st['doc'] = X.doc.name; st['active'] = X.app.activeDocument.name
        try:
            st['version'] = X.doc.dataFile.versionNumber
        except Exception:
            st['version'] = None
        st['modified'] = X.doc.isModified
        ns = X.names()
        st['n'] = len(ns)
        st['AUD'] = [n for n in ns if n.startswith('AUD_')]
        cur = []; pre = {}
        for b in X.root.bRepBodies:
            n = b.name
            if n in LEGACY or BACK.search(n) or n.startswith('AUD_'):
                continue
            if n.startswith(PRE):
                k = [p for p in PRE if n.startswith(p)][0]
                pre.setdefault(k, []).append(n + ('' if b.isLightBulbOn else '*'))
                continue
            cur.append(n + ('' if b.isLightBulbOn else '*'))
        st['current'] = sorted(cur)
        st['pre'] = {k: sorted(v) for k, v in pre.items() if k != 'LEAD_'}
        st['n_lead'] = len(pre.get('LEAD_', []))
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    status('g2a', st)


run(None)
