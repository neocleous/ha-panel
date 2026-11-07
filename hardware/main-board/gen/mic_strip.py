"""HA panel mic strip (one design, two boards) - schematic (KiCad 9). Run: python3 mic_strip.py <outdir>"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kicadgen as kg
import lib_ha_panel

OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/work/out/mic-strip'
DATE = '2026-11-07'
R0603 = 'Resistor_SMD:R_0603_1608Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'
TP_SMD = 'TestPoint:TestPoint_Pad_D1.0mm'


def F(mpn='', mfr='', dk='', spec='', note=''):
    d = {}
    if mpn: d['MPN'] = mpn
    if mfr: d['Manufacturer'] = mfr
    if dk: d['DigiKey'] = dk
    if spec: d['Spec'] = spec
    if note: d['Note'] = note
    return d


def design(prj):
    s = prj.root
    s.text('MIC STRIP  (MSM261DHP006 PDM mic, one design for both strips; cable to the ReSpeaker Lite vacated U4/U5 pads)',
           20.32, 15.24, size=1.8, bold=True)
    # cable connector
    s.comp('J1', 'Connector_Generic_MountingPin:Conn_01x05_MountingPin', 'BM05B-SRSS-TB', (40.64, 66.04),
           nets={'1': 'VDD_C', '2': 'GND', '3': 'CLK_C', '4': 'SEL_C', '5': 'DATA_C', 'MP': 'GND'},
           footprint='Connector_JST:JST_SH_BM05B-SRSS-TB_1x05-1MP_P1.00mm_Vertical',
           fields=F('BM05B-SRSS-TB', 'JST', note='cable A05SR05SR30K305B cut at the ReSpeaker end: 1 VDD->pad 1, 2 GND->pad 4/6, '
                                                '3 CLK->pad 2, 4 SEL->pad 5 (L/R strap), 5 DATA->pad 3'))
    # ESD at the connector
    for i, (ref, net) in enumerate((('D1', 'VDD_C'), ('D2', 'CLK_C'), ('D3', 'DATA_C'))):
        s.comp(ref, 'Power_Protection:TPD1E05U06DYA', 'TPD1E05U06', (63.5 + i * 22.86, 86.36),
               nets={'1': net, '2': 'GND'}, footprint='Diode_SMD:D_SOD-523',
               fields=F('TPD1E05U06DYAR', 'Texas Instruments', spec='ESD 5.5 V VRWM, 0.42 pF (DYA), SOD-523',
                        note='at the connector (datasheet 4-1 note 2); SOD-523 instead of the X1SON DPY for hand assembly'))
    # supply RC
    s.comp('R1', 'Device:R', '100R', (101.6, 45.72), rot=90, nets={'1': 'VDD_C', '2': 'VDD_MIC'}, footprint=R0603,
           fields=F(spec='100 Ohm 1% 0603', note='VDD RC filter with C1: fc 159 Hz; drop 0.1 V at 0.67 mA mic + buffer'))
    s.comp('C1', 'Device:C', '10u 10V', (121.92, 53.34), nets={'1': 'VDD_MIC', '2': 'GND'}, footprint=C0603,
           fields=F(spec='10 uF 10 V X5R 0603', note='mic decoupling (E0-D6), at the mic VDD pin'))
    s.comp('C2', 'Device:C', '100n 50V', (137.16, 53.34), nets={'1': 'VDD_MIC', '2': 'GND'}, footprint=C0603,
           fields=F(spec='100 nF 50 V X7R 0603', note='mic decoupling, closest to the VDD pin'))
    s.pwr_flag('VDD_C', (50.8, 38.1))
    s.pwr_flag('VDD_MIC', (147.32, 38.1))
    s.pwr_flag('GND', (63.5, 38.1))
    # clock buffer + bypass + pull-down
    s.comp('R2', 'Device:R', '100k', (76.2, 124.46), nets={'1': 'CLK_C', '2': 'GND'}, footprint=R0603,
           fields=F(spec='100 kOhm 1% 0603', note='weak pull-down on the buffer input (CLK tri-stated when muted - inference)'))
    s.comp('U1', '74xGxx:74LVC1G17', 'SN74LVC1G17DCKR', (134.62, 116.84), ref_pos=(139.7, 104.14),
           value_pos=(139.7, 106.68),
           nets={'2': 'CLK_C', '4': 'CLK_MIC', '3': 'GND', '5': 'VDD_MIC'},
           footprint='Package_TO_SOT_SMD:SOT-353_SC-70-5',
           fields=F('SN74LVC1G17DCKR', 'Texas Instruments', '296-11934-1-ND', 'Schmitt buffer, SC-70-5 (DCK)',
                    'fitted by default: re-drives CLK next to the mic (bench 2.4 designed out)'))
    s.comp('C3', 'Device:C', '100n 50V', (165.1, 109.22), nets={'1': 'VDD_MIC', '2': 'GND'}, footprint=C0603,
           fields=F(spec='100 nF 50 V X7R 0603', note='buffer VCC decoupling'))
    s.comp('R3', 'Device:R', '0R DNP', (134.62, 142.24), rot=90, nets={'1': 'CLK_C', '2': 'CLK_MIC'}, footprint=R0603, dnp=True,
           fields=F(spec='0 Ohm 0603', note='buffer bypass: fit R3 only with U1 removed (bench 2.5 lever)'))
    # mic
    s.comp('MK1', 'ha_panel:MSM261DHP006', 'MSM261DHP006', (177.8, 76.2),
           nets={'1': 'VDD_MIC', '2': 'MIC_LR', '3': 'CLK_MIC', '4': 'DATA_MIC', '5': 'GND', '6': 'GND', '7': 'GND', '8': 'GND'},
           footprint='ha_panel:MEMSensing_MSM261DHP006_LGA-8_4x3mm',
           fields=F('MSM261DHP006', 'MEMSensing', note='LCSC C22390138, shipped with the boards (not at DigiKey); '
                                                      'bottom port through the board to the cap port'))
    s.comp('R4', 'Device:R', '33R', (215.9, 83.82), rot=90, nets={'1': 'DATA_MIC', '2': 'DATA_C'}, footprint=R0603,
           fields=F(spec='33 Ohm 1% 0603', note='DATA source termination (100 Ohm alternative, bench 2.5 lever)'))
    # L/R select
    s.comp('R5', 'Device:R', '0R', (215.9, 116.84), rot=90, nets={'1': 'SEL_C', '2': 'MIC_LR'}, footprint=R0603,
           fields=F(spec='0 Ohm 0603', note='L/R from the cable (ReSpeaker pad 5 strap); remove to use JP1'))
    s.comp('JP1', 'Jumper:SolderJumper_3_Open', 'L/R GND-VDD', (190.5, 129.54),
           nets={'1': 'GND', '2': 'MIC_LR', '3': 'VDD_MIC'}, footprint='Jumper:SolderJumper-3_P1.3mm_Open_RoundedPad1.0x1.5mm',
           in_bom=False, fields=F(note='local L/R strap: bridge 1-2 = GND (L), 2-3 = VDD (R); only with R5 removed'))
    # test pads
    for i, (ref, net, lab) in enumerate((('TP1', 'CLK_MIC', 'CLK'), ('TP2', 'DATA_MIC', 'DATA'), ('TP3', 'VDD_MIC', 'VDD'),
                                         ('TP4', 'GND', 'GND'))):
        s.comp(ref, 'Connector:TestPoint', lab, (220.98 + i * 12.7, 38.1), nets={'1': net}, footprint=TP_SMD, in_bom=False,
               fields=F(note='test pad (bench 2.4/2.5: CLK edge and DATA at the mic, if a scope is borrowed)'))
    s.text('\n'.join([
        'MSM261DHP006 (MEMSensing DS-042 Ver.1.1): VDD 1.6-3.6 V, IDD 670 uA at 2.4 MHz, VIH 0.7 VDD, VIL 0.3 VDD,',
        '  clock 1.1-4.8 MHz, edge <= 20 ns; L/R = GND -> DATA valid on CLK falling edge.',
        'Cable (JST SR 1.0, A05SR05SR30K305B, cut >= 175 mm): 1 VDD, 2 GND, 3 CLK, 4 SEL, 5 DATA - SEL is static,',
        '  so it separates CLK from DATA like a ground. Default: U1 fitted, R3 open, R4 33 Ohm, R5 0 Ohm, JP1 open.',
        'Levers (bench 2.5): R3 bypass with U1 removed; R4 100 Ohm; R5 out + JP1 if the cable SEL is not wanted.',
        'Passives 0603 (D42); ESD in SOD-523 (D42: leaded alternative to the X1SON); MK1 LGA accepted as is.']),
        20.32, 160.02)


def build(out):
    lib_path = os.path.join(out, 'lib', 'ha_panel.kicad_sym')
    lib_ha_panel.build(lib_path, which=('msm',))
    prj = kg.Project('mic-strip', out, 'HA panel mic strip', DATE, '1', 'HA panel (neocleous/ha-panel)',
                     comments=['KiCad 9.0.9 - generated by hardware/main-board/gen/mic_strip.py (checkpoint 1)',
                               'Brief claude/brief-electronics-design-2026-11-07.md, K21, E0-D6',
                               'Two boards of this design: L and R set by the cable SEL wire'])
    prj.root.paper = 'A4'
    design(prj)
    prj.write()
    prj.write_project_files(
        sym_libs=[('ha_panel', 'lib/ha_panel.kicad_sym', 'HA panel custom symbols')],
        fp_libs=[('ha_panel', 'lib/ha_panel.pretty', 'HA panel custom footprints (block 2)')])
    pretty = os.path.join(out, 'lib', 'ha_panel.pretty')
    os.makedirs(pretty, exist_ok=True)
    with open(os.path.join(pretty, 'README.md'), 'w') as f:
        f.write('# ha_panel footprints\n\nCreated in block 2 (layout): MEMSensing_MSM261DHP006_LGA-8_4x3mm '
                '(from the Voice PE footprint Misc:MIC8P-0.85-4X3X1MM, risk review R5).\n')
    return prj


if __name__ == '__main__':
    build(OUT)
