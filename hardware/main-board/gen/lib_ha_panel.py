"""Project symbol library 'ha_panel' (custom symbols drawn from the datasheets)."""
import copy
import kicadgen as kg
import symlib
from sexpr import Sym, find, findall

DS_TAS = 'https://www.ti.com/lit/ds/symlink/tas5756m.pdf'
DS_TPS1663 = 'https://www.ti.com/lit/ds/symlink/tps1663.pdf'
DS_NID = 'https://www.meanwell.com/Upload/PDF/NID100/NID100-SPEC.PDF'
DS_TPS709 = 'https://www.ti.com/lit/ds/symlink/tps709.pdf'
DS_MSM = 'https://www.lcsc.com/datasheet/C22390138.pdf'


def tas5756m():
    left = [('23', 'SCLK', 'input'), ('25', 'LRCK/FS', 'input'), ('24', 'SDIN', 'input'), ('22', 'MCLK', 'input'), None,
            ('16', 'SDA', 'bidirectional'), ('17', 'SCL', 'input'), ('26', 'ADR0', 'input'), ('20', 'ADR1', 'input'), None,
            ('18', 'GPIO0', 'bidirectional'), ('19', 'GPIO1', 'bidirectional'), ('21', 'GPIO2', 'bidirectional'), None,
            ('27', '~{SPK_MUTE}', 'input'), None, ('40', '~{SPK_FAULT}', 'open_collector'), None,
            ('30', 'DVDD', 'power_in'), ('31', 'CPVDD', 'power_in'), ('14', 'AVDD', 'power_in'),
            ('28', 'DVDD_REG', 'power_out'), None,
            ('32', 'CP', 'passive'), ('34', 'CN', 'passive'), ('35', 'CPVSS', 'power_out')]
    right = [('6', 'PVDD', 'power_in'), ('7', 'PVDD', 'power_in'), ('41', 'PVDD', 'power_in'), ('42', 'PVDD', 'power_in'),
             ('43', 'PVDD', 'power_in'), None,
             ('8', 'GVDD_REG', 'power_out'), ('9', 'SPK_GAIN/FREQ', 'input'), None,
             ('5', 'BSTRPA+', 'passive'), ('4', 'SPK_OUTA+', 'output'), ('2', 'SPK_OUTA-', 'output'), ('1', 'BSTRPA-', 'passive'), None,
             ('44', 'BSTRPB+', 'passive'), ('45', 'SPK_OUTB+', 'output'), ('47', 'SPK_OUTB-', 'output'), ('48', 'BSTRPB-', 'passive'), None,
             ('13', 'DAC_OUTA', 'output'), ('12', 'SPK_INA+', 'input'), ('11', 'SPK_INA-', 'input'), None,
             ('36', 'DAC_OUTB', 'output'), ('37', 'SPK_INB+', 'input'), ('38', 'SPK_INB-', 'input')]
    bottom = [('10', 'AGND', 'power_in'), ('15', 'AGND', 'power_in'), ('29', 'DGND', 'power_in'), ('33', 'GND', 'power_in'),
              ('3', 'PGND', 'power_in'), ('39', 'PGND', 'power_in'), ('46', 'PGND', 'power_in'), ('49', 'PAD', 'power_in')]
    return kg.box_symbol('TAS5756M', 'U', 'TAS5756M', 'ha_panel:TI_DCA0048A_HTSSOP-48-1EP', DS_TAS,
                         'Digital-input closed-loop class-D amplifier, 2x BTL, HTSSOP-48 PowerPAD (DCA)',
                         left=left, right=right, bottom=bottom, width=45.72)


def tps16630():
    left = [('1', 'IN', 'power_in'), ('2', 'IN', 'power_in'), ('3', 'IN', 'power_in'), ('6', 'P_IN', 'power_in'), None,
            ('7', 'UVLO', 'input'), ('8', 'OVP', 'input'), None, ('13', 'SHDN', 'input'), ('12', 'MODE', 'input'), None,
            ('4', 'NC', 'no_connect'), ('5', 'NC', 'no_connect'), ('17', 'NC', 'no_connect')]
    right = [('18', 'OUT', 'power_out'), ('19', 'OUT', 'passive'), ('20', 'OUT', 'passive'), None,
             ('16', 'PGOOD', 'open_collector'), None, ('15', '~{FLT}', 'open_collector'), ('14', 'IMON', 'output'), None,
             ('10', 'dVdT', 'passive'), ('11', 'ILIM', 'passive')]
    bottom = [('9', 'GND', 'power_in'), ('21', 'PAD', 'power_in')]
    return kg.box_symbol('TPS16630', 'U', 'TPS16630PWPT', 'Package_SO:HTSSOP-20-1EP_4.4x6.5mm_P0.65mm_EP3.4x6.5mm_Mask2.96x2.96mm_ThermalVias', DS_TPS1663,
                         '60 V 6 A eFuse, adjustable OVP cut-off, UVLO, current limit, dV/dt (HTSSOP-20 PWP)',
                         left=left, right=right, bottom=bottom, width=20.32)


