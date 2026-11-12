# rev F m2 (2026-11-13): ribbon pass, block 2 - the rest of both leads. Run through the loader with k = v5f_k, m = v5f_m and
#   s1 = the namespace of v5f_m1_behind_display.py (its PV and the leads' first parts).
#   ribbon()   the whole DSI ribbon: block 1's part, then the drop beside the left box, level above the Pi, down into the Pi's connector
#   cable()    the whole USB cable: block 1's top run and fold, the drop behind the left box, the spare as one flat oval roll
#              (the cable doubled and rolled: five lanes side by side), the fold at the bottom, through the box's rear opening to the plug
#   usba()     the ADT USB-A end in the Pi's lower blue port, from the sheet's tables (not from the maker's models)
#   spk()      the left speaker lead led round the two new leads (route as data)
# World mm unless said. Assumed values are marked.
import math

P2 = {
    # --- ribbon ---
    'zlev': 28.5,       # height of the level run above the Pi: 5.2 above the cooler's envelope, 3.8 below the Pi power cable's lap
    'R4': 3.0,          # radius of the two bends at the Pi; assumed
    'xpi': 11.8,        # x of the ribbon in the Pi's connector: the middle of the connector's body (x 10.3 .. 13.3); assumed
    'zpi': 13.5,        # top of the Pi's connector, read from the model
    'rin': 3.0,         # ribbon inside the connector; assumed
    'Wpi': 11.5,        # width of the ribbon's 22-way end; assumed by the usual rule
    'Lpi': 15.0,        # length of the narrow end; assumed (the maker's picture gives no widths)
    'Lr': 200.0,        # the ribbon's stock length, taken as its whole length, ends included; the shorter of the two stock lengths
    # --- cable ---
    'Lc': 300.0,        # length between the plugs' bodies that is drawn (the sheet: 288 to 300)
    'Rq': 5.5,          # radius of the bend from the drop into the row over the roll; assumed
    'sg': 0.5,          # drawn gap between two strands that lie beside each other in the roll (in the real roll they touch)
    'Ri': 3.0,          # radius of the roll's two innermost half turns; assumed (the room is 21.5 wide: with 4 the roll is 4 too wide)
    'zb': 17.5,         # height of the centres of the roll's lower turns (the outer one passes 1.6 above the plate's anchor)
    'zport': 13.93, 'yport': -28.95, 'xface': 45.1,   # the lower blue port: middle of its opening, face of the stack; read from the model
    'DA': 10.38,        # how much of the USB-A shell the port takes: reference mating depth of a USB 3 Standard-A socket; assumed
    'abt': 1.6,         # USB-A plug's board thickness: the drawing's (model 0.8); the larger
}


# ---------- ribbon ----------
def ribbon(X, pv=None, p2=P2, a=None):               # a = the height of the arch over the Pi's connector that takes up what a stock length leaves
    pv = pv or s1['PV']                              #     (None: solved for Lr; a < 0: no arch, the shortest way)
    if a is None:
        a = (p2['Lr'] - ribbon(Dry(), pv, p2, 0.0).L) / 2.0
    R = p2['R4']
    s = s1['ribbon'](X, pv, full=False)              # ... to the start of crease 3
    s.log.pop()                                      # its 'end' mark
    s.F(s1['DOWN'], -1, -1, pv['rgap'], 'crease 3')
    s.S(s.P[2] - (p2['zlev'] + R), 'drop')
    s.B(-90, R, 'bend toward the middle 2')
    zin = p2['zpi'] - p2['rin']
    if a < 0:
        s.S(s.P[0] - (p2['xpi'] + R), 'level above the Pi')
        s.B(90, R, 'bend down')
    else:
        s.S(s.P[0] - (p2['xpi'] + 3 * R), 'level above the Pi')
        s.B(-90, R, 'bend up')
        s.S(a, 'arch, up')
        s.B(180, R, 'arch, over')
    s.S(s.P[2] - zin - p2['Lpi'], 'down to the Pi')
    s.width(p2['Wpi'])
    s.S(s.P[2] - zin, 'into the Pi')
    s.a = a
    return s.end()


