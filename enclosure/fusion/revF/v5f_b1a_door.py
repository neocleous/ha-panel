# rev F block 1a (2026-11-03): DOOR_F = rev E door outline shrunk 0.7 per side for the D1 cloth layer
# (outer generator section offset 3.5 = wall 2.5 + D1 layer 0.7 + gap 0.3; front edge y 4.0; front corners R8.5;
# z 0-2.5). Rev E DOOR_plate renamed DOOR_plate_revE and hidden (kept). Port of v5e_p18 door().
# --- paste v5f_common.py above this line ---

def section_pts(hw, dep, n, rc, N=241):
    ai = hw - rc; bi = dep - 2 * rc
    th = [math.pi * i / (N - 1) for i in range(N)]
    def sp(t):
        c = math.cos(t); s = math.sin(t)
        return (ai * (1 if c >= 0 else -1) * abs(c) ** (2.0 / n), -rc - bi * abs(s) ** (2.0 / n))
    P = [sp(t) for t in th]; Q = []
    for i in range(N):
        a = P[max(i - 1, 0)]; b = P[min(i + 1, N - 1)]; tu = b[0] - a[0]; tv = b[1] - a[1]; L = math.hypot(tu, tv) or 1e-9
        Q.append((P[i][0] + rc * (-tv / L), P[i][1] + rc * (tu / L)))
    Q[0] = (hw, -rc); Q[-1] = (-hw, -rc)
    tot = sum(math.hypot(Q[i + 1][0] - Q[i][0], Q[i + 1][1] - Q[i][1]) for i in range(N - 1)); dmin = max(3.0, tot / 64.0)
    inner = []; last = Q[0]; acc = 0.0
    for i in range(1, N - 1):
        acc += math.hypot(Q[i][0] - last[0], Q[i][1] - last[1]); last = Q[i]
        if acc >= dmin and math.hypot(Q[i][0] - Q[-1][0], Q[i][1] - Q[-1][1]) >= dmin:
            inner.append(Q[i]); acc = 0.0
    return ai, inner


