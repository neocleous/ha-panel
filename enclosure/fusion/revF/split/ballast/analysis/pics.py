import sys, json
sys.path.insert(0, '/home/claude/bal')
import geo, shapely
from shapely.geometry import box, Point, Polygon, LineString
from shapely.ops import unary_union, polygonize
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch, Circle, Patch, Rectangle
from matplotlib.lines import Line2D
from matplotlib.path import Path
import numpy as np

INK, INK2, MUTED, SURF = '#0b0b0b', '#52514e', '#8a8984', '#fcfcfb'
BLUE, ORANGE, AQUA = '#2a78d6', '#eb6834', '#1baf7a'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'text.color': INK, 'axes.edgecolor': MUTED,
                     'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2})

def patch(ax, geom, **kw):
    if geom is None or geom.is_empty: return
    gs = geom.geoms if hasattr(geom, 'geoms') else [geom]
    for g in gs:
        if g.geom_type != 'Polygon': continue
        verts = []; codes = []
        for ring in [g.exterior] + list(g.interiors):
            c = np.asarray(ring.coords)
            verts += c.tolist(); codes += [Path.MOVETO] + [Path.LINETO] * (len(c) - 2) + [Path.CLOSEPOLY]
        ax.add_patch(PathPatch(Path(verts, codes), **kw))

S = geo.secs(); floor = geo.floor()
F = json.load(open(geo.DATA + '/plate_faces_v65.json'))
outer = [l for l in F['1.80'] if l['outer']][0]
plate = geo.region(outer['edges'])
C = {k: shapely.from_geojson(v) for k, v in json.load(open('/home/claude/bal/cand.json')).items()}
OF = json.load(open('/home/claude/bal/opt_figs.json'))

# ---------- picture 1: plan
fig, ax = plt.subplots(figsize=(16, 9.6), facecolor=SURF)
ax.set_facecolor(SURF)
patch(ax, plate, facecolor='#e8e7e3', edgecolor=INK2, lw=0.8)
patch(ax, floor, facecolor='#f4f3f0', edgecolor='none')
free2 = geo.free_col(2.5, 5.0, clear=0.5)
free10 = geo.free_col(2.5, 13.0, clear=0.5)
patch(ax, free2, facecolor=AQUA, alpha=0.18, edgecolor='none')
patch(ax, free10, facecolor=AQUA, alpha=0.45, edgecolor='none')
walls = unary_union([S[6.5][n] for n in ('HOUSING_F_front', 'HOUSING_F_door')])
patch(ax, walls, facecolor='#b9b8b2', edgecolor='#8a8984', lw=0.4)
for n in ('SPKBOX_L', 'SPKBOX_R'):
    patch(ax, geo.filled(S[8.5][n]), facecolor='#dcdbd6', edgecolor=INK2, lw=0.9, alpha=0.85)
low = S[3.2]['FLOOR_PLATE']
patch(ax, low, facecolor='#a3a29c', edgecolor='#6f6e69', lw=0.4)
for x, y in ((50, -67), (-50, -67), (19, -74.5), (-19, -77.0)):
    ax.add_patch(Circle((x, y), 4.0, facecolor='#a3a29c', edgecolor='#6f6e69', lw=0.4))
patch(ax, S[8.5]['PI5_F'], facecolor='none', edgecolor=INK2, lw=1.0)
patch(ax, S[15.0]['CRADLE_5807'], facecolor='none', edgecolor=INK2, lw=0.9, ls='--')
patch(ax, S[8.5]['PIPWR_a_env'], facecolor='none', edgecolor=INK2, lw=0.9, ls=':')
keep_intake = geo.KEEP['intake field']; keep_sd = geo.KEEP['microSD finger channel'].intersection(floor); keep_anchor = geo.KEEP['anchor and its tie']
patch(ax, keep_intake, facecolor='none', edgecolor=INK2, hatch='//', lw=0.0)
patch(ax, keep_sd, facecolor='none', edgecolor=INK2, hatch='\\\\', lw=0.0)
patch(ax, keep_anchor, facecolor='none', edgecolor=INK2, hatch='xx', lw=0.0)
roll = S[12.0].get('LEAD_USB_RESP')
patch(ax, roll, facecolor='none', edgecolor=INK2, lw=0.8)
# weights
patch(ax, C['left'], facecolor=ORANGE, alpha=0.85, edgecolor='#9a3d17', lw=1.0, ls='--')
patch(ax, C['right'], facecolor=ORANGE, alpha=0.85, edgecolor='#9a3d17', lw=1.0, ls='--')
patch(ax, C['rear'], facecolor=BLUE, alpha=0.9, edgecolor='#174a86', lw=1.0)
# feet and lines
for x, y in ((80, -5.5), (-80, -5.5), (30, -70.6), (-30, -70.6)):
    ax.add_patch(Circle((x, y), 6.35, facecolor='none', edgecolor=INK, lw=1.2, ls=(0, (2, 2))))
