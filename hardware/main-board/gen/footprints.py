"""Custom footprints (KiCad 9) drawn from the datasheets. Run: python3 footprints.py <dir>.pretty [which...]

TI_DCA0048A_HTSSOP-48-1EP  TAS5756M (SLAS988B): signal pads = KiCad TSSOP-48_6.1x12.5mm_P0.5mm (1.475 x 0.3, rows
                            7.425 c-c; TI DGG0048A 4214859/B: 1.5 x 0.3, 7.5 c-c, same 6.1 body / 8.1 span / 0.5 pitch);
                            exposed pad: mask opening 3.7 x 8.8 = the largest package pad (2.90-3.72 x 7.96-8.78,
                            drawing 4206320-7/S), copper land 5.0 x 15.0 (11.1.3.2: no smaller than the package pad);
                            paste 8 windows 1.40 x 1.80 = 20.16 mm2 = 72.8 % of the nominal pad 3.31 x 8.37 (70-80 %);
                            thermal vias drill 0.20 (<= 8 mil) / 0.45, solid connection, tented outside the opening.
MeanWell_NID100_SIP-13     NID100-SPEC 2024-10-30: 13 x 0.64 sq pins, 2.54 pitch, pins 1-6 at 0-12.70, 7-13 at
                            33.02-48.26; body 50.8 x 12 (pin 1 1.24 from the end, pin row 4.0 from the back face).
L_Codaca_CSBA0850          CODACA CSBA0850 (revised 2026-03-16): land 2 x 3.0 x 3.0, gap 3.6; body 8.7 x 8.5 x 5.1.
TouchElectrode_16x16mm_R2  F.Cu only, no mask opening (copper under the mask), no paste.
WirePads_1x04_P3.50mm_2.0x3.0mm  SMD wire pads like rev C (2 x 3 at 3.5 pitch), mask open, no paste.
"""
import os
import sys
import uuid

NS = uuid.UUID('6c1f3a52-6b0e-4f7e-9d3a-0b6d2a6e1f00')


def U(seed):
    return str(uuid.uuid5(NS, seed))


def fmt(v):
    s = ('%.4f' % v).rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


class FP:
    def __init__(self, name, descr, tags, attr='smd'):
        self.name, self.descr, self.tags, self.attr = name, descr, tags, attr
        self.items = []
        self.n = 0

    def _u(self):
        self.n += 1
        return U('%s/%d' % (self.name, self.n))

    def line(self, x1, y1, x2, y2, layer, w):
        self.items.append('\t(fp_line (start %s %s) (end %s %s) (stroke (width %s) (type solid)) (layer "%s") (uuid "%s"))'
                          % (fmt(x1), fmt(y1), fmt(x2), fmt(y2), fmt(w), layer, self._u()))

    def rect(self, x1, y1, x2, y2, layer, w, fill=False):
        self.items.append('\t(fp_rect (start %s %s) (end %s %s) (stroke (width %s) (type solid)) (fill %s) (layer "%s") '
                          '(uuid "%s"))' % (fmt(x1), fmt(y1), fmt(x2), fmt(y2), fmt(w), 'yes' if fill else 'no', layer,
                                            self._u()))

    def circle(self, x, y, r, layer, w, fill=False):
        self.items.append('\t(fp_circle (center %s %s) (end %s %s) (stroke (width %s) (type solid)) (fill %s) (layer "%s") '
                          '(uuid "%s"))' % (fmt(x), fmt(y), fmt(x + r), fmt(y), fmt(w), 'yes' if fill else 'no', layer,
                                            self._u()))

    def text(self, s, x, y, layer, size=1.0, th=0.15):
        self.items.append('\t(fp_text user "%s" (at %s %s 0) (layer "%s") (uuid "%s") (effects (font (size %s %s) '
                          '(thickness %s))))' % (s, fmt(x), fmt(y), layer, self._u(), fmt(size), fmt(size), fmt(th)))

    def pad(self, num, kind, shape, x, y, w, h, layers, drill=None, rratio=None, extra=''):
        s = '\t(pad "%s" %s %s (at %s %s) (size %s %s)' % (num, kind, shape, fmt(x), fmt(y), fmt(w), fmt(h))
        if drill is not None:
            s += ' (drill %s)' % fmt(drill)
        s += ' (layers %s)' % ' '.join('"%s"' % l for l in layers)
        if rratio is not None:
            s += ' (roundrect_rratio %s)' % fmt(rratio)
        s += extra + ' (uuid "%s"))' % self._u()
        self.items.append(s)

    def write(self, d, ref_y, val_y, model=None):
        out = ['(footprint "%s"' % self.name, '\t(version 20241229)', '\t(generator "pcbnew")',
               '\t(generator_version "9.0")', '\t(layer "F.Cu")', '\t(descr "%s")' % self.descr, '\t(tags "%s")' % self.tags]
        for k, v, y, lay, hide in (('Reference', 'REF**', ref_y, 'F.SilkS', False), ('Value', self.name, val_y, 'F.Fab', False),
                                   ('Datasheet', '', 0, 'F.Fab', True), ('Description', self.descr, 0, 'F.Fab', True)):
            out.append('\t(property "%s" "%s" (at 0 %s 0) (layer "%s")%s (uuid "%s") (effects (font (size 1 1) '
                       '(thickness 0.15))))' % (k, v, fmt(y), lay, ' (hide yes)' if hide else '', self._u()))
        out.append('\t(attr %s)' % self.attr)
        out += self.items
        if model:
            out.append('\t(model "%s" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))' % model)
        out.append('\t(embedded_fonts no)')
        out.append(')')
        with open(os.path.join(d, self.name + '.kicad_mod'), 'w') as f:
            f.write('\n'.join(out) + '\n')


