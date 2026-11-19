# pf_0_preflight (block 0). READ-ONLY on the design (connector readOnly: true). Writes only under print_files/_work/.
#   Records: document, version, modified flag; body count, visible bodies, AUD_/NEW_ templates, the _v63 / _v64 backups;
#   the unit's count (16 leads, 13 keep-outs expected); the nine guard volumes and lumps; scope B volumes; camera as found;
#   open documents; Bambu Studio's version; whether the system presets still equal the copies the 11-14 run flattened;
#   the X2D 0.4 filament presets the Mac's Bambu Studio offers for PLA; the re-check's jobs and meshes present.
import plistlib, shutil

R2_BS_APP = '/Applications/BambuStudio.app'
R2_BS_SYS = os.path.expanduser('~/Library/Application Support/BambuStudio/system/BBL')
R2_KEYS_P = ('layer_height', 'initial_layer_print_height', 'wall_loops', 'top_shell_layers', 'bottom_shell_layers',
             'sparse_infill_density', 'sparse_infill_pattern', 'support_type', 'support_style', 'support_threshold_angle',
             'support_top_z_distance', 'support_bottom_z_distance', 'support_interface_top_layers',
             'support_interface_bottom_layers', 'support_interface_spacing', 'support_interface_pattern',
             'support_object_xy_distance', 'support_filament', 'support_interface_filament', 'tree_support_wall_count',
             'enable_prime_tower', 'prime_tower_width', 'prime_tower_brim_width', 'wipe_tower_x', 'wipe_tower_y',
             'brim_type', 'brim_width', 'brim_object_gap', 'elefant_foot_compensation', 'xy_hole_compensation',
             'xy_contour_compensation', 'bridge_no_support', 'independent_support_layer_height', 'top_surface_pattern',
             'bottom_surface_pattern', 'ironing_type', 'seam_position', 'enable_support', 'raft_layers',
             'support_base_pattern', 'support_base_pattern_spacing', 'filament_map_mode', 'print_sequence')
R2_KEYS_F = ('filament_type', 'filament_vendor', 'filament_colour', 'filament_density', 'filament_shrink',
             'filament_shrinkage_compensation_z', 'nozzle_temperature', 'nozzle_temperature_initial_layer',
             'textured_plate_temp', 'textured_plate_temp_initial_layer', 'eng_plate_temp', 'eng_plate_temp_initial_layer',
             'cool_plate_temp', 'cool_plate_temp_initial_layer', 'supertack_plate_temp', 'hot_plate_temp',
             'chamber_temperatures', 'filament_is_support', 'required_nozzle_HRC', 'filament_max_volumetric_speed',
             'filament_settings_id', 'compatible_printers', 'filament_cost', 'temperature_vitrification',
             'filament_flow_ratio', 'filament_notes')


