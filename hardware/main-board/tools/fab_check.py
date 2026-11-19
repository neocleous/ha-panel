"""Check a JLC fab set against the board it was made from: fab_check.py <board.kicad_pcb> <fab dir>/gerbers [render.png]

Reads the Gerber and Excellon files themselves (a small reader: apertures, flashes, arcs; holes per tool) and compares
with what KiCad's Python reads from the board:
  1. every expected file is there, and each says what it is (X2 FileFunction);
  2. copper layers: one round flash of the via's diameter at every via, on every copper layer;
  3. soldermask: no opening flashed at a via (vias stay covered), one opening per pad that has one;
  4. paste (if plotted): one aperture per pad that has paste;
  5. outline: its extent, and the number of arcs;
  6. drill files: holes per diameter, plated and not, against the board's vias and pad holes;
  7. the job file: board size, layer count, stack-up, finish;
  8. the stored pours are up to date (a refill of a copy gives the same areas).
Then draws every layer with pygerber for a look."""
import glob
import json
import os
import re
import sys
from collections import Counter

import pcbnew

TO = pcbnew.ToMM


def read_gerber(path):
    txt = open(path).read()
    ff = re.search(r'%TF\.FileFunction,([^*]*)\*%', txt)
    aps = {}
    for m in re.finditer(r'%ADD(\d+)([A-Za-z0-9_]+),?([^*]*)\*%', txt):
        aps[int(m.group(1))] = (m.group(2), m.group(3))
    cur, flashes, arcs, regions, draws = None, [], 0, 0, 0
    x = y = 0
    mode = 'G01'
    for line in txt.split('\n'):
        line = line.strip()
        if line.startswith('%'):
            continue
        m = re.match(r'^(?:G54)?D(\d+)\*$', line)
        if m and int(m.group(1)) >= 10:
            cur = int(m.group(1))
            continue
        if line.startswith('G36'):
            regions += 1
        g = re.match(r'^(G0[123])\*?', line)
        if g:
            mode = g.group(1)
            line = line[len(g.group(1)):]
        m = re.match(r'^(?:X(-?\d+))?(?:Y(-?\d+))?(?:I(-?\d+))?(?:J(-?\d+))?D0([123])\*$', line)
        if m:
            if m.group(1) is not None:
                x = int(m.group(1)) / 1e6
            if m.group(2) is not None:
                y = int(m.group(2)) / 1e6
            d = m.group(5)
            if d == '3':
                flashes.append((round(x, 4), round(-y, 4), cur))
            elif d == '1':
                draws += 1
                if mode in ('G02', 'G03'):
                    arcs += 1
    xs = [int(v) / 1e6 for v in re.findall(r'X(-?\d+)', txt)]
    ys = [-int(v) / 1e6 for v in re.findall(r'Y(-?\d+)', txt)]
    return dict(function=ff.group(1) if ff else '', aps=aps, flashes=flashes, arcs=arcs, regions=regions, draws=draws,
                bbox=(min(xs), min(ys), max(xs), max(ys)) if xs else None)


def read_drill(path):
    txt = open(path).read()
    tools = {int(t): float(d) for t, d in re.findall(r'^T(\d+)C([\d.]+)', txt, re.M)}
    cur, n, slots = None, Counter(), Counter()
    for line in txt.split('\n'):
        m = re.match(r'^T(\d+)$', line.strip())
        if m:
            cur = int(m.group(1))
            continue
        if re.match(r'^X-?[\d.]+Y-?[\d.]+G85', line):
            slots[tools[cur]] += 1
            n[tools[cur]] += 1
        elif re.match(r'^X-?[\d.]+Y-?[\d.]+$', line.strip()):
            n[tools[cur]] += 1
    return n, slots


