"""J6 with and without C7 (rev 2 board, top 89, cap on, cradle out): fingertip gap to the plug top by tip size."""
import numpy as np, sys
sys.path.insert(0, '.')
import access as A
from kpcb import parse, footprints
from scipy import ndimage
A.BODIES['cap'] = A.EXP + 'cap.stl'
fps_all = footprints(parse(open('/home/claude/ha-panel/hardware/main-board/main-board.kicad_pcb').read()))
base = [n for n in A.BODIES if n not in ('CRADLE_5807', 'PD_5807_env')]
occ0 = A.occupancy(base)
yc = A.Y0 + 0.5 + np.arange(A.NY)
for label, fps in (('as laid out', fps_all), ('without C7', [f for f in fps_all if f['ref'] != 'C7'])):
    occ = occ0.copy(); A.board(occ, 89, fps)
    edt = ndimage.distance_transform_edt(np.pad(~occ, 1, constant_values=True))[1:-1, 1:-1, 1:-1]
    seed = (int(0 - A.X0), int(60 - A.Z0), int(-97 - A.Y0))
    xa, xb, za, zb = A.targets(fps_all)['J6']
    row = []
    for d in (12, 14, 16, 18, 20):
        r = d / 2
        lab, n = ndimage.label(edt >= r, structure=np.ones((3, 3, 3)))
        reach = lab == lab[seed]
        sub = reach[int(np.ceil(xa - A.X0)):int(np.floor(xb - A.X0)) + 1, int(np.ceil(za - A.Z0)):int(np.floor(zb - A.Z0)) + 1, :]
        js = np.flatnonzero(sub.any(axis=(0, 1)) & (yc > -53.6))
        row.append('D%d %.1f' % (d, (yc[js].min() - r + 53.6) if len(js) else float('nan')))
    print('J6 %-12s gap to plug top: %s' % (label, '  '.join(row)))
