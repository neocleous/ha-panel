"""Parts list of the three boards from their schematics, and its difference to the DigiKey lines of order list rev 5.

    python3 boards_bom.py <hardware dir> <date> > report
Reads:  main-board/main-board.kicad_sch, mic-strip/mic-strip.kicad_sch, touch-board/touch-board.kicad_sch (through
        kicad-cli; each symbol carries MPN, Manufacturer and DigiKey), notes/digikey-bom.md (need and buy per line, as
        frozen on 2026-11-08) and notes/digikey-bom.csv (the basket's quick-add list).
Writes: notes/bom-<date>.csv (one row per part and board) and notes/bom-<date>.md: the text of
        notes/bom/bom-<date>-head.md, the tables made here, the text of notes/bom/bom-<date>-foot.md. The two texts are
        written by hand; the script stops if a DigiKey line has changed, so that they cannot go stale unnoticed.
Nothing is looked up: no price, no stock, no part is chosen here.

Set: 1 main board, 2 mic strips, 1 touch board.
Spares rule (Daniel 2026-11-08, D50; text from notes/bom/lines.py): at least 3 for 0603 and smaller (SC-70 and SOD-523
included), at least 2 for 0805 and 1206 and for the MEMS microphone, 1 for larger parts and ICs; none for L1 and C5/C6.
"""
import csv
import io
import os
import re
import subprocess
import sys
import tempfile
from collections import OrderedDict, defaultdict

BOARDS = [('main-board', 'Main board rev 3.2', 1), ('mic-strip', 'Mic strip', 2), ('touch-board', 'Touch board rev D', 1)]

PACKAGE = [  # footprint (after the library name) -> (package in plain words, spares class)
    (r'^[CR]_0603_', ('0603', 'small')),
    (r'^[CR]_0805_', ('0805', 'medium')),
    (r'^C_1206_', ('1206', 'medium')),
    (r'^Fuse_1206_', ('1206', 'medium')),
    (r'^Fuse_2920_', ('2920', 'large')),
    (r'^Fuse_Littelfuse-NANO2', ('NANO2, SMD', 'large')),
    (r'^D_SMB$', ('SMB (DO-214AA)', 'large')),
    (r'^D_SOD-523$', ('SOD-523', 'small')),
    (r'^SOT-353_SC-70-5$', ('SC-70-5', 'small')),
    (r'^SOT-23-5$', ('SOT-23-5', 'large')),
    (r'^HTSSOP-20-1EP', ('HTSSOP-20 with centre pad, 0.65 pitch', 'large')),
    (r'^TI_DCA0048A_HTSSOP-48-1EP$', ('HTSSOP-48 with centre pad, 0.5 pitch', 'large')),
    (r'^SOIC-14_', ('SOIC-14, 1.27 pitch', 'large')),
    (r'^Infineon_IM69D120_PG-LLGA-5-1$', ('PG-LLGA-5-1 (MEMS microphone)', 'medium')),
    (r'^CP_Radial_D10\.0mm_P5\.00mm$', ('radial Ø10, pitch 5.0, through-hole', 'large')),
    (r'^CP_Radial_D5\.0mm_P2\.00mm$', ('radial Ø5, pitch 2.0, through-hole', 'large')),
    (r'^JST_XH_B2B-XH-A', ('JST XH, 2 pins, through-hole', 'large')),
    (r'^JST_XH_B4B-XH-A', ('JST XH, 4 pins, through-hole', 'large')),
    (r'^USB_C_Receptacle_GCT_USB4085$', ('USB-C socket, through-hole', 'large')),
    (r'^PinHeader_1x04_P2\.54mm_Vertical$', ('pin header 1 × 4, 2.54 pitch, through-hole', 'large')),
    (r'^L_Bourns_SRR1260$', ('SRR1260, SMD', 'large')),
    (r'^L_Codaca_CSBA0850$', ('CSBA0850, SMD', 'large')),
    (r'^MeanWell_NID100_SIP-13$', ('SIP-13 module, through-hole', 'large')),
    (r'^WireLink_P7\.62mm_D1\.3mm$', ('two Ø1.3 holes, 7.62 apart', 'none')),
]
SPARES = {'small': 3, 'medium': 2, 'large': 1, 'none': 0}
NO_SPARE_REFS = {('main-board', 'L1'), ('main-board', 'C5'), ('main-board', 'C6')}   # large, robust (2026-11-08)
MAKER = {'YAGEO': 'Yageo', 'Samsung Electro-Mechanics': 'Samsung', 'Texas Instruments': 'TI', 'Bel Fuse': 'Bel',
         'Microchip Technology': 'Microchip'}


