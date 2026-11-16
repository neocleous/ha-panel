"""Assembly drawing of main board rev 3.2 for hand assembly: every one of the 120 part names and every value.

    python3 gen/assembly_rev32.py [board.kicad_pcb] [out.pdf]        (from hardware/main-board; KiCad 9's Python)

The silkscreen hides 53 of the 120 names, so the drawing is made from the board file itself, not from the silkscreen:
outline, pads and each part's fab-layer outline, with the name (page 1) or the value (page 2) written into the part.
Page 3 is the placing list, value by value, with the maker's part numbers read from the schematic's fields
(kicad-cli sch export bom). Page 4 names the test pads and the connectors and shows the back face.
A3 landscape, vector, 4.25 : 1. Everything is seen from the door (the parts' face) except the back view on page 4.
"""
import csv
import os
import re
import subprocess
import sys
import tempfile
import textwrap

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle, PathPatch, Polygon as MP, Rectangle
from matplotlib.path import Path
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.dirname(HERE)
TO = pcbnew.ToMM
U0, V0 = 43.5, 28.95
SCALE = 4.25                         # paper mm per board mm
PT = SCALE * 72 / 25.4               # points per board mm
PAGE = (420.0, 297.0)                # A3 landscape, mm
ISSUE = '2026-11-16'
MAXERR = pcbnew.FromMM(0.005)

GROUPS = [  # the order of placing: (heading, test on (ref, value, footprint))
    ('Resistors 0603', lambda r, v, f: r.startswith('R') and '0603' in f),
    ('Resistors 0805', lambda r, v, f: r.startswith('R') and '0805' in f),
    ('Capacitors 0603', lambda r, v, f: r.startswith('C') and '0603' in f),
    ('Capacitors 0805', lambda r, v, f: r.startswith('C') and '0805' in f),
    ('Capacitors 1206', lambda r, v, f: r.startswith('C') and '1206' in f),
    ('Fuses', lambda r, v, f: r.startswith('F')),
    ('Diodes', lambda r, v, f: r.startswith('D')),
    ('Coils', lambda r, v, f: r.startswith('L') and not r.startswith('LK')),
    ('Chips', lambda r, v, f: r.startswith('U')),
]
THT_ORDER = ['LK1', 'J2', 'J1', 'J8', 'J9', 'J5', 'J6', 'J10', 'J11', 'C7', 'C5', 'C6', 'PS1']   # low to high (MAIN_env.md section 4)
CONN = {'J1': '20 V in, from the USB-C inlet board', 'J2': "Pi power (USB-C socket)", 'J3': 'Pi signal wires, 9 (wire pads; pad 10 spare)',
        'J4': 'Pi signal wires, 4 (wire pads)', 'J5': 'radar (LD2410C)', 'J6': 'touch board', 'J7': 'ReSpeaker echo tap (wire pads; empty)',
        'J8': 'speaker left', 'J9': 'speaker right', 'J10': 'BME680 (4-pin header)', 'J11': 'VEML6030 (4-pin header)'}
TPUSE = {'TP1': '20 V after the fuse F1, before the protection chip', 'TP2': '20 V after the protection chip', 'TP3': 'current monitor, 0.279 V per A on the 20 V bus',
         'TP4': 'protection chip fault (low = fault)', 'TP5': 'power good (enables the 5 V module)', 'TP6': 'shutdown pin', 'TP7': 'ground',
         'TP8': '5 V module input, after the coil L1', 'TP9': '5 V module output', 'TP10': '5 V after the Pi fuse F2', 'TP11': "5 V at the Pi's USB-C socket",
         'TP12': 'radar 5 V, after its fuse F3', 'TP13': '5 V module trim pin', 'TP14': '5 V module on/off pin', 'TP15': 'ground', 'TP16': '3.3 V',
         'TP17': 'ground', 'TP19': 'amplifier fault (low = fault)', 'TP20': 'ground'}


