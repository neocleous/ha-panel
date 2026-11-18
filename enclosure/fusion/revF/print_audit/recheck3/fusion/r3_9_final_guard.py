# recheck3 (print re-check of version 67), closing read. READ-ONLY (connector readOnly: true); writes nothing, prints one JSON line.
#   Document, version, modified flag; body count, visible bodies, AUD_/NEW_ templates, the _v63.._v66 backups; the unit's count
#   (the enclosure chat's rule, as recheck2's r2_unit); the 14 guard volumes of the brief (D228) with lumps; camera and visual style; open documents.
import adsk.core, adsk.fusion, re, json, time
R3_GUARD = {'HOUSING_F_plate': 66463.676, 'HOUSING_F_front': 111611.475, 'SPKBOX_L': 26342.557, 'SPKBOX_R': 27112.045, 'FLOOR_PLATE': 32643.331,
            'RESP_CARRIER': 13651.988, 'CRADLE_5807': 1771.219, 'HOUSING_F_door': 50476.660, 'HOUSING_F_cap': 9986.525, 'TOUCH_CLIP_L': 580.762,
            'TOUCH_CLIP_R': 580.762, 'SLAB_frame': 62932.407, 'GROMMET_usbc_F': 506.176, 'BME_HOOD': 802.884}
R3_BACK = re.compile(r'(_v\d+|_[a-e]\d+[a-z0-9]*| \(\d+\))$')
R3_LEGACY = ('DOOR_tray', 'HOUSING_E', 'HOUSING_shell', 'HOUSING_F_wip', 'AMP_env_20x20x10', 'BUCK_20to5V_env_43x25x13', 'DOOR_plate_revE',
             'GROMMET_usbc', 'HOUSING_F_front_d10_sliver', 'HOUSING_F_front_d12a_sliver1', 'LD2410C_env', 'MAIN_BRACKET_d1split_L',
             'MAIN_BRACKET_d1split_R', 'MAIN_BRACKET_d1split_plug', 'PD_trigger_env_20V', 'PI5_board', 'SPKBOX_L_r2', 'SPK_driver_D40',
             'V11a_mx', 'V11a_px', 'V11a_up', 'V11b_mx', 'V11b_px', 'V11b_up', 'V11c_straight', 'VOICEPE_back_env', 'VOICEPE_encoder_env',
             'VOICEPE_pcb', 'BME680_env_revD', 'TOUCH_pcb_100x44')
R3_NOTPART = ('REF_', 'TOOL_', 'INNER', 'RENDER_', 'AUD_')


def run(_context: str):
    t0 = time.time(); app = adsk.core.Application.get(); doc = app.activeDocument
    if doc.name != 'HA Panel v5 - tapered':
        raise RuntimeError('active document is %r' % doc.name)
    des = adsk.fusion.Design.cast(app.activeProduct); root = des.rootComponent; df = doc.dataFile
    out = {'t': time.strftime('%Y-%m-%d %H:%M:%S'), 'doc': [doc.name, df.versionNumber, df.latestVersionNumber, df.description, doc.isModified]}
    names = [b.name for b in root.bRepBodies]; out['n_bodies'] = len(names)
    out['n_visible'] = sum(1 for b in root.bRepBodies if b.isLightBulbOn)
    out['templates'] = [n for n in names if n.upper().startswith(('AUD_', 'NEW_', 'RENDER_TMP'))]
    out['backups'] = {k: len([n for n in names if n.endswith(k)]) for k in ('_v63', '_v64', '_v65', '_v66')}
    unit = []
    for n in names:
        if n.startswith('LCD_'):
            if not re.search(r'(_v\d+|_[a-e]\d+[a-z0-9]*)$', n): unit.append(n)
            continue
        if R3_BACK.search(n) or n in R3_LEGACY or n.startswith(R3_NOTPART): continue
        unit.append(n)
    out['unit'] = [len(unit), sum(1 for n in unit if n.startswith('LEAD_')), sum(1 for n in unit if n.startswith('KO_'))]
    g = {}
    for n, v in R3_GUARD.items():                       # one body at a time
        b = root.bRepBodies.itemByName(n); vol = b.volume * 1000.0
        g[n] = [round(vol, 3), round(vol - v, 3), b.lumps.count]
    out['guard'] = g
    vp = app.activeViewport; cm = vp.camera
    out['camera'] = {'eye': [round(cm.eye.x, 4), round(cm.eye.y, 4), round(cm.eye.z, 4)], 'target': [round(cm.target.x, 4), round(cm.target.y, 4), round(cm.target.z, 4)], 'style': vp.visualStyle}
    out['docs_open'] = [[d.name, d.isModified] for d in app.documents]
    out['t_s'] = round(time.time() - t0, 1)
    print(json.dumps(out, separators=(',', ':')))