def run(_context):
    t0 = time.time(); X = R2Ctx(); out = {'t': time.strftime('%Y-%m-%d %H:%M:%S')}
    df = X.doc.dataFile
    out['doc'] = [X.doc.name, df.versionNumber, df.latestVersionNumber, df.description, X.doc.isModified, X.des.designType]
    bodies = list(X.root.bRepBodies)
    names = [b.name for b in bodies]
    out['n_bodies'] = len(names)
    vis = sorted(b.name for b in bodies if b.isLightBulbOn)
    out['n_visible'] = len(vis); out['visible'] = vis
    out['templates'] = [n for n in names if n.upper().startswith(('AUD_', 'NEW_', 'RENDER_TMP'))]
    out['backups'] = {k: len([b for b in bodies if b.name.endswith(k)]) for k in ('_v63', '_v64')}
    cur = r2_unit(X)
    out['unit'] = [len(cur), sum(1 for b in cur if b.name.startswith('LEAD_')), sum(1 for b in cur if b.name.startswith('KO_'))]
    out['dups'] = sorted(set(n for n in names if names.count(n) > 1))
    rep, bad = r2_guard(X, strict=False)
    out['guard'] = {n: [rep.get(n, [None])[0], (round(rep[n][0] - v, 3) if n in rep else None), rep.get(n, [None, None])[1]]
                    for n, v in R2_GUARD.items()}
    out['guard_bad'] = bad
    out['scope_b'] = {}
    for n, v in R2_SCOPE_B.items():
        b = X.body(n)
        out['scope_b'][n] = None if b is None else [round(b.volume * 1000.0, 3), round(b.volume * 1000.0 - v, 3), b.lumps.count]
    vp = X.app.activeViewport; cm = vp.camera
    out['camera'] = {'eye': [round(cm.eye.x, 3), round(cm.eye.y, 3), round(cm.eye.z, 3)],
                     'target': [round(cm.target.x, 3), round(cm.target.y, 3), round(cm.target.z, 3)], 'style': vp.visualStyle}
    out['docs_open'] = [[d.name, d.isModified] for d in X.app.documents]
    # slicer
    q = os.path.join(R2_BS_APP, 'Contents', 'Info.plist')
    out['bambu_studio'] = None
    if os.path.exists(q):
        d = plistlib.load(open(q, 'rb'))
        out['bambu_studio'] = [d.get('CFBundleShortVersionString'), d.get('CFBundleVersion')]
    prof = os.path.join(R2_RC1, 'slicer', 'profiles')
    cmp_ = {}
    if os.path.isdir(prof):
        for kind in sorted(os.listdir(prof)):
            kd = os.path.join(prof, kind)
            if not os.path.isdir(kd):
                continue
            for f in sorted(os.listdir(kd)):
                a = r2_sha(os.path.join(kd, f)); s = r2_sha(os.path.join(R2_BS_SYS, kind, f))
                cmp_['%s/%s' % (kind, f)] = 'equal' if (a and a == s) else ('system missing' if s is None else 'DIFFERS')
    out['presets_vs_system'] = cmp_
    # PLA presets for the X2D 0.4 in the system folder
    fd = os.path.join(R2_BS_SYS, 'filament')
    out['pla_x2d'] = sorted(f for f in os.listdir(fd) if 'PLA' in f and 'X2D 0.4' in f) if os.path.isdir(fd) else None
    out['abs_x2d'] = sorted(f for f in os.listdir(fd) if ('ABS' in f) and 'X2D 0.4' in f) if os.path.isdir(fd) else None
    # flat presets of the re-check: copy to this session's work folder; key values
    fl = os.path.join(R2_RC2, 'slicer', 'flat')
    for sub in ('exports', 'data', 'orient', 'slicer/flat', 'slicer/jobs', 'slicer/out', 'slicer/bsdata', 'lib/steps'):
        os.makedirs(os.path.join(R2_DIR, sub), exist_ok=True)
    copied = []; keys = {}
    for f in sorted(os.listdir(fl)):
        if not f.endswith('.json'):
            continue
        dst = os.path.join(R2_DIR, 'slicer', 'flat', f)
        if not os.path.exists(dst):
            shutil.copy2(os.path.join(fl, f), dst); copied.append(f)
        j = json.load(open(dst))
        ks = R2_KEYS_P if f.startswith('process') else (R2_KEYS_F if f.startswith('filament') else ())
        keys[f] = {k: j.get(k) for k in ks if k in j}
        keys[f]['_sha'] = r2_sha(dst)[:12]
    out['flat_copied'] = copied
    out['flat_keys'] = keys
    # the re-check's oriented meshes and job outputs
    out['rc2_orient'] = sorted(os.listdir(os.path.join(R2_RC2, 'slicer', 'orient')))
    out['rc1_orient'] = sorted(os.listdir(os.path.join(R2_RC1, 'slicer', 'orient')))
    out['rc2_out_3mf'] = sorted(j for j in os.listdir(os.path.join(R2_RC2, 'slicer', 'out'))
                                if os.path.exists(os.path.join(R2_RC2, 'slicer', 'out', j, j + '.3mf')))
    out['t_s'] = round(time.time() - t0, 1)
    r2_out(os.path.join(R2_DIR, 'data', 'pf_0_preflight.json'), out)
    r2_log('pf_0_preflight', 'run', {'bad': bad, 'n_bodies': out['n_bodies'], 'unit': out['unit'], 'n_visible': out['n_visible']})
    o2 = dict(out); o2.pop('visible')
    print(json.dumps(o2, separators=(',', ':')))
