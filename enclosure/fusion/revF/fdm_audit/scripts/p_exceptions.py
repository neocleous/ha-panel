"""Pictures for the exceptions put to Daniel and for the main findings (world coordinates, mm)."""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from sec import section_polys, patch
from secm import COLS
from s3_posts import panel as gpanel
from fdm_lib import *

def secax(ax, axis, value, win, parts, title, grid=1.0):
    for nm in parts:
        for p in section_polys(nm, axis, value):
            ax.add_patch(patch(p, facecolor=COLS.get(nm, '#bbb'), edgecolor='k', linewidth=0.6))
    a0, a1, b0, b1 = win
    ax.set_xlim(a0, a1); ax.set_ylim(b0, b1); ax.set_aspect('equal')
    ax.set_xticks(np.arange(np.ceil(a0 / grid) * grid, a1 + 1e-9, grid)); ax.set_yticks(np.arange(np.ceil(b0 / grid) * grid, b1 + 1e-9, grid))
    ax.tick_params(labelsize=6); ax.grid(True, linewidth=0.3, alpha=0.5); ax.set_title(title, fontsize=10)
    lab = {'x': ('front  ←  world y  →  back is left', 'height z'), 'y': ('world x', 'height z'), 'z': ('world x', 'world y')}[axis]
    ax.set_xlabel('mm', fontsize=7)

def note(ax, text, xy, xytext, col='#b00020'):
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=9, color=col, ha='center', va='center',
                arrowprops=dict(arrowstyle='->', color=col, lw=1.1), bbox=dict(boxstyle='round,pad=0.25', fc='white', ec=col, lw=0.8))

# ---- Q1: the lip round the door opening
fig = plt.figure(figsize=(13, 6.2), dpi=100)
ax0 = fig.add_axes([0.01, 0.02, 0.50, 0.90]); ax0.imshow(mpimg.imread('../img/ov_shell_rear.png')); ax0.axis('off')
ax0.set_title('Shell from behind, door off. Yellow: the 1.2 lip. Orange: its ten magnet seats (0.45)', fontsize=10)
ax1 = fig.add_axes([0.56, 0.10, 0.42, 0.80])
secax(ax1, 'x', 0, (-64, -50, 143, 160), ['HOUSING_F_front', 'HOUSING_F_door'], 'Cut through the top of the door opening (door on, purple)')
note(ax1, 'lip: 1.2 thick,\n8.5 standing free', (-57.3, 150.0), (-53.2, 147.0))
note(ax1, 'its foot: a joint\nbetween layers', (-55.6, 156.6), (-52.6, 153.2))
note(ax1, 'door', (-60.3, 149.0), (-62.3, 154.5), col='#4b3b8f')
fig.savefig('../img/Q1_lip.png'); plt.close(fig)

# ---- Q2: magnet seats
fig, axs = plt.subplots(1, 2, figsize=(12, 5.4), dpi=100)
secax(axs[0], 'x', -16, (-63, -53, 141, 156), ['HOUSING_F_front', 'HOUSING_F_door'], 'Cut through one magnet pair (magnets not drawn)')
note(axs[0], 'door skin 0.45', (-57.55, 148.5), (-61.2, 151.6), col='#4b3b8f')
note(axs[0], 'door magnet\nsits here', (-58.9, 148.0), (-61.3, 145.6), col='#4b3b8f')
note(axs[0], 'lip skin 0.45', (-56.7, 149.4), (-54.6, 146.4))
note(axs[0], 'lip magnet\nsits here', (-55.5, 149.0), (-54.5, 153.6))
gpanel(axs[1], 'door', 145.2, (-25, -12, -62, -54), 'Door as sliced: the skin is one line wide')
axs[1].set_title('Door as sliced, one layer: the skin is a single line', fontsize=10)
fig.tight_layout(); fig.savefig('../img/Q2_magnet_seats.png'); plt.close(fig)

# ---- Q3: cloth groove under the screen
fig, ax = plt.subplots(1, 1, figsize=(7.2, 7.4), dpi=100)
secax(ax, 'x', 0, (1.5, 9.5, 46.5, 54.5), ['HOUSING_F_front', 'HOUSING_F_plate', 'SLAB_frame'], 'Cut through the chin below the screen, at the middle', grid=0.5)
note(ax, 'web 0.5', (5.2, 49.9), (2.6, 49.2))
note(ax, 'cloth groove,\n1.3 deep', (6.2, 49.85), (8.4, 48.2))
note(ax, 'rail', (5.3, 51.6), (2.6, 52.6))
note(ax, 'chin wall 2.5', (5.5, 47.2), (8.4, 47.0))
note(ax, 'bezel', (8.3, 50.5), (8.8, 53.2), col='#2e6b3a')
note(ax, 'screen plate', (6.6, 53.6), (3.2, 54.0), col='#8a6d1c')
fig.tight_layout(); fig.savefig('../img/Q3_groove_web.png'); plt.close(fig)

# ---- F: door bars
fig, axs = plt.subplots(1, 2, figsize=(12, 4.6), dpi=100)
secax(axs[0], 'z', 90, (-28, 28, -77, -67), ['HOUSING_F_door'], 'Door, cut across the vent bars at mid height', grid=2)
note(axs[0], 'bar 3.0 wide, 2.5 deep,\n56.5 long, printed upright', (3.0, -73.8), (0, -69.5))
gpanel(axs[1], 'door', 87.2, (-4, 10, -76.5, -69.5), 'as sliced')
axs[1].set_title('Two bars as sliced: two wall lines and a solid core', fontsize=10)
fig.tight_layout(); fig.savefig('../img/F_door_bars.png'); plt.close(fig)
print('ok')
