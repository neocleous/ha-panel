"""Main board floorplan (decision 6.1: two-sided, 4-layer). Board frame: KiCad top = Pi side (front),
x = 45 - x_rel, y = 84 - z. Front: big parts, ICs with thermal pads, magnetics, electrolytics, connectors.
Back: iron-solderable SMD (auto-placed next to the pad they serve), J2 USB4085 (THT), LK1, bare test pads.
Run: python3 plan_main.py <netlist> <out.kicad_pcb>"""
import math
import os
import sys
import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcb_main as pm

MM = pm.MM

# ---- front (courtyard centre x, y, rotation, side) ----
FRONT = {
    'H1': (3.5, 3.5, 0), 'H2': (86.5, 3.5, 0), 'H3': (3.5, 46.5, 0), 'H4': (86.5, 46.5, 0),
    'PS1': (35.4, 7.0, 180),            # body x 10.0-60.8, y 1.0-13.0; pin 1 (+Vo) at x 59.56, pin row y 9.0
    'J10': (64.7, 6.5, 0),              # sensor landing 2 x 4
    'J5': (75.7, 4.0, 0),               # radar XH, landing x_rel -30.7, z 80 (decision 2)
    'F5': (74.0, 10.5, 0),              # PVDD PTC
    'C6': (15.5, 19.0, 0),              # NID input C (EMC C2), under +Vin pins 9/10
    'L1': (27.6, 20.3, 0),              # EMC L1
    'C5': (27.8, 32.5, 0),              # EMC C1 (+20V)
    'U1': (37.0, 38.4, 90),             # TPS16630 eFuse
    'J1': (45.0, 45.3, 0),              # 20 V pigtail XH, landing x_rel 0, body bottom at z 35.8
    'J4': (46.3, 36.27, 0),             # GPIO landing B (plug B), x_rel 0
    'J3': (59.5, 36.27, 90),            # GPIO landing A (plug A), x_rel -10..-20
    'J7': (63.0, 42.0, 90),             # D4a tap
    'J9': (78.0, 44.0, 0),              # speaker R, landing x_rel -33, z 40
    'J8': (11.5, 44.0, 90),             # speaker L, landing x_rel +33.5, z 40
    'J6': (41.0, 24.0, 0),              # touch XH, landing x_rel 4, z 60
    'U100': (60.0, 25.5, 270),          # TAS5756M horizontal, output end toward the LC block (TI Fig. 86)
    'C7': (55.5, 16.8, 0),              # NID output C (EMC C3), under +Vo pins
    # LC block: the output nearer the package end (OUT_xN) takes the nearer inductor, so the OUT traces fan out uncrossed
    'L101': (74.0, 18.6, 90), 'L100': (83.6, 18.6, 90),   # channel A (top row), pad 1 (OUT) at the bottom
    'L102': (74.0, 28.8, 270), 'L103': (83.6, 28.8, 270), # channel B (bottom row), pad 1 (OUT) at the top
    'C104': (62.95, 19.35, 0), 'C108': (66.6, 19.35, 180), 'C100': (60.4, 19.35, 180),   # bootstraps A, PVDD 0.1u
    'C115': (62.95, 31.6, 0), 'C111': (66.6, 31.6, 180), 'C121': (60.4, 31.6, 180),      # bootstraps B, PVDD 0.1u
}
FIXED_BACK = {
    'J2': (20.0, 45.415, 0),            # USB4085: A1 at (22.975, 41.39) -> mouth flush with the bottom edge
    'LK1': (31.0, 46.3, 0),
}
# back parts: anchor = (ref, pad) whose position the part is placed next to (mirrored onto the back)
ANCHOR = {
    'C101': ('U100', '7'), 'C102': ('U100', '6'), 'C122': ('U100', '41'), 'C123': ('U100', '43'),
    'C103': ('U100', '8'), 'R101': ('U100', '9'), 'R100': ('U100', '9'),
    'C105': ('U100', '14'), 'C119': ('U100', '30'), 'C118': ('U100', '28'), 'C120': ('U100', '35'), 'C112': ('U100', '33'),
    'C106': ('U100', '13'), 'C107': ('U100', '11'), 'C113': ('U100', '36'), 'C114': ('U100', '38'),
    'R102': ('U100', '40'), 'R103': ('U100', '18'), 'R104': ('U100', '19'), 'R105': ('U100', '21'),
    'R17': ('U100', '27'), 'R14': ('U100', '23'), 'R15': ('U100', '25'), 'R16': ('U100', '24'),
    'C109': ('L100', '2'), 'C110': ('L101', '2'), 'C117': ('L103', '2'), 'C116': ('L102', '2'),
    'R1': ('U1', '7'), 'R2': ('U1', '7'), 'R3': ('U1', '8'), 'R4': ('U1', '11'), 'R5': ('U1', '14'), 'R6': ('U1', '15'),
    'C1': ('U1', '1'), 'C2': ('U1', '2'), 'C3': ('U1', '10'), 'C4': ('U1', '19'), 'D1': ('U1', '19'), 'F1': ('J1', '1'),
    'F2': ('J2', 'A4'), 'C8': ('J2', 'A9'), 'C9': ('J2', 'B4'), 'R10': ('J2', 'A5'), 'R11': ('J2', 'B5'),
    'F3': ('J5', '1'), 'C10': ('J5', '1'), 'R19': ('J5', '3'),
    'D2': ('C7', '1'), 'R7': ('PS1', '13'), 'R8': ('PS1', '12'), 'R9': ('PS1', '12'),
    'U2': ('J6', '1'), 'R12': ('J6', '1'), 'C11': ('J6', '1'), 'C12': ('J6', '1'), 'R13': ('J6', '1'), 'F4': ('J6', '1'),
    'R26': ('U100', '30'), 'R27': ('U100', '31'),
    'R18': ('J4', '2'),
    'R20': ('J7', '2'), 'R21': ('J7', '3'), 'R22': ('J7', '4'), 'R23': ('J7', '5'), 'R24': ('J7', '7'), 'R25': ('J7', '8'),
    'TP1': ('U1', '1'), 'TP2': ('U1', '18'), 'TP3': ('U1', '14'), 'TP4': ('U1', '15'), 'TP5': ('U1', '16'), 'TP6': ('U1', '13'),
    'TP7': ('U1', '9'), 'TP8': ('C6', '1'), 'TP9': ('C7', '1'), 'TP10': ('LK1', '1'), 'TP11': ('J2', 'A9'),
    'TP12': ('J5', '1'), 'TP13': ('PS1', '12'), 'TP14': ('PS1', '13'), 'TP15': ('J2', 'A12'), 'TP16': ('J6', '1'),
    'TP17': ('J6', '2'), 'TP18': ('F5', '2'), 'TP19': ('U100', '40'), 'TP20': ('U100', '39'),
}
ORDER = ['C101', 'C102', 'C122', 'C123', 'C103', 'C105', 'C119', 'C118', 'C120', 'C112', 'R101', 'R100',
         'C106', 'C107', 'C113', 'C114', 'R102', 'R103', 'R104', 'R105', 'R17', 'R14', 'R15', 'R16', 'R26', 'R27',
         'C109', 'C110', 'C117', 'C116',
         'C1', 'C2', 'R1', 'R2', 'R3', 'C3', 'R4', 'R5', 'R6', 'C4', 'D1', 'F1',
         'F2', 'C8', 'C9', 'R10', 'R11', 'F3', 'C10', 'R19', 'D2', 'R7', 'R8', 'R9',
         'U2', 'R12', 'C11', 'C12', 'R13', 'F4', 'R18', 'R20', 'R21', 'R22', 'R23', 'R24', 'R25']
