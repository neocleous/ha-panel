"""Print files of version 67: reads a published project (3MF) back and lists what the Bambu Studio window will load:
  - project settings (Metadata/project_settings.config): filaments, support and interface filaments, top Z distance, interface
    spacing and layers, prime tower and its place, walls, infill, brim, plate type, nozzles, filament map, shrinkage, thin walls;
  - plate (Metadata/model_settings.config): plate name, filament grouping (mode and maps), the objects with their parts
    (normal parts, support blockers), per-object settings;
  - placement (3D/3dmodel.model): each build item's translation.
  - whether G-code is inside (a sliced project) and the plate's slice info.
Usage: python3 check3mf.py <file.3mf> [...]   -> prints one JSON per file"""
import sys, zipfile, json, re

KEYS = ('filament_settings_id', 'filament_colour', 'filament_type', 'filament_shrink', 'filament_map', 'filament_map_mode',
        'nozzle_volume_type', 'curr_bed_type', 'enable_support', 'support_type', 'support_style', 'support_threshold_angle',
        'support_filament', 'support_interface_filament', 'support_top_z_distance', 'support_bottom_z_distance',
        'support_interface_top_layers', 'support_interface_bottom_layers', 'support_interface_spacing', 'support_object_xy_distance',
        'enable_prime_tower', 'prime_tower_width', 'prime_tower_brim_width', 'wipe_tower_x', 'wipe_tower_y', 'wall_loops',
        'sparse_infill_density', 'sparse_infill_pattern', 'layer_height', 'initial_layer_print_height', 'brim_type', 'brim_width',
        'brim_object_gap', 'xy_hole_compensation', 'elefant_foot_compensation', 'bridge_no_support', 'detect_thin_wall',
        'print_settings_id', 'printer_settings_id', 'top_shell_layers', 'bottom_shell_layers')


def read(path):
    z = zipfile.ZipFile(path); names = z.namelist(); out = {'file': path.split('/')[-1], 'entries': len(names)}
    ps = json.loads(z.read('Metadata/project_settings.config').decode('utf-8'))
    out['settings'] = {k: ps.get(k) for k in KEYS if k in ps}
    ms = z.read('Metadata/model_settings.config').decode('utf-8')
    plate = re.search(r'<plate>(.*?)</plate>', ms, re.S)
    meta = lambda blk, k: (re.search(r'<metadata key="%s" value="([^"]*)"' % re.escape(k), blk) or [None, None])[1]
    if plate:
        pb = plate.group(1)
        out['plate'] = {k: meta(pb, k) for k in ('plater_id', 'plater_name', 'filament_map_mode', 'filament_maps', 'locked')}
    objs = []
    for ob in re.finditer(r'<object id="(\d+)">(.*?)</object>', ms, re.S):
        blk = ob.group(2)
        o = {'id': ob.group(1), 'name': meta(blk, 'name'), 'extruder': meta(blk, 'extruder'), 'parts': []}
        head = blk.split('<part')[0]
        o['settings'] = {m.group(1): m.group(2) for m in re.finditer(r'<metadata key="([^"]+)" value="([^"]*)"', head)
                         if m.group(1) not in ('name', 'extruder')}
        for pt in re.finditer(r'<part id="(\d+)" subtype="([^"]+)"[^>]*>(.*?)</part>', blk, re.S):
            mx = meta(pt.group(3), 'matrix'); t = [round(float(v), 3) for v in mx.split()][3:12:4] if mx else None
            o['parts'].append({'id': pt.group(1), 'subtype': pt.group(2), 'name': meta(pt.group(3), 'name'),
                               'extruder': meta(pt.group(3), 'extruder'), 'source': meta(pt.group(3), 'source_file'),
                               'translation': t,
                               'settings': {m.group(1): m.group(2) for m in re.finditer(r'<metadata key="([^"]+)" value="([^"]*)"', pt.group(3))
                                            if m.group(1) not in ('name', 'extruder', 'matrix', 'source_file', 'source_object_id',
                                                                  'source_volume_id', 'source_offset_x', 'source_offset_y', 'source_offset_z')}})
        objs.append(o)
    out['objects'] = objs
    mdl = z.read('3D/3dmodel.model').decode('utf-8', 'replace')
    out['build_items'] = [(m.group(1), [round(float(v), 3) for v in m.group(2).split()[-3:]])
                          for m in re.finditer(r'<item objectid="(\d+)"[^>]*?transform="([^"]+)"', mdl)]
    out['pngs'] = [n for n in names if n.endswith('.png')]
    out['gcode_inside'] = [n for n in names if n.endswith('.gcode')]
    if 'Metadata/slice_info.config' in names:
        si = z.read('Metadata/slice_info.config').decode('utf-8', 'replace')
        out['slice_info'] = {k: meta(si, k) for k in ('prediction', 'weight', 'support_used', 'label_object_enabled', 'nozzle_diameters')}
        out['slice_warnings'] = re.findall(r'<warning msg="([^"]+)"', si)
    z.close()
    return out


if __name__ == '__main__':
    for p in sys.argv[1:]:
        print(json.dumps(read(p), indent=1))
