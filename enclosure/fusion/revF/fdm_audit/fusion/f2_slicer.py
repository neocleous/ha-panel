# Design-for-FDM audit of version 66 -- audit slices. READ-ONLY on the design: it never touches the Fusion document.
# Starts or polls Bambu Studio's command-line slicer through the print re-check's own runner (r2bs.py), with this audit's folder.
# Set MODE and JOBS before running. Never sleep in this script: it runs on Fusion's main thread and the bridge drops the call.
import os
MODE = 'poll'                                   # 'start' or 'poll'
JOBS = ['F_shell', 'F_door', 'F_base', 'F_boxL', 'F_boxR', 'F_cap', 'F_carrier', 'F_plate', 'F_bezel', 'F_grommet', 'F_cradle', 'F_hood', 'F_clipL']

def run(_context: str):
    src = open(os.path.expanduser('~/Documents/HA_panel_renders/print_audit_recheck2/lib/r2bs.py')).read()
    g = {'R2_DIR': os.path.expanduser('~/Documents/HA_panel_renders/fdm_audit'), 'R2_MODE': MODE,
         'R2_JOBS': JOBS if MODE == 'start' else [], 'R2_ONLY': ','.join(JOBS)}
    exec(compile(src, 'r2bs.py', 'exec'), g)
    g['run'](None)
