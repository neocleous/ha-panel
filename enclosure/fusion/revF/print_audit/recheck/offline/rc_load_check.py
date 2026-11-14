# recheck: mesh check of the 13 exports against the B-rep volumes (rc1_export.json)
import trimesh, numpy as np, json
UP = '/mnt/user-data/uploads/print_audit_recheck/exports/'
E = json.load(open('/mnt/user-data/uploads/print_audit_recheck/data/rc1_export.json'))
res = {}
for tag in ['front','plate','spkbox_L','spkbox_R','carrier','cradle','door','cap','slab','grommet','clip_L','clip_R','bme_hood']:
    m = trimesh.load(UP + tag + '.stl', force='mesh', process=True)
    v = E[tag]['vol_mm3']
    res[tag] = dict(tris=len(m.faces), watertight=bool(m.is_watertight), winding=bool(m.is_winding_consistent),
                    vol_mm3=round(float(m.volume), 2), brep_mm3=v, dvol_pct=round(100*(m.volume-v)/v, 4),
                    bbox=[round(float(x), 3) for x in np.concatenate([m.bounds[0], m.bounds[1]])])
    print(tag, res[tag], flush=True)
json.dump(res, open('/home/claude/pa/data/mesh_check.json', 'w'), indent=1)
