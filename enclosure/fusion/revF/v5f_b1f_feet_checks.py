# rev F block 1f (2026-11-03): SJ5012 feet (D12.7 x 3.5, in the D13 x 0.5 recesses: z 0.5 -> -3.0) as FOOT_* envelopes,
# block 1 interference matrix (new bodies vs every LCD_* / slab / glass / housing / door / envelope) and door-gap probes.
# --- paste v5f_common.py above this line ---
SCREWS = {'FL': (XC + 88.5, -7.0), 'FR': (XC - 88.5, -7.0), 'ML': (XC + 75.5, -45.75), 'MR': (XC - 75.5, -45.75),
          'RL': (XC + 44.0, -68.5), 'RR': (XC - 44.0, -68.5)}


def run(_context):
    X = Ctx()
    out = {}
    feet = []
    for k, (x, y) in SCREWS.items():
        old = X.body('FOOT_' + k)
        if old is None:
            feet.append(X.add(X.wcyl_z(x, y, 6.35, -3.0, 0.5), 'FOOT_' + k))
    names = [b.name for b in X.comp.bRepBodies]
    lcd = [X.body(n) for n in names if n.startswith('LCD_')]
    new = [X.body(n) for n in ('DOOR_F', 'PI5_F', 'PI5_F_cooler', 'GPIO_plugA_env', 'GPIO_plugB_env')] + [X.body('FOOT_' + k) for k in SCREWS]
    hb = X.body('HOUSING_E'); slab = X.body('SLAB_frame')
    def bbox_overlap(a, b):
        A = a.boundingBox; B = b.boundingBox
        return all(A.minPoint.asArray()[i] <= B.maxPoint.asArray()[i] and B.minPoint.asArray()[i] <= A.maxPoint.asArray()[i] for i in range(3))
    mat = {}; npairs = 0; nchecked = 0
    for b in new:
        cands = [o for o in [hb, slab] + lcd if o is not None]
        npairs += len(cands)
        cands = [o for o in cands if bbox_overlap(b, o)]
        nchecked += len(cands)
        r = X.interference(b, cands)
        mat[b.name] = {k: v for k, v in r.items() if v > 0} or 'all 0'
    out['interference_nonzero'] = mat
    out['pairs'] = {'total': npairs, 'bbox_overlapping_checked': nchecked}
    out['door_vs_feet'] = X.interference(X.body('DOOR_F'), [X.body('FOOT_' + k) for k in SCREWS])
    # door edge gap to the shell inner face, measured along +-x / -y at z 1.25 (D1 layer will take 0.7 of it in block 5)
    def gap(x0, y0, dx, dy):
        door = X.body('DOOR_F')
        lo, hi = 0.0, 30.0
        for _ in range(30):
            m = (lo + hi) / 2
            if X.inside(door, x0 + dx * m, y0 + dy * m, 1.25): lo = m
            else: hi = m
        d_edge = lo
        lo2, hi2 = d_edge, d_edge + 2.0     # +2.0 lands inside the 2.5 wall
        for _ in range(30):
            m = (lo2 + hi2) / 2
            if X.inside(hb, x0 + dx * m, y0 + dy * m, 1.25): hi2 = m
            else: lo2 = m
        return round(hi2 - d_edge, 2)
    out['door_gap_mm'] = {'+x@y-7': gap(XC + 92.5, -7.0, 1, 0), '-x@y-7': gap(XC - 92.5, -7.0, -1, 0),   # start outside the counterbores
                          '+x@y-45.75': gap(XC + 80, -45.75, 1, 0), 'back@XC': gap(XC, -70.0, 0, -1),
                          'front@XC': gap(XC, -5.0, 0, 1)}
    log('v5f_b1f_feet_checks', 'feet + checks', out)
    print(json.dumps(out))
