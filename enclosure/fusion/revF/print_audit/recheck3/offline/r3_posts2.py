"""recheck3: the posts' sections as sliced with 2, 3 and 4 walls against the model (rule 11), and the torque and pull cases."""
import sys, numpy as np
from r3_gq import *
from r3_posts import axis_at, bp, slab_to_world
T = 500.0
jobs = {}
for nm, j in (('2 walls', 'H4_P3a_w2'), ('3 walls', 'H4_P3a_w3'), ('4 walls', 'H4_P3a_w4')):
    try: jobs[nm] = G(j)
    except Exception as e: print('no', j)
print('POSTS, horizontal sections (in the layers): printed footprint against the model; torque 0.5 N.m about the screw axis -> shear between layers tau = T r / J')
for label, x, up, cases in (('top post, viewer left', 70, 27, [('at the land (insert)', 25.6, 4.6), ('insert, mid', 27.0, 5.2), ('insert end', 31.0, 6.4), ('cone', 33.0, 6.8)]),
                            ('top post, viewer right', -70, 27, [('insert, mid', 27.0, 5.2), ('insert end', 31.0, 6.4)]),
                            ('bottom post, viewer left', 85, -82, [('peg', 1.8, 4.2), ('at the land (insert)', 3.0, 5.6), ('insert, mid', 4.0, 5.9), ('insert end', 7.0, 6.2), ('behind the insert', 8.4, 6.4)]),
                            ('bottom post, viewer right', -85, -82, [('insert, mid', 4.0, 5.9), ('insert end', 7.0, 6.2)])):
    for cname, zb, r in cases:
        c, land = axis_at(x, up, zb); win = (c[0] - r, c[0] + r, c[1] - r, c[1] + r)
        circ = shapely.Point(c[0], c[1]).buffer(r, quad_segs=32)
        line = '%-26s %-22s z %.1f r %.1f |' % (label, cname, zb, r)
        for nm, g in jobs.items():
            li = g.layer_at(zb); zm = float(g.L[li]) - g.lh / 2
            Mo = bp.layer(zm).intersection(circ); P = foot(g, li, win).intersection(circ)
            mo = gprops(Mo, win, about=c); pr = gprops(P, win, about=c)
            if nm == '2 walls': line += ' model A %.1f Jo %.0f ro %.2f tau %.2f |' % (mo['A'], mo['Jo'], mo['ro'], T * mo['ro'] / mo['Jo'])
            line += ' %s: A %.0f%% Jo %.0f%% tau %.2f |' % (nm, 100 * pr['A'] / mo['A'], 100 * pr['Jo'] / mo['Jo'], T * pr['ro'] / pr['Jo'])
        print(line)
