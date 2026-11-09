"""Touch board rev D: give every footprint its library nickname, so DRC's schematic parity matches the symbols'
Footprint fields (pcbnew.FootprintLoad drops the nickname; block 2 lesson). Geometry is untouched.
Run next to touch-board.kicad_pro: python3 fix_touch_fpid.py <touch-board.kicad_pcb>"""
import sys

import pcbnew

LIBS = {'C_0603_1608Metric': 'Capacitor_SMD', 'R_0603_1608Metric': 'Resistor_SMD',
        'SOIC-14_3.9x8.7mm_P1.27mm': 'Package_SO', 'TouchElectrode_16x16mm_R2': 'ha_panel',
        'WirePads_1x04_P3.50mm_2.0x3.0mm': 'ha_panel'}


def main(path):
    b = pcbnew.LoadBoard(path)
    for fp in b.GetFootprints():
        name = fp.GetFPID().GetLibItemName().wx_str()
        lib = fp.GetFPID().GetLibNickname().wx_str()
        if not lib and name in LIBS:
            fp.SetFPID(pcbnew.LIB_ID(LIBS[name], name))
            print(fp.GetReference(), '->', LIBS[name] + ':' + name)
    pcbnew.SaveBoard(path, b)


if __name__ == '__main__':
    main(sys.argv[1])
