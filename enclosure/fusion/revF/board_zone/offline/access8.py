"""Rev 2.1 (C7 in the top strip) against rev 2: per fingertip diameter, the gap (mm) a fingertip ball travelling from
behind the open back gets to each plug's top face (y -53.6); cap on; step 10 (cradle out) and step 11 (cradle in, J1).
Then which opening it uses for rev 2.1: seal above the top edge / below the bottom edge / beside the side edges."""
import numpy as np, sys
sys.path.insert(0, '.')
import access as A
from kpcb import parse, footprints
from scipy import ndimage
A.BODIES['cap'] = A.EXP + 'cap.stl'
yc = A.Y0 + 0.5 + np.arange(A.NY)
def gaps(occ, d, tg):
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
boards = {'rev 2  ': 'rev2.kicad_pcb', 'rev 2.1': 'rev21.kicad_pcb'}
occs = {}
for cradle in (False, True):
    names = [n for n in A.BODIES if cradle or n not in ('CRADLE_5807', 'PD_5807_env')]
    occs[cradle] = A.occupancy(names)
for bl, bf in boards.items():
    fps = footprints(parse(open(bf).read())); tg = A.targets(fps)
    for cradle in (False, True):
        occ = occs[cradle].copy(); A.board(occ, 89, fps)
        for d in (14, 16, 20):
            print('%s %-10s D%d gap: %s' % (bl, 'cradle in' if cradle else 'cradle out', d, gaps(occ, d, tg)))
fps = footprints(parse(open('rev21.kicad_pcb').read())); tg = A.targets(fps)
occ0 = occs[False].copy(); A.board(occ0, 89, fps)
for label, seal in (('sealed above the top edge', (-75, 75, 89, 190)), ('sealed below the bottom edge', (-75, 75, -5, 34)), ('sealed beside both side edges', 'sides')):
    occ = occ0.copy()
    if seal == 'sides':
        A.add_box(occ, 45, 75, -5, 190, -66.5, -63.0); A.add_box(occ, -75, -45, -5, 190, -66.5, -63.0)
    else:
        A.add_box(occ, seal[0], seal[1], seal[2], seal[3], -66.5, -63.0)
    print('rev 2.1 cradle out %-30s D20 gap: %s' % (label, gaps(occ, 20, tg)))
