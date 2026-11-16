# pf_4_flatten (block 1/3). Touches no Fusion object. Flattens Bambu Studio system presets (inherits chain + "include"
#   templates, as print_audit/recheck/slicer/flatten.py) straight from the Mac's system folder into _work/slicer/flat/, for the
#   command line (it reads only the keys in the file it is given). Re-flattens the ABS and Support for ABS presets as a check
#   against the copies the re-checks used, and adds the PLA preset Daniel chose. Then writes the coloured variants the print
#   files load (display colour only; the name stays the system preset's, so Bambu Studio links each project to its preset).
R2_SYSD = os.path.expanduser('~/Library/Application Support/BambuStudio/system/BBL')
R2_JOBS_F = [('filament', 'Bambu ABS @BBL X2D 0.4 nozzle', 'chk_filament_BambuABS.json'),
             ('filament', 'Bambu Support for ABS @BBL X2D 0.4 nozzle', 'chk_filament_SupportABS.json'),
             ('filament', 'Bambu PLA Basic @BBL X2D 0.4 nozzle', 'filament_BambuPLABasic.json')]
R2_COLOUR = [('filament_BambuABS.json', 'filament_BambuABS_black.json', '#000000'),
             ('filament_SupportABS.json', 'filament_SupportABS_white.json', '#FFFFFF'),
             ('filament_BambuPLABasic.json', 'filament_BambuPLABasic_black.json', '#000000')]


def r2_load(kind, name):
    return json.load(open(os.path.join(R2_SYSD, kind, name + '.json')))


def r2_flat(kind, name):
    chain = []; n = name
    while n:
        d = r2_load(kind, n); chain.append(d); n = d.get('inherits', '')
    out = {}
    META = ('name', 'type', 'from', 'inherits', 'setting_id', 'instantiation', 'include', 'description')
    for d in reversed(chain):
        inc = d.get('include', [])
        for n2 in ([inc] if isinstance(inc, str) else inc):
            for k, v in r2_load(kind, n2).items():
                if k not in META:
                    out[k] = v
        for k, v in d.items():
            if k != 'include':
                out[k] = v
    out['name'] = name; out['from'] = 'system'; out['inherits'] = ''; out['instantiation'] = 'true'
    return out, [c.get('name') for c in chain]


def run(_context):
    fd = os.path.join(R2_DIR, 'slicer', 'flat'); res = {}
    for kind, name, fn in R2_JOBS_F:
        d, ch = r2_flat(kind, name)
        json.dump(d, open(os.path.join(fd, fn), 'w'), indent=1)
        res[fn] = {'chain': ch, 'keys': len(d)}
    for chk, ref in (('chk_filament_BambuABS.json', 'filament_BambuABS.json'), ('chk_filament_SupportABS.json', 'filament_SupportABS.json')):
        a = json.load(open(os.path.join(fd, chk))); b = json.load(open(os.path.join(fd, ref)))
        res[chk]['same_as_recheck_flat'] = (a == b)
        res[chk]['keys_differing'] = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))[:20]
    p = json.load(open(os.path.join(fd, 'filament_BambuPLABasic.json')))
    res['pla_keys'] = {k: p.get(k) for k in ('filament_type', 'filament_density', 'filament_shrink', 'nozzle_temperature',
                                             'nozzle_temperature_initial_layer', 'textured_plate_temp', 'cool_plate_temp',
                                             'eng_plate_temp', 'supertack_plate_temp', 'chamber_temperatures',
                                             'filament_max_volumetric_speed', 'compatible_printers', 'filament_cost',
                                             'filament_colour', 'default_filament_colour', 'filament_vendor',
                                             'temperature_vitrification')}
    for src, dst, col in R2_COLOUR:
        j = json.load(open(os.path.join(fd, src)))
        j['filament_colour'] = [col]; j['default_filament_colour'] = [col]
        json.dump(j, open(os.path.join(fd, dst), 'w'), indent=1)
        res[dst] = r2_sha(os.path.join(fd, dst))[:12]
    r2_out(os.path.join(R2_DIR, 'data', 'pf_4_flatten.json'), res)
    print(json.dumps(res, separators=(',', ':')))
