# Block 9: draws the section pictures from p65's outlines (p65_b9_*.json). Plain Python with matplotlib, no Fusion call.
# Each body's cut edges are chained into closed loops and filled (a loop inside an odd number of others is a hole).
#   b9_sec_radar_holder.png   plan at z 42.0 (through the arm), upright sections at x 31.5 (the radar's middle) and x 22.5 (the -x M2)
#   b9_sec_holder_on_box.png  plans at z 57.6 (through the holder's screw; the M3 x 8 is drawn in, it is not a model body), at z 60.5
#                             (above the slot: the land and the rib) and at z 48.8 (through the +x M2 and standoff C)
# Only the bodies named in the legend are drawn. Run in the folder: python3 p92_b9_draw.py
import json, math, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Rectangle

D = os.path.dirname(os.path.abspath(__file__)) + '/'
COL = {'HOUSING_F_front': ('#3a3f45', 'shell'), 'HOUSING_F_plate': ('#6b727a', 'screen plate'), 'SPKBOX_L': ('#8fa3b8', 'left speaker box'),
       'SPK_L': ('#cfd6dd', 'left driver'), 'TOUCH_PCB': ('#2f8f5b', 'touch board'), 'TOUCH_components_env': ('#9fd3b5', 'touch board\'s parts'),
       'TOUCH_CLIP_L': ('#e09a3a', 'left touch clip'), 'RADAR_HOLDER': ('#c8324b', 'radar holder (new)'), 'LD2410C_env_F': ('#f2d24b', 'radar board'),
       'SCREWS_M2x6_env': ('#111111', 'M2 x 6'), 'LEAD_RADAR': ('#7a4fb5', 'radar lead'), 'LEAD_TOUCH': ('#4f7fb5', 'touch lead'),
       'PI5_F': ('#3d6b4f', 'Pi 5'), 'PI5_F_cooler': ('#7f9f8c', 'Pi cooler'), 'KO_K7_fan': ('#d9e6dd', 'keep-out over the cooler'),
       'FLOOR_PLATE': ('#55595e', 'base plate'), 'LEAD_GPIO_B': ('#b58a4f', 'signal wires'), 'GPIO_plugB_env': ('#c9b08a', 'signal plug')}
ORDER = ['KO_K7_fan', 'HOUSING_F_front', 'HOUSING_F_plate', 'FLOOR_PLATE', 'SPKBOX_L', 'SPK_L', 'PI5_F', 'PI5_F_cooler', 'TOUCH_PCB', 'TOUCH_components_env',
         'TOUCH_CLIP_L', 'LD2410C_env_F', 'RADAR_HOLDER', 'SCREWS_M2x6_env', 'LEAD_TOUCH', 'LEAD_GPIO_B', 'GPIO_plugB_env', 'LEAD_RADAR']


def loops(lines, tol=0.02):
    segs = [list(map(tuple, l)) for l in lines if len(l) > 1]
    out = []
    while segs:
        cur = segs.pop(0)
        grew = True
        while grew:
            grew = False
            if math.dist(cur[0], cur[-1]) < tol and len(cur) > 2:
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


def area(p):
    return 0.5 * sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))


