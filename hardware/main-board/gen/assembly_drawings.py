"""Assembly drawings for the main board, the mic strip and the touch board (block 3 part 3, 2026-11-09).

Each page = one side of one board, from its fab layer (outlines, pin-1 and polarity marks, ${REFERENCE}), the outline and,
for back views, the back silkscreen (test-pad names), plotted by kicad-cli as PDF without values, with DNP footprints crossed out
and their references struck through, cropped to the drawn area and scaled onto an A3 (main board) or A4 landscape page
with a title and notes; the result stays vector. Back views are mirrored, i.e.
drawn as seen from the back. Nothing in the boards is changed: each is plotted from a moved copy in a temporary folder.

Run from the repo root: python3 hardware/main-board/gen/assembly_drawings.py
Needs kicad-cli 9, pdftoppm, Pillow, reportlab, pypdf."""
import os
import subprocess
import tempfile

import pcbnew

from pypdf import PdfReader, PdfWriter, Transformation
from PIL import Image
from reportlab.lib.pagesizes import A3, A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

HW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')

# (board file, output pdf, page size, pages); page = (layers, mirror, sketch pads, hide silk references, title, notes)
SETS = [
    ('main-board/main-board.kicad_pcb', 'main-board/main-board-assembly.pdf', A3, [
        ('F.Fab,Edge.Cuts', False, False, True, 'Main board rev 2.1 - front (Pi side): every SMD part and the THT bodies',
         ['DNP, crossed out: R8, R9 (V20 trim), R20-R25 (D4a links; topology A), R27 (amp logic from the Pi 3V3).',
          'Fitted options: R26 (amp logic from the board LDO), R7 (NID enable from the eFuse PGOOD), R14-R16 0 R (I2S series).',
          'Polarity: D1 SMBJ22A, D2 SMBJ6.0A-E (band = cathode); C5, C6, C7 (+); ICs: pin 1 at the chamfered corner.',
          'THT, fitted from this side and soldered on the back after the hotplate: J1, J5, J6, J8, J9 (XH), J10 (2x4 header), '
          'C5, C6, C7, PS1.',
          'J3, J4: holes for the GPIO lead wires (no part). J7: empty in topology A. PVDD: probe F5 pin 2 here (bench only).']),
        ('B.Mask,B.Silkscreen,Edge.Cuts', True, False, False, 'Main board rev 2.1 - back (door side), seen from the back',
         ['J2 (USB4085) and LK1 (1.0 mm tinned wire) are fitted from this side and soldered on the front: fit them before '
          'the tall front parts.',
          'Black = exposed copper on this side: the THT joints and the bare test pads TP1-TP20 (no TP18); nothing to fit on '
          'the pads.',
          'Ground returns: TP7, TP15, TP17, TP20.']),
    ]),
    ('mic-strip/mic-strip.kicad_pcb', 'mic-strip/mic-strip-assembly.pdf', A4, [
        ('B.Fab,B.Silkscreen,Edge.Cuts', True, True, True, 'Mic strip (one design, build two) - back (parts side), seen from the back',
         ['All parts fitted, none DNP. R5 0 R on both strips (L/R comes from the cable SEL wire).',
          'MK1 sits over the 0.8 mm port hole: keep paste, flux and residue out of the hole.',
          'D1-D3 ESD321: pin 1 = GND = the dot / notch on the body; here the bar end of the fab symbol and the closed end '
          'of the silk bracket (right). Check by diode test.',
          'J1 wire pads, top to bottom on this view: 1 VDD, 2 GND, 3 CLK, 4 SEL, 5 DATA (cable order).']),
    ]),
    ('touch-board/touch-board.kicad_pcb', 'touch-board/touch-board-assembly.pdf', A4, [
        ('B.Fab,B.Silkscreen,Edge.Cuts', True, True, True, 'Touch board rev D - back (parts side), seen from the back',
         ['All parts fitted, none DNP. U1 AT42QT1070 from Daniel\'s stock (D56); pin 1 at the chamfered corner.',
          'J1 HOST pads (labelled VCC, GND, SDA, SCL): the touch lead from main-board J6 is soldered here, no paste.',
          'The front carries only the four electrodes: KEY0-KEY3 left to right, seen from the front.']),
    ]),
]


def plot_pdf(board, layers, mirror, sketch, out_pdf):
    cmd = ['kicad-cli', 'pcb', 'export', 'pdf', '--mode-single', '--exclude-value',
           '--crossout-DNP-footprints-on-fab-layers', '--black-and-white', '--layers', layers, '-o', out_pdf, board]
    if mirror:
        cmd.insert(4, '--mirror')
    if sketch:
        cmd.insert(4, '--sketch-pads-on-fab-layers')
    subprocess.run(cmd, check=True, capture_output=True)


def ink_box(pdf, tmp, idx):
    """Bounding box of everything drawn on page 1, in PDF points (x0, y0, x1, y1), from a 100 dpi grey render."""
    stem = os.path.join(tmp, f'r{idx}')
    subprocess.run(['pdftoppm', '-r', '100', '-gray', '-singlefile', '-png', pdf, stem], check=True)
    im = Image.open(stem + '.png').convert('L')
    box = im.point(lambda v: 255 if v < 200 else 0).getbbox()
    pw, ph = im.size
    page_w = float(PdfReader(pdf).pages[0].mediabox.width)
    k = page_w / pw
    x0, y0t, x1, y1t = box
    return x0 * k, (ph - y1t) * k, x1 * k, (ph - y0t) * k


