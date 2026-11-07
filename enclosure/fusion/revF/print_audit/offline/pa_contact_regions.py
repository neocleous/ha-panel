# HA panel print audit (P4): support-contact regions per print: location clusters (z band 1 mm, 8-connected 0.25 mm grid,
#   in build coordinates) with the touched faces' dominant world normal and the world box. Input work/CF_<gcode>.npz.
import sys, json, numpy as np
from scipy import ndimage as ndi
G = 0.25
res = {}
for gtag in sys.argv[1:]:
    d = np.load('/home/claude/pa/work/CF_%s.npz' % gtag)
    cells, w, nrm = d['cells'], d['world'], d['nrm']
    x0, y0 = cells[:, 1].min() - 2, cells[:, 2].min() - 2
    nx = int((cells[:, 1].max() - x0 + 2) / G) + 2; ny = int((cells[:, 2].max() - y0 + 2) / G) + 2
    zb = np.floor(cells[:, 0]).astype(int)
    regs = []
    for band in np.unique(zb):
        sel_b = np.nonzero(zb == band)[0]
        ii = ((cells[sel_b, 1] - x0) / G).astype(int); jj = ((cells[sel_b, 2] - y0) / G).astype(int)
        m = np.zeros((nx, ny), bool); m[ii, jj] = True
        lab, n = ndi.label(ndi.binary_dilation(m, iterations=4), structure=np.ones((3, 3)))
        L = lab[ii, jj]
        for k in range(1, n + 1):
            s = sel_b[L == k]
            if len(s) < 4:
                continue
            nn = nrm[s].mean(0); nn = nn / (np.linalg.norm(nn) + 1e-9)
            regs.append({'area_mm2': round(len(s) * G * G, 1), 'z_build': [round(float(cells[s, 0].min()), 1), round(float(cells[s, 0].max()), 1)],
                         'normal': [round(float(v), 2) for v in nn],
                         'world_min': [round(float(v), 1) for v in w[s].min(0)], 'world_max': [round(float(v), 1) for v in w[s].max(0)]})
    regs.sort(key=lambda r: -r['area_mm2'])
    res[gtag] = regs
    print('==', gtag, 'contact %.1f mm2 in %d regions' % (len(cells) * G * G, len(regs)))
    for r in regs[:25]:
        print('  %6.1f mm2 n %-20s world x %6.1f..%6.1f y %6.1f..%6.1f z %6.1f..%6.1f' % (r['area_mm2'], r['normal'], r['world_min'][0], r['world_max'][0], r['world_min'][1], r['world_max'][1], r['world_min'][2], r['world_max'][2]))
json.dump(res, open('/home/claude/pa/data/contact_regions.json', 'w'), indent=1)
