# Block 3, read-only: the door's ten magnet pockets (axes, ends, the flat over each) and its faces round the grommet's seats,
# for p34. Nothing in the document changes.
# Run: runpy.run_path(D + 'p34a_door_probe.py')['main']()  -> p34a_door_probe.txt, p34a_door_probe.json
import runpy, math

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def _main():
    k = L['load'](); X = k.K()
    b = X.body('HOUSING_F_door')
    print(L['stamp'](), 'door volume %.3f' % (b.volume * 1000.0))
    pk = [h for h in k.holes_of(b, 4.0, 4.3) if h['k'] == 'h']
    out = {'pockets': [], 'seat_faces': None}
    for h in sorted(pk, key=lambda q: (q['A'][0], q['A'][2])):
        A, B = h['A'], h['B']
        lo = [min(A[i], B[i]) - 6 for i in range(3)]; hi = [max(A[i], B[i]) + 6 for i in range(3)]
        fl = [f for f in k.faces(X, b, [lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]], kinds=('p',), amin=0.2)
              if f[1][2] < -0.99]
        az = h['a'][2]
        top = max(A[2], B[2]) + h['r'] * math.sqrt(max(0.0, 1 - az * az))
        row = dict(h, flats=fl, top=round(top, 3))
        out['pockets'].append(row)
        print('pocket r %.3f A %s B %s a %s L %.2f cov %.2f top %.3f' % (h['r'], A, B, h['a'], h['L'], h['cov'], top))
        for f in fl:
            print('   flat n %s at %s area %.1f ext %s' % (f[1], f[2], f[3], f[4]))
    sf = k.faces(X, b, [-14.5, 14.5, -84.5, -75.0, 2.7, 13.5], kinds=('p', 'c'), amin=0.05)
    out['seat_faces'] = sf
    print('faces round the seats: %d' % len(sf))
    for f in sf:
        print('  ', f)
    L['jdump']('p34a_door_probe.json', out)


def main():
    L['out']('p34a_door_probe.txt', _main)
