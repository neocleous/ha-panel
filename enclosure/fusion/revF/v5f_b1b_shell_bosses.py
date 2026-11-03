# rev F block 1b (2026-11-03): six door-screw bosses on the shell (K8, Daniel: M3 standard, Ruthex RX-M3x5.7).
# Axes (world, x rel. XC): front +-88.5 @ y -7.0, middle +-75.5 @ y -45.75 (on the planned back partitions), rear +-44.0 @ y -68.5.
# Boss D8 z 5.0 (bottom face, on the door pad) -> 12.7; insert hole D4.0 z 5.0 -> 11.7 (L 5.7 + 1); rib 2.0 thick to the
# nearest INNER_E wall (+0.5 embed), z 5.0 -> 12.7. Built with TemporaryBRep in world coordinates, added as NEW bodies,
# interference-checked, then combine JOIN into HOUSING_E (explicit tools only; no extrude JOIN).
# --- paste v5f_common.py above this line ---
AXES = {'FL': (XC + 88.5, -7.0), 'FR': (XC - 88.5, -7.0), 'ML': (XC + 75.5, -45.75), 'MR': (XC - 75.5, -45.75),
        'RL': (XC + 44.0, -68.5), 'RR': (XC - 44.0, -68.5)}
RB, Z0, Z1, RH, ZH = 4.0, 5.0, 12.7, 2.0, 11.7     # boss radius, bottom, top, hole radius, hole top


def run(_context):
    X = Ctx()
    inner = X.body('INNER_E'); hb = X.body('HOUSING_E')
    out = {'axes': {k: (round(v[0], 2), v[1]) for k, v in AXES.items()}, 'ribs': {}}

    def wall_dir(x, y, z=9.0, n=36):
        best = (1e9, None)
        for i in range(n):
            a = 2 * math.pi * i / n; lo, hi = 0.0, 40.0
            for _ in range(18):
                m = (lo + hi) / 2
                if X.inside(inner, x + m * math.cos(a), y + m * math.sin(a), z): lo = m
                else: hi = m
            if lo < best[0]: best = (lo, a)
        return best

    tools = []
    for k, (x, y) in AXES.items():
        d, a = wall_dir(x, y)
        out['ribs'][k] = (round(d, 2), round(math.degrees(a), 1))
        tb = X.wcyl_z(x, y, RB, Z0, Z1)
        L = d + 0.5                                   # rib length from the axis to 0.5 inside the wall
        c = (x + math.cos(a) * L / 2, y + math.sin(a) * L / 2, (Z0 + Z1) / 2)
        ldir = V3(math.cos(a), math.sin(a) * C, -math.sin(a) * S)
        wdir = V3(-math.sin(a), math.cos(a) * C, -math.cos(a) * S)
        obb = adsk.core.OrientedBoundingBox3D.create(Dw(*c), ldir, wdir, L / 10, RH / 10, (Z1 - Z0) / 10)
        X.union(tb, X.tbm.createBox(obb))
        X.diff(tb, X.wcyl_z(x, y, 2.0, Z0 - 0.5, ZH))   # D4.0 hole, open at the bottom
        b = X.add(tb, 'DBOSS_' + k)
        tools.append(b)
    others = [X.body(n) for n in ('SLAB_frame', 'LCD_glass', 'DOOR_F', 'LCD_panel_body', 'LCD_pcb_76x110')]
    out['interf'] = {t.name: X.interference(t, others) for t in tools}
    bad = {k: v for k, v in out['interf'].items() if any(val > 0 for val in v.values())}
    if bad:
        log('v5f_b1b_shell_bosses', 'ABORT interference', out)
        raise RuntimeError('interference: %s' % json.dumps(bad))
    v0 = hb.volume
    X.combine(hb, tools)
    hb = X.body('HOUSING_E')
    out['housing_vol'] = (round(v0, 2), round(hb.volume, 2))
    out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('DBOSS_')]
    pr = {}
    for k, (x, y) in AXES.items():
        pr[k] = {'hole_z8_open': not X.inside(hb, x, y, 8.0), 'wall_r3_z8': X.inside(hb, x + 3.0, y, 8.0) or X.inside(hb, x - 3.0, y, 8.0),
                 'cap_z12.2': X.inside(hb, x, y, 12.2), 'below_z4.5_open': not X.inside(hb, x, y, 4.5)}
    out['probes'] = pr
    log('v5f_b1b_shell_bosses', 'bosses', out)
    print(json.dumps(out))
