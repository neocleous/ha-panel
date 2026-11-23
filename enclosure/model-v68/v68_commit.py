# Version 67 -> 68: the seven new screws as one body, and the steps that put the new bodies into the
# document, save it and export the archive. Run only after the parts are built and checked
# (v68_cap, v68_door, v68_shell). commit() and save() change the document.
import sys, os

v = sys.modules['v68']; k = v.k; G = v.G

CHANGED = ['HOUSING_F_cap', 'HOUSING_F_door', 'HOUSING_F_front', 'GROMMET_usbc_F', 'BME_HOOD',
           'VEML_env', 'LEAD_MIC_L', 'LEAD_MIC_R']
NEW = [('MIC_CLAMP_L', 'TOUCH_CLIP_L'), ('MIC_CLAMP_R', 'TOUCH_CLIP_R'), ('SCREWS_M2x6_env', 'DRV_screw_heads_env')]
NAME = 'rev F WIP %s g23: screws and clamps instead of staking (D270, D280-D287, D307), checks (D274) - not for print'
ARCHIVE = '~/Documents/HA Panel v5 - tapered revF-g23.f3d'


def screw(X, head, toward_tip):
    """An M2 x 6 flat-head screw: head 3.8 across and 1.2 high, shank 2.0 across, 6.0 long over all."""
    d = k.unit(toward_tip)

    def at(s):
        return (head[0] + s * d[0], head[1] + s * d[1], head[2] + s * d[2])
    t = X.cyl(at(0.0), at(0.3), 1.9)
    X.uni(t, X.cyl(at(0.3), at(1.2), 1.9, 1.0))
    X.uni(t, X.cyl(at(1.2), at(6.0), 1.0))
    return t


def screw_list():
    """[(name, centre of the head's top face, direction from head to tip)] of the seven new screws."""
    cp = sys.modules['v68_cap']; dr = sys.modules['v68_door']; sh = sys.modules['v68_shell']
    rows = []
    for sx, side in ((1.0, 'left'), (-1.0, 'right')):
        rows.append(('strip clamp, ' + side, (sx * cp.SCREW[0], cp.SCREW[1], cp.Z0), (0.0, 0.0, 1.0)))
        h, u = dr.head(sx * dr.X_SCREW)
        rows.append(('grommet, ' + side, h, (-u[0], -u[1], -u[2])))
    for sg, side in ((1.0, 'screen side'), (-1.0, 'door side')):
        h, u = sh.radar_head(sg)
        rows.append(('radar, ' + side, h, (-u[0], -u[1], -u[2])))
    h, u = sh.hood_head()
    rows.append(('hood', h, (-u[0], -u[1], -u[2])))
    return rows


def screws(X):
    t = None
    for name, h, d in screw_list():
        s = screw(X, h, d)
        t = s if t is None else X.uni(t, s)
    G['SCREWS_M2x6_env'] = t
    return t


def commit(X):
    """Each changed body becomes a hidden ..._v67 copy and the new body takes its name; the new parts are added."""
    for n in CHANGED:
        X.swap(n, G[n], v.BACKUP)
    for n, like in NEW:
        b = X.body(like)
        X.add(G[n], n, like=b, show=b.isLightBulbOn)
    return X.state()


def save(X, date):
    X.doc.save(NAME % date)
    return X.state()


def export(X):
    path = os.path.expanduser(ARCHIVE)
    em = X.des.exportManager
    em.execute(em.createFusionArchiveExportOptions(path))
    return path, os.path.getsize(path)
