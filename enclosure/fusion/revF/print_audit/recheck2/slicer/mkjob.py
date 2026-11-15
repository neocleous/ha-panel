# Builds a Bambu Studio CLI job (recheck2): jobs/<job>/assemble.json + args.json with Mac paths, written to $R2_JOBS/<job>/.
# spec (JSON file or python dict literal): {"job": str, "process": "process_0.20_Standard.json", "filaments": ["filament_BambuABS.json"],
#   "bed": "Textured PEI Plate", "opts": {cli option: value}, "plates": [{"name": str, "arrange": false, "objects": [
#       {"stl": "screen_plan.stl" | "path": "{R2}/exports/x.stl", "subtype": "normal_part", "assemble": 1, "fil": 1,
#        "pos": [x, y, z], "params": {...}, "ranges": [[z0, z1, {...}]]}], "assembled": {index: {"params": {...}}}}]}
# {R2} stands for the Mac folder of this run, {OLD} for the 2026-11-14 run's folder. Set R2_MAC_DIR / R2_OLD_DIR.
import sys, json, os, ast
R2 = os.environ.get('R2_MAC_DIR', '/Users/<mac-user>/Documents/HA_panel_renders/print_audit_recheck2')
OLD = os.environ.get('R2_OLD_DIR', '/Users/<mac-user>/Documents/HA_panel_renders/print_audit_recheck')
MAC = R2 + '/slicer'
OUT = os.environ.get('R2_JOBS', '/home/claude/r2/jobs')
BASE_OPTS = {'nozzle-volume-type': 'High Flow,High Flow', 'filament-map-mode': 'Manual', 'xy-hole-compensation': '0.1',
             'elefant-foot-compensation': '0.15', 'bridge-no-support': '1', 'support-type': 'tree(auto)',
             'support-threshold-angle': '30'}


def sub(p):
    return p.replace('{R2}', R2).replace('{OLD}', OLD)


def objs_of(lst):
    objs = []
    for o in lst:
        pos = o.get('pos', (0.0, 0.0, 0.0))
        j = {'path': sub(o.get('path') or '%s/orient/%s' % (MAC, o['stl'])), 'count': 1, 'filaments': [o.get('fil', 1)],
             'subtype': o.get('subtype', 'normal_part'), 'pos_x': [float(pos[0])], 'pos_y': [float(pos[1])], 'pos_z': [float(pos[2])]}
        if o.get('assemble'):
            j['assemble_index'] = [o['assemble']]
        if o.get('params'):
            j['print_params'] = {k: str(v) for k, v in o['params'].items()}
        if o.get('ranges'):
            j['height_ranges'] = [{'min_z': r[0], 'max_z': r[1], 'range_params': {k: str(v) for k, v in r[2].items()}} for r in o['ranges']]
        objs.append(j)
    return objs


def build(spec):
    job = spec['job']; d = os.path.join(OUT, job); os.makedirs(d, exist_ok=True)
    plates = []
    for p in spec['plates']:
        pj = {'plate_name': p.get('name', job), 'need_arrange': bool(p.get('arrange', False)), 'objects': objs_of(p['objects'])}
        if p.get('plate_params'):
            pj['plate_params'] = {k: str(v) for k, v in p['plate_params'].items()}
        asm = []
        for ai, a in (p.get('assembled') or {}).items():
            e = {'assemble_index': int(ai)}
            if a.get('params'):
                e['print_params'] = {k: str(v) for k, v in a['params'].items()}
            if a.get('ranges'):
                e['height_ranges'] = [{'min_z': r[0], 'max_z': r[1], 'range_params': {k: str(v) for k, v in r[2].items()}} for r in a['ranges']]
            asm.append(e)
        if asm:
            pj['assembled_params'] = asm
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
    args += spec.get('extra_args', [])
    args += ['--slice', '0', '--outputdir', '%s/out/%s' % (MAC, job), '--export-3mf', job + '.3mf']
    json.dump(args, open(os.path.join(d, 'args.json'), 'w'), indent=1)
    json.dump(spec, open(os.path.join(d, 'spec.json'), 'w'), indent=1)
    return d, args


if __name__ == '__main__':
    for s in sys.argv[1:]:
        spec = json.load(open(s)) if os.path.exists(s) else ast.literal_eval(s)
        d, args = build(spec)
        print(d, len(args), 'args')
