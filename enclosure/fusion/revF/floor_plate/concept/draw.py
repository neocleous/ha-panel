import sys, math
sys.path.insert(0, '.')
from geom import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Circle, Patch
from matplotlib.lines import Line2D
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if 'Inter' in f:
        fm.fontManager.addfont(f)
plt.rcParams['font.family'] = 'Inter'

C_SHELL = '#e9e5de'; C_CLOTH = '#8f8f8f'; C_PLATE = '#d3e5f5'; C_PLATE_E = '#1f5f9e'; C_LIP = '#b9b0a2'
C_HID = '#666666'; C_NEW = '#c0392b'

def U(x):
    return -x

def poly_patch(ax, g, **kw):
    for p in ([g] if g.geom_type == 'Polygon' else list(g.geoms)):
        if p.is_empty:
            continue
        ax.add_patch(MPoly([(U(x), y) for x, y in p.exterior.coords], closed=True, **kw))
        for r in p.interiors:
            ax.add_patch(MPoly([(U(x), y) for x, y in r.coords], closed=True, fc='white', ec='none'))

def outline(ax, g, **kw):
    for p in ([g] if g.geom_type in ('Polygon', 'LineString') else list(g.geoms)):
        xy = p.exterior.coords if p.geom_type == 'Polygon' else p.coords
        ax.plot([U(x) for x, y in xy], [y for x, y in xy], **kw)

def circ(ax, c, r, **kw):
    ax.add_patch(Circle((U(c[0]), c[1]), r, **kw))

fig, ax = plt.subplots(figsize=(12.0, 6.6), dpi=200)
FOOT = PLATE.union(PLATE_LIP)
SHELL_FLOOR = W.difference(CLOTH_NEW).difference(FOOT.buffer(0.3, join_style=2))
poly_patch(ax, SHELL_FLOOR, fc=C_SHELL, ec='none')
poly_patch(ax, CLOTH_NEW, fc=C_CLOTH, ec='none')
poly_patch(ax, RING_LIP, fc=C_LIP, ec='none')
poly_patch(ax, PLATE, fc=C_PLATE, ec=C_PLATE_E, lw=1.3)
outline(ax, W, color='black', lw=1.0)
old = off(12.0).exterior.intersection(FRONT)
for g in (old.geoms if hasattr(old, 'geoms') else [old]):
    ax.plot([U(x) for x, y in g.coords], [y for x, y in g.coords], color=C_NEW, lw=0.7, ls=(0, (1, 2)))
ax.plot([U(-99.5), U(99.5)], [JOINT_Y, JOINT_Y], color='black', lw=0.5, ls=(0, (8, 3, 1, 3)))
for (x, y) in intake_holes():
    ax.add_patch(Circle((U(x), y), 1.0, fc='white', ec='#7aa6d1', lw=0.25))
hid = dict(color=C_HID, lw=0.55, ls=(0, (3, 2)))
for g in [PI] + PI_PORTS + [ADAPTER, PLUG, USBA_PLUG, USBA_CABLE, BOX_L, BOX_R, TOUCH, MAIN, CRADLE_BODY] + CLIPS:
    outline(ax, g, **hid)
ax.plot([U(x) for x, y in PI_CABLE.coords], [y for x, y in PI_CABLE.coords], color=C_HID, lw=2.4, alpha=0.3, solid_capstyle='round')
ax.plot([U(x) for x, y in DOOR_INNER.coords], [y for x, y in DOOR_INNER.coords], **hid)
for (x, y) in PI_BOSSES + CRADLE_BOSSES:
    circ(ax, (x, y), 3.8, fc='none', ec=C_HID, lw=0.55, ls=(0, (3, 2)))
for (x, y) in ARM_BOSSES:
    circ(ax, (x, y), ARM_R, fc='none', ec=C_PLATE_E, lw=0.8, ls=(0, (3, 2)))
for k, (x, y) in FEET_NEW.items():
    circ(ax, (x, y), 6.5, fc='white', ec='black', lw=0.6); circ(ax, (x, y), 6.35, fc='#2f2f2f', ec='none')
for (x, y) in DOOR_BOSSES + BRACKET_FEET_NEW:
    circ(ax, (x, y), 3.25, fc='white', ec='black', lw=0.6); circ(ax, (x, y), 2.85, fc='#707070', ec='none')
circ(ax, BRACKET_FEET_NOW[0], 3.25, fc='none', ec=C_NEW, lw=0.7, ls=(0, (2, 2)))
for (x, y) in ARM_BOSSES:
    circ(ax, (x, y), 3.25, fc='white', ec=C_PLATE_E, lw=1.0); circ(ax, (x, y), 2.85, fc=C_PLATE_E, ec='none')
