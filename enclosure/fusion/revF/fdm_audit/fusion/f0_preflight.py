# Design-for-FDM audit of version 66 -- preflight. READ-ONLY (run with readOnly: true through the Fusion connector).
# Prints: document, version, modified flag, body count, visible bodies, AUD_* bodies, and the 14 guard volumes (mm3).
import adsk.core, adsk.fusion, time
GUARD = ['HOUSING_F_plate', 'HOUSING_F_front', 'SPKBOX_L', 'SPKBOX_R', 'FLOOR_PLATE', 'RESP_CARRIER', 'CRADLE_5807',
         'HOUSING_F_door', 'HOUSING_F_cap', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'SLAB_frame', 'GROMMET_usbc_F', 'BME_HOOD']

def run(_context: str):
    app = adsk.core.Application.get(); doc = app.activeDocument
    des = adsk.fusion.Design.cast(app.activeProduct); root = des.rootComponent; df = doc.dataFile
    print(time.strftime('%Y-%m-%d %H:%M:%S'), doc.name, 'version', df.versionNumber, 'of', df.latestVersionNumber, 'modified', doc.isModified)
    names = [b.name for b in root.bRepBodies]
    print('bodies', len(names), 'visible', sum(1 for b in root.bRepBodies if b.isLightBulbOn),
          'AUD', [n for n in names if n.startswith('AUD_')], '_v65', sum(1 for n in names if n.endswith('_v65')))
    for n in GUARD:                       # one body at a time: asking all 419 bodies for their volume in one call times out
        b = root.bRepBodies.itemByName(n)
        print('%s %.3f lumps %d' % (n, b.volume * 1000.0, b.lumps.count))
