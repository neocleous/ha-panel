import math, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Circle

# ---------- 1 roof plan ----------
fig, ax = plt.subplots(figsize=(11, 8.2), dpi=150)
free = {-50: (-72.9, -57.5), -45: (-77.5, -58.1), -40: (-81.2, -58.6), -35: (-84.3, -59.1), -30: (-86.8, -59.6), -25: (-88.9, -60.2),
        -22: (-89.9, -60.6), -21.9: (-89.9, -66.0), -20: (-90.5, -66.0), -15: (-91.8, -66.0), -12: (-92.4, -66.0), -8: (-93.0, -66.0), -3.7: (-93.5, -66.0)}
ys = sorted(free)
out = [(free[y][0], y) for y in ys]; inn = [(free[y][1], y) for y in reversed(ys)]
# box outline: outboard edge = free envelope's outboard edge moved 0 (it is the box outline there), rear y -52, inboard x -46, front y -3.7
box = [(-72.0, -52.0)] + [(free[y][0], y) for y in ys] + [(-46.0, -3.7), (-46.0, -52.0)]
ax.add_patch(Polygon(box, closed=True, fc='#eeeeee', ec='black', lw=1.6, zorder=1))
ax.add_patch(Polygon(out + inn, closed=True, fc='#9fd49f', ec='#2e7d32', lw=1.2, alpha=0.9, zorder=2))
# v42 raised air (L shape)
v42 = [(-90.7, -11.5), (-51.5, -11.5), (-51.5, -42.5), (-47.5, -42.5), (-47.5, -50.5), (-55.4, -50.5), (-55.4, -22.0), (-88.0, -22.0)]
ax.add_patch(Polygon(v42, closed=True, fc='none', ec='#1565c0', lw=1.6, ls='--', zorder=4))
# key corridor
H = (-58.0, -8.25)
for ps, col in ((6, '#c62828'), (14, '#c62828')):
    s = np.array([0, 50]); ax.plot(H[0] + s * math.sin(math.radians(ps)), H[1] - s * math.cos(math.radians(ps)), color=col, lw=1.0, zorder=5)
corr = []
for s in np.linspace(0, 47, 30):
    corr.append((H[0] + s * math.sin(math.radians(6)) - 4.7 * math.cos(math.radians(6)), H[1] - s * math.cos(math.radians(6)) - 4.7 * math.sin(math.radians(6))))
for s in np.linspace(47, 0, 30):
    corr.append((H[0] + s * math.sin(math.radians(14)) + 4.7 * math.cos(math.radians(14)), H[1] - s * math.cos(math.radians(14)) + 4.7 * math.sin(math.radians(14))))
ax.add_patch(Polygon(corr, closed=True, fc='#ffcdd2', ec='none', alpha=0.75, zorder=3))
ax.add_patch(Rectangle((-62.2, -6.6), 8.4, 2.7, fc='#555555', ec='black', zorder=6))
ax.add_patch(Circle(H, 2.85, fc='white', ec='black', zorder=7))
ax.annotate('box-top screw\n(tab on the box)', xy=(-58, -6.0), xytext=(-52.5, -1.2), fontsize=8, ha='left', arrowprops=dict(arrowstyle='-', lw=0.6))
ax.text(-78, -30, 'new raised roof\n(option 1)\nenvelope 6.9 cm$^3$,\nz 76 to 82', fontsize=10, ha='center', va='center', color='#1b5e20', zorder=8)
ax.text(-54.5, -33, 'key path\n2.0 key,\n6 to 14 deg', fontsize=8, ha='center', va='center', color='#b71c1c', rotation=-80, zorder=8)
ax.text(-72, -16.5, 'version 42 raised roof (dashed): option 2 restores\nthe part of it outside the key path', fontsize=8, ha='center', color='#0d47a1', zorder=8)
ax.text(-47.3, -28, 'inboard\nwall', fontsize=7, ha='right', va='center', color='#444444')
ax.set_xlim(-98, -42); ax.set_ylim(-56, 2); ax.set_aspect('equal')
ax.set_xlabel('x_rel (mm): the right speaker box, seen from above; the unit\'s middle is to the right')
ax.set_ylabel('y (mm): screen side up, door side down')
ax.set_title('Right speaker box: where the roof can be raised (z 76 to 82)', fontsize=12)
ax.grid(True, lw=0.3, alpha=0.5)
fig.text(0.02, 0.02, 'Grey: the box\'s flat roof today (z 76). Pink: the key\'s path with 2.0 clear and a 1.5 wall. Green: free of every part, also while the plate unit is lifted in.', fontsize=8)
fig.savefig('roof_plan.png', bbox_inches='tight'); plt.close(fig)

# ---------- 2 rim section ----------
def arc(cx, cz, r, z0, z1, n=60):
    zs = np.linspace(z0, z1, n); return list(zip(cx + np.sqrt(np.maximum(r * r - (cz - zs) ** 2, 0)), zs))
