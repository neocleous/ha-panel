"""The Pi 5 V path and the 20 V sections of any revision of the board: python3 pi5v_board.py <board.kicad_pcb>"""
import pcb, rnet, sys, time
B = sys.argv[1]
N5 = '+5V'; NF = '/5 V supply and outputs/5V_PI_F'; NV = '/5 V supply and outputs/VBUS_PI'
VE = '/20 V inlet and eFuse/VIN_EF'; VP = '/20 V inlet and eFuse/VIN_PIGTAIL'; NI = '/5 V supply and outputs/NID_VIN'
VB = [('pin', 'J2.A4'), ('pin', 'J2.B9'), ('pin', 'J2.A9'), ('pin', 'J2.B4')]
GN = [('pin', 'J2.A1'), ('pin', 'J2.B12'), ('pin', 'J2.A12'), ('pin', 'J2.B1')]
PSO = [('pin', 'PS1.%d' % i) for i in (1, 2, 3, 4)]; PSC = [('pin', 'PS1.%d' % i) for i in (5, 6, 7, 8)]
b = pcb.load(B); t0 = time.time()
s1 = rnet.Net(b, [N5], (45, 8, 59, 40), 0.05).solve(PSO, [('pad', 'F2', '1', 'F.Cu')])[0]
s2 = rnet.Net(b, [NF], (46, 33, 54, 45), 0.05).solve([('pad', 'F2', '2', 'F.Cu')], [('pin', 'LK1.1')])[0]
n = rnet.Net(b, [NV], (49, 35, 73, 52), 0.05); s3, pins = n.solve([('pin', 'LK1.2')], VB, mode='equal')
s3q = rnet.Net(b, [NV], (49, 35, 73, 52), 0.05).solve([('pin', 'LK1.2')], VB, mode='equipotential')[0]
n = rnet.Net(b, ['GND'], (10, 20, 80, 58), 0.1); s4, gp = n.solve(PSC, GN, mode='equal')
print('Pi 5 V path, board copper, mohm at 20 C:')
print('   module -> fuse           %.2f' % (s1 * 1e3))
print('   fuse -> wire link        %.2f' % (s2 * 1e3))
print('   wire link -> socket      %.2f  (per pin %s; pins at one potential %.2f)' % (s3 * 1e3, ' '.join('%.2f' % (x * 1e3) for x in pins), s3q * 1e3))
print('   return                   %.2f  (per pin %s)' % (s4 * 1e3, ' '.join('%.2f' % (x * 1e3) for x in gp)))
print('   board copper             %.2f   with fuse 5.6 and link 0.17: %.2f' % ((s1 + s2 + s3 + s4) * 1e3, (s1 + s2 + s3 + s4) * 1e3 + 5.6 + 0.167))
a = rnet.Net(b, [VP], (30, 50, 46, 57.5), 0.05).solve([('pin', 'J1.1')], [('pad', 'F1', '1', 'F.Cu')])[0]
c = rnet.Net(b, [VE], (20, 44, 36, 57.5), 0.025).solve([('pad', 'F1', '2', 'F.Cu')], [('pad', 'U1', '1', 'F.Cu'), ('pad', 'U1', '2', 'F.Cu'), ('pad', 'U1', '3', 'F.Cu')])[0]
d = rnet.Net(b, ['+20V'], (21, 0, 52, 52), 0.1).solve([('pad', 'U1', '18', 'F.Cu'), ('pad', 'U1', '19', 'F.Cu'), ('pad', 'U1', '20', 'F.Cu')], [('pad', 'L1', '1', 'F.Cu')])[0]
e = rnet.Net(b, [NI], (10, 5, 28, 32), 0.05).solve([('pad', 'L1', '2', 'F.Cu')], [('pin', 'PS1.9'), ('pin', 'PS1.10')])[0]
print('20 V: socket -> fuse %.2f | fuse -> protection chip %.2f | chip -> filter coil (layer 3) %.2f | coil -> module %.2f' % (a * 1e3, c * 1e3, d * 1e3, e * 1e3))
print('(%.0f s)' % (time.time() - t0))
