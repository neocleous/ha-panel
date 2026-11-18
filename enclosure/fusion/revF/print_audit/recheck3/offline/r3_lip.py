"""recheck3: the lip round the door opening as sliced (2 and 4 walls): printed footprint against the model in the lip's band, layer by layer,
at a side (world z 40..50, between two magnet seats), at the arch's shoulder (x 30..45) and at the top of the arch (x -8..8); line types; pictures."""
import numpy as np
from r3_gq import *
POS = (0.0, -30.0, 0.0)
bp = BedPart('shell', POS)
jobs = {'2 walls': G('H4_P3a_w2'), '4 walls': G('H4_P3a_w4')}
def wbox(x0, x1, z0, z1):                      # world x, z window -> bed x, y window
    return (x0 + 128.003, x1 + 128.003, z0 + 6.608, z1 + 6.608)
def zb(yw): return 6.799 - yw
places = [('side, viewer left (x 62..76, z 40..50)', wbox(62, 76, 40, 50)), ('side, viewer right (x -76..-62, z 40..50)', wbox(-76, -62, 40, 50)),
          ('shoulder (x 30..45, z 120..150)', wbox(30, 45, 120, 150)), ('top of the arch (x -8..8, z 143..158)', wbox(-8, 8, 143, 158))]
for name, win in places:
    print(name)
    for yw in (-55.5, -56.5, -57.5, -58.5, -60.0, -61.5, -62.8):
        line = '   world y %.1f (bed z %.1f):' % (yw, zb(yw))
        for nm, g in jobs.items():
            li = g.layer_at(zb(yw)); zm = float(g.L[li]) - g.lh / 2
            Mo = bp.layer(zm).intersection(box(win[0], win[2], win[1], win[3])); P = foot(g, li, win)
            if Mo.is_empty: line += ' (no model) |'; continue
            Pm = P.intersection(Mo.buffer(0.05)); s = props(g, li, win)
            line += ' %s: model %.1f mm2, printed %.0f%% (%s) |' % (nm, Mo.area, 100 * Pm.area / Mo.area, mixstr(s, 5))
        print(line)
specs = []
for nm, g in jobs.items():
    for yw in (-56.5, -58.5, -61.5):
        specs.append((g, g.layer_at(zb(yw)), wbox(60, 78, 36, 54), bp, 'lip side %s y %.1f' % (nm, yw)))
    specs.append((g, g.layer_at(zb(-57.0)), wbox(-10, 10, 142, 160), bp, 'lip arch top %s y -57' % nm))
sheet('/home/claude/r3/scan/img/lip_sliced.png', specs, ncol=4)