def main(board, gdir, png=None):
    b = pcbnew.LoadBoard(board)
    ok = True

    def say(cond, text):
        nonlocal ok
        ok = ok and cond
        print(('  ok   ' if cond else '  FAIL ') + text)
    files = {os.path.basename(f): f for f in glob.glob(os.path.join(gdir, '*'))}
    stem = [f for f in files if f.endswith('-Edge_Cuts.gm1')][0][:-len('-Edge_Cuts.gm1')]
    ncu = b.GetCopperLayerCount()
    cu = {'F_Cu.gtl': pcbnew.F_Cu, 'B_Cu.gbl': pcbnew.B_Cu}
    if ncu == 4:
        cu.update({'In1_Cu.g1': pcbnew.In1_Cu, 'In2_Cu.g2': pcbnew.In2_Cu})
    want = list(cu) + ['F_Mask.gts', 'B_Mask.gbs', 'F_Silkscreen.gto', 'B_Silkscreen.gbo', 'Edge_Cuts.gm1', 'PTH.drl', 'NPTH.drl', 'job.gbrjob']
    print('1. files (%s-...)' % stem)
    for w in want:
        say('%s-%s' % (stem, w) in files, w)
    extra = sorted(set(files) - {'%s-%s' % (stem, w) for w in want})
    print('     also in the set: %s' % (', '.join(e[len(stem) + 1:] for e in extra) or 'nothing'))
    G = {k[len(stem) + 1:]: read_gerber(v) for k, v in files.items() if not k.endswith(('.drl', '.gbrjob'))}
    for k in sorted(G):
        print('     %-18s %-28s flashes %5d, drawn pieces %6d (arcs %d), filled regions %4d' % (k, G[k]['function'], len(G[k]['flashes']), G[k]['draws'], G[k]['arcs'], G[k]['regions']))
    vias = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
    print('2. vias on the copper layers (%d vias)' % len(vias))
    for k, lay in cu.items():
        g = G[k]
        pos = Counter((x, y) for x, y, a in g['flashes'] if g['aps'][a][0] == 'C')
        dia = {(x, y): float(g['aps'][a][1].split('X')[0]) for x, y, a in g['flashes'] if g['aps'][a][0] == 'C'}
        miss = [v for v in vias if (round(TO(v.GetPosition().x), 4), round(TO(v.GetPosition().y), 4)) not in pos]
        wrong = [v for v in vias if v not in miss and abs(dia[(round(TO(v.GetPosition().x), 4), round(TO(v.GetPosition().y), 4))] - TO(v.GetWidth(lay))) > 1e-4]
        say(not miss and not wrong, '%s: a round flash of the right diameter at every via (missing %d, wrong size %d)' % (k, len(miss), len(wrong)))
    print('3. soldermask')
    for k, lay in (('F_Mask.gts', pcbnew.F_Mask), ('B_Mask.gbs', pcbnew.B_Mask)):
        g = G[k]
        pos = {(x, y) for x, y, a in g['flashes']}
        pads = [(round(TO(p.GetPosition().x), 4), round(TO(p.GetPosition().y), 4)) for f in b.GetFootprints() for p in f.Pads() if p.IsOnLayer(lay)]
        padset = set(pads)
        open_via = [v for v in vias if (round(TO(v.GetPosition().x), 4), round(TO(v.GetPosition().y), 4)) in pos - padset]
        say(not open_via, '%s: no opening flashed at a via (%d)' % (k, len(open_via)))
        # pads whose shape is not centred on their position are flashed at the shape's place: count instead of matching
        say(len(g['flashes']) + g['regions'] >= len(pads) and len(g['flashes']) <= len(pads), '%s: %d openings flashed, %d drawn as regions, for %d pads with an opening' % (k, len(g['flashes']), g['regions'], len(pads)))
    print('4. paste')
    for k, lay in (('F_Paste.gtp', pcbnew.F_Paste), ('B_Paste.gbp', pcbnew.B_Paste)):
        n = sum(1 for f in b.GetFootprints() for p in f.Pads() if p.IsOnLayer(lay))
        if k in G:
            say(len(G[k]['flashes']) + G[k]['regions'] == n or len(G[k]['flashes']) == n, '%s: %d apertures for %d pasted pads' % (k, len(G[k]['flashes']), n))
        else:
            print('     %s: not in this set (the board has %d pasted pads on that face)' % (k, n))
    print('5. outline')
    bb = b.GetBoardEdgesBoundingBox()
    g = G['Edge_Cuts.gm1']
    w, h = g['bbox'][2] - g['bbox'][0], g['bbox'][3] - g['bbox'][1]
    arcs_board = sum(1 for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts and d.GetShape() in (pcbnew.SHAPE_T_ARC, pcbnew.SHAPE_T_CIRCLE))
    for f in b.GetFootprints():
        arcs_board += sum(1 for d in f.GraphicalItems() if d.GetLayer() == pcbnew.Edge_Cuts and d.GetClass() == 'PCB_SHAPE' and d.GetShape() in (pcbnew.SHAPE_T_ARC, pcbnew.SHAPE_T_CIRCLE))
    say(abs(w - TO(bb.GetWidth())) < 0.11 and abs(h - TO(bb.GetHeight())) < 0.11, 'extent %.2f x %.2f in the file; the board %.2f x %.2f with its 0.1 line' % (w, h, TO(bb.GetWidth()), TO(bb.GetHeight())))
    say(g['arcs'] >= arcs_board, 'arcs: %d in the file, %d arcs and circles on the board\'s outline layer' % (g['arcs'], arcs_board))
    print('6. holes')
    pth, slots = read_drill(files['%s-PTH.drl' % stem])
    npth, _ = read_drill(files['%s-NPTH.drl' % stem])
    exp_p, exp_n = Counter(), Counter()
    for v in vias:
        exp_p[round(TO(v.GetDrillValue()), 3)] += 1
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.HasHole():
                d = round(min(TO(p.GetDrillSize().x), TO(p.GetDrillSize().y)), 3)
                (exp_p if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH else exp_n)[d] += 1
    say(dict(pth) == dict(exp_p), 'plated: %s' % ', '.join('%d of %.2f' % (pth[d], d) for d in sorted(pth)) + ('' if dict(pth) == dict(exp_p) else '  expected %s' % dict(exp_p)))
    say(dict(npth) == dict(exp_n), 'not plated: %s' % (', '.join('%d of %.2f' % (npth[d], d) for d in sorted(npth)) or 'none') + ('' if dict(npth) == dict(exp_n) else '  expected %s' % dict(exp_n)))
    print('     slots (plated, oval holes): %s' % (dict(slots) or 'none'))
    print('7. job file')
    job = json.load(open(files['%s-job.gbrjob' % stem]))
    gs = job['GeneralSpecs']
    print('     size %s x %s, %s layers, thickness %s, finish %s; project %s rev %s' % (gs['Size']['X'], gs['Size']['Y'], gs['LayerNumber'], gs.get('BoardThickness'), gs.get('Finish', '-'),
                                                                                      job['Header'].get('GenerationSoftware', {}).get('Application', ''), gs.get('ProjectId', {}).get('Revision', '')))
    for m in job.get('MaterialStackup', []):
        if m.get('Type') in ('Copper', 'Dielectric'):
            print('       %-10s %-22s %s%s' % (m['Type'], m.get('Name', ''), m.get('Thickness', ''), ('  ' + m.get('Material', '') + (' er %s' % m['DielectricConstant'] if 'DielectricConstant' in m else '')) if m['Type'] == 'Dielectric' else ''))
    say(int(gs['LayerNumber']) == ncu, 'layer count %s' % gs['LayerNumber'])
    print('8. pours')
    def areas():
        out = []
        for z in b.Zones():
            if not z.GetIsRuleArea():
                z.CalculateFilledArea()
                out.append(z.GetFilledArea() / 1e12)
        return out
    a0 = areas()
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    a1 = areas()
    diff = max([abs(x - y) for x, y in zip(a0, a1)] or [0.0])
    say(diff < 0.005, '%d pours; a refill changes none by more than %.4f mm2 (the stored pours are current)' % (len(a0), diff))
    if png:
        from pygerber.gerberx3.api.v2 import GerberFile, ColorScheme, PixelFormatEnum, ImageFormatEnum
        from PIL import Image
        order = [k for k in ('F_Cu.gtl', 'In1_Cu.g1', 'In2_Cu.g2', 'B_Cu.gbl', 'F_Mask.gts', 'B_Mask.gbs', 'F_Silkscreen.gto', 'B_Silkscreen.gbo', 'F_Paste.gtp', 'B_Paste.gbp', 'Edge_Cuts.gm1') if k in G]
        ims = []
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            for k in order:
                out = os.path.join(t, k + '.png')
                GerberFile.from_file(files['%s-%s' % (stem, k)]).parse().render_raster(out, dpmm=14, color_scheme=ColorScheme.COPPER_ALPHA if 'Cu' in k else ColorScheme.SILK, pixel_format=PixelFormatEnum.RGBA, image_format=ImageFormatEnum.PNG)
                ims.append((k, Image.open(out).convert('RGBA')))
            cols = 4 if len(ims) > 6 else 3
            W = max(i.size[0] for k, i in ims) + 20
            H = max(i.size[1] for k, i in ims) + 40
            rows = (len(ims) + cols - 1) // cols
            sheet = Image.new('RGB', (W * cols, H * rows), 'white')
            from PIL import ImageDraw
            dr = ImageDraw.Draw(sheet)
            for n, (k, im) in enumerate(ims):
                bg = Image.new('RGBA', im.size, (20, 40, 30, 255))
                bg.alpha_composite(im)
                x0, y0 = (n % cols) * W + 10, (n // cols) * H + 30
                sheet.paste(bg.convert('RGB'), (x0, y0))
                dr.text((x0, y0 - 22), '%s-%s' % (stem, k), fill='black')
            sheet.save(png)
            print('drawn: %s (%d layers, as the files hold them: the back layers are seen through the board)' % (png, len(ims)))
    print('RESULT: %s' % ('all checks passed' if ok else 'CHECK FAILED'))
    return ok


if __name__ == '__main__':
    sys.exit(0 if main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None) else 1)