def nid100():
    left = [('9', '+Vin', 'power_in'), ('10', '+Vin', 'power_in'), None, ('13', 'R.C.', 'input'), ('12', 'Trim', 'passive'),
            ('11', 'NC', 'no_connect')]
    right = [('1', '+Vout', 'power_out'), ('2', '+Vout', 'passive'), ('3', '+Vout', 'passive'), ('4', '+Vout', 'passive')]
    bottom = [('5', 'Com', 'power_in'), ('6', 'Com', 'power_in'), ('7', 'Com', 'power_in'), ('8', 'Com', 'power_in')]
    return kg.box_symbol('NID100-5', 'PS', 'NID100-5', 'ha_panel:MeanWell_NID100_SIP-13', DS_NID,
                         'Mean Well NID100-5 non-isolated DC-DC, 10.5-53 V in, 5 V 11 A out, SIP-13',
                         left=left, right=right, bottom=bottom, width=20.32)


def tps70933():
    left = [('1', 'IN', 'power_in'), ('3', 'EN', 'input'), ('4', 'NC', 'no_connect')]
    right = [('5', 'OUT', 'power_out')]
    bottom = [('2', 'GND', 'power_in')]
    return kg.box_symbol('TPS70933DBV', 'U', 'TPS70933DBVR', 'Package_TO_SOT_SMD:SOT-23-5', DS_TPS709,
                         '150 mA 30 V LDO, 3.3 V fixed, enable, SOT-23-5 (DBV)', left=left, right=right, bottom=bottom,
                         width=15.24)


def msm261():
    left = [('1', 'VDD', 'power_in'), ('2', 'L/R', 'input'), ('3', 'CLK', 'input')]
    right = [('4', 'DATA', 'tri_state')]
    bottom = [('5', 'GND', 'power_in'), ('6', 'GND', 'power_in'), ('7', 'GND', 'power_in'), ('8', 'GND', 'power_in')]
    return kg.box_symbol('MSM261DHP006', 'MK', 'MSM261DHP006', 'ha_panel:MEMSensing_MSM261DHP006_LGA-8_4x3mm', DS_MSM,
                         'Top-port PDM MEMS microphone, 1.6-3.6 V, LGA-8 4 x 3 x 1 mm', left=left, right=right,
                         bottom=bottom, width=15.24)


def touch_electrode():
    return kg.box_symbol('TouchElectrode', 'E', 'TouchElectrode', 'ha_panel:TouchElectrode_16x16mm_R2', '~',
                         'Self-capacitance touch electrode: F.Cu copper under the solder mask, via to the back',
                         left=[('1', 'E', 'passive')], width=7.62)


def power_20v():
    s = symlib.load('power:+5V')
    s = copy.deepcopy(s)
    s[1] = '+20V'
    for e in s:
        if isinstance(e, list) and e and e[0] == 'property':
            if e[1] == 'Value':
                e[2] = '+20V'
            elif e[1] == 'Description':
                e[2] = 'Power symbol creates a global label with name "+20V" (20 V bus after the eFuse)'
        if isinstance(e, list) and e and e[0] == 'symbol' and e[1].startswith('+5V_'):
            e[1] = '+20V' + e[1][3:]
            for p in findall(e, 'pin'):
                nm = find(p, 'name')
                nm[1] = '+20V'
    return s


def build(path, which=('tas', 'tps1663', 'nid', 'tps709', 'msm', '+20V')):
    syms = []
    table = {'tas': tas5756m, 'tps1663': tps16630, 'nid': nid100, 'tps709': tps70933, 'msm': msm261, '+20V': power_20v,
             'electrode': touch_electrode}
    for k in which:
        syms.append(table[k]())
    kg.write_symbol_lib(path, syms)
    symlib.EXTRA_LIBS['ha_panel'] = path
    symlib._cache.pop('ha_panel', None)
    return path
