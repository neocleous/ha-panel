# Builds Bambu Studio command-line jobs for the print files (2026-11-16): jobs/<job>/assemble.json + args.json + spec.json with
#   Mac paths, written to $PF_JOBS/<job>/. Derived from print_audit/recheck2/slicer/mkjob.py (docs 89d06d7).
# spec: {"job": str, "process": "process_0.20_Standard.json", "filaments": ["filament_BambuABS_black.json", ...],
#   "bed": "Textured PEI Plate", "opts": {cli option: value}, "slice": true|false (false = project only, for the window),
#   "title": str, "desc": str, "deliver": [folder, file name],
#   "plates": [{"name": str, "objects": [{"stl": "x.stl" | "path": "...", "subtype": "normal_part", "assemble": 1, "fil": 1,
#        "pos": [x, y, z], "params": {...}}]}]}
# {RC2} in a path stands for the re-check's folder (PF_RC2_DIR), used by the two control jobs Z1, Z2.
# pos is a plain offset added to the mesh's own bed coordinates (the oriented meshes are centred on 128, 128).
import sys, json, os, ast
WORK = os.environ.get('PF_MAC_WORK', '/Users/<mac-user>/Documents/HA_panel_renders/print_files/_work')
MAC = WORK + '/slicer'
ORIENT = WORK + '/orient'
RC2 = os.environ.get('PF_RC2_DIR', '/Users/<mac-user>/Documents/HA_panel_renders/print_audit_recheck2')
OUT = os.environ.get('PF_JOBS', '/home/claude/pf/jobs')
BASE_OPTS = {'nozzle-volume-type': 'High Flow,High Flow', 'filament-map-mode': 'Manual', 'xy-hole-compensation': '0.1',
             'elefant-foot-compensation': '0.15', 'bridge-no-support': '1', 'support-type': 'tree(auto)',
             'support-threshold-angle': '30'}


def objs_of(lst):
    objs = []
    for o in lst:
        pos = o.get('pos', (0.0, 0.0, 0.0))
        j = {'path': (o.get('path') or '%s/%s' % (ORIENT, o['stl'])).replace('{RC2}', RC2), 'count': 1, 'filaments': [o.get('fil', 1)],
             'subtype': o.get('subtype', 'normal_part'), 'pos_x': [float(pos[0])], 'pos_y': [float(pos[1])], 'pos_z': [float(pos[2])]}
        if o.get('assemble'):
            j['assemble_index'] = [o['assemble']]
        if o.get('params'):
            j['print_params'] = {k: str(v) for k, v in o['params'].items()}
        objs.append(j)
    return objs


def build(spec):
    job = spec['job']; d = os.path.join(OUT, job); os.makedirs(d, exist_ok=True)
    plates = []
    for p in spec['plates']:
        pj = {'plate_name': p.get('name', job), 'need_arrange': False, 'objects': objs_of(p['objects'])}
        plates.append(pj)
    json.dump({'plates': plates}, open(os.path.join(d, 'assemble.json'), 'w'), indent=1)
    opts = dict(BASE_OPTS); opts.update({k: str(v) for k, v in (spec.get('opts') or {}).items()})
    opts.setdefault('curr-bed-type', spec.get('bed', 'Textured PEI Plate'))
    opts.setdefault('filament-map', ','.join(str(i + 1) for i in range(len(spec['filaments']))) if len(spec['filaments']) > 1 else '1')
    args = ['--debug=%s' % spec.get('debug', 2), '--datadir', MAC + '/bsdata',
            '--load-settings', '%s/flat/machine_X2D_0.4.json;%s/flat/%s' % (MAC, MAC, spec['process']),
            '--load-filaments', ';'.join('%s/flat/%s' % (MAC, f) for f in spec['filaments']),
            '--load-assemble-list', '%s/jobs/%s/assemble.json' % (MAC, job)]
    for k, v in opts.items():
        args += ['--%s=%s' % (k, v)]          # key=value form: a bool must not take the next token
    if spec.get('title') or spec.get('desc'):
        for s in (spec.get('title', ''), spec.get('desc', '')):
            assert ';' not in s, 'no semicolons in metadata'
        args += ['--metadata-name', 'Title;Description', '--metadata-value', '%s;%s' % (spec.get('title', ''), spec.get('desc', ''))]
    if spec.get('slice', True):
        args += ['--slice', '0']
    args += ['--outputdir', '%s/out/%s' % (MAC, job), '--export-3mf', job + '.3mf']
    json.dump(args, open(os.path.join(d, 'args.json'), 'w'), indent=1)
    json.dump(spec, open(os.path.join(d, 'spec.json'), 'w'), indent=1)
    return d, args


if __name__ == '__main__':
    for s in sys.argv[1:]:
        spec = json.load(open(s)) if os.path.exists(s) else ast.literal_eval(s)
        d, args = build(spec)
        print(d, len(args), 'args')