def _fab_box(fp, layer):
    """(centre, width, height) of the part's graphics on its fab layer, or None. Boxes over 100 mm are ignored
    (pcbnew 9.0.9 returns an unset box for some filled shapes)."""
    xs, ys = [], []
    lim = pcbnew.FromMM(100)
    for g in fp.GraphicalItems():
        if g.GetClass() != 'PCB_TEXT' and g.GetLayer() == layer:
            b = g.GetBoundingBox()
            if 0 <= b.GetWidth() < lim and 0 <= b.GetHeight() < lim:
                xs += [b.GetLeft(), b.GetRight()]
                ys += [b.GetTop(), b.GetBottom()]
    if not xs:
        return None
    return (pcbnew.VECTOR2I((min(xs) + max(xs)) // 2, (min(ys) + max(ys)) // 2), max(xs) - min(xs), max(ys) - min(ys))


def on_page_copy(board, hide_silk_refs, tmp, idx):
    """Copy of the board for plotting only:
    - footprints and drawings moved so the outline starts at (40, 40) mm (the boards sit at the page origin with
      negative y, and a PDF plot clips everything outside the page);
    - optionally the silkscreen reference fields hidden, so each reference appears once, from the fab layer;
    - each fab-layer reference text centred on its part's fab outline and shrunk to fit inside it (minimum 0.3 mm),
      so neighbours don't overlap."""
    b = pcbnew.LoadBoard(board)
    bb = b.GetBoardEdgesBoundingBox()
    off = pcbnew.VECTOR2I(pcbnew.FromMM(40) - bb.GetLeft(), pcbnew.FromMM(40) - bb.GetTop())
    for fp in b.GetFootprints():
        if hide_silk_refs and fp.Reference().GetLayerName().endswith('Silkscreen'):
            fp.Reference().SetVisible(False)
        for t in fp.GraphicalItems():
            if t.GetClass() == 'PCB_TEXT' and t.GetLayerName().endswith('Fab') and '${REFERENCE}' in t.GetText():
                body = _fab_box(fp, t.GetLayer())
                if body is None:
                    continue
                centre, bw, bh = body
                t.SetPosition(centre)
                tb = t.GetBoundingBox()
                k = min(1.0, 0.85 * bw / max(tb.GetWidth(), 1), 0.85 * bh / max(tb.GetHeight(), 1))
                if k < 1.0:
                    t.SetTextSize(pcbnew.VECTOR2I(max(pcbnew.FromMM(0.3), int(t.GetTextWidth() * k)),
                                                  max(pcbnew.FromMM(0.3), int(t.GetTextHeight() * k))))
                    t.SetTextThickness(max(pcbnew.FromMM(0.05), int(t.GetTextThickness() * k)))
        fp.Move(off)
    for d in b.GetDrawings():
        d.Move(off)
    out = os.path.join(tmp, f'b{idx}', os.path.basename(board))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pcbnew.SaveBoard(out, b)
    return out


def page(board, layers, mirror, sketch, hide, title, notes, size, tmp, idx):
    pdf = os.path.join(tmp, f'p{idx}.pdf')
    plot_pdf(on_page_copy(board, hide, tmp, idx), layers, mirror, sketch, pdf)
    x0, y0, x1, y1 = ink_box(pdf, tmp, idx)
    m = 2 * mm
    x0, y0, x1, y1 = x0 - m, y0 - m, x1 + m, y1 + m
    art = PdfReader(pdf).pages[0]
    art.mediabox.lower_left = (x0, y0)
    art.mediabox.upper_right = (x1, y1)
    aw, ah = x1 - x0, y1 - y0

    W, H = landscape(size)
    frame = os.path.join(tmp, f'f{idx}.pdf')
    c = canvas.Canvas(frame, pagesize=(W, H))
    c.setFont('Helvetica-Bold', 12)
    c.drawString(12 * mm, H - 12 * mm, title)
    c.setFont('Helvetica', 8)
    c.drawRightString(W - 12 * mm, H - 12 * mm, 'HA panel - assembly drawing - 2026-11-09 - from the KiCad fab layers')
    y = 12 * mm + 4 * mm * (len(notes) - 1)
    for n in notes:
        c.drawString(12 * mm, y, n)
        y -= 4 * mm
    c.save()

    top, bottom = H - 18 * mm, 12 * mm + 4 * mm * len(notes) + 2 * mm
    box_w, box_h = W - 24 * mm, top - bottom
    s = min(box_w / aw, box_h / ah)
    tx = 12 * mm + (box_w - aw * s) / 2 - x0 * s
    ty = bottom + (box_h - ah * s) / 2 - y0 * s
    base = PdfReader(frame).pages[0]
    base.merge_transformed_page(art, Transformation().scale(s).translate(tx, ty))
    return base, s


def main():
    with tempfile.TemporaryDirectory() as tmp:
        i = 0
        for board, out, size, pages in SETS:
            w = PdfWriter()
            for layers, mirror, sketch, hide, title, notes in pages:
                p, s = page(os.path.join(HW, board), layers, mirror, sketch, hide, title, notes, size, tmp, i)
                w.add_page(p)
                print(out, '|', title, '| scale %.2f : 1' % s)
                i += 1
            with open(os.path.join(HW, out), 'wb') as f:
                w.write(f)


if __name__ == '__main__':
    main()