for yy, lab in ((-70.6, 'rear feet line: the unit tips backward about it'), (-5.5, 'front feet line: the unit tips forward about it')):
    ax.plot([-100, 100], [yy, yy], color=INK, lw=0.9, ls='-.')
ax.text(-99, -70.6 + 0.8, 'rear feet line: the unit tips backward about it', fontsize=10, color=INK, va='bottom')
ax.text(-99, -5.5 + 0.8, 'front feet line: the unit tips forward about it', fontsize=10, color=INK, va='bottom')
ax.plot([-0.81], [-17.84], marker='+', color=INK, ms=22, mew=3)
ax.text(1.5, -16.6, 'balance point', fontsize=11, color=INK, weight='bold', bbox=dict(facecolor=SURF, edgecolor='none', alpha=0.85, pad=1.6))
# antenna and magnets
ax.add_patch(Rectangle((-42.4, -10.0), 12.4, 8.0, facecolor='none', edgecolor=INK, lw=1.2))
ax.annotate('Pi Wi-Fi antenna corner', xy=(-36, -10), xytext=(-31, -27), fontsize=10, bbox=dict(facecolor=SURF, edgecolor='none', alpha=0.85, pad=1.6), arrowprops=dict(arrowstyle='-', color=INK2, lw=0.8))
for sx in (1, -1):
    ax.plot([sx * 72.1], [-59.9], marker='s', ms=7, mfc=INK, mec=INK)
ax.annotate('lowest door magnets (25 above the floor)', xy=(72.1, -59.9), xytext=(58, -46.5), fontsize=10, ha='left', arrowprops=dict(arrowstyle='-', color=INK2, lw=0.8))
# labels
BB = dict(facecolor=SURF, edgecolor='none', alpha=0.85, pad=1.6)
def lab(x, y, s, **kw):
    ax.text(x, y, s, fontsize=kw.pop('fs', 10.5), color=kw.pop('c', INK), ha=kw.pop('ha', 'center'), va=kw.pop('va', 'center'), bbox=BB, **kw)
lab(71, -13, 'left box', fs=12, weight='bold'); lab(-71, -13, 'right box', fs=12, weight='bold')
lab(0, -46, 'Pi, board 5.5 above the floor:\nits air intake (hatched) stays open', fs=11)
lab(-54, -40, 'microSD\nfinger\nchannel', fs=9.5)
lab(58.5, -64.5, 'USB roll\nand anchor', fs=9)
lab(0, -82.3, 'cradle (dashed, from 13 up)', fs=9.5)
lab(-21, -61.0, 'Pi power plug (dotted, from 4.8 up)', fs=9)
ax.annotate('C  steel plate 10 thick behind the Pi: %.0f g' % (C['rear'].area * 10 * 7.85 / 1000), xy=(36, -62), xytext=(18, -33.5), fontsize=11, color=INK, weight='bold', bbox=dict(facecolor=SURF, edgecolor='none', alpha=0.9, pad=2),
            arrowprops=dict(arrowstyle='->', color='#174a86', lw=1.3))
ax.annotate('B  steel sheet 2.5 under the box: %.0f g' % (C['left'].area * 2.5 * 7.85 / 1000), xy=(70, -38), xytext=(48, 1.8), fontsize=11, color=INK, weight='bold',
            arrowprops=dict(arrowstyle='->', color='#9a3d17', lw=1.3))
ax.annotate('B  under the box: %.0f g' % (C['right'].area * 2.5 * 7.85 / 1000), xy=(-78, -20), xytext=(-97, 1.8), fontsize=11, color=INK, weight='bold',
            arrowprops=dict(arrowstyle='->', color='#9a3d17', lw=1.3))
ax.text(100, -88.2, 'door', fontsize=11, ha='right', color=INK2); ax.text(100, 9.2, 'screen', fontsize=11, ha='right', color=INK2)
ax.set_xlim(-101, 101); ax.set_ylim(-89, 10.5); ax.set_aspect('equal')
ax.set_xticks(range(-100, 101, 20)); ax.set_yticks(range(-80, 11, 10)); ax.tick_params(labelsize=9)
ax.grid(True, lw=0.3, color='#e2e1dc'); ax.set_axisbelow(True)
for s in ax.spines.values(): s.set_visible(False)
legend = [Patch(facecolor=AQUA, alpha=0.45, label='free from the floor up 10 (green), up 2.5 (pale)'),
          Patch(facecolor=BLUE, alpha=0.9, label='option C: plate behind the Pi'),
          Patch(facecolor=ORANGE, alpha=0.85, label='option B: sheets under the boxes'),
          Patch(facecolor='#dcdbd6', edgecolor=INK2, label='speaker boxes'),
          Patch(facecolor='none', edgecolor=INK2, hatch='//', label='keep clear')]
