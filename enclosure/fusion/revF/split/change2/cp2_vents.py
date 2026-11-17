# change2/cp2_vents.py - the rear door's vent field (D210): today's slots filled from the backup, then a layout cut. Temporary copies only.
# Exec'd into sys.modules['cp2']. k = cp2k (v5f_k_lib.py). World mm. Rebuilt on 2026-11-18 from the bytecode of the functions that ran
# (the typed source was not kept); run again from this file on version 65's door it gives the same volumes (README, lesson 205).
import sys
k = sys.modules['cp2k']
# (centre x, width, z bottom, z top) per slot. Letters as put to Daniel: a = 'b' here (chosen), b = 'a', c = 'c'.
VENTS = {'today': [(c, 3.0, 66.0, {36: 104.5, 42: 96.5}.get(c, 110.0)) for c in range(-24, 43, 6)],
         'a': [(s * c, 3.0, 66.0, 107.5 if c == 33 else 110.0) for c in (3, 9, 15, 21, 27, 33) for s in (-1, 1)],
         'b': [(c, 3.0, 59.5, 116.0) for c in range(-24, 25, 6)],
         'c': [(c, 4.0, 66.0, 110.0) for c in range(-28, 29, 7)]}


def slot_cut(X, rows):                                  # round-ended slots, cut through along world y
    out = None
    for (cx, w, z0, z1) in rows:
        r = w / 2.0
        t = X.wbox(cx - r, cx + r, -100.0, -45.0, z0 + r, z1 - r)
        X.uni(t, X.cyl((cx, -100.0, z0 + r), (cx, -45.0, z0 + r), r))
        X.uni(t, X.cyl((cx, -100.0, z1 - r), (cx, -45.0, z1 - r), r))
        out = t if out is None else X.uni(out, t)
    return out


def door_blank(X, backup='HOUSING_F_door_d5b', src='HOUSING_F_door'):
    # version 65's door with its slots filled: (the backup from before the slots, cut to the field) minus the door = the twelve plugs (3,901.46 mm3).
    # On version 66 pass src='HOUSING_F_door_v65'.
    cur = k.tcopy(X, src); box = X.wbox(-30.0, 48.0, -95.0, -50.0, 62.0, 114.0)
    f = X.tbm.copy(k.tcopy(X, backup)); X.sec(f, box); X.dif(f, cur)
    b = X.tbm.copy(cur); X.uni(b, f)
    return b, X.vol(f), f.lumps.count                   # blank 50,930.19 mm3


def new_door(X, key, src='HOUSING_F_door'):
    b, vf, nl = door_blank(X, src=src)
    v0 = X.vol(b); X.dif(b, slot_cut(X, VENTS[key]))
    return b, v0 - X.vol(b)                             # 'b': 47,034.26; 'a': 46,917.36; 'c': 46,906.91 (today 47,019.77)
