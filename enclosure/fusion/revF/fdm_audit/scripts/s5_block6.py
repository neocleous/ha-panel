"""Block 6: the checks made on the last seven audit slices (boxes, cap, carrier, screen plate, bezel, grommet).
1 as-sliced volume and line types of all thirteen slices; 2 posts and bosses with inserts: section and torsion shear
between layers, as sliced, by height; 3 the boxes' touch-clip block and floor boss, layer by layer; 4 the grommet's
0.80 walls as lines; 5 regions that start in mid-air (the slicer's "floating regions").
Areas count each line as width x layer height, so plastic that is solid reads 100 to 113 %."""
import numpy as np
from fdm_lib import *
from s2_gcode import load, TYPES, TID
import s4_section as s4
import a7_holes

T = 500.0   # N.mm, the enclosure chat's 0.5 N.m
GUARD_VOL = {'shell': 107864.325, 'plate': 66463.676, 'boxL': 26321.751, 'boxR': 27043.249, 'base': 32621.881, 'carrier': 13651.988,
             'cradle': 1771.219, 'door': 47573.052, 'cap': 9980.253, 'clipL': 571.162, 'bezel': 62932.407, 'grommet': 506.176, 'hood': 802.884}


def volumes():
    print('%-8s %9s %9s %6s | walls solid sparse gap bridge' % ('slice', 'model', 'sliced', '%'))
    for tag, vm in GUARD_VOL.items():
        a = load(tag); ln = np.hypot(a[:, 6] - a[:, 4], a[:, 7] - a[:, 5]); v = ln * a[:, 3] * a[:, 1]
        s = lambda *names: sum(v[a[:, 2] == TID[n]].sum() for n in names)
        tot = v.sum()
        w = s('Outer wall', 'Inner wall', 'Overhang wall'); so = s('Internal solid infill', 'Top surface', 'Bottom surface', 'Floating vertical shell')
        print('%-8s %9.0f %9.0f %5.1f%% | %4.0f%% %4.0f%% %4.0f%% %4.0f%% %4.0f%%' % (
            tag, vm, tot, 100 * tot / vm, 100 * w / tot, 100 * so / tot, 100 * s('Sparse infill') / tot, 100 * s('Gap infill') / tot, 100 * s('Bridge') / tot))


def mix_of(s, n=4):
    return ', '.join('%s %.0f%%' % (k[:14], 100 * v / s['A']) for k, v in sorted(s['mix'].items(), key=lambda kv: -kv[1])[:n]) if s['A'] else ''


def torsion(tag, body, c, hs, R=6.5):
    """Section round an upright hole axis at (u, v): area and polar second moment as modelled and as sliced; shear between layers T r / J."""
    p = Part(body); L = p.slice(); H = np.array([x[0] for x in L]); win = (c[0] - R, c[0] + R, c[1] - R, c[1] + R)
    for h in hs:
        i = int(np.argmin(np.abs(H - (h - p.lh / 2))))
        g = L[i][1].intersection(box(win[0], win[2], win[1], win[3]))
        best = None
        for q in polys_of(g):
            d = q.distance(Point(c))
            if best is None or d < best[0]: best = (d, q)
        if best is None: continue
        q = best[1]; ext = np.array(q.exterior.coords); ro = np.hypot(ext[:, 0] - c[0], ext[:, 1] - c[1]); r = float(np.median(ro))
        s = s4.sliced_props(tag, h, win); m = s4.solid_props(p, h, win); Js = s['I1'] + s['I2']; Jm = m['I1'] + m['I2']
        print('  h %5.2f | r %.2f-%.2f | model A %6.1f J %7.1f | sliced A %6.1f (%3.0f%%) J %7.1f (%3.0f%%) | shear full %.1f half %.1f MPa (solid %.1f) | %s' % (
            s['z'], ro.min(), ro.max(), m['A'], Jm, s['A'], 100 * s['A'] / m['A'], Js, 100 * Js / Jm, T * r / Js, T / 2 * r / Js, T * r / Jm, mix_of(s, 3)))


def layers_through(tag, body, win, h0, h1):
    p = Part(body)
    for h in np.arange(h0, h1 + 1e-6, 0.2):
        s = s4.sliced_props(tag, h, win); m = s4.solid_props(p, h, win)
        print('  layer top %.1f | model A %5.1f | sliced A %5.1f (%3.0f%%) | %s' % (s['z'], m['A'], s['A'], 100 * s['A'] / m['A'] if m['A'] else 0, mix_of(s)))


def grommet_lines():
    a = load('grommet'); zs = np.unique(a[:, 0])
    for h in (8.6, 17.84):
        z = zs[np.argmin(np.abs(zs - h))]; b = a[a[:, 0] == z]
        dv = np.abs(b[:, 7] - b[:, 5]); du = np.abs(b[:, 6] - b[:, 4]); s = b[(dv > 1.0) & (du < 0.05)]
        for r in s[np.argsort(s[:, 4])]:
            print('  layer top %.2f  %-10s width %.2f at u %.3f, v %.2f..%.2f' % (z, TYPES[int(r[2])], r[3], r[4], min(r[5], r[7]), max(r[5], r[7])))


def islands(body, amin=0.3):
    p = Part(body); prev = None; out = []
    for h, g in p.slice():
        if prev is not None:
            for q in polys_of(g):
                if q.area >= amin and not q.intersects(prev):
                    c = q.representative_point(); w = p.uvh_to_world([[c.x, c.y, h]])[0]
                    out.append((round(h - p.lh / 2, 2), round(q.area, 1), [round(float(x), 1) for x in w]))
        prev = g
    return out


if __name__ == '__main__':
    print('1 as-sliced volume by line type'); volumes()
    print('2 carrier post (-31.05, -52.70)'); torsion('carrier', 'RESP_CARRIER', (-31.05, -52.70), [2.2, 3.0, 5.0, 8.0, 9.0, 9.4, 12.0, 15.0])
    print('2 carrier post (-37.05, -5.45)'); torsion('carrier', 'RESP_CARRIER', (-37.05, -5.45), [2.2, 3.0, 5.0, 7.0, 9.0, 9.4, 12.0])
    c = [o for o in a7_holes.holes('HOUSING_F_cap') if abs(o[3] - 4.0) < 0.1][0]
    print('2 cap boss (%.2f, %.2f)' % (c[1], c[2])); torsion('cap', 'HOUSING_F_cap', (c[1], c[2]), [2.5, 3.0, 4.0, 6.0, 7.2], R=5.2)
    print('3 left box, touch-clip block round the pilot (pilot h 43.8 to 46.3)'); layers_through('boxL', 'SPKBOX_L', (40.5, 48.4, 100.5, 110.5), 41.8, 48.4)
    print('3 right box, the same'); layers_through('boxR', 'SPKBOX_R', (-53.5, -45.6, 100.5, 110.5), 41.8, 48.4)
    print('3 left box, floor boss (64, -45), hole lying in the layers'); layers_through('boxL', 'SPKBOX_L', (57.3, 65.6, 132.0, 139.7), 3.2, 11.0)
    print('4 grommet, upright lines of the 0.80 walls'); grommet_lines()
    print('5 regions that start in mid-air (layer bottom h, area, world place)')
    for b in ('HOUSING_F_front', 'HOUSING_F_plate', 'HOUSING_F_door', 'HOUSING_F_cap', 'FLOOR_PLATE', 'SPKBOX_L', 'SPKBOX_R', 'RESP_CARRIER',
              'CRADLE_5807', 'TOUCH_CLIP_L', 'GROMMET_usbc_F', 'BME_HOOD', 'SLAB_frame'):
        print(' ', b, islands(b))
