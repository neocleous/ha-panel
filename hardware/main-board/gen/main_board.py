"""HA panel main board — schematic (KiCad 9). Run: python3 main_board.py <outdir>"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kicadgen as kg
import lib_ha_panel
import footprints
import symlib

OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/work/out/main-board'
DATE = '2026-11-11'
REV = '3'            # rev 3: re-laid for the site behind the display (claude/main-board-site-2026-11-10.md issue 2)

R0603 = 'Resistor_SMD:R_0603_1608Metric'
R0805 = 'Resistor_SMD:R_0805_2012Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'
C0805 = 'Capacitor_SMD:C_0805_2012Metric'
C1206 = 'Capacitor_SMD:C_1206_3216Metric'
TP_BACK = 'TestPoint:TestPoint_Pad_D1.5mm'
NANO2 = 'Fuse:Fuse_Littelfuse-NANO2-451_453'


def F(mpn='', mfr='', dk='', spec='', note=''):
    d = {}
    if mpn: d['MPN'] = mpn
    if mfr: d['Manufacturer'] = mfr
    if dk: d['DigiKey'] = dk
    if spec: d['Spec'] = spec
    if note: d['Note'] = note
    return d


def design(prj):
    # ------------------------------------------------------------------ sheets
    s_in = prj.add_sheet('20 V inlet and eFuse', 'inlet.kicad_sch', 'Main board - 20 V inlet and eFuse')
    s_5v = prj.add_sheet('5 V supply and outputs', 'supply_5v.kicad_sch', 'Main board - 5 V supply and outputs')
    s_io = prj.add_sheet('3.3 V, Pi link, sensors, radar, echo-ref', 'io.kicad_sch',
                         'Main board - 3.3 V, Pi link, XH, D4a')
    s_amp = prj.add_sheet('Amplifier', 'amplifier.kicad_sch', 'Main board - amplifier')

    def tp(sh, ref, net, x, y, label, note=''):
        sh.comp(ref, 'Connector:TestPoint', label, (x, y), nets={'1': net}, footprint=TP_BACK,
                fields=F(note=note or 'bare test pad on the door-side face: probe with the door off'), in_bom=False)

    # =================================================================== 20 V INLET
    s = s_in
    s.text('20 V INLET  (5807 pigtail -> fuse -> TPS16630 eFuse -> +20V bus)', 25.4, 25.4, size=2.0, bold=True)
    s.comp('J1', 'Connector_Generic:Conn_01x02', 'B2B-XH-A', (53.34, 60.96),
           nets={'1': 'VIN_PIGTAIL', '2': 'GND'}, footprint='Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical',
           fields=F('B2B-XH-A', 'JST', '455-B2B-XH-A-ND', note='pin 1 = +20 V from 5807 X4-1 (VOUT), pin 2 = GND (X4-2); pigtail ~70 mm'))
    s.comp('F1', 'Device:Fuse', '5 A 0453005.MR', (101.6, 60.96), rot=90, nets={'1': 'VIN_PIGTAIL', '2': 'VIN_EF'},
           footprint=NANO2, fields=F('0453005.MR', 'Littelfuse', 'F3139CT-ND', '5 A very fast, 12.5 mOhm cold'))
    s.comp('C1', 'Device:C', '1u 50V', (127.0, 68.58), nets={'1': 'VIN_EF', '2': 'GND'}, footprint=C0805,
           fields=F(spec='1 uF 50 V X7R 0805', note='eFuse input, >=1 uF with TVS (SLVSET9G 9.4.1)'))
    s.comp('C2', 'Device:C', '100n 50V', (139.7, 68.58), nets={'1': 'VIN_EF', '2': 'GND'}, footprint=C0603,
           fields=F(spec='100 nF 50 V X7R 0603', note='eFuse IN bypass >=0.1 uF (SLVSET9G 8.3.9)'))
    s.pwr_flag('VIN_EF', (114.3, 76.2))
    s.pwr_flag('GND', (63.5, 76.2))
    s.comp('R1', 'Device:R', '412k 1%', (165.1, 114.3), nets={'1': 'VIN_EF', '2': 'EF_UVLO'}, footprint=R0603,
           fields=F(spec='412 kOhm 1% 0603', note='UVLO/OVP divider R1'))
    s.comp('R2', 'Device:R', '9.09k 1%', (177.8, 114.3), nets={'1': 'EF_UVLO', '2': 'EF_OVP'}, footprint=R0603,
           fields=F(spec='9.09 kOhm 1% 0603', note='UVLO/OVP divider R2'))
    s.comp('R3', 'Device:R', '22.1k 1%', (190.5, 114.3), nets={'1': 'EF_OVP', '2': 'GND'}, footprint=R0603,
           fields=F(spec='22.1 kOhm 1% 0603', note='UVLO/OVP divider R3'))
    s.comp('U1', 'ha_panel:TPS16630', 'TPS16630PWPT', (231.14, 76.2),
           nets={'1': 'VIN_EF', '2': 'VIN_EF', '3': 'VIN_EF', '6': 'VIN_EF', '7': 'EF_UVLO', '8': 'EF_OVP',
                 '13': 'EF_SHDN', '12': 'GND', '18': '+20V', '19': '+20V', '20': '+20V', '16': 'EF_PGOOD',
                 '15': 'EF_FLT_N', '14': 'EF_IMON', '10': 'EF_DVDT', '11': 'EF_ILIM', '9': 'GND', '21': 'GND'},
           footprint='Package_SO:HTSSOP-20-1EP_4.4x6.5mm_P0.65mm_EP3.4x6.5mm_Mask2.96x2.96mm_ThermalVias', fields=F('TPS16630PWPT', 'Texas Instruments', '296-TPS16630PWPTCT-ND'))
    s.comp('C3', 'Device:C', '47n 50V', (274.32, 106.68), nets={'1': 'EF_DVDT', '2': 'GND'}, footprint=C0603,
           fields=F(spec='47 nF 50 V X7R 0603', note='dV/dt: t = 20.8e3 x 20 V x 47 nF = 19.6 ms'))
    s.comp('R4', 'Device:R', '5.49k 1%', (287.02, 106.68), nets={'1': 'EF_ILIM', '2': 'GND'}, footprint=R0603,
           fields=F(spec='5.49 kOhm 1% 0603', note='I_OL = 18/5.49k = 3.28 A (+-7%)'))
    s.comp('R5', 'Device:R', '10k 1%', (299.72, 106.68), nets={'1': 'EF_IMON', '2': 'GND'}, footprint=R0603,
           fields=F(spec='10 kOhm 1% 0603', note='IMON 27.9 uA/A -> 0.279 V/A'))
    s.comp('R6', 'Device:R', '100k', (325.12, 76.2), nets={'1': '+3V3', '2': 'EF_FLT_N'}, footprint=R0603,
           fields=F(spec='100 kOhm 1% 0603', note='FLT pull-up (open drain)'))
    s.comp('C4', 'Device:C', '100n 50V', (274.32, 63.5), nets={'1': '+20V', '2': 'GND'}, footprint=C0603,
           fields=F(spec='100 nF 50 V X7R 0603', note='eFuse OUT >=0.1 uF'))
    s.comp('D1', 'Device:D_Zener', 'SMBJ22A', (287.02, 63.5), rot=270, nets={'1': '+20V', '2': 'GND'},
           footprint='Diode_SMD:D_SMB', fields=F('SMBJ22A', 'Littelfuse', 'SMBJ22ALFCT-ND', 'TVS 22 V standoff, unidirectional',
                                                'bus TVS (power budget 1.3)'))
    tp(s, 'TP1', 'VIN_EF', 152.4, 45.72, 'VIN')
    tp(s, 'TP2', '+20V', 299.72, 45.72, '20V')
    tp(s, 'TP3', 'EF_IMON', 274.32, 139.7, 'IMON')
    tp(s, 'TP4', 'EF_FLT_N', 287.02, 139.7, 'FLT')
    tp(s, 'TP5', 'EF_PGOOD', 299.72, 139.7, 'PG')
    tp(s, 'TP6', 'EF_SHDN', 312.42, 139.7, 'SHDN')
    tp(s, 'TP7', 'GND', 325.12, 139.7, 'GND')
    s.text('\n'.join([
        'TPS16630 settings (TI SLVSET9G, Rev. G, 2026-04):',
        '  UVLO rising 1.2 V x 443.2k/31.19k = 17.05 V, falling 15.94 V  -> runs only on the 20 V PD contract',
        '  OVP rising 1.2 V x 443.2k/22.1k = 24.06 V (+-2 %), release 22.5 V  -> below TAS5756M PVDD 26.4 V (SLAS988B 7.3)',
        '  Divider current 20 V / 443 k = 45 uA  (> 20 x 150 nA pin leakage, SLVSET9G 9.2.2.2)',
        '  I_OL = 18 / R_ILIM[k] = 18 / 5.49 = 3.28 A (+-7 %)  vs design peak 2.83 A and 65 W PD contract 3.25 A',
        '  dV/dt: 47 nF -> 19.6 ms to 20 V; inrush = 385 uF x 20 V / 19.6 ms = 0.39 A; turn-on delay 742 us + 49.5 us/nF x 47',
        '  MODE = GND: auto-retry after faults; SHDN open = on (internal pull-up 2.7 V); PGOOD (open drain) enables the NID',
        'F1 0453005.MR kept as decided (5 A); NID spec recommends 8 A for its own input - see checkpoint 1 note.',
        'D1 SMBJ22A on the +20V bus (eFuse output) per power budget; output load is capacitive, no Schottky needed.']),
        25.4, 198.12)

    # =================================================================== 5 V SUPPLY
    s = s_5v
    s.text('5 V SUPPLY  (Mean Well EMC circuit -> NID100-5 -> Pi USB-C output, radar branch)', 25.4, 25.4, size=2.0, bold=True)
    s.comp('C5', 'Device:C_Polarized', '120u 63V', (45.72, 68.58), nets={'1': '+20V', '2': 'GND'},
           footprint='Capacitor_THT:CP_Radial_D10.0mm_P5.00mm',
           fields=F('EEU-FR1J121B', 'Panasonic', 'P15289CT-ND', '120 uF 63 V FR Ø10x16', 'Mean Well EMC circuit C1'))
    s.comp('L1', 'Device:L', '15u SRR1260', (71.12, 60.96), rot=90, nets={'1': '+20V', '2': 'NID_VIN'},
           footprint='Inductor_SMD:L_Bourns_SRR1260',
           fields=F('SRR1260-150M', 'Bourns', 'SRR1260-150MCT-ND', '15 uH 20%, Isat 4.6 A, 27 mOhm max',
                    'Mean Well EMC circuit L1 (NiZn asked; Bourns states ferrite only)'))
    s.comp('C6', 'Device:C_Polarized', '120u 63V', (101.6, 68.58), nets={'1': 'NID_VIN', '2': 'GND'},
           footprint='Capacitor_THT:CP_Radial_D10.0mm_P5.00mm',
           fields=F('EEU-FR1J121B', 'Panasonic', 'P15289CT-ND', '120 uF 63 V FR Ø10x16', 'Mean Well EMC circuit C2'))
    s.pwr_flag('NID_VIN', (88.9, 83.82))
    s.comp('PS1', 'ha_panel:NID100-5', 'NID100-5', (165.1, 73.66),
           nets={'9': 'NID_VIN', '10': 'NID_VIN', '13': 'NID_RC', '12': 'NID_TRIM', '1': '+5V', '2': '+5V', '3': '+5V',
                 '4': '+5V', '5': 'GND', '6': 'GND', '7': 'GND', '8': 'GND'},
           footprint='ha_panel:MeanWell_NID100_SIP-13', fields=F('NID100-5', 'Mean Well', '1866-NID100-5-ND'))
    s.comp('R7', 'Device:R', '0R', (114.3, 109.22), rot=90, nets={'1': 'EF_PGOOD', '2': 'NID_RC'}, footprint=R0603,
           fields=F(spec='0 Ohm 0603', note='eFuse PGOOD -> NID R.C. (NID off until the +20V bus is up); remove = NID free-running'))
    s.comp('R8', 'Device:R', 'DNP (bench)', (127.0, 144.78), nets={'1': 'NID_TRIM', '2': 'GND'}, footprint=R0805,
           dnp=True, fields=F(note='trim-up position Trim->Com (5.1 V option, D23/V20): value found on the bench by '
                                    'substitution at TP13, then fitted'))
    s.comp('R9', 'Device:R', 'DNP (bench)', (152.4, 144.78), nets={'1': 'NID_TRIM', '2': '+5V'}, footprint=R0805, dnp=True,
           fields=F(note='trim-down position Trim->+Vout, not expected to be used'))
    s.comp('C7', 'Device:C_Polarized', '22u 35V', (203.2, 68.58), nets={'1': '+5V', '2': 'GND'},
           footprint='Capacitor_THT:CP_Radial_D5.0mm_P2.00mm',
           fields=F('860160572003', 'Würth', '732-9541-1-ND', '22 uF 35 V Ø5', 'Mean Well EMC circuit C3 (total ext. C <= 100 uF)'))
    s.comp('D2', 'Device:D_Zener', 'SMBJ6.0A-E', (218.44, 68.58), rot=270, nets={'1': '+5V', '2': 'GND'},
           footprint='Diode_SMD:D_SMB', fields=F('SMBJ6.0A-E', 'Littelfuse', '18-SMBJ6.0A-ECT-ND', 'TVS 6.0 V standoff'))
    # Pi branch
    s.comp('F2', 'Device:Fuse', '10 A 0453010.MR', (241.3, 60.96), rot=90, nets={'1': '+5V', '2': '5V_PI_F'},
           footprint=NANO2, fields=F('0453010.MR', 'Littelfuse', 'F3141CT-ND', '10 A very fast, 5.6 mOhm cold', 'Pi branch'))
    s.comp('LK1', 'Jumper:Jumper_2_Bridged', 'wire link', (289.56, 60.96), nets={'1': '5V_PI_F', '2': 'VBUS_PI'},
           footprint='ha_panel:WireLink_P7.62mm_D1.3mm',
           fields=F(spec='tinned Cu wire 1.0 mm (18 AWG)', note='Pi-branch current link: open for bench 2.7 (10 A meter in series)'))
    s.comp('J2', 'Connector:USB_C_Receptacle_USB2.0_16P', 'USB4085-GF-A', (360.68, 101.6),
           nets={'A4': 'VBUS_PI', 'A9': 'VBUS_PI', 'B4': 'VBUS_PI', 'B9': 'VBUS_PI', 'A5': 'PI_CC1', 'B5': 'PI_CC2',
                 'A6': None, 'B6': None, 'A7': None, 'B7': None, 'A8': None, 'B8': None,
                 'A1': 'GND', 'A12': 'GND', 'B1': 'GND', 'B12': 'GND', 'S1': 'GND'},
           footprint='Connector_USB:USB_C_Receptacle_GCT_USB4085',
           fields=F('USB4085-GF-A', 'GCT', spec='USB 2.0 Type-C, THT dip / PCB top mount, 5.00 A VBUS, 6.25 A GND, 48 V; '
                    '3.46 above the board, axis 1.88 (GCT USB4085 rev B 2023-02-28)',
                    note='source port to the Pi: VBUS + Rp only, no data. Door-side face, soldered from the back; '
                         'mouth flush with the bottom edge, opening downward (rev 3)'))
    s.comp('R10', 'Device:R', '10k 1%', (317.5, 111.76), nets={'1': 'VBUS_PI', '2': 'PI_CC1'}, footprint=R0603,
           fields=F(spec='10 kOhm 1% 0603', note='Rp to 5 V = 3.0 A advertisement (USB Type-C)'))
    s.comp('R11', 'Device:R', '10k 1%', (330.2, 111.76), nets={'1': 'VBUS_PI', '2': 'PI_CC2'}, footprint=R0603,
           fields=F(spec='10 kOhm 1% 0603', note='Rp to 5 V = 3.0 A advertisement'))
    s.comp('C8', 'Device:C', '10u 25V', (317.5, 68.58), nets={'1': 'VBUS_PI', '2': 'GND'}, footprint=C1206,
           fields=F(spec='10 uF 25 V X7R 1206', note='local at J2 (USB4085)'))
    s.comp('C9', 'Device:C', '100n 50V', (330.2, 68.58), nets={'1': 'VBUS_PI', '2': 'GND'}, footprint=C0603,
           fields=F(spec='100 nF 50 V X7R 0603'))
    # radar branch
    s.comp('F3', 'Device:Fuse', '1 A 0453001.MR', (241.3, 139.7), rot=90, nets={'1': '+5V', '2': '5V_RADAR'},
           footprint=NANO2, fields=F('0453001.MR', 'Littelfuse', 'F3137CT-ND', '1 A very fast, 153 mOhm cold', 'radar branch'))
    s.comp('C10', 'Device:C', '1u 50V', (279.4, 147.32), nets={'1': '5V_RADAR', '2': 'GND'}, footprint=C0805,
           fields=F(spec='1 uF 50 V X7R 0805', note='radar local decoupling'))
    tp(s, 'TP8', 'NID_VIN', 114.3, 45.72, 'NID_IN')
    tp(s, 'TP9', '+5V', 228.6, 45.72, '5V')
    tp(s, 'TP10', '5V_PI_F', 269.24, 45.72, '5V_F')
    tp(s, 'TP11', 'VBUS_PI', 342.9, 45.72, 'EXT5V')
    tp(s, 'TP12', '5V_RADAR', 292.1, 129.54, 'RADAR')
    tp(s, 'TP13', 'NID_TRIM', 165.1, 132.08, 'TRIM')
    tp(s, 'TP14', 'NID_RC', 139.7, 101.6, 'RC')
    tp(s, 'TP15', 'GND', 355.6, 45.72, 'GND')
    s.text('\n'.join([
        'Mean Well NID100-SPEC (2024-10-30): EMC circuit C1/C2 120 uF/63 V, L1 15 uH (NiZn), C3 22 uF/35 V; ext. C max 100 uF/16 V;',
        '  fuse recommended 8 A; R.C.: on = open or 1.2-12 V, off = < 0.4 V; pin 12 "Trim (optional)", no formula published.',
        'L1 is a single winding in +Vin: the input return is the common board ground (non-isolated NID, amp on the same ground).',
        'External C on +5V: C7 22 uF + C8 10 uF (X7R 1206, ~70 % at 5 V) + C9 + C10 + LDO input path (behind 2.2 Ohm)  ~ 35 uF << 100 uF.',
        'Pi output: 0453010.MR -> LK1 (wire link) -> J2 USB4085 VBUS; CC1/CC2 Rp 10 k to 5 V (3 A); Pi uses PSU_MAX_CURRENT=5000.',
        'J2 USB4085-GF-A (THT, decision 3A) sits on the door-side face like every other part, mouth down at the bottom edge (rev 3).',
        'Bench 2.7 test pads: 5V (NID out) | 5V_F (after fuse) | EXT5V (at J2) ; LK1 opened for the series current.',
        'Trim network DNP (D23/V20): R8 Trim->Com raises Vout, R9 Trim->+Vout lowers it (FB-divider convention, not published',
        '  by Mean Well). Spec lists pin 12 as "Trim (optional)" with no formula; on arrival measure R(pin 12-Com) unpowered and',
        '  Vout with a trimmer clipped from TP13 to GND before fitting R8. No response at pin 12 -> alternative-regulator decision.']),
        25.4, 190.5)

    # =================================================================== 3.3 V / IO
    s = s_io
    s.text('3.3 V LDO (follows the Pi 3V3)', 25.4, 25.4, size=2.0, bold=True)
    s.comp('R12', 'Device:R', '2.2R', (50.8, 50.8), rot=90, nets={'1': '+5V', '2': 'LDO_IN'}, footprint=R0805,
           fields=F(spec='2.2 Ohm 1% 0805', note='RC pre-filter with C11: fc 7.2 kHz, ~29 dB at the NID 200 kHz'))
    s.comp('C11', 'Device:C', '10u 25V', (73.66, 58.42), nets={'1': 'LDO_IN', '2': 'GND'}, footprint=C1206,
           fields=F(spec='10 uF 25 V X7R 1206'))
    s.pwr_flag('LDO_IN', (63.5, 66.04))
    s.comp('U2', 'ha_panel:TPS70933DBV', 'TPS70933DBVR', (101.6, 58.42),
           nets={'1': 'LDO_IN', '3': 'PI_3V3', '5': '+3V3', '2': 'GND'},
           footprint='Package_TO_SOT_SMD:SOT-23-5', fields=F('TPS70933DBVR', 'Texas Instruments', note='new part (V17)'))
    s.comp('R13', 'Device:R', '100k', (73.66, 83.82), nets={'1': 'PI_3V3', '2': 'GND'}, footprint=R0603,
           fields=F(spec='100 kOhm 1% 0603', note='EN pull-down: LDO off unless the Pi 3V3 (header pin 1) is up'))
    s.comp('C12', 'Device:C', '4.7u 16V', (127.0, 58.42), nets={'1': '+3V3', '2': 'GND'}, footprint=C0805,
           fields=F(spec='4.7 uF 16 V X7R 0805', note='>= 2.0 uF effective (SBVS186H 8.1.1)'))
    s.comp('F4', 'Device:Polyfuse', '0.2 A 0ZCJ0020FF2E', (152.4, 50.8), rot=90, nets={'1': '+3V3', '2': '3V3_SENS'},
           footprint='Fuse:Fuse_1206_3216Metric',
           fields=F('0ZCJ0020FF2E', 'Bel Fuse', '5923-0ZCJ0020FF2ECT-ND', 'PTC 0.20 A hold, 30 V, R1max 2.5 Ohm',
                    'touch / BME680 / VEML6030 branch'))
    tp(s, 'TP16', '+3V3', 127.0, 38.1, '3V3')
    s.comp('R26', 'Device:R', '0R', (177.8, 76.2), rot=90, nets={'1': '+3V3', '2': '3V3_AMP'}, footprint=R0603,
           fields=F(spec='0 Ohm 0603', note='amp logic rail (DVDD/AVDD/CPVDD) from the board LDO - default'))
    s.comp('R27', 'Device:R', '0R DNP', (177.8, 88.9), rot=90, nets={'1': 'PI_3V3', '2': '3V3_AMP'}, footprint=R0603,
           dnp=True, fields=F(spec='0 Ohm 0603', note='option: amp logic rail from the Pi 3V3 (same supply as the Pi '
                                                   'drivers, SLAS988B 7.3 note 2); fit only with R26 removed'))
    s.pwr_flag('3V3_AMP', (195.58, 99.06))

    s.text('Pi signal leads (wire pads, 2.54 mm; 13 leads to three housings at the Pi, gpio-leads.md)', 25.4, 106.68, size=2.0, bold=True)
    s.comp('J3', 'Connector_Generic:Conn_02x05_Odd_Even', 'Pi signal leads, 9 (wire pads)', (63.5, 132.08),
           nets={'1': 'PI_3V3', '2': 'I2C_SDA', '3': 'I2C_SCL', '4': 'PI_TXD', '5': 'GND', '6': 'PI_RXD',
                 '7': 'PI_BCLK', '8': 'GND', '9': 'AMP_MUTE_N', '10': None},
           footprint='ha_panel:WirePads_2x05_P2.54mm_D1.0mm', in_bom=False,
           fields=F(note='wire pads only, in the order of the housings at the Pi (rev 3): 1x3 on Pi 1-3-5: J3.1=Pi1 3V3, '
                         '.2=Pi3 SDA, .3=Pi5 SCL; 2x5 on Pi 7-16: .4=Pi8 TXD, .5=Pi9 GND, .6=Pi10 RXD, .7=Pi12 BCLK, '
                         '.8=Pi14 GND, .9=Pi15 GPIO22; .10 spare'))
    s.comp('J4', 'Connector_Generic:Conn_02x02_Odd_Even', 'Pi signal leads, 4 (wire pads)', (63.5, 165.1),
           nets={'1': 'PI_LRCLK', '3': 'GND', '2': 'PI_DIN', '4': 'PI_DOUT'},
           footprint='ha_panel:WirePads_2x02_P2.54mm_D1.0mm', in_bom=False,
           fields=F(note='wire pads only, 2x3 housing on Pi 35-40: J4.1=Pi35 LRCLK, .2=Pi38 DIN, .3=Pi39 GND, .4=Pi40 DOUT'))
    s.comp('R14', 'Device:R', '0R', (124.46, 121.92), rot=90, nets={'1': 'PI_BCLK', '2': 'I2S_BCLK'}, footprint=R0603,
           fields=F(spec='0 Ohm 0603', note='I2S series position (spin-1 lever: 22-47 Ohm if edges ring)'))
    s.comp('R15', 'Device:R', '0R', (124.46, 134.62), rot=90, nets={'1': 'PI_LRCLK', '2': 'I2S_LRCLK'}, footprint=R0603,
           fields=F(spec='0 Ohm 0603', note='I2S series position'))
    s.comp('R16', 'Device:R', '0R', (124.46, 147.32), rot=90, nets={'1': 'PI_DOUT', '2': 'I2S_DOUT'}, footprint=R0603,
           fields=F(spec='0 Ohm 0603', note='I2S series position'))
    s.comp('R17', 'Device:R', '100k', (160.02, 132.08), nets={'1': 'AMP_MUTE_N', '2': 'GND'}, footprint=R0603,
           fields=F(spec='100 kOhm 1% 0603', note='amp muted while GPIO22 is not driven'))
    s.comp('R18', 'Device:R', '100k', (172.72, 132.08), nets={'1': 'PI_DIN', '2': 'GND'}, footprint=R0603,
           fields=F(spec='100 kOhm 1% 0603', note='keeps the unused DIN lead defined in topology A'))

    s.text('XH headers (JST XH 2.50 mm) - radar, touch board', 208.28, 25.4, size=2.0, bold=True)
    s.comp('J5', 'Connector_Generic:Conn_01x04', 'B4B-XH-A radar', (238.76, 53.34),
           nets={'1': '5V_RADAR', '2': 'GND', '3': 'LD_TX', '4': 'PI_TXD'},
           footprint='Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical',
           fields=F('B4B-XH-A', 'JST', '455-B4B-XH-A-ND', note='LD2410C: 1 VCC(5V) 2 GND 3 LD TX 4 LD RX'))
    s.comp('R19', 'Device:R', '4.7k', (284.48, 53.34), rot=90, nets={'1': 'LD_TX', '2': 'PI_RXD'}, footprint=R0603,
           fields=F(spec='4.7 kOhm 1% 0603', note='radar TX -> Pi RXD: limits back-feed into an unpowered Pi to 0.64 mA'))
    s.comp('J6', 'Connector_Generic:Conn_01x04', 'B4B-XH-A touch', (238.76, 88.9),
           nets={'1': '3V3_SENS', '2': 'GND', '3': 'I2C_SDA', '4': 'I2C_SCL'},
           footprint='Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical',
           fields=F('B4B-XH-A', 'JST', '455-B4B-XH-A-ND', note='touch board (hardware/touch-board) HOST pads: VCC GND SDA SCL'))
    hdr = 'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical'
    for ref, what, y in (('J10', 'BME680', 76.2), ('J11', 'VEML6030', 101.6)):
        s.comp(ref, 'Connector_Generic:Conn_01x04', '1x04 header ' + what, (330.2, y),
               nets={'1': '3V3_SENS', '2': 'GND', '3': 'I2C_SDA', '4': 'I2C_SCL'}, footprint=hdr,
               fields=F(spec='1 x 4 male pin header, 2.54 mm, straight', note=what + ' lead: 1 x 4 Dupont housing, pin 1 = 3V3 '
                        '(rev 3: the shared 2 x 4 header of rev 2.1 split, one header where each lead arrives)'))

    s.text('Echo-reference (D4a) - default topology A: all links OPEN', 208.28, 116.84, size=2.0, bold=True)
    s.comp('J7', 'Connector_Generic:Conn_01x08', 'D4a ReSpeaker tap', (238.76, 147.32),
           nets={'1': 'GND', '2': 'RS_BCLK', '3': 'RS_LRCLK', '4': 'RS_REF', '5': 'RS_OUT', '6': 'GND', '7': 'RS_SDA', '8': 'RS_SCL'},
           footprint='ha_panel:WirePads_1x08_P2.54mm_D1.0mm', in_bom=False,
           fields=F(note='wire pads (leads soldered, topology B only) to ReSpeaker XIAO footprint: 2=I2S_BCLK 3=I2S_LRCLK 4=I2S_DIN_SEC(dout) 5=I2S_DIN_XIAO(din) 7=SDA 8=SCL'))
    links = [('R20', 'I2S_BCLK', 'RS_BCLK'), ('R21', 'I2S_LRCLK', 'RS_LRCLK'), ('R22', 'I2S_DOUT', 'RS_REF'),
             ('R23', 'PI_DIN', 'RS_OUT'), ('R24', 'I2C_SDA', 'RS_SDA'), ('R25', 'I2C_SCL', 'RS_SCL')]
    for i, (ref, a, b) in enumerate(links):
        s.comp(ref, 'Device:R', '0R DNP', (284.48, 139.7 + i * 12.7), rot=90, nets={'1': a, '2': b}, footprint=R0603, dnp=True,
               fields=F(spec='0 Ohm 0603', note='D4a link: fit for topology B (I2S reference, XU316 master)'))
    tp(s, 'TP17', 'GND', 152.4, 38.1, 'GND')
    for i, ref in enumerate(('H1', 'H2', 'H3', 'H4')):
        s.comp(ref, 'Mechanical:MountingHole', 'M3 x 8', (330.2 + i * 12.7, 38.1), footprint='ha_panel:MountingHole_3.2mm_M3_Post',
               in_bom=False, fields=F(note='dia 3.2 NPTH for the unit standard M3 x 8 button head into a Ruthex M3 in the carrier '
                                           'post; clear dia 7 on the door side (head), dia 9 on the back face (post) - site section 2'))
    s.text('\n'.join([
        'V17: Raspberry Pi publishes no current rating for the Pi 5 header 3V3 pins -> 3.3 V LDO on this board (brief item 4).',
        '  U2 TPS70933: 2.7-30 V in (survives the NID OVP 6.4-7.5 V), 150 mA, EN follows the Pi 3V3 (pin 1 lead, ~33 uA).',
        '  Loads: TAS5756M DVDD/AVDD/CPVDD 35 mA (SLAS988B 7.12) + touch/BME680/VEML6030 via F4.',
        '  STANDBY (Pi 3V3 off, 5 V on, HAT+ spec 2.2): LDO off -> no back-feed through I2C; amp muted by R17.',
        'R26/R27: amp logic rail 3V3_AMP from the LDO (default, R26) or from the Pi 3V3 (R27): TAS5756M VIH = 0.9 x DVDD',
        '  (SLAS988B 7.3) and TI advises driving its inputs from the DVDD supply; LDO +-1 % (SBVS186H) vs Pi 3V3 (not published).',
        'Pi pins: 3/5 SDA/SCL (GPIO2/3, 1.8 k pull-ups on the Pi); 8/10 TXD/RXD (GPIO14/15, uart0);',
        '  12/35/38/40 = GPIO18/19/20/21 I2S BCLK/LRCLK/DIN/DOUT; 15 = GPIO22 amp mute (rpi-digiampplus).',
        'I2C map: AT42QT1070 0x1B, VEML6030 0x48, TAS5756M 0x4C, BME680 0x76/0x77 (ReSpeaker 0x42/0x18 only if R24/R25 fitted).',
        'Sensor branch 3V3_SENS (F4 0.2 A PTC): J6 touch board, J10 BME680, J11 VEML6030 (one 1 x 4 header each, rev 3).',
        'Topology B (bench 2.2): fit R20-R23 (+R24/R25 for XU316 I2C), jumper J7 to the ReSpeaker XIAO footprint, I2S firmware.']),
        25.4, 190.5)

    # =================================================================== AMPLIFIER
    s = s_amp
    s.text('TAS5756M stereo BTL (TI SLAS988B Fig. 79 / Table 22; DigiAMP+ wiring for the rpi-digiampplus overlay)', 25.4, 20.32,
           size=2.0, bold=True)
    s.comp('F5', 'Device:Polyfuse', '2.6 A 2920L260/33DR', (50.8, 45.72), rot=90, nets={'1': '+20V', '2': 'PVDD'},
           footprint='Fuse:Fuse_2920_7451Metric',
           fields=F('2920L260/33DR', 'Littelfuse', '18-2920L260/33DRCT-ND', 'PTC 2.6 A hold (1.81 A at 60 C), 33 V, R1max 75 mOhm'))
    s.pwr_flag('PVDD', (66.04, 60.96))
    s.text('PVDD probe point: F5 pin 2 (2920 land, door-side face). No TP18.',
           88.9, 38.1, size=1.27)
    # PVDD decoupling (left side pins 6/7 and right side 41-43)
    for i, (ref, val, fp, spec) in enumerate([('C100', '0.1u 50V', C0603, '0.1 uF 50 V X7R 0603'),
                                              ('C101', '22u 35V', C0805, '22 uF 35 V X5R 0805'),
                                              ('C102', '22u 35V', C0805, '22 uF 35 V X5R 0805'),
                                              ('C121', '0.1u 50V', C0603, '0.1 uF 50 V X7R 0603'),
                                              ('C122', '22u 35V', C0805, '22 uF 35 V X5R 0805'),
                                              ('C123', '22u 35V', C0805, '22 uF 35 V X5R 0805')]):
        mpn = ('GMC21X5R226M35NT', 'Cal-Chip', '4713-GMC21X5R226M35NTCT-ND') if val.startswith('22u') else ('', '', '')
        s.comp(ref, 'Device:C', val, (101.6 + i * 12.7, 53.34), nets={'1': 'PVDD', '2': 'GND'}, footprint=fp,
               fields=F(mpn[0], mpn[1], mpn[2], spec, 'PVDD pins 6/7 (C100-C102) and 41-43 (C121-C123): place at the pins'))
    s.comp('U100', 'ha_panel:TAS5756M', 'TAS5756MDCAR', (190.5, 129.54),
           nets={'23': 'I2S_BCLK', '25': 'I2S_LRCLK', '24': 'I2S_DOUT', '22': 'GND',
                 '16': 'I2C_SDA', '17': 'I2C_SCL', '26': 'GND', '20': 'GND',
                 '18': 'AMP_GPIO0', '19': 'AMP_GPIO1', '21': 'AMP_GPIO2',
                 '27': 'AMP_MUTE_N', '40': 'AMP_FAULT_N',
                 '30': '3V3_AMP', '31': '3V3_AMP', '14': '3V3_AMP', '28': 'DVDD_REG', '32': 'CP', '34': 'CN', '35': 'CPVSS',
                 '6': 'PVDD', '7': 'PVDD', '41': 'PVDD', '42': 'PVDD', '43': 'PVDD',
                 '8': 'GVDD', '9': 'SPK_GAIN',
                 '5': 'BST_AP', '4': 'OUT_AP', '2': 'OUT_AN', '1': 'BST_AN',
                 '44': 'BST_BP', '45': 'OUT_BP', '47': 'OUT_BN', '48': 'BST_BN',
                 '13': 'DAC_A', '12': 'INA_P', '11': 'INA_N', '36': 'DAC_B', '37': 'INB_P', '38': 'INB_N',
                 '10': 'GND', '15': 'GND', '29': 'GND', '33': 'GND', '3': 'GND', '39': 'GND', '46': 'GND', '49': 'GND'},
           footprint='ha_panel:TI_DCA0048A_HTSSOP-48-1EP',
           fields=F('TAS5756MDCAR', 'Texas Instruments', '296-40565-1-ND', note='I2C 0x4C (ADR1=ADR0=0); MCLK tied low, PLL from SCLK'))
    # gain / frequency divider + GVDD
    s.comp('C103', 'Device:C', '1u 50V', (264.16, 76.2), nets={'1': 'GVDD', '2': 'GND'}, footprint=C0603,
           fields=F('UMK107AB7105KA-T', 'Taiyo Yuden', '587-3247-1-ND', '1 uF 50 V X7R 0603', 'GVDD_REG (>16 V)'))
    s.comp('R101', 'Device:R', '150k 1%', (297.18, 76.2), rot=90, nets={'1': 'GVDD', '2': 'SPK_GAIN'}, footprint=R0603,
           fields=F(spec='150 kOhm 1% 0603', note='to GVDD_REG'))
    s.comp('R100', 'Device:R', '100k 1%', (325.12, 88.9), nets={'1': 'SPK_GAIN', '2': 'GND'}, footprint=R0603,
           fields=F(spec='100 kOhm 1% 0603', note='to GND: 20 dBV, 8 x fSYNC (Table 15)'))
    # bootstrap
    for i, (ref, a, b) in enumerate([('C104', 'BST_AP', 'OUT_AP'), ('C108', 'BST_AN', 'OUT_AN'),
                                     ('C115', 'BST_BP', 'OUT_BP'), ('C111', 'BST_BN', 'OUT_BN')]):
        s.comp(ref, 'Device:C', '0.22u 50V', (317.5, 116.84 + i * 12.7), rot=90, nets={'1': a, '2': b}, footprint=C0603,
               fields=F('CL10B224KB8NNNC', 'Samsung', '1276-CL10B224KB8NNNCCT-ND', '0.22 uF 50 V X7R 0603', 'bootstrap'))
    # LC filters (type 2: L in each leg, C to GND)
    lc = [('L100', 'C109', 'OUT_AP', 'SPK_L_P', 233.68, 182.88), ('L101', 'C110', 'OUT_AN', 'SPK_L_N', 233.68, 213.36),
          ('L103', 'C117', 'OUT_BP', 'SPK_R_P', 309.88, 182.88), ('L102', 'C116', 'OUT_BN', 'SPK_R_N', 309.88, 213.36)]
    for lref, cref, a, b, x, y in lc:
        s.comp(lref, 'Device:L', '10u', (x, y), rot=90, nets={'1': a, '2': b},
               footprint='ha_panel:L_Codaca_CSBA0850',
               fields=F('CSBA0850-100M', 'CODACA', '4044-CSBA0850-100MCT-ND',
                        '10 uH +-20 %, Isat 3.50 A (L -10 %) / 8.00 A (L -30 %), DCR 31.6 mOhm max, Irms 5.60 A, 8.7 x 8.5 x 5.1',
                        'LC output filter (CODACA CSBA0850 datasheet, revised 2026-03-16)'))
        s.comp(cref, 'Device:C', '0.68u 50V', (x + 22.86, y + 7.62), nets={'1': b, '2': 'GND'}, footprint=C0805,
               fields=F('CL21B684KBFVPNE', 'Samsung', '1276-7009-1-ND', '0.68 uF 50 V X7R 0805', 'LC filter C to GND (>1.8 x PVDD)'))
    s.comp('J8', 'Connector_Generic:Conn_01x02', 'B2B-XH-A speaker L', (294.64, 190.5),
           nets={'1': 'SPK_L_P', '2': 'SPK_L_N'}, footprint='Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical',
           fields=F('B2B-XH-A', 'JST', '455-B2B-XH-A-ND', note='speaker L (+x side, viewer left) - channel A'))
    s.comp('J9', 'Connector_Generic:Conn_01x02', 'B2B-XH-A speaker R', (370.84, 190.5),
           nets={'1': 'SPK_R_P', '2': 'SPK_R_N'}, footprint='Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical',
           fields=F('B2B-XH-A', 'JST', '455-B2B-XH-A-ND', note='speaker R (-x side) - channel B'))
    # DAC -> speaker input coupling
    for i, (ref, a, b) in enumerate([('C106', 'DAC_A', 'INA_P'), ('C113', 'DAC_B', 'INB_P')]):
        s.comp(ref, 'Device:C', '2.2u 25V', (165.1, 195.58 + i * 22.86), rot=90, nets={'1': a, '2': b}, footprint=C0603,
               fields=F(spec='2.2 uF 25 V X7R 0603', note='DAC_OUT -> SPK_IN+ coupling (Fig. 79)'))
    for i, (ref, a) in enumerate([('C107', 'INA_N'), ('C114', 'INB_N')]):
        s.comp(ref, 'Device:C', '2.2u 25V', (198.12, 195.58 + i * 22.86), nets={'1': a, '2': 'GND'}, footprint=C0603,
               fields=F(spec='2.2 uF 25 V X7R 0603', note='SPK_IN- to GND (Fig. 79)'))
    # low-voltage supplies
    lv = [('C105', '3V3_AMP', 'AVDD'), ('C119', '3V3_AMP', 'DVDD/CPVDD'), ('C118', 'DVDD_REG', 'DVDD_REG'), ('C120', 'CPVSS', 'CPVSS')]
    for i, (ref, net, what) in enumerate(lv):
        s.comp(ref, 'Device:C', '1u 25V', (38.1 + i * 12.7, 160.02), nets={'1': net, '2': 'GND'}, footprint=C0603,
               fields=F(spec='1 uF 25 V X7R 0603', note=what + ' (Table 22: 1 uF X5R 6.3 V min)'))
    s.comp('C112', 'Device:C', '1u 25V', (63.5, 190.5), rot=90, nets={'1': 'CP', '2': 'CN'}, footprint=C0603,
           fields=F(spec='1 uF 25 V X7R 0603', note='charge-pump flying cap CP-CN (Fig. 79)'))
    # control pins
    s.comp('R102', 'Device:R', '100k', (38.1, 106.68), nets={'1': '3V3_AMP', '2': 'AMP_FAULT_N'}, footprint=R0603,
           fields=F(spec='100 kOhm 1% 0603', note='SPK_FAULT pull-up (VOL spec uses 100 k)'))
    for i, (ref, net) in enumerate([('R103', 'AMP_GPIO0'), ('R104', 'AMP_GPIO1'), ('R105', 'AMP_GPIO2')]):
        s.comp(ref, 'Device:R', '100k', (55.88 + i * 12.7, 106.68), nets={'1': net, '2': 'GND'}, footprint=R0603,
               fields=F(spec='100 kOhm 1% 0603', note='unused GPIO held low'))
    tp(s, 'TP19', 'AMP_FAULT_N', 25.4, 106.68, 'FAULT')
    tp(s, 'TP20', 'GND', 101.6, 38.1, 'GND')
    s.text('\n'.join([
        'Gain/switching: SPK_GAIN = GVDD_REG x 100k/250k = 2.8 V at GVDD 7.0 V -> 20 dBV, 8 x fSYNC = 768 kHz @48 kHz (Table 15,',
        '  window 2.33-3.10 V holds for GVDD 5.83-7.75 V). D22: software ceiling -4.0 dBFS keeps 10 W into 4 Ohm.',
        'LC: type 2 (L per leg, C to GND) as Fig. 79 and SLAA701B 1.3.2 for BD modulation; 10 uH + 0.68 uF: f0 61 kHz,',
        '  Q 0.52 at 4 Ohm (-0.8 dB at 20 kHz). Power budget cited SLAA701B 1.3.4.1 = type 1 (differential C) - corrected.',
        'CSBA0850-100M: Isat 3.50 A (L -10 %) vs normal peak 2.6 A (10 W/4 Ohm 2.24 A + 0.33 A ripple at 768 kHz); at the 7.5 A',
        '  OCE L >= 7 uH (-30 % at 8.00 A) vs 4.7 uH nominal / 1 uH min under short circuit (SLAS988B 7.3; CODACA 2026-03-16).',
        'Caps: TI Table 22 values; 0402 parts moved to 0603 (hand assembly D42). PVDD caps > 1.45 x PVDD, LC caps > 1.8 x PVDD.',
        'Overlay rpi-digiampplus: pcm5122@4c on i2c1, i2s_clk_producer, mute-gpios GPIO22 active high (driver sets 1 = unmute).',
        'Thermal pad: via array + paste windows 70-80 % of the pad area (SLAS988B 11.1.3.2) - footprint in block 2.',
        'No PVDD electrolytic at the amp (block 2, layout density): TI Table 22 says the 390 uF bulk "can be reduced or even removed";',
        '  C5 (120 uF on +20V) feeds PVDD through F5 (75 mOhm max, tau 9 us), plus 4 x 22 uF + 2 x 0.1 uF at the PVDD pins.']),
        25.4, 243.84)


def build(out):
    # block 3 (2026-11-08): purchase fields (MPN, Manufacturer, DigiKey; U2 value) chosen in the DigiKey BOM
    import json
    kg.EXTRA_FIELDS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bom_fields_main.json')))
    # pass 1: discover nets per sheet
    lib_path = os.path.join(out, 'lib', 'ha_panel.kicad_sym')
    lib_ha_panel.build(lib_path, which=('tas', 'tps1663', 'nid', 'tps709', '+20V'))
    p1 = kg.Project('main-board', '/tmp/mb_pass1', 'HA panel main board', DATE, REV, 'HA panel (neocleous/ha-panel)')
    design(p1)
    seen = {}
    for sh in p1.sheets:
        for n in sh.nets_used:
            seen.setdefault(n, set()).add(sh.filename)
    glob = {n for n, v in seen.items() if len(v) > 1}
    prj = kg.Project('main-board', out, 'HA panel main board', DATE, REV, 'HA panel (neocleous/ha-panel)',
                     comments=['KiCad 9.0.9 - generated by hardware/main-board/gen',
                               'Rev 3: brief claude/brief-electronics-step2-2026-11-10.md, site claude/main-board-site-2026-11-10.md issue 2',
                               'Board 87.0 x 57.9 x 1.6, 4 x dia 3.2 for M3 x 8, every part on the door-side face'])
    prj.global_nets = glob
    design(prj)
    prj.root.text('HA panel main board - schematic index\n'
                  'Sheet 2: 20 V inlet, fuse, TPS16630 eFuse, bus TVS\n'
                  'Sheet 3: NID100-5 5 V supply, Pi USB-C output, radar 5 V\n'
                  'Sheet 4: 3.3 V LDO, Pi signal leads, radar/touch XH, BME680 and VEML6030 headers, D4a echo-reference links\n'
                  'Sheet 5: TAS5756M amplifier and speaker outputs', 25.4, 20.32, size=1.8)
    prj.write()
    prj.write_project_files(
        sym_libs=[('ha_panel', 'lib/ha_panel.kicad_sym', 'HA panel custom symbols')],
        fp_libs=[('ha_panel', 'lib/ha_panel.pretty', 'HA panel custom footprints (block 2)')])
    pretty = os.path.join(out, 'lib', 'ha_panel.pretty')
    os.makedirs(pretty, exist_ok=True)
    for k in ('tas', 'nid', 'csba', 'wirelink', 'wp2x5', 'wp2x2', 'wp1x8', 'm3post'):
        footprints.ALL[k](pretty)
    with open(os.path.join(pretty, 'README.md'), 'w') as f:
        f.write('# ha_panel footprints\n\nDrawn in block 2 from the datasheets (gen/footprints.py): '
                'TI_DCA0048A_HTSSOP-48-1EP (TAS5756M, SLAS988B package addendum + via array + paste windows), '
                'MeanWell_NID100_SIP-13 (NID100-SPEC 2024-10-30), L_Codaca_CSBA0850 (CODACA 2026-03-16).\n\n'
                'Rev 3 (2026-11-11): WirePads_2x05 / 2x02 / 1x08_P2.54mm_D1.0mm (wire landings, pads only, same pad numbering '
                'as the KiCad pin headers) and MountingHole_3.2mm_M3_Post (dia 3.2 NPTH, courtyard dia 7 = screw-head zone).\n')
    return prj, seen


if __name__ == '__main__':
    prj, seen = build(OUT)
    print('global nets:', sorted(n for n, v in seen.items() if len(v) > 1))
