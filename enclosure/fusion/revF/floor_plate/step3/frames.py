import math
S12, C12 = 0.2079, 0.9781
U0, V0, D0 = 2.5, -27.45, 32.7
def s2w(x, d, zd):            # slab -> world
    return (x, -C12 * d - S12 * zd, 143.3 - S12 * d + C12 * zd)
def w2s(x, y, z):
    d = -C12 * y - S12 * (z - 143.3); zd = -S12 * y + C12 * (z - 143.3)
    return (x, d, zd)
def b2w(u, v, w):
    return s2w(U0 + u, D0 + w, V0 + v)
def w2b(x, y, z):
    x, d, zd = w2s(x, y, z)
    return (x - U0, zd - V0, d - D0)
def P(n):                     # node -> world
    k = n[0]
    return b2w(*n[1:]) if k == 'B' else s2w(*n[1:]) if k == 'S' else tuple(n[1:])
def length(nodes):
    ps = [P(n) for n in nodes]
    return sum(math.dist(ps[i], ps[i + 1]) for i in range(len(ps) - 1))
if __name__ == '__main__':
    for name, pt in [('board bottom edge door side', ('B', 0, -28.95, 0)), ('board bottom edge back', ('B', 0, -28.95, -1.6)), ('plate bottom edge', ('S', 0, 17.2, -56.9)),
                     ('J1 plug top', ('B', 0, -25, 9.8)), ('J9 plug top', ('B', -39, -25, 9.8)), ('J8 plug top', ('B', 38.75, -25, 9.8)), ('J5 plug top', ('B', -40.3, -13.85, 9.8)),
                     ('J6 plug top', ('B', 12.3, -22.2, 9.8)), ('J10 housing top', ('B', -34.3, -14.1, 16.5)), ('J11 housing top', ('B', -0.7, -12, 16.5)),
                     ('J2 plug end', ('B', 21.625, -48.95, 1.72)), ('J3 A1 back', ('B', -24.5, -26.2, -1.6)), ('J3 A2 back', ('B', -19.0, -25.7, -1.6)), ('J4 back', ('B', 6.92, -25.73, -1.6)),
                     ('PS1 top mid', ('B', -11.6, 1.7, 28.5)), ('LCD hdr top', ('S', 32.85, 15.4, -2.93))]:
        w = P(pt); print('%-28s world %7.1f %7.1f %7.1f' % (name, *w))
    for name, w in [('radar end', (-69, -24, 128)), ('BME end', (-71, -40.5, 94)), ('BME n2', (-72, -41.5, 86)), ('BME n1', (-67, -36, 84)), ('VEML end', (0, -40, 176)), ('inlet pads', (0, -65, 22)),
                    ('spk L hole', (62, -54, 30)), ('touch pads', (12, 2, 46)), ('Pi hdr A1', (-32.29, -6.71, 32)), ('Pi hdr A2', (-22.13, -5.45, 32)), ('Pi hdr B', (10.91, -5.45, 32)), ('Pi pwr end', (25, -66, 35.5)),
                    ('GPIO old n3', (-10, -18, 62)), ('GPIO old n4', (12, -36, 84)), ('touch old n', (8, -10, 70)), ('touch old n2', (4, -45, 75.5))]:
        b = w2b(*w); print('%-28s board %7.1f %7.1f %7.1f' % (name, *b))
