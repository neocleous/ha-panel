"""Slice check: read Bambu Studio G-code of an audit slice into extrusion segments in the part's print frame.
(u, v) = G-code (x, y) minus the placement offset written by s1_make_jobs.py; h = layer top height."""
import sys, re, json, numpy as np
from fdm_lib import *
TYPES = ['Outer wall', 'Inner wall', 'Overhang wall', 'Sparse infill', 'Internal solid infill', 'Top surface', 'Bottom surface',
         'Bridge', 'Gap infill', 'Floating vertical shell', 'Support', 'Support interface', 'Brim', 'Skirt', 'Other']
TID = {t: i for i, t in enumerate(TYPES)}
GDIR = '/mnt/user-data/uploads/fdm_audit/slicer/out'

def parse(tag):
    place = json.load(open(os.path.join(DATA, 'slice_place.json')))[tag]
    path = os.path.join(GDIR, 'F_' + tag, 'plate_1.gcode')
    x = y = None; z = 0.0; lh = 0.2; typ = TID['Other']; w = 0.42
    rows = []
    num = re.compile(r'([XYZE])(-?\d*\.?\d+)')
    started = False
    for line in open(path, errors='ignore'):
        if line.startswith(';'):
            if line.startswith('; FEATURE:'):
                typ = TID.get(line[10:].strip(), TID['Other'])
            elif line.startswith('; LINE_WIDTH:'):
                w = float(line[13:])
            elif line.startswith('; Z_HEIGHT:'):
                z = float(line[11:]); started = True
            elif line.startswith('; LAYER_HEIGHT:'):
                lh = float(line[15:])
            continue
        if not (line.startswith('G1 ') or line.startswith('G0 ')):
            continue
        body = line.split(';')[0]
        d = dict((k, float(v)) for k, v in num.findall(body))
        nx = d.get('X', x); ny = d.get('Y', y)
        if started and d.get('E', 0.0) > 0 and x is not None and (nx != x or ny != y):
            rows.append((z, lh, typ, w, x, y, nx, ny))
        x, y = nx, ny
    a = np.array(rows, dtype=np.float32)
    a[:, [4, 6]] -= place['du']; a[:, [5, 7]] -= place['dv']
    np.save(os.path.join(DATA, 'gc_%s.npy' % tag), a)
    return a

def load(tag):
    fn = os.path.join(DATA, 'gc_%s.npy' % tag)
    return np.load(fn) if os.path.exists(fn) else parse(tag)

def region(tag, ubox, vbox, hbox):
    """Extruded volume by line type inside a box of the print frame (segments counted by their midpoint)."""
    a = load(tag)
    mu = (a[:, 4] + a[:, 6]) / 2; mv = (a[:, 5] + a[:, 7]) / 2
    s = (mu >= ubox[0]) & (mu <= ubox[1]) & (mv >= vbox[0]) & (mv <= vbox[1]) & (a[:, 0] > hbox[0] + 1e-3) & (a[:, 0] <= hbox[1] + 1e-3)
    b = a[s]
    ln = np.hypot(b[:, 6] - b[:, 4], b[:, 7] - b[:, 5])
    vol = ln * b[:, 3] * b[:, 1]
    out = {}
    for i, t in enumerate(TYPES):
        m = b[:, 2] == i
        if m.any():
            out[t] = float(vol[m].sum())
    return out

def draw_layer(tag, h, win, out, title=''):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    a = load(tag)
    zs = np.unique(a[:, 0]); z = zs[np.argmin(np.abs(zs - h))]
    b = a[a[:, 0] == z]
    u0, u1, v0, v1 = win
    col = {0: '#d95f02', 1: '#e6ab02', 2: '#a6761d', 3: '#bbbbbb', 4: '#1b9e77', 5: '#7570b3', 6: '#7570b3', 7: '#66a61e', 8: '#e7298a', 9: '#1f78b4'}
    fig, ax = plt.subplots(figsize=(7, 7 * (v1 - v0) / (u1 - u0) + 0.6), dpi=110)
    ppm = 7 * 110 / (u1 - u0) / 110 * 72      # points per mm
    for t in np.unique(b[:, 2]).astype(int):
        s = b[b[:, 2] == t]
        segs = np.stack([s[:, 4:6], s[:, 6:8]], axis=1)
        lc = LineCollection(segs, colors=col.get(t, '#000000'), linewidths=float(np.median(s[:, 3])) * ppm * 0.92, capstyle='round', label=TYPES[t], alpha=0.9)
        ax.add_collection(lc)
    ax.set_xlim(u0, u1); ax.set_ylim(v0, v1); ax.set_aspect('equal'); ax.grid(True, linewidth=0.3, alpha=0.5)
    ax.legend(fontsize=7, loc='upper right'); ax.set_title(title or '%s as sliced, layer top at %.2f' % (tag, z), fontsize=9)
    ax.set_xlabel('print u (mm)'); ax.set_ylabel('print v (mm)')
    fig.tight_layout(); fig.savefig(out); plt.close(fig)

if __name__ == '__main__':
    for t in sys.argv[1:]:
        a = parse(t)
        ln = np.hypot(a[:, 6] - a[:, 4], a[:, 7] - a[:, 5]); vol = ln * a[:, 3] * a[:, 1]
        print(t, 'segments', len(a), 'layers', len(np.unique(a[:, 0])), 'extruded %.0f mm3' % vol.sum(),
              ' | '.join('%s %.0f' % (TYPES[i], vol[a[:, 2] == i].sum()) for i in range(len(TYPES)) if (a[:, 2] == i).any()))
