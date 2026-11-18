import sys
from render import *
name = sys.argv[1]; d = [float(x) for x in sys.argv[2:5]]; out = sys.argv[5]
ppm = float(sys.argv[6]) if len(sys.argv) > 6 else 6.0
m, cols = thickness_colours(name, maxcls=int(sys.argv[7]) if len(sys.argv) > 7 else 4)
c = m.bounds.mean(0); r, u, dd = view_axes(d)
ext = m.vertices - c
w = np.ptp(ext @ r) + 6; h = np.ptp(ext @ u) + 6
cen = c + r * ((ext @ r).max() + (ext @ r).min()) / 2 + u * ((ext @ u).max() + (ext @ u).min()) / 2
img, cam = render([(m, cols)], d, cen, w, h, ppm=ppm)
save(img, out, title='%s — thickness classes, view from (%g, %g, %g)' % (PARTS[name]['label'], d[0], d[1], d[2]), cam=cam, centre=cen, width=w, height=h)
print(out, img.shape)
