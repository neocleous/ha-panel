"""Turn body meshes read from the model (version 91, read-only) into 2D outlines for the unit view.

Input: a JSON of meshes {body: {"xyz": [mm...], "idx": [...]}} read from Fusion.
Output: data/positions.json — for each body, its silhouette from the back (x right, z up) and from above
(x right, y toward the back), as simplified polygons in model millimetres.
"""
import json
import sys

from shapely.geometry import Polygon, mapping
from shapely.ops import unary_union


def silhouette(xyz, idx, a, b):
    tris = []
    for i in range(0, len(idx), 3):
        p = [(xyz[3 * j + a], xyz[3 * j + b]) for j in idx[i:i + 3]]
        t = Polygon(p)
        if t.area > 1e-4:
            tris.append(t.buffer(0.05))
    u = unary_union(tris).buffer(-0.05).simplify(0.15)
    polys = [u] if u.geom_type == "Polygon" else list(getattr(u, "geoms", []))
    return [[list(map(lambda c: [round(c[0], 2), round(c[1], 2)], p.exterior.coords))] +
            [[[round(x, 2), round(y, 2)] for x, y in r.coords] for r in p.interiors] for p in polys if p.area > 0.05]


def main(src, dst):
    meshes = json.load(open(src))
    out = {"source": "HA Panel v5 - tapered, version 91 (read-only); bodies' meshes, low quality", "bodies": {}}
    for name, m in meshes.items():
        xyz, idx = m["xyz"], m["idx"]
        xs, ys, zs = xyz[0::3], xyz[1::3], xyz[2::3]
        out["bodies"][name] = {
            "bbox": [min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)],
            "back": silhouette(xyz, idx, 0, 2),
            "plan": silhouette(xyz, idx, 0, 1),
        }
    json.dump(out, open(dst, "w"), separators=(",", ":"))
    print("bodies", len(out["bodies"]))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
