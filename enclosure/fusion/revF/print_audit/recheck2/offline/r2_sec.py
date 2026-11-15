# Section of a world-mm mesh by a plane 'up = u0' (slab frame: up along the screen), returned in (x, d) coordinates.
import numpy as np, trimesh, math, sys
C12, S12 = math.cos(math.radians(12)), math.sin(math.radians(12)); H = 143.3
def sec_up(mw, u0):
    n = np.array([0.0, -S12, C12])                 # world direction of 'up'
    o = n * u0 + np.array([0.0, 0.0, H]) * 0    # plane: -y*S + (z-H)*C = u0  ->  n.(p - (0,0,H)) = u0
    o = np.array([0.0, 0.0, H]) + n * u0
    s = trimesh.intersections.mesh_plane(mw, n, o)
    # (x, d) of segment ends
    def xd(p): return np.c_[p[..., 0], -(p[..., 1] * C12 + (p[..., 2] - H) * S12)]
    return xd(s[:, 0, :]), xd(s[:, 1, :])
