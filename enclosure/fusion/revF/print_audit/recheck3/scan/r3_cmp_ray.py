"""recheck3: the true-thickness features of version 67 against the audit's of version 66 (repo data).
Usage: r3_cmp_ray.py <body> [amin] [maxcls] [mode]   mode: all | changed (default: changed = no v66 feature of the same class at the place, or area/thickness moved)"""
import sys, json, os
from fdm_lib import *
OLD = '/home/claude/repo/enclosure/fusion/revF/fdm_audit/data'
name = sys.argv[1]; amin = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0; maxcls = int(sys.argv[3]) if len(sys.argv) > 3 else 2
mode = sys.argv[4] if len(sys.argv) > 4 else 'changed'
new = json.load(open(os.path.join(DATA, 'ray_%s.json' % name)))
old = json.load(open(os.path.join(OLD, 'ray_%s.json' % name)))
CL = ['<0.45', '.45-.85', '.85-1.3', '1.3-1.7', '1.7-2.0', '2.0-2.6']
def ov(a, b, pad=0.8):
    return all(a['wmin'][i] - pad <= b['wmax'][i] and b['wmin'][i] - pad <= a['wmax'][i] for i in range(3))
def kind(r): return 'wall' if r['upc'] < 0.35 else ('skin' if r['upc'] > 0.87 else 'slope')
print(name, '|', PARTS[name]['label'], '| v67 features %d, v66 %d' % (len(new), len(old)))
nsame = 0
for i, r in enumerate(new):
    if r['area'] < amin or r['cls'] > maxcls: continue
    mt = [o for o in old if o['cls'] == r['cls'] and ov(r, o)]
    same = [o for o in mt if abs(o['area'] - r['area']) <= max(1.0, 0.15 * r['area']) and abs(o['tmed'] - r['tmed']) <= 0.04]
    if same and mode == 'changed':
        nsame += 1; continue
    tag = 'same' if same else ('MOVED ' + '; '.join('%.1f mm2 %.2f/%.2f' % (o['area'], o['tmin'], o['tmed']) for o in mt[:2]) if mt else 'NEW')
    print('%3d %-7s %.2f/%.2f %7.1f %-5s h %.1f-%.1f | x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f | %s' % (
        i, CL[r['cls']], r['tmin'], r['tmed'], r['area'], kind(r), r['h'][0], r['h'][1], r['wmin'][0], r['wmax'][0], r['wmin'][1], r['wmax'][1], r['wmin'][2], r['wmax'][2], tag))
print('  unchanged against v66 (same class, place, area within 15 %%, median within 0.04): %d' % nsame)
gone = [o for o in old if o['area'] >= amin and o['cls'] <= maxcls and not any(n['cls'] == o['cls'] and ov(o, n) for n in new)]
for o in gone:
    print('  GONE %-7s %.2f/%.2f %7.1f %-5s | x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f' % (CL[o['cls']], o['tmin'], o['tmed'], o['area'], kind(o), o['wmin'][0], o['wmax'][0], o['wmin'][1], o['wmax'][1], o['wmin'][2], o['wmax'][2]))
