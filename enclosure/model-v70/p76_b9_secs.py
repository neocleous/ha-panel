# Block 9: section outlines of every body of the unit (leads included) for laying out the holder and the radar's lead.
# READ-ONLY. Run: runpy.run_path(D + 'p76_b9_secs.py')['main'](tag, origin, normal, uax, box)  -> p65_<tag>.json via p65_section
import runpy
D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
P = runpy.run_path(D + 'p65_section.py')


def main(tag, origin, normal, uax, box, extra=()):
    k = L['load'](); X = k.K()
    names = [b.name for b in k.current(X, leads=True)] + list(extra)
    P['main'](tag, origin, normal, uax, names, box)
