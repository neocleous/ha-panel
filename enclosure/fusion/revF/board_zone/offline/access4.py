"""Per fingertip ball diameter: how close (mm) the ball, travelling from behind the open back (cap on, cradle out), gets to
the top face of each plug (y -53.6) within the plug's footprint. Board top edge 84 (old) and 89 (rev 2)."""
import numpy as np, sys
sys.path.insert(0, '.')
import access as A
from kpcb import parse, footprints
from scipy import ndimage
A.BODIES['cap'] = A.EXP + 'cap.stl'
fps = footprints(parse(open('/home/claude/ha-panel/hardware/main-board/main-board.kicad_pcb').read()))
base = [n for n in A.BODIES if n not in ('CRADLE_5807', 'PD_5807_env')]
occ0 = A.occupancy(base)
tg = A.targets(fps)
yc = A.Y0 + 0.5 + np.arange(A.NY)                        # voxel centre y
for top in (84, 89):
    occ = occ0.copy(); A.board(occ, top, fps)
    edt = ndimage.distance_transform_edt(np.pad(~occ, 1, constant_values=True))[1:-1, 1:-1, 1:-1]
    seed = (int(0 - A.X0), int(60 - A.Z0), int(-97 - A.Y0))
    print('top', top)
    for d in (12, 14, 16, 18, 20):
        r = d / 2
        lab, n = ndimage.label(edt >= r, structure=np.ones((3, 3, 3)))
        reach = lab == lab[seed]
        row = []
        for k, (xa, xb, za, zb) in sorted(tg.items()):
            sub = reach[int(np.ceil(xa - A.X0)):int(np.floor(xb - A.X0)) + 1, int(np.ceil(za - A.Z0)):int(np.floor(zb - A.Z0)) + 1, :]
            js = np.flatnonzero(sub.any(axis=(0, 1)) & (yc > -53.6))
            gap = (yc[js].min() - r + 53.6) if len(js) else float('nan')
            row.append('%s %5.1f' % (k, gap))
        print('   fingertip D %2d: gap to plug top  %s' % (d, '  '.join(row)))
