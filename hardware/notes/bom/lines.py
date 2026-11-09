# BOM lines for block 3 part 2: (key, refs, spec, need, buy, candidates or known DigiKey PN)
# need = parts on 1 main board + 2 strips; buy = need + spares. Spares rule (Daniel 2026-11-08): >= 3 for 0603 and smaller
# (SC-70 and SOD-523 included), >= 2 for 0805/1206 and the MEMS mic, 1 for larger parts and ICs; the next price break
# is taken where it costs <= CHF 0.40 more. L1 and C5/C6 have none (large, robust).
LINES = [
 # --- main board ---
 ('C_1u50_0805',  'C1, C10',                    '1 µF 50 V X7R 0805',                 2, 4,  ['GRM21BR71H105KA12L','C2012X7R1H105K125AB','C0805C105K5RACTU','UMK212B7105KG-T']),
 ('C_100n50_0603','C2, C4, C9, C100, C121; strip C2, C3 ×2; touch C1', '100 nF 50 V X7R 0603', 10, 14, ['CC0603KRX7R9BB104']),
 ('C_47n50_0603', 'C3',                         '47 nF 50 V X7R 0603',                1, 10,  ['CL10B473KB8NNNC']),
 ('C_120u63',     'C5, C6',                     '120 µF 63 V radial Ø10 (EEU-FR1J121B)', 2, 2, ['P15289CT-ND']),
 ('C_22u35_THT',  'C7',                         '22 µF 35 V radial Ø5 (860160572003)', 1, 2, ['732-9541-1-ND']),
 ('C_10u25_1206', 'C8, C11',                    '10 µF 25 V X7R 1206',                2, 4,  ['GRM31CR71E106KA12L','C3216X7R1E106K160AB','C1206C106K3RACTU','TMK316B7106KL-TD']),
 ('C_4u7_16_0805','C12',                        '4.7 µF 16 V X7R 0805',               1, 3,  ['CL21B475KOFNNNE','CC0805KKX7R7BB475','GRM21BR71C475KA73L','C2012X7R1C475K125AC']),
 ('C_22u35_0805', 'C101, C102, C122, C123',     '22 µF 35 V X5R 0805 (GMC21X5R226M35NT)', 4, 6, ['4713-GMC21X5R226M35NTCT-ND']),
 ('C_1u50_0603',  'C103',                       '1 µF 50 V X7R 0603 (UMK107AB7105KA-T)', 1, 10, ['587-3247-1-ND']),
 ('C_220n50_0603','C104, C108, C111, C115',     '0.22 µF 50 V X7R 0603 (CL10B224KB8NNNC)', 4, 6, ['1276-CL10B224KB8NNNCCT-ND']),
 ('C_1u25_0603',  'C105, C112, C118, C119, C120','1 µF 25 V X7R 0603',                5, 8,  ['CL10B105KA8NNNC','CC0603KRX7R8BB105','GRM188R71E105KA12D','C1608X7R1E105K080AB']),
 ('C_2u2_25_0603','C106, C107, C113, C114',     '2.2 µF 25 V X7R 0603',               4, 6,  ['CL10B225KA8VPNC','CC0603KRX7R8BB225','GRM188R71E225KA12D','C1608X7R1E225K080AC','TMK107BB7225KA-T']),
 ('C_680n50_0805','C109, C110, C116, C117',     '0.68 µF 50 V X7R 0805 (CL21B684KBFVPNE)', 4, 6, ['1276-7009-1-ND']),
 ('D_SMBJ22A',    'D1',                         'TVS 22 V SMB (SMBJ22A)',             1, 2,  ['SMBJ22ALFCT-ND']),
 ('D_SMBJ6',      'D2',                         'TVS 6.0 V SMB (SMBJ6.0A-E)',         1, 2,  ['18-SMBJ6.0A-ECT-ND']),
 ('F1',           'F1',                         'fuse 5 A NANO2 (0453005.MR)',        1, 2,  ['F3139CT-ND']),
 ('F2',           'F2',                         'fuse 10 A NANO2 (0453010.MR)',       1, 2,  ['F3141CT-ND']),
 ('F3',           'F3',                         'fuse 1 A NANO2 (0453001.MR)',        1, 2,  ['F3137CT-ND']),
 ('F4',           'F4',                         'PTC 0.2 A 1206 (0ZCJ0020FF2E)',      1, 5,  ['5923-0ZCJ0020FF2ECT-ND']),
 ('F5',           'F5',                         'PTC 2.6 A 2920 (2920L260/33DR)',     1, 2,  ['18-2920L260/33DRCT-ND']),
 ('J_XH2',        'J1, J8, J9',                 'JST B2B-XH-A',                       3, 4,  ['455-B2B-XH-A-ND']),
 ('J_XH4',        'J5, J6',                     'JST B4B-XH-A',                       2, 3,  ['455-B4B-XH-A-ND']),
 ('J2',           'J2',                         'GCT USB4085-GF-A USB-C THT',         1, 2,  ['USB4085-GF-A']),
 ('L1',           'L1',                         'Bourns SRR1260-150M 15 µH',          1, 1,  ['SRR1260-150MCT-ND']),
 ('L100',         'L100–L103',                  'CODACA CSBA0850-100M 10 µH',         4, 5,  ['4044-CSBA0850-100MCT-ND']),
 ('PS1',          'PS1',                        'Mean Well NID100-5',                 1, 1,  ['1866-NID100-5-ND']),
 ('R_412k',       'R1',                         '412 kΩ 1 % 0603',                    1, 2,  ['RC0603FR-07412KL']),
 ('R_9k09',       'R2',                         '9.09 kΩ 1 % 0603',                   1, 2,  ['RC0603FR-079K09L']),
 ('R_22k1',       'R3',                         '22.1 kΩ 1 % 0603',                   1, 2,  ['RC0603FR-0722K1L']),
 ('R_5k49',       'R4',                         '5.49 kΩ 1 % 0603',                   1, 2,  ['RC0603FR-075K49L']),
 ('R_10k',        'R5, R10, R11',               '10 kΩ 1 % 0603',                     3, 5,  ['RC0603FR-0710KL']),
 ('R_100k',       'R6, R13, R17, R18, R100, R102–R105; strip R2 ×2', '100 kΩ 1 % 0603', 11, 17, ['RC0603FR-07100KL']),
 ('R_0R',         'R7, R14–R16, R26; strip R5 ×2; options R20–R25, R27', '0 Ω 0603', 7, 20, ['RC0603JR-070RL']),
 ('R_2R2',        'R12',                        '2.2 Ω 1 % 0805',                     1, 2,  ['RC0805FR-072R2L']),
 ('R_4k7',        'R19; touch R1–R4',           '4.7 kΩ 1 % 0603',                    5, 10,  ['RC0603FR-074K7L']),
 ('R_150k',       'R101',                       '150 kΩ 1 % 0603',                    1, 2,  ['RC0603FR-07150KL']),
 ('U1',           'U1',                         'TI TPS16630PWPT eFuse',              1, 2,  ['296-TPS16630PWPTCT-ND']),
 ('U2',           'U2',                         'TI TPS70933DBVR LDO',                1, 2,  ['TPS70933DBVR']),
 ('U100',         'U100',                       'TI TAS5756MDCAR amplifier',          1, 2,  ['296-40565-1-ND']),
 # --- mic strip (×2) ---
 ('S_C10u',       'strip C1 ×2; touch C2',      '10 µF 10 V X5R 0603',                3, 10,  ['CL10A106KP8NNNC','CC0603MRX5R6BB106','GRM188R61A106KAALD','C1608X5R1A106K080AC']),
 ('S_TPD',        'strip D1–D3 ×2',             'TI TPD1E05U06DYAR ESD, SOD-523',     6, 9,  ['TPD1E05U06DYAR']),
 ('S_MK1',        'strip MK1 ×2',               'Infineon IM69D120V01XTSA1',          2, 4,  ['IM69D120V01XTSA1CT-ND']),
 ('S_U1',         'strip U1 ×2',                'TI SN74LVC1G17DCKR',                 2, 10,  ['296-11934-1-ND']),
 ('S_100R',       'strip R1 ×2 (+2 for the R4 100 Ω option)', '100 Ω 1 % 0603',      2, 5,  ['RC0603FR-07100RL']),
 ('S_33R',        'strip R4 ×2',                '33 Ω 1 % 0603',                      2, 3,  ['RC0603FR-0733RL']),
]

