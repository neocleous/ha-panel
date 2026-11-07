import numpy as np, bz, sys
sys.path.insert(0, '.')
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Polygon as MPoly, Circle
from outlines import *
from evalpoly import mask
R = dict(np.load('plane_cur.npz'))
X, Z = np.meshgrid(bz.XS, bz.ZS)
ins = R['inside']; hf = R['hf'] - 0.5; hb = np.minimum(R['hb_door'], R['hb_fixed'])
bands = [0, 3, 10, 16, 24, 28, 1e9]
cols = ['#b2182b', '#ef8a62', '#fddbc7', '#d1e5f0', '#92c5de', '#e8eef4']
cm = ListedColormap(cols); nrm = BoundaryNorm(bands, cm.N)
fig, ax = plt.subplots(figsize=(13, 12))
im = ax.imshow(np.where(ins, hf, np.nan), origin='lower', extent=[bz.X0, bz.X1, bz.Z0, bz.Z1], cmap=cm, norm=nrm, interpolation='nearest')
cb = plt.colorbar(im, ax=ax, fraction=0.03, ticks=[0, 3, 10, 16, 24, 28]); cb.set_label('front height to the first fixed part or keep-out, 0.5 clearance (mm)')
# areas the board slab cannot use (not in the free region), lightly grey
ax.imshow(np.where(~ins & (np.abs(X) < 70) & (Z > 5) & (Z < 128), 1.0, np.nan), origin='lower', extent=[bz.X0, bz.X1, bz.Z0, bz.Z1], cmap=ListedColormap(['#9e9e9e']), alpha=0.35, interpolation='nearest')
pm = mask(PMAX)
bare = pm & (hb < 3.4)
ax.contourf(X, Z, bare.astype(float), levels=[0.5, 1.5], colors='none', hatches=['////'])
ax.contour(X, Z, bare.astype(float), levels=[0.5], colors='#7b3294', linewidths=0.8)
ax.add_patch(MPoly(PMAX, closed=True, fill=False, ec='k', lw=2.2))
ax.add_patch(MPoly(T, closed=True, fill=False, ec='#0571b0', lw=1.8, ls='--'))
ax.add_patch(MPoly(C0, closed=True, fill=False, ec='#4d4d4d', lw=1.0, ls=':'))
for hx, hz in HOLES:
    ax.add_patch(Circle((hx, hz), 1.35, fill=False, ec='k', lw=1)); ax.add_patch(Circle((hx, hz), 4, fill=False, ec='k', lw=0.7, ls=':'))
ax.contour(X, Z, ((R['hbr'] < 2) & pm).astype(float), levels=[0.5], colors='#1a9641', linewidths=1.2)
txt = dict(fontsize=8.5, ha='center', va='center')
ax.text(0, 105, 'tab\nfront >= 41', **txt); ax.text(0, 60, 'base (today 90 x 50)\nfront >= 30', **txt)
ax.text(-28, 29, 'leg (optional)  front >= 27\n(24 in x -17.6...-12: K7)', **txt); ax.text(38.6, 27.5, 'leg\n(optional)', **txt)
ax.text(25, 29, 'J2 plug\npath', fontsize=7.5, ha='center'); ax.text(0, 27, 'cradle /\nPD / pigtail', fontsize=7.5, ha='center')
ax.text(-47, 91.5, 'K5', fontsize=7.5); ax.text(50.5, 93.5, 'K5', fontsize=7.5)
for x0, z0 in ((23.5, 108), (-23.5, 108), (32.5, 101), (-32.5, 101)):
    ax.text(x0, z0, 'cap\nkey', fontsize=7, ha='center', va='center')
ax.text(56, 55, 'speaker box\nfront <= 10.9\n(bracket post\nat 46.5-52.5)', fontsize=7.5, ha='center')
ax.text(-56, 55, 'speaker box\nfront <= 10.9\n(bracket post\nat -46.5..-52.5)', fontsize=7.5, ha='center')
ax.text(0, 125.5, 'door (sweep / back gap)', fontsize=7.5, ha='center')
ax.set_xlim(70, -70); ax.set_ylim(15, 130); ax.set_aspect('equal'); ax.grid(alpha=.25)
ax.set_xticks(np.arange(-70, 71, 5)); ax.set_yticks(np.arange(15, 131, 5)); ax.tick_params(labelsize=7)
ax.set_xlabel('x_rel (mm), seen from the Pi side (KiCad top view: x_board = 45 - x_rel)'); ax.set_ylabel('z (mm)  (y_board = 84 - z)')
ax.set_title('Main board at the current plane (front face y -63.4): maximum outline (black; legs below z 34 optional), T outline (blue dashed), today (dotted)\n'
             'hatched = back gap to the door or a cap-key lane < 3.4 (bare board only); green = bracket 0-0.9 mm in front; grey = no board',
             fontsize=9.5)
plt.savefig('main_board_outline_2026-11-07.png', dpi=110, bbox_inches='tight')
