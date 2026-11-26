# Block 3: what the door and the base plate have where block 3 changes them. READ-ONLY.
# Run: runpy.run_path(D + 'p30_inspect.py')['main'](part)  part in ('holes', 'door', 'plate')  -> p30_<part>.json / .txt
import runpy
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
F = runpy.run_path(D + 'p20_faces.py')


def _holes():
    k = L['load'](); X = k.K()
    out = {}
    for n in ('HOUSING_F_door', 'FLOOR_PLATE', 'GROMMET_usbc_F'):
        rows = k.holes_of(X.body(n), rmin=0.5, rmax=8.0)
        out[n] = rows
        print(n, len(rows))
        for r in sorted(rows, key=lambda r: (r['r'], r['A'])):
            print('   %s r %.3f A %s B %s a %s L %.2f cov %.2f' % (r['k'], r['r'], r['A'], r['B'], r['a'], r['L'], r['cov']))
    L['jdump']('p30_holes.json', out)


def _door():
    # the four insert bosses (door's screws at (-19, -77), (19, -74.5), (+-50, -67)), one magnet pocket region, the new cut-out's box
    boxes = {'boss_m19': [-24, -14, -82, -72, 2.5, 12], 'boss_p19': [14, 24, -80, -69, 2.5, 12],
             'boss_p50': [45, 55, -72, -62, 2.5, 12], 'boss_m50': [-55, -45, -72, -62, 2.5, 12],
             'cut_box': [-13.5, 13.5, -86.5, -79.5, 11.5, 31.5], 'seats': [-12, 12, -83, -76, 2.5, 13]}
    for t, bx in boxes.items():
        F['dump']('door_' + t, 'HOUSING_F_door', bx, 0.02)


def _plate():
    boxes = {'rear_left': [5, 45, -84, -68, -0.5, 3.2], 'rear_right': [-45, -5, -84, -68, -0.5, 3.2]}
    for t, bx in boxes.items():
        F['dump']('plate_' + t, 'FLOOR_PLATE', bx, 0.02)


def main(part):
    f = {'holes': _holes, 'door': _door, 'plate': _plate}[part]
    L['out']('p30_%s.txt' % part, f)