def uv(p):
    return (TO(p.x) - U0, V0 - TO(p.y))


def paths(sps, mirror=False):
    """A SHAPE_POLY_SET as matplotlib paths with their holes."""
    out = []
    for k in range(sps.OutlineCount()):
        verts, codes = [], []
        rings = [sps.Outline(k)] + [sps.Hole(k, h) for h in range(sps.HoleCount(k))]
        for ring in rings:
            pts = [uv(ring.CPoint(i)) for i in range(ring.PointCount())]
            if mirror:
                pts = [(-x, y) for x, y in pts]
            verts += pts + [pts[0]]
            codes += [Path.MOVETO] + [Path.LINETO] * (len(pts) - 1) + [Path.CLOSEPOLY]
        out.append(Path(verts, codes))
    return out


class Part:
    def __init__(self, b, f):
        self.ref, self.value = f.GetReference(), f.GetValue()
        self.fp = f.GetFPID().GetLibItemName().wx_str()
        self.dnp = f.IsDNP()
        a = f.GetAttributes()
        self.kind = 'smd' if a & pcbnew.FP_SMD else ('tht' if a & pcbnew.FP_THROUGH_HOLE else 'other')
        self.nobom = bool(a & pcbnew.FP_EXCLUDE_FROM_BOM)
        self.pos = uv(f.GetPosition())
        self.shown = f.Reference().IsVisible()
        self.fab, self.pads = [], []
        xs, ys = [], []
        for g in f.GraphicalItems():
            if g.GetLayer() == pcbnew.F_Fab and g.GetClass() == 'PCB_SHAPE':
                sps = pcbnew.SHAPE_POLY_SET()
                g.TransformShapeToPolygon(sps, pcbnew.F_Fab, 0, MAXERR, pcbnew.ERROR_INSIDE)
                self.fab.append(sps)
                bb = g.GetBoundingBox()
                for c in (uv(pcbnew.VECTOR2I(bb.GetLeft(), bb.GetTop())), uv(pcbnew.VECTOR2I(bb.GetRight(), bb.GetBottom()))):
                    xs.append(c[0]); ys.append(c[1])
        for p in f.Pads():
            lay = pcbnew.F_Cu if p.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
            sps = pcbnew.SHAPE_POLY_SET()
            p.TransformShapeToPolygon(sps, lay, 0, MAXERR, pcbnew.ERROR_INSIDE)
            hole = TO(p.GetDrillSize().x) if p.HasHole() else 0
            self.pads.append(dict(num=p.GetNumber(), c=uv(p.GetPosition()), sps=sps, hole=hole, net=p.GetNetname().split('/')[-1],
                                  front=p.IsOnLayer(pcbnew.F_Cu), back=p.IsOnLayer(pcbnew.B_Cu), plated=p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH,
                                  w=TO(p.GetSize(lay).x), h=TO(p.GetSize(lay).y)))
            if not self.fab:
                bb = p.GetBoundingBox()
                for c in (uv(pcbnew.VECTOR2I(bb.GetLeft(), bb.GetTop())), uv(pcbnew.VECTOR2I(bb.GetRight(), bb.GetBottom()))):
                    xs.append(c[0]); ys.append(c[1])
        self.box = (min(xs), min(ys), max(xs), max(ys))
        self.net = next((p['net'] for p in self.pads if p['net']), '')


def read_board(path):
    b = pcbnew.LoadBoard(path)
    parts = [Part(b, f) for f in b.GetFootprints()]
    parts.sort(key=lambda p: (re.match(r'[A-Z]+', p.ref).group(0), int(re.search(r'\d+', p.ref).group(0))))
    outl = pcbnew.SHAPE_POLY_SET()
    b.GetBoardPolygonOutlines(outl)
    texts = [(uv(d.GetPosition()), d.GetText(), TO(d.GetTextHeight()), d.GetLayer()) for d in b.GetDrawings() if d.GetClass() == 'PCB_TEXT']
    return b, parts, outl, texts