TPS = ['TP%d' % i for i in range(1, 21)]
BACK_KEEPOUT = [(52.3, 22.8, 67.7, 28.2),        # TAS thermal land / via field (rot 270)
                (0.0, 0.0, 9.0, 9.0), (81.0, 0.0, 90.0, 9.0)]   # door touches the back top corners (K19)
GAP = 0.45


def rect_of(fp, layer):
    cy = fp.GetCourtyard(layer)
    bb = cy.BBox() if cy.OutlineCount() else fp.GetBoundingBox(False)
    return (pcbnew.ToMM(bb.GetX()), pcbnew.ToMM(bb.GetY()), pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom()))


def overlap(a, b, g=0.0):
    return not (a[2] + g <= b[0] or b[2] + g <= a[0] or a[3] + g <= b[1] or b[3] + g <= a[1])


def back_obstacles(board):
    obs = list(BACK_KEEPOUT)
    for fp in board.GetFootprints():
        if fp.GetLayer() == pcbnew.F_Cu:
            for p in fp.Pads():
                if p.HasHole() or p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                    bb = p.GetBoundingBox()
                    c = 0.35
                    obs.append((pcbnew.ToMM(bb.GetX()) - c, pcbnew.ToMM(bb.GetY()) - c,
                                pcbnew.ToMM(bb.GetRight()) + c, pcbnew.ToMM(bb.GetBottom()) + c))
    for (x, y) in pm.HOLES:
        obs.append((x - 3.4, y - 3.4, x + 3.4, y + 3.4))        # screw head Ø6 + margin
    return obs


def place_back(board, ref, target, obs, rots=(0, 90, 180, 270), rmax=22.0, step=0.3):
    fp = board.FindFootprintByReference(ref)
    if fp.GetLayer() == pcbnew.F_Cu:
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
                bb = rect_of(fp, pcbnew.B_CrtYd)
                cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
                fp.Move(pcbnew.VECTOR2I(MM(x - cx), MM(y - cy)))
                bb = rect_of(fp, pcbnew.B_CrtYd)
                if bb[0] < 0.4 or bb[1] < 0.4 or bb[2] > pm.W - 0.4 or bb[3] > pm.H - 0.4:
                    continue
                if any(overlap(bb, o, GAP) for o in obs):
                    continue
                obs.append(bb)
                return (round(x, 2), round(y, 2), rot)
        r += step
    raise RuntimeError('no spot for ' + ref)


def main(netlist, out):
    plan = {r: (v[0], v[1], v[2], 'F') for r, v in FRONT.items()}
    plan.update({r: (v[0], v[1], v[2], 'B') for r, v in FIXED_BACK.items()})
    board, placed, missing = pm.build(netlist, out, plan, layers=4)
    obs = back_obstacles(board)
    for r in FIXED_BACK:
        obs.append(rect_of(board.FindFootprintByReference(r), pcbnew.B_CrtYd))
    where = {}
    for ref in ORDER + TPS:
        aref, apad = ANCHOR[ref]
        afp = board.FindFootprintByReference(aref)
        pad = [p for p in afp.Pads() if p.GetNumber() == apad][0]
        tgt = (pcbnew.ToMM(pad.GetPosition().x), pcbnew.ToMM(pad.GetPosition().y))
        where[ref] = place_back(board, ref, tgt, obs)
    left = [r for r in missing if r not in where]
    pcbnew.SaveBoard(out, board)
    return board, where, left


if __name__ == '__main__':
    b, where, left = main(sys.argv[1], sys.argv[2])
    print('back placed', len(where), 'unplaced', left)
