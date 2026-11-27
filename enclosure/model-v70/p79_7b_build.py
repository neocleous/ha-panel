# Part A of claude/architect-log-2026-11-25-b.md §4 (block 7b): five changes to blocks 6 and 7, built as temporary bodies.
# CHANGES NOTHING IN THE DOCUMENT. Stages (each from the model's own body at version 77; results in k.c):
#   'cap'    D435 the eight strip pads 0.6 tall (face z 177.7, bed 2.3 at 0.10 layers); the four pins' tips 0.2 lower
#            (z 177.2, bed 2.8), 0.3 above the toes as block 6 has them;  D436 the lip over the shell's shelf opened to 0.30:
#            the cap's underside over the shelf raised 0.2, to z 177.7 (bed 2.3), only where the cap's underside is the lip
#            (not through a wall)                                                              -> b7b_cap
#   'clamp'  D435 the step 0.6: toes z 177.1 -> 176.9 (bed 4.2), ledges 176.7 -> 176.5 (bed 3.8), the bar under the strip's
#            back 175.1 -> 174.9 (bed 2.2), so it keeps its 2.0 to the strip's back face   -> b7b_clampL, b7b_clampR
#   'strip'  the strip envelopes 0.2 lower at the strip and still to the ceiling (z 176.9..178.3); the keep-outs to 0.3
#            under the strip (176.6), less the clamp                                       -> b7b_stripL/R, b7b_koL/R
#   'boxR'   D438 the right box cut back by the shell's inner face set off 0.48 (true distance: the union of the shell's
#            local copies moved 0.48 along 33 directions within 70 deg of +x), over z 76.5..84, back of the front face's
#            plane (y <= -3.7)                                                                 -> b7b_boxR
#   'clip'   D439 the clip's step face on the box's front face (y -3.7) moved 0.4 forward (y -3.3), so that as modelled the
#            clip stands 0.4 off its stop with its tongue on the board, the screw centred in the 0.8 slot; right = left
#            turned top for bottom                                                             -> b7b_clipL, b7b_clipR
# Run: runpy.run_path(D + 'p79_7b_build.py')['main'](stage)  -> p79_<stage>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
PADS_X = ((8.3, 9.9), (36.1, 37.7)); PADS_Y = ((-29.7, -28.1), (-24.9, -23.3))


def bx(X, sx, x0, x1, y0, y1, z0, z1):
    a, b = sorted((sx * x0, sx * x1)); return X.wbox(a, b, y0, y1, z0, z1)


def ivals(k, X, b, p0, p1):
    L_ = math.sqrt(sum((p1[i] - p0[i]) ** 2 for i in range(3)))
    u = [(p1[i] - p0[i]) / L_ for i in range(3)]
    return [(tuple(round(p0[i] + u[i] * s, 3) for i in range(3)), tuple(round(p0[i] + u[i] * e, 3) for i in range(3)))
            for s, e in k.needle_t(X, [b], p0, p1, 0.02)]


def cap(k, X):
    t = X.tbm.copy(X.body('HOUSING_F_cap')); v0 = X.vol(t)
    for sx in (1, -1):
        for a, b in PADS_X:
            for y0, y1 in PADS_Y:
                X.uni(t, bx(X, sx, a, b, y0, y1, 177.7, 177.95))
        for xp in (11.5, 30.0):
            X.uni(t, X.cyl((sx * xp, -26.5, 177.2), (sx * xp, -26.5, 177.45), 0.75))
    v1 = X.vol(t)
    print('pads to 0.6 and pins 0.2 longer: +%.4f mm3' % (v1 - v0))
    # the lip: where along x is the cap's underside at the shelf the lip (no cap below 177.6 at y -22.9) and the shell's shelf there
    c0 = X.tbm.copy(X.body('HOUSING_F_cap')); s0 = X.tbm.copy(X.body('HOUSING_F_front'))
    walls = [(round(-120 + a, 2), round(-120 + b, 2)) for a, b in k.needle_t(X, [c0], (-120.0, -22.9, 177.45), (120.0, -22.9, 177.45), 0.02)]
    lipc = [(round(-120 + a, 2), round(-120 + b, 2)) for a, b in k.needle_t(X, [c0], (-120.0, -22.9, 177.6), (120.0, -22.9, 177.6), 0.02)]
    shelf = [(round(-120 + a, 2), round(-120 + b, 2)) for a, b in k.needle_t(X, [s0], (-120.0, -22.9, 177.3), (120.0, -22.9, 177.3), 0.02)]
    print('at y -22.9: cap solid at z 177.45 (walls reaching below the lip): %s' % walls)
    print('            cap solid at z 177.6: %s' % lipc)
    print('            shell solid at z 177.3 (the shelf): %s' % shelf)
    # cut the cap's underside 177.5 -> 177.7 over y -23.65..-22.3 (0.35 behind the shelf's back edge at y -23.3) where the cap is solid at 177.6 and not at 177.45
    spans = []
    for a, b in lipc:
        cur = a
        for wa, wb in sorted(walls):
            if wb <= cur or wa >= b:
                continue
            if wa > cur:
                spans.append((cur, wa))
            cur = max(cur, wb)
        if cur < b:
            spans.append((cur, b))
    spans = [(a + 0.05, b - 0.05) for a, b in spans if b - a > 0.5]
    print('lip spans cut (x): %s' % [(round(a, 2), round(b, 2)) for a, b in spans])
    for a, b in spans:
        X.dif(t, X.wbox(a, b, -23.65, -22.3, 177.45, 177.7))
    print('HOUSING_F_cap: %.3f -> %.3f mm3 (lip %.4f off), lumps %d, faces %d' % (v0, X.vol(t), v1 - X.vol(t), t.lumps.count, t.faces.count))
    k.c['b7b_cap'] = t


