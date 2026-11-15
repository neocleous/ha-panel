import sys, json
sys.path.insert(0, '/home/claude/bal')
import geo, shapely
C = {k: shapely.from_geojson(v) for k, v in json.load(open('/home/claude/bal/cand.json')).items()}
def piece(p, t, z0, rho=7.85):
    return (p.area * t * rho / 1000.0, (p.centroid.x, p.centroid.y, z0 + t / 2.0))
rear = piece(C['rear'], 10.0, 2.5)
left = piece(C['left'], 2.5, 0.9)
right = piece(C['right'], 2.5, 0.9)
O = {'A  none': [], 'B  under the boxes': [left, right], 'C  behind the Pi': [rear], 'D  both': [left, right, rear]}
rows = [('back top horizontal centres', 'Backward, glass top edge, horizontal (rear feet centres)', 'N'),
        ('back top horizontal edges', '  same, about the rear feet\'s back edges', 'N'),
        ('back top normal centres', 'Backward, glass top edge, square to the glass', 'N'),
        ('back top normal edges', '  same, about the back edges', 'N'),
        ('back centre normal centres', 'Backward, screen centre, square to the glass', 'N'),
        ('back centre normal edges', '  same, about the back edges', 'N'),
        ('fwd tips at deg centres', 'Forward, tips at (front feet centres)', 'deg'),
        ('fwd tips at deg edges', '  same, about the front edges', 'deg'),
        ('fwd pull top centres', 'Forward, pull at the glass top edge', 'N'),
        ('fwd pull top edges', '  same, about the front edges', 'N'),
        ('fwd lift door foot centres', 'Forward, lift at the door foot (y -84)', 'N'),
        ('fwd lift door foot edges', '  same, about the front edges', 'N'),
        ('rear share %', 'Rear feet\'s share of the weight', '%')]
F = {}
for n, parts in O.items():
    m, cog = geo.add(parts)
    F[n] = (m, cog, geo.figs(m, cog), sum(p[0] for p in parts))
print('%-60s' % 'case' + ''.join('%22s' % n for n in O))
print('%-60s' % 'added, g' + ''.join('%22.1f' % F[n][3] for n in O))
print('%-60s' % 'unit, g' + ''.join('%22.0f' % F[n][0] for n in O))
for k, lab, u in rows:
    base = F['A  none'][2][k]
    print('%-60s' % (lab + ' [' + u + ']') + ''.join('%15.2f (%+5.1f%%)' % (F[n][2][k], 100 * (F[n][2][k] / base - 1)) for n in O))
for n in O:
    print(n, 'cog', [round(c, 2) for c in F[n][1]])
for nm, (g, c) in (('rear', rear), ('left', left), ('right', right)):
    print('%s %.1f g at (%.1f, %.1f, %.2f)' % (nm, g, *c))
json.dump({n: {'added': F[n][3], 'mass': F[n][0], 'cog': F[n][1], 'figs': F[n][2]} for n in O}, open('/home/claude/bal/opt_figs.json', 'w'), indent=1)
