"""Main board floorplan, single-sided SMD (Daniel 2026-11-07 22:48: no SMD on the back) on the T outline from the design
chat (claude/report-main-board-outline-2026-11-07.md), tab top lowered to z 116. Frame as MAIN_env: x = 45 - x_rel,
y = 84 - z (y < 0 above the old top edge). Front: every SMD part + the THT parts; back: J2 USB4085, LK1, bare test pads.
Run: python3 plan_main1s.py <netlist> <out.kicad_pcb>"""
import math
import os
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcb_main as pm
import plan_main as p2

MM = pm.MM
OUTLINE = [(0, 50), (0, -5), (25.5, -5), (25.5, -32), (64.5, -32), (64.5, -5), (88, -5), (90, -4.5), (90, 50)]   # T, tab top z 116
BASE = [(0, 50), (0, -5), (88, -5), (90, -4.5), (90, 50)]   # final: the layout left the tab empty, so it was cut off
EDGE = 0.45                     # courtyard to board edge
GAP = 0.3                       # courtyard to courtyard
FRONT = dict(p2.FRONT)
FRONT['F5'] = (45.6, 30.45, 0)   # PVDD PTC on the front: pad 1 (+20V) in the +20V plane, pad 2 (PVDD) in the PVDD plane
FIXED_BACK = {'J2': p2.FIXED_BACK['J2'], 'LK1': p2.FIXED_BACK['LK1']}
ANCHOR = dict(p2.ANCHOR)
EF_FIRST = ['F1', 'C1', 'C2', 'C4', 'D1', 'R1', 'R2', 'R3', 'C3', 'R4', 'R5', 'R6']   # inlet path first: F1 next to J1
ORDER = EF_FIRST + [r for r in p2.ORDER if r not in EF_FIRST]
TPS = list(p2.TPS)
FRONT_KEEPOUT = [
    (52.3, 22.8, 67.7, 28.2),                                  # TAS land / via field
    (53.6, 19.3, 63.5, 21.0), (53.6, 30.0, 63.5, 31.7),        # TAS fan-out via rows (front copper)
    (64.4, 17.3, 81.0, 19.4),                                  # OUT_AP pre-route: C104 -> under L101 -> L100
    (64.4, 31.6, 70.0, 33.6), (69.0, 26.0, 80.5, 33.6),        # OUT_BP pre-route: C115 -> under L102 -> L103
] + [(x - 4.1, y - 4.1, x + 4.1, y + 4.1) for x, y in pm.HOLES]   # bracket bosses Ø8 touch the front
BACK_KEEPOUT = [(25.5, -32, 64.5, -26),                       # tab above z 110: bare board only (door 1.1-3.4 behind)
                (0, -5, 1.5, 2.0), (83.0, -5, 90, 2.0),        # top corners: bare board only
                (52.3, 22.8, 67.7, 28.2),                          # TAS land / via field
                (53.2, 17.6, 63.8, 21.2), (53.2, 29.8, 63.8, 33.4)] + \
               [(x - 3.4, y - 3.4, x + 3.4, y + 3.4) for x, y in pm.HOLES]   # screw heads


def inside(poly, x, y):
    n, c = len(poly), False
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def rect_in_outline(r, m=EDGE):
    x0, y0, x1, y1 = r[0] - m, r[1] - m, r[2] + m, r[3] + m
    if not all(inside(OUTLINE, x, y) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))):
        return False
    return not any(x0 < vx < x1 and y0 < vy < y1 for vx, vy in OUTLINE)     # concave corners of the T


def obstacles(board, side):
    lay = pcbnew.F_CrtYd if side == 'F' else pcbnew.B_CrtYd
    cu = pcbnew.F_Cu if side == 'F' else pcbnew.B_Cu
    obs = list(FRONT_KEEPOUT if side == 'F' else BACK_KEEPOUT)
    for fp in board.GetFootprints():
        if fp.GetReference().startswith('H'):
            continue
        if fp.GetLayer() == cu:
            obs.append(p2.rect_of(fp, lay))
        else:                                                  # THT pads of the other side block this side too
            for p in fp.Pads():
                if p.HasHole():
                    bb = p.GetBoundingBox()
                    obs.append((pcbnew.ToMM(bb.GetX()) - 0.3, pcbnew.ToMM(bb.GetY()) - 0.3,
                                pcbnew.ToMM(bb.GetRight()) + 0.3, pcbnew.ToMM(bb.GetBottom()) + 0.3))
    return obs


def place(board, ref, target, obs, side, rots=(0, 90, 180, 270), rmax=30.0, step=0.25):
    fp = board.FindFootprintByReference(ref)
    lay = pcbnew.F_CrtYd if side == 'F' else pcbnew.B_CrtYd
    if side == 'B' and fp.GetLayer() == pcbnew.F_Cu:
        fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    tx, ty = target
    r = 0.0
    while r <= rmax:
        n = max(1, int(2 * math.pi * r / step))
        for k in range(n):
            a = 2 * math.pi * k / n
            x, y = tx + r * math.cos(a), ty + r * math.sin(a)
            for rot in rots:
                fp.SetOrientationDegrees(rot)
                bb = p2.rect_of(fp, lay)
                cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
                fp.Move(pcbnew.VECTOR2I(MM(x - cx), MM(y - cy)))
                bb = p2.rect_of(fp, lay)
                if not rect_in_outline(bb):
                    continue
                if any(p2.overlap(bb, o, GAP) for o in obs):
                    continue
                obs.append(bb)
                return (round(x, 2), round(y, 2), rot, round(r, 2))
        r += step
    raise RuntimeError('no spot for ' + ref)


def anchor_xy(board, a):
    if isinstance(a[0], (int, float)):
        return a
    afp = board.FindFootprintByReference(a[0])
    pad = [p for p in afp.Pads() if p.GetNumber() == a[1]][0]
    return (pcbnew.ToMM(pad.GetPosition().x), pcbnew.ToMM(pad.GetPosition().y))


def main(netlist, out):
    plan = {r: (v[0], v[1], v[2], 'F') for r, v in FRONT.items()}
    plan.update({r: (v[0], v[1], v[2], 'B') for r, v in FIXED_BACK.items()})
    board, placed, missing = pm.build(netlist, out, plan, layers=4, poly=OUTLINE)
    where = {}
    obs_f = obstacles(board, 'F')
    for ref in ORDER:
        where[ref] = place(board, ref, anchor_xy(board, ANCHOR[ref]), obs_f, 'F')
    obs_b = obstacles(board, 'B')
    for ref in TPS:
        where[ref] = place(board, ref, anchor_xy(board, ANCHOR[ref]), obs_b, 'B', rots=(0,))
    left = [r for r in missing if r not in where]
    pcbnew.SaveBoard(out, board)
    far = sorted(((v[3], k) for k, v in where.items()), reverse=True)[:12]
    print('placed', len(where), 'unplaced', left, 'farthest from anchor', far)
    return board, where, left


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
