import os
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')) + os.sep
import pcb, rnet, math
P = ROOT
def ipc2221(I, w_mm, t_um=35.0, external=True):
    """IPC-2221 (the old MIL-STD-275 chart fit): I = k dT^0.44 A^0.725, A in square mils; returns dT in K."""
    A = (w_mm / 0.0254) * (t_um / 25.4)
    k = 0.048 if external else 0.024
    return (I / (k * A ** 0.725)) ** (1 / 0.44)
if __name__ == '__main__':
    print('IPC-2221 rise, outer layer 35 um:')
    for w, I, what in ((0.6, 2.5, 'neck into one pin pair, half of 5 A'), (0.6, 5.0, 'neck, all 5 A in one pair'), (0.4, 1.25, 'link A-B pin, quarter of 5 A'),
                       (1.4, 5.0, 'back track 1.4'), (2.0, 5.0, 'back track 2.0'), (1.5, 5.0, 'front track F2-LK1'), (0.8, 1.25, 'stub at F2, quarter'),
                       (1.4, 4.0, '1.4 at the bounded 4.0 A'), (0.6, 2.0, 'neck at 4.0 A total'), (1.4, 2.3, '1.4 at the bench load 2.3 A'), (0.6, 1.15, 'neck at 2.3 A total'),
                       (3.1, 5.0, 'planned 3.1'), (2.0, 5.0, 'planned bar 2.0'), (0.7, 2.5, 'planned 0.7 entry, half'),
                       (0.6, 2.83, '20 V inlet neck at design peak'), (0.6, 3.28, '20 V inlet neck at the current limit'), (0.6, 3.51, '20 V inlet neck at limit +7 %'), (0.6, 0.70, '20 V inlet neck nominal'),
                       (1.0, 2.83, '20 V socket to fuse 1.0'), (1.0, 3.51, '20 V socket to fuse at limit +7 %'), (1.8, 1.70, 'into the supply module at design peak'), (1.8, 2.96, 'into the supply module at its full load'),
                       (1.9, 3.51, 'planned inlet 1.9')):
        print('   %.1f wide, %.2f A: %5.1f K   (%s)' % (w, I, ipc2221(I, w), what))
    print('   inner 15.2 um, 11 wide +5V area at 5 A: %.1f K' % ipc2221(5.0, 11.0, 15.2, False))
    b = pcb.load(P + 'rev3/main-board-rev3.kicad_pcb')
    VE = '/20 V inlet and eFuse/VIN_EF'; VP = '/20 V inlet and eFuse/VIN_PIGTAIL'; NI = '/5 V supply and outputs/NID_VIN'
    n = rnet.Net(b, [VP], (30, 50, 46, 57.5), 0.05); print('rev 3  J1.1 -> F1.1: %.2f mohm' % (1e3 * n.solve([('pin', 'J1.1')], [('pad', 'F1', '1', 'F.Cu')])[0]))
    n = rnet.Net(b, [VE], (20, 44, 36, 57.5), 0.025)
    print('rev 3  F1.2 -> U1 pins 1-3: %.2f mohm' % (1e3 * n.solve([('pad', 'F1', '2', 'F.Cu')], [('pad', 'U1', '1', 'F.Cu'), ('pad', 'U1', '2', 'F.Cu'), ('pad', 'U1', '3', 'F.Cu')])[0]))
    n = rnet.Net(b, ['+20V'], (21, 0, 52, 52), 0.1)
    print('rev 3  U1 pins 18-20 -> L1.1 (layer 3 area): %.2f mohm' % (1e3 * n.solve([('pad', 'U1', '18', 'F.Cu'), ('pad', 'U1', '19', 'F.Cu'), ('pad', 'U1', '20', 'F.Cu')], [('pad', 'L1', '1', 'F.Cu')])[0]))
    n = rnet.Net(b, [NI], (10, 5, 28, 32), 0.05)
    print('rev 3  L1.2 -> PS1 pins 9, 10: %.2f mohm' % (1e3 * n.solve([('pad', 'L1', '2', 'F.Cu')], [('pin', 'PS1.9'), ('pin', 'PS1.10')])[0]))
    b2 = pcb.load(P + 'rev2.1/main-board.kicad_pcb')
    n = rnet.Net(b2, [VE], (28, 36, 60, 50), 0.05)
    print('rev 2.1 F1.2 -> U1 pins 1-3: %.2f mohm' % (1e3 * n.solve([('pad', 'F1', '2', 'F.Cu')], [('pad', 'U1', '1', 'F.Cu'), ('pad', 'U1', '2', 'F.Cu'), ('pad', 'U1', '3', 'F.Cu')])[0]))
    n = rnet.Net(b2, [NI], (8, 4, 38, 26), 0.05)
    print('rev 2.1 L1.2 -> PS1 pins 9, 10: %.2f mohm' % (1e3 * n.solve([('pad', 'L1', '2', 'F.Cu')], [('pin', 'PS1.9'), ('pin', 'PS1.10')])[0]))
    print('wire link 1.0 mm Cu, 7.62 long: %.3f mohm' % (1e3 * rnet.RHO * 7.62e-3 / (math.pi * 0.5e-3 ** 2)))
    for d in (0.3, 0.4): print('via %.1f drill, front to layer 3: %.2f mohm; front to back %.2f' % (d, 1e3 * (rnet.barrel_R(d, rnet.DZ[0]) + rnet.barrel_R(d, rnet.DZ[1])), 1e3 * sum(rnet.barrel_R(d, z) for z in rnet.DZ)))