def sch_fields():
    """Maker's part numbers per name, from the schematic's own fields."""
    with tempfile.TemporaryDirectory() as t:
        out = os.path.join(t, 'bom.csv')
        subprocess.run(['kicad-cli', 'sch', 'export', 'bom', '--fields', 'Reference,Value,MPN,Manufacturer,DigiKey', '--labels', 'Ref,Value,MPN,Mfr,DigiKey',
                        '-o', out, os.path.join(MAIN, 'main-board.kicad_sch')], check=True, capture_output=True)
        return {r['Ref']: r for r in csv.DictReader(open(out))}


def fit(text, w, h, lo=3.0, hi=9.5):
    """Font size (pt) and rotation for a text in a box of w x h board mm; the larger of flat and upright."""
    n = max(len(text), 1)
    flat = min(h * PT * 0.80, w * PT / (0.66 * n))
    up = min(w * PT * 0.80, h * PT / (0.66 * n))
    size, rot = (flat, 0) if flat >= up * 0.98 else (up, 90)
    return max(lo, min(hi, size)), rot


def axes(fig, title, sub, mirror=False):
    W, H = PAGE
    w, h = 89.0 * SCALE, 59.9 * SCALE
    left, bottom = (W - w) / 2, H - 15.0 - h
    ax = fig.add_axes([left / W, bottom / H, w / W, h / H])
    ax.set_xlim(-44.5, 44.5); ax.set_ylim(-29.95, 29.95); ax.set_aspect('equal'); ax.axis('off')
    fig.text(left / W, 1 - 7.0 / H, title, fontsize=13, weight='bold', va='center')
    fig.text(1 - left / W, 1 - 7.0 / H, sub, fontsize=8, va='center', ha='right')
    return ax, left, bottom


def draw_board(ax, outl, parts, mirror=False, pads='front'):
    for p in paths(outl, mirror):
        ax.add_patch(PathPatch(p, fc='#fbfaf5', ec='k', lw=1.0, zorder=0))
    for pt in parts:
        for pd in pt.pads:
            if pads == 'front' and not pd['front']:
                continue
            if pads == 'back' and not pd['back']:
                continue
            for p in paths(pd['sps'], mirror):
                ax.add_patch(PathPatch(p, fc='#d9d9d9', ec='none', zorder=1))
            if pd['hole']:
                c = (-pd['c'][0], pd['c'][1]) if mirror else pd['c']
                ax.add_patch(Circle(c, pd['hole'] / 2, fc='white', ec='#888888', lw=0.3, zorder=1.5))


def draw_fab(ax, pt, col='k'):
    for sps in pt.fab:
        for p in paths(sps):
            ax.add_patch(PathPatch(p, fc=col, ec='none', zorder=3))


def footer(fig, left, bottom, cols):
    W, H = PAGE
    cw = (W - 2 * left) / len(cols)
    for i, lines in enumerate(cols):
        txt = '\n'.join(textwrap.fill(l, 92, subsequent_indent='   ') for l in lines)
        fig.text((left + i * cw) / W, (bottom - 2.0) / H, txt, fontsize=6.3, va='top', ha='left', linespacing=1.3)


