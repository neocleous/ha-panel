"""Slice check: oriented audit meshes of version 66 (print frame, on the bed) and Bambu Studio command-line jobs
with the print plan's settings. These are audit slices, not print files: no supports, no brim, one part per job."""
import json, os, struct, numpy as np
from fdm_lib import *
OUT = '/mnt/user-data/outputs/fdm_slicer'
MAC = '/Users/danielneocleous/Documents/HA_panel_renders/fdm_audit/slicer'
FLAT = '/Users/danielneocleous/Documents/HA_panel_renders/print_audit_recheck2/slicer/flat'
TAG = {'HOUSING_F_front': 'shell', 'HOUSING_F_plate': 'plate', 'SPKBOX_L': 'boxL', 'SPKBOX_R': 'boxR', 'FLOOR_PLATE': 'base',
       'RESP_CARRIER': 'carrier', 'CRADLE_5807': 'cradle', 'TOUCH_CLIP_L': 'clipL', 'BME_HOOD': 'hood', 'HOUSING_F_cap': 'cap',
       'GROMMET_usbc_F': 'grommet', 'SLAB_frame': 'bezel', 'HOUSING_F_door': 'door'}
os.makedirs(os.path.join(OUT, 'orient'), exist_ok=True)
place = {}
for name, tag in TAG.items():
    p = Part(name)
    V = p.pm.vertices.copy()
    mid = (V[:, :2].min(0) + V[:, :2].max(0)) / 2
    V[:, 0] += 128.0 - mid[0]; V[:, 1] += 128.0 - mid[1]
    place[tag] = dict(body=name, du=float(128.0 - mid[0]), dv=float(128.0 - mid[1]), h0=p.h0,
                      u=p.u.tolist(), v=p.v.tolist(), up=p.up.tolist(), lh=p.lh)
    m = trimesh.Trimesh(vertices=V, faces=p.pm.faces, process=False)
    m.export(os.path.join(OUT, 'orient', 'AUDIT_%s_v66.stl' % tag))
    jd = os.path.join(OUT, 'jobs', 'F_' + tag); os.makedirs(jd, exist_ok=True)
    json.dump({'plates': [{'plate_name': 'F_' + tag, 'need_arrange': False, 'objects': [{
        'path': '%s/orient/AUDIT_%s_v66.stl' % (MAC, tag), 'count': 1, 'filaments': [1], 'subtype': 'normal_part',
        'pos_x': [0.0], 'pos_y': [0.0], 'pos_z': [0.0]}]}]}, open(os.path.join(jd, 'assemble.json'), 'w'), indent=1)
    proc = 'process_0.20_Standard.json' if p.lh == 0.20 else 'process_0.12_HQ.json'
    args = ['--debug=2', '--datadir', MAC + '/bsdata', '--load-settings', '%s/machine_X2D_0.4.json;%s/%s' % (FLAT, FLAT, proc),
            '--load-filaments', FLAT + '/filament_BambuABS.json', '--load-assemble-list', '%s/jobs/F_%s/assemble.json' % (MAC, tag),
            '--nozzle-volume-type=High Flow,High Flow', '--filament-map-mode=Manual', '--xy-hole-compensation=0.1',
            '--elefant-foot-compensation=0.15', '--bridge-no-support=1', '--enable-support=0', '--brim-type=no_brim',
            '--curr-bed-type=Textured PEI Plate', '--filament-map=1']
    if tag == 'plate':
        args += ['--sparse-infill-density=100%', '--sparse-infill-pattern=zig-zag']
    if tag == 'bezel':
        args += ['--layer-height=0.1']
    args += ['--slice', '0', '--outputdir', '%s/out/F_%s' % (MAC, tag), '--export-3mf', 'F_%s.3mf' % tag]
    json.dump(args, open(os.path.join(jd, 'args.json'), 'w'), indent=1)
json.dump(place, open(os.path.join(OUT, 'place.json'), 'w'), indent=1)
json.dump(place, open(os.path.join(DATA, 'slice_place.json'), 'w'), indent=1)
print('jobs', len(TAG))
