import rnet, math
# synthetic check: a 1.0 wide, 20 long track on F.Cu between two 2x2 pads -> rho*L/(w*t) between the pad edges
def pad(n, x, y, net): return dict(n=n, type='smd', shape='rect', x=x, y=y, sx=2.0, sy=2.0, drill=None, net=net, layers=['F.Cu'])
b = dict(zones=[], vias=[], segs=[dict(x1=5, y1=5, x2=25, y2=5, w=1.0, layer='F.Cu', net='N')],
         fps={'A': dict(pads=[pad('1', 5, 5, 'N')]), 'B': dict(pads=[pad('1', 25, 5, 'N')])})
for h in (0.1, 0.05):
    n = rnet.Net(b, ['N'], (0, 0, 30, 10), h)
    R, _ = n.solve([('pad', 'A', '1', 'F.Cu')], [('pad', 'B', '1', 'F.Cu')])
    print('h', h, 'solver %.3f mohm' % (R * 1e3), ' analytic (18 mm between pad edges) %.3f mohm' % (rnet.RHO * 18e-3 / (1e-3 * 35e-6) * 1e3))
# via check: two pads on F and B joined by one 0.4 via
b2 = dict(zones=[], vias=[dict(x=10, y=5, size=0.8, drill=0.4, layers=['F.Cu', 'B.Cu'], net='N')],
          segs=[dict(x1=5, y1=5, x2=10, y2=5, w=1.0, layer='F.Cu', net='N'), dict(x1=10, y1=5, x2=15, y2=5, w=1.0, layer='B.Cu', net='N')],
          fps={'A': dict(pads=[pad('1', 5, 5, 'N')]), 'B': dict(pads=[dict(pad('1', 15, 5, 'N'), layers=['B.Cu'])])})
n = rnet.Net(b2, ['N'], (0, 0, 20, 10), 0.05)
R, _ = n.solve([('pad', 'A', '1', 'F.Cu')], [('pad', 'B', '1', 'B.Cu')])
vb = sum(rnet.barrel_R(0.4, d) for d in rnet.DZ)
print('via case: solver %.3f mohm; lumped: 2 x 4 mm track %.3f + barrel %.3f = %.3f (plus spreading at the via)' % (R * 1e3, 2 * rnet.RHO * 4e-3 / (1e-3 * 35e-6) * 1e3, vb * 1e3, 2 * rnet.RHO * 4e-3 / (1e-3 * 35e-6) * 1e3 + vb * 1e3))