fig, axs = plt.subplots(1, 2, figsize=(13, 6.2), dpi=150, sharey=True)
for k, ax in enumerate(axs):
    cx, cz = 89.5, 6.0
    step = k == 1
    # plate
    ztop = 2.5
    if not step:
        plate = [(86.0, 0.0)] + arc(cx, cz, 6.0, 0.0, 2.5) + [(86.0, 2.5)]
        # arc at z=0 gives x=89.5; plate bottom from 86 to 89.5
    else:
        plate = [(86.0, 0.0)] + arc(cx, cz, 6.0, 0.0, 1.8) + [(91.2, 1.8), (91.2, 2.5), (86.0, 2.5)]
    ax.add_patch(Polygon(plate, closed=True, fc='#303030', ec='black', lw=0.8, zorder=2))
    # shell wall
    shell = [(92.2, 2.8)] + arc(cx, cz, 5.3, 2.8, 6.0) + [(94.8, 9.0), (92.2, 9.0)]
    ax.add_patch(Polygon(shell, closed=True, fc='#8a8a8a', ec='black', lw=0.8, zorder=2))
    # cloth
    outer = arc(cx, cz, 6.0, 2.8, 6.0) + [(95.5, 9.0)]
    inner = [(94.8, 9.0)] + list(reversed(arc(cx, cz, 5.3, 2.8, 6.0)))
    if not step:
        cloth = outer + inner
    else:
        xo = cx + math.sqrt(36 - 3.2 ** 2); xi = cx + math.sqrt(5.3 ** 2 - 3.2 ** 2)
        under = [(xi, 2.8), (92.2, 2.8), (92.2, 2.1), (xo - 0.25, 2.1), (xo, 2.35), (xo, 2.8)]
        cloth = [(xo, 2.35)] + outer + inner + [(92.2, 2.8), (92.2, 2.1), (xo - 0.25, 2.1)]
    ax.add_patch(Polygon(cloth, closed=True, fc='#c9b458', ec='#7a6a1a', lw=0.8, zorder=3))
    # table and foot hint
    ax.axhline(-2.9, color='#8d6e63', lw=2)
    ax.text(86.2, -2.75, 'table', fontsize=7, color='#5d4037', va='bottom')
    ax.set_xlim(85.5, 97.5); ax.set_ylim(-3.4, 9.2); ax.set_aspect('equal'); ax.grid(True, lw=0.3, alpha=0.5)
    ax.set_xlabel('x_rel (mm), outward to the right')
    if not step:
        ax.set_title('As built (version 46)', fontsize=11)
        ax.annotate('cloth cut at the\nshell\'s edge, z 2.8', xy=(94.6, 2.85), xytext=(95.3, 0.6), fontsize=8, arrowprops=dict(arrowstyle='->', lw=0.6))
        ax.annotate('gap 0.3', xy=(93.4, 2.65), xytext=(88.2, 4.6), fontsize=8, arrowprops=dict(arrowstyle='->', lw=0.6))
        ax.text(88.0, 1.1, 'plate\n(top z 2.5)', fontsize=8, color='white', ha='center')
        ax.text(93.1, 6.5, 'shell\nwall', fontsize=8, ha='center')
        ax.text(95.45, 7.8, 'cloth 0.7', fontsize=8, rotation=90, va='center')
    else:
        ax.set_title('Proposed: cloth turned under, plate\'s rim lowered', fontsize=11)
        ax.annotate('cloth turned under\nthe wall\'s edge, 1.5 wide', xy=(93.0, 2.4), xytext=(94.6, -0.6), fontsize=8, arrowprops=dict(arrowstyle='->', lw=0.6))
        ax.annotate('rim top z 1.8\n(0.7 lower, from x 91.2 outward)', xy=(92.3, 1.8), xytext=(86.0, 5.2), fontsize=8, arrowprops=dict(arrowstyle='->', lw=0.6))
        ax.annotate('gap 0.3', xy=(92.8, 1.95), xytext=(88.6, 3.6), fontsize=8, arrowprops=dict(arrowstyle='->', lw=0.6))
        ax.text(88.0, 1.1, 'plate', fontsize=8, color='white', ha='center')
        ax.text(93.1, 6.5, 'shell\nwall', fontsize=8, ha='center')
axs[0].set_ylabel('z (mm) above the plate\'s underside')
fig.suptitle('Bottom edge at the side wall (section at y -30): cloth cut flush and cloth turned under', fontsize=12)
fig.text(0.02, 0.01, 'From the model: body outline R 6.0 about (89.5, 6.0); shell plastic 0.7 inside it; wall\'s inner face x 92.2; shell\'s bottom edge z 2.8; plate z 0 to 2.5. Cloth 0.7 thick as assumed so far.', fontsize=8)
fig.savefig('rim_section.png', bbox_inches='tight'); plt.close(fig)
print('ok')