def clamp(k, X):
    for sx, nm in ((1, 'MIC_CLAMP_L'), (-1, 'MIC_CLAMP_R')):
        b = X.body(nm); t = X.tbm.copy(b); v0 = X.vol(t)
        for a, c in ((9.8, 11.8), (29.0, 31.0)):
            X.dif(t, bx(X, sx, a, c, -28.5, -24.5, 176.9, 177.15))      # toes 177.1 -> 176.9
            X.dif(t, bx(X, sx, a, c, -29.9, -28.5, 176.5, 176.75))      # ledges 176.7 -> 176.5
        # the bar: the +z faces at 175.1 in front of the slot (y > -31)
        cut = 0
        for f in b.faces:
            if f.geometry.surfaceType != k.PLN:
                continue
            ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); n = k.wv(nv); c = k.W(f.centroid)
            if n[2] > 0.99 and abs(c[2] - 175.1) < 0.01 and c[1] > -31.0:
                pts = [k.W(v.geometry) for v in f.vertices]
                x0 = min(p[0] for p in pts); x1 = max(p[0] for p in pts); y0 = min(p[1] for p in pts); y1 = max(p[1] for p in pts)
                X.dif(t, X.wbox(x0, x1, y0, y1, 174.9, 175.1))
                cut += 1
                print('   %s bar face %.2f mm2, x %.2f..%.2f, y %.2f..%.2f: top 175.1 -> 174.9' % (nm, f.area * 100, x0, x1, y0, y1))
        print('%s: %.3f -> %.3f mm3, lumps %d, faces %d (%d bar faces)' % (nm, v0, X.vol(t), t.lumps.count, t.faces.count, cut))
        k.c['b7b_clamp' + nm[-1]] = t
    print('L vs R: %.4f / %.4f' % (X.vol(k.c['b7b_clampL']), X.vol(k.c['b7b_clampR'])))


def strip(k, X):
    for sx, s in ((1, 'L'), (-1, 'R')):
        e = X.body('MIC_strip_%s_env' % s); t = X.tbm.copy(e); v0 = X.vol(t)
        X.uni(t, X.move(X.tbm.copy(e), 0, 0, -0.2))
        print('MIC_strip_%s_env: %.3f -> %.3f, box %s' % (s, v0, X.vol(t), k.wbb(X, t)))
        k.c['b7b_strip' + s] = t
        ko = bx(X, sx, 9.5, 37.5, -29.5, -23.5, 166.5, 176.6); X.dif(ko, X.tbm.copy(k.c['b7b_clamp' + s]))
        print('KO_mic_%s_back: %.3f -> %.3f' % (s, X.body('KO_mic_%s_back' % s).volume * 1000, X.vol(ko)))
        k.c['b7b_ko' + s] = ko


def dirs(maxdeg=70, rings=(0, 20, 40, 55, 70), per=8):
    out = [(1.0, 0.0, 0.0)]
    for th in rings[1:]:
        for i in range(per):
            ph = 2 * math.pi * i / per; t = math.radians(th)
            out.append((math.cos(t), math.sin(t) * math.cos(ph), math.sin(t) * math.sin(ph)))
    return out


def boxR(k, X):
    k.budget(78)
    B = X.body('SPKBOX_R'); t = X.tbm.copy(B); v0 = X.vol(t)
    sh = X.wbox(-100, -86, -56, -3.0, 72, 87); X.sec(sh, X.tbm.copy(X.body('HOUSING_F_front')))
    cut = None
    ds = dirs()
    for d in ds:
        c = X.move(X.tbm.copy(sh), 0.48 * d[0], 0.48 * d[1], 0.48 * d[2])
        cut = c if cut is None else X.uni(cut, c)
    X.sec(cut, X.wbox(-97, -86, -53, -3.7, 76.5, 84))
    off = X.xv(t, cut)
    X.dif(t, cut)
    print('cutter: the shell set off 0.48 along %d directions within 70 deg of +x; %.4f mm3 of the box inside it' % (len(ds), off))
    print('SPKBOX_R: %.3f -> %.3f, lumps %d, faces %d' % (v0, X.vol(t), t.lumps.count, t.faces.count))
    k.c['b7b_boxR'] = t


def clip(k, X):
    t = X.tbm.copy(X.body('TOUCH_CLIP_L')); v0 = X.vol(t)
    X.dif(t, X.wbox(43.45, 45.05, -3.75, -3.3, 29.9, 46.1))
    print('TOUCH_CLIP_L: %.3f -> %.3f, lumps %d, faces %d, box %s' % (v0, X.vol(t), t.lumps.count, t.faces.count, k.wbb(X, t)))
    r = X.tbm.copy(t)
    m = adsk.core.Matrix3D.create(); m.setToRotation(math.pi, k.dv((0, 1, 0)), k.Wp(0.0, 0.0, 38.0)); X.tbm.transform(r, m)
    print('TOUCH_CLIP_R (the left turned top for bottom): %.3f, box %s' % (X.vol(r), k.wbb(X, r)))
    k.c['b7b_clipL'] = t; k.c['b7b_clipR'] = r


def _main(stage):
    k = L['load'](); X = k.K(); k.budget(70)
    print(L['stamp'](), 'before', X.state())
    {'cap': cap, 'clamp': clamp, 'strip': strip, 'boxR': boxR, 'clip': clip}[stage](k, X)
    print(L['stamp'](), 'after', X.state())


def main(stage):
    L['out']('p79_%s.txt' % stage, _main, stage)