# --- harness (XH): each ASXHSXH22K305 wire (XH socket both ends, 305 mm) is cut in the middle -> two ~150 mm conductors.
# Conductors: J1 pigtail 2, J5 radar 4, J6 touch 4, J8/J9 speakers 2 each = 14 -> 7 wires; colours: DigiKey stocks black only.
HARNESS = [
 ('XH_wire', 'XH leads J1, J5, J6, J8, J9 (14 conductors)', 'JST crimped XH wire 22 AWG 305 mm, black', 7, 9, ['ASXHSXH22K305']),
 ('XHP2',    'J1, J8, J9 plugs',  'JST XHP-2 housing', 3, 4, ['XHP-2']),
 ('XHP4',    'J5, J6 plugs',      'JST XHP-4 housing', 2, 3, ['XHP-4']),
]
NONBOARD = [
 ('ReSpeaker', 'voice front end', 'Seeed ReSpeaker Lite 107990273', 1, 1, ['1597-107990273-ND']),
 ('SC1132',    'Pi 5 DSI cable 300 mm (2nd = spare, as AliExpress A1)', 'Raspberry Pi SC1132', 2, 2, ['2648-SC1132-ND']),
 ('AF266',     'GPIO leads (40 × F-F 152 mm)', 'Adafruit 266', 1, 1, ['1528-1379-ND']),
 ('AF1949',    'sensor leads and LD2410C bench (20 × F-F 305 mm)', 'Adafruit 1949', 1, 1, ['1528-1960-ND']),
 ('AF261',     'ReSpeaker speaker out → DMA45-4 (bench)', 'Adafruit 261 PH 2-pin 100 mm', 1, 1, ['1528-261-ND']),
]
SYSTEM = [
 ('PD5807',    '20 V PD sink at the inlet (D13; 2nd = spare, as rev 4)', 'Adafruit 5807 HUSB238', 2, 2, ['1528-5807-ND']),
 ('MICCABLE',  'mic strip → ReSpeaker leads (2 + 2 spare, as rev 4)', 'JST A05SR05SR30K305B 5-pos SR 305 mm', 4, 4, ['/en/products/detail/jst-sales-america-inc/A05SR05SR30K305B/6708516']),
]
