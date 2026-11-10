# Concept v2 sections (to scale, world mm; y horizontal with the front on the left, z up):
#   A  centre section at x_rel 0.3: base plate, Pi, display stack with the main board behind the ReSpeaker, door, inlet
#   B  speaker section at x_rel 70.5: speaker box on the plate, driver, top tab (drawn from x 57)
#   bottom front edge at the speaker, today and proposed (enlarged)
# Profiles from the version 42 model (f1c side sections); main-board pose from f1d (pose B).
import math, sys
sys.path.insert(0, '.')
from geom2 import D2W, MB_ZC, MB_YB, MB_YF
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Rectangle
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if 'Inter' in f:
        fm.fontManager.addfont(f)
plt.rcParams['font.family'] = 'Inter'
C_SHELL = '#d9d3c9'; C_SHELL_E = '#6b6255'; C_CLOTH = '#5f5f5f'; C_PLATE = '#b9d4ee'; C_PLATE_E = '#1f5f9e'
C_INS = '#c99a2e'; C_STEEL = '#3a3a3a'; C_HID = '#777777'; C_DOOR = '#e6dfd2'; C_PCB = '#3f8f4f'; C_PCB_E = '#1f4f2f'
C_BOX = '#f0cfa8'; C_BOX_E = '#b5651d'; C_SLAB = '#c4c9cf'; C_GLASS = '#2b2f36'; C_FOAM = '#8e3b46'; C_NEW = '#1f5f9e'
FY, FZ = 1.5, 6.0                                     # bottom fillet centre at the chin


