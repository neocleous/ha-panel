# rev F j wrap (2026-11-12): close of the enclosure work - earlier scripts run again unchanged on the model as it stands.
#   STEP (from the loader) names the run; G holds the globals the script reads. Each run writes into fp/close; the earlier results are
#   not touched. The only changes to a script's text are the ones listed here (the library, the status file's name, the data file).
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_j_lib.py'), encoding='utf-8').read())
WRAP = {
    'j6c': ('v5f_g2b_holes.py', (("os.path.join(FP, 'g2b_holes.json')", "os.path.join(S3, 'j6c_holes.json')"),
                                 ("status('g2b', st)", "status3('j6c', st)"))),              # every cylindrical hole in the printed parts
    'j6v': ('v5f_g3a_checks.py', (("status('g3a', st)", "status3('j6v_' + PART, st)"),)),     # PART 'vol' chambers, 'air' intake and deflector, 'sd' microSD finger
    'j_renders': ('v5f_h1f_renders.py', ()),                                                # pictures (PRE and SHOTS from the loader)
    'j_save': ('v5f_h_save_export.py', ()),                                                 # named version and archive
    'j_reach': ('v5f_h3e_reach.py', (("status3('h3e' + TAG, st)", "status3('j_reach' + TAG, st)"),)),
    'j_leads': ('v5f_h3c_lead_checks.py', (("status3('h3c', st)", "status3('j_leads', st)"),)),
}
STEP = globals()['STEP']
G = globals().get('G', {})
run_j(WRAP[STEP][0], WRAP[STEP][1], G)
