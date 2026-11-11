"""Rev 3.1, block 0: one picture of what is planned to move, seen from the door. Reads the rev 3 board; draws nothing into it."""
import os, math
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')) + os.sep
import pcb
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, Polygon
b = pcb.load(ROOT + 'main-board.kicad_pcb')
U0, V0 = 43.5, 28.95
def bx(r):
    c = b['fps'][r]['crt']; return [c[0] - U0, V0 - c[3], c[2] - U0, V0 - c[1]]
fig = plt.figure(figsize=(17, 11.6), dpi=110); ax = fig.add_axes([0.04, 0.05, 0.93, 0.9]); ax.set_aspect('equal')
ax.set_xlim(-47, 47); ax.set_ylim(-32, 32)
ax.add_patch(Rectangle((-U0, -V0), 2 * U0, 2 * V0, fc='#f7faf4', ec='black', lw=2.2, zorder=1))
BIG = {'PS1': 'supply module', 'C5': 'C5', 'C6': 'C6', 'L1': 'L1 filter coil', 'C7': 'C7', 'U100': 'amplifier', 'F5': 'amplifier fuse F5', 'F2': 'Pi fuse F2', 'LK1': 'wire link',
       'J1': '20 V\nsocket', 'J2': 'Pi power\nsocket', 'J3': 'Pi signal pads', 'J4': 'Pi\npads', 'J5': 'radar\nsocket', 'J6': 'touch\nsocket', 'J7': 'echo-reference pads', 'J8': 'speaker\nleft',
       'J9': 'speaker\nright', 'L100': '', 'L101': '', 'L102': '', 'L103': '', 'U1': 'inlet\nprotection', 'F1': '20 V fuse F1'}
MOVE = ('J10', 'J11', 'R26', 'R27', 'F3', 'C10', 'TP12', 'F4', 'C11', 'TP3', 'H2')
for r, f in b['fps'].items():
    if not f['crt'] or r in MOVE or r.startswith('H'): continue
    c = bx(r)
    ax.add_patch(Rectangle((c[0], c[1]), c[2] - c[0], c[3] - c[1], fc='#e3e3e3' if r in BIG else '#efefef', ec='#555' if r in BIG else '#aaa', lw=0.9 if r in BIG else 0.4, zorder=2))
    if BIG.get(r): ax.text((c[0] + c[2]) / 2, (c[1] + c[3]) / 2, BIG[r], fontsize=7.5, ha='center', va='center', color='#333', zorder=3)
for h, (u, v) in {'H1': (-37.0, 22.0), 'H3': (-31.0, -25.25), 'H4': (31.0, -25.25)}.items():
    ax.add_patch(Circle((u, v), 3.5, fc='#e9f3e9', ec='#7a9a7a', lw=0.8, zorder=2)); ax.add_patch(Circle((u, v), 1.6, fc='white', ec='black', lw=1.0, zorder=3)); ax.text(u, v + 2.4, h, fontsize=7, ha='center', color='#3d6b3d', zorder=4)
OLD = dict(fc='none', ec='#c0392b', ls='--', lw=1.3, zorder=6); NEW = dict(fc='#bfe3bf', ec='#1c7a1c', lw=1.8, zorder=7, alpha=0.9)
def arrow(a, c):
    ax.add_patch(FancyArrowPatch(a, c, arrowstyle='-|>', mutation_scale=13, color='#1c7a1c', lw=1.4, zorder=9))
