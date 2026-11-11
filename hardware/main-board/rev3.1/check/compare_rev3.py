"""Rev 3.1 against rev 3, from the two board files: parts moved, tracks changed by net, vias, pours.
python3 compare_rev3.py <rev 3 board> <rev 3.1 board> [picture.png]"""
import collections, math, sys
import pcb
a = pcb.load(sys.argv[1]); c = pcb.load(sys.argv[2])
U0, V0 = 43.5, 28.95
print('parts: rev 3 %d, rev 3.1 %d' % (len(a['fps']), len(c['fps'])))
for r in sorted(a['fps'], key=lambda r: (r.rstrip('0123456789'), int(''.join(ch for ch in r if ch.isdigit()) or 0))):
    fa, fc = a['fps'][r], c['fps'][r]
    if abs(fa['x'] - fc['x']) > 1e-6 or abs(fa['y'] - fc['y']) > 1e-6 or abs(fa['rot'] - fc['rot']) > 1e-6:
        print('   %-5s u %+7.2f v %+7.2f rot %3.0f  ->  u %+7.2f v %+7.2f rot %3.0f   %s' % (r, fa['x'] - U0, V0 - fa['y'], fa['rot'] % 360, fc['x'] - U0, V0 - fc['y'], fc['rot'] % 360, fa['value']))
key = lambda s: (s['layer'], round(s['x1'], 3), round(s['y1'], 3), round(s['x2'], 3), round(s['y2'], 3), s['net'])
L = lambda s: math.hypot(s['x2'] - s['x1'], s['y2'] - s['y1'])
ka = {key(s): s for s in a['segs']}; kc = {key(s): s for s in c['segs']}
gone = collections.defaultdict(float); new = collections.defaultdict(float); wid = collections.defaultdict(set)
for k, s in ka.items():
    if k not in kc: gone[s['net'].split('/')[-1]] += L(s)
    elif abs(kc[k]['w'] - s['w']) > 1e-6: wid[s['net'].split('/')[-1]].add((s['w'], kc[k]['w']))
for k, s in kc.items():
    if k not in ka: new[s['net'].split('/')[-1]] += L(s)
print('tracks by net: taken out mm / new mm')
for n in sorted(set(gone) | set(new), key=lambda n: -(gone[n] + new[n])):
    if gone[n] + new[n] > 0.05: print('   %-14s %6.1f %6.1f' % (n, gone[n], new[n]))
tot = sum(L(s) for s in a['segs'])
print('   total: %.0f mm taken out, %.0f mm new, of %.0f mm on rev 3 (%.0f %% of rev 3 unchanged); rev 3.1 has %.0f mm' % (sum(gone.values()), sum(new.values()), tot, 100 * (1 - sum(gone.values()) / tot), sum(L(s) for s in c['segs'])))
print('same track, new width:', {n: sorted(v) for n, v in wid.items()})
va = {(round(v['x'], 3), round(v['y'], 3), v['net']) for v in a['vias']}; vc = {(round(v['x'], 3), round(v['y'], 3), v['net']) for v in c['vias']}
print('vias: rev 3 %d, rev 3.1 %d; ground vias %d -> %d; removed %d, added %d (of them ground %d)' % (len(va), len(vc), sum(1 for v in va if v[2] == 'GND'), sum(1 for v in vc if v[2] == 'GND'), len(va - vc), len(vc - va), sum(1 for v in vc - va if v[2] == 'GND')))
amp = sorted({s['net'] for s in a['segs'] + c['segs'] if s['net'].startswith('/Amplifier/')})
print('amplifier nets with a changed track:', [n.split('/')[-1] for n in amp if any(key(s) not in kc for s in a['segs'] if s['net'] == n) or any(key(s) not in ka for s in c['segs'] if s['net'] == n)] or 'none')
def area(pts):
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]))) / 2
for lay, name in (('F.Cu', 'door side'), ('B.Cu', 'back')):
    for b_, rev in ((a, 'rev 3'), (c, 'rev 3.1')):
        ar = sum(area(pts) for z in b_['zones'] if z['net'] == 'GND' for l, pts in z['fills'] if l == lay)
        print('ground pour, %s, %s: %.0f mm2 (%.0f %% of the board)' % (name, rev, ar, 100 * ar / (4 * U0 * V0)))
if len(sys.argv) > 3:
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon, Rectangle, Circle
    fig, axs = plt.subplots(1, 2, figsize=(22, 7.6), dpi=95)
    for ax, (lay, name) in zip(axs, (('F.Cu', 'door side'), ('B.Cu', 'back, seen through the board'))):
        ax.set_aspect('equal'); ax.set_xlim(-44.5, 44.5); ax.set_ylim(-30, 30)
        ax.add_patch(Rectangle((-U0, -V0), 2 * U0, 2 * V0, fc='#222', ec='black'))
        for z in c['zones']:
            for l, pts in z['fills']:
                if l == lay: ax.add_patch(Polygon([(x - U0, V0 - y) for x, y in pts], fc={'GND': '#7fbf7f'}.get(z['net'], '#ffb347'), ec='none'))
        for s in c['segs']:
            if s['layer'] == lay: ax.plot([s['x1'] - U0, s['x2'] - U0], [V0 - s['y1'], V0 - s['y2']], color='#d0342c' if lay == 'F.Cu' else '#4a90e2', lw=max(0.6, s['w'] * 6.0), solid_capstyle='round')
        for r, f in c['fps'].items():
            for p in f['pads']:
                if p['n'] and (lay in p['layers'] or '*.Cu' in p['layers']):
                    ax.add_patch(Rectangle((p['x'] - U0 - p['sx'] / 2, V0 - p['y'] - p['sy'] / 2), p['sx'], p['sy'], fc='#e2a52e', ec='none'))
        for v in c['vias']:
            ax.add_patch(Circle((v['x'] - U0, V0 - v['y']), v['size'] / 2, fc='yellow' if v['net'] == 'GND' else 'white', ec='none'))
        ax.set_title('rev 3.1, %s: ground pour green, supply areas orange, tracks %s, ground vias yellow, other vias white' % (name, 'red' if lay == 'F.Cu' else 'blue'), fontsize=9)
        ax.set_xlabel('u (mm)'); ax.set_ylabel('v (mm)')
    fig.tight_layout(); fig.savefig(sys.argv[3])
