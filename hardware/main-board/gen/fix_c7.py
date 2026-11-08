"""Main board rev 2.1 (2026-11-08): C7 (NID EMC output C, Wuerth 860160572003, 12.5 tall) leaves the slot between the
NID and J6 for the top strip above the NID, so every front lead (J6 included) can be plugged after the board is mounted
(design chat 2026-11-08, reach check: J6 was tight because of C7). Same part, same footprint, same nets.

New place: courtyard centre (50.67, -2.05), pad 1 (+) at (51.67, -2.05), rotation 180 (+ towards the NID +Vo pins 1-4,
- towards the GND pins 5-6). Courtyard (r 2.79) between the board edge (y -5) and the NID courtyard (y 0.75).
The THT pads reach In2 +5V and In1 GND directly; no tracks.
Run: python3 fix_c7.py <in.kicad_pcb> <out.kicad_pcb>"""
import sys

import pcbnew

import mroute
import route_main as rm
import silk

MM = pcbnew.FromMM


def main(src, dst):
    b = pcbnew.LoadBoard(src)
    fp = b.FindFootprintByReference('C7')
    fp.SetOrientationDegrees(180)
    fp.SetPosition(pcbnew.VECTOR2I(MM(51.67), MM(-2.05)))
    for p in fp.Pads():
        q = p.GetPosition()
        print('C7 pad', p.GetNumber(), round(pcbnew.ToMM(q.x), 3), round(pcbnew.ToMM(q.y), 3), p.GetNetname())
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    for _ in range(2):
        print('stitch vias', len(mroute.stitch(b, rm.CLASSES)))
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    print('dangling removed', rm.clean_dangling(b))
    shown, hidden = silk.place(b)
    print('silk refs shown', shown, 'hidden', len(hidden), hidden)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(dst, b)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