# ---------- cable ----------
class Dry:                                           # no solids: a strip built on this gives frames and lengths only
    def __getattr__(self, name):
        return lambda *a, **q: None


def lanes(pv, p2=P2):                                # the roll's five lanes (x of their centre lines) and its two radii
    p = pv['ct'] + p2['sg']                          # centre to centre of two strands that lie beside each other
    xc = p2['xface'] + 14.6 - p2['DA'] - pv['ct'] / 2.0      # the cable at the plug
    xF = xc + pv['ct'] + pv['cgap']                  # the last lane: one layer beside it, away from the Ethernet jack
    L1 = xF + p; C = L1 + 2 * p2['Ri']; R1 = C + 2 * p2['Ri']; R2 = R1 + p
    return {'p': p, 'xc': xc, 'F': xF, 'L1': L1, 'C': C, 'R1': R1, 'R2': R2, 'Ro': 2 * p2['Ri'] + p / 2.0}


def cable(X, pv=None, p2=P2, h=None, direct=False):
    pv = pv or s1['PV']
    if h is None and not direct:                     # the straight length of the roll's lanes that makes the cable Lc long
        L0 = cable(Dry(), pv, p2, 0.0).L
        h = (p2['Lc'] - L0) / 4.0
    q = lanes(pv, p2)
    s = s1['cable'](X, pv, full=False)
    s.log.pop()
    s.F(s1['DOWN'], -1, +1, pv['cgap'], 'fold down')
    if direct:                                       # the shortest way, for the record: down, a step outward, down to the fold at the bottom
        dx = q['F'] - s.P[0]; R = 6.0
        a = math.degrees(math.acos(1.0 - dx / (2 * R)))
        s.S(s.P[2] - 100.0, 'drop').B(a, R, 'step out').B(-a, R, 'step back')
        s.S(s.P[2] - p2['zport'], 'lane F')
    else:
        zt = p2['zb'] + h; Re = q['Ro'] + q['p']          # the way in lies round the roll's upper end, one strand outside its outer turn
        s.S(s.P[2] - (zt + Re + p2['Rq']), 'drop')
        s.B(90, p2['Rq'], 'bend outward')
        s.S((q['R2'] - Re) - s.P[0], 'row')
        s.B(-90, Re, 'round the roll')
        s.S(s.P[2] - p2['zb'], 'lane 1 down')
        s.B(-180, q['Ro'], 'outer turn below')
        s.S(h, 'lane 2 up')
        s.B(-180, p2['Ri'], 'inner turn above')
        s.S(h, 'lane 3 down')
        s.B(180, p2['Ri'], 'inner turn below')
        s.S(h, 'lane 4 up')
        s.B(180, q['Ro'], 'outer turn above')
        s.S(s.P[2] - p2['zport'], 'lane 5 down')
    turn = 1 if m.dot(s.w, (0, 1, 0)) > 0 else -1    # the fold turns the cable toward the screen (+y) ...
    side = 1 if m.dot(s.n, (-1, 0, 0)) > 0 else -1   # ... and it goes on one layer toward the middle (-x)
    s.F(45, turn, side, pv['cgap'], 'fold at the bottom')
    s.S((p2['yport'] - 19.73) - s.P[1], 'to the plug')
    s.h = h
    return s.end()