def export(hw, board):
    with tempfile.TemporaryDirectory() as t:
        out = os.path.join(t, 'b.csv')
        subprocess.run(['kicad-cli', 'sch', 'export', 'bom', '--fields', 'Reference,Value,Footprint,${DNP},MPN,Manufacturer,DigiKey',
                        '--labels', 'Ref,Value,Footprint,DNP,MPN,Manufacturer,DigiKey', '--ref-range-delimiter', '', '-o', out,
                        os.path.join(hw, board, board + '.kicad_sch')], check=True, capture_output=True)
        return list(csv.DictReader(open(out, encoding='utf-8')))


def package(fp):
    name = fp.split(':')[-1]
    for pat, res in PACKAGE:
        if re.search(pat, name):
            return res
    raise SystemExit('no package for footprint %s' % fp)


def clean(v):
    """the value without the words that only say where the part is used"""
    return re.sub(r' DNP$| (radar|touch|speaker [LR]|BME680|VEML6030)$', '', v).replace('0.1u ', '100n ')


def one_value(g):
    vals = sorted({clean(r['value']) for r in g}, key=lambda v: ('%' not in v, v))
    return vals[0]


def refkey(r):
    m = re.match(r'([A-Z]+)(\d+)', r)
    return (m.group(1), int(m.group(2)))


def refs_text(refs):
    """R20, R21, R22 -> R20–R22"""
    refs = sorted(refs, key=refkey)
    out, i = [], 0
    while i < len(refs):
        j = i
        while j + 1 < len(refs) and refkey(refs[j + 1])[0] == refkey(refs[i])[0] and refkey(refs[j + 1])[1] == refkey(refs[j])[1] + 1:
            j += 1
        out.append(refs[i] if j == i else (refs[i] + ', ' + refs[j] if j == i + 1 else refs[i] + '–' + refs[j]))
        i = j + 1
    return ', '.join(out)


def basket(hw):
    """DigiKey lines as frozen: number -> dict(refs, part, need, buy); and the csv's quantities."""
    lines, section = OrderedDict(), None
    for row in open(os.path.join(hw, 'notes', 'digikey-bom.md'), encoding='utf-8'):
        if row.startswith('## '):
            section = row[3:].strip()
        m = re.match(r'^\| (.+?) \| (.+?) \| \[(.+?)\]\(.+?\) \| (\d+) \| (\d+) \| ([\d.]+) \| ([\d.]+) \|', row)
        if m:
            lines[m.group(3)] = dict(refs=m.group(1), part=m.group(2), need=int(m.group(4)), buy=int(m.group(5)),
                                     unit=float(m.group(6)), ext=float(m.group(7)), section=section)
    qty = {r['Part Number']: int(r['Quantity']) for r in csv.DictReader(open(os.path.join(hw, 'notes', 'digikey-bom.csv'), encoding='utf-8'))}
    return lines, qty


