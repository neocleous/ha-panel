# Sections for the floor plate concept (schematic, to scale): A-A at x_rel 18.35 (front to back through the Pi's right
# bosses and the door screw at (19, -74.5)); B-B at x_rel 48.6 (the +x plate screw). World mm, y horizontal (front right),
# z up. Numbers from the version 42 model (f1a/f1b sections) and the concept geometry (geom.py).
import math, sys
sys.path.insert(0, '.')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Rectangle, Circle, Wedge
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if 'Inter' in f:
        fm.fontManager.addfont(f)
plt.rcParams['font.family'] = 'Inter'
C_SHELL = '#d9d3c9'; C_SHELL_E = '#6b6255'; C_CLOTH = '#5f5f5f'; C_PLATE = '#b9d4ee'; C_PLATE_E = '#1f5f9e'
C_INS = '#c99a2e'; C_STEEL = '#3a3a3a'; C_HID = '#777777'; C_DOOR = '#e3dccf'

def arc(cy, cz, r, a0, a1, n=24):
    return [(cy + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]

def P(ax, pts, fc, ec, lw=0.6, **kw):
    ax.add_patch(MPoly(pts, closed=True, fc=fc, ec=ec, lw=lw, **kw))

def R(ax, y0, y1, z0, z1, fc, ec, lw=0.6, **kw):
    ax.add_patch(Rectangle((min(y0, y1), min(z0, z1)), abs(y1 - y0), abs(z1 - z0), fc=fc, ec=ec, lw=lw, **kw))

def screw_iso7380(ax, y, ztop_head_seat, L=8.0):
    # head Ø5.7 x 1.65 below the seat, shank Ø3 up to seat + L
    R(ax, y - 2.85, y + 2.85, ztop_head_seat - 1.65, ztop_head_seat, C_STEEL, 'black', lw=0.4)
    R(ax, y - 1.5, y + 1.5, ztop_head_seat, ztop_head_seat + L, '#5a5a5a', 'black', lw=0.4)

def insert(ax, y, z0, z1):
    R(ax, y - 2.1, y + 2.1, z0, z1, C_INS, '#7a5a10', lw=0.4)

fig, (axA, axB) = plt.subplots(2, 1, figsize=(12.0, 7.6), dpi=200, gridspec_kw={'height_ratios': [1.0, 0.92]})
# ---------------- A-A ----------------
ax = axA
# chin: cloth face y 7.5, plastic 4.3..6.8 (D1 inner layer 0.7), bottom fillet R6 centre (1.5, 6.0), cove R2.8 same centre
outer = [(6.8, 30.0), (6.8, 6.0)] + arc(1.5, 6.0, 5.3, 0, -90) + [(1.5, 0.7), (0.5, 0.7), (0.5, 0.0), (-0.5, 0.0), (-0.5, 1.25),
         (-2.5, 1.25), (-2.5, 0.0)]
# shell ring + lip region polygon (approximate the land / lip): build the solid
shell_front = [(4.3, 30.0), (6.8, 30.0), (6.8, 6.0)] + arc(1.5, 6.0, 5.3, 0, -90) + [(1.5, 0.7), (0.5, 0.7), (0.5, 0.0),
               (-0.5, 0.0), (-0.5, 0.0), (-2.5, 0.0), (-2.5, 1.25), (-0.5, 1.25), (-0.5, 2.5), (1.5, 2.5), (1.5, 3.2)] + \
              arc(1.5, 6.0, 2.8, -90, 0) + [(4.3, 30.0)]
P(ax, shell_front, C_SHELL, C_SHELL_E)
cloth = [(7.5, 30.0), (7.5, 6.0)] + arc(1.5, 6.0, 6.0, 0, -90) + [(0.5, 0.0), (0.5, 0.7), (1.5, 0.7)] + arc(1.5, 6.0, 5.3, -90, 0) + [(6.8, 30.0)]
P(ax, cloth, C_CLOTH, 'none', lw=0)
# plate: lip -0.8..-2.8 at z 1.25..2.5, full from -2.8 to -59.5
plate = [(-0.8, 2.5), (-0.8, 1.25), (-2.8, 1.25), (-2.8, 0.0), (-59.5, 0.0), (-59.5, 2.5)]
P(ax, plate, C_PLATE, C_PLATE_E, lw=0.9)
# Pi bosses at y -5.5 / -54.5: Ø7.6 z 2.5-8.0 on the plate, insert Ø4.0 hole z 1.5-8.0
for yb in (-5.5, -54.5):
    R(ax, yb - 3.8, yb + 3.8, 2.5, 8.0, C_PLATE, C_PLATE_E, lw=0.7)
    insert(ax, yb, 2.3, 8.0)
    R(ax, yb - 1.25, yb + 1.25, 8.0, 12.0, '#5a5a5a', 'black', lw=0.3)         # M2.5 shank through the PCB
    R(ax, yb - 2.25, yb + 2.25, 9.4, 11.9, C_STEEL, 'black', lw=0.4)           # DIN 912 M2.5 head
# Pi PCB and cooler (hidden outline)
R(ax, -58.0, -2.0, 8.0, 9.4, '#3f8f4f', '#1f4f2f', lw=0.5)
R(ax, -50.1, -7.6, 13.6, 23.1, 'none', C_HID, lw=0.6, ls=(0, (3, 2)))
ax.text(-28.8, 18.4, 'Pi Active Cooler', ha='center', fontsize=6.8, color=C_HID)
# touch PCB
R(ax, 2.7, 4.3, 6.0, 30.0, '#3f8f4f', '#1f4f2f', lw=0.4)
# rear shell floor y -59.8 .. -78.4 (fillet tangent), fillet R6 centre (-78.4, 6.0); door pad + boss at y -74.5
shell_rear = [(-59.8, 0.0), (-78.4, 0.0)] + arc(-78.4, 6.0, 6.0, -90, -180) + [(-84.4, 2.5), (-59.8, 2.5)]
P(ax, shell_rear, C_SHELL, C_SHELL_E)
R(ax, -78.5, -70.5, 2.5, 2.8, C_SHELL, C_SHELL_E, lw=0.5)
# c-bore and through hole for the door screw (white = void)
R(ax, -77.75, -71.25, -0.01, 1.0, 'white', C_SHELL_E, lw=0.4)
R(ax, -76.2, -72.8, 1.0, 2.8, 'white', C_SHELL_E, lw=0.4)
# door: bottom band z 2.8-3.65 and wall (schematic), boss Ø8 z 2.8-10.5 with insert
door = [(-84.4, 2.8), (-84.4, 30.0), (-81.2, 30.0), (-81.2, 3.65), (-78.4, 3.65), (-78.4, 2.8)]
P(ax, door, C_DOOR, '#8a7f6a')
R(ax, -78.5, -70.5, 2.8, 10.5, C_DOOR, '#8a7f6a', lw=0.6)
insert(ax, -74.5, 2.9, 8.6)
screw_iso7380(ax, -74.5, 1.0)
ax.text(-74.5, 11.2, 'door boss + screw\n(unchanged)', ha='center', fontsize=6.6, color='#5a4f3a', va='bottom')
# Pi power cable (hidden) and the USB4085 plug behind the plane
ax.add_patch(Circle((-67.0, 5.4), 2.25, fc='none', ec=C_HID, lw=0.6, ls=(0, (3, 2))))
R(ax, -69.9, -63.3, 14.0, 30.0, 'none', C_HID, lw=0.6, ls=(0, (3, 2)))
ax.text(-66.6, 25.5, 'main-board\nUSB-C plug', ha='center', fontsize=6.4, color=C_HID)
# annotations
def note(ax, xy, txt, xyt, ha='center', color='black'):
    ax.annotate(txt, xy=xy, xytext=xyt, fontsize=7.0, ha=ha, va='center', color=color,
                arrowprops=dict(arrowstyle='-', lw=0.5, color=color, shrinkA=1, shrinkB=0))
note(ax, (-1.8, 1.9), "plate's upper half lies on a 2 mm ring lip (z 0–1.25); gaps 0.3", (13.5, -9.0), ha='left', color=C_PLATE_E)
note(ax, (3.5, 0.3), 'cloth wraps the R6 fillet + 1 mm', (13.5, -4.0), ha='left')
note(ax, (-34.0, 1.25), 'floor plate 2.5 thick (z 0–2.5); intake Ø2 on a 3.0 grid', (-28.0, -9.0), ha='left', color=C_PLATE_E)
note(ax, (-5.5, 6.0), 'Pi bosses Ø7.6 on the plate, Ruthex M2.5 pressed on the bench', (-30.0, 27.0), color=C_PLATE_E)
note(ax, (-59.65, 1.25), "plate's rear edge, 0.3 to the shell floor", (-56.0, -4.0), ha='left', color=C_PLATE_E)

note(ax, (3.5, 18), 'touch board', (12, 22), ha='left')
note(ax, (-30, 8.7), 'Pi 5 PCB', (-30, 11.3))
ax.set_xlim(14, -92); ax.set_ylim(-11.5, 30.5); ax.set_aspect('equal')
ax.set_title('A–A  at x 18.35 (through the Pi\'s bosses on the viewer\'s left and the door screw at x 19), seen from the viewer\'s right (−x side)',
             fontsize=8.6, loc='left', fontweight='bold')
ax.axhline(0, color='#bbbbbb', lw=0.4, zorder=0)
ax.text(13.5, 0.15, 'z 0', fontsize=6, color='#888888', va='bottom')
ax.set_yticks([]); ax.set_xticks(range(10, -91, -10)); ax.tick_params(labelsize=6.5)
ax.set_xlabel('y (mm, + toward the screen)', fontsize=7)
for s in ('top', 'right', 'left'):
    ax.spines[s].set_visible(False)
ax.text(5.5, 29.0, 'chin', fontsize=7, ha='center'); ax.text(-82.8, 29.0, 'door', fontsize=7, ha='center')

# ---------------- B-B (detail, 2x) ----------------
ax = axB
# plate tab from y -20.6 (strip) back to -61.6 at x 48.6; shell floor from -61.9 back; door pad (50,-67) at x 48.6
P(ax, [(-36.0, 0.0), (-61.6, 0.0), (-61.6, 2.5), (-36.0, 2.5)], C_PLATE, C_PLATE_E, lw=0.9)
# c-bore + hole in the plate (void)
R(ax, -60.85, -54.35, -0.01, 1.0, 'white', C_PLATE_E, lw=0.4)
R(ax, -59.3, -55.9, 1.0, 2.5, 'white', C_PLATE_E, lw=0.4)
# shell floor behind the tab, rear fillet at x 48.6 (tangent ~ -72.9 at z 0)
shell_b = [(-61.9, 0.0), (-72.9, 0.0)] + arc(-72.9, 6.0, 6.0, -90, -150) + [(-76.0, 2.5), (-61.9, 2.5)]
P(ax, shell_b, C_SHELL, C_SHELL_E)
# arm boss (shell) Ø7 at y -57.6, z 2.5-10.5, with its arm over the gap onto the shell floor (z 2.5-6.0, to y -64)
arm = [(-54.1, 2.5), (-54.1, 10.5), (-61.1, 10.5), (-61.1, 2.5)]
P(ax, arm, C_SHELL, C_SHELL_E, lw=0.7)
R(ax, -59.6, -55.6, 2.5, 9.5, 'white', C_SHELL_E, lw=0.4)
insert(ax, -57.6, 2.5, 8.2)
screw_iso7380(ax, -57.6, 1.0)
# door pad/boss at (50, -67): at x 48.6 the pad spans y -63.3..-70.7
R(ax, -70.7, -63.3, 2.5, 2.8, C_SHELL, C_SHELL_E, lw=0.5)
R(ax, -70.7, -63.3, 2.8, 10.5, C_DOOR, '#8a7f6a', lw=0.6)
ax.text(-67.0, 11.0, 'door boss', ha='center', fontsize=6.6, color='#5a4f3a', va='bottom')
# speaker box rear face (y -52) and bracket column from the knee (z 21, cranked) - hidden
ax.plot([-52.0, -52.0], [3.7, 13.5], color=C_HID, lw=0.6, ls=(0, (3, 2)))
ax.text(-52.0, 14.4, '+x box rear face', fontsize=6.4, color=C_HID, ha='center', va='center')
R(ax, -62.5, -58.5, 13.0, 14.0, 'none', C_HID, lw=0.6, ls=(0, (3, 2)))
ax.text(-60.5, 12.2, 'bracket column now\nstarts at z 21 (crank)', fontsize=6.4, color=C_HID, ha='center', va='top')
note(ax, (-54.3, 7.0), 'shell boss Ø7, bears on\nthe plate; arm to the\nshell floor on its +x side\n(out of plane); Ruthex M3\npressed from below', (-38.6, 8.0), ha='left', color=C_SHELL_E)
note(ax, (-57.6, -0.65), 'ISO 7380 M3 × 8 from below, head in Ø6.5 × 1.0 — same screw, insert and boss as the door', (-38.6, -5.6), ha='left')
note(ax, (-61.75, 1.0), '0.3 gap', (-66.0, -2.4), ha='left')
ax.set_xlim(-38.0, -80.0); ax.set_ylim(-7.5, 15.5); ax.set_aspect('equal')
ax.set_title('B–B  at x 48.6 (the +x plate screw), detail, seen from the viewer\'s right (−x side)', fontsize=8.6, loc='left', fontweight='bold')
ax.axhline(0, color='#bbbbbb', lw=0.4, zorder=0)
ax.set_yticks([]); ax.set_xticks(range(-40, -81, -5)); ax.tick_params(labelsize=6.5)
ax.set_xlabel('y (mm)', fontsize=7)
for s in ('top', 'right', 'left'):
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig('fp_concept_sections.png', dpi=200)
print('ok')