def tas5756m_dca(d):
    f = FP('TI_DCA0048A_HTSSOP-48-1EP',
           'TI DCA (R-PDSO-G48) HTSSOP-48 PowerPAD 6.1x12.5 P0.5, TAS5756M; EP mask 3.7x8.8, land 5.0x15, 39 vias 0.2/0.45, '
           'paste 72.8 %% (SLAS988B 11.1.3.2)'.replace('%%', '%'), 'HTSSOP-48 DCA PowerPAD TAS5756M thermal vias')
    px, pw, ph = 3.7125, 1.475, 0.3          # KiCad TSSOP-48_6.1x12.5mm_P0.5mm
    for i in range(24):
        y = -5.75 + i * 0.5
        f.pad(str(i + 1), 'smd', 'roundrect', -px, y, pw, ph, ['F.Cu', 'F.Mask', 'F.Paste'], rratio=0.25)
        f.pad(str(48 - i), 'smd', 'roundrect', px, y, pw, ph, ['F.Cu', 'F.Mask', 'F.Paste'], rratio=0.25)
    # exposed pad: copper land (no mask) + mask-defined opening + paste windows
    f.pad('49', 'smd', 'rect', 0, 0, 5.0, 15.0, ['F.Cu'], extra=' (zone_connect 2)')
    f.pad('49', 'smd', 'rect', 0, 0, 3.7, 8.8, ['F.Cu', 'F.Mask'], extra=' (zone_connect 2)')
    for x in (-0.85, 0.85):
        for y in (-3.35, -1.15, 1.15, 3.35):
            f.pad('', 'smd', 'rect', x, y, 1.40, 1.80, ['F.Paste'])
    vias = [(x, y) for x in (-2.15, 2.15) for y in [k * 1.0 for k in range(-6, 7)]]       # 26 under the body, tented
    vias += [(x, y) for y in (-6.95, 6.95) for x in (-1.6, -0.8, 0.0, 0.8, 1.6)]           # 10 beyond the ends, tented
    vias += [(0.0, y) for y in (-2.25, 0.0, 2.25)]                                           # 3 in the paste gaps
    for (x, y) in vias:
        f.pad('49', 'thru_hole', 'circle', x, y, 0.45, 0.45, ['*.Cu'], drill=0.2, extra=' (zone_connect 2)')
    # fab body + pin 1
    f.line(-3.05, -5.25, -2.55, -6.25, 'F.Fab', 0.1)
    f.line(-2.55, -6.25, 3.05, -6.25, 'F.Fab', 0.1)
    f.line(3.05, -6.25, 3.05, 6.25, 'F.Fab', 0.1)
    f.line(3.05, 6.25, -3.05, 6.25, 'F.Fab', 0.1)
    f.line(-3.05, 6.25, -3.05, -5.25, 'F.Fab', 0.1)
    # silk: short end lines outside the land, pin-1 dot
    for y in (-7.85, 7.85):
        f.line(-2.6, y, 2.6, y, 'F.SilkS', 0.15)
    f.circle(-3.0, -6.7, 0.25, 'F.SilkS', 0.15, fill=True)       # pin-1 dot beside pin 1, clear of the bootstrap cap
    # courtyard: body + pins (x +-4.7, y +-6.5) plus the exposed-land tongues to y +-7.8 (keeps the bootstrap caps legal
    # beside pins 1/48 and 24/25, where only bare land copper extends past the package)
    cy = [(-4.7, -6.5), (-2.75, -6.5), (-2.75, -7.8), (2.75, -7.8), (2.75, -6.5), (4.7, -6.5), (4.7, 6.5), (2.75, 6.5),
          (2.75, 7.8), (-2.75, 7.8), (-2.75, 6.5), (-4.7, 6.5)]
    for (x1, y1), (x2, y2) in zip(cy, cy[1:] + cy[:1]):
        f.line(x1, y1, x2, y2, 'F.CrtYd', 0.05)
    f.text('${REFERENCE}', 0, 0, 'F.Fab', 1.0)
    f.write(d, -9.0, 9.0, '${KICAD9_3DMODEL_DIR}/Package_SO.3dshapes/TSSOP-48_6.1x12.5mm_P0.5mm.step')
    return f.name