ax.legend(handles=legend, loc='upper center', bbox_to_anchor=(0.5, -0.045), ncol=5, frameon=False, fontsize=10)
fig.suptitle('Base plate seen from above (version 65): where weight can sit low', fontsize=15, weight='bold', x=0.02, ha='left', y=0.985)
fig.text(0.02, 0.945, 'Screen at the top, door at the bottom; the left box is on the right. Millimetres, measured on the model.', fontsize=11, color=INK2)
plt.subplots_adjust(left=0.03, right=0.99, top=0.93, bottom=0.08)
plt.savefig('/home/claude/bal/out/ballast_1_plan.png', dpi=100, facecolor=SURF)

# ---------- picture 2: what 100 g does, by where it sits
W, back, fwd = 1055.1, 52.764, 12.336
y = np.linspace(-84, 6, 361)
pb = 100 * 100 * (y + 70.6) / (W * back)
pf = 100 * 100 * (-5.5 - y) / (W * fwd)
fig, ax = plt.subplots(figsize=(16, 7.2), facecolor=SURF)
ax.set_facecolor(SURF)
ax.axvspan(-59.7, -2.0, color='#e8e7e3', zorder=0)
ax.text(-31, 66, 'middle of the plate: the Pi and its air intake;\nbeside them only the 1.2 gap under the boxes (B)', ha='center', fontsize=11, color=INK2)
ax.axhline(0, color=MUTED, lw=0.8)
ax.plot(y, pb, color=BLUE, lw=2.2, label='backward: push at the glass top edge')
ax.plot(y, pf, color=ORANGE, lw=2.2, label='forward: pull at the glass top edge')
for yy, s in ((-70.6, 'rear feet'), (-17.84, 'balance point'), (-5.5, 'front feet')):
    ax.axvline(yy, color=INK, lw=0.9, ls='-.')
    ax.text(yy + 0.6, -12.5, s, fontsize=10.5, color=INK, rotation=90, va='bottom')
pts = [('C behind the Pi', -66.4), ('B under the boxes', -25.1)]
for s, yy in pts:
    b = 100 * 100 * (yy + 70.6) / (W * back); f = 100 * 100 * (-5.5 - yy) / (W * fwd)
    ax.plot([yy, yy], [b, f], color=INK2, lw=0.8, ls=':')
    ax.plot([yy], [b], 'o', ms=9, mfc=BLUE, mec=SURF, mew=2); ax.plot([yy], [f], 'o', ms=9, mfc=ORANGE, mec=SURF, mew=2)
    ax.text(yy + 1.2, f + 2.0, '%s: forward %+.0f %%' % (s, f), fontsize=10.5, color=INK)
    ax.text(yy - 1.2 if b > 3 else yy + 1.2, b - 4.5 if b > 3 else b + 1.6, 'backward %+.1f %%' % b, fontsize=10.5, color=INK, ha='right' if b > 3 else 'left')
ax.annotate('under the balance point:\nboth %+.1f %%' % (100 * 100 / W), xy=(-17.84, 100 * 100 / W), xytext=(-15.5, 31), fontsize=10.5, color=INK, arrowprops=dict(arrowstyle='-', color=INK2, lw=0.8))
ax.set_xlim(-84, 6); ax.set_ylim(-14, 75)
ax.set_xlabel('where 100 g of weight sits, door (left) to screen (right): y in mm')
ax.set_ylabel('change of the tipping force, %')
ax.grid(True, axis='y', lw=0.3, color='#e2e1dc'); ax.set_axisbelow(True)
for s in ('top', 'right'): ax.spines[s].set_visible(False)
ax.legend(loc='upper right', frameon=False, fontsize=11)
fig.suptitle('What 100 g of weight does, depending on how far forward it sits', fontsize=15, weight='bold', x=0.02, ha='left', y=0.98)
fig.text(0.02, 0.915, 'Version 65 on the agreed base (D9, 1,055 g). The room low in the plate is only at the back and under the boxes.', fontsize=11, color=INK2)
plt.subplots_adjust(left=0.06, right=0.99, top=0.86, bottom=0.11)
plt.savefig('/home/claude/bal/out/ballast_2_lever.png', dpi=100, facecolor=SURF)
print('ok')
