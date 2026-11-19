# pf67_9b_camera (block 6). READ-ONLY (connector readOnly: true); writes nothing. Prints the active viewport's camera, the
#   document's modified flag and version, to compare with the preflight's record (the closing check found the camera moved).


def run(_context):
    X = R2Ctx(); vp = X.app.activeViewport; cm = vp.camera
    pre = json.load(open(os.path.join(R2_DIR, 'data', 'pf67_0_preflight.json')))['camera']
    now = {'eye': [round(cm.eye.x, 4), round(cm.eye.y, 4), round(cm.eye.z, 4)],
           'target': [round(cm.target.x, 4), round(cm.target.y, 4), round(cm.target.z, 4)],
           'up': [round(cm.upVector.x, 4), round(cm.upVector.y, 4), round(cm.upVector.z, 4)], 'style': vp.visualStyle,
           'ortho': cm.cameraType, 'extents': round(cm.viewExtents, 3)}
    df = X.doc.dataFile
    print(json.dumps({'t': time.strftime('%H:%M:%S'), 'preflight': pre, 'now': now, 'doc': [df.versionNumber, df.latestVersionNumber, X.doc.isModified]}))
