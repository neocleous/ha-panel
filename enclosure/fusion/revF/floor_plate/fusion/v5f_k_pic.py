# rev F fix pass (2026-11-12) - pictures and tool templates. Run through k.step(); the library is the global k.
#   Template bodies are named AUD_*, are never joined to a part and are deleted with X.wipe() before any save.
#   The picture itself is taken with the connector's screenshot query after view() has set the camera.
APP = {'grey': 'Plastic - Matte (Gray)', 'white': 'Plastic - Matte (White)', 'green': 'Plastic - Matte (Green)', 'yellow': 'Plastic - Matte (Yellow)',
       'red': 'Paint - Enamel Glossy (Red)', 'blue': 'Paint - Enamel Glossy (Blue)', 'steel': 'Steel - Satin'}


def aud(X, tb, name, colour='grey'):                 # a temporary body into the model as a template
    b = X.root.bRepBodies.add(tb)
    b.name = 'AUD_' + name
    a = X.des.appearances.itemByName(APP[colour])
    if a is not None:
        b.appearance = a
    b.isLightBulbOn = True
    return b


def tool(X, o, u, secs):                             # a tool as one solid: sections [(dia, length), ...] from the working end o along u
    u = k.unit(u); s = 0.0; out = None
    for dia, L in secs:
        t = X.cyl(k.along(o, u, s - (0.02 if s > 0 else 0.0)), k.along(o, u, s + L), dia / 2.0)
        out = t if out is None else X.uni(out, t)
        s += L
    return out


def screw(X, seat, u_out, d=3.0, L=8.0, head_d=5.7, head_h=1.65):   # a screw: seat = centre of the head's seat, u_out = from the seat out of the head
    u = k.unit(u_out)
    t = X.cyl(seat, k.along(seat, u, head_h), head_d / 2.0)
    X.uni(t, X.cyl(k.along(seat, u, 0.02), k.along(seat, u, -L), d / 2.0))
    return t


def clash(X, tb, bodies, eps=0.005):                 # mm3 of a temporary body inside model bodies (big bodies through their slabs)
    out = {}
    for b in bodies:
        if not tb.boundingBox.intersects(b.boundingBox):
            continue
        v = k.xvol(X, tb, b.name)
        if abs(v) > eps:
            out[b.name] = round(v, 2)
    return out


def slices(X, names, box, prefix, colours=None):     # crops of model bodies to a world box, added as templates
    out = []
    for i, n in enumerate(names):
        col = (colours or {}).get(n, 'grey')
        for j, p in enumerate(k.region(X, n, prefix, box)):
            out.append(aud(X, X.cp(p), '%s_%s_%d' % (prefix, n, j), col))
    return out


def only(X, names=(), prefixes=('AUD_',)):           # show the templates (and the bodies named) and nothing else; returns what was visible
    was = [b.name for b in X.root.bRepBodies if b.isLightBulbOn]
    want = set(names)
    for b in X.root.bRepBodies:
        on = b.name in want or b.name.startswith(tuple(prefixes))
        if b.isLightBulbOn != on:
            b.isLightBulbOn = on
    return was


def restore(X, was):
    want = set(was)
    for b in X.root.bRepBodies:
        on = b.name in want
        if b.isLightBulbOn != on:
            b.isLightBulbOn = on


def view(X, eye, tgt, ext=None, angle=None, up=(0, 0, 1)):
    k.cam(X, eye, tgt, ext=ext, angle=angle, up=up)
