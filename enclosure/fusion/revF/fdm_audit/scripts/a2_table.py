"""Print the in-plane thickness features of a part (classes below 2.0 by default)."""
import sys, json
from fdm_lib import *
name = sys.argv[1]; maxband = int(sys.argv[2]) if len(sys.argv) > 2 else 4; minvol = float(sys.argv[3]) if len(sys.argv) > 3 else 0.3
rows = json.load(open(os.path.join(DATA, 'plane_%s.json' % name)))
print(name, PARTS[name]['label'], '| id band wmin wtyp | h0-h1 (layers) vol | world x, y, z box')
for i, r in enumerate(rows):
    if r['band'] > maxband or r['vol'] < minvol: continue
    a, b = r['world_min'], r['world_max']
    print('%3d b%d %.2f %.2f | h %.1f-%.1f (%d) %.1f | x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f' % (
        i, r['band'], r['wmin'], r['wtyp'], r['h'][0], r['h'][1], r['nlayers'], r['vol'], a[0], b[0], a[1], b[1], a[2], b[2]))
