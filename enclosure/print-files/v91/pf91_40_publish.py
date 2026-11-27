# Print files of version 91: the print files. No Fusion object. Ported from version 67's pf67_5_publish.py.
# Copies each finished project (slicer/out/<job>/<job>.3mf) of a plate that passed the stop rule to its set's folder under
# print_files_v91/ with its final name, setting two plate fields that the command line leaves unset or at its default: the plate's
# name (part, plate type, glue) and the plate's filament grouping, set to Manual with the nozzles the project settings already name
# (filament 1 on nozzle 1, the main (left) nozzle; Support for ABS, filament 2, on nozzle 2, the auxiliary (right)), so that the window
# keeps them when the project is sliced again. Every other entry of the 3MF is copied unchanged (same bytes, same compression),
# G-code included. Then reads the published file back. Never writes outside print_files_v91/.
#   publish(jobs): the jobs named.   held(): what is held, and why (written beside the files as HELD.md is not done: the sheet says it).
import os, re, json, time, zipfile, runpy
D = os.path.dirname(os.path.abspath(__file__))
L = runpy.run_path(os.path.join(D, 'pf91_lib.py'))
OUTDIR = L['OUTDIR']


def _fix(xml, plate_name, maps):
    def set_meta(x, key, val):
        pat = re.compile(r'(<metadata key="%s" value=")[^"]*("/>)' % re.escape(key))
        if pat.search(x):
            return pat.sub(lambda m: m.group(1) + val + m.group(2), x, count=1)
        return x.replace('<metadata key="locked"', '<metadata key="%s" value="%s"/>\n    <metadata key="locked"' % (key, val), 1)
    xml = set_meta(xml, 'plater_name', plate_name)
    xml = set_meta(xml, 'filament_map_mode', 'Manual')
    xml = set_meta(xml, 'filament_maps', ' '.join(str(m) for m in maps))
    return xml


def _meta(path):
    z = zipfile.ZipFile(path); names = z.namelist(); x = z.read('Metadata/model_settings.config').decode('utf-8')
    mdl = z.read('3D/3dmodel.model').decode('utf-8', 'replace'); z.close()
    get = lambda k: (re.search(r'<metadata key="%s" value="([^"]*)"/>' % re.escape(k), x) or [None, None])[1]
    t = re.search(r'<metadata name="Title">([^<]*)</metadata>', mdl)
    return {'plater_name': get('plater_name'), 'filament_map_mode': get('filament_map_mode'), 'filament_maps': get('filament_maps'),
            'gcode': [n for n in names if n.endswith('.gcode')], 'title': t.group(1) if t else None}


def publish(jobs):
    recp = os.path.join(L['W'], 'out', 'pf91_40_publish.json')
    rec = json.load(open(recp)) if os.path.exists(recp) else {}
    for job in jobs:
        spec = json.load(open(os.path.join(L['W'], 'slicer', 'jobs', job, 'spec.json')))
        src = os.path.join(L['W'], 'slicer', 'out', job, job + '.3mf')
        res = json.load(open(os.path.join(L['W'], 'slicer', 'out', job, 'result.json')))
        if res.get('return_code') != 0 or not os.path.exists(src):
            rec[job] = {'error': 'no finished 3mf'}; print(job, 'NOT PUBLISHED: no finished 3mf'); continue
        folder, name = spec['deliver']; dd = os.path.join(OUTDIR, folder)
        if not os.path.abspath(dd).startswith(OUTDIR + os.sep) or '_work' in folder:
            raise RuntimeError('refused: ' + dd)
        os.makedirs(dd, exist_ok=True); dst = os.path.join(dd, name); tmp = dst + '.tmp'
        zin = zipfile.ZipFile(src); zout = zipfile.ZipFile(tmp, 'w')
        for it in zin.infolist():
            data = zin.read(it.filename)
            if it.filename == 'Metadata/model_settings.config':
                data = _fix(data.decode('utf-8'), spec['plates'][0]['name'], list(range(1, len(spec['filaments']) + 1))).encode('utf-8')
            zout.writestr(it, data, compress_type=it.compress_type)
        zout.close(); zin.close(); os.replace(tmp, dst)
        pl = (res.get('sliced_plates') or [{}])[0]
        rec[job] = {'file': os.path.join(folder, name), 'bytes': os.path.getsize(dst), 'sha256': L['sha'](dst), 'meta': _meta(dst),
                    'min': round(pl.get('main_predication', 0) / 60.0, 1), 'min_prep': round(pl.get('total_predication', 0) / 60.0, 1),
                    'g': [round(f.get('total_used_g', 0), 2) for f in pl.get('filaments', [])], 'warning': (pl.get('warning_message') or '')[:200],
                    't': L['stamp']()}
        print('%-8s -> %-60s %9d bytes sha %s | %s' % (job, rec[job]['file'], rec[job]['bytes'], rec[job]['sha256'][:12], rec[job]['meta']))
    L['jdump'](recp, rec)
# END pf91_40_publish.py