# hole
ax.add_patch(Rectangle((-12.0, 21.6), 34.7, 3.9, fc='#fff3c4', ec='#b8860b', lw=1.2, ls='-', alpha=0.45, zorder=1.5))
ax.text(-11.5, 20.5, "zone for the hole's centre (enclosure): u -12.0...+22.7, v +21.6...+25.5", fontsize=7.5, color='#8a6508', zorder=5)
ax.add_patch(Circle((30.0, 25.0), 1.6, **OLD)); ax.add_patch(Circle((30.0, 25.0), 3.5, **OLD)); ax.text(33.5, 29.9, 'old hole (+30.0, +25.0)', fontsize=7.5, ha='center', color='#c0392b')
ax.add_patch(Rectangle((27.25, 21.42), 6.2, 6.2, fc='none', ec='#555', ls=':', lw=1.2, zorder=6)); ax.text(37.6, 23.2, "display's power\nplug behind\nthe board", fontsize=7, ha='center', color='#555')
ax.add_patch(Circle((19.5, 25.0), 4.5, fc='none', ec='#1c7a1c', ls='--', lw=1.0, zorder=7)); ax.add_patch(Circle((19.5, 25.0), 3.5, **NEW)); ax.add_patch(Circle((19.5, 25.0), 1.6, fc='white', ec='black', lw=1.3, zorder=8))
ax.text(13.5, 30.0, 'NEW top right hole  u +19.5, v +25.0', fontsize=9, ha='center', color='#0f5f0f', weight='bold'); arrow((27.9, 25.0), (23.2, 25.0))
# headers and small parts: old -> new boxes
plan = {'J10': (4.0, 0.0, 'NEW BME680 header\npins at u -30.3\n(4.0 further from\nthe radar socket)'), 'J11': (0.0, -1.0, 'NEW VEML6030 header, pins at v -13.0 (1.0 lower)'),
        'F4': (1.2, 0.0, ''), 'C11': (0.4, 0.0, ''), 'TP3': (0.0, -0.5, '')}
for r, (du, dv, txt) in plan.items():
    c = bx(r)
    ax.add_patch(Rectangle((c[0], c[1]), c[2] - c[0], c[3] - c[1], **OLD)); ax.add_patch(Rectangle((c[0] + du, c[1] + dv), c[2] - c[0], c[3] - c[1], **NEW))
ax.text(-30.3, -14.1, 'J10', fontsize=7.5, ha='center', va='center', rotation=90, weight='bold', zorder=9); ax.text(-0.7, -13.0, 'J11', fontsize=7.5, ha='center', va='center', weight='bold', zorder=9)
ax.annotate(plan['J10'][2], xy=(-30.3, -8.6), xytext=(-24.5, 13.0), fontsize=8.5, color='#0f5f0f', weight='bold', ha='center', arrowprops=dict(arrowstyle='-', color='#0f5f0f', lw=0.9), zorder=10, bbox=dict(fc='white', ec='#0f5f0f', lw=0.6, pad=2.5))
ax.annotate(plan['J11'][2], xy=(-0.7, -14.8), xytext=(3.0, -31.0), fontsize=8.5, color='#0f5f0f', weight='bold', ha='center', arrowprops=dict(arrowstyle='-', color='#0f5f0f', lw=0.9), zorder=10, bbox=dict(fc='white', ec='#0f5f0f', lw=0.6, pad=2.5))
place = {'R26': (15.0, 22.9, 1.46, 2.96), 'R27': (15.0, 26.2, 1.46, 2.96), 'F3': (-34.24, -16.80, 3.66, 7.38), 'C10': (-34.24, -11.90, 3.40, 1.96), 'TP12': (-34.24, -9.40, 2.5, 2.5)}
for r, (cu, cv, w, h) in place.items():
    c = bx(r)
    ax.add_patch(Rectangle((c[0], c[1]), c[2] - c[0], c[3] - c[1], **OLD)); ax.add_patch(Rectangle((cu - w / 2, cv - h / 2), w, h, **NEW))
    ax.text(cu, cv, r, fontsize=6, ha='center', va='center', zorder=9, rotation=90 if h > w * 1.5 else 0)
