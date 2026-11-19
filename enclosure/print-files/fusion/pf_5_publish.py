# pf_5_publish (blocks 1-3). Touches no Fusion object. Copies each finished project (slicer/out/<job>/<job>.3mf) to its folder
#   under print_files/ with its final name (spec "deliver"), setting two plate fields that the command line leaves unset or at
#   its default: the plate's name (the spec's plate name: part, plate type, glue) and the plate's filament grouping, set to Manual
#   with the nozzles the project settings already name (filament 1 on nozzle 1, the left; Support for ABS, filament 2, on
#   nozzle 2, the right), so the window keeps them when the project is sliced again. Every other entry of the 3MF is copied
#   unchanged (same bytes, same compression), G-code included. R2_ARGS: {'jobs': [...]}. Records size and sha256.
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


def run(_context):
    recp = os.path.join(R2_DIR, 'data', 'pf_5_publish.json')
    rec = json.load(open(recp)) if os.path.exists(recp) else {}
    for job in R2_ARGS['jobs']:
        spec = json.load(open(os.path.join(R2_DIR, 'slicer', 'jobs', job, 'spec.json')))
        if 'deliver' not in spec:
            continue
        src = os.path.join(R2_DIR, 'slicer', 'out', job, job + '.3mf')
        if not os.path.exists(src):
            rec[job] = {'error': 'no 3mf'}; continue
        folder, name = spec['deliver']
        dd = os.path.join(R2_OUTDIR, folder); os.makedirs(dd, exist_ok=True); dst = os.path.join(dd, name)
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
        rec[job] = {'file': os.path.join(folder, name), 'bytes': os.path.getsize(dst), 'sha256': r2_sha(dst)[:16], 'how': how}
    r2_out(recp, rec)
    print(json.dumps(rec, separators=(',', ':')))
