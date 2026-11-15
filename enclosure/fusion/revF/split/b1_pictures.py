# Block 1 pictures for the three questions (2D, from the read-only sections in data/sec_b1.json and data/sec_front.json).
# World mm: x = x_rel (+x = viewer's left), y + toward the screen, z up; d = depth behind the glass plane.
import json, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MP, FancyArrowPatch
from shapely.geometry import Polygon, box, LineString
from shapely.ops import unary_union
from shapely import affinity

C, S, H = math.cos(math.radians(12)), math.sin(math.radians(12)), 143.3
D = json.load(open('data/sec_b1.json'))
F = json.load(open('data/sec_front.json'))['res']

COL = dict(plate='#3f5fd6', rest='#a3a8ae', tab='#f0c43a', screw='#d23c3c', insert='#3a3a3a', slab='#2a2a2a',
           glass='#9fd0e6', panel='#5a5a5a', box='#d9d9d9', new='#7d8790', mod='#e08a3c')


def y_at(dd, z):                      # y on the depth plane dd at height z
    return -(dd + (z - H) * S) / C


def poly(pts):
    p = Polygon(pts)
    return p if p.is_valid else p.buffer(0)


def draw(ax, g, fc, ec='black', lw=0.6, hatch=None, alpha=1.0, z=2, T=None, ls='-'):
    if g is None or g.is_empty:
        return
    gs = getattr(g, 'geoms', [g])
    for q in gs:
        if q.geom_type != 'Polygon' or q.area < 1e-4:
            continue
        xy = [T(*p) for p in q.exterior.coords]
        ax.add_patch(MP(xy, closed=True, fc=fc, ec=ec, lw=lw, hatch=hatch, alpha=alpha, zorder=z, ls=ls))
        for r in q.interiors:
            ax.add_patch(MP([T(*p) for p in r.coords], closed=True, fc='white', ec=ec, lw=lw, zorder=z + 0.01))


def bar_along(p0, u, s0, s1, w):      # rectangle along direction u from s0 to s1, width w
    nx, ny = u[1], -u[0]
    a = (p0[0] + u[0] * s0, p0[1] + u[1] * s0); b = (p0[0] + u[0] * s1, p0[1] + u[1] * s1)
    h = w / 2.0
    return Polygon([(a[0] + nx * h, a[1] + ny * h), (b[0] + nx * h, b[1] + ny * h), (b[0] - nx * h, b[1] - ny * h), (a[0] - nx * h, a[1] - ny * h)])


def s_at_y(p0, u, y):                 # parameter along u where the line reaches y
    return (y - p0[1]) / u[1]


