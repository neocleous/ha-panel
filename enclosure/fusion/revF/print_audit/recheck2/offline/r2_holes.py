# recheck2: printed insert holes against their true axes. For each hole: in every layer that cuts it, the free radius round the
#   true axis point at that layer's mid-plane (distance to the nearest extruded line, lines drawn with their width).
#   The smallest free radius over the hole's length is the largest straight pin along the true axis that passes the print.
import sys, json, math, numpy as np
sys.path.insert(0, '/home/claude/r2/offline')
from r2_gq import G
from r2_faces import load
from scipy import ndimage as ndi
def run(job, tag, hole_faces, length_hint):
    g = G(job, tag); F = {f['i']: f for f in load(tag)}; part = g.fmask(exclude=('Support', 'Brim', 'Skirt'))
    Z = np.array(sorted(set(round(float(v), 3) for v in g.S[:, 4]))); out = []
    for fi in hole_faces:
        f = F[fi]; ax = np.array(f['ax']); o = np.array(f['o']); r = f['r']
        # extent of the hole along its axis from the face's vertex box: project the box corners
        bb = f['bb']; corners = np.array([[bb[0], bb[2], bb[4]], [bb[1], bb[3], bb[5]]])
        p = np.array(f['p']); t0 = (p - o) @ ax
        ts = np.linspace(t0 - length_hint, t0 + length_hint, 400)
        Pw = o[None, :] + ts[:, None] * ax[None, :]
        Pb = g.to_bed(Pw)
        zlo, zhi = Pb[:, 2].min(), Pb[:, 2].max()
        rows = []
        for zt in Z[(Z > zlo) & (Z < zhi + 0.2)]:
            zm = zt - 0.1
            k = np.argmin(np.abs(Pb[:, 2] - zm)); c = Pb[k]
            px = 0.01; x0, y0 = c[0] - 3.5, c[1] - 3.5; W = H = 700
            R = g.raster(part, zt, x0, y0, W, H, px)
            if not R.any():
                continue
            dist = ndi.distance_transform_edt(~R) * px
            ci, cj = int((c[0] - x0) / px), int((c[1] - y0) / px)
            free = dist[cj, ci]
            if free > 3.0:          # outside the part at this layer (beyond the hole's ends)
                continue
            rows.append((round(float(zt), 2), round(float(free), 3)))
        fr = [v for _, v in rows]
        out.append({'face': fi, 'r_model': r, 'axis_to_vertical_deg': round(math.degrees(math.acos(abs(g.M[:3, :3] @ ax)[2])), 2),
                    'layers': len(rows), 'free_r_min': min(fr) if fr else None, 'free_r_mean': round(float(np.mean(fr)), 3) if fr else None,
                    'rows': rows})
    return out
res = {}
res['screen'] = run('A_screen', 'screen', [11, 14], 6.0)
res['shell'] = run('A_shell_plain', 'shell', [14, 16, 1479, 1480], 9.0)
for k, v in res.items():
    for h in v:
        print(k, h['face'], 'model r', h['r_model'], 'tilt', h['axis_to_vertical_deg'], 'layers', h['layers'], 'free r min', h['free_r_min'], 'mean', h['free_r_mean'])
        print('   ', h['rows'][:6], '...', h['rows'][-4:])
json.dump(res, open('/home/claude/r2/data/holes_A7.json', 'w'), indent=1)
