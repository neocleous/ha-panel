"""Sensitivity: larger fingertips (D24, D28) and the hand-ball finger length (hand D40, finger D14/D16), rev 2 vs rev 2.1,
cap on, cradle out (J1: cradle in)."""
import numpy as np, sys
sys.path.insert(0, '.')
import access as A
from access8 import gaps, occs
from kpcb import parse, footprints
for bl, bf in (('rev 2  ', 'rev2.kicad_pcb'), ('rev 2.1', 'rev21.kicad_pcb')):
    fps = footprints(parse(open(bf).read())); tg = A.targets(fps)
    occ = occs[False].copy(); A.board(occ, 89, fps)
    for d in (24, 28):
        print('%s cradle out D%d gap: %s' % (bl, d, gaps(occ, d, tg)))
    for r in (7, 8):
        o = A.run(89, False, r, 20, fps, occs[False])
        o1 = A.run(89, True, r, 20, fps, occs[True])
        print('%s finger D%d, hand D40: %s | J1 cradle in: %s' % (bl, 2 * r, '  '.join('%s %s' % (k, ('+%d' % v['finger_beyond_hand_mm']) if 'finger_beyond_hand_mm' in v else ('no' if not v['reachable'] else '?')) for k, v in sorted(o.items())),
              ('+%d' % o1['J1']['finger_beyond_hand_mm']) if 'finger_beyond_hand_mm' in o1['J1'] else 'no'))
