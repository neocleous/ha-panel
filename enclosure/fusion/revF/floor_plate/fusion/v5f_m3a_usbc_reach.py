# rev F m3a (2026-11-13): ribbon pass - read-only: can the ADT USB-C plug be pulled out of the ReSpeaker and put back with the display module in
# place, through the door opening (door off)? Asked by Daniel 2026-11-13 08:39: unplug the lead for service instead of stowing its spare.
#   k = v5f_k, m = v5f_m. Board frame (u toward the left-speaker side, v up the board, w toward the door; w 0 = the main board's door-side face).
#   sweep()   the plug's envelope moved out of the socket along +u in steps: mm3 inside every other body
#   fingers() the reach standard's rounded fingertip (16 across, 60 long) lying against the plug's two flat faces, in the standard's six directions
#   jaws()    a pair of pliers or tweezers jaws on the two narrow edges of the sleeve, straddling the cable, in the same directions; then moved out with the plug
import math
OWN = ('RESP_usbc_plug_env', 'LEAD_USB_RESP')
PL = {'u0': 43.70, 'v': 7.21, 'w0': -7.29,          # the sleeve's socket-side face, the plug's centre line (stand-off 0.92 as in block 1)
      'un': 45.50, 'um': 47.10,                      # far faces of the narrow and the middle part of the sleeve
      'wn': (4.26, 11.67), 'hn': 2.70,               # the narrow part: along w, half width along v
      'out': 7.12}                                   # length of shell in the socket
DIRS = {'straight': (0, 1, 0), 'down25': (0, 0.9063, -0.4226), 'down45': (0, 0.7071, -0.7071), 'up25': (0, 0.9063, 0.4226), 'to-x25': (-0.4226, 0.9063, 0),
        'to+x25': (0.4226, 0.9063, 0)}               # slab frame (x, depth, Zd): the standard's six, all toward the door


def wdir(q):                                         # slab-frame direction -> world
    return m.unit((q[0], -k.C * q[1] - k.S * q[2], -k.S * q[1] + k.C * q[2]))


def hits(X, tool, obs, eps=0.02):                    # {obstacle: mm3} of a temporary tool inside the obstacles
    out = {}; qt = m.bb6(tool)
    for name, bodies in obs:
        v = 0.0
        for b in bodies:
            if m.bgap(qt, m.bb6(b)) > 0.01:
                continue
            tb = b if b.isTemporary else k.tcopy(X, b.name)
            v += X.xv(tool, tb)
        if v > eps:
            out[k.sn(name)] = round(v, 1)
    return out


def obstacles(X):                                    # every current body and lead but the plug, its cable and the door (off in service)
    return m.obstacles(X, skip=OWN + ('HOUSING_F_door',))


def sweep(X, obs, steps=(0.0, 2.0, 4.0, 6.0, 7.2, 8.5, 10.0)):
    out = {}
    for s in steps:
        tb = X.tbm.copy(X.body('RESP_usbc_plug_env'))
        if s:
            X.move(tb, dx=s)
        out[s] = hits(X, tb, obs)
    return out


def finger(X, c, a, r=8.0, L=60.0):                  # ball of radius r centred at c (world), the finger behind it along a (world)
    t = X.cyl(c, m.add(c, m.mul(a, L - r)), r)
    return X.uni(t, X.sph(c, r))


def fingers(X, obs, shift=0.0):                      # the ball lies against a flat face of the sleeve; its centre is r + 0.1 from the face
    out = {}
    for lab, u, ws in (('thumb on the face toward the middle', PL['u0'] - 8.1, (9.0, 11.0, 13.0)),
                       ('finger on the face toward the side wall', PL['un'] + 8.1, (8.0, 10.0, 12.0))):
        for w in ws:
            c = k.B2W(u + shift, PL['v'], w)
            row = {}
            for dn, q in DIRS.items():
                row[dn] = hits(X, finger(X, c, wdir(q)), obs)
            out['%s, w %.0f' % (lab, w)] = row
    return out


def jaws(X, obs, th=2.5, wd=3.0, L=70.0, shift=0.0, w0=5.0):     # two jaws th thick (along v), wd wide (along u), from w0 toward the door
    out = {}
    uc = (PL['u0'] + PL['un']) / 2.0 + shift
    for dn, q in DIRS.items():
        a = wdir(q); tool = None
        ux = m.bdir(1, 0, 0); ay = m.unit(m.sub(ux, m.mul(a, m.dot(ux, a))))
        for sg in (-1.0, 1.0):
            p0 = k.B2W(uc, PL['v'] + sg * (PL['hn'] + 0.2 + th / 2.0), w0)
            j = X.obox(m.add(p0, m.mul(a, L / 2.0)), a, ay, L, wd, th)
            tool = j if tool is None else X.uni(tool, j)
        out[dn] = hits(X, tool, obs)
    return out


# Results on version 62 (2026-11-13, read-only; hard bodies only, key paths left out; mm3 of the tool inside a body):
#   sweep: the plug leaves the socket freely: its own socket only up to 6.0 out, nothing from 7.2 to 10.0 out.
#   straight behind the plug's door-side end the shell's door frame begins 20.9 away (a lip 1.5 thick): the plug sits behind the frame's left edge.
#   fingers, plate unit in place: on the face toward the middle free of hard bodies from 'down25' and 'to-x25' (the ribbon is touched, 2 to 47);
#     on the face toward the side wall the shell blocks all six directions (196 to 557). No pinch with two fingertips.
#   jaws on the rigid part of the plug (the sleeve over its board: 7.4 across, w -2.5 .. 4.3, 3.3 of it above the main board's face), plate unit in place:
#     plug seated: free from 'to-x25' only. Plug 3.6 out: shell 2.6 (pliers 2.5 x 3.0), 0.1 (tweezers 1.5 x 2.0). 7.2 out: shell 13.8 / 5.6.
#     'down45' meets the left speaker box (24.7 / 8.0). A stick 6 across cannot reach the side-wall face from any of the six directions (shell 43 to 85).
#   jaws with the plate unit's bodies and the leads unplugged before it moves left out (the unit lowered out of the tool's way; not run with the box at
#     exactly 30 lower): 'down45' seated: ribbon only (9.9 / 2.4); 3.6 and 7.2 out: free, pliers and tweezers.