# ---------- the ADT USB-A end (S3K / S3J: the two hands are mirror images; drawn with its cable toward the door) ----------
def usba(X, p2=P2):
    xf = p2['xface']; yc = p2['yport']; zc = p2['zport']; bt = p2['abt']
    xb = xf + 14.6 - p2['DA']                        # the board's port-side face
    def bx(a0, a1, e0, e1, hz):                      # along the plug a0..a1 from the board's port-side face (+ toward the port), exit e0..e1 from the
        return X.wbox(xb - a1, xb - a0, yc - e1, yc - e0, zc - hz, zc + hz)    # shell's centre (+ toward the cable = toward the door), half height hz
    plug = [['shell', bx(0.0, 14.6 - p2['DA'], -6.0, 6.0, 2.25)],              # the part of the shell that stands out of the port
            ['board', bx(-bt, 0.0, -7.51, 15.99, 3.0)],
            ['back wall', bx(-bt - 1.5, -bt, -6.0, 6.0, 0.75)],                # bare metal: the shell's back wall, 1.5 proud
            ['pin ends', bx(-bt - 1.0, -bt, -5.0, 5.0, 2.25)]]                 # bare metal: pin ends 1.0 proud; their place inside the shell's outline is assumed
    sleeve = [['sleeve wide', bx(-bt - 0.49, 1.50, 8.25, 16.75, 3.365)],
              ['sleeve narrow', bx(-0.48, 1.50, 16.70, 19.73, 2.845)],
              ['cable on the board', bx(0.0, 1.44, 6.0, 19.73, 2.625)]]
    return plug, sleeve, xb


# ---------- the left speaker lead, moved clear of the two new leads (nodes as in k3_routes.json) ----------
SPK = [1.6, [['B', 38.75, -25, 9.8], ['B', 38.75, -25.5, 17.5], ['B', 39, -31, 18.5], ['W', 43.5, -49.0, 58.0], ['W', 43.6, -53.5, 55.0],
             ['W', 47.5, -61.0, 50.0], ['W', 54.0, -61.5, 42.0], ['W', 62.0, -61.5, 33.0], ['W', 62, -54, 30]]]


def rope(X, r, nodes):                               # as v5f_k3a_leads.py
    def pt(n):
        return k.Bp(n[1], n[2], n[3]) if n[0] == 'B' else (k.Dp(n[1], n[2], n[3]) if n[0] == 'S' else k.Wp(n[1], n[2], n[3]))
    ps = [pt(n) for n in nodes]; segs = []
    for i in range(len(ps) - 1):
        t = X.tbm.createCylinderOrCone(ps[i], r / 10.0, ps[i + 1], r / 10.0)
        if i > 0:
            X.uni(t, X.tbm.createSphere(ps[i], (r + 0.05) / 10.0))
        segs.append(t)
    while len(segs) > 1:
        nxt = [X.uni(segs[i], segs[i + 1]) for i in range(0, len(segs) - 1, 2)]
        if len(segs) % 2:
            nxt.append(segs[-1])
        segs = nxt
    L = sum(ps[i].distanceTo(ps[i + 1]) for i in range(len(ps) - 1)) * 10.0
    return segs[0], round(L, 1)


def report(s):
    return s1['report'](s)


NEW = ('LEAD_DSI', 'LEAD_USB_RESP', 'RESP_usbc_plug_env', 'USBA_plug_env', 'USBA_cable_env', 'LEAD_SPK_L')    # what this pass draws or replaces


def solids(X, pv=None, p2=P2):                       # block 2's bodies as temporary solids
    cb = cable(X, pv, p2); rb = ribbon(X, pv, p2); pl, sl, xb = usba(X, p2); sp, Ls = rope(X, *SPK)
    return {'LEAD_USB_RESP': cb.solid(), 'LEAD_DSI': rb.solid(), 'USBA_plug_env': m.join(X, pl + sl), 'LEAD_SPK_L': sp}, cb, rb, pl, sl, Ls


def commit(X, pv=None, p2=P2):                       # model change: the bodies replace the present ones (those of version 60 stay hidden as <name>_v60)
    sol, cb, rb, pl, sl, Ls = solids(X, pv, p2)
    for name, tb in sol.items():
        if tb.lumps.count != 1:
            raise RuntimeError('%s has %d lumps' % (name, tb.lumps.count))
    out = {}
    for name, tb in sol.items():
        b = m.lead(X, name, tb)
        out[name] = round(b.volume * 1000.0, 1)
    old = X.body('USBA_cable_env')                   # the round cable's stub at the plug: the flat cable is LEAD_USB_RESP itself
    if old is not None:
        X.retire(old, '_v60'); out['USBA_cable_env'] = 'retired'
    return out, round(cb.L, 2), round(rb.L, 2), Ls
