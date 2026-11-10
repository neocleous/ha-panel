# Concept v2, view from below: the base plate is the whole underside out to the edge.
import sys, math
sys.path.insert(0, '.')
from geom2 import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Circle, Patch, Rectangle
from matplotlib.lines import Line2D
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if 'Inter' in f:
        fm.fontManager.addfont(f)
plt.rcParams['font.family'] = 'Inter'

C_CLOTH = '#8f8f8f'; C_PLATE = '#d3e5f5'; C_RIM = '#a9cbe8'; C_PLATE_E = '#1f5f9e'; C_HID = '#666666'; C_BOX = '#c9772b'


def U(x):
    return -x


def poly_patch(ax, g, **kw):
    for p in ([g] if g.geom_type == 'Polygon' else list(g.geoms)):
        if p.is_empty:
            continue
        ax.add_patch(MPoly([(U(x), y) for x, y in p.exterior.coords], closed=True, **kw))


def outline(ax, g, **kw):
    for p in ([g] if g.geom_type in ('Polygon', 'LineString') else list(g.geoms)):
        xy = p.exterior.coords if p.geom_type == 'Polygon' else p.coords
        ax.plot([U(x) for x, y in xy], [y for x, y in xy], **kw)


def circ(ax, c, r, **kw):
    ax.add_patch(Circle((U(c[0]), c[1]), r, **kw))


PS = [(75.0, -49.5), (-75.0, -49.5)]
fig, ax = plt.subplots(figsize=(12.0, 5.75), dpi=200)
poly_patch(ax, W, fc=C_CLOTH, ec='none')                       # cloth on the rounded bottom edge above the plate (z 2.8-6)
poly_patch(ax, Z25, fc=C_RIM, ec='none')                       # plate rim (rounded, z 0-2.5)
poly_patch(ax, Z0, fc=C_PLATE, ec='none')                      # flat underside
outline(ax, Z25, color=C_PLATE_E, lw=1.3)
outline(ax, W, color='black', lw=0.9)
outline(ax, Z0, color=C_PLATE_E, lw=0.4, ls=(0, (1, 2)))
for (x, y) in intake_holes():
    ax.add_patch(Circle((U(x), y), 1.0, fc='white', ec='#7aa6d1', lw=0.25))
hid = dict(color=C_HID, lw=0.55, ls=(0, (3, 2)))
for g in [PI] + PI_PORTS + [ADAPTER, PLUG, TOUCH, CRADLE_BODY]:
    outline(ax, g, **hid)
for g in (BOX2_L, BOX2_R):
    poly_patch(ax, g, fc='#f3d9bf', ec='none', alpha=0.55)
    outline(ax, g, color=C_BOX, lw=0.9, ls=(0, (4, 2)))
for g in (FRAME_L, FRAME_R):
    outline(ax, g, color=C_BOX, lw=0.7)
ax.plot([U(x) for x, y in DOOR_INNER.coords], [y for x, y in DOOR_INNER.coords], **hid)
for (x, y) in PI_BOSSES + CRADLE_BOSSES:
    circ(ax, (x, y), 3.8, fc='none', ec=C_HID, lw=0.55, ls=(0, (3, 2)))
for g in TONGUES:
    poly_patch(ax, g, fc=C_PLATE_E, ec='none')
for k, (x, y) in FEET_NOW.items():
    circ(ax, (x, y), 6.5, fc='white', ec='black', lw=0.6); circ(ax, (x, y), 6.35, fc='#2f2f2f', ec='none')
for (x, y) in DOOR_BOSSES:
    circ(ax, (x, y), 3.25, fc='white', ec='black', lw=0.6); circ(ax, (x, y), 2.85, fc='#707070', ec='none')
for (x, y) in PS:
    circ(ax, (x, y), 3.25, fc='white', ec=C_PLATE_E, lw=1.0); circ(ax, (x, y), 2.85, fc=C_PLATE_E, ec='none')
for (x, y) in BOX_PLATE:
    circ(ax, (x, y), 3.25, fc='white', ec=C_BOX, lw=1.0); circ(ax, (x, y), 2.85, fc=C_BOX, ec='none')
for sx in (1, -1):                                              # key path of the box-top screw, from the back
    ax.annotate('', xy=(U(sx * TAB_X), -4.5), xytext=(U(sx * TAB_X), -66.0),
                arrowprops=dict(arrowstyle='->', lw=0.9, color=C_BOX, ls=(0, (5, 2)), shrinkA=0, shrinkB=0))
