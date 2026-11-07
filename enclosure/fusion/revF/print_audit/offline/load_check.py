import trimesh, numpy as np, json, sys
UP = '/mnt/user-data/uploads/print_audit/exports/'
GUARD = {'front':235.2269,'cap':9.9591,'slab':62.9324,'resp_carrier':10.0716,'door':47.2694,'grommet':0.5062,
         'cradle':2.1775,'bracket_L':2.8294,'bracket_R':3.7268,'bme_hood':0.8029,'spkbox_L':25.6082,'spkbox_R':26.3874,
         'clip_L':0.4896,'clip_R':0.4896}
res = {}
for tag, v in GUARD.items():
    m = trimesh.load(UP + tag + '.stl', force='mesh', process=True)   # merges duplicate vertices by position
    mv = m.volume / 1000.0
    res[tag] = dict(tris=len(m.faces), verts=len(m.vertices), watertight=bool(m.is_watertight),
                    winding=bool(m.is_winding_consistent), vol_cm3=round(mv, 4), guard=v,
                    dvol_pct=round(100*(mv-v)/v, 3), bodies=len(m.split(only_watertight=False)) if len(m.faces) < 400000 else None,
                    bbox=[round(x, 2) for x in np.concatenate([m.bounds[0], m.bounds[1]])])
    print(tag, res[tag], flush=True)
json.dump(res, open('/home/claude/pa/data/mesh_check.json', 'w'), indent=1)
