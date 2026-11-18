# rev F g22 (version 66 -> 67): the calls as run on 2026-11-18, in order.
# Record, not a one-shot script: each block was one connector call (time limit
# 45 s of work, the connector gives up at 80 s). Needs c3k (v5f_k_lib.py),
# c3 (c3_lib.py, c3_fix.py, c3_shell.py) loaded as in README.
# World mm: x + = viewer's left, y + toward the screen, z up. Slab frame (x, d, up).
# Nothing here exports a print file.
import math, sys
import adsk.core, adsk.fusion

C = math.cos(math.radians(12.0)); S = math.sin(math.radians(12.0)); H = 143.3


def new_prism(X, rc, face, dist_mm):
    """Extrude a planar face of a real body as a new body, copy it, delete it.
    Positive distance runs along the face's outward normal."""
    tbm = adsk.fusion.TemporaryBRepManager.get()
    exts = rc.features.extrudeFeatures
    n0 = rc.bRepBodies.count
    inp = exts.createInput(face, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp.setDistanceExtent(False, adsk.core.ValueInput.createByReal(dist_mm / 10.0))
    exts.add(inp)
    if rc.bRepBodies.count != n0 + 1:
        raise RuntimeError('no new body')
    nb = rc.bRepBodies.item(rc.bRepBodies.count - 1)
    tb = tbm.copy(nb)
    nb.deleteMe()
    return tb


def slit_tool(X, w, reg, lo, hi, axis='z', ov=0.01):
    """Fill for a thin slit between two levels: (slice beyond hi) AND (slice
    before lo), stacked through the slit. reg = the other two axes' ranges."""
    def slab(a, b):
        if axis == 'z':
            return X.wbox(reg[0], reg[1], reg[2], reg[3], a, b)
        return X.wbox(reg[0], reg[1], a, b, reg[2], reg[3])
    def mv(tb, s):
        if axis == 'z':
            X.move(tb, 0.0, 0.0, s)
        else:
            X.move(tb, 0.0, s, 0.0)
    Sa = X.cp(w); X.sec(Sa, slab(hi + 0.02, hi + 0.07)); mv(Sa, -(hi + 0.02))
    Sb = X.cp(w); X.sec(Sb, slab(lo - 0.07, lo - 0.02)); mv(Sb, -(lo - 0.07))
    X.sec(Sa, Sb)
    tool = None; p = lo - ov; top = hi + ov - 0.05
    while p < top - 1e-6:
        c = X.cp(Sa); mv(c, p)
        if tool is None: tool = c
        else: X.uni(tool, c)
        p += 0.04
    c = X.cp(Sa); mv(c, top)
    if tool is None: tool = c
    else: X.uni(tool, c)
    return tool


def shell_steps(X, k, c3, rc):
    """HOUSING_F_front, version 66 -> 67. sh = the version-66 body (face numbers are its)."""
    sh = X.body('HOUSING_F_front')
    # FDM3: lip 1.2 -> 2.0, grown inward; frame faces at y -53.5 stay
    c3.shell_start(X)
    c3.shell_add(X, c3.lip_layer(X, 2.1, 2.9))            # + 3,536.8 (stray 0.001 lump removed first)
    w = k.c['shell_wip']
    # FDM4: web behind the cloth groove 0.5 -> 1.0 (groove 1.3 -> 0.8 deep), x -48..48
    t = X.dbox(-48.0, 48.0, 13.80, 14.35, -93.48, -91.88)  # + 72.0
    # FDM6: toe 0.4 -> 0.85, grown upward; lips at x +-23.5..36.5 and corners left
    for xa, xb in ((-87.66, -36.4), (-23.6, 23.6), (36.4, 87.66)):
        X.uni(t, X.wbox(xa, xb, 1.5, 3.1, 2.85, 3.65))
    for xa, xb in ((45.4, 46.9), (-46.8, -45.3)):
        X.uni(t, X.wbox(xa, xb, 1.5, 3.1, 3.6, 3.75))       # + 69.55 in all
    X.uni(w, t)
    # FDM11b at y -55.0: seat floor moved 0.2 to y -55.2 (past the wall's edge)
    lay = X.cp(X.body('TOOL_inner_skin_1p2')); X.dif(lay, X.cp(X.body('TOOL_inner_skin_0p2')))
    X.sec(lay, X.wbox(-150, 150, -55.2, -54.8, 6.5, 250))   # + 32.16
    # FDM11b at y -52.5: the step's five faces carried 0.5 back
    for fi in (578, 579, 1412, 1429, 1430):
        X.uni(lay, new_prism(X, rc, sh.faces.item(fi), 0.5))  # + 8.7
    X.uni(w, lay)
    # FDM11a: the four leaves, by their front faces, 0.05 into the leaf
    for fi in (316, 197, 177, 184):
        X.dif(w, new_prism(X, rc, sh.faces.item(fi), -0.05))  # - 16.69
    # FDM11c: the seam in the oblique gusset (face 0), 0.15 each way
    X.uni(w, new_prism(X, rc, sh.faces.item(0), 0.15))
    X.uni(w, new_prism(X, rc, sh.faces.item(0), -0.15))
    # FDM11c: slits z 170.0..170.1 above the gussets (8 places, + 1.41)
    X.uni(w, slit_tool(X, w, (-60.0, 60.0, -53.0, -27.0), 170.0, 170.1))
    # FDM11d: under the roof ledge down to each top post's cone, d >= 14.05
    for xa, xb in ((64.0, 78.5), (-78.5, -64.0)):
        sl = X.cp(w); X.sec(sl, X.wbox(xa, xb, -27.5, -19.9, 172.30, 172.40))
        rb = rc.bRepBodies.add(sl); rb.name = 'AUD_S'
        P = None
        for f in rb.faces:
            if f.geometry.surfaceType != adsk.core.SurfaceTypes.PlaneSurfaceType:
                continue
            ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
            if k.wv(nv)[2] < -0.999 and abs(k.W(f.pointOnFace)[2] - 172.30) < 0.005:
                p = new_prism(X, rc, f, 3.4)
                if P is None: P = p
                else: X.uni(P, p)
        rb.deleteMe()
        X.sec(P, X.dbox(-200.0, 200.0, 14.05, 40.0, 0.0, 60.0))
        X.uni(w, P)                                        # + 19.17 and + 19.15
    # FDM11d: slit z 175.3..175.6 under the top wall, and the seam beside it
    X.uni(w, slit_tool(X, w, (-80.0, 80.0, -27.0, -18.0), 175.3, 175.6))  # + 0.14
    # FDM11e: radar brace head, one face each side
    O = (0.0, 0.0, H); ns = (0.0, C, S)
    def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
    def unit(a):
        L = math.sqrt(sum(q*q for q in a)); return tuple(q / L for q in a)
    no = (-0.515, -0.8572, 0.0)
    t3 = unit(cross(ns, no)); m = unit(cross(ns, t3))
    def pt(a, b, e): return tuple(O[i] + a*m[i] + b*ns[i] + e*t3[i] for i in range(3))
    # left: valleys filled to the plane through the bar's corner (m -67.345), d 13.0..14.8
    X.uni(w, c3.obox_w(X, pt((-67.345 - 65.70) / 2.0, -13.9, (-49.4 - 24.3) / 2.0), t3, ns, 25.1, 1.8, 1.645))   # + 29.05
    # right: teeth cut back to the plane through the bar's corner (m -61.841)
    X.dif(w, c3.obox_w(X, pt((-61.841 - 60.20) / 2.0, -13.9, (-50.9 - 18.8) / 2.0), t3, ns, 32.1, 1.8, 1.641))  # - 37.66
    # after the interference table: K5 upper-left lane re-cut through the raised floor (- 0.008)
    cut = X.cp(X.body('KO_K5_UL')); X.sec(cut, X.wbox(50.0, 56.0, -55.35, -54.9, 117.0, 123.0))
    X.dif(w, cut)
    return w


def box_r_rear(X, b):
    """SPKBOX_R: the 0.4 slot between the rear wall and the block and stair in front (+ 2.228)."""
    X.uni(b, slit_tool(X, b, (-56.0, -46.0, 17.0, 33.0), -50.5, -50.1, axis='y'))
    return b


def cap_fix(X):
    """HOUSING_F_cap: the 8 corner slots closed from the pins' seat level z 177.6 up
    (not from the rim's 177.5: the microphone strips sit on 177.6). + 8 x 0.784."""
    old = X.cp(X.body('HOUSING_F_cap_v66'))
    c3 = sys.modules['c3']
    c3.build_cap(X, pin=1.6, gap=0.4)                      # boxes z 177.5..178.35
    cap = c3.G['HOUSING_F_cap']
    for xa, xb in ((8.3, 37.7), (-37.7, -8.3)):
        X.dif(cap, X.wbox(xa, xb, -29.7, -23.3, 177.4, 177.6))   # takes more than the fills: lesson 234
    d = X.cp(cap); X.dif(d, old)                           # = the 8 fills, 0.784 each
    good = X.cp(old); X.uni(good, d)
    return good


# Not kept: CRADLE_5807 rear bezel 0.80 -> 0.85 by moving its rear face 0.05 out.
# The outer-skin check read 10.924 -> 15.921 outside the reference; the body was put back.

COMMIT = ['HOUSING_F_front', 'HOUSING_F_door', 'HOUSING_F_cap', 'FLOOR_PLATE',
          'SPKBOX_L', 'SPKBOX_R', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R']   # X.swap(name, G[name], '_v66')

GUARD_V67 = {
    'HOUSING_F_plate': 66463.676, 'HOUSING_F_front': 111611.475, 'SPKBOX_L': 26342.557,
    'SPKBOX_R': 27112.045, 'FLOOR_PLATE': 32643.331, 'RESP_CARRIER': 13651.988,
    'CRADLE_5807': 1771.219, 'HOUSING_F_door': 50476.660, 'HOUSING_F_cap': 9986.525,
    'TOUCH_CLIP_L': 580.762, 'TOUCH_CLIP_R': 580.762, 'SLAB_frame': 62932.407,
    'GROMMET_usbc_F': 506.176, 'BME_HOOD': 802.884,
}
