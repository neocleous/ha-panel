"""Build hardware/notes/digikey-bom.md and .csv from lines.py + R.json (DigiKey lookups 2026-11-08) + CHOICE."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lines import LINES, HARNESS, NONBOARD, SYSTEM
from choice import CHOICE, NOTES, EXTRA_LINES

R = json.load(open(os.path.join(HERE, 'R.json')))
DATE = '2026-11-08'

def tiers(r):
    out = []
    for t in (r.get('tiers') or '').split():
        q, p = t.split('@')
        out.append((int(q.replace('’', '').replace("'", '')), float(p)))
    return out

def unit_at(r, qty):
    ts = tiers(r); best = None
    for q, p in ts:
        if qty >= q:
            best = p
    return best

def stock(r):
    v = (r.get('stock') or '').replace('In-Stock: ', '').replace('’', '').replace("'", '')
    return "{:,}".format(int(v)).replace(',', "'") if v.isdigit() else v

MFR = {'Samsung Electro-Me': 'Samsung', 'Cal-Chip Electroni': 'Cal-Chip', 'MEAN WELL USA Inc.': 'Mean Well', 'Littelfuse Inc.': 'Littelfuse',
       'Bel Fuse Inc.': 'Bel', 'JST Sales America': 'JST', 'Bourns Inc.': 'Bourns', 'Texas Instruments': 'TI', 'Infineon Technologies': 'Infineon',
       'Stackpole Electronics': 'Stackpole', 'Adafruit Industries': 'Adafruit', 'Seeed Technology Co': 'Seeed', 'Würth Elektronik': 'Würth',
       'Panasonic Industry': 'Panasonic', 'YAGEO': 'Yageo'}


FOOTER = """
## Not bought
- **LK1** (Pi-branch wire link): tinned copper wire ≤ 1.15 mm into the Ø1.3 holes, e.g. a 1.0 mm² solid core. Owned stock is assumed.
- **R8, R9** (NID trim network): DNP. Values come from the bench only if the 5.1 V option is needed (V20).
- **R20–R25, R27** (D4a and amplifier options): DNP. They are covered by the 25 × 0 Ω on the 0 Ω line.
- **Test pads, J3, J4, J7, J10:** bare pads. Nothing to buy.

## Removed from order list rev 4 §2.2 (provisional lines)
- **0402 parts, replaced by the 0603 parts above:**
  - Murata GRM155R71H104KE14D
  - Taiyo Yuden LMK105BJ105KVHF and TMK105CBJ225MV-F
  - Yageo CC0402MPX5R5BB106
  - Yageo RC0402 33 Ω, 100 Ω, 0 Ω, 100 kΩ, 150 kΩ, 10 kΩ and 1 kΩ (R19 4.7 kΩ replaces the 1 kΩ)
- **Samsung CL21B104KBCNNNC** (100 nF 0805) and **CL32B106KBJNNNE** (10 µF 1210): not in the schematic.
- **JST BM05B-SRSS-TB**: no strip connector (decision 9.1).
- **GCT USB4105-GF-A**: replaced by the through-hole USB4085-GF-A (decision 3A).
- **TI TPD1E05U06DPYR** (0402): replaced by the SOD-523 footprint in block 1. The SOD-523 TPD1E05U06DYAR then gave way to the ESD321DYAR (decision 10.1).
- **Kept unchanged in the basket:** the 3M SJ-5012 feet.

## DigiKey basket (rebuilt 2026-11-08, not ordered)
- **Removed:** the 39 old "HA panel" / "HA panel provisional" electronics lines (order list rev 4 §2.2). **Kept:** 56 × 3M SJ-5012 feet (SJ5012-0-ND, CHF 6.35).
- **Added:** the 55 lines above from `digikey-bom.csv`, customer reference "HA panel". Quantities and prices were checked line by line against this list after the upload: CHF 169.97, every line "Immediate".
- **HA panel in the basket:** CHF 176.32 excl. VAT (list 169.97 + feet 6.35), CHF 190.60 incl. 8.1 % VAT.
- **Not touched:** 21 lines with "V2 …" references and 2 lines without a reference (Chip Quik CQ2LF-1.0, MG Chemicals 8342-10ML). Whole basket: CHF 265.98 excl. VAT + VAT 21.54 = CHF 287.52, shipping free (DigiKey, 2026-11-08).
- **Shared part numbers:** RMCF0603FT100KCT-ND, RMCF0603FT100RCT-ND and 1528-261-ND are also on V2 lines. DigiKey keeps them as separate lines and flags "Duplicate line item"; its note only asks that stock covers the combined quantity (35, 20 and 2 against 802'912, 1'820'162 and 29'215).

