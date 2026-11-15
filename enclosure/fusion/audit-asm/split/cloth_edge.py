# Where the cloth's side edge must end on the rounded front corner of a side wall so that its outer surface stays behind
# the screen plate's back (d 12.8) with 0.1 left. Section of the shell's outer face (slab frame: d, x) read with needles
# on version 64 at up 20 and up -40 (aud5x session, R['sw_section']).
import math
sec = {
 20.0: [(13.15, 81.69), (13.40, 82.17), (13.65, 82.49), (13.90, 82.72), (14.15, 82.89), (14.40, 83.02), (14.65, 83.11),
        (14.90, 83.17), (15.15, 83.20), (15.40, 83.20)],
 -40.0: [(13.15, 93.16), (13.40, 93.62), (13.65, 93.92), (13.90, 94.14), (14.15, 94.30), (14.40, 94.42), (14.65, 94.51),
         (14.90, 94.57), (15.15, 94.60), (15.40, 94.60)],
}
PLATE_BACK, MARGIN = 12.8, 0.1
for up, pts in sec.items():
    # the wall's front face is at d 13.0; the outer corner runs from (13.0, x0) to the flat at d 15.15
    pts = [(13.0, pts[0][1] - (pts[1][1] - pts[0][1]) * 0.15 / 0.25)] + pts
    print('up', up)
    for t in (0.7, 1.0, 1.2):
        ok = None
        # cloth laid on the outer surface from the back up to an end point; its outer surface = the wall offset by t along the normal.
        # The forward-most point of the cloth is at its end: end point offset by t along the local normal (pointing out and forward).
        for i in range(1, len(pts)):
            (d0, x0), (d1, x1) = pts[i - 1], pts[i]
            ld, lx = d1 - d0, x1 - x0; L = math.hypot(ld, lx)
            nd, nx = lx / L, -ld / L            # outward normal in (d, x): out (+x) and forward (-d) on the round
            if nx < 0:
                nd, nx = -nd, -nx
            fwd = (d0 + d1) / 2 + nd * t       # d of the cloth's outer surface at this segment's middle
            if fwd >= PLATE_BACK + MARGIN:
                ok = ((d0 + d1) / 2, round(fwd, 2), round(-nd, 2))
                break
        print('   cloth %.1f: end it at d %.2f or further back (its outer surface then at d %s; normal forward share %s)' % (t, ok[0], ok[1], ok[2]))
