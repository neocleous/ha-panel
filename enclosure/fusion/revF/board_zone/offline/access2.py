import numpy as np, sys, json
sys.path.insert(0, '.')
import access as A
from kpcb import parse, footprints
A.BODIES['cap'] = A.EXP + 'cap.stl'
t = parse(open('/home/claude/ha-panel/hardware/main-board/main-board.kicad_pcb').read())
fps = footprints(t)
base = [n for n in A.BODIES if n not in ('CRADLE_5807', 'PD_5807_env', 'cap')]
occ_capon = A.occupancy(base + ['cap'])
occ_capon_cr = A.occupancy(base + ['cap', 'CRADLE_5807', 'PD_5807_env'])
for top in (84, 89):
    for r, rh in ((7, 15), (7, 20), (8, 20)):
        for label, occ in (('cap on, no cradle', occ_capon), ('cap on, cradle in', occ_capon_cr)):
            o = A.run(top, True, r, rh, fps, occ)
            print('top %d  finger r %d  hand r %d  %-18s' % (top, r, rh, label),
                  '  '.join('%s %s%s' % (k, 'yes' if v['reachable'] else 'NO', (' +%d' % v['finger_beyond_hand_mm']) if 'finger_beyond_hand_mm' in v else '') for k, v in sorted(o.items())))