def patch(lps, color, alpha=1.0, z=1):
    verts = []; codes = []
    paths = [Path(l) for l in lps]
    for i, l in enumerate(lps):
        depth = sum(1 for j, q in enumerate(paths) if j != i and q.contains_point(l[0]) and q.contains_point(l[len(l) // 2]))
        if (area(l) > 0) != (depth % 2 == 0):
            l = l[::-1]
        verts += list(l) + [l[0]]
        codes += [Path.MOVETO] + [Path.LINETO] * (len(l) - 1) + [Path.CLOSEPOLY]
    return PathPatch(Path(verts, codes), facecolor=color, edgecolor='#000000', linewidth=0.5, alpha=alpha, zorder=z)


def panel(ax, tag, title, xlim, ylim, xlabel, ylabel):
    d = json.load(open(D + 'p65_%s.json' % tag))
    used = []
    for z, nm in enumerate(ORDER):
        if nm not in d['bodies']:
            continue
        lp = loops(d['bodies'][nm])
        closed = [l for l in lp if math.dist(l[0], l[-1]) < 0.05 and len(l) > 3]
        if closed:
            ax.add_patch(patch(closed, COL[nm][0], 0.55 if nm.startswith('KO_') else 1.0, z + 2))
        for l in lp:
            if l not in closed:
                ax.plot([p[0] for p in l], [p[1] for p in l], color=COL[nm][0], lw=1.0, zorder=z + 2)
        used.append(nm)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect('equal')
    ax.set_title(title, fontsize=9.5, loc='left')
    ax.set_xlabel(xlabel, fontsize=8); ax.set_ylabel(ylabel, fontsize=8)
    ax.tick_params(labelsize=7)
    ax.grid(True, color='#e3e3e3', lw=0.4, zorder=0)
    return used


def note(ax, xy, text, to=None, ha='left', va='center', fs=7.5):
    box = dict(boxstyle='round,pad=0.2', fc='white', ec='#999999', lw=0.4, alpha=0.95)
    if to is None:
        ax.text(xy[0], xy[1], text, fontsize=fs, ha=ha, va=va, zorder=80, bbox=box)
    else:
        ax.annotate(text, xy=to, xytext=xy, fontsize=fs, ha=ha, va=va, zorder=80, bbox=box,
                    arrowprops=dict(arrowstyle='-|>', lw=0.6, color='#000000', shrinkA=0, shrinkB=0, mutation_scale=6))


def dim(ax, a, b, text, off=(0, 0), fs=7.5):
    ax.annotate('', xy=a, xytext=b, arrowprops=dict(arrowstyle='<->', lw=0.7, color='#0033aa', shrinkA=0, shrinkB=0, mutation_scale=6), zorder=79)
    ax.text((a[0] + b[0]) / 2 + off[0], (a[1] + b[1]) / 2 + off[1], text, fontsize=fs, color='#0033aa', ha='center', va='center', zorder=81,
            bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='none', alpha=0.9))


def legend(fig, used, y):
    seen = []
    for u in used:
        for n in u:
            if n not in seen:
                seen.append(n)
    hs = [Rectangle((0, 0), 1, 1, fc=COL[n][0], ec='black', lw=0.5) for n in ORDER if n in seen]
    fig.legend(hs, [COL[n][1] for n in ORDER if n in seen], loc='upper left', bbox_to_anchor=(0.035, y), fontsize=8, ncol=12, frameon=False,
               handlelength=1.4, columnspacing=1.4)


def pic1():
    fig = plt.figure(figsize=(16, 12), dpi=150)
    a = fig.add_axes([0.05, 0.595, 0.92, 0.30]); b = fig.add_axes([0.05, 0.07, 0.42, 0.46]); c = fig.add_axes([0.55, 0.07, 0.42, 0.46])
    u = [panel(a, 'b9_z42', 'Seen from above, cut at z 42.0 (through the arm). The screen is at the top; x + is the viewer\'s left.', (-9, 52), (-14, 8.6), 'x', 'y')]
    dim(a, (31.5, -2.9), (31.5, 2.8), '5.7', off=(1.5, 0))
    note(a, (-8.5, -3.5), 'pad at the arm\'s end: 0.6 into the board\'s back\nas modelled, which is the spring\'s press', to=(0.5, 2.7))
    note(a, (-8.5, -9.0), 'arm 1.2 x 3.6, a spring, in the band\nof the board\'s back that is free of parts', to=(8.0, 1.5))
    note(a, (-0.5, -12.4), 'the arm\'s root on the holder\'s -x wall, with a gusset\n(standoffs A and B are above and below this cut)', to=(22.2, -0.5))
    note(a, (27.5, -10.5), 'radar board 16 x 22 x 3.0, its face toward the screen', to=(33.0, -4.4))
    note(a, (27.5, -12.8), 'radar lead, going up to its tie under the top plate', to=(25.6, -8.3))
    note(a, (33.0, 0.9), 'left touch clip', to=(42.0, -0.4))
    note(a, (-8.5, 7.5), 'chin wall of the shell; the touch board sits on its inner face (y 4.4)')
    u.append(panel(b, 'b9_x315', 'Cut at x 31.5 (the radar\'s middle), seen from the viewer\'s left. The screen side is on the right.', (-38, 9), (19, 66), 'y', 'z'))
    dim(b, (-2.9, 36.0), (2.8, 36.0), '5.7', off=(0, 1.5))
    note(b, (-37.5, 61.0), 'top plate, 1.6 thick over the radar;\nthe tie bar is at its rear edge', to=(-8.5, 52.3))
    note(b, (-37.5, 55.0), '0.4 between the plate and the board\'s top edge', to=(-4.4, 51.2))
    note(b, (-37.5, 49.0), 'ledge plate 1.25, with a window;\nthe board sits on its rear face', to=(-2.3, 50.7))
    note(b, (-37.5, 41.0), 'radar board, its face 5.7 behind\nthe touch board\'s back', to=(-4.4, 41.0))
    note(b, (-37.5, 31.5), 'bottom 1.2, 0.2 under the board', to=(-4.0, 28.2))
    note(b, (-37.5, 26.0), 'Pi 5', to=(-14.0, 23.0))
    u.append(panel(c, 'b9_x225', 'Cut at x 22.5 (through the -x M2), seen from the viewer\'s left.', (-38, 9), (19, 66), 'y', 'z'))
    note(c, (-37.5, 61.0), 'radar lead under the top plate, at its tie', to=(-10.6, 50.4))
    note(c, (-37.5, 54.5), 'standoff B, on the board\'s back', to=(1.0, 47.0))
    note(c, (-37.5, 48.0), 'the arm\'s root', to=(0.5, 42.0))
    note(c, (-37.5, 42.0), 'standoff A, on the board\'s back', to=(1.0, 37.0))
    note(c, (-37.5, 33.0), 'M2 x 6 in its post: the head\'s flat face\nat y -5.19, the tip at y 0.81;\nthe post ends 0.5 off the board', to=(-3.5, 31.6))
    note(c, (-37.5, 24.0), 'the holder\'s -x wall and bottom', to=(-4.5, 28.2))
    fig.text(0.04, 0.972, 'Block 9: the radar on its holder behind the touch board. Model after the last put, 2026-11-26; lengths in mm.', fontsize=12, weight='bold')
    legend(fig, u, 0.957)
    fig.text(0.04, 0.012, 'Only the bodies named in the legend are drawn; the white space behind the holder is not empty in the unit.', fontsize=8, color='#444444')
    fig.savefig(D + 'b9_sec_radar_holder.png'); plt.close(fig)


def pic2():
    fig = plt.figure(figsize=(16.5, 6.0), dpi=150)
    a = fig.add_axes([0.04, 0.10, 0.262, 0.72]); b = fig.add_axes([0.345, 0.10, 0.262, 0.72]); c = fig.add_axes([0.65, 0.10, 0.335, 0.72])
    lim = ((26, 53), (-19, 6.6))
    u = [panel(a, 'b9_z576', 'From above, cut at z 57.6: through the holder\'s screw', lim[0], lim[1], 'x', 'y')]
    # the M3 x 8 button head (ISO 7380: head 5.7 across, 1.65 high), drawn in at the slot's middle; not a model body
    y0 = -7.35
    a.add_patch(Rectangle((36.6 - 1.65, y0 - 2.85), 1.65, 5.7, fc='#c9c9c9', ec='black', lw=0.7, zorder=70))
    a.add_patch(Rectangle((36.6, y0 - 1.5), 8.0, 3.0, fc='#c9c9c9', ec='black', lw=0.7, zorder=70, alpha=0.8))
    a.plot([33.5, 46.5], [y0, y0], color='black', lw=0.5, ls='-.', zorder=71)
    note(a, (26.4, -15.5), 'M3 x 8, drawn in (not a model body):\nhead on the land, 4.6 of thread in the\nblock\'s pilot, axis at y -7.35', to=(35.8, -9.9))
    note(a, (26.4, 4.2), 'slot through the tab: the holder can stand\n0.4 forward or back of the screw', to=(38.3, -5.55))
    note(a, (26.4, 0.2), '1.25 of tab on either side of the slot', to=(38.0, -4.5))
    note(a, (40.3, -1.6), 'block on the box\'s inner face,\nwith a 45 deg foot; pilot 2.7 across,\n5.35 deep, 2.15 of wall behind it', to=(44.9, -6.3))
    dim(a, (43.0, -6.0), (43.0, -4.0), '2.0', off=(1.3, 0))
    dim(a, (41.3, -11.0), (41.3, -8.7), '2.3', off=(-1.4, 0))
    u.append(panel(b, 'b9_z605', 'From above, cut at z 60.5: above the slot', lim[0], lim[1], 'x', 'y'))
    note(b, (26.4, 4.2), 'land under the screw\'s head:\n0.4 proud, 2.0 wide', to=(36.8, -7.0))
    note(b, (26.4, 0.0), 'rib 0.4 x 1.2 on the block\'s face:\nthe tab bears on a line', to=(39.8, -6.9))
    note(b, (26.4, -15.5), 'tab: 6.7 along y, 2.6 thick\nbeside the land', to=(38.3, -10.0))
    note(b, (40.3, -1.6), 'the block\'s front stands 0.3 behind\nthe box\'s front face', to=(45.6, -3.9))
    u.append(panel(c, 'b9_z488', 'From above, cut at z 48.8: through the +x M2 and standoff C', (17, 53), lim[1], 'x', 'y'))
    note(c, (24.2, 0.0), 'standoff C on the board\'s back,\noutboard of the rib\'s line (x 40)', to=(43.2, 1.7))
    note(c, (17.4, -17.2), 'M2 x 6 beside the board\'s long edge, its head over the edge (as today\'s);\nthe block under the head is the outer half only', to=(41.4, -4.7))
    note(c, (27.5, -9.5), '+x post round the pilot: wall 1.6\n(the clip is 0.4 under it)', to=(38.9, 0.6))
    note(c, (17.4, -13.5), 'radar lead', to=(23.0, -10.3))
    dim(c, (44.5, 2.0), (45.4, 2.0), '0.9', off=(0.0, -1.1))
    fig.text(0.04, 0.955, 'Block 9: the holder on the left speaker box. Model after the last put, 2026-11-26; lengths in mm. The screen is at the top; x + is the viewer\'s left.',
             fontsize=12, weight='bold')
    legend(fig, u, 0.925)
    fig.text(0.04, 0.015, 'Only the bodies named in the legend are drawn.', fontsize=8, color='#444444')
    fig.savefig(D + 'b9_sec_holder_on_box.png'); plt.close(fig)


if __name__ == '__main__':
    pic1(); pic2()
    print('drawn')
