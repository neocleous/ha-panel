# HA panel print audit: how the speaker boxes print (rear face down, world +y up; print height = world y + 52). Rev 2.
#   One row per box, four panels:
#   (a) section through the speaker axis (y-z plane);  (b) section through the two screw tubes (y-z plane, x_rel +-53);
#   (c) a plan section (x-y plane): left box z 15 through the USB-A slot, right box z 77 through the L-shaped hump;
#   (d) the front wall's first layer from the G-code (print height 46.6: bridge infill blue, overhang perimeters orange) over the
#       support interface under it (46.2, magenta), drawn as seen from the front.
#   In (a)-(c): black = section outline, red = faces pointing down in print (>= 45 deg), magenta = support extrusions within
#   +-0.5 mm of the plane (PrusaSlicer 2.7.2, ASSUMED X2D/ASA profile, organic trees). Writes img/box_views.png.
import sys, json, numpy as np, trimesh
sys.path.insert(0, '/home/claude/pa')
from pa_geom import load_world, to_build, b2w
from pa_gview import parse
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

U = (0, 1, 0)
NAME = {'spkbox_L': "Left speaker box (viewer's left)", 'spkbox_R': "Right speaker box (viewer's right)"}
ARW = dict(arrowstyle='->', lw=0.7, color='0.15')


def seg_world(S, off, M):
    a = np.c_[S[:, 1] - off[0], S[:, 2] - off[1], S[:, 0]]
    b = np.c_[S[:, 3] - off[0], S[:, 4] - off[1], S[:, 0]]
    return b2w(M, a), b2w(M, b)


def section(ax, m, normal, origin, h, v, pts, title, xlim, ylim, hl):
    lines, fi = trimesh.intersections.mesh_plane(m, normal, origin, return_faces=True)
    d = m.face_normals[fi] @ np.array(U, float)
    ang = np.degrees(np.arcsin(np.clip(-d, -1, 1)))
    for L, a in zip(lines, ang):
        ax.plot(L[:, h], L[:, v], 'r' if a >= 45 else 'k', lw=1.3 if a >= 45 else 0.7)
    if len(pts):
        ax.plot(pts[:, h], pts[:, v], '.', color='m', ms=1.3, alpha=0.6)
    if v == 1:
        ax.axhline(-52.0, color='0.55', lw=2.5)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect('equal'); ax.grid(True, lw=0.3)
    ax.set_title(title, fontsize=8.5); ax.tick_params(labelsize=6)
    ax.set_xlabel(hl, fontsize=7)
    ax.set_ylabel('world y (mm); print height = y + 52' if v == 1 else 'world z (mm)', fontsize=7)


def note(ax, text, xy, xytext):
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=6.6, arrowprops=ARW, ha='left', va='center',
                bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='0.7', lw=0.4, alpha=0.9))


