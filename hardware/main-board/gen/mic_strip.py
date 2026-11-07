"""HA panel mic strip (one design, two boards) - schematic (KiCad 9). Run: python3 mic_strip.py <outdir>"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kicadgen as kg
import lib_ha_panel
import footprints

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
    s.text('MIC STRIP  (IM69D120 bottom-port PDM mic, one design for both strips; cable to the ReSpeaker Lite vacated U4/U5 pads)',
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
    s.comp('MK1', 'ha_panel:IM69D120', 'IM69D120V01', (177.8, 76.2),
           nets={'1': 'DATA_MIC', '2': 'VDD_MIC', '3': 'CLK_MIC', '4': 'MIC_LR', '5': 'GND'},
           footprint='ha_panel:Infineon_IM69D120_PG-LLGA-5-1',
           fields=F('IM69D120V01XTSA1', 'Infineon', 'IM69D120V01XTSA1CT-ND',
                    '-26 dBFS +-1, SNR 69 dB(A) at 3.072 MHz, 2.9-3.3 MHz range, 980 uA typ', 
                    'decision 8.1; bottom port through the strip (PCB hole 0.8), mic on the inner side'))
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
        'IM69D120 (Infineon datasheet rev 1.0, 2017-12-20): VDD 1.62-3.6 V; 3.072 MHz lies in the 2.9-3.3 MHz operating range',
        '  (no mode-entry restriction; start-up 20 ms), clock duty 48-52 % at >= 2.9 MHz, rise/fall 13 ns; IDD 980 uA typ;',
        '  -26 dBFS, SNR 69 dB(A); ambient <= 70 C above VDD 3.0 V. SELECT has no stated internal pull: driven via R5 or JP1.',
        'Cable (JST SR 1.0, A05SR05SR30K305B, cut >= 175 mm): 1 VDD, 2 GND, 3 CLK, 4 SEL, 5 DATA - SEL is static,',
        '  so it separates CLK from DATA like a ground. Default: U1 fitted, R3 open, R4 33 Ohm, R5 0 Ohm, JP1 open.',
        'Levers (bench 2.5): R3 bypass with U1 removed; R4 100 Ohm; R5 out + JP1 if the cable SEL is not wanted.',
        'Passives 0603 (D42); ESD in SOD-523 (D42: leaded alternative to the X1SON); MK1 LGA (no leaded MEMS exists).',
        'Decision 8.1 (2026-11-07): SPH0641LU4H-1 dropped - it must not start in ultrasonic mode (3.072-4.8 MHz), where the XU316 runs.']),
        20.32, 160.02)


def build(out):
    lib_path = os.path.join(out, 'lib', 'ha_panel.kicad_sym')
    lib_ha_panel.build(lib_path, which=('im69',))
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
    footprints.ALL['im69'](pretty)
    with open(os.path.join(pretty, 'README.md'), 'w') as f:
        f.write('# ha_panel footprints\n\nInfineon_IM69D120_PG-LLGA-5-1: KiCad Sensor_Audio:Infineon_PG-LLGA-5-1 with pads '
                '0.45 x 0.76 per the IM69D120 datasheet rev 1.0 Fig. 12 (pin numbering checked against Fig. 11 bottom view).\n')
    return prj


if __name__ == '__main__':
    build(OUT)