# ---------------------------------------------------------------- picture 1: box-top screws, top view at z 80
def pic1():
    z = 80.0
    yB = y_at(12.8, z); yF = y_at(9.0, z); yG = y_at(13.1, z)        # plate back, plate front, 0.3 behind the plate
    Tv = lambda x, y: (-x, -y)                                          # seen from above, screen at the bottom, viewer's left on the left
    fig, axs = plt.subplots(2, 1, figsize=(10.5, 11.5))
    out = {}
    for row, (side, ax) in enumerate((('L', axs[0]), ('R', axs[1]))):
        g = 1.0 if side == 'L' else -1.0
        shell = poly(D['z80']['shell_' + side])
        slab = poly(D['z80']['slab_' + side]); glass = poly(D['z80']['glass']); panel = poly(D['z80']['panel'])
        tab0 = unary_union([poly(p) for p in D['z80']['tab_' + side]]).convex_hull
        hole = D['holes']['boxtop_' + side]
        u = (g * 0.17365, 0.98481)
        dmid = (hole['d'][0] + hole['d'][1]) / 2.0
        p0 = (hole['x_mid'], -dmid * C - hole['up'] * S)
        notch = Polygon([(g * 60.03, -3.9), (g * 61.09, 2.36), (g * 57.19, 3.05), (g * 56.01, -3.9)])
        inner = 93.45
        side_wall = shell.intersection(box(-200, -60, 200, yB)).difference(box(-inner, -6.0, inner, 10.0))
        removed = shell.intersection(box(-200, -60, 200, yB)).intersection(box(-inner, -6.0, inner, 10.0))
        X = (40.0, 106.0) if side == 'L' else (-106.0, -40.0)
        clip = box(X[0], -60, X[1], 20)
        draw(ax, glass.intersection(clip), COL['glass'], T=Tv, z=1)
        draw(ax, panel.intersection(clip), COL['panel'], T=Tv, z=1)
        draw(ax, slab, COL['slab'], T=Tv, z=1)
        draw(ax, side_wall.intersection(clip), COL['rest'], T=Tv)
        draw(ax, removed.intersection(clip), 'none', ec='#777777', lw=0.7, hatch='////', T=Tv, z=1.5, ls='--')
        if side == 'L':                                                 # option a on the left box
            plate = shell.intersection(box(-200, yB, 200, 20)).union(notch.intersection(box(-200, yB, 200, 20)))
            sF = s_at_y(p0, u, yF); sI = sF - 5.7                         # insert flush with the plate's front face, 5.7 long
            insert = bar_along(p0, u, sI, sF, 4.0)
            dy = yG - (-3.9)                                              # tab forward until 0.3 behind the plate
            tab = affinity.translate(tab0, 0.0, dy)
            tab = tab.difference(bar_along(p0, u, sI - 0.3, sF, 4.6)).difference(bar_along(p0, u, sI - 20, sF, 3.6))
            back = affinity.translate(tab0, 0.0, dy)
            sBack = min(s_at_y(p0, u, y) for (x, y) in back.exterior.coords if abs(x - p0[0] - u[0] * s_at_y(p0, u, y)) < 3.0)
            draw(ax, plate.intersection(clip), COL['plate'], T=Tv, z=2.5)
            draw(ax, tab, COL['tab'], T=Tv, z=3)
            draw(ax, insert, COL['insert'], T=Tv, z=3.5)
            sc = bar_along(p0, u, sBack, sF - 0.4, 3.0).union(bar_along(p0, u, sBack - 1.65, sBack, 5.7))
            draw(ax, sc, COL['screw'], T=Tv, z=4)
            out['a_tab_forward'] = round(dy, 2); out['a_insert_proud'] = round((s_at_y(p0, u, yB) - sI), 2)
            ax.set_title('a. Box-top screws into the screen plate (left box shown; the right is its mirror)', fontsize=11, loc='left')
            notes = [((-55.0, 2.0), 'box tab,\nabout %.0f forward' % dy, (-52.5, 8.5)),
                     ((-57.6, 0.6), 'insert set flush with the plate\'s front,\n%.2f standing out behind it' % out['a_insert_proud'], (-88.0, 4.2)),
                     ((-80.0, -2.3), 'screen plate (thin plate, 3.8)', (-91.0, -7.0)),
                     ((-94.8, 8.0), 'rest of the shell (side wall)', (-104.5, 13.8)),
                     ((-58.5, 5.6), 'screw from behind: 2.0 key through\nthe door opening, path unchanged', (-80.0, 11.0))]
        else:                                                           # option b on the right box
            plate = shell.intersection(box(-200, yB, 200, 20)).union(notch.intersection(box(-200, yB, 200, 20)))
            yBoxF = -3.7                                                  # right box's front face at z 80
            sFront = s_at_y(p0, u, yG); sBk = sFront - 6.45               # boss from 0.3 behind the plate, hole 6.35 + floor
            boss = bar_along(p0, u, sBk, sFront, 8.0)
            web = box(-inner, yBoxF + 0.3, p0[0] - g * 2.0, yG)
            newpart = boss.union(web)
            insert = bar_along(p0, u, sBk, sBk + 5.7, 4.0)
            dy = (p0[1] + u[1] * sBk) - (-3.9) - 0.3                         # tab back until 0.3 behind the boss
            tab = affinity.translate(tab0, 0.0, dy).difference(bar_along(p0, u, sBk - 20, sBk, 3.6))
            back = affinity.translate(tab0, 0.0, dy)
            sBack = min(s_at_y(p0, u, y) for (x, y) in back.exterior.coords if abs(x - p0[0] - u[0] * s_at_y(p0, u, y)) < 3.0)
            boxo = poly(D['z80']['boxR_outer'] + [[-58.07, -60.0], [-75.17, -60.0]])
            draw(ax, boxo.intersection(clip).intersection(box(-200, -14.5, 200, 20)), COL['box'], ec='#999999', T=Tv, z=1.2)
            draw(ax, plate.intersection(clip), COL['plate'], T=Tv, z=2.5)
            draw(ax, newpart.intersection(clip), COL['new'], hatch='xx', T=Tv, z=2.6)
            draw(ax, tab, COL['tab'], T=Tv, z=3)
            draw(ax, insert, COL['insert'], T=Tv, z=3.5)
            sc = bar_along(p0, u, sBack, sBk + 5.3, 3.0).union(bar_along(p0, u, sBack - 1.65, sBack, 5.7))
            draw(ax, sc, COL['screw'], T=Tv, z=4)
            out['b_tab_back'] = round(-dy, 2); out['b_web_depth'] = round(yG - (yBoxF + 0.3), 2)
            out['b_web_len'] = round(inner - abs(p0[0]) - 2.0, 1)
            ax.set_title('b. Bosses stay on the rest of the shell (right box shown: the tight side)', fontsize=11, loc='left')
            notes = [((80.0, 1.7), 'new web from the side wall:\n%.1f deep, %.0f long, between\nthe plate and the right box' % (out['b_web_depth'], out['b_web_len']), (67.0, 9.0)),
                     ((54.6, 2.4), 'new boss, insert at its back', (40.6, 0.6)),
                     ((55.3, 6.4), 'box tab, about %.0f back' % out['b_tab_back'], (40.6, 13.2)),
                     ((80.0, -2.3), 'screen plate (thin plate, 3.8)', (66.0, -7.2))]
            ax.text(90.5, 14.0, 'right box', fontsize=8.5, ha='right', color='#555555')
        for (xy, t, xyt) in notes:
            ax.annotate(t, xy=xy, xytext=xyt, fontsize=8.5, arrowprops=dict(arrowstyle='-', lw=0.6, color='#333333'), zorder=6)
        ax.set_xlim(-X[1], -X[0]); ax.set_ylim(-16.5, 16.0); ax.set_aspect('equal')
        ax.set_xticks([]); ax.set_yticks([])
        ax.plot([-X[1] + 2, -X[1] + 12], [-15.2, -15.2], color='black', lw=2); ax.text(-X[1] + 13, -15.6, '10 mm', fontsize=8)
        ax.text(-X[0] - 1.0, -15.6, 'screen side', ha='right', fontsize=8, color='#555555')
    fig.text(0.01, 0.006, 'Top view cut at the box-top screws (z 80), screen at the bottom. Blue: screen plate (the thin plate of question 2a). Grey: rest of the shell.\n'
             'Hatched outline: the screen wall and old bosses that go. Yellow: box tab. Red: screw. Dark: insert. Light grey: right box.', fontsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig('img/q1_box_top_screws.png', dpi=150)
    return out


# ---------------------------------------------------------------- picture 2: thin or full plate, the screen's edge at z 127.5
def pic2():
    z = 127.513
    yF, yB, yW, yS = y_at(9.0, z), y_at(12.8, z), y_at(14.8, z), y_at(12.0, z)
    Tv = lambda x, y: (-x, -y)
    shell = poly(D['z127']['shell']); slab = poly(D['z127']['slab']); glass = poly(D['z127']['glass']); panel = poly(D['z127']['panel'])
    flange = box(80.0, yW - 0.01, 89.36, yB + 0.01)
    fig, axs = plt.subplots(1, 2, figsize=(11.5, 6.4))
    out = {}
    for ax, opt in zip(axs, ('a', 'b')):
        draw(ax, glass, COL['glass'], T=Tv, z=1); draw(ax, panel, COL['panel'], T=Tv, z=1); draw(ax, slab, COL['slab'], T=Tv, z=1)
        if opt == 'a':
            plate = shell.intersection(box(0, yB, 200, 10))
            rest = shell.intersection(box(0, -60, 200, yB)).difference(flange)
            gone = shell.intersection(flange)
            vis = (yS, yB)
            title = 'a. Thin plate: the slab\'s seat alone (3.8)'
        else:
            plate = shell.intersection(box(0, yW, 200, 10)).union(box(89.36, yW, 98.7, yB))
            cut = y_at(14.8 + 0.3, z)
            rest = shell.intersection(box(0, -60, 200, cut))
            gone = shell.intersection(box(0, cut, 200, yW)).difference(flange)
            vis = (yS, yW)
            title = 'b. Full plate: the whole screen wall (5.8)'
        plate = plate.buffer(0.1, join_style=2).buffer(-0.1, join_style=2)
        draw(ax, rest, COL['rest'], T=Tv); draw(ax, plate, COL['plate'], T=Tv, z=2.5)
        draw(ax, gone, 'none', ec='#777777', hatch='////', T=Tv, z=1.5, ls='--')
        w = vis[0] - vis[1]; out[opt] = round(w / 1.0, 2)
        xv = -100.6
        ax.annotate('', xy=(xv, -vis[0]), xytext=(xv, -vis[1]), arrowprops=dict(arrowstyle='<->', lw=1.0, color='#c0392b'))
        ax.annotate('plate edge seen from the side\nbetween slab frame and side wall: %.1f' % w, xy=(xv, -(vis[0] + vis[1]) / 2.0), xytext=(-105.5, 15.5),
                    fontsize=8.5, color='#c0392b', arrowprops=dict(arrowstyle='-', lw=0.6, color='#c0392b'))
        ax.set_title(title, fontsize=11, loc='left')
        ax.set_xlim(-106.0, -78.0); ax.set_ylim(-4.5, 24.0); ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([])
        ax.plot([-105.0, -100.0], [22.5, 22.5], color='black', lw=2); ax.text(-102.5, 23.0, '5 mm', ha='center', fontsize=8)
        ax.text(-80.0, 23.0, 'cloth-covered side wall', fontsize=8, ha='right', color='#555555')
        ax.text(-80.0, -3.8, 'slab (glass and frame)', fontsize=8, ha='right', color='#555555')
    fig.text(0.01, 0.01, 'The screen\'s left edge from above, cut 15.8 below the screen\'s middle (z 127.5), screen at the bottom. Blue: screen plate. '
             'Grey: rest of the shell. Hatched: what goes.', fontsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig('img/q2_plate_edge.png', dpi=150)
    return out


# ---------------------------------------------------------------- picture 3: order of assembly, middle section (x 0)
def pic3():
    Tv = lambda y, z: (y, z)                                            # seen from the left side: screen on the right
    pl = D['plate_pic']
    def rect_du(d0, d1, u0, u1):
        return Polygon([(-d * C - u * S, H - d * S + u * C) for d, u in ((d0, u0), (d1, u0), (d1, u1), (d0, u1))])
    shells = [poly(l) for l in F['x0']['HOUSING_F_front']]
    shell = unary_union([s for s in shells if s.area > 1.0])
    zone = rect_du(-10.0, 14.8, pl['up'][0], pl['up'][1])
    plate = shell.intersection(rect_du(-10.0, 12.8, pl['up'][0], pl['up'][1]))
    rest = shell.difference(zone)
    mod = [poly(D['x0'][k]) for k in ('slab_top', 'slab_bot', 'glass', 'panel', 'lcd_pcb', 'carrier', 'main_pcb')]
    module = unary_union(mod)
    cap = unary_union([poly(D['x0']['cap_a']), poly(D['x0']['cap_b'])])
    touch = poly(D['x0']['touch_pcb'])
    n = (C, S); off = 48.0
    fig, axs = plt.subplots(1, 2, figsize=(11.5, 9.0))
    for ax, opt in zip(axs, ('a', 'b')):
        draw(ax, rest, COL['rest'], T=Tv); draw(ax, touch, '#7aa86b', T=Tv); draw(ax, cap, '#b9b9b9', T=Tv)
        if opt == 'a':
            draw(ax, plate, COL['plate'], T=Tv, z=2.5)
            draw(ax, affinity.translate(module, n[0] * off, n[1] * off), COL['mod'], T=Tv, z=3)
            draw(ax, module, 'none', ec='#999999', T=Tv, z=1.4, ls='--')
            title = 'a. Plate on the shell first; the display module rides in as now'
            txt = ('1  screen plate onto the shell: 4 screws from the front, 2.0 key\n'
                   '2  plate unit in, box-top screws into the plate\n'
                   '3  display module rides in through the LCD opening;\n'
                   '    4 display screws from behind through the door opening (2.5 key)')
        else:
            draw(ax, affinity.translate(plate, n[0] * off, n[1] * off), COL['plate'], T=Tv, z=2.5)
            draw(ax, affinity.translate(module, n[0] * off, n[1] * off), COL['mod'], T=Tv, z=3)
            draw(ax, plate.union(module), 'none', ec='#999999', T=Tv, z=1.4, ls='--')
            title = 'b. Display module onto the plate on the bench; both go in together'
            txt = ('1  bench: display module onto the plate, 4 display screws\n'
                   '2  plate unit in\n'
                   '3  screen sub-assembly in from the front;\n'
                   '    2 screws from behind at the top, box-top screws at the bottom')
        x0a, z0a = 84.0, 112.0
        ax.add_patch(FancyArrowPatch((x0a, z0a), (x0a - n[0] * 26, z0a - n[1] * 26), arrowstyle='-|>', mutation_scale=18, lw=1.8, color='black', zorder=6))
        ax.set_title(title, fontsize=10.5, loc='left')
        ax.text(0.0, -0.015, txt, fontsize=8.5, va='top', family='monospace', transform=ax.transAxes)
        ax.set_xlim(-80.0, 88.0); ax.set_ylim(0.0, 192.0); ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([])
        ax.text(72.0, 4.0, 'screen side', ha='right', fontsize=8, color='#555555')
    fig.text(0.01, 0.008, 'Middle section (x 0) seen from the viewer\'s left, screen on the right. Blue: screen plate. Orange: display module (slab, display, carrier, main board),\n'
             'drawn %.0f out along the screen\'s normal; dashed: where it ends up. Grey: rest of the shell (top band, top of the back, chin). Green: touch board.' % off, fontsize=8)
    fig.tight_layout(rect=(0, 0.11, 1, 1))
    fig.savefig('img/q3_order.png', dpi=150)


if __name__ == '__main__':
    print('pic1', pic1())
    print('pic2', pic2())
    pic3(); print('pic3 done')
