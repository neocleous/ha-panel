# Version 68 -> 69: four corrections that the checks on version 68 asked for.
#
# 1. BME680 hood and its boss on the shell. At version 68 the screw's line ran so close to the hood's
#    side plate that the boss had to be cut away beside it: the wall round the pilot fell to about 1.25,
#    and the screw's last 1.15 was threaded into the tray's thin end wall. Lifted off its pegs and moved
#    toward the middle, the hood's side plate also caught the boss.
#    Now the boss is a plain round one, 6 across and 4.45 long (2.9 before): the whole thread lies in the
#    boss and the pilot stops at the wall's face. The ear moves out with it. Below the ear the hood's side
#    plate ends 1.75 short of the end wall's outer face, with its corner toward the wall broken 0.3,
#    so the boss keeps 2.0 of wall or more all round and the lifted hood passes it.
#    The flat and the gusset that version 68 had under the boss are left out: they were drawn for a shell
#    printed standing on its floor. The shell prints lying on its chin (world y is the print's height),
#    where they would lie sideways and only add to the faces that look at the bed.
# 2. Radar: the two blocks beside the board are 0.6 taller, so the pilots keep 1.6 of wall or more to their ends.
# 3. Supply module on the main board: its 13 pins are drawn 3.0 toward +v, as on board rev 3.3.
#
# Loaded into Fusion's Python as the module "v69", after "c3k", "c3", "v68", "v68_shell" and "v68_commit".
# Lengths in mm. build() makes temporary bodies only; commit(), save() and export() change the document.
import sys, os
import adsk.core

v = sys.modules['v68']; k = v.k
sh = sys.modules['v68_shell']
G = k.c.setdefault('v69', {})      # name -> the new temporary body of a changed part
BACKUP = '_v68'                    # suffix of the hidden copy kept of every body changed here
FROM = '_v67'                      # the shell and the hood are made again from their version-67 copies


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


LB = 4.45                          # the hood boss's length
TRIM = 1.75                        # below the ear the hood's side plate ends this far short of the end wall's outer face
BREAK = 0.3                        # ... and the corner of that end toward the wall is broken by this much at 45 degrees
BLOCK_TOP = 123.0                  # top of the radar blocks (122.4 at version 68)
PIN_SHIFT = 3.0                    # the supply module's pins, toward +v
MORE = LB - sh.H_BOSS              # how far the ear and the screw move out along the screw's line
OUT_L = MORE * dot(sh.HU, sh.LW)   # the same move, measured square to the wall
OUT_N = MORE * dot(sh.HU, sh.HN)   # ... and square to the hood's side plate
ALONG = MORE / dot(sh.HU, sh.LW)   # ... and along the side plate
NAME = 'rev F WIP %s g24: hood boss and side plate, radar blocks, supply module pins as rev 3.3 (checks on version 68) - not for print'
ARCHIVE = '~/Documents/HA Panel v5 - tapered revF-g24.f3d'
CHANGED = ['HOUSING_F_front', 'BME_HOOD', 'MAIN_PS1', 'SCREWS_M2x6_env']


def hp(t, side=0.0, dz=0.0):
    """A point on the hood screw's line: t from the wall's face toward the head; side along HT; dz up."""
    return sh.hp(t, side, dz)


def hood_head():
    """Centre of the head's top face, and the direction from the tip to the head."""
    return hp(LB + sh.H_GAP + sh.H_EAR), sh.HU


def along(p, u, s):
    return (p[0] + s * u[0], p[1] + s * u[1], p[2] + s * u[2])


# ---------- the shell ----------
def boss_tools(X):
    """What is added to the shell for the hood's boss, and what is cut out of it."""
    a = X.cyl(hp(-0.8), hp(LB), 3.0)
    # none of it in the lane of the hood's side plate, up to 0.4 before that plate's new end
    X.dif(a, sh.hood_slab(X, -3.0, 0.4 - TRIM, sh.SIDE[0] - 0.05, sh.SIDE[0] + 4.0, 78.0, 94.0))
    c = X.cyl(hp(LB + 0.3), hp(0.0), 0.8)                                     # pilot, 1.6 across: it stops at the wall's face, 0.4 beyond the screw's tip
    X.uni(c, X.cyl(hp(LB + 0.1), hp(LB - 0.3), 1.2, 0.8))                     # 0.3 x 45 degree entry
    return a, c


def block_tops(X):
    """The extra 0.6 on top of the two radar blocks. On the screen side it stops 0.2 short of the block's outer
    face, so that it stays as far from the screen plate, which leans in over it, as the block was (0.6)."""
    t = None
    for sg in (1.0, -1.0):
        dmin = -5.2 if sg > 0 else -6.6
        b = sh.rbox(X, sg * 10.1, sg * (11.6 if sg > 0 else 11.8), dmin, 2.0, 122.3, BLOCK_TOP)
        t = b if t is None else X.uni(t, b)
    return t


def shell(X):
    ra, rc = sh.radar_tools(X)
    ha, hc = boss_tools(X)
    add = X.uni(X.uni(ra, block_tops(X)), ha)
    cut = X.uni(rc, hc)
    t = X.tbm.copy(X.body('HOUSING_F_front' + FROM))
    X.uni(t, add)
    X.dif(t, cut)
    G['HOUSING_F_front'] = t
    return t


