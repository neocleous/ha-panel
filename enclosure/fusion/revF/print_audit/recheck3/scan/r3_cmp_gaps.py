"""recheck3: the gap scan of version 67 against the audit's scan of version 66 (repo data). Usage: r3_cmp_gaps.py <body> [amin]"""
import sys, json, os
from fdm_lib import *
OLD = '/home/claude/repo/enclosure/fusion/revF/fdm_audit/data'
name = sys.argv[1]; amin = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
new = json.load(open(os.path.join(DATA, 'gaps_%s.json' % name)))
try: old = json.load(open(os.path.join(OLD, 'gaps_%s.json' % name)))
except Exception: old = []
def ov(a, b, pad=0.6):
    return all(a['wmin'][i] - pad <= b['wmax'][i] and b['wmin'][i] - pad <= a['wmax'][i] for i in range(3))
print(name, '| v67 gaps %d (v66 %d) | area gap p10/med/p90 kind h | world box | v66 match' % (len(new), len(old)))
for r in new:
    if r['area'] < amin: continue
    mt = [o for o in old if ov(r, o)]
    kind = 'flat' if r['upc'] > 0.87 else ('upright' if r['upc'] < 0.35 else 'slope')
    even = (r['g90'] - r['gmin'] < 0.12 or r['g90'] < 0.2)
    print('%6.1f %.3f/%.3f/%.3f %-7s %s h %.1f-%.1f | x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f | %s' % (
        r['area'], r['gmin'], r['gmed'], r['g90'], kind, 'EVEN' if even else 'taper', r['h'][0], r['h'][1], r['wmin'][0], r['wmax'][0], r['wmin'][1], r['wmax'][1], r['wmin'][2], r['wmax'][2],
        ('v66: ' + '; '.join('%.1f mm2 med %.3f' % (o['area'], o['gmed']) for o in mt[:3])) if mt else 'NEW'))
gone = [o for o in old if o['area'] >= amin and not any(ov(o, r) for r in new)]
print('  v66 gaps of %.1f mm2 or more with no v67 gap at the place: %d' % (amin, len(gone)))
for o in gone:
    print('   gone: %6.1f med %.3f | x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f' % (o['area'], o['gmed'], o['wmin'][0], o['wmax'][0], o['wmin'][1], o['wmax'][1], o['wmin'][2], o['wmax'][2]))
