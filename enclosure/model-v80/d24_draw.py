# Draws section pictures from d23's outlines (pictures/d23_*.json). Plain Python with matplotlib, no Fusion call.
# Each body's cut edges are chained into closed loops and filled (even-odd, so a loop inside another is a hole).
# In the three data files of block 1 the base plate's fine teeth at its front edge are drawn as one line; nothing else is changed
# from what Fusion returned.
#   b1_drivers_seat_plan.png   upright sections of the left driver's joint, looking from the unit's middle outward:
#                              on the driver's axis (x 70.5) as the model stands and as planned, and through the inner screws
#                              (x 52.75) as planned
# Run in this folder: python3 d24_draw.py b1
import json, math, os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch

HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
P = HERE + 'pictures/'
COL = {'HOUSING_F_front': ('#3f454c', 'shell'), 'SPKBOX_L': ('#8fa3b8', 'left speaker box'), 'SPK_L': ('#d9c7a3', 'driver'),
       'FOAM': ('#e0773a', 'the driver\'s foam, squeezed'), 'HEADS': ('#111111', 'M3 x 8, head sunk'), 'FLOOR_PLATE': ('#6c7178', 'base plate'),
       'TOUCH_CLIP_L': ('#3a8f5b', 'touch clip'), 'TOUCH_PCB': ('#2f6f9f', 'touch board'), 'RADAR_HOLDER': ('#b03a5b', 'radar holder'),
       'LD2410C_env_F': ('#f2d24b', 'radar board')}
ORDER = ['FLOOR_PLATE', 'HOUSING_F_front', 'SPKBOX_L', 'SPK_L', 'FOAM', 'HEADS', 'TOUCH_PCB', 'TOUCH_CLIP_L', 'RADAR_HOLDER', 'LD2410C_env_F']


def loops(lines, tol=0.03):
    segs = [list(map(tuple, l)) for l in lines if len(l) > 1]
    out = []
    while segs:
        cur = segs.pop(0)
        grew = True
        while grew:
            grew = False
            if len(cur) > 2 and math.dist(cur[0], cur[-1]) < tol:
                break
            for i, s in enumerate(segs):
                if math.dist(cur[-1], s[0]) < tol:
                    cur += s[1:]; segs.pop(i); grew = True; break
                if math.dist(cur[-1], s[-1]) < tol:
                    cur += s[::-1][1:]; segs.pop(i); grew = True; break
                if math.dist(cur[0], s[-1]) < tol:
                    cur = s[:-1] + cur; segs.pop(i); grew = True; break
                if math.dist(cur[0], s[0]) < tol:
                    cur = s[::-1][:-1] + cur; segs.pop(i); grew = True; break
        out.append(cur)
    return out


def body(ax, lines, col, alpha=1.0):
    verts = []; codes = []; opened = 0
    for lp in loops(lines):
        if math.dist(lp[0], lp[-1]) > 0.05:
            opened += 1
        verts += lp + [lp[0]]
        codes += [Path.MOVETO] + [Path.LINETO] * (len(lp) - 1) + [Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts, codes), facecolor=col, edgecolor='#000000', lw=0.5, alpha=alpha))
    return opened


def panel(ax, fn, title, notes=(), xlim=(-13.5, 8.2), ylim=(1.0, 56.5)):
    d = json.load(open(P + fn))
    seen = []
    for nm in ORDER:
        if nm in d['bodies']:
            o = body(ax, d['bodies'][nm], COL[nm][0])
            seen.append(nm)
            if o:
                print('%s %s: %d loops not closed' % (fn, nm, o))
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect('equal')
    ax.set_title(title, fontsize=10, loc='left')
    ax.set_xlabel('y, mm (toward the screen ->)', fontsize=8); ax.set_ylabel('z, mm', fontsize=8)
    ax.tick_params(labelsize=7)
    ax.set_xticks(range(-12, 9, 2))
    ax.grid(True, lw=0.25, color='#bbbbbb'); ax.set_axisbelow(True)
    for (x, y, txt, tx, ty) in notes:
        ax.annotate(txt, xy=(x, y), xytext=(tx, ty), fontsize=6.6, arrowprops=dict(arrowstyle='-', lw=0.5, color='#aa0000'), color='#7a0000',
                    bbox=dict(boxstyle='round,pad=0.15', fc='#ffffff', ec='none', alpha=0.85))
    return seen


