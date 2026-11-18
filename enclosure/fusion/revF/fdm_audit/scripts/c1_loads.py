"""Block 3: load cases. Single loads on simple members; every load is an assumption unless a source is named.
Strengths: Bambu ABS data sheet V3.0 (read 2026-11-18): 33 MPa along the layers, 28 MPa across them."""
import math
SZ, SXY = 28.0, 33.0
LIM = dict(z_short=SZ / 3, z_long=SZ / 5, xy_short=SXY / 2.5, xy_long=SXY / 4, shear_z_short=0.58 * SZ / 3)
print('limits MPa:', {k: round(v, 1) for k, v in LIM.items()})
def row(name, stress, lim, note=''):
    print('%-58s %6.1f MPa | limit %4.1f | %5.2f of limit | %4.1f x below the sheet | %s' % (name, stress, LIM[lim], stress / LIM[lim], (SZ if 'z' in lim else SXY) / stress if 'shear' not in lim else 0.58 * SZ / stress, note))
# 1 door vent bar, 10 N on one bar at mid length (assumed, as the enclosure chat)
L, b = 56.5, 3.0
for d in (2.5, 4.0, 4.5):
    Z = b * d * d / 6
    row('door bar %.1f deep, ends held' % d, 10 * L / 8 / Z, 'z_short'); row('door bar %.1f deep, ends free to turn' % d, 10 * L / 4 / Z, 'z_short')
# 2 lip round the door opening
h = 8.5
for t in (1.2, 1.7, 2.0):
    row('lip %.1f: 10 N over 20 mm of rim' % t, 6 * 10 * h / ((20 + 2 * h) * t * t), 'z_short')
    row('lip %.1f: 10 N from a tool tip (2 mm)' % t, 6 * 10 * h / ((2 + 2 * h) * t * t), 'z_short')
    row('lip %.1f: one magnet pair, 4.3 N at mid height' % t, 6 * 4.3 * (h / 2) / ((12 + h) * t * t), 'z_long')
# 3 magnet seat skins
row('door skin 0.45: 4.3 N, shear round the rim', 4.3 / (math.pi * 8.3 * 0.45), 'z_long')
row('door skin 0.45: 4.3 N as a clamped plate, magnet not glued', 3 * 4.3 / (4 * math.pi * 0.45 ** 2), 'z_long')
# 4 groove web: 1 N/mm prying on the rail's front edge, arm 1.2 (assumed)
for t in (0.51, 0.8, 1.0):
    row('groove web %.2f: 1 N/mm on the rail edge, arm 1.2' % t, 6 * 1.0 * 1.2 / (t * t), 'z_short')
# 5 chin lip and nose: plate unit about 370 g on two noses (box-top screws not in)
F = 0.370 * 9.81 / 2
row('chin lip 1.25 under a nose (11 wide), arm 1.9', 6 * (F / 11) * 1.9 / 1.25 ** 2, 'z_short', 'F per nose %.2f N' % F)
row('nose 0.9, arm 0.6', 6 * (F / 11) * 0.6 / 0.9 ** 2, 'xy_short')
# 6 screw torque 0.5 N.m (assumed, as the enclosure chat); half enters the post through the thread
T = 500.0
rm_o, rm_i, t2 = 4.5 - 0.435, 2.085 + 0.435, 0.87
cap = 2 * math.pi * rm_o ** 2 * t2 + 2 * math.pi * rm_i ** 2 * t2
row('top post at its land as sliced (2+2 lines), full torque', T / cap, 'shear_z_short'); row('the same, half the torque', T / 2 / cap, 'shear_z_short')
J = math.pi / 32 * (8 ** 4 - 4.17 ** 4)
row('boss O8 with insert, solid ring (cap, carrier top), full torque', T * 4 / J, 'shear_z_short'); row('the same, half the torque', T / 2 * 4 / J, 'shear_z_short')
print('clamp force at 0.5 N.m, K 0.2: %.0f N; land 51 mm2: %.1f MPa in compression' % (T / (0.2 * 3), T / (0.2 * 3) / 51.05))