def nid100(d):
    f = FP('MeanWell_NID100_SIP-13', 'Mean Well NID100 SIP-13, 0.64 sq pins P2.54 (1-6, 7-13 with a 20.32 gap), '
           'body 50.8 x 12 x 27.5 (NID100-SPEC 2024-10-30)', 'NID100 Mean Well SIP DC-DC', attr='through_hole')
    xs = [i * 2.54 for i in range(6)] + [33.02 + i * 2.54 for i in range(7)]
    for i, x in enumerate(xs):
        f.pad(str(i + 1), 'thru_hole', 'rect' if i == 0 else 'circle', x, 0, 2.1, 2.1, ['*.Cu', '*.Mask'], drill=1.15)
    x0, x1 = -1.24, 49.56          # body ends (pin 1 is 1.24 from the left end)
    y0, y1 = -4.0, 8.0             # pin row 4.0 from the back face; 12 deep
    f.rect(x0, y0, x1, y1, 'F.Fab', 0.1)
    f.line(x0, y0, x1, y0, 'F.SilkS', 0.15)
    f.line(x0, y1, x1, y1, 'F.SilkS', 0.15)
    f.line(x0, y0, x0, y1, 'F.SilkS', 0.15)
    f.line(x1, y0, x1, y1, 'F.SilkS', 0.15)
    f.text('+Vo', 3.81, 2.0, 'F.SilkS', 1.0)
    f.text('Vin', 39.37, 2.0, 'F.SilkS', 1.0)
    f.text('back', 24.0, -2.8, 'F.Fab', 1.0)
    f.rect(x0 - 0.25, y0 - 0.25, x1 + 0.25, y1 + 0.25, 'F.CrtYd', 0.05)
    f.text('${REFERENCE}', 24.0, 4.0, 'F.Fab', 1.0)
    f.write(d, -5.5, 9.5)
    return f.name


def csba0850(d):
    f = FP('L_Codaca_CSBA0850', 'CODACA CSBA0850 power inductor 8.7 x 8.5 x 5.1, land 2 x 3.0 x 3.0 gap 3.6 '
           '(datasheet revised 2026-03-16)', 'inductor CODACA CSBA0850')
    for n, x in (('1', -3.3), ('2', 3.3)):
        f.pad(n, 'smd', 'roundrect', x, 0, 3.0, 3.0, ['F.Cu', 'F.Mask', 'F.Paste'], rratio=0.1)
    f.rect(-4.35, -4.25, 4.35, 4.25, 'F.Fab', 0.1)
    for y in (-4.36, 4.36):
        f.line(-1.6, y, 1.6, y, 'F.SilkS', 0.15)
    f.rect(-5.05, -4.75, 5.05, 4.75, 'F.CrtYd', 0.05)
    f.text('${REFERENCE}', 0, 0, 'F.Fab', 1.0)
    f.write(d, -5.6, 5.6)
    return f.name