ax.annotate('radar fuse F3, radar capacitor C10 and\nradar test pad TP12 go between the\nradar socket and the header', xy=(-34.3, -20.6), xytext=(-37.5, -31.0), fontsize=7.5, color='#0f5f0f', ha='center', arrowprops=dict(arrowstyle='-', color='#0f5f0f', lw=0.8), zorder=10, bbox=dict(fc='white', ec='#0f5f0f', lw=0.5, pad=2))
ax.annotate('R26, R27 beside the hole', xy=(15.0, 21.3), xytext=(6.5, 19.2), fontsize=7.5, color='#0f5f0f', ha='center', arrowprops=dict(arrowstyle='-', color='#0f5f0f', lw=0.8), zorder=10)
ax.annotate('F4 and C11 a little to the right', xy=(-26.0, -13.0), xytext=(-20.5, -3.2), fontsize=7.5, color='#0f5f0f', ha='center', arrowprops=dict(arrowstyle='-', color='#0f5f0f', lw=0.8), zorder=10, bbox=dict(fc='white', ec='none', pad=1))
ax.annotate('test pad TP3\n0.5 lower', xy=(-3.2, -17.5), xytext=(-19.0, -30.9), fontsize=7.5, color='#0f5f0f', ha='center', arrowprops=dict(arrowstyle='-', color='#0f5f0f', lw=0.8), zorder=10, bbox=dict(fc='white', ec='none', pad=1))
# supply copper to widen
N5 = ('/5 V supply and outputs/VBUS_PI', '/5 V supply and outputs/5V_PI_F'); NE = ('/20 V inlet and eFuse/VIN_EF', '/20 V inlet and eFuse/VIN_PIGTAIL')
for sg in b['segs']:
    if sg['net'] in N5 and sg['w'] >= 0.4 and (sg['layer'] == 'B.Cu' or sg['w'] >= 1.5):
        ax.plot([sg['x1'] - U0, sg['x2'] - U0], [V0 - sg['y1'], V0 - sg['y2']], color='#1f5fbf', lw=sg['w'] * 6.2, solid_capstyle='round', alpha=0.85, zorder=8)
    if sg['net'] in NE and sg['w'] in (0.6, 1.0) and sg['y1'] > 49.4:
        ax.plot([sg['x1'] - U0, sg['x2'] - U0], [V0 - sg['y1'], V0 - sg['y2']], color='#d35400', lw=sg['w'] * 6.2 + 1, solid_capstyle='round', alpha=0.9, zorder=8)
ax.annotate("Pi's 5 V on the back, wire link to socket:\n2.0, 1.4 and 0.6 wide today;\nbecomes one copper area", xy=(15.5, -17.0), xytext=(27.5, -3.5), fontsize=7.5, color='#1f5fbf', ha='center', arrowprops=dict(arrowstyle='-', color='#1f5fbf', lw=0.8), zorder=10, bbox=dict(fc='white', ec='#1f5fbf', lw=0.5, pad=2))
ax.annotate('20 V in, fuse to protection chip:\n0.6 wide today; becomes a copper area', xy=(-12.65, -22.2), xytext=(-22.0, -21.2), fontsize=7.5, color='#d35400', ha='center', arrowprops=dict(arrowstyle='-', color='#d35400', lw=0.8), zorder=10, bbox=dict(fc='white', ec='#d35400', lw=0.5, pad=2))
ax.text(-46.0, 30.6, 'red dashed: where it is on rev 3      green: planned for rev 3.1      grey: stays', fontsize=8.5, color='#333')
ax.set_xlabel('u (mm), to the right as seen from the door', fontsize=9); ax.set_ylabel('v (mm), up', fontsize=9)
ax.set_title('Main board rev 3.1, block 0: planned changes, seen from the door (nothing has been changed on the board yet)', fontsize=12)
ax.grid(True, lw=0.25, color='#bbb', zorder=0); ax.set_xticks(range(-40, 41, 10)); ax.set_yticks(range(-30, 31, 10))
fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'block0-planned-changes.png')); print('saved')
