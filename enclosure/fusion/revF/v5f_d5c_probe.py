# rev F audit-response d5c (2026-11-06), read-only: sections for the shelf land, exhaust bridge posts, vents and the lip end
#   (audit findings 4, 6, 10, 35). Writes ~/Documents/HA_panel_renders/d_data/data/d5c_sections.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/HA_panel_renders/scripts_d/v5f_d0_sections.py')).read())   # sections()
import traceback
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d5c_sections.json')
F, D, CAP = 'HOUSING_F_front', 'HOUSING_F_door', 'HOUSING_F_cap'
FLOOR = [F, 'PI5_F', 'PI5_F_cooler', 'SPKBOX_L', 'SPKBOX_R', 'MAIN_BRACKET', 'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR', 'CRADLE_5807',
         'LEAD_PI_POWER', 'PIPWR_a_env', 'USBA_plug_env', 'USBA_cable_env', D]
PL = {
    'SH_x0': ('x', 0.0, (-24.5, -21.0, 175.0, 178.6), [F, CAP]),
    'SH_x40': ('x', 40.0, (-24.5, -21.0, 175.0, 178.6), [F, CAP]),
    'SH_x-58': ('x', -58.0, (-24.5, -21.0, 175.0, 178.6), [F, CAP]),
    'EX_x0': ('x', 0.0, (-64.0, -36.0, 150.0, 182.0), [F, CAP, D]),
    'EX_x10': ('x', 10.0, (-64.0, -36.0, 150.0, 182.0), [F, CAP, D]),
    'EX_z164': ('z', 164.0, (-56.0, 56.0, -64.0, -36.0), [F, D]),
    'EX_z168.5': ('z', 168.5, (-56.0, 56.0, -64.0, -36.0), [F, D]),
    'FL_z1.0': ('z', 1.0, (-95.0, 95.0, -90.0, 12.0), [F, D]),
    'FL_z5.0': ('z', 5.0, (-95.0, 95.0, -90.0, 12.0), FLOOR),
    'FL_z12': ('z', 12.0, (-95.0, 95.0, -90.0, 12.0), FLOOR),
    'DR_x0': ('x', 0.0, (-92.0, -40.0, 0.0, 182.0), [F, D, CAP, 'MAIN_pcb', 'MAIN_back_env', 'MAIN_BRACKET']),
    'DR_x40': ('x', 40.0, (-92.0, -40.0, 0.0, 182.0), [F, D, CAP, 'MAIN_pcb', 'MAIN_back_env', 'MAIN_BRACKET']),
    'DR_z120': ('z', 120.0, (-95.0, 95.0, -92.0, -30.0), [F, D, 'MAIN_back_env', 'MAIN_BRACKET', 'LD2410C_env_F', 'BME680_env']),
    'DR_z60': ('z', 60.0, (-95.0, 95.0, -92.0, -30.0), [F, D, 'MAIN_back_env', 'MAIN_pcb', 'MAIN_BRACKET', 'SPKBOX_L', 'SPKBOX_R']),
    'LP_y-63.45': ('y', -63.45, (-90.0, 90.0, 0.0, 175.0), [F, D]),
    'LP_y-60': ('y', -60.0, (-90.0, 90.0, 0.0, 175.0), [F, D]),
}


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        sec = sections(X, PL)
        sec['t_s'] = round(time.time() - t0, 1)
        os.makedirs(os.path.dirname(OUTF), exist_ok=True)
        json.dump(sec, open(OUTF, 'w'))
        out['t_s'] = sec['t_s']
        out['planes'] = {k: sorted(v['loops'].keys()) for k, v in sec.items() if isinstance(v, dict) and 'loops' in v}
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d5c_probe', 'sections', {'t_s': out.get('t_s'), 'FAIL': out.get('FAIL')})
    print(json.dumps({'t_s': out.get('t_s'), 'FAIL': out.get('FAIL')}))