def electrode(d, w=16.0, h=16.0, r=2.0):
    f = FP('TouchElectrode_16x16mm_R2', 'Self-capacitance touch electrode %gx%g r%g, F.Cu under the solder mask '
           '(no opening), via to the back placed in the layout' % (w, h, r), 'touch electrode QTouch', attr='smd')
    f.pad('1', 'smd', 'roundrect', 0, 0, w, h, ['F.Cu'], rratio=r / min(w, h))
    f.rect(-w / 2 - 0.25, -h / 2 - 0.25, w / 2 + 0.25, h / 2 + 0.25, 'F.CrtYd', 0.05)
    f.text('${REFERENCE}', 0, 0, 'F.Fab', 1.0)
    f.write(d, -h / 2 - 1.5, h / 2 + 1.5)
    return f.name


def wirepads(d):
    f = FP('WirePads_1x04_P3.50mm_2.0x3.0mm', 'Four SMD wire pads 2.0 x 3.0 at 3.5 pitch (rev C style), mask open, no '
           'paste', 'wire pad solder')
    for i in range(4):
        f.pad(str(i + 1), 'smd', 'roundrect', i * 3.5, 0, 2.0, 3.0, ['F.Cu', 'F.Mask'], rratio=0.15)
    f.rect(-1.25, -1.75, 3 * 3.5 + 1.25, 1.75, 'F.CrtYd', 0.05)
    f.text('${REFERENCE}', 5.25, 0, 'F.Fab', 1.0)
    f.write(d, -2.8, 2.8)
    return f.name


def wirepads_col(d):
    f = FP('WirePads_1x05_P1.10mm_2.0x0.7mm', 'Five SMD wire pads 2.0 x 0.7 at 1.1 pitch in one column (mic strip cable, '
           'soldered conductors), mask open, no paste', 'wire pad solder cable')
    for i in range(5):
        f.pad(str(i + 1), 'smd', 'roundrect', 0, (i - 2) * 1.1, 2.0, 0.7, ['F.Cu', 'F.Mask'], rratio=0.15)
    f.rect(-1.2, -2.85, 1.2, 2.85, 'F.CrtYd', 0.05)
    f.text('${REFERENCE}', 0, 0, 'F.Fab', 0.8)
    f.write(d, -3.4, 3.4)
    return f.name


def heatstake(d):
    f = FP('HeatStake_D2.0mm_Head3.6mm', 'Heat-stake hole for a 1.8 mm pin (rev F K21), NPTH 2.0; staked head 3.6 on '
           'the back (keep-out drawn on B.Fab, enforced by a rule area in the layout)', 'heat stake hole',
           attr='board_only exclude_from_pos_files exclude_from_bom')
    f.pad('', 'np_thru_hole', 'circle', 0, 0, 2.0, 2.0, ['*.Cu', '*.Mask'], drill=2.0)
    f.circle(0, 0, 1.8, 'B.Fab', 0.1)
    f.circle(0, 0, 1.25, 'F.CrtYd', 0.05)
    f.write(d, -2.5, 2.5)
    return f.name


def wirelink(d):
    f = FP('WireLink_P7.62mm_D1.3mm', 'Wire link, 2 pads 7.62 apart, drill 1.3 for 1.0 mm (18 AWG) tinned Cu wire; '
           'opened for a series ammeter (bench 2.7)', 'wire link jumper bridge', attr='through_hole')
    for n, x in (('1', 0.0), ('2', 7.62)):
        f.pad(n, 'thru_hole', 'circle', x, 0, 2.6, 2.6, ['*.Cu', '*.Mask'], drill=1.3)
    f.line(1.5, 0, 6.12, 0, 'F.SilkS', 0.15)
    f.rect(-1.55, -1.55, 9.17, 1.55, 'F.CrtYd', 0.05)
    f.rect(-1.3, -0.6, 8.92, 0.6, 'F.Fab', 0.1)
    f.text('${REFERENCE}', 3.81, 0, 'F.Fab', 1.0)
    f.write(d, -2.4, 2.4)
    return f.name