# ---------- the hood ----------
def hood(X):
    t = X.tbm.copy(X.body('BME_HOOD' + FROM))
    hd, u = hood_head()
    m = (hd[0] - 0.5 * sh.H_EAR * u[0], hd[1] - 0.5 * sh.H_EAR * u[1])
    up = (0.0, 0.0, 1.0)
    # the ear: a plate square to the screw in front of the boss, 6.1 wide round the screw (z 96.95 to 103.5) ...
    ear = X.obox((m[0], m[1], 100.225), sh.HT, up, 6.1, 6.55, sh.H_EAR)
    # ... hung from the top plate by its room-side part
    X.uni(ear, X.obox((m[0] + 1.225 * sh.HT[0], m[1] + 1.225 * sh.HT[1], 106.2), sh.HT, up, 3.65, 5.6, sh.H_EAR))
    # the top plate drawn out over the ear, and the side plate's end drawn out to it above the boss
    X.uni(ear, sh.hood_slab(X, 0.9, 4.6 + OUT_L, -93.4 + OUT_N, -89.2 + OUT_N, sh.TOP[0], sh.TOP[1]))
    X.uni(ear, sh.hood_slab(X, -0.5, 2.2 + ALONG, sh.SIDE[0], sh.SIDE[1], 91.13, 95.78))
    # nothing of it beyond the ear's outer face, nor above the top plate
    o = along(hd, u, 5.0)
    X.dif(ear, X.obox((o[0], o[1], 103.0), sh.HT, up, 40.0, 40.0, 10.0))
    top0 = tuple(sh.L_T0 * sh.LW[i] - 92.4 * sh.HN[i] + (sh.TOP[1] + 5.0) * sh.HA[i] for i in range(3))
    X.dif(ear, X.obox(top0, sh.LW, sh.HN, 40.0, 40.0, 10.0))
    X.uni(t, ear)
    X.dif(t, X.cyl(along(hd, u, 1.0), along(hd, u, -3.0), 1.1))               # screw clearance, 2.2 across
    X.dif(t, X.cyl(along(hd, u, 0.1), along(hd, u, -1.1), 2.3, 1.1))          # countersink, head flush
    # below the ear the side plate ends TRIM short of the end wall's outer face
    X.dif(t, sh.hood_slab(X, -TRIM, 0.6, sh.SIDE[0] - 0.3, sh.SIDE[1] + 0.3, 76.0, 91.13))
    # that end's corner toward the wall, broken at 45 degrees (only the side plate is cut)
    q = 0.5 ** 0.5
    ax = tuple(q * (sh.LW[i] + sh.HN[i]) for i in range(3))                   # along the broken corner's face; the box's height then points out of the corner
    l = -TRIM - BREAK / 2.0 + 0.5 * q + sh.L_T0; n = sh.SIDE[0] + BREAK / 2.0 - 0.5 * q
    cut = X.obox(tuple(l * sh.LW[i] + n * sh.HN[i] + 83.565 * sh.HA[i] for i in range(3)), ax, sh.HA, 2.0, 15.13, 1.0)
    X.sec(cut, sh.hood_slab(X, -TRIM - 1.0, 0.1 - TRIM, sh.SIDE[0] - 0.3, sh.SIDE[1] + 0.3, 76.0, 91.13))
    X.dif(t, cut)
    G['BME_HOOD'] = t
    return t


# ---------- the supply module's pins ----------
def supply_module(X):
    """The 13 pins moved PIN_SHIFT toward +v (board frame); the module's block stays where it is."""
    old = X.body('MAIN_PS1')
    t = X.tbm.copy(old)
    zone = X.bbox(-37.5, 14.2, -0.75, 0.15, -4.7, -0.005)                     # the pins: everything of the body below its block, whose underside lies at w -0.005
    pins = X.tbm.copy(zone)
    X.sec(pins, X.tbm.copy(old))
    X.dif(t, zone)
    a = k.Bp(0.0, 0.0, 0.0); b = k.Bp(0.0, PIN_SHIFT, 0.0)
    m = adsk.core.Matrix3D.create()
    m.translation = adsk.core.Vector3D.create(b.x - a.x, b.y - a.y, b.z - a.z)
    X.tbm.transform(pins, m)
    G['MAIN_PS1_pins'] = X.tbm.copy(pins)                                     # kept for the checks; not a body of the model
    X.uni(t, pins)
    G['MAIN_PS1'] = t
    return t


# ---------- the seven new screws, with the hood's screw at its new place ----------
def screw_list():
    vc = sys.modules['v68_commit']
    rows = [r for r in vc.screw_list() if r[0] != 'hood']
    h, u = hood_head()
    rows.append(('hood', h, (-u[0], -u[1], -u[2])))
    return rows


def screws(X):
    vc = sys.modules['v68_commit']
    t = None
    for name, h, d in screw_list():
        s = vc.screw(X, h, d)
        t = s if t is None else X.uni(t, s)
    G['SCREWS_M2x6_env'] = t
    return t


def build(X):
    shell(X); hood(X); supply_module(X); screws(X)
    return sorted(G)


# ---------- into the document ----------
def commit(X):
    """Each changed body becomes a hidden ..._v68 copy and the new body takes its name."""
    for n in CHANGED:
        X.swap(n, G[n], BACKUP)
    return X.state()


def save(X, date):
    X.doc.save(NAME % date)
    return X.state()


def export(X):
    path = os.path.expanduser(ARCHIVE)
    em = X.des.exportManager
    em.execute(em.createFusionArchiveExportOptions(path))
    return path, os.path.getsize(path)