# section lines
for xs, nm in ((18.35, 'A'), (48.6, 'B')):
    ax.plot([U(xs), U(xs)], [12, -92], color='#333333', lw=0.6, ls=(0, (10, 3, 2, 3)))
    ax.text(U(xs), 13.5, nm, ha='center', fontsize=8, fontweight='bold'); ax.text(U(xs), -95.5, nm, ha='center', fontsize=8, fontweight='bold')

def lab(pts, tx, ty, t, ha='left', color='black'):
    for (x, y) in pts:
        ax.annotate('', xy=(U(x), y), xytext=(U(tx), ty), arrowprops=dict(arrowstyle='-', lw=0.5, color=color, shrinkA=0, shrinkB=0))
    ax.text(U(tx) + (-1.5 if ha == 'right' else 1.5), ty, t, fontsize=7.4, ha=ha, va='center', color=color, linespacing=1.25)

LX = 108; RX = -108
lab([(94, -2)], LX, 6, 'Cloth under the bottom edge: fillet + 1 mm\n(rev D pattern), then 1 mm hard ring.\nRed dots: today\'s edge (fillet + 6 mm).', ha='right')
lab([(80, -11.5)], LX, -16, 'Front feet and the left rear foot stay\non the shell; none is ever removed.', ha='right')
lab([(51, -38)], LX, -33, 'Plate strip under the USB-A plug: the +x\nspeaker box\'s plug slot opens through the\nbox bottom so the plug drops out with the Pi.', ha='right', color=C_PLATE_E)
lab([(48.6, -57.6)], LX, -51.5, 'Plate screw (1 of 2), see section B.', ha='right', color=C_PLATE_E)
lab([(65, -57), (49.5, -58)], LX, -63, 'Bracket +x screw moves to the outside\n(+x half cranked like the −x half);\nred: today\'s position.', ha='right')
lab([(30, -69)], LX, -78, 'Left rear foot: unchanged.', ha='right')
lab([(-20, -1.6)], RX, 6, 'Front edge: the plate\'s upper half lies on a\n2 mm lip of the ring — hooks in, no screw.')
lab([(-39.65, -5.5)], RX, -12, 'Pi on 4 bosses on the plate: Ruthex M2.5\npressed in on the bench (loose plate).')
lab([(-30, -36)], RX, -27, 'Intake field (475 × Ø2) on the plate,\nunder the Pi cooler as before.', color=C_PLATE_E)
lab([(-47.2, -57.6)], RX, -51.5, 'Plate screw (2 of 2).', color=C_PLATE_E)
lab([(-31.2, -68.5), (-15, -65)], RX, -66, 'Pi power adapter, plug and the right rear foot\nsit on the plate (foot 1.2 out, 0.5 forward);\nthe plate keeps 0.85 off the door\'s edge.', color=C_PLATE_E)
lab([(19, -74.5), (-19, -77), (-1.5, -72.5)], RX, -82, 'Door screws (4) and the 5807 cradle:\nunchanged, on the shell.')
ax.text(U(0), 17.0, 'SCREEN SIDE', ha='center', fontsize=8.5, fontweight='bold')
ax.text(U(0), -101.0, 'BACK (door)', ha='center', fontsize=8.5, fontweight='bold')
ax.text(U(0), -57.5, 'joint', ha='center', fontsize=6.5, color='#333333')
ax.text(U(78), 20.5, "viewer's left (+x)", ha='center', fontsize=7.5)
ax.text(U(-78), 20.5, "viewer's right (−x)", ha='center', fontsize=7.5)
ax.set_xlim(U(178), U(-178)); ax.set_ylim(-112, 25)
ax.set_aspect('equal'); ax.axis('off')
fig.suptitle('Floor plate concept — underside, unit tipped back onto its rear (screen side up)', x=0.02, y=0.975, ha='left',
             fontsize=11, fontweight='bold')
hand = [Patch(fc=C_PLATE, ec=C_PLATE_E, label='floor plate (removable, M3 × 2)'), Patch(fc=C_SHELL, label='shell floor (fixed)'),
        Patch(fc=C_LIP, label='ring lip under the plate\'s front edge'), Patch(fc=C_CLOTH, label='cloth'),
        Line2D([0], [0], color=C_HID, lw=0.6, ls=(0, (3, 2)), label='parts above the floor, hidden'),
        Line2D([0], [0], color='#333333', lw=0.6, ls=(0, (10, 3, 2, 3)), label='section lines A, B')]
ax.legend(handles=hand, loc='lower left', bbox_to_anchor=(0.0, -0.02), fontsize=7.2, frameon=False, ncol=3)
ax.plot([U(-120), U(-170)], [-106, -106], color='black', lw=1.0)
ax.text(U(-145), -109.5, '50 mm', ha='center', fontsize=7)
fig.subplots_adjust(left=0.01, right=0.99, top=0.95, bottom=0.02)
fig.savefig('fp_concept_below.png', dpi=200)
print('ok')
