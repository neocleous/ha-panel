# Flattens Bambu Studio system presets (inherits chain + machine "include" templates) into single JSONs for the CLI, which reads
# only the keys in the file it is given (no inherits resolution for "from": "system"; the app bundle has no *_full folders).
import json, os, sys
SRC = '/mnt/user-data/uploads/print_audit_recheck/slicer/profiles'
OUT = '/home/claude/rc/slicer/flat'

def load(kind, name):
    return json.load(open(os.path.join(SRC, kind, name + '.json')))

def flat(kind, name):
    chain = []; n = name
    while n:
        d = load(kind, n); chain.append(d); n = d.get('inherits', '')
    out = {}
    META = ('name', 'type', 'from', 'inherits', 'setting_id', 'instantiation', 'include', 'description')
    for d in reversed(chain):                      # root first: full(d) = full(parent) <- includes(d) <- own(d) (PresetBundle order)
        inc = d.get('include', [])
        for n in ([inc] if isinstance(inc, str) else inc):
            for k, v in load(kind, n).items():
                if k not in META:
                    out[k] = v
        for k, v in d.items():
            if k != 'include':
                out[k] = v
    out['name'] = name; out['from'] = 'system'; out['inherits'] = ''; out['instantiation'] = 'true'
    return out, [c.get('name') for c in chain]

JOBS = [('machine', 'Bambu Lab X2D 0.4 nozzle', 'machine_X2D_0.4.json'),
        ('process', '0.20mm Standard @BBL X2D', 'process_0.20_Standard.json'),
        ('process', '0.16mm Standard @BBL X2D', 'process_0.16_Standard.json'),
        ('process', '0.12mm High Quality @BBL X2D', 'process_0.12_HQ.json'),
        ('process', '0.08mm High Quality @BBL X2D', 'process_0.08_HQ.json'),
        ('process', '0.20mm High Quality @BBL X2D', 'process_0.20_HQ.json'),
        ('filament', 'Bambu ABS @BBL X2D 0.4 nozzle', 'filament_BambuABS.json'),
        ('filament', 'Bambu ASA @BBL X2D 0.4 nozzle', 'filament_BambuASA.json'),
        ('filament', 'Bambu Support for ABS @BBL X2D 0.4 nozzle', 'filament_SupportABS.json')]
os.makedirs(OUT, exist_ok=True)
for kind, name, fn in JOBS:
    d, ch = flat(kind, name)
    json.dump(d, open(os.path.join(OUT, fn), 'w'), indent=1)
    print(fn, len(d), 'keys; chain', ch, '; start_gcode' if 'machine_start_gcode' in d else '')