fig, axes = plt.subplots(2, 4, figsize=(22, 11.2), dpi=100)
for row, tag in enumerate(('spkbox_L', 'spkbox_R')):
    s = 1 if tag == 'spkbox_L' else -1
    m = load_world(tag); mb, M = to_build(m, U)
    off = json.load(open('/home/claude/pa/data/C_%s_plan.json' % tag))['offset']
    S = parse('/home/claude/pa/slice/gc_%s_plan.gcode' % tag)
    sup = S[S[:, 5] <= 1]
    A, B = seg_world(sup, off, M); mid = (A + B) / 2
    lo, hi = m.bounds
    nm = NAME[tag]
    # (a) speaker axis
    ax = axes[row, 0]; x0 = 70.5 * s
    section(ax, m, (1, 0, 0), (x0, 0, 0), 2, 1, mid[np.abs(mid[:, 0] - x0) < 0.5],
            '%s\n(a) section through the speaker axis, x_rel %.1f' % (nm, x0), (0, 88), (-56, 3), 'world z (mm)')
    note(ax, 'front wall: bridged in one layer\nat print height 46.6', (62, -5.8), (42, -17))
    note(ax, 'Ø40 speaker bore', (28, -4.2), (17, 1.0))
    ax.text(30, -36, 'sealed chamber', fontsize=7, color='0.35')
    ax.text(30, -54.6, 'rear face on the bed', fontsize=6.5, color='0.35')
    if s < 0:
        note(ax, 'hump pocket ceiling (inside):\nno support, droops, hidden', (77.5, -11.6), (40, -26))
        note(ax, 'hump outer step (outside):\ntree from the bed', (80, -24.1), (52, -42))
    # (b) screw tubes
    ax = axes[row, 1]; x1 = 52.8 * s
    section(ax, m, (1, 0, 0), (x1, 0, 0), 2, 1, mid[np.abs(mid[:, 0] - x1) < 0.5],
            '(b) section through both screw tubes, x_rel %.1f' % x1, (0, 88), (-56, 3), 'world z (mm)')
    note(ax, 'upper screw tube: Ø6.2 bore open at the rear,\nsupport column inside from the bed;\nØ3.4 hole through the front wall',
         (45.8, -30), (52, -30))
    if s > 0:
        note(ax, 'lower screw tube: bore opens\ninto the USB-A slot', (10.2, -15), (18, -12))
        note(ax, 'USB-A slot: open to the bed,\ntrees stand on the bed', (14, -44), (24, -44))
    else:
        note(ax, 'lower screw tube: bore opens\ninto the finger channel', (10.2, -15), (18, -12))
        note(ax, 'finger channel: open to the bed,\ntrees stand on the bed', (9, -44), (20, -46))
        note(ax, 'hump pocket\n(inside)', (78.5, -30), (60, -20))
    # (c) plan section
    ax = axes[row, 2]
    if s > 0:
        z2 = 15.0
        section(ax, m, (0, 0, 1), (0, 0, z2), 0, 1, mid[np.abs(mid[:, 2] - z2) < 0.5],
                '(c) plan section at z %.0f through the USB-A slot' % z2, (lo[0] - 3, hi[0] + 3), (-56, 3), 'x_rel (mm)')
        note(ax, 'USB-A slot roof: bridged\n(~10 mm) at print height 31', (50, -21.1), (58, -26))
        note(ax, 'trees in the slot\nstand on the bed', (52, -45), (60, -40))
    else:
        z2 = 77.0
        section(ax, m, (0, 0, 1), (0, 0, z2), 0, 1, mid[np.abs(mid[:, 2] - z2) < 0.5],
                '(c) plan section at z %.0f through the L-shaped hump on top' % z2, (lo[0] - 3, hi[0] + 3), (-56, 3), 'x_rel (mm)')
        note(ax, 'pocket ceiling (inside): no support', (-75, -11.6), (-88, -4))
        note(ax, 'outer step (outside): tree from the bed', (-87.5, -26), (-92, -34))
        note(ax, 'ledge deep in the pocket (inside):\none 9 mm tree from the rear wall,\n~45 mm behind the bore', (-49.5, -45), (-90, -46))
    # (d) front wall's first layer
    ax = axes[row, 3]
    for zb in (46.2, 46.6):
        L = S[np.abs(S[:, 0] - zb) < 1e-3]
        a, b = seg_world(L, off, M)
        for p, q, t in zip(a, b, L[:, 5]):
            if t <= 1:
                c, lw = 'm', 0.6
            elif zb > 46.4:
                c, lw = {2: ('tab:blue', 0.35), 3: ('orange', 0.6)}.get(int(t), ('k', 0.5))
            else:
                continue
            ax.plot([p[0], q[0]], [p[2], q[2]], color=c, lw=lw)
    ax.set_aspect('equal'); ax.grid(True, lw=0.3); ax.tick_params(labelsize=6)
    ax.set_xlim(lo[0] - 3, hi[0] + 3); ax.set_ylim(lo[2] - 3, hi[2] + 3)
    ax.set_title('(d) front wall, first layer (print height 46.6) seen from the front:\nbridge lines blue, overhang perimeters orange, '
                 'support interface under it magenta', fontsize=8.5)
    ax.set_xlabel('x_rel (mm)', fontsize=7); ax.set_ylabel('world z (mm)', fontsize=7)
    note(ax, 'Ø40 bore rim:\nsupport ring', (70.5 * s + 19.5 * s, 30), (70.5 * s - 12 if s > 0 else 70.5 * s - 8, 60))
    note(ax, 'screw-tube seats\n(support from inside the bores)', (52.7 * s, 45.8), (52.7 * s - (2 if s > 0 else 20), 66))
    note(ax, 'touch-clip block', (47.0 * s, 38), (52.7 * s - (2 if s > 0 else 20), 18))
fig.suptitle('Speaker boxes as printed: rear face down, 51.8 mm tall. Black = section outline, red = faces pointing down in print '
             '(≥45°), magenta = tree supports (PrusaSlicer 2.7.2, ASSUMED X2D/ASA profile); grey bar = bed', fontsize=10)
fig.tight_layout(rect=(0, 0, 1, 0.97))
fig.savefig('/home/claude/pa/img/box_views.png')
print('ok')
