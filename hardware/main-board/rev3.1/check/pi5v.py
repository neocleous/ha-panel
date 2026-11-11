import os
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')) + os.sep
import pcb, rnet, time, sys, json
P = ROOT
N5 = '+5V'; NF = '/5 V supply and outputs/5V_PI_F'; NV = '/5 V supply and outputs/VBUS_PI'
VB = [('pin', 'J2.A4'), ('pin', 'J2.B9'), ('pin', 'J2.A9'), ('pin', 'J2.B4')]
GN = [('pin', 'J2.A1'), ('pin', 'J2.B12'), ('pin', 'J2.A12'), ('pin', 'J2.B1')]
PSO = [('pin', 'PS1.%d' % i) for i in (1, 2, 3, 4)]; PSC = [('pin', 'PS1.%d' % i) for i in (5, 6, 7, 8)]
def run(name, path, boxes):
    b = pcb.load(path); out = {}
    t0 = time.time()
    n = rnet.Net(b, [N5], boxes['s1'][0], boxes['s1'][1]); out['s1'] = n.solve(PSO, [('pad', 'F2', '1', 'F.Cu')])[0]
    n = rnet.Net(b, [NF], boxes['s2'][0], boxes['s2'][1]); out['s2'] = n.solve([('pad', 'F2', '2', 'F.Cu')], [('pin', 'LK1.1')])[0]
    n = rnet.Net(b, [NV], boxes['s3'][0], boxes['s3'][1])
    out['s3_equal'], pins = n.solve([('pin', 'LK1.2')], VB, mode='equal'); out['s3_pins'] = pins
    out['s3_equi'] = n.solve([('pin', 'LK1.2')], VB, mode='equipotential')[0]
    out['s3_one_pair_A4B9'] = n.solve([('pin', 'LK1.2')], VB[:2], mode='equal')[0]
    out['s3_one_pair_A9B4'] = n.solve([('pin', 'LK1.2')], VB[2:], mode='equal')[0]
    n = rnet.Net(b, ['GND'], boxes['s4'][0], boxes['s4'][1])
    out['s4_equal'], gp = n.solve(PSC, GN, mode='equal'); out['s4_pins'] = gp
    out['s4_equi'] = n.solve(PSC, GN, mode='equipotential')[0]
    print('==', name, '(%.0f s)' % (time.time() - t0))
    for k, v in out.items():
        print('   %-18s' % k, ('%.3f mohm' % (v * 1e3)) if not isinstance(v, list) else ['%.3f' % (x * 1e3) for x in v])
    return out
r3 = run('rev 3', P + 'main-board.kicad_pcb', dict(s1=((45, 8, 59, 40), 0.05), s2=((46, 33, 54, 45), 0.05), s3=((49, 35, 73, 52), 0.05), s4=((10, 20, 80, 58), 0.1)))
r21 = run('rev 2.1', P + 'rev2.1/main-board.kicad_pcb', dict(s1=((0, -5, 75, 42), 0.1), s2=((12, 30, 40, 49), 0.05), s3=((14, 36, 30, 51), 0.05), s4=((0, -5, 75, 50), 0.1)))
json.dump(dict(rev3=r3, rev21=r21), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pi5v_solve.json'), 'w'), indent=1)
