# pf67_5_publish (blocks 2-4). Touches no Fusion object. pf_5_publish of 2026-11-16 for the new folder: copies each finished
#   project (slicer/out/<job>/<job>.3mf) to its folder under print_files_v67/ with its final name (spec "deliver"), setting two
#   plate fields that the command line leaves unset or at its default (README lesson 3): the plate's name (part, plate type,
#   glue) and the plate's filament grouping, set to Manual with the nozzles the project settings already name (filament 1 on
#   nozzle 1, the main (left) nozzle; Support for ABS, filament 2, on nozzle 2, the auxiliary (right)), so the window keeps them
#   when the project is sliced again. Every other entry of the 3MF is copied unchanged (same bytes, same compression), G-code
#   included. Then reads the published file back and records what the plate now says. Never writes into print_files/ (the
#   files of 2026-11-16). R2_ARGS: {'jobs': [...]}. Records size and sha256.
import zipfile, re


def r2_fix_plate(xml, plate_name, maps):
    def set_meta(x, key, val):
        pat = re.compile(r'(<metadata key="%s" value=")[^"]*("/>)' % re.escape(key))
        if pat.search(x):
            return pat.sub(lambda m: m.group(1) + val + m.group(2), x, count=1)
        return x.replace('<metadata key="locked"', '<metadata key="%s" value="%s"/>\n    <metadata key="locked"' % (key, val), 1)
    xml = set_meta(xml, 'plater_name', plate_name)
    if maps:
        xml = set_meta(xml, 'filament_map_mode', 'Manual')
        xml = set_meta(xml, 'filament_maps', ' '.join(str(m) for m in maps))
    return xml


def r2_plate_meta(path):
    z = zipfile.ZipFile(path); x = z.read('Metadata/model_settings.config').decode('utf-8'); z.close()
    get = lambda k: (re.search(r'<metadata key="%s" value="([^"]*)"/>' % re.escape(k), x) or [None, None])[1]
    return {'plater_name': get('plater_name'), 'filament_map_mode': get('filament_map_mode'), 'filament_maps': get('filament_maps')}


def run(_context):
    recp = os.path.join(R2_DIR, 'data', 'pf67_5_publish.json')
    rec = json.load(open(recp)) if os.path.exists(recp) else {}
    for job in R2_ARGS['jobs']:
        spec = json.load(open(os.path.join(R2_DIR, 'slicer', 'jobs', job, 'spec.json')))
        if 'deliver' not in spec:
            continue
        src = os.path.join(R2_DIR, 'slicer', 'out', job, job + '.3mf')
        if not os.path.exists(src):
            rec[job] = {'error': 'no 3mf'}; continue
        folder, name = spec['deliver']
        dd = os.path.join(R2_OUTDIR, folder)
        if not os.path.abspath(dd).startswith(os.path.abspath(R2_OUTDIR) + os.sep):
            raise RuntimeError('outside print_files_v67: ' + dd)
        os.makedirs(dd, exist_ok=True); dst = os.path.join(dd, name)
        zin = zipfile.ZipFile(src)
        tmp = dst + '.tmp'
        zout = zipfile.ZipFile(tmp, 'w')
        for it in zin.infolist():
            data = zin.read(it.filename)
            if it.filename == 'Metadata/model_settings.config':
                x = data.decode('utf-8')
                x2 = r2_fix_plate(x, spec['plates'][0]['name'], list(range(1, len(spec['filaments']) + 1)))
                data = x2.encode('utf-8')
            zout.writestr(it, data, compress_type=it.compress_type)
        zout.close(); zin.close()
        os.replace(tmp, dst); how = 'sliced' if spec.get('slice', True) else 'for the window'
        rec[job] = {'file': os.path.join(folder, name), 'bytes': os.path.getsize(dst), 'sha256': r2_sha(dst), 'how': how,
                    'plate': r2_plate_meta(dst), 't': time.strftime('%Y-%m-%d %H:%M:%S')}
    r2_out(recp, rec)
    r2_log('pf67_5_publish', 'run', {j: rec.get(j, {}).get('file') for j in R2_ARGS['jobs']})
    print(json.dumps({j: {k: v for k, v in rec[j].items() if k != 'sha256'} for j in R2_ARGS['jobs'] if j in rec}, separators=(',', ':')))