def im69d120(d):
    src = '/usr/share/kicad/footprints/Sensor_Audio.pretty/Infineon_PG-LLGA-5-1.kicad_mod'
    s = open(src).read()
    s = s.replace('(footprint "Infineon_PG-LLGA-5-1"', '(footprint "Infineon_IM69D120_PG-LLGA-5-1"')
    import re as _re
    s = _re.sub(r'\(descr "[^"]*"\)', '(descr "Infineon IM69D120 / IM69D130 PG-LLGA-5-1 4 x 3 x 1.2, bottom port; KiCad '
                'Infineon_PG-LLGA-5-1 with pads 1-4 at 0.45 x 0.76 per IM69D120 datasheet rev 1.0 (2017-12-20) Fig. 12; '
                'ring R0.58-R1.04, PCB sound hole 0.8")', s, count=1)
    # pads 1-4: 0.45 x 0.7 -> 0.45 x 0.76
    s = _re.sub(r'(\(pad "[1-4]" smd rect\s*\(at [^)]*\)\s*\(size )0\.45 0\.7(\))', r'\g<1>0.45 0.76\2', s)
    s = s.replace('(property "Value" "Infineon_PG-LLGA-5-1"', '(property "Value" "Infineon_IM69D120_PG-LLGA-5-1"')
    open(os.path.join(d, 'Infineon_IM69D120_PG-LLGA-5-1.kicad_mod'), 'w').write(s)
    return 'Infineon_IM69D120_PG-LLGA-5-1'


def _wire_grid(d, cols, rows, name_cols):
    """Wire landing: plated holes dia 1.0 on 1.7 pads at 2.54, numbered like KiCad's PinHeader_<cols>x<rows> (pad 1 at the
    origin, numbers run along x first). No header body: the courtyard is the pads + 0.3."""
    name = 'WirePads_%s_P2.54mm_D1.0mm' % name_cols
    f = FP(name, 'Wire landing %s, 2.54 pitch, hole 1.0 for 22-28 AWG stranded wire, pad 1.7; wires soldered on the bench '
           '(main board rev 3)' % name_cols.replace('x', ' x '), 'wire pad solder lead', attr='through_hole')
    n = 0
    for r in range(rows):
        for c in range(cols):
            n += 1
            f.pad(str(n), 'thru_hole', 'roundrect' if n == 1 else 'circle', c * 2.54, r * 2.54, 1.7, 1.7, ['*.Cu', '*.Mask'],
                  drill=1.0, rratio=0.2 if n == 1 else None)
    x1, y1 = (cols - 1) * 2.54, (rows - 1) * 2.54
    f.rect(-1.15, -1.15, x1 + 1.15, y1 + 1.15, 'F.CrtYd', 0.05)
    f.rect(-0.95, -0.95, x1 + 0.95, y1 + 0.95, 'F.Fab', 0.1)
    f.text('${REFERENCE}', x1 / 2, y1 / 2, 'F.Fab', 0.8)
    f.write(d, -2.2, y1 + 2.2)
    return f.name


def wirepads_2x05(d):
    return _wire_grid(d, 2, 5, '2x05')


def wirepads_2x02(d):
    return _wire_grid(d, 2, 2, '2x02')


def wirepads_1x08(d):
    return _wire_grid(d, 1, 8, '1x08')


def m3_post_hole(d):
    """Board hole for the unit's standard M3 x 8 button head (site document section 2, issue 2)."""
    f = FP('MountingHole_3.2mm_M3_Post', 'Mounting hole dia 3.2 NPTH for M3 x 8 ISO 7380-1 into a carrier post dia 8; '
           'keep clear dia 7 on the door side (head dia 5.7), dia 9 on the back face (post)', 'mounting hole M3 post',
           attr='exclude_from_pos_files exclude_from_bom')
    f.pad('', 'np_thru_hole', 'circle', 0, 0, 3.2, 3.2, ['*.Cu', '*.Mask'], drill=3.2)
    f.circle(0, 0, 3.5, 'F.CrtYd', 0.05)
    f.circle(0, 0, 4.5, 'B.CrtYd', 0.05)
    f.circle(0, 0, 2.85, 'F.Fab', 0.1)           # screw head dia 5.7
    f.circle(0, 0, 4.0, 'B.Fab', 0.1)            # post dia 8
    f.circle(0, 0, 4.5, 'Cmts.User', 0.1)
    f.text('${REFERENCE}', 0, 0, 'F.Fab', 0.8)
    f.write(d, -4.2, 4.2)
    return f.name


ALL = {'tas': tas5756m_dca, 'nid': nid100, 'csba': csba0850, 'electrode': electrode, 'wirepads': wirepads,
       'wirelink': wirelink, 'im69': im69d120, 'wirecol': wirepads_col, 'stake': heatstake,
       'wp2x5': wirepads_2x05, 'wp2x2': wirepads_2x02, 'wp1x8': wirepads_1x08, 'm3post': m3_post_hole}

if __name__ == '__main__':
    d = sys.argv[1]
    os.makedirs(d, exist_ok=True)
    for k in (sys.argv[2:] or ALL):
        print(ALL[k](d))