ax.plot([U(-99.5), U(99.5)], [JOINT_Y, JOINT_Y], color='black', lw=0.5, ls=(0, (8, 3, 1, 3)))
for xs, nm in ((0.3, 'A'), (70.5, 'B')):
    ax.plot([U(xs), U(xs)], [12, -92], color='#333333', lw=0.6, ls=(0, (10, 3, 2, 3)))
    ax.text(U(xs), 13.5, nm, ha='center', fontsize=8, fontweight='bold'); ax.text(U(xs), -95.5, nm, ha='center', fontsize=8, fontweight='bold')


def lab(pts, tx, ty, t, ha='left', color='black'):
    for (x, y) in pts:
        ax.annotate('', xy=(U(x), y), xytext=(U(tx), ty), arrowprops=dict(arrowstyle='-', lw=0.5, color=color, shrinkA=0, shrinkB=0))
    ax.text(U(tx) + (-1.5 if ha == 'right' else 1.5), ty, t, fontsize=7.4, ha=ha, va='center', color=color, linespacing=1.25)


LX = 110; RX = -110
lab([(97.0, -8.0)], LX, 8, 'Rim: the plate\'s edge is the lowest 2.5 mm of the\nrounded bottom edge, painted. The cloth ends\njust above it, as it does under the door today.', ha='right', color=C_PLATE_E)
lab([(80, -11.5)], LX, -12, 'All four feet on the plate, where they\nare today. No screw under a foot.', ha='right')
lab([(51, -12), (64, -45)], LX, -30, 'Speaker box on the plate:\n2 screws from below (each side).', ha='right', color=C_BOX)
lab([(75, -49.5)], LX, -45, 'Plate screw into a post on the\nside wall (each side).', ha='right', color=C_PLATE_E)
lab([(TAB_X, -62)], LX, -60, 'Path of the key for the screw at the top\nof the box: from the back, door off.', ha='right', color=C_BOX)
lab([(30, -69)], LX, -76, 'Door: unchanged. Its 4 screws now\npass through the plate.', ha='right')
lab([(-28, 1.0)], RX, 8, 'Front edge: two tongues hook behind the chin as\nthe plate slides the last 2 mm forward. No screw.', color=C_PLATE_E)
lab([(-39.65, -5.5)], RX, -10, 'Pi on 4 posts on the plate; inserts\npressed in on the bench.')
lab([(-30, -36)], RX, -24, 'Intake holes under the Pi cooler,\nas today.')
lab([(-70.5, -30)], RX, -38, 'Speaker box (orange, dashed): rides on the plate\nand enters the shell from below with it.', color=C_BOX)
lab([(-1.5, -72.5)], RX, -66, 'Inlet board cradle: on the plate.\nNo bracket: the main board moves up\nbehind the display (section A).')
ax.text(U(0), 17.0, 'SCREEN SIDE', ha='center', fontsize=8.5, fontweight='bold')
ax.text(U(0), -101.0, 'BACK (door)', ha='center', fontsize=8.5, fontweight='bold')
ax.text(U(-14), -57.6, 'joint', ha='center', fontsize=6.5, color='#333333')
ax.text(U(78), 20.5, "viewer's left (+x)", ha='center', fontsize=7.5)
ax.text(U(-78), 20.5, "viewer's right (−x)", ha='center', fontsize=7.5)
ax.set_xlim(U(186), U(-186)); ax.set_ylim(-116, 25)
ax.set_aspect('equal'); ax.axis('off')
fig.suptitle('Base plate concept (second round) — underside, unit tipped back onto its rear (screen side up)', x=0.02, y=0.975,
             ha='left', fontsize=11, fontweight='bold')
hand = [Patch(fc=C_PLATE, ec=C_PLATE_E, label='base plate, flat underside'), Patch(fc=C_RIM, label='base plate, rounded rim'),
        Patch(fc=C_CLOTH, label='cloth on the shell and door'),
        Line2D([0], [0], color=C_BOX, lw=0.9, ls=(0, (4, 2)), label='speaker boxes and drivers, on the plate'),
        Line2D([0], [0], color=C_HID, lw=0.6, ls=(0, (3, 2)), label='other parts above the plate'),
        Line2D([0], [0], color='#333333', lw=0.6, ls=(0, (10, 3, 2, 3)), label='section lines A, B')]
ax.legend(handles=hand, loc='lower left', bbox_to_anchor=(0.0, -0.02), fontsize=7.2, frameon=False, ncol=3)
ax.plot([U(-125), U(-175)], [-109, -109], color='black', lw=1.0)
ax.text(U(-150), -112.5, '50 mm', ha='center', fontsize=7)
fig.subplots_adjust(left=0.01, right=0.99, top=0.94, bottom=0.02)
fig.savefig('fp2_concept_below.png', dpi=200)
print('ok')
