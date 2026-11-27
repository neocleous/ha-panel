# Pictures for the instructions page, drawn as custom graphics over a hidden
# model. Nothing is added to the design and no version is saved.
#
# Three modes, set by the loader in MODE:
#   hide     record every body's light bulb and the three folders' bulbs in
#            out/bulbs.json, then turn off the bodies that are on
#   shots    render the shots of spec/<SPEC_NAME>.json not yet done, for at
#            most about 60 s; the custom graphics are deleted after each
#   restore  put every light bulb back as recorded
#
# A shot: name; grey (bodies in light grey: the unit as it stands); color
# ([body, [r,g,b], [dx,dy,dz] mm, optional lump index]); arrows
# ([[x0,y0,z0],[x1,y1,z1],[r,g,b], radius] mm); marks ([label, [x,y,z]] mm,
# projected and written to json in % of the picture); view ({dir, up, pad,
# focus or box}).
import adsk.core, adsk.fusion, os, json, math, time, datetime

BASE = os.path.expanduser("~/Documents/HA_panel_renders/instructions_page_v91")
SPEC = globals().get("SPEC_NAME", "sample")
MODE = globals().get("MODE", "shots")
UP = (0.0, math.sin(math.radians(12)), math.cos(math.radians(12)))

def V(a):
    return adsk.core.Vector3D.create(a[0], a[1], a[2])

def P(a):
    return adsk.core.Point3D.create(a[0] / 10, a[1] / 10, a[2] / 10)

def unit(v):
    n = math.sqrt(sum(c * c for c in v))
    return [c / n for c in v]

def cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def color(rgb, opacity=1.0):
    c = adsk.core.Color.create(rgb[0], rgb[1], rgb[2], 255)
    a = adsk.core.Color.create(int(rgb[0] * 0.45), int(rgb[1] * 0.45), int(rgb[2] * 0.45), 255)
    s = adsk.core.Color.create(90, 90, 90, 255)
    return adsk.fusion.CustomGraphicsBasicMaterialColorEffect.create(
        c, a, s, adsk.core.Color.create(0, 0, 0, 255), 20.0, opacity)

def log(line):
    open(os.path.join(BASE, "out", "p91_10_render_%s.txt" % SPEC), "a").write(line + "\n")

