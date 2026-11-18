"""Print the ray-thickness features of a part."""
import sys, json
from fdm_lib import *
name = sys.argv[1]; amin = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0; maxcls = int(sys.argv[3]) if len(sys.argv) > 3 else 5
rows = json.load(open(os.path.join(DATA, 'ray_%s.json' % name)))
print(name, '|', PARTS[name]['label'], '| id class tmin/tmed area(mm2) kind | h | world box')
CL = ['<0.45', '.45-.85', '.85-1.3', '1.3-1.7', '1.7-2.0', '2.0-2.6']
for i, r in enumerate(rows):
    if r['area'] < amin or r['cls'] > maxcls: continue
    kind = 'wall' if r['upc'] < 0.35 else ('skin' if r['upc'] > 0.87 else 'slope')
    print('%3d %-7s %.2f/%.2f %6.1f %-5s h %.1f-%.1f | x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f' % (
        i, CL[r['cls']], r['tmin'], r['tmed'], r['area'], kind, r['h'][0], r['h'][1],
        r['wmin'][0], r['wmax'][0], r['wmin'][1], r['wmax'][1], r['wmin'][2], r['wmax'][2]))