def b1():
    fig, axs = plt.subplots(1, 3, figsize=(16.5, 10.5))
    s = set()
    s |= set(panel(axs[0], 'd23_b1_x705_today.json', 'On the driver\'s axis (x 70.5): the model as it stands, version 79',
                   notes=[(0.0, 49.5, 'upper bar, face y 0.0:\nthe flange (3.0 as drawn) rests on it', -12.8, 53.6),
                          (0.0, 6.5, 'lower bar, face y 0.0', -12.8, 2.0),
                          (-3.7, 6.0, 'box front face y -3.7', -11.0, 9.5),
                          (4.3, 30.0, 'grille\'s inner face y 4.2992\n(the "driver seat face" of D441)', -3.0, 30.0),
                          (0.7, 8.0, 'land y 0.7', 1.3, 2.0)]))
    s |= set(panel(axs[1], 'd23_b1_x705_plan.json', 'The same section as planned',
                   notes=[(0.0, 49.5, 'upper bar kept, y 0.0', -12.8, 53.6),
                          (1.8, 5.5, 'channel for the ring:\nfloor y 1.8, lower bar gone', -12.8, 1.6),
                          (2.0, 28.0, 'ring 36 across,\n2.0 proud: top y 2.0;\n2.30 to the grille', -5.2, 28.0),
                          (-3.8, 49.5, 'flange 3.8: back y -3.8', -12.9, 50.9),
                          (-5.0, 6.0, 'box front face y -5.0\n(bed 47.0); foam 2.0 -> 1.2', -12.8, 10.5),
                          (-7.0, 50.5, 'wall 2.0: inner face y -7.0', -12.9, 46.5),
                          (-4.3, 52.2, 'step at z 52.2: above it\nthe face stays at y -3.7', -1.5, 55.0)]))
    s |= set(panel(axs[2], 'd23_b1_x5275_plan.json', 'Through the inner screws (x 52.75), as planned',
                   notes=[(-4.0, 45.75, 'stop: 8.0 across at y -4.0 (bed 48.0),\nflared 45 deg to 10.0; foam taken\nas 0.2 on it', -12.9, 53.6),
                          (-10.7, 45.75, 'insert hole 4.0 x 6.7', -12.9, 39.0),
                          (-1.2, 45.75, 'head 0.35 under the\nflange\'s front', 1.2, 53.8),
                          (1.8, 16.5, 'channel floor y 1.8;\nthe old head pocket (2.0)\nand channel stay', -1.5, 21.5),
                          (-12.6, 45.75, 'column to y -12.6', -12.9, 35.5)]))
    hs = [plt.Rectangle((0, 0), 1, 1, fc=COL[n][0], ec='#000000', lw=0.5) for n in ORDER if n in s]
    fig.legend(hs, [COL[n][1] for n in ORDER if n in s], loc='lower center', ncol=6, fontsize=9, frameon=False)
    fig.suptitle('HA Panel v5: the left driver between its box and the shell. World mm; y + toward the screen, z up. Read on the model 2026-11-26 (version 79) '
                 'and on the plan\'s temporary bodies; nothing is put into the model.', fontsize=9.5, y=0.985)
    fig.tight_layout(rect=(0, 0.035, 1, 0.975))
    fig.savefig(P + 'b1_drivers_seat_plan.png', dpi=130)
    print('wrote', P + 'b1_drivers_seat_plan.png')


if __name__ == '__main__':
    {'b1': b1}[sys.argv[1] if len(sys.argv) > 1 else 'b1']()
# END