def main(hw, date):
    rows = []                                   # one per symbol
    for board, title, n in BOARDS:
        for r in export(hw, board):
            pk, cls = package(r['Footprint'])
            if (board, r['Ref']) in NO_SPARE_REFS:
                cls = 'none'
            dk = r['DigiKey'] if re.match(r'^[A-Za-z0-9./-]+-ND$', r['DigiKey']) else ''
            rows.append(dict(board=board, ref=r['Ref'], value=r['Value'], package=pk, cls=cls, dnp=bool(r['DNP']),
                             mpn=r['MPN'], maker=MAKER.get(r['Manufacturer'], r['Manufacturer']), dk=dk, dknote='' if dk else r['DigiKey']))
    lines, qty = basket(hw)
    assert set(lines) == set(qty) and all(lines[k]['buy'] == qty[k] for k in lines), 'digikey-bom.md and .csv disagree'

    # ---- per board ---------------------------------------------------------------------------------------------
    md = []
    with open(os.path.join(hw, 'notes', 'bom-%s.csv' % date), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['Board', 'Boards per set', 'References', 'Fitted', 'Value', 'Package', 'Maker', "Maker's part number", 'Qty per board',
                    'Qty per set', 'DigiKey number', 'Note'])
        for board, title, n in BOARDS:
            groups = OrderedDict()
            for r in rows:
                if r['board'] == board:
                    groups.setdefault((r['mpn'] or r['value'], r['package'], r['dnp']), []).append(r)
            fitted = sum(len(g) for k, g in groups.items() if not k[2])
            dnp = sum(len(g) for k, g in groups.items() if k[2])
            md.append('### %s — %d per set; %d parts fitted%s' % (title, n, fitted, ', %d places left empty' % dnp if dnp else ''))
            md.append('')
            md.append("| References | Value | Package | Maker | Maker's part number | Per board | Per set |")
            md.append('|---|---|---|---|---|---|---|')
            for (_, pk, isdnp), g in sorted(groups.items(), key=lambda kv: (kv[0][2], refkey(sorted(kv[1], key=lambda r: refkey(r['ref']))[0]['ref']))):
                r0 = g[0]
                mpn, value = r0['mpn'], one_value(g)
                note = r0['dknote']
                refs = refs_text([r['ref'] for r in g])
                shown_mpn = mpn if mpn else '—'
                if isdnp:
                    md.append('| %s | %s | %s | %s | %s | not fitted (%d) | — |' % (refs, value, pk, r0['maker'] or '—', shown_mpn, len(g)))
                else:
                    md.append('| %s | %s | %s | %s | %s | %d | %d |' % (refs, value, pk, r0['maker'] or '—', shown_mpn, len(g), len(g) * n))
                w.writerow([title, n, refs, 'no' if isdnp else 'yes', value, pk, r0['maker'], mpn, len(g), 0 if isdnp else len(g) * n, r0['dk'], note])
            md.append('')

    # ---- per set, against the DigiKey lines ----------------------------------------------------------------------
    need = defaultdict(lambda: dict(per={}, cls=None, mpn=None, maker=None, value=None, package=None, options=0))
    nodk = []
    for r in rows:
        n = dict((b, k) for b, _, k in BOARDS)[r['board']]
        if not r['dk']:
            if not r['dnp']:
                nodk.append(r)
            continue
        d = need[r['dk']]
        if r['dnp']:
            d['options'] += n
            continue
        d['per'][r['board']] = d['per'].get(r['board'], 0) + 1
        for k in ('mpn', 'maker', 'package'):
            assert d[k] in (None, r[k]), (r['dk'], k, d[k], r[k])
            d[k] = r[k]
        d['value'] = one_value([r] + ([dict(value=d['value'])] if d['value'] else []))
        assert d['cls'] in (None, r['cls']) or {d['cls'], r['cls']} <= {'none', 'large'}, r
        d['cls'] = r['cls'] if d['cls'] is None else d['cls']
    md.append('## 2. The set against the 45 DigiKey lines for board parts')
    md.append('')
    md.append("| Maker's part number | Value, package | Main | Strips (2) | Touch | Set needs | Spares by the rule | Least to buy | Basket: need on 2026-11-08 | Basket: quantity | Result |")
    md.append('|---|---|---|---|---|---|---|---|---|---|---|')
    summary = dict(same=0, need_changed=[], short=[], added=[], removed=[])
    order = list(lines)
    for dk in sorted(need, key=lambda k: order.index(k) if k in order else 999):
        d = need[dk]
        m, s, t = d['per'].get('main-board', 0), 2 * d['per'].get('mic-strip', 0), d['per'].get('touch-board', 0)
        tot = m + s + t
        sp = SPARES[d['cls']]
        least = tot + sp
        if dk not in lines:
            summary['added'].append((dk, d, tot))
            md.append('| %s | %s, %s | %d | %d | %d | %d | %d | %d | — | — | **added** |' % (d['mpn'], d['value'], d['package'], m, s, t, tot, sp, least))
            continue
        b = lines[dk]
        res = []
        if b['need'] != tot:
            summary['need_changed'].append((dk, d, b['need'], tot))
            res.append('**need %d → %d**' % (b['need'], tot))
        if b['buy'] < least:
            summary['short'].append((dk, d, b['buy'], least))
            res.append('**%d short of the rule**' % (least - b['buy']))
        if not res:
            summary['same'] += 1
            res.append('unchanged; %d spare' % (b['buy'] - tot))
        opt = ' (+%d option places)' % d['options'] if d['options'] else ''
        md.append('| %s | %s, %s | %d | %d | %d | %d%s | %d | %d | %d | %d | %s |' % (d['mpn'], d['value'], d['package'], m, s, t, tot, opt, sp, least, b['need'], b['buy'], '; '.join(res)))
    md.append('')
    board_lines = [k for k in lines if lines[k]['section'] in ('Main board', 'Mic strip (two boards)')]
    for dk in board_lines:
        if dk not in need:
            summary['removed'].append((dk, lines[dk]))
    other = [k for k in lines if k not in board_lines]

    md.append('## 3. Parts on the boards with no DigiKey line')
    md.append('')
    md.append("| Board | References | Value | Package | Maker's part number | Per set | Where it comes from (the schematic's note) |")
    md.append('|---|---|---|---|---|---|---|')
    g2 = OrderedDict()
    for r in nodk:
        g2.setdefault((r['board'], r['mpn'], r['package'], r['dknote']), []).append(r)
    for (board, mpn, pk, note), g in g2.items():
        n = dict((b, k) for b, _, k in BOARDS)[board]
        title = dict((b, t) for b, t, _ in BOARDS)[board]
        md.append('| %s | %s | %s | %s | %s | %d | %s |' % (title, refs_text([r['ref'] for r in g]), one_value(g), pk, mpn or '—', len(g) * n, note or '—'))
    md.append('')
    md.append('## 4. The %d DigiKey lines that are not board parts' % len(other))
    md.append('')
    md.append('| DigiKey number | Line | Need on 2026-11-08 | Quantity |')
    md.append('|---|---|---|---|')
    for k in other:
        md.append('| %s | %s: %s | %d | %d |' % (k, lines[k]['refs'], lines[k]['part'], lines[k]['need'], lines[k]['buy']))
    md.append('')
    changed = summary['need_changed'] or summary['short'] or summary['added'] or summary['removed']
    here = os.path.dirname(os.path.abspath(__file__))
    head = open(os.path.join(here, 'bom-%s-head.md' % date), encoding='utf-8').read()
    foot = open(os.path.join(here, 'bom-%s-foot.md' % date), encoding='utf-8').read()
    open(os.path.join(hw, 'notes', 'bom-%s.md' % date), 'w', encoding='utf-8').write(head + '\n'.join(md) + '\n' + foot)

    # ---- report ----------------------------------------------------------------------------------------------------
    print('symbols: ' + ', '.join('%s %d (%d not fitted)' % (b, sum(1 for r in rows if r['board'] == b), sum(1 for r in rows if r['board'] == b and r['dnp'])) for b, _, _ in BOARDS))
    print('DigiKey lines: %d in the list (%d board lines, %d others); total of the Ext column %.2f' % (len(lines), len(board_lines), len(other), sum(l['ext'] for l in lines.values())))
    print('DigiKey numbers on the boards: %d; all in the list: %s' % (len(need), all(k in lines for k in need)))
    print('board lines unchanged: %d' % summary['same'])
    print('need changed: %s' % [(k, a, b) for k, d, a, b in summary['need_changed']])
    print('short of the rule: %s' % [(k, a, b) for k, d, a, b in summary['short']])
    print('added (on a board, not in the list): %s' % [(k, d['mpn'], n) for k, d, n in summary['added']])
    print('removed (in the list, on no board): %s' % [(k, l['part']) for k, l in summary['removed']])
    print('parts with no DigiKey line: %s' % [(r['board'], r['ref'], r['value']) for r in nodk])
    print('pieces per set: %d fitted' % sum(dict((b, k) for b, _, k in BOARDS)[r['board']] for r in rows if not r['dnp']))
    if changed:
        raise SystemExit('A DigiKey line has changed: rewrite bom-%s-head.md before using bom-%s.md' % (date, date))


if __name__ == '__main__':
    main(os.path.abspath(sys.argv[1]), sys.argv[2])
