# change2/offline/gap_sections.py - question 1 again: today, a and b in one section (left side, 20 below mid-screen), drawn from version 65's
# sections; a and b are made here by cutting and adding in the section (not from built bodies).
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import model as M, numpy as np, geo
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in ('Regular', 'Medium', 'SemiBold'):
    fm.fontManager.addfont('/usr/share/fonts/opentype/inter/Inter-%s.otf' % f)
plt.rcParams['font.family'] = 'Inter'
UP = -40.0


def poly(name):
    ps = [Polygon(p[:, [0, 1]]).buffer(0) for p in geo.sect(M.mesh(name, 's'), [0, 0, UP], [0, 0, 1]) if len(p) > 3]
    return unary_union([p for p in ps if p.area > 0.01])


def xmax(P, d, x0=60.0):
    I = P.intersection(LineString([(x0, d), (130, d)])); return I.bounds[2]


def xmin(P, d, x0=80.0):
    I = P.intersection(LineString([(x0, d), (130, d)])); return I.bounds[0]


W = box(76.0, 3.0, 108.5, 21.5)
shell, plate, frame, glass, ref = [poly(n).intersection(W) for n in ('HOUSING_F_front', 'HOUSING_F_plate', 'SLAB_frame', 'LCD_glass', 'REF_F_outer')]
x_isl = xmax(poly('REF_F_outer'), 12.6)               # the island's edge in option a
x_tip_out = xmax(shell, 13.1); x_tip_in = xmin(shell, 13.1)
print('island edge x %.2f, wall tip x %.2f..%.2f, plate edge %.2f, bezel back d %.2f' % (x_isl, x_tip_in, x_tip_out, plate.bounds[2], 12.0))
plate_a = plate.difference(box(x_isl, 12.0, 120, 13.0))
plate_b = plate.intersection(box(0, 0, 200, 12.0))
lip = box(x_tip_in, 12.2, x_isl, 13.7)
shell_b = unary_union([shell, lip])
print('lip: %.2f wide, stands %.2f in front of the wall tip; in front of the cloth reference plane (d 12.3) by %.2f' % (x_isl - x_tip_in, 13.05 - 12.2, 12.3 - 12.2))
COL = dict(shell='#b9b6aa', plate='#5d6170', frame='#26262a', glass='#9fc5e8', add='#d9480f')


def draw(ax, P, color, z=1, ec='#111111'):
    for g in (P.geoms if hasattr(P, 'geoms') else [P]):
        if g.is_empty or g.geom_type != 'Polygon':
            continue
        x, y = g.exterior.xy; ax.fill(x, y, color=color, zorder=z, ec=ec, lw=0.6)
        for r in g.interiors:
            x, y = r.xy; ax.fill(x, y, color='white', zorder=z, ec=ec, lw=0.6)


def note(ax, text, xy, to, color='#111111', ha='left'):
    ax.annotate(text, xy=to, xytext=xy, fontsize=11.5, color=color, ha=ha, va='center', zorder=9,
                arrowprops=dict(arrowstyle='-', color=color, lw=1.0, shrinkA=2, shrinkB=0),
                bbox=dict(boxstyle='square,pad=0.25', fc='white', ec='none'))
    ax.plot([to[0]], [to[1]], 'o', ms=3.5, color=color, zorder=9)


DX = x_isl - 91.12                                     # labels were placed for the section 20 below; shift them with the wall
fig, axs = plt.subplots(1, 3, figsize=(21, 6.9))
for ax, (title, S, P, key) in zip(axs, (('Today (version 65)', shell, plate, 't'), ('a.  The step is on the plate (recommended)', shell, plate_a, 'a'),
                                        ('b.  Plate thin everywhere; the step becomes a lip on the shell', shell_b, plate_b, 'b'))):
    draw(ax, glass, COL['glass']); draw(ax, frame, COL['frame']); draw(ax, S, COL['shell']); draw(ax, P, COL['plate'], z=2)
    if key == 'b':
        draw(ax, lip.difference(shell), COL['add'], z=3)
    for g in (ref.geoms if hasattr(ref, 'geoms') else [ref]):
        x, y = g.exterior.xy; ax.plot(x, y, '--', color='#1864ab', lw=1.0, zorder=5)
    x0 = 84.6 + DX
    ax.set_xlim(x0, x0 + 21.5); ax.set_ylim(18.2, 5.6); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(title, fontsize=15, fontweight='semibold', loc='left')
    ax.text(101.6, 8.4, 'bezel', color='white', fontsize=13, ha='center', zorder=9)
    ax.text(x0 + 0.5, 9.9, 'screen plate', color='white', fontsize=12, zorder=9)
    note(ax, 'side wall', (x0 + 0.4, 16.9), (89.75 + DX, 15.6))
    note(ax, "cloth's surface (dashed)", (95.4 + DX, 16.9), (92.72 + DX, 15.0), color='#1864ab')
    if key == 't':
        note(ax, 'plate 3.8 thick everywhere', (x0 + 0.4, 6.3), (x0 + 2.4, 9.3))
        note(ax, "plate's edge shows 0.8 behind the bezel", (93.2 + DX, 14.3), (98.62, 12.45))
        note(ax, '0.2 slit', (x0 + 0.4, 14.6), (x_tip_out - 0.15, 12.93))
        ax.text(0.0, -0.05, 'The screen looks sunk into the shell.', fontsize=12.5, va='center', transform=ax.transAxes)
    if key == 'a':
        note(ax, 'plate 3.8 only on the shell', (x0 + 0.4, 6.3), (x0 + 2.4, 9.3))
        note(ax, "border 3.0: level with the bezel's back", (94.6 + DX, 14.7), (97.6 + DX, 12.0))
        note(ax, 'the gap', (95.0 + DX, 13.2), (x_isl + 0.55, 12.45), color='#c92a2a')
        note(ax, '0.2 slit, covered', (x0 + 0.4, 14.6), (x_tip_out - 0.15, 12.93))
        ax.text(0.0, -0.05, 'Changes: the plate only. Its border prints 0.8 above the bed, on support.', fontsize=12.5, va='center', transform=ax.transAxes)
    if key == 'b':
        note(ax, 'plate 3.0 everywhere, flat back', (x0 + 0.4, 6.3), (x0 + 2.4, 9.3))
        note(ax, 'new lip on the shell, all round', (x0 + 0.4, 14.6), (x_tip_in + 0.25, 12.6), color=COL['add'])
        note(ax, 'the gap', (95.0 + DX, 13.2), (x_isl + 0.55, 12.45), color='#c92a2a')
        ax.text(0.0, -0.05, 'Changes: the plate, the shell, both speaker boxes, the display screws.', fontsize=12.5, va='center', transform=ax.transAxes)
fig.suptitle('Question 1 again - a and b in section (left side, 40 below mid-screen, seen from above; glass at the top)', fontsize=17, fontweight='semibold', x=0.012, ha='left')
fig.text(0.012, 0.03, "From outside a and b look the same. Both are drawn into version 65's section; b is not built. The dashed line is the model's cloth reference, 0.7 outside the shell. Lengths in mm.", fontsize=12)
fig.tight_layout(rect=(0, 0.09, 1, 0.93)); fig.savefig(os.path.join(M.D, '..', 'img', 'q1b_gap_sections.png'), dpi=110)
