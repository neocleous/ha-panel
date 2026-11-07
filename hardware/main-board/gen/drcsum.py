"""python3 drcsum.py <board> : DRC summary (errors only) with unconnected pairs"""
import json, subprocess, sys, collections
b = sys.argv[1]
subprocess.run(['kicad-cli', 'pcb', 'drc', '--format', 'json', '--schematic-parity', '--severity-error', '-o', '/tmp/drc.json', b],
               capture_output=True)
d = json.load(open('/tmp/drc.json'))
v = d['violations']; u = d['unconnected_items']; p = d.get('schematic_parity', [])
print('viol', len(v), dict(collections.Counter(x['type'] for x in v)), 'unconn', len(u), 'parity', len(p))
for x in u:
    print('  U', ' | '.join('%s @(%.2f,%.2f)' % (it['description'][:44], it['pos']['x'], it['pos']['y']) for it in x['items']))
if '-v' in sys.argv:
    for x in v:
        print('  V', x['type'], x['description'][:70], ' | '.join('%s @(%.2f,%.2f)' % (it['description'][:40], it['pos']['x'], it['pos']['y']) for it in x['items']))