def run(_context: str):
    app = adsk.core.Application.get()
    des = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent
    vp = app.activeViewport
    state = os.path.join(BASE, "out", "bulbs.json")
    if MODE == "hide":
        rec = {"bodies": [b.isLightBulbOn for b in root.bRepBodies],
               "names": [b.name for b in root.bRepBodies],
               "folders": [root.isOriginFolderLightBulbOn, root.isSketchFolderLightBulbOn,
                           root.isConstructionFolderLightBulbOn],
               "style": int(vp.visualStyle)}
        if not os.path.exists(state):
            json.dump(rec, open(state, "w"))
        for b in root.bRepBodies:
            if b.isLightBulbOn:
                b.isLightBulbOn = False
        root.isOriginFolderLightBulbOn = False
        root.isSketchFolderLightBulbOn = False
        root.isConstructionFolderLightBulbOn = False
        vp.visualStyle = adsk.core.VisualStyles.ShadedVisualStyle
        log("hide %s" % datetime.datetime.now().isoformat())
        return
    if MODE == "restore":
        rec = json.load(open(state))
        for i, b in enumerate(root.bRepBodies):
            if rec["names"][i] != b.name:
                raise Exception("body order changed at %d" % i)
            if b.isLightBulbOn != rec["bodies"][i]:
                b.isLightBulbOn = rec["bodies"][i]
        (root.isOriginFolderLightBulbOn, root.isSketchFolderLightBulbOn,
         root.isConstructionFolderLightBulbOn) = rec["folders"]
        vp.visualStyle = rec["style"]
        os.rename(state, state + ".restored")
        log("restore %s modified %s" % (datetime.datetime.now().isoformat(), app.activeDocument.isModified))
        return
    t0 = time.time()
    tm = adsk.fusion.TemporaryBRepManager.get()
    spec = json.load(open(os.path.join(BASE, "spec", SPEC + ".json")))
    os.makedirs(os.path.join(BASE, "img"), exist_ok=True)
    bodies = {b.name: b for b in root.bRepBodies}
    donefile = os.path.join(BASE, "out", "p91_10_done_%s.txt" % SPEC)
    done = set(open(donefile).read().split()) if os.path.exists(donefile) else set()
    try:
        for shot in spec:
            if shot["name"] in done:
                continue
            if time.time() - t0 > 55:
                log("time: stopped before " + shot["name"])
                break
            t1 = time.time()
            grp = root.customGraphicsGroups.add()
            pts = []
            grey = color([176, 179, 184])
            cut = shot.get("cut")
            cutbox = None
            if cut:
                # keep the half-space on one side of a plane square to x, y or z
                ax = "xyz".index(cut["axis"])
                ctr = [0.0, -60.0, -50.0]
                ext = [400.0, 400.0, 400.0]
                ctr[ax] = cut["at"] + (100.0 if cut["keep"] == ">" else -100.0)
                ext[ax] = 200.0
                obb = adsk.core.OrientedBoundingBox3D.create(
                    P(ctr), V([1, 0, 0]), V([0, 1, 0]), ext[0] / 10, ext[1] / 10, ext[2] / 10)
                cutbox = tm.createBox(obb)

            def shown(b):
                if cutbox is None:
                    return b
                t = tm.copy(b)
                tm.booleanOperation(t, tm.copy(cutbox), adsk.fusion.BooleanTypes.IntersectionBooleanType)
                return t

            for n in shot.get("grey", []):
                b = bodies[n]
                g = grp.addBRepBody(shown(b))
                g.color = grey
                bb = b.boundingBox
                pts += [[bb.minPoint.x * 10, bb.minPoint.y * 10, bb.minPoint.z * 10],
                        [bb.maxPoint.x * 10, bb.maxPoint.y * 10, bb.maxPoint.z * 10]]
            for item in shot.get("color", []):
                n, rgb, off = item[0], item[1], item[2]
                b = bodies[n]
                src = b
                if len(item) > 3 and item[3] is not None:
                    src = tm.copy(b.lumps.item(item[3]))
                if shot.get("cutcolor"):
                    src = shown(src)
                g = grp.addBRepBody(src)
                g.color = color(rgb)
                m = adsk.core.Matrix3D.create()
                bb = src.boundingBox
                corners = [[x, y, z] for x in (bb.minPoint.x, bb.maxPoint.x)
                           for y in (bb.minPoint.y, bb.maxPoint.y) for z in (bb.minPoint.z, bb.maxPoint.z)]
                if len(item) > 4 and item[4]:
                    m.setWithArray(item[4])
                    for c in corners:
                        q = adsk.core.Point3D.create(c[0], c[1], c[2])
                        q.transformBy(m)
                        pts.append([q.x * 10, q.y * 10, q.z * 10])
                else:
                    m.translation = V([off[0] / 10, off[1] / 10, off[2] / 10])
                    for c in corners:
                        pts.append([c[0] * 10 + off[0], c[1] * 10 + off[1], c[2] * 10 + off[2]])
                g.transform = m
            for a in shot.get("arrows", []):
                p0, p1, rgb = a[0], a[1], a[2]
                d = [p1[i] - p0[i] for i in range(3)]
                ln = math.sqrt(dot(d, d))
                u = [c / ln for c in d]
                r = a[3] if len(a) > 3 else 1.6
                head = min(ln * 0.4, r * 6)
                mid = [p1[i] - u[i] * head for i in range(3)]
                cyl = tm.createCylinderOrCone(P(p0), r / 10, P(mid), r / 10)
                cone = tm.createCylinderOrCone(P(mid), r * 2.4 / 10, P(p1), 0.0001)
                for body in (cyl, cone):
                    g = grp.addBRepBody(body)
                    g.color = color(rgb)
                pts += [p0, p1]
            view = shot["view"]
            frame = pts
            if view.get("focus"):
                frame = []
                for n in view["focus"]:
                    bb = bodies[n].boundingBox
                    frame += [[bb.minPoint.x * 10, bb.minPoint.y * 10, bb.minPoint.z * 10],
                              [bb.maxPoint.x * 10, bb.maxPoint.y * 10, bb.maxPoint.z * 10]]
            if view.get("box"):
                frame = view["box"]
            lo = [min(p[i] for p in frame) for i in range(3)]
            hi = [max(p[i] for p in frame) for i in range(3)]
            corners = [[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
            tgt = [(lo[i] + hi[i]) / 2 for i in range(3)]
            dirv = unit(view["dir"])
            upv = unit(view.get("up", UP))
            right = unit(cross(upv, dirv))
            upv = unit(cross(dirv, right))
            xs = [dot([c[i] - tgt[i] for i in range(3)], right) for c in corners]
            ys = [dot([c[i] - tgt[i] for i in range(3)], upv) for c in corners]
            pad = view.get("pad", 1.10)
            w = (max(xs) - min(xs)) * pad
            h = (max(ys) - min(ys)) * pad
            cx = (max(xs) + min(xs)) / 2
            cy = (max(ys) + min(ys)) / 2
            tgt = [tgt[i] + right[i] * cx + upv[i] * cy for i in range(3)]
            cam = vp.camera
            cam.isSmoothTransition = False
            cam.cameraType = adsk.core.CameraTypes.OrthographicCameraType
            cam.target = P(tgt)
            cam.eye = P([tgt[i] + dirv[i] * 800.0 for i in range(3)])
            cam.upVector = V(upv)
            vw, vh = vp.width, vp.height
            aspect = vw / vh
            if w / h > aspect:
                h = w / aspect
            else:
                w = h * aspect
            cam.setExtents(w / 10, h / 10)
            vp.camera = cam
            vp.refresh()
            adsk.doEvents()
            W = shot.get("width", 1800)
            H = int(round(W * vh / vw))
            opt = adsk.core.SaveImageFileOptions.create(os.path.join(BASE, "img", shot["name"] + ".png"))
            opt.width = W
            opt.height = H
            opt.isBackgroundTransparent = True
            opt.isAntiAliased = True
            ok = vp.saveAsImageFileWithOptions(opt)
            marks = []
            for lab, p in shot.get("marks", []):
                v2 = vp.modelToViewSpace(P(p))
                marks.append({"label": lab, "x": round(100 * v2.x / vw, 2), "y": round(100 * v2.y / vh, 2)})
            json.dump({"name": shot["name"], "w": W, "h": H, "marks": marks},
                      open(os.path.join(BASE, "img", shot["name"] + ".json"), "w"))
            grp.deleteMe()
            done.add(shot["name"])
            open(donefile, "w").write("\n".join(sorted(done)))
            log("%s saved %s %dx%d in %.1f s" % (shot["name"], ok, W, H, time.time() - t1))
    finally:
        for g in list(root.customGraphicsGroups):
            g.deleteMe()
        vp.refresh()
