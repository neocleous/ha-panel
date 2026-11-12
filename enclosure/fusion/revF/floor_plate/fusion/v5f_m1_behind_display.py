# rev F m1 (2026-11-12): ribbon pass, block 1 - both flat leads behind the display. Run through the loader with k = v5f_k, m = v5f_m.
#   plug()    the ADT USB-C end at the ReSpeaker, from the sheet's tables (m.usbc)
#   cable()   the flat USB cable from the sleeve's end: straight toward the door on edge, then its fold down (no bends)
#   ribbon()  the DSI ribbon from the display's connector: bend toward the door, two creases that step it down under the plug's
#             sleeve, through the slot beside the board's edge, two bends that take it toward the middle, then its crease down
#   Parameters are in PV; every length is board frame mm unless said. Assumed values are marked.
import math

PV = {
    'g': 0.92,          # how far the sleeve's face stands off the socket's face: 7.12 (maker's model) - 6.20 (USB-C reference shell length); assumed
    'bt': 1.6,          # plug board thickness: the drawing's (the model has 0.8); the larger
    'cW': 5.25, 'ct': 1.44,     # cable section (maker's model)
    'cfold': 28.1,      # w of the centre of the cable's fold down: its drop then lies at y -52.6 .. -57.9, behind the left box
    'cgap': 1.0,        # air between the two layers of a fold in the cable; assumed
    'rW': 16.0, 'rt': 0.4,      # ribbon section along its run; assumed by the usual rule
    'rw0': -24.35,      # w at which the ribbon leaves the display's connector: mid-height of the connector's envelope; assumed
    'rin': 3.0,         # ribbon inside the connector
    'rs0': 1.45,        # straight out of the connector before the first bend
    'R1': 2.5,          # radius of the bend toward the door; assumed
    'c1': -11.0,        # w of the first crease's centre
    'step': 8.0,        # how far the two creases step the ribbon down
    'rgap': 0.4,        # air between the two layers of a crease in the ribbon; assumed
    'wa': 5.0,          # w at which the ribbon starts to turn toward the middle
    'R2': 3.0,          # radius of the two bends behind the board; assumed
    'ud': 36.0,         # u of the ribbon's run toward the door after those bends (x_rel 38.5)
    'c3': 25.5,         # w of the third crease's centre: the drop then lies at y -57.55 .. -41.55, the Pi connector's
    'drop': 12.0,       # how much of each drop is drawn in block 1
}
CONN = (39.35, 44.25, -11.48, 11.32, -25.3, -23.4)   # LCD_DSI_conn_d9.3, board frame, read at version 60
DOWN = 39.0             # crease angle that turns a lead heading toward the door (12 deg below level) straight down


def plug(X, pv=PV):
    return m.usbc(X, pv['g'], pv['bt'])


def cable(X, pv=PV, full=True):
    P, d, w = m.usbc_start(pv['g'])
    s = m.Strip(X, P, d, w, pv['cW'], pv['ct'], 'usb')
    s.S(pv['cfold'] - (m.UC['w'] + 18.96), 'top run')
    if full:
        s.F(DOWN, -1, +1, pv['cgap'], 'fold down')   # turns toward -v; the drop lies one layer toward the middle
        s.S(pv['drop'], 'drop')
    return s.end()


def ribbon(X, pv=PV, full=True):
    vc = (CONN[2] + CONN[3]) / 2.0
    P = k.B2W(CONN[1] - pv['rin'], vc, pv['rw0'])
    s = m.Strip(X, P, m.bdir(1, 0, 0), m.bdir(0, 1, 0), pv['rW'], pv['rt'], 'dsi')
    s.S(pv['rin'], 'in the connector').S(pv['rs0'], 'out of the connector')
    s.B(90, pv['R1'], 'bend toward the door')
    s.S(pv['c1'] - (pv['rw0'] + pv['R1']), 'on edge 1')
    s.F(45, -1, +1, pv['rgap'], 'crease 1')          # heading down the display, second layer toward the middle
    s.S(pv['step'], 'step')
    s.F(45, -1, -1, pv['rgap'], 'crease 2')          # heading toward the door again, third layer toward the middle
    s.S(pv['wa'] - pv['c1'], 'on edge 2')            # under the plug's sleeve and past the board's side edge
    s.B(90, pv['R2'], 'bend toward the middle')
    u_now = k.W2B(*s.P)[0]
    s.S(u_now - (pv['ud'] + pv['R2']), 'toward the middle')
    s.B(-90, pv['R2'], 'bend toward the door 2')
    w_now = k.W2B(*s.P)[2]
    s.S(pv['c3'] - w_now, 'on edge 3')
    if full:
        s.F(DOWN, -1, -1, pv['rgap'], 'crease 3')
        s.S(pv['drop'], 'drop')
    return s.end()


def report(s):                                       # the stations of a strip in the board frame and in the world
    out = []
    for lab, op, L, P, d, w in s.log:
        out.append('%-24s %-3s L %6.1f  B %s  W %s' % (lab, op, L, m.r2(k.W2B(*P)), P))
    return '\n'.join(out)
