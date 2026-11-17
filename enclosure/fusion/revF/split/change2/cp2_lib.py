# change2/cp2_lib.py - loader and helpers of the posts / shadow gap / FDM strength pass (2026-11-17).
# WRITTEN AGAIN on 2026-11-18 from the bytecode of what ran in Fusion (names, constants, call order); the typed source was not kept and
# this file has NOT been run as it stands (README, lesson 205). The model was built by cp2_posts.py, cp2_vents.py and cp2_fix.py, which are as run.
import adsk.core, adsk.fusion, sys, os, json, struct, zlib, types, urllib.request

RAW = 'https://raw.githubusercontent.com/neocleous/ha-panel/%s/%s'
DOCS = 'd223ad333982c9d219732c7a5079d3d1ebcefde7'       # docs head at the start of the pass
KLIB = 'enclosure/fusion/revF/floor_plate/fusion/v5f_k_lib.py'      # blob ba85884
OUT = os.path.expanduser('~/Documents/HA_panel_renders/posts-shadow-gap')


def load():                                             # v5f_k_lib as sys.modules['cp2k'] with its own cache; cp2 = this pass's module
    src = urllib.request.urlopen(RAW % (DOCS, KLIB), timeout=25).read().decode('utf-8').replace("'v5f_h_cache'", "'cp2_cache'")
    k = types.ModuleType('cp2k'); exec(compile(src, KLIB, 'exec'), k.__dict__); sys.modules['cp2k'] = k

    class KX(k.K):                                      # binds to the main document by name, so that another document may be the active one
        def __init__(self):
            self.app = adsk.core.Application.get(); self.doc = None
            docs = self.app.documents
            for i in range(docs.count):
                d = docs.item(i)
                if d.name == k.DOC:
                    self.doc = d
            if self.doc is None:
                raise RuntimeError('document not open: ' + k.DOC)
            self.des = adsk.fusion.Design.cast(self.doc.products.itemByProductType('DesignProductType'))
            self.root = self.des.rootComponent
            self.tbm = adsk.fusion.TemporaryBRepManager.get(); self.mm = self.app.measureManager
    k.K0 = k.K; k.K = KX
    cp2 = types.ModuleType('cp2'); cp2.k = k; sys.modules['cp2'] = cp2
    return k, cp2


k = sys.modules.get('cp2k')


class KS(k.K0 if k else object):                        # my scratch document: unsaved, root attribute cp2/scratch, AUD_* copies for pictures only
    def __init__(self):
        self.app = adsk.core.Application.get(); self.doc = None
        docs = self.app.documents
        for i in range(docs.count):
            d = docs.item(i)
            if d.name == k.DOC:
                continue
            des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
            if des and des.rootComponent.attributes.itemByName('cp2', 'scratch'):
                self.doc = d; self.des = des
        if self.doc is None:
            raise RuntimeError('no scratch document')
        self.root = self.des.rootComponent
        self.tbm = adsk.fusion.TemporaryBRepManager.get(); self.mm = self.app.measureManager

    def active(self):
        if self.app.activeDocument != self.doc:
            self.doc.activate()


def appearance(Xs, lib_name, new_name, rgb=None):       # a library appearance copied into the scratch design, tinted if rgb is given
    a = Xs.des.appearances.itemByName(new_name)
    if a is None:
        src = None
        for lib in Xs.app.materialLibraries:
            src = lib.appearances.itemByName(lib_name)
            if src:
                break
        a = Xs.des.appearances.addByCopy(src, new_name)
    if rgb is not None:
        for p in a.appearanceProperties:
            c = adsk.core.ColorProperty.cast(p)
            if c and c.name == 'Color':
                c.value = adsk.core.Color.create(rgb[0], rgb[1], rgb[2], 255)
    return a


def put(Xs, tb, name, app=None, show=True):             # a temporary body into the scratch document under a name, replacing the old one
    old = Xs.root.bRepBodies.itemByName(name)
    if old:
        old.deleteMe()
    b = Xs.root.bRepBodies.add(tb); b.name = name
    if app:
        b.appearance = app
    b.isLightBulbOn = show
    return b


def shot(Xs, fname, w=1600, h=1200):
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    p = os.path.join(OUT, fname); vp = Xs.app.activeViewport; vp.refresh(); adsk.doEvents()
    ok = vp.saveAsImageFile(p, w, h)
    return ok, p, os.path.getsize(p) if os.path.exists(p) else None


def shot2(Xs, fname, w=1600, h=1200):                   # transparent background (set on white afterwards), anti-aliased
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    p = os.path.join(OUT, fname); vp = Xs.app.activeViewport; vp.refresh(); adsk.doEvents()
    o = adsk.core.SaveImageFileOptions.create(p); o.width = w; o.height = h; o.isBackgroundTransparent = True; o.isAntiAliased = True
    ok = vp.saveAsImageFileWithOptions(o)
    return ok, p, os.path.getsize(p) if os.path.exists(p) else None


def tint(Xs, name, rgb, base='Plastic - Matte (Gray)'):
    return appearance(Xs, base, name, rgb)


def look(Xs, tgt, v, dist=300.0, ext=5.0, up=(0, 0, 1)):    # orthographic view along world direction v onto world point tgt; ext = view extents (cm)
    v = k.unit(v)
    k.cam(Xs, (tgt[0] - v[0] * dist, tgt[1] - v[1] * dist, tgt[2] - v[2] * dist), tgt, ext=ext, up=up)


# ---------- data channel Mac -> workspace: a payload packed into a grey PNG, read back with the Filesystem connector (offline/chan.py) ----------
def png_bytes(payload, width=2048):
    z = zlib.compress(payload, 9); data = struct.pack('>Q', len(z)) + z
    rows = (len(data) + width - 1) // width; data += b'\x00' * (rows * width - len(data))
    raw = b''.join(b'\x00' + data[i * width:(i + 1) * width] for i in range(rows))

    def chunk(tag, body):
        return struct.pack('>I', len(body)) + tag + body + struct.pack('>I', zlib.crc32(tag + body) & 0xffffffff)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, rows, 8, 0, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b'')


def send(fname, payload):
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    p = os.path.join(OUT, fname)
    with open(p, 'wb') as f:
        f.write(png_bytes(payload))
    return p, len(payload)


def mesh_pack(items, tol=0.002):                        # [(name, body)] -> header (json) + vertices (float32, design cm) + triangles (int32); offline/geo.py unpacks
    head = []; blobs = []
    for name, b in items:
        c = b.meshManager.createMeshCalculator(); c.surfaceTolerance = tol
        m = c.calculate()
        v = struct.pack('<%df' % (m.nodeCount * 3), *m.nodeCoordinatesAsFloat); t = struct.pack('<%di' % (m.triangleCount * 3), *m.nodeIndices)
        head.append({'name': name, 'nv': m.nodeCount, 'nt': m.triangleCount}); blobs.append(v + t)
    h = json.dumps({'items': head}).encode('utf-8')
    return struct.pack('>I', len(h)) + h + b''.join(blobs)