def page_names(pdf, parts, outl, what):
    names = what == 'names'
    fig = plt.figure(figsize=(PAGE[0] / 25.4, PAGE[1] / 25.4))
    title = 'Main board rev 3.2 - door side - ' + ('part names (all 120)' if names else 'values')
    ax, left, bottom = axes(fig, title, 'fab issue %s  |  seen from the door, the face with every part  |  4.25 : 1  |  page %d of 4' % (ISSUE, 1 if names else 2))
    draw_board(ax, outl, parts)
    for pt in parts:
        col = '#b03a2e' if pt.dnp else 'k'
        draw_fab(ax, pt, col)
        x0, y0, x1, y1 = pt.box
        w, h = x1 - x0, y1 - y0
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if pt.ref.startswith('H'):
            txt = pt.ref if names else 'M3'
        elif pt.ref.startswith('TP'):
            txt = pt.ref if names else pt.value
        elif names:
            txt = pt.ref
        elif pt.dnp:
            txt = 'not fitted'
        elif pt.ref.startswith('J'):
            txt = {'J3': 'Pi wires 9', 'J4': 'Pi wires 4', 'J7': 'echo tap'}.get(pt.ref, pt.value.replace('B2B-XH-A', 'XH 2').replace('B4B-XH-A', 'XH 4').replace(' header', ''))
        elif pt.ref[0] in 'RC' and not pt.ref.startswith('C5') and pt.ref not in ('C6', 'C7'):
            txt = pt.value.split()[0]                      # the tolerance and voltage are in the list on page 3
        elif pt.ref.startswith('F'):
            txt = pt.value.split()[0] + ' A'
        else:
            txt = pt.value
        if pt.ref.startswith('TP'):                         # the name beside the bare pad
            size = 4.6
            ax.text(cx, y1 + 0.12, txt, fontsize=size, ha='center', va='bottom', color='#1f618d', zorder=6)
            continue
        tw, th = w - 0.25, h - 0.25
        lines = [txt]
        if not names and len(txt) > 7 and min(tw, th) > 2.2 and ' ' in txt:
            k = txt.rfind(' ', 0, len(txt) // 2 + 3)
            lines = [txt[:k], txt[k + 1:]] if k > 0 else [txt]
        n = max(len(l) for l in lines)
        size, rot = fit('x' * n, tw, th / len(lines) if tw >= th else th, hi=9.0)
        if len(lines) > 1 and th > tw:
            size, rot = fit('x' * n, tw / len(lines), th, hi=9.0)
            rot = 90
        ax.text(cx, cy, '\n'.join(lines), fontsize=size, rotation=rot, ha='center', va='center', color=col, zorder=7, linespacing=0.95,
                bbox=dict(boxstyle='square,pad=0.08', fc='white', ec='none', alpha=0.80) if (pt.kind != 'other') else None)
        if pt.dnp:
            ax.plot([x0, x1], [y0, y1], color='#b03a2e', lw=0.5, zorder=5)
            ax.plot([x0, x1], [y1, y0], color='#b03a2e', lw=0.5, zorder=5)
        # pad 1: chips, diodes, the three can capacitors, the module, the connectors
        if pt.ref[0] in 'UDJ' or pt.ref in ('C5', 'C6', 'C7', 'PS1'):
            p1 = next((pd for pd in pt.pads if pd['num'] == '1'), None)
            if p1:
                ax.add_patch(Circle(p1['c'], 0.22 if pt.ref[0] == 'U' else 0.30, fc='#c0392b', ec='none', zorder=9))
    shown = sum(1 for p in parts if p.shown)
    footer(fig, left, bottom, [
        ['Red dot = pad 1.  Chips U1, U2, U100: pin 1.  D1, D2: the cathode, the end with the band.  C5, C6, C7: the + lead (the can\'s stripe marks the - lead).',
         'PS1: pin 1, at the end the board marks "+Vo".  Connectors: pin 1.',
         'Red, crossed out = not fitted: R8, R9 (5 V trim), R20 to R25 (echo tap), R27 (amplifier logic from the Pi). Their pads still get paste; leave them empty.'],
        ['%d of the 120 names are printed on the board, %d are not: this drawing carries all of them.' % (shown, len(parts) - shown),
         'H1 to H4: holes for the M3 x 8 screws into the carrier\'s posts. Nothing is soldered there.',
         'TP1 to TP20 (no TP18): bare round pads to probe. No paste, no part. Their uses are on page 4.'],
        ['Hotplate: every surface-mount part, this face up. Then by iron: the through-hole parts, fitted from this face and soldered on the back.',
         'The 13 Pi signal wires (J3, J4) go the other way: pushed in from the back, soldered on this face.',
         'Source: main-board.kicad_pcb (rev 3.2, fab issue %s); gen/assembly_rev32.py.' % ISSUE],
    ] if names else [
        ['Short values on the drawing: resistors and capacitors without tolerance and voltage. The full value, the size and the maker\'s part number are on page 3.',
         'Red dot = pad 1, as on page 1.  "not fitted" = leave empty (R8, R9, R20 to R25, R27).'],
        ['Same-looking parts with different values sit side by side, above all the 0603 capacitors round the amplifier U100:',
         '0.1u, 0.22u, 1u (25 V and 50 V) and 2.2u. Place one value at a time from page 3 and tick it off.'],
        ['Fuses: 5 A = F1, 10 A = F2, 1 A = F3 (the same body, read the marking); 0.2 A = F4 (1206); 2.6 A = F5 (2920).',
         'Source: main-board.kicad_pcb (rev 3.2, fab issue %s); gen/assembly_rev32.py.' % ISSUE],
    ])
    pdf.savefig(fig)
    plt.close(fig)
    return fig


def page_list(pdf, parts, fields):
    fig = plt.figure(figsize=(PAGE[0] / 25.4, PAGE[1] / 25.4))
    W, H = PAGE
    fig.text(20 / W, 1 - 9.0 / H, 'Main board rev 3.2 - placing list, value by value', fontsize=13, weight='bold', va='center')
    fig.text(1 - 20 / W, 1 - 9.0 / H, 'fab issue %s  |  page 3 of 4' % ISSUE, fontsize=8, va='center', ha='right')
    smd = [p for p in parts if p.kind == 'smd' and not p.dnp]
    rows = []                                              # (heading | None, count, value, size, maker's part, names)
    used = set()
    for head, test in GROUPS:
        grp = [p for p in smd if test(p.ref, p.value, p.fp)]
        keyed = {}
        for p in grp:
            keyed.setdefault(fields.get(p.ref, {}).get('MPN', '') or p.value, []).append(p)
            used.add(p.ref)
        first = True
        for mpn, ps in sorted(keyed.items(), key=lambda kv: (-len(kv[1]), kv[1][0].value)):
            size = re.search(r'(0603|0805|1206|2920|SMB|SOT-23-5|HTSSOP-20|HTSSOP-48|SRR1260|CSBA0850|NANO2)', ps[0].fp)
            vals = []
            for p in ps:                                    # the same part under two spellings of its value: show both
                if p.value not in vals:
                    vals.append(p.value)
            rows.append((head if first else '', len(ps), ' = '.join(vals), size.group(1) if size else '', '%s %s' % (fields.get(ps[0].ref, {}).get('Mfr', ''), mpn),
                         ', '.join(p.ref for p in ps)))
            first = False
    assert used == {p.ref for p in smd}, sorted({p.ref for p in smd} - used)
    n_smd = len(smd)
    tht = {p.ref: p for p in parts if p.kind == 'tht'}
    rows2 = []
    for ref in THT_ORDER:
        p = tht[ref]
        fl = fields.get(ref, {})
        mpn = ('%s %s' % (fl.get('Mfr', ''), fl.get('MPN', ''))).strip()
        if ref == 'LK1':
            mpn = 'tinned copper wire, 1.0 mm (holes 1.3)'
        if ref in ('J10', 'J11'):
            mpn = 'pin header 1 x 4, 2.54 mm, straight (not in the DigiKey basket)'
        rows2.append((ref, p.value, mpn, {'LK1': 'bridge 7.62 long, flat on the board', 'J2': 'Pi power; 16 contacts and 4 shell stakes, its mouth at the bottom edge; pin ends only 0.5 behind the board',
                                          'C5': '+ lead in pad 1 (red dot)', 'C6': '+ lead in pad 1 (red dot)', 'C7': '+ lead in pad 1 (red dot)',
                                          'PS1': 'last; 13 pins; pin 1 at the end marked "+Vo"'}.get(ref, CONN.get(ref, ''))))
    dnp = [p for p in parts if p.dnp]
    y = 1 - 20.0 / H
    lh = 4.55 / H

    def line(cells, xs, weight='normal', size=7.6, color='k'):
        nonlocal y
        for c, x in zip(cells, xs):
            fig.text(x / W, y, c, fontsize=size, weight=weight, va='center', color=color)
        y -= lh
    xs = (20, 58, 70, 104, 124, 205)
    fig.text(20 / W, y, 'A. Hotplate: %d surface-mount parts, door side up. Paste through the stencil, then place one line at a time.' % n_smd, fontsize=9, weight='bold', va='center')
    y -= lh * 1.3
    line(('Group', 'Qty', 'Value', 'Size', "Maker's part", 'Places'), xs, 'bold')
    fig.add_artist(plt.Line2D([20 / W, 1 - 20 / W], [y + lh * 0.5, y + lh * 0.5], color='k', lw=0.5))
    for head, n, val, size, mpn, refs in rows:
        if head:
            y -= lh * 0.25
        line((head, str(n), val, size, mpn, refs), xs, size=7.4)
    y -= lh * 0.6
    fig.text(20 / W, y, 'B. By iron, after the hotplate: %d through-hole parts, fitted from the door side, soldered on the back, in this order (low to high).' % len(rows2), fontsize=9, weight='bold', va='center')
    y -= lh * 1.3
    xs2 = (20, 40, 104, 205)
    line(('Place', 'Value', "Maker's part", 'Note'), xs2, 'bold')
    fig.add_artist(plt.Line2D([20 / W, 1 - 20 / W], [y + lh * 0.5, y + lh * 0.5], color='k', lw=0.5))
    for r in rows2:
        line(r, xs2, size=7.4)
    y -= lh * 0.6
    fig.text(20 / W, y, 'C. Left empty', fontsize=9, weight='bold', va='center')
    y -= lh * 1.3
    line(('Not fitted (%d):' % len(dnp), '', ', '.join(p.ref for p in dnp) + '  -  options; their pads get paste and stay empty', ''), xs2, size=7.4)
    line(('Wire pads:', '', 'J3, J4: the 13 Pi signal wires, pushed in from the back and soldered on the door side (gpio-leads.md).  J7: empty.', ''), xs2, size=7.4)
    line(('No part:', '', 'TP1 to TP17, TP19, TP20 (19 bare test pads); H1 to H4 (screw holes).', ''), xs2, size=7.4)
    y -= lh * 0.4
    tot = n_smd + len(rows2) + len(dnp) + 3 + 19 + 4
    fig.text(20 / W, y, 'Count: %d surface-mount fitted + %d not fitted + %d through-hole parts + 3 wire-pad blocks (J3, J4, J7) + 19 test pads + 4 holes = %d names.' % (
        n_smd, len(dnp), len(rows2), tot), fontsize=7.4, va='center')
    assert tot == len(parts), (tot, len(parts))
    pdf.savefig(fig)
    plt.close(fig)
    return rows, rows2


def page_test(pdf, parts, outl, texts):
    fig = plt.figure(figsize=(PAGE[0] / 25.4, PAGE[1] / 25.4))
    W, H = PAGE
    fig.text(12 / W, 1 - 7.0 / H, 'Main board rev 3.2 - test pads, connectors and the back face', fontsize=13, weight='bold', va='center')
    fig.text(1 - 12 / W, 1 - 7.0 / H, 'fab issue %s  |  page 4 of 4' % ISSUE, fontsize=8, va='center', ha='right')
    s = 2.15                                               # both views at 2.15 : 1
    w, h = 89.0 * s, 59.9 * s
    ax = fig.add_axes([12 / W, (H - 16 - h) / H, w / W, h / H]); ax.set_xlim(-44.5, 44.5); ax.set_ylim(-29.95, 29.95); ax.set_aspect('equal'); ax.axis('off')
    draw_board(ax, outl, parts)
    k = s * 72 / 25.4
    for pt in parts:
        if pt.ref.startswith('TP'):
            ax.add_patch(Circle(pt.pads[0]['c'], 0.95, fc='#f5b041', ec='#b9770e', lw=0.5, zorder=4))
            ax.text(pt.pads[0]['c'][0], pt.pads[0]['c'][1] + 1.15, '%s %s' % (pt.ref, pt.value), fontsize=5.6, ha='center', va='bottom', weight='bold', color='#784212', zorder=8,
                    bbox=dict(boxstyle='square,pad=0.05', fc='white', ec='none', alpha=0.75))
        else:
            draw_fab(ax, pt, '#909497')
            if pt.ref[0] == 'J' or pt.ref in ('PS1', 'U1', 'U100', 'F1', 'F2', 'F3', 'F5', 'L1', 'LK1', 'C5', 'C6', 'C7'):
                x0, y0, x1, y1 = pt.box
                ax.text((x0 + x1) / 2, (y0 + y1) / 2, pt.ref, fontsize=min(7.0, max(4.2, min(x1 - x0, y1 - y0) * k * 0.55)), ha='center', va='center', color='#1b2631', zorder=7)
    fig.text(12 / W, (H - 16 - h - 4) / H, 'Door side, seen from the door, 2.15 : 1. Orange = the 19 test pads (bare, 1.5 across).', fontsize=7.5, va='top')
    # the back, seen from the back
    ax2 = fig.add_axes([(W - 12 - w) / W, (H - 16 - h) / H, w / W, h / H]); ax2.set_xlim(-44.5, 44.5); ax2.set_ylim(-29.95, 29.95); ax2.set_aspect('equal'); ax2.axis('off')
    draw_board(ax2, outl, parts, mirror=True, pads='back')
    for (x, yv), t, hgt, lay in texts:
        if lay == pcbnew.B_SilkS:
            ax2.text(-x, yv, t, fontsize=max(4.5, hgt * k * 0.95), ha='center', va='center', color='k', zorder=6)
    for pt in parts:
        if pt.kind == 'tht':
            x0, y0, x1, y1 = pt.box
            ax2.add_patch(Rectangle((-x1, y0), x1 - x0, y1 - y0, fc='none', ec='#2874a6', lw=0.5, ls=(0, (3, 2)), zorder=5))
            ax2.text(-x0 - 0.2, y1 - 0.2, pt.ref, fontsize=5.0, ha='right', va='top', color='#2874a6', zorder=7)
    fig.text((W - 12 - w) / W, (H - 16 - h - 4) / H, 'Back face (toward the display), seen from the back: left and right are swapped against the other views. No part is fitted here.\n'
             'Blue, dashed = the through-hole parts on the other face, whose pins are soldered here; black = the names printed on this face.\n'
             'Cut the leads of C5, C6, C7 and LK1 to 1.5 or less behind the board.', fontsize=7.5, va='top', linespacing=1.3)
    # tables
    y0t = (H - 16 - h - 22) / H
    lh = 4.3 / H
    y = y0t
    cols = (12, 24, 38, 62, 76, 92)
    for c, x in zip(('Pad', 'Name', 'Net', 'From left', 'From bottom', 'What it is; what stands beside it'), cols):
        fig.text(x / W, y, c, fontsize=7, weight='bold', va='center')
    y -= lh
    near = [p for p in parts if not p.ref.startswith(('TP', 'H'))]
    tps = [p for p in parts if p.ref.startswith('TP')]
    tprows = []
    for pt in tps:
        c = pt.pads[0]['c']
        def gap(q):
            x0, y0, x1, y1 = q.box
            dx = max(x0 - c[0], 0, c[0] - x1); dy = max(y0 - c[1], 0, c[1] - y1)
            return (dx * dx + dy * dy) ** 0.5
        nb = sorted(near, key=gap)[:2]
        def side(q):
            x0, y0, x1, y1 = q.box
            qx, qy = (x0 + x1) / 2, (y0 + y1) / 2
            dx, dy = c[0] - qx, c[1] - qy
            return ('right of' if dx > 0 else 'left of') if abs(dx) / max(x1 - x0, 0.1) > abs(dy) / max(y1 - y0, 0.1) else ('above' if dy > 0 else 'below')
        where = '; '.join('%s %s' % (side(q), q.ref) for q in nb)
        tprows.append((pt.ref, pt.value, pt.net, c[0] + U0, c[1] + V0, TPUSE[pt.ref], where))
        for cell, x in zip((pt.ref, pt.value, pt.net, '%.1f' % (c[0] + U0), '%.1f' % (c[1] + V0), '%s; %s' % (TPUSE[pt.ref], where)), cols):
            fig.text(x / W, y, cell, fontsize=6.6, va='center')
        y -= lh
    y = y0t
    cols2 = (226, 236, 296, 362)
    for c, x in zip(('Place', 'What plugs in or is soldered', 'Pin 1 (red dot, pages 1 and 2): net; from left, bottom', 'Printed on the back'), cols2):
        fig.text(x / W, y, c, fontsize=7, weight='bold', va='center')
    y -= lh
    back = {'J1': '20V IN, +', 'J2': 'PI USB-C', 'J3': 'PI 1-15', 'J4': 'PI 35-40', 'J5': '(door side: RADAR)', 'J6': 'TOUCH', 'J7': 'ECHO', 'J8': 'SPK L (door side: +)',
            'J9': 'SPK R, +', 'J10': 'BME680', 'J11': 'VEML6030'}
    for ref in ('J1', 'J2', 'J3', 'J4', 'J5', 'J6', 'J7', 'J8', 'J9', 'J10', 'J11'):
        pt = next(p for p in parts if p.ref == ref)
        p1 = next(pd for pd in pt.pads if pd['num'] in ('1', 'A1'))
        for cell, x in zip((ref, CONN[ref], '%s; %.1f, %.1f' % (p1['net'] or '-', p1['c'][0] + U0, p1['c'][1] + V0), back[ref]), cols2):
            fig.text(x / W, y, cell, fontsize=6.6, va='center')
        y -= lh
    y -= lh * 0.5
    for t in ('Distances in mm on the door side: from the board\'s left edge and from its bottom edge (the edge with the sockets), to the pad\'s centre.',
              'PVDD, the amplifier\'s supply, has no test pad: probe pad 2 of the fuse F5 (the pad nearer the right-hand edge).',
              'Ground for the probe: TP7, TP15, TP17 or TP20.'):
        fig.text(226 / W, y, t, fontsize=6.6, va='center')
        y -= lh
    pdf.savefig(fig)
    plt.close(fig)
    return tprows


def main(board, out):
    b, parts, outl, texts = read_board(board)
    assert len(parts) == 120, len(parts)
    fields = sch_fields()
    with PdfPages(out) as pdf:
        page_names(pdf, parts, outl, 'names')
        page_names(pdf, parts, outl, 'values')
        rows, rows2 = page_list(pdf, parts, fields)
        tprows = page_test(pdf, parts, outl, texts)
        d = pdf.infodict()
        d['Title'] = 'HA panel main board rev 3.2 - assembly drawing (fab issue %s)' % ISSUE
        d['Subject'] = 'All 120 part names and values, placing list, test pads; from main-board.kicad_pcb'
    print('wrote %s: 4 pages, %d parts (%d names printed on the board, %d not)' % (out, len(parts), sum(1 for p in parts if p.shown), sum(1 for p in parts if not p.shown)))
    return parts, tprows


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(MAIN, 'main-board.kicad_pcb'),
         sys.argv[2] if len(sys.argv) > 2 else os.path.join(MAIN, 'main-board-rev3.2-assembly.pdf'))
