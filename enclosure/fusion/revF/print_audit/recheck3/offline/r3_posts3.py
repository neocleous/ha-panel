"""recheck3: bottom posts - the buttress (to the side wall) and the strut (to the chin block) on cuts square to the bed, as sliced against the model."""
import numpy as np
from r3_gq import *
from r3_posts import axis_at, bp
jobs = {'2 walls': G('H4_P3a_w2'), '4 walls': G('H4_P3a_w4')}
c4, land = axis_at(85, -82, 4.0)
print('bottom post viewer-left: axis at bed', np.round(c4, 2), 'land', np.round(land, 2))
# model outline extents at z 4 and 7 near the post
for zb in (3.0, 5.0, 7.0, 9.0):
    Mo = bp.layer(zb - 0.1).intersection(box(c4[0] - 12, c4[1] - 14, c4[0] + 10, c4[1] + 12))
    print(' z %.1f model bounds' % zb, np.round(Mo.bounds, 2), 'area %.1f' % Mo.area)
for name, axis, val, lo, hi in (('buttress, cut x = axis + 6.3', 'x', c4[0] + 6.3, c4[1] - 7.5, c4[1] + 7.5), ('buttress, cut x = axis + 7.0', 'x', c4[0] + 7.0, c4[1] - 7.5, c4[1] + 7.5),
                                ('post ring + buttress, cut x = axis + 3.0', 'x', c4[0] + 3.0, c4[1] - 7.5, c4[1] + 7.5),
                                ('strut, cut y = axis - 6.6', 'y', c4[1] - 6.6, c4[0] - 5.0, c4[0] + 5.0), ('strut, cut y = axis - 8.0', 'y', c4[1] - 8.0, c4[0] - 5.0, c4[0] + 5.0)):
    line = '%-42s |' % name
    for nm, g in jobs.items():
        r = vcut(g, bp, axis, val, lo, hi, 1.0, 9.4)
        if nm == '2 walls': line += ' model A %.1f I %.1f Z %.1f (z %.1f..%.1f) |' % (r['model']['A'], r['model']['I'], r['model']['Z'], r['rows'][r['rows'][:, 2] > 0, 0].min() - 0.1, r['rows'][r['rows'][:, 2] > 0, 0].max() + 0.1)
        line += ' %s: A %.0f%% I %.0f%% Z %.0f%% |' % (nm, 100 * r['sliced']['A'] / r['model']['A'], 100 * r['sliced']['I'] / r['model']['I'], 100 * r['sliced']['Z'] / r['model']['Z'])
    print(line)
