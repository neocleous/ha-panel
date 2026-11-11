# rev F i wrap (2026-11-11): step 3 repeated - the h scripts that are run again unchanged on the model with main board rev 3.1.
#   STEP (from the loader) names the run; G holds the globals the h script reads (ONLY, SKIP, MODE, PAIRS, SHOTS, POSTS, VERSION ...).
#   Each run writes fp/step3r/<STEP>_status.json; the h scripts' own results in fp/step3 are not touched. The only changes to an h
#   script's text are the ones listed here: the status file's name and the backup suffix of this pass (_v50).
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_i_lib.py'), encoding='utf-8').read())
WRAP = {
    'i1c': ('v5f_h1c_distances.py', (("status3('h1c', st)", "status3('i1c', st)"),)),                 # board bodies to their neighbours
    'i1e': ('v5f_h1e_ride_in2.py', (("status3('h1e', st)", "status3('i1e', st)"),)),                 # ride-in on the display module
    'i1i': ('v5f_h1i_closest.py', (("status3('h1i', st)", "status3('i1i', st)"),)),                  # closest points of the tight pairs
    'i_renders': ('v5f_h1f_renders.py', ()),                                                         # pictures (PRE and SHOTS from the loader)
    'i2b': ('v5f_h2b_carrier.py', (("'_v48'", "'_v50'"), ("'RESP_CARRIER_v48'", "'RESP_CARRIER_v50'"),
                                   ("'h2b_apply' if APPLY else 'h2b'", "'i2b_apply' if APPLY else 'i2b'"))),   # carrier, POSTS from the loader
    'i2c': ('v5f_h2c_carrier_checks.py', (("'RESP_CARRIER_v48'", "'RESP_CARRIER_v50'"), ("status3('h2c', st)", "status3('i2c', st)"))),
    'i2e': ('v5f_h1e_ride_in2.py', (("('MAIN_pcb', 'MAIN_PS1', 'MAIN_PS1_tol', 'MAIN_conn', 'MAIN_tall', 'MAIN_low')", "('RESP_CARRIER',)"),
                                    ("status3('h1e', st)", "status3('i2e', st)"))),                # the carrier's ride-in (MODE 'C')
    'i3': ('v5f_h3e_reach.py', (("status3('h3e' + TAG, st)", "status3('i3' + TAG, st)"),)),          # reach, targets and plug blocks from the loader
    'i4b': ('v5f_h3b_leads.py', (("'_v49'", "'_v50'"), ("status3('h3b', st)", "status3('i4b', st)"))),   # leads from fp/step3r/h3_routes.json
    'i4c': ('v5f_h3c_lead_checks.py', (("status3('h3c', st)", "status3('i4c', st)"),)),
    'i4f': ('v5f_h3f_lead_pairs.py', (("status3('h3f', st)", "status3('i4f', st)"),)),
    'i_save': ('v5f_h_save_export.py', ()),
}
STEP = globals()['STEP']
G = globals().get('G', {})
run_h(WRAP[STEP][0], WRAP[STEP][1], G)