def run(_context):
    X = Ctx(); comp = X.comp; feats = X.feats
    out = {}
    fl = X.plane('FLOOR_plane')
    sb = X.body('SLAB_frame').boundingBox
    YBK = wy(P3(0, sb.minPoint.y, sb.minPoint.z)); YC = YBK - 0.5; YF = -sb.minPoint.z * 10 * S
    ZT = 180.0; PW = 2.2; PWW = 1.7; DTOP = 28.0; YTOP = yfront(13.0, ZT) - DTOP; HWT = 90.0
    hwE = lambda z: 100 - (100 - HWT) * (z / ZT) ** PWW
    ybE = lambda z: -85 + (YTOP + 85) * (z / ZT) ** PW
    nE = lambda z: 2.6 - 0.6 * (z / ZT)
    out['YC'] = round(YC, 3); out['YF'] = round(YF, 3)
    OFF = 3.5; WALL = 2.5

    def sign_toward(sk, vec):
        n = sk.xDirection.crossProduct(sk.yDirection); return 1.0 if n.dotProduct(vec) > 0 else -1.0

    # outline sketch
    sk = comp.sketches.add(fl); sk.name = 'skF_door'; sk.isLightBulbOn = False
    hw = hwE(0) - OFF; dep = (YF - ybE(0)) - 2 * OFF; n = nE(0); rc = 12.0 - OFF; yf = YF - OFF
    cu, mid = section_pts(hw, dep, n, rc)
    Q = lambda x, y: sk.modelToSketchSpace(Dw(x, y, 0.0))
    L = sk.sketchCurves.sketchLines; A = sk.sketchCurves.sketchArcs; k = math.sqrt(0.5)
    ln = L.addByTwoPoints(Q(XC - cu, yf), Q(XC + cu, yf)); ln.isFixed = True
    aR = A.addByThreePoints(ln.endSketchPoint, Q(XC + cu + rc * k, yf - rc + rc * k), Q(XC + hw, yf - rc)); aR.isFixed = True
    aL = A.addByThreePoints(Q(XC - hw, yf - rc), Q(XC - cu - rc * k, yf - rc + rc * k), ln.startSketchPoint); aL.isFixed = True
    cps = [aR.endSketchPoint, Q(XC + hw, yf - rc - 2.0)] + [Q(XC + u, yf + v) for (u, v) in mid] + [Q(XC - hw, yf - rc - 2.0), aL.startSketchPoint]
    sk.sketchCurves.sketchControlPointSplines.add(cps, adsk.fusion.SplineDegrees.SplineDegreeThree)
    pr = max((sk.profiles.item(i) for i in range(sk.profiles.count)), key=lambda p: p.areaProperties().area)
    inp = feats.extrudeFeatures.createInput(pr, NEW); s = sign_toward(sk, UP)
    inp.startExtent = adsk.fusion.OffsetStartDefinition.create(VI(0.0)); inp.setDistanceExtent(False, VI(s * WALL / 10))
    f = feats.extrudeFeatures.add(inp); door = f.bodies.item(0); door.name = 'DOOR_F'
    # chin cut: remove y > YC - OFF
    sk2 = comp.sketches.add(fl); sk2.name = 'skF_door_chin'; sk2.isLightBulbOn = False
    Q2 = lambda x, y: sk2.modelToSketchSpace(Dw(x, y, 0.0))
    sk2.sketchCurves.sketchLines.addTwoPointRectangle(Q2(-130.0, YC - OFF), Q2(130.0, 60.0))
    coll = adsk.core.ObjectCollection.create()
    for i in range(sk2.profiles.count):
        coll.add(sk2.profiles.item(i))
    ci = feats.extrudeFeatures.createInput(coll, CUT); s2 = sign_toward(sk2, UP)
    ci.startExtent = adsk.fusion.OffsetStartDefinition.create(VI(s2 * -0.5)); ci.setDistanceExtent(False, VI(s2 * 1.5))
    ci.participantBodies = [door]; feats.extrudeFeatures.add(ci)
    # front vertical corner fillets R(12 - OFF)
    front = None
    for fc in door.faces:
        if fc.geometry.objectType.endswith('Plane') and abs(wy(fc.centroid) - (YC - OFF)) < 0.5:
            front = fc
    ec = adsk.core.ObjectCollection.create()
    for e in front.edges:
        if abs(wz(e.startVertex.geometry) - wz(e.endVertex.geometry)) > 0.5:
            ec.add(e)
    fi = feats.filletFeatures.createInput(); fi.edgeSetInputs.addConstantRadiusEdgeSet(ec, VI(rc / 10), True)
    feats.filletFeatures.add(fi)
    out['front_corner_edges'] = ec.count
    # rename/hide the rev E door
    old = X.body('DOOR_plate')
    if old:
        old.name = 'DOOR_plate_revE'; old.isLightBulbOn = False
    door = X.body('DOOR_F')
    out['vol_cm3'] = round(door.volume, 2)
    # probes: door edges vs INNER_E
    inner = X.body('INNER_E')
    def edge(b, pin, pout, n=40):
        a, c = pin, pout
        for _ in range(n):
            m = tuple((a[i] + c[i]) / 2 for i in range(3))
            if X.inside(b, *m): a = m
            else: c = m
        return a
    out['front_y'] = round(edge(door, (XC, -10, 1.25), (XC, 20, 1.25))[1], 2)
    out['back_y_XC'] = round(edge(door, (XC, -40, 1.25), (XC, -120, 1.25))[1], 2)
    hwd = {}
    for y in (-7.0, -45.75, -72.0, -74.0):
        xd = edge(door, (XC, y, 1.25), (XC + 120, y, 1.25))[0] - XC
        xi = edge(inner, (XC, y, 1.25), (XC + 120, y, 1.25))[0] - XC
        hwd[y] = (round(xd, 2), round(xi - xd, 2))
    out['halfwidth_and_xgap_to_INNER'] = hwd
    out['interf'] = X.interference(door, [X.body('HOUSING_E'), X.body('SLAB_frame'), X.body('LCD_glass')])
    log('v5f_b1a_door', 'DOOR_F', out)
    print(json.dumps(out))
