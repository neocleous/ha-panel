"""recheck3: in-layer thickness features of version 67 against the audit's of version 66. Usage: r3_cmp_plane.py <body> [maxband] [minvol] [mode all|changed]"""
import sys, json, os
from fdm_lib import *
OLD = '/home/claude/repo/enclosure/fusion/revF/fdm_audit/data'
name = sys.argv[1]; maxband = int(sys.argv[2]) if len(sys.argv) > 2 else 1; minvol = float(sys.argv[3]) if len(sys.argv) > 3 else 0.3
mode = sys.argv[4] if len(sys.argv) > 4 else 'changed'
new = json.load(open(os.path.join(DATA, 'plane_%s.json' % name))); old = json.load(open(os.path.join(OLD, 'plane_%s.json' % name)))
def ov(a, b, pad=0.6):
    return all(a['world_min'][i] - pad <= b['world_max'][i] and b['world_min'][i] - pad <= a['world_max'][i] for i in range(3))
def summ(rows):
    by = {}
    for r in rows: by.setdefault(r['band'], [0, 0.0]); by[r['band']][0] += 1; by[r['band']][1] += r['vol']
    return ' '.join('b%d:%d(%.0f)' % (k, v[0], v[1]) for k, v in sorted(by.items()))
print(name, '|', PARTS[name]['label'], '\n  v67:', summ(new), '\n  v66:', summ(old))
print('  id band wmin wtyp | h (layers) vol | world box | against v66')
ns = 0
for i, r in enumerate(new):
    if r['band'] > maxband or r['vol'] < minvol: continue
    mt = [o for o in old if o['band'] == r['band'] and ov(r, o)]
    same = [o for o in mt if abs(o['vol'] - r['vol']) <= max(0.3, 0.2 * r['vol']) and abs(o['wmin'] - r['wmin']) <= 0.05]
    if same and mode == 'changed': ns += 1; continue
    a, b = r['world_min'], r['world_max']
    tag = 'same' if same else (('MOVED ' + '; '.join('%.1f mm3 w %.2f' % (o['vol'], o['wmin']) for o in mt[:2])) if mt else 'NEW')
    print('%4d b%d %.2f %.2f | h %.1f-%.1f (%d) %.1f | x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f | %s' % (i, r['band'], r['wmin'], r['wtyp'], r['h'][0], r['h'][1], r['nlayers'], r['vol'], a[0], b[0], a[1], b[1], a[2], b[2], tag))
print('  unchanged:', ns)
for o in old:
    if o['band'] > maxband or o['vol'] < minvol: continue
    if not any(n['band'] == o['band'] and ov(o, n) for n in new):
        a, b = o['world_min'], o['world_max']
        print('  GONE b%d %.2f | (%d layers) %.1f mm3 | x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f' % (o['band'], o['wmin'], o['nlayers'], o['vol'], a[0], b[0], a[1], b[1], a[2], b[2]))
