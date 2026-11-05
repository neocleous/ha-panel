#!/usr/bin/env python3
"""HA panel model audit (2026-11-05), G.4: sharp concave edges (from v5f_a1a_validity.py, data/a1a.json) at load-path
features. An edge counts for a feature when its midpoint lies inside the feature's world box (x_rel, y, z ranges).
Output per feature: edges, total length (mm), angle between the face normals (90 = square corner)."""
import json, os
ROOT = os.path.expanduser('~/mnt/audit') if os.path.isdir(os.path.expanduser('~/mnt/audit')) else os.path.expanduser('~/Documents/audit')
rows = {r['step']: r['data'] for r in json.load(open(os.path.join(ROOT, 'data', 'a1a.json'))) if r['step'] not in ('FAIL',)}


def box(cx, cy, r, z0, z1):
    return (cx - r, cx + r, cy - r, cy + r, z0, z1)


F = {
    'HOUSING_F_cap': {'cap bosses BL/BR/SL/SR (Ø8, z 172.5-177.5)': [box(sx * x, y, 4.6, 172.3, 177.6) for sx in (1, -1) for (x, y) in ((25.91, -37.80), (43.36, -32.85))],
                      'mic heat-stake pins Ø1.8 (z 174.8-178.3)': [box(sx * x, -26.5, 1.3, 174.6, 178.4) for sx in (1, -1) for x in (11.5, 30.0)]},
    'HOUSING_F_front': {'cap pads + ribs (z 158-172.6, r 8 round the axes)': [box(sx * x, y, 8.0, 158.0, 172.6) for sx in (1, -1) for (x, y) in ((25.91, -37.80), (43.36, -32.85))],
                        'Pi floor bosses Ø7.6 (z 2.5-8.0)': [box(x, y, 4.3, 2.3, 8.1) for x in (18.35, -39.65) for y in (-5.5, -54.5)],
                        'cradle floor bosses Ø8 (z 2.5-8.0)': [box(x, -72.5, 4.5, 2.3, 8.1) for x in (6.5, -1.5)],
                        'bracket-tab floor bosses Ø8 (z 2.5-8.0)': [box(x, -58.0, 4.5, 2.3, 8.1) for x in (49.5, -49.5)],
                        'zip-tie anchors (±58.5, -56.5)': [box(x, -56.5, 4.0, 2.3, 8.2) for x in (58.5, -58.5)],
                        'lip root band (y -55.0…-53.5, z >= 6.5)': [(-100, 100, -55.2, -53.3, 6.4, 172.0)],
                        'lip end (y -63.5)': [(-100, 100, -63.7, -63.3, 6.4, 172.0)],
                        'ledge / flange / spline groove (z 170-175.4)': [(-100, 100, -60, -22.4, 170.0, 175.4)],
                        'baffle stop pads / pilots (y -0.1…1.0)': [box(sx * x, 0.4, 4.2, z - 4.2, z + 4.2) for sx in (1, -1) for x in (52.75, 88.25) for z in (10.25, 45.75)]},
    'HOUSING_F_door': {'door bosses Ø8 (z 2.8-10.5)': [box(x, y, 4.6, 2.7, 10.6) for (x, y) in ((19, -74.5), (-19, -77.0), (50, -67.0), (-50, -67.0))],
                       'inlet cutout (x ±12.2, z 13.3-27.9)': [(-14.8, 14.8, -86, -80, 12.5, 28.7)]},
    'MAIN_BRACKET': {'M2.5 bosses (±41.5, z 37.5 / 80.5)': [box(sx * 41.5, -60.55, 4.6, z - 4.6, z + 4.6) for sx in (1, -1) for z in (37.5, 80.5)],
                     'tabs on the floor bosses (±49.5, -58.0)': [box(sx * 49.5, -58.0, 5.0, 6.0, 14.0) for sx in (1, -1)]},
    'CRADLE_5807': {'legs Ø8 (z 8.0-14.6)': [box(x, -72.5, 4.6, 7.9, 17.6) for x in (6.5, -1.5)],
                    '5807 posts Ø6 (M2)': [box(x, -81.16, 3.6, 15.0, 21.0) for x in (7.75, -7.49)]},
    'GROMMET_usbc_F': {'heat-stake pins Ø1.8': [(sx * 13.6 - 1.6, sx * 13.6 + 1.6, -86.5, -79.0, 19.0, 22.2) for sx in (1, -1)]},
    'RESP_CARRIER': {'M2 bosses Ø6': [(22.6 - 3.6, 22.6 + 3.6, -13.5, -8.0, 95.0, 102.5), (-35.11 - 3.6, -35.11 + 3.6, -19.5, -14.0, 123.3, 130.8)]},
    'SPKBOX_L': {'screw tubes Ø8 / pegs': [(48.0, 57.5, -52.0, -3.0, 5.5, 15.0), (48.0, 57.5, -52.0, -3.0, 41.0, 50.5), (86.0, 90.5, -4.0, 0.0, 8.0, 12.5), (86.0, 90.5, -4.0, 0.0, 43.5, 48.0)]},
    'SPKBOX_R': {'screw tubes Ø8 / pegs': [(-57.5, -48.0, -52.0, -3.0, 5.5, 15.0), (-57.5, -48.0, -52.0, -3.0, 41.0, 50.5), (-90.5, -86.0, -4.0, 0.0, 8.0, 12.5), (-90.5, -86.0, -4.0, 0.0, 43.5, 48.0)]},
}
res = {}
for part, feats in F.items():
    ce = rows.get(part, {}).get('concave_edges', [])
    for fname, boxes in feats.items():
        hit = [e for e in ce if any(b[0] <= e[2][0] <= b[1] and b[2] <= e[2][1] <= b[3] and b[4] <= e[2][2] <= b[5] for b in boxes)]
        L = sum(e[0] for e in hit)
        ang = sorted(e[1] for e in hit)
        res['%s | %s' % (part, fname)] = {'edges': len(hit), 'len_mm': round(L, 1),
                                          'angles': [ang[0], ang[-1]] if ang else None,
                                          'longest': sorted(hit, key=lambda e: -e[0])[:3]}
for k, v in res.items():
    print(k, json.dumps(v))
