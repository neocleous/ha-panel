# recheck2 block 1: helpers over the face dumps (data/r2_2_faces_<tag>.json from Fusion).
import json, math, numpy as np
C12, S12 = math.cos(math.radians(12)), math.sin(math.radians(12))
H = 143.3
def load(tag): return json.load(open('/mnt/user-data/uploads/print_audit_recheck2/data/r2_2_faces_%s.json' % tag))
def ang(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    return math.degrees(math.acos(max(-1, min(1, abs(a @ b) / np.linalg.norm(a) / np.linalg.norm(b)))))
def d_of(p): return -(p[1] * C12 + (p[2] - H) * S12)          # depth behind the glass of a world point
def up_of(p): return -p[1] * S12 + (p[2] - H) * C12           # 'up' in the slab frame (design z * 10)
SN = (0, C12, S12)                                            # the screen's outward normal (world)
