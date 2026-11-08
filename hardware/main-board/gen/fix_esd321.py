"""Mic strip, decision 10.1 (Daniel 2026-11-08): D1-D3 become TI ESD321DYAR (TPD1E05U06DYAR: 0 stock, 26 weeks).

The ESD321 DYA pinout is the reverse of the TPD1E05U06 DYA: pin 1 = GND, pin 2 = IO (ESD321 datasheet rev C,
table 4-2; TPD1E05U06 SLVSBO7O: pin 1 = I/O, pin 2 = GND). Each footprint turns 180 deg about its centre and the
pad nets swap, so the copper stays where it was: pad 1 (GND) at x 19.8, pad 2 (signal) at x 21.2, rows y 1.25 /
3.0 / 4.75 for VDD_C / CLK_C / DATA_C. The closed end of the silk bracket follows pad 1 (GND).
Idempotent: a footprint whose pad 1 is already on GND is left alone.
Run: python3 fix_esd321.py <in.kicad_pcb> <out.kicad_pcb>, with the strip's .kicad_pro beside <in> under the same
name: the zone refill takes the 0.3 mm copper-to-edge rule from it (without it KiCad's 0.5 mm default applies)."""
import sys

import pcbnew


def main(src, dst):
    b = pcbnew.LoadBoard(src)
    gnd = b.FindNet('GND')
    for ref in ('D1', 'D2', 'D3'):
        fp = b.FindFootprintByReference(ref)
        p1, p2 = fp.FindPadByNumber('1'), fp.FindPadByNumber('2')
        if p1.GetNetname() != 'GND':
            sig = p1.GetNet()
            fp.SetOrientationDegrees(fp.GetOrientationDegrees() + 180)
            p1.SetNet(gnd)
            p2.SetNet(sig)
        fp.SetValue('ESD321')
        for p in fp.Pads():
            q = p.GetPosition()
            print(ref, 'pad', p.GetNumber(), round(pcbnew.ToMM(q.x), 3), round(pcbnew.ToMM(q.y), 3), p.GetNetname())
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(dst, b)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