def arc(cy, cz, r, a0, a1, n=20):
    return [(cy + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def P(ax, pts, fc, ec, lw=0.5, **kw):
    ax.add_patch(MPoly(pts, closed=True, fc=fc, ec=ec, lw=lw, **kw))


def R(ax, y0, y1, z0, z1, fc, ec, lw=0.5, **kw):
    ax.add_patch(Rectangle((min(y0, y1), min(z0, z1)), abs(y1 - y0), abs(z1 - z0), fc=fc, ec=ec, lw=lw, **kw))


def DR(Y0, Y1, Z0, Z1):
    """rectangle in the slab's frame (depth Y, height Zd) as world points"""
    return [D2W(Y0, Z0), D2W(Y1, Z0), D2W(Y1, Z1), D2W(Y0, Z1)]


def note(ax, xy, txt, xyt, ha='left', va='center', color='black', fs=6.8):
    ax.annotate(txt, xy=xy, xytext=xyt, fontsize=fs, ha=ha, va=va, color=color, linespacing=1.25,
                arrowprops=dict(arrowstyle='-', lw=0.5, color=color, shrinkA=1.5, shrinkB=0))


A_R53 = math.degrees(math.asin((2.8 - FZ) / 5.3))     # shell's bottom edge on the recess surface
A_R60 = math.degrees(math.asin((2.8 - FZ) / 6.0))     # ... on the cloth face
A_PL = math.degrees(math.asin((2.5 - FZ) / 6.0))      # plate's top edge on the body surface
SLAB_BOT = [(16.6, 59.6), (8.9, 58.0), (9.9, 53.5), (7.0, 52.8), (7.4, 50.9), (7.6, 50.2), (8.4, 49.2), (9.6, 48.6), (10.9, 48.6),
            (13.9, 49.2), (15.6, 49.9), (16.4, 50.4), (17.7, 51.8), (18.1, 52.6), (18.6, 54.4), (18.5, 56.3), (18.1, 58.0), (17.0, 57.7)]
SLAB_TOP = [(-7.1, 176.6), (-7.4, 177.5), (-8.3, 179.2), (-9.7, 180.4), (-11.4, 181.2), (-13.3, 181.4), (-14.2, 181.2), (-17.1, 180.6),
            (-18.3, 180.1), (-19.2, 179.0), (-19.4, 178.4), (-19.4, 177.1), (-19.0, 175.1), (-16.1, 175.7), (-15.1, 171.2),
            (-7.5, 172.9), (-7.9, 174.7), (-6.7, 175.0)]
GLASS = [(-6.7, 174.7), (-7.7, 174.4), (17.0, 58.0), (18.1, 58.3)]
PANEL = [(-7.4, 172.3), (-11.0, 171.5), (12.8, 59.4), (16.4, 60.1)]
LCDPCB = [(-7.9, 152.4), (-9.4, 152.1), (6.4, 77.8), (7.9, 78.1)]


def slab(ax, pcb=True):
    P(ax, SLAB_BOT, C_SLAB, '#6d737a'); P(ax, SLAB_TOP, C_SLAB, '#6d737a')
    P(ax, PANEL, '#9aa3ad', '#5a626b', lw=0.4); P(ax, GLASS, C_GLASS, 'none', lw=0)
    if pcb:
        P(ax, LCDPCB, C_PCB, C_PCB_E, lw=0.4)


def plate(ax, rear):
    pts = arc(FY, FZ, 6.0, A_PL, -90) + rear
    P(ax, pts, C_PLATE, C_PLATE_E, lw=0.9)


def foot(ax, yc):
    R(ax, yc - 6.35, yc + 6.35, -3.0, 0.0, '#2f2f2f', 'none', lw=0, alpha=0.45)


def chin_cloth(ax, ztop):
    P(ax, [(7.5, ztop), (7.5, FZ)] + arc(FY, FZ, 6.0, 0, A_R60, 8) + arc(FY, FZ, 5.3, A_R53, 0, 8) + [(6.8, ztop)], C_CLOTH, 'none', lw=0)


def screw_up(ax, y, L=8.0):
    """ISO 7380 M3 from below, head in a 1.0 counterbore in the plate"""
    R(ax, y - 3.25, y + 3.25, 0.0, 1.0, 'white', C_PLATE_E, lw=0.3)
    R(ax, y - 2.85, y + 2.85, -0.65, 1.0, C_STEEL, 'black', lw=0.3)
    R(ax, y - 1.5, y + 1.5, 1.0, 1.0 + L, '#5a5a5a', 'black', lw=0.3)


fig = plt.figure(figsize=(12.6, 7.9), dpi=200)
gs = fig.add_gridspec(1, 2, width_ratios=[176.0, 150.0], left=0.012, right=0.995, top=0.90, bottom=0.02, wspace=0.03)
axA = fig.add_subplot(gs[0, 0]); axB = fig.add_subplot(gs[0, 1])
fig2, (axT, axN) = plt.subplots(1, 2, figsize=(11.0, 4.9), dpi=200)
fig2.subplots_adjust(left=0.02, right=0.98, top=0.86, bottom=0.03, wspace=0.08)

# =============================== A: centre section ===============================
ax = axA
chin = [(5.73, 2.8)] + arc(FY, FZ, 5.3, A_R53, 0, 8) + [(6.8, 48.5), (6.7, 49.0), (6.7, 49.2), (5.4, 48.9), (5.1, 50.4), (7.1, 50.8),
        (6.7, 52.8), (9.9, 53.5), (3.1, 85.3), (-2.5, 84.0), (5.0, 48.6), (5.0, 48.0), (4.3, 47.8), (4.3, 6.0)] + \
       arc(FY, FZ, 2.8, 0, -90, 8) + [(1.5, 2.8)]
# slot under the chin block for the plate's tongue (drawn from x 28)
P(ax, chin, C_SHELL, C_SHELL_E)
top = [(-19.3, 174.8), (-19.9, 177.6), (-20.4, 178.8), (-20.8, 179.2), (-21.9, 179.9), (-22.5, 180.0), (-22.5, 177.4), (-23.3, 177.4),
       (-23.3, 177.0), (-22.0, 175.7), (-15.0, 142.7), (-9.3, 143.9), (-11.4, 153.7), (-8.9, 154.3), (-10.5, 162.1), (-13.1, 161.5),
       (-16.0, 175.4)]
P(ax, top, C_SHELL, C_SHELL_E)
for loop in ([(-55.5, 162.5), (-57.3, 158.0), (-55.1, 157.2), (-55.0, 156.8), (-59.4, 144.3), (-63.5, 131.7), (-62.3, 131.3),
              (-58.1, 144.5), (-53.5, 157.4), (-53.5, 161.3), (-53.1, 162.5)],
             [(-54.4, 165.5), (-51.7, 165.5), (-51.1, 166.9), (-51.3, 167.0), (-53.8, 167.0)],
             [(-49.5, 175.3), (-50.3, 175.2), (-50.5, 174.8), (-51.9, 171.5), (-52.6, 170.0), (-50.1, 170.0), (-48.8, 170.1),
              (-48.5, 170.9), (-47.5, 170.9), (-47.1, 171.8), (-46.2, 171.8), (-44.7, 175.3), (-45.8, 175.3), (-46.1, 175.1),
              (-47.1, 172.8), (-50.1, 172.8), (-49.2, 174.9)]):
    P(ax, loop, C_SHELL, C_SHELL_E)
for loop in ([(-26.0, 178.3), (-26.0, 177.5), (-22.6, 177.5), (-22.6, 180.0), (-32.7, 180.0), (-32.7, 178.3)],
             [(-50.9, 175.8), (-44.2, 175.8), (-44.5, 173.3), (-42.9, 173.3), (-42.3, 177.2), (-42.4, 177.5), (-41.4, 177.5),
              (-41.4, 178.3), (-34.7, 178.3), (-34.7, 180.0), (-47.1, 180.0), (-48.8, 179.5), (-49.9, 178.2)]):
    P(ax, loop, '#cfc8bb', C_SHELL_E)
chin_cloth(ax, 48.5)
# door at the centre: inner surface = wall reference + 0.7, 2.55 thick, cloth 0.7; inlet cut-out z 13.3-27.9
ZI = [(28.0, -81.2), (40.0, -80.48), (50.0, -79.64), (60.0, -78.58), (70.0, -77.29), (82.0, -75.41), (100.0, -71.92), (110.0, -69.5),
      (120.2, -67.0), (138.1, -61.7), (155.6, -55.7)]
inner = [(y, z) for z, y in ZI]
outer = [(y - 2.55, z) for z, y in ZI[:-1]] + [(-57.9, 156.4)]
P(ax, inner + outer[::-1], C_DOOR, C_SHELL_E)
P(ax, [(y - 0.7, z) for y, z in outer] + outer[::-1], C_CLOTH, 'none', lw=0)
low = [(-83.2, 2.8), (-79.0, 2.8), (-79.0, 3.6), (-80.5, 3.6), (-81.5, 4.7), (-81.8, 6.0), (-81.7, 13.3), (-84.2, 13.3), (-84.3, 6.0), (-84.0, 4.3)]
P(ax, low, C_DOOR, C_SHELL_E)
P(ax, [(-84.9, 13.3), (-85.0, 6.0), (-84.7, 4.2), (-83.9, 2.8), (-83.2, 2.8), (-84.0, 4.3), (-84.3, 6.0), (-84.2, 13.3)], C_CLOTH, 'none', lw=0)
# inlet: cradle, inlet board, grommet
for loop in ([(-76.1, 8.0), (-68.9, 8.0), (-68.9, 13.7), (-68.7, 14.3), (-68.1, 14.5), (-60.5, 14.5), (-60.5, 17.5), (-69.8, 17.5),
              (-69.8, 16.0), (-75.2, 16.0), (-75.2, 17.5), (-81.6, 17.5), (-81.6, 20.5), (-83.8, 20.5), (-83.8, 21.9), (-84.6, 21.9),
              (-84.6, 14.5), (-76.9, 14.5), (-76.3, 14.3), (-76.1, 13.7)],
             [(-81.6, 25.6), (-81.6, 26.7), (-84.6, 26.7), (-84.6, 25.6)]):
    P(ax, loop, '#cbbfa9', C_SHELL_E)
P(ax, [(-77.3, 25.4), (-84.6, 25.4), (-84.6, 22.1), (-83.7, 22.1), (-83.7, 19.5), (-60.2, 19.5), (-60.2, 22.1), (-77.2, 22.1)], C_PCB, C_PCB_E, lw=0.4)
for loop in ([(-83.7, 27.8), (-83.7, 27.0), (-81.2, 27.0), (-81.2, 27.8)], [(-83.6, 30.9), (-84.2, 30.9), (-84.1, 33.1), (-85.1, 33.1), (-85.3, 30.1), (-83.7, 30.1)],
             [(-81.7, 14.2), (-85.9, 14.2), (-85.9, 11.2), (-84.9, 11.2), (-84.9, 13.4), (-81.7, 13.4)]):
    P(ax, loop, '#444444', 'none', lw=0)
# base plate with the cradle post, rear fillet centre (-79.03, 6.0)
plate(ax, [(-79.03, 0.0)] + arc(-79.03, FZ, 6.0, -90, -180 - A_PL, 12) + [(FY + 6.0 * math.cos(math.radians(A_PL)), 2.5)])
R(ax, -76.1, -73.4, 2.5, 8.0, C_PLATE, C_PLATE_E, lw=0.6); R(ax, -71.6, -68.9, 2.5, 8.0, C_PLATE, C_PLATE_E, lw=0.6)
# tongue (drawn from x 28): upstand on the plate, nose into a slot under the chin block
R(ax, 1.5, 3.1, 3.3, 4.5, 'white', C_SHELL_E, lw=0.3)
P(ax, [(-0.9, 2.5), (-0.9, 4.4), (2.9, 4.4), (2.9, 3.4), (1.2, 3.4), (1.2, 2.5)], C_PLATE, C_PLATE_E, lw=0.6)
foot(ax, -69.0)
# Pi on the plate
for yb in (-5.5, -54.5):
    R(ax, yb - 3.8, yb + 3.8, 2.5, 8.0, C_PLATE, C_PLATE_E, lw=0.5, ls=(0, (3, 1.5)))
R(ax, -58.0, -2.0, 8.0, 9.4, C_PCB, C_PCB_E, lw=0.4)
R(ax, -50.1, -7.6, 13.6, 23.1, 'none', C_HID, lw=0.6, ls=(0, (3, 2)))
ax.text(-28.8, 18.3, 'Pi cooler', ha='center', va='center', fontsize=6.3, color=C_HID)
R(ax, 2.7, 4.3, 6.0, 50.0, C_PCB, C_PCB_E, lw=0.4)                      # touch board
# display stack
slab(ax)
for zc in (-2.93, -51.93):                                               # the LCD's Pi standoffs (drawn from x -16 / 42)
    P(ax, DR(-7.4, -15.2, zc - 2.75, zc + 2.75), '#b9b9b9', '#666666', lw=0.3)
P(ax, DR(-15.2, -17.2, -56.9, 2.2), '#cbbfa9', C_SHELL_E, lw=0.4)        # carrier plate
P(ax, DR(-19.2, -22.2, -48.0, -14.0), '#cbbfa9', 'none', lw=0, alpha=0.6)  # carrier bosses / mic side
P(ax, DR(-22.2, -23.71, -48.0, -14.0), C_PCB, C_PCB_E, lw=0.4)           # ReSpeaker, 4 mm lower
for zc in (MB_ZC + 19.0, MB_ZC - 24.0):                                   # posts (drawn from x -39 / 44)
    P(ax, DR(-17.2, MB_YB, zc - 3.5, zc + 3.5), C_PLATE, C_PLATE_E, lw=0.5, ls=(0, (3, 1.5)))
P(ax, DR(MB_YB, MB_YF, MB_ZC - 27.5, MB_ZC + 27.5), C_PCB, C_NEW, lw=0.9)  # main board
P(ax, DR(MB_YF, MB_YF - 27.5, MB_ZC + 22.5 - 13.25, MB_ZC + 22.5 - 0.75), '#8a8a8a', '#444444', lw=0.4)   # NID100-5
P(ax, DR(MB_YF, MB_YF - 9.8, MB_ZC + 22.5 - 27.4, MB_ZC + 22.5 - 20.6), '#e8e4da', '#555555', lw=0.4)     # J6 plug
P(ax, DR(MB_YF, MB_YF - 9.8, MB_ZC + 22.5 - 48.7, MB_ZC + 22.5 - 41.9), '#e8e4da', '#555555', lw=0.4)     # J1 plug
P(ax, DR(MB_YB + 5.13, MB_YB - 1.37, MB_ZC - 47.5, MB_ZC - 27.5), 'none', C_HID, lw=0.6, ls=(0, (3, 2)))  # Pi power plug
# today's main board
R(ax, -65.0, -63.4, 34.0, 89.0, 'none', '#b03a2e', lw=0.7, ls=(0, (3, 2)))
ax.plot([24, -92], [-3.0, -3.0], color='#999999', lw=0.5)
# labels: column right of the door
LC = -101.0
note(ax, D2W(MB_YF, MB_ZC + 25.0), 'Main board, new place: on four posts\nbehind the ReSpeaker. Parts and plugs\nface the door; fitted from the back.', (LC, 158.0), color=C_NEW)
note(ax, D2W(MB_YF - 27.5, MB_ZC + 10.0), 'Power module (27.5 tall): about 1.5 mm\nfrom the door frame at its tightest spot,\n30 mm toward the viewer\'s right.', (LC, 134.0))
note(ax, D2W(-23.71, -40.0), 'ReSpeaker: 4 mm lower, on a new carrier.', (LC, 115.0))
note(ax, D2W(MB_YB - 1.37, MB_ZC - 40.0), 'Pi power plug, below the board\n(drawn from x −22).', (LC, 99.0), color=C_HID)
note(ax, (-65.0, 70.0), "Today's main board and bracket:\nremoved.", (LC, 80.0), color='#b03a2e')
note(ax, (-82.0, 50.0), 'Door: unchanged. Its 4 screws now\npass through the plate.', (LC, 60.0), color='#5a4f3a')
note(ax, (-76.0, 16.0), 'Inlet board and its cradle:\non the plate.', (LC, 40.0), color=C_PLATE_E)
note(ax, (-56.0, 8.7), 'Pi on four posts on the plate.', (LC, 22.0))
note(ax, (-60.0, 1.2), 'Base plate, 2.5 thick, out to the edge;\n0.3 gap to the shell and the door.', (LC, 6.0), color=C_PLATE_E)
note(ax, (1.0, 3.9), 'Tongue under the chin\n(drawn from x 28)', (21.0, -9.5), color=C_PLATE_E)
ax.text(13.5, 120.0, 'glass', rotation=78, ha='center', va='center', fontsize=6.3, color='#333333')
ax.set_xlim(24, -152); ax.set_ylim(-14.5, 185); ax.set_aspect('equal')
ax.set_title('A  centre section (x 0.3)', fontsize=9, loc='left', fontweight='bold')

# =============================== B: speaker section ===============================
ax = axB
low = [(5.73, 2.8)] + arc(FY, FZ, 5.3, A_R53, 0, 8) + [(6.8, 9.7), (4.3, 9.7), (4.3, 8.0), (0.7, 8.0), (0.7, 5.0), (4.1, 5.0), (3.5, 4.1),
       (3.1, 3.7), (2.6, 3.4), (1.5, 3.2), (1.5, 2.8)]
P(ax, low, C_SHELL, C_SHELL_E)
for z0, z1 in ((11.6, 14.1), (16.0, 18.4), (20.3, 22.7), (24.6, 27.0), (28.9, 31.4), (33.3, 35.7), (37.6, 40.0), (41.9, 44.4)):
    R(ax, 4.3, 6.8, z0, z1, C_SHELL, C_SHELL_E, lw=0.3)
up = [(4.3, 46.3), (6.8, 46.3), (6.8, 48.5), (6.7, 49.0), (6.7, 49.2), (4.8, 48.8), (4.4, 50.3), (7.1, 50.8), (6.7, 52.8), (9.9, 53.5),
      (-11.4, 153.7), (-8.9, 154.3), (-10.5, 162.1), (-13.1, 161.5), (-16.0, 175.4), (-19.3, 174.8), (-19.9, 177.6), (-20.4, 178.8),
      (-20.8, 179.2), (-21.9, 179.9), (-22.5, 180.0), (-22.5, 177.2), (-22.2, 176.7), (-21.9, 175.3), (-23.0, 175.3), (-23.4, 175.1),
      (-24.2, 172.8), (-28.0, 172.8), (-27.3, 174.9), (-27.4, 175.2), (-27.7, 175.3), (-28.6, 175.2), (-29.0, 174.7), (-38.0, 148.4),
      (-42.0, 136.2), (-45.5, 124.3), (-48.7, 113.1), (-51.5, 102.3), (-54.6, 89.2), (-57.0, 78.0), (-56.7, 77.0), (-56.2, 74.8),
      (-55.7, 72.6), (-55.2, 70.6), (-55.0, 69.5), (-57.8, 53.0), (-59.7, 38.2), (-61.2, 23.5), (-62.4, 6.5), (-60.8, 6.5),
      (-60.0, 18.9), (-58.9, 18.8), (-58.7, 20.6), (-60.8, 21.1), (-60.1, 28.8), (-57.9, 28.9), (-57.8, 30.7), (-58.9, 30.7),
      (-57.4, 43.7), (-55.6, 56.3), (-54.5, 57.6), (-54.1, 60.2), (-54.7, 61.8), (-53.5, 68.7), (-53.5, 78.6), (-52.5, 83.5),
      (-47.9, 102.7), (-45.6, 111.7), (-41.9, 124.7), (-35.0, 147.1), (-27.2, 170.1), (-26.0, 170.1), (-25.7, 170.9), (-24.4, 170.9),
      (-24.1, 171.8), (-22.8, 171.8), (-21.8, 174.7), (4.5, 51.0), (0.7, 51.0), (0.7, 48.0), (4.3, 48.0)]
P(ax, up, C_SHELL, C_SHELL_E)
chin_cloth(ax, 48.5)
back = [(-29.0, 174.7), (-38.0, 148.4), (-42.0, 136.2), (-45.5, 124.3), (-48.7, 113.1), (-51.5, 102.3), (-54.6, 89.2), (-57.0, 78.0)]
P(ax, [(y - 0.7, z) for y, z in back] + back[::-1], C_CLOTH, 'none', lw=0)
door = [(-65.9, 6.2), (-65.6, 4.4), (-64.5, 2.8), (-59.3, 2.8), (-59.3, 3.6), (-61.0, 3.6), (-62.2, 4.6), (-62.6, 5.4), (-62.7, 6.0),
        (-61.7, 21.1), (-60.4, 34.8), (-58.7, 48.3), (-56.3, 63.7), (-56.6, 65.5), (-57.2, 68.5), (-57.7, 70.6), (-58.1, 72.3),
        (-59.7, 63.4), (-58.4, 62.4), (-57.5, 61.3), (-58.0, 57.6), (-59.3, 56.8), (-60.8, 56.3), (-62.1, 47.3), (-64.0, 31.2), (-65.3, 15.4)]
P(ax, door, C_DOOR, C_SHELL_E)
dout = [(-64.5, 2.8), (-65.6, 4.4), (-65.9, 6.2), (-65.3, 15.4), (-64.0, 31.2), (-62.1, 47.3), (-60.8, 56.3), (-59.7, 63.4), (-58.1, 72.3)]
P(ax, [(y - 0.7, z) for y, z in dout] + dout[::-1], C_CLOTH, 'none', lw=0)
plate(ax, [(-59.0, 0.0), (-60.3, 0.1), (-62.4, 0.6), (-63.9, 1.3), (-65.4, 2.5), (FY + 6.0 * math.cos(math.radians(A_PL)), 2.5)])
foot(ax, -11.5)
# speaker box on the plate, driver on the box
bx = [(-52.0, 2.5), (-3.7, 2.5), (-3.7, 7.7), (-5.7, 7.7), (-5.7, 4.0), (-50.5, 4.0), (-50.5, 74.5), (-5.7, 74.5), (-5.7, 48.3),
      (-3.7, 48.3), (-3.7, 76.0), (-52.0, 76.0)]
P(ax, bx, C_BOX, C_BOX_E, lw=0.7)
for yb in (-12.0, -45.0):                                                # box-bottom screws (drawn from x 51 / 64)
    R(ax, yb - 3.5, yb + 3.5, 4.0, 9.0, C_BOX, C_BOX_E, lw=0.5)
    R(ax, yb - 2.1, yb + 2.1, 2.6, 8.3, C_INS, '#7a5a10', lw=0.3)
    screw_up(ax, yb, 6.6)
P(ax, [(-3.0, 8.0), (-3.0, 48.0), (-12.0, 45.0), (-19.0, 39.0), (-29.1, 37.0), (-29.1, 19.0), (-19.0, 17.0), (-12.0, 11.0)], '#b8b8b8', '#555555', lw=0.5)
R(ax, -3.0, 0.0, 5.0, 51.0, '#6f6f6f', '#333333', lw=0.4)
for z0, z1 in ((5.0, 8.0), (48.0, 51.0)):
    R(ax, 0.0, 0.7, z0, z1, C_FOAM, 'none', lw=0)
for zc in (10.2, 45.7):                                                  # driver screws (drawn from x 52.8 / 88.2)
    R(ax, -9.5, 0.0, zc - 1.5, zc + 1.5, '#5a5a5a', 'black', lw=0.3); R(ax, 0.0, 1.65, zc - 2.85, zc + 2.85, C_STEEL, 'black', lw=0.3)
# top tab and its screw (drawn from x 57): boss on the wall behind the screen, insert, M3 from the back
wy = lambda z: 4.5 - (z - 51.0) * 0.2126
P(ax, [(wy(84.2), 84.2), (-3.7, 84.2), (-3.7, 75.9), (wy(75.9), 75.9)], C_SHELL, C_NEW, lw=0.6, ls=(0, (3, 1.5)))
R(ax, -3.7, 2.0, 77.9, 82.1, C_INS, '#7a5a10', lw=0.3)
P(ax, [(-6.2, 76.0), (-3.7, 76.0), (-3.7, 84.0), (-6.2, 84.0)], C_BOX, C_BOX_E, lw=0.7)
R(ax, -6.2, 1.8, 78.5, 81.5, '#5a5a5a', 'black', lw=0.3); R(ax, -7.85, -6.2, 77.15, 82.85, C_STEEL, 'black', lw=0.3)
ax.annotate('', xy=(-9.0, 80.0), xytext=(-50.5, 80.0), arrowprops=dict(arrowstyle='->', lw=0.8, color=C_BOX_E, ls=(0, (5, 2)), shrinkA=0, shrinkB=0))
slab(ax, pcb=False)
ax.plot([24, -70], [-3.0, -3.0], color='#999999', lw=0.5)
LC = -79.0
note(ax, (-5.0, 82.5), 'Top of the box: a slotted tab and one\nM3 from the back into an insert in the\nshell. Drawn from x 57, beside the\ndisplay-screw path.', (LC, 150.0), color=C_BOX_E)
note(ax, (-45.0, 80.0), 'Path of the key for that screw,\nwith the door off.', (LC, 118.0), color=C_BOX_E)
note(ax, (-3.0, 40.0), 'Driver screwed to its box (4 screws):\na sealed speaker you can test on the\nbench. A foam ring seals it to the shell.', (LC, 94.0), color='#333333')
note(ax, (-51.2, 50.0), 'Speaker box: stands on the plate and\nenters the shell from below with it.', (LC, 62.0), color=C_BOX_E)
note(ax, (-45.0, 0.3), '2 screws from below into inserts\nin the box.', (LC, 30.0), color=C_BOX_E)
note(ax, (-64.0, 20.0), 'Door', (LC, 12.0), color='#5a4f3a')
note(ax, (4.0, 1.0), 'Rounded rim of the plate:\nsee the enlarged edge', (21.0, -9.5), color=C_PLATE_E)
ax.set_xlim(24, -126); ax.set_ylim(-14.5, 185); ax.set_aspect('equal')
ax.set_title('B  speaker section (x 70.5)', fontsize=9, loc='left', fontweight='bold')

# =============================== bottom front edge, enlarged ===============================
ZT = 15.0; YR = -19.0
ax = axT                                                                  # today
sh = [(6.8, 9.7), (6.8, FZ)] + arc(FY, FZ, 5.3, 0, -90, 16) + [(-4.5, 0.7), (-4.5, 0.0), (YR, 0.0), (YR, 2.5), (1.5, 2.5), (1.5, 3.2),
      (2.6, 3.4), (3.1, 3.7), (3.5, 4.1), (4.1, 5.0), (0.7, 5.0), (0.7, 8.0), (4.3, 8.0), (4.3, 9.7)]
P(ax, sh, C_SHELL, C_SHELL_E)
R(ax, 4.3, 6.8, 11.6, 14.1, C_SHELL, C_SHELL_E, lw=0.4)
P(ax, [(7.5, ZT), (7.5, FZ)] + arc(FY, FZ, 6.0, 0, -90, 16) + [(-4.5, 0.0), (-4.5, 0.7)] + arc(FY, FZ, 5.3, -90, 0, 16) + [(6.8, ZT)], C_CLOTH, 'none', lw=0)
P(ax, [(-3.7, 3.7), (-3.7, 7.7), (-5.7, 7.7), (-5.7, 5.2), (YR, 5.2), (YR, 3.7)], C_BOX, C_BOX_E, lw=0.7)
R(ax, -3.0, 0.0, 5.0, ZT, '#6f6f6f', '#333333', lw=0.4)
R(ax, 0.0, 0.7, 5.0, 8.0, C_FOAM, 'none', lw=0); R(ax, -3.7, -3.0, 5.0, 7.7, C_FOAM, 'none', lw=0)
R(ax, -17.85, -5.15, -3.0, 0.5, '#2f2f2f', 'none', lw=0, alpha=0.45)
ax.plot([12, YR], [-3.0, -3.0], color='#999999', lw=0.5)
note(ax, (0.0, 0.35), 'cloth wraps under the edge\n(6 mm strip)', (11.0, -6.0), fs=7.2)
note(ax, (-10.0, 1.3), 'floor: part of the shell', (-7.0, -6.0), fs=7.2)
note(ax, (-11.0, 4.4), 'speaker box', (-9.0, 11.5), fs=7.2, color=C_BOX_E)
note(ax, (-3.0, 11.0), 'driver', (-6.5, 13.6), fs=7.2)
ax.set_xlim(12, YR); ax.set_ylim(-8.2, ZT); ax.set_aspect('equal')
ax.set_title('Today', fontsize=9.5, loc='left', fontweight='bold')

ax = axN                                                                  # proposed
P(ax, low, C_SHELL, C_SHELL_E)
R(ax, 4.3, 6.8, 11.6, 14.1, C_SHELL, C_SHELL_E, lw=0.4)
P(ax, [(7.5, ZT), (7.5, FZ)] + arc(FY, FZ, 6.0, 0, A_R60, 10) + arc(FY, FZ, 5.3, A_R53, 0, 10) + [(6.8, ZT)], C_CLOTH, 'none', lw=0)
P(ax, arc(FY, FZ, 6.0, A_PL, -90, 14) + [(YR, 0.0), (YR, 2.5)], C_PLATE, C_PLATE_E, lw=1.0)
P(ax, [(-3.7, 2.5), (-3.7, 7.7), (-5.7, 7.7), (-5.7, 4.0), (YR, 4.0), (YR, 2.5)], C_BOX, C_BOX_E, lw=0.7)
R(ax, -3.0, 0.0, 5.0, ZT, '#6f6f6f', '#333333', lw=0.4)
R(ax, 0.0, 0.7, 5.0, 8.0, C_FOAM, 'none', lw=0); R(ax, -3.7, -3.0, 5.0, 7.7, C_FOAM, 'none', lw=0)
R(ax, -17.85, -5.15, -3.0, 0.5, '#2f2f2f', 'none', lw=0, alpha=0.45)
ax.plot([12, YR], [-3.0, -3.0], color='#999999', lw=0.5)
note(ax, (6.2, 2.65), 'cloth ends at the shell\'s\nbottom edge; 0.3 gap', (11.5, -6.0), fs=7.2)
note(ax, (4.6, 1.0), 'plate rim: painted, the\nlowest 2.5 mm of the\nrounded edge', (0.5, -6.0), fs=7.2, color=C_PLATE_E)
note(ax, (-11.0, 3.2), 'speaker box stands\non the plate', (-9.0, 11.5), fs=7.2, color=C_BOX_E)
note(ax, (0.35, 6.5), 'foam ring', (-6.5, 13.6), fs=7.2, color=C_FOAM)
ax.set_xlim(12, YR); ax.set_ylim(-8.2, ZT); ax.set_aspect('equal')
ax.set_title('Proposed', fontsize=9.5, loc='left', fontweight='bold')

for ax in (axA, axB, axT, axN):
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
fig.suptitle('Base plate concept (second round) — sections; the front of the unit is on the left', x=0.012, y=0.975, ha='left',
             fontsize=11.5, fontweight='bold')
fig.savefig('fp2_concept_sections.png', dpi=200)
fig2.suptitle('Bottom front edge at the speaker, enlarged — the visible change', x=0.02, y=0.97, ha='left', fontsize=11.5, fontweight='bold')
fig2.savefig('fp2_concept_edge.png', dpi=200)
print('ok')
