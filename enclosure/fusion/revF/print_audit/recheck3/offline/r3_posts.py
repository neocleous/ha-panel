"""recheck3: the shell's four posts as sliced with 2 and 4 walls (FDM7): pictures and sections."""
import sys, numpy as np
from r3_gq import *
C12, S12 = math.cos(math.radians(12)), math.sin(math.radians(12))
def slab_to_world(x, up, d): return np.array([x, -d * C12 - up * S12, 143.3 - d * S12 + up * C12])
POS = (0.0, -30.0, 0.0)
bp = BedPart('shell', POS)
def axis_at(x, up, zbed):
    land = bp.to_bed(slab_to_world(x, up, 12.8))[0]; return np.array([land[0], land[1] - S12 / C12 * (zbed - land[2])]), land
if __name__ == '__main__':
    jobs = {'w2': G('H4_P3a_w2'), 'w4': G('H4_P3a_w4')}
    specs = []
    for nm, g in jobs.items():
        for zb in (26.0, 30.0, 33.0, 37.0):
            c, land = axis_at(70, 27, zb); specs.append((g, g.layer_at(zb), (c[0] - 10, c[0] + 10, c[1] - 10, c[1] + 10), bp, 'top post %s' % nm))
    sheet('/home/claude/r3/scan/img/posts_top.png', specs, ncol=4)
    specs = []
    for nm, g in jobs.items():
        for zb in (2.0, 4.0, 7.0, 9.4):
            c, land = axis_at(85, -82, zb); specs.append((g, g.layer_at(zb), (c[0] - 11, c[0] + 9, c[1] - 10, c[1] + 10), bp, 'bottom post %s' % nm))
    sheet('/home/claude/r3/scan/img/posts_bottom.png', specs, ncol=4)
    print('top land bed', axis_at(70, 27, 25)[1], 'bottom land bed', axis_at(85, -82, 2)[1])
