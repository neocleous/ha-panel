"""Hand-assembly rules on the board file (Daniel's standing decisions): every part on the door-side face, surface-mount
parts on one face only, connectors through-hole, nothing smaller than 0603.  python3 hand_assembly.py <board.kicad_pcb>"""
import re, sys
import pcb
b = pcb.load(sys.argv[1])
back = sorted(r for r, f in b['fps'].items() if f['layer'] != 'F.Cu')
tht = sorted((r for r, f in b['fps'].items() if any(p['type'] == 'thru_hole' and p['drill'] and p['drill'][0] > 0.35 for p in f['pads'] if p['n'])),   # 0.3 holes are the heat vias under the two chips
             key=lambda r: (r.rstrip('0123456789'), int(re.sub(r'\D', '', r) or 0)))
small = sorted(r for r, f in b['fps'].items() if re.search(r'_(0402|0201|01005)_', f['fp']))
sizes = sorted({m.group(1) for f in b['fps'].values() for m in [re.search(r'_(\d{4})_\d{4}Metric', f['fp'])] if m})
conn = sorted(r for r in b['fps'] if r.startswith('J'))
conn_smd = [r for r in conn if not any(p['type'] == 'thru_hole' for p in b['fps'][r]['pads'])]
smd_back = sorted({r for r, f in b['fps'].items() for p in f['pads'] if p['n'] and p['type'] == 'smd' and 'F.Cu' not in p['layers'] and 'B.Cu' in p['layers'] and r != 'U1'})
print('parts: %d; on the back face: %s' % (len(b['fps']), back or 'none'))
print('surface-mount pads on the back face: %s (U1 has a bare copper pad there for its heat, nothing is soldered to it)' % (smd_back or 'none'))
print('chip sizes used: %s; smaller than 0603: %s' % (', '.join(sizes), small or 'none'))
print('connectors: %s; not through-hole: %s' % (', '.join(conn), conn_smd or 'none'))
print('through-hole parts (%d): %s' % (len(tht), ', '.join(tht)))
