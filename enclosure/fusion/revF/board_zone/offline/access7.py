"""Which opening each fingertip uses (rev 2, top 89, cap on): seal the board plane above the top edge, below the bottom
edge, or beside the side edges, one at a time; Ø20 and Ø14 fingertips; cradle out (step 10) and in (step 11, J1)."""
import numpy as np, sys
sys.path.insert(0, '.')
import access as A
from kpcb import parse, footprints
from scipy import ndimage
A.BODIES['cap'] = A.EXP + 'cap.stl'
fps = footprints(parse(open('/home/claude/ha-panel/hardware/main-board/main-board.kicad_pcb').read()))
yc = A.Y0 + 0.5 + np.arange(A.NY)
tg = A.targets(fps)
def gaps(occ, d):
    r = d / 2
    edt = ndimage.distance_transform_edt(np.pad(~occ, 1, constant_values=True))[1:-1, 1:-1, 1:-1]
    lab, n = ndimage.label(edt >= r, structure=np.ones((3, 3, 3)))
    reach = lab == lab[(int(0 - A.X0), int(60 - A.Z0), int(-97 - A.Y0))]
    out = []
    for k, (xa, xb, za, zb) in sorted(tg.items()):
        sub = reach[int(np.ceil(xa - A.X0)):int(np.floor(xb - A.X0)) + 1, int(np.ceil(za - A.Z0)):int(np.floor(zb - A.Z0)) + 1, :]
        js = np.flatnonzero(sub.any(axis=(0, 1)) & (yc > -53.6))
        out.append('%s %4.1f' % (k, (yc[js].min() - r + 53.6) if len(js) else float('nan')))
    return '  '.join(out)
for cradle in (False, True):
    names = [n for n in A.BODIES if cradle or n not in ('CRADLE_5807', 'PD_5807_env')]
    occ0 = A.occupancy(names); A.board(occ0, 89, fps)
    for label, seal in (('all open', None), ('sealed above the top edge', (-75, 75, 89, 190)), ('sealed below the bottom edge', (-75, 75, -5, 34)),
                        ('sealed beside both side edges', 'sides')):
        occ = occ0.copy()
        if seal == 'sides':
            A.add_box(occ, 45, 75, -5, 190, -66.5, -63.0); A.add_box(occ, -75, -45, -5, 190, -66.5, -63.0)
        elif seal is not None:
            A.add_box(occ, seal[0], seal[1], seal[2], seal[3], -66.5, -63.0)
        for d in (14, 20):
            print('%-13s %-30s D%d gap: %s' % ('cradle in' if cradle else 'cradle out', label, d, gaps(occ, d)))