## Decision 10 — strip ESD diodes (D1–D3 on each strip): option 1 (Daniel, 2026-11-08)
TPD1E05U06DYAR was at 0 stock with a 26-week factory lead time (DigiKey, 2026-11-08), so **TI ESD321DYAR** is fitted (238'921 in stock).
- 0.9 pF typ / 1.1 pF max, VRWM 3.6 V, leakage 50 nA max at 3.6 V, SOD-523 (ESD321 datasheet rev C, 2025-06-04). The 3.3 V lines stay below its 3.6 V standoff.
- Its DYA pinout is the reverse of the TPD1E05U06 DYA: pin 1 = GND, pin 2 = IO. The strip schematic has an ESD321 symbol and the three footprints are turned 180°; the copper is unchanged and the silk pin-1 mark sits at the GND pad.
"""

rows = []
for section, lines in (('Main board', [l for l in LINES if not l[0].startswith('S_')]),
                       ('Mic strip (two boards)', [l for l in LINES if l[0].startswith('S_')]),
                       ('XH harness', HARNESS), ('System parts kept from order list rev 4', SYSTEM), ('Non-board parts moved from AliExpress', NONBOARD)):
    for key, refs, spec, need, buy, cands in lines:
        if key in CHOICE and CHOICE[key] is None:
            continue
        q = CHOICE.get(key, cands[0] if cands else None)
        buy = EXTRA_LINES.get(key, {}).get('buy', buy)
        r = R.get(q, {}) if q else {}
        u = unit_at(r, buy)
        # round up to the next price break when that costs at most 10 % (or CHF 0.10) more
        for tq, tp in tiers(r):
            if u is not None and tq > buy and tq * tp <= max(buy * u * 1.10, buy * u + 0.10):
                buy, u = tq, tp
        rows.append(dict(section=section, key=key, refs=refs, spec=spec, need=need, buy=buy, mpn=r.get('mpn', ''),
                         mfr=r.get('mfr', ''), dk=r.get('dk', ''), desc=r.get('desc', ''), unit=u,
                         ext=(u * buy if u is not None else None), stock=stock(r), url=(r.get('url') or ('https://www.digikey.ch/en/products/result?keywords=' + r.get('dk', ''))),
                         note=NOTES.get(key, '')))

def fmt_need(n):
    return ('%g' % n) if n == int(n) else '%.1f' % n

total = sum(r['ext'] for r in rows if r['ext'] is not None)
md = ['# DigiKey BOM — main board, mic strips, harness (block 3, %s)' % DATE, '',
      'Derived from the schematics on `docs` (main board rev 2.1, mic strip decisions 9.1 and 10.1). Prices are DigiKey CH, CHF excl. VAT, '
      'cut tape at the quantity bought, seen %s; stock as shown the same day. Build: one main board and two strips. '
      'Spares: small passives +50 %% (rounded up), ICs +1, cheap discretes and connectors +1.' % DATE, '',
      '**Total: CHF %.2f excl. VAT** (%d lines; CHF %.2f incl. 8.1 %% VAT). The DigiKey quick-add list is `digikey-bom.csv`.' % (total, len(rows), total * 1.081), '']
sec = None
for r in rows:
    if r['section'] != sec:
        sec = r['section']
        md += ['', '## ' + sec, '', '| Refs | Part | DigiKey | Need | Buy | Unit | Ext | Stock | Note |', '|---|---|---|---|---|---|---|---|---|']
    part = ('%s %s' % (MFR.get(r['mfr'], r['mfr']), r['mpn'])).strip()
    md.append('| %s | %s — %s | [%s](%s) | %s | %d | %s | %s | %s | %s |' % (
        r['refs'], part, r['desc'], r['dk'], r['url'], fmt_need(r['need']), r['buy'],
        ('%.3f' % r['unit']) if r['unit'] is not None else '–', ('%.2f' % r['ext']) if r['ext'] is not None else '–',
        r['stock'], r['note']))
open(os.path.join(HERE, '..', 'digikey-bom.md'), 'w').write('\n'.join(md) + '\n' + FOOTER)
with open(os.path.join(HERE, '..', 'digikey-bom.csv'), 'w') as f:
    f.write('Quantity,Part Number,Customer Reference\n')
    for r in rows:
        f.write('%d,%s,HA panel\n' % (r['buy'], r['dk']))
print('lines', len(rows), 'total %.2f' % total)
for r in rows:
    if not r['dk'] or r['unit'] is None or r['stock'] in ('0', '', 'Obsolete'):
        print('CHECK', r['key'], r['mpn'], r['dk'], r['stock'], r['unit'])
