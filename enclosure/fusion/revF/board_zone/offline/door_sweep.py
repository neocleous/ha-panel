"""Door removal (straight back, -y) against the rev 2 main board bodies: door material ahead of a body's rear face that lies
over the body's x-z footprint would pass through it. Least x-z distance from that door material to each footprint, and the
least y gap behind each footprint (door material behind it)."""
import numpy as np, sys
sys.path.insert(0, '.')
from exact import samples, clearance, M
from shapely.geometry import Polygon, box
import shapely
OUTLINE = Polygon([(45, 34), (45, 89), (-43, 89), (-45, 88.5), (-45, 34)])
BACK29 = OUTLINE.difference(box(-46, 82, -38, 90)).difference(box(43.5, 82, 46, 90))
J2BOX = box(19.72, 34, 30.28, 43.67)
OLD = Polygon([(45, 34), (45, 84), (-45, 84), (-45, 34)])
P = samples(M + 'HOUSING_F_door.stl', 0.25, (np.array([-80, -90, 20]), np.array([80, -40, 130])))
print('door samples', len(P))
def sweep(poly, y_rear, name):
    Q = P[P[:, 1] > y_rear]
    d, p = clearance(list(poly.exterior.coords), Q)
    print('%-34s door ahead of y %.1f: least x-z distance to the footprint %.2f at %s' % (name, y_rear, d, np.round(p, 2)))
def gap_behind(poly, y_rear, name):
    # door samples over the footprint (x-z inside) and behind the rear face: least y gap
    pts = shapely.points(P[:, 0], P[:, 2])
    inside = shapely.contains(poly, pts)
    Q = P[inside & (P[:, 1] <= y_rear)]
    i = np.argmax(Q[:, 1])
    print('%-34s door behind the footprint: least gap %.2f at %s' % (name, y_rear - Q[i, 1], np.round(Q[i], 2)))
sweep(OUTLINE, -65.0, 'MAIN_pcb (rev 2)')
sweep(OLD, -65.0, 'MAIN_pcb (old 90 x 50)')
sweep(BACK29, -67.9, 'MAIN_back_env 2.9 (rev 2)')
sweep(J2BOX, -68.5, 'MAIN_back_env J2 3.5 (rev 2)')
sweep(OLD, -68.5, 'MAIN_back_env 3.5 (old)')
gap_behind(OUTLINE, -65.0, 'MAIN_pcb (rev 2)')
gap_behind(BACK29, -65.0, 'back face over the 2.9 zone (rev 2)')
gap_behind(OLD, -65.0, 'MAIN_pcb (old)')
