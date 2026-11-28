"""Draw a KiCad board to scale as SVG, every element tagged for the focus viewer.

Tokens on elements (data-k, space separated):
  p:<board>:<ref>   a part (its body, pads and label)
  n:<board>:<net>   a pad on that net
  l:<n>             a lead's stub and tag
"""
from __future__ import annotations

import html
import math

import panel

GND_LIKE = {"GND"}


def esc(s):
    return html.escape(str(s), quote=True)


class View:
    def __init__(self, board, scale, ox, oy, mirror=False, width=None):
        self.b = board
        self.s = scale
        self.ox, self.oy = ox, oy
        self.mirror = mirror
        self.W = board["bbox"][2] - board["bbox"][0]

    def xy(self, p):
        x, y = p
        x -= self.b["bbox"][0]
        y -= self.b["bbox"][1]
        if self.mirror:
            x = self.W - x
        return self.ox + x * self.s, self.oy + y * self.s

    def path_outline(self):
        d = []
        for i, seg in enumerate(self.b["outline"]):
            pts = [self.xy(p) for p in seg["pts"]]
            if i == 0:
                d.append(f"M{pts[0][0]:.1f},{pts[0][1]:.1f}")
            if seg["k"] == "line":
                d.append(f"L{pts[1][0]:.1f},{pts[1][1]:.1f}")
            elif seg["k"] == "arc":
                (x0, y0), (x1, y1), (x2, y2) = pts
                r, sweep, large = _arc(x0, y0, x1, y1, x2, y2)
                d.append(f"A{r:.2f},{r:.2f} 0 {large} {sweep} {x2:.1f},{y2:.1f}")
        return " ".join(d) + " Z"


def _arc(x0, y0, x1, y1, x2, y2):
    ax, ay, bx, by, cx, cy = x0, y0, x1, y1, x2, y2
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    r = math.hypot(ax - ux, ay - uy)
    cross = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
    sweep = 1 if cross > 0 else 0
    a0 = math.atan2(ay - uy, ax - ux)
    a2 = math.atan2(cy - uy, cx - ux)
    a1 = math.atan2(by - uy, bx - ux)
    def between(a, s, e, ccw):
        if ccw:
            return (a - s) % (2 * math.pi) <= (e - s) % (2 * math.pi)
        return (s - a) % (2 * math.pi) <= (s - e) % (2 * math.pi)
    ccw = sweep == 1
    span = (a2 - a0) % (2 * math.pi) if ccw else (a0 - a2) % (2 * math.pi)
    large = 1 if span > math.pi else 0
    return r, sweep, large


def prim_svg(v, g, cls):
    if g["k"] == "line":
        (x0, y0), (x1, y1) = v.xy(g["pts"][0]), v.xy(g["pts"][1])
        return f'<line class="{cls}" x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}"/>'
    if g["k"] == "poly":
        pts = " ".join(f"{a:.1f},{b:.1f}" for a, b in (v.xy(p) for p in g["pts"]))
        return f'<polygon class="{cls}" points="{pts}"/>'
    if g["k"] == "circle":
        cx, cy = v.xy(g["c"])
        return f'<circle class="{cls}" cx="{cx:.1f}" cy="{cy:.1f}" r="{g["r"] * v.s:.1f}"/>'
    if g["k"] == "arc":
        (x0, y0), (x1, y1), (x2, y2) = (v.xy(p) for p in g["pts"])
        r, sweep, large = _arc(x0, y0, x1, y1, x2, y2)
        return f'<path class="{cls}" d="M{x0:.1f},{y0:.1f} A{r:.1f},{r:.1f} 0 {large} {sweep} {x2:.1f},{y2:.1f}"/>'
    return ""


def pad_svg(v, pad, tokens, extra_cls=""):
    cx, cy = v.xy(pad["xy"])
    w, h = pad["size"][0] * v.s, pad["size"][1] * v.s
    ang = -pad["angle"] if not v.mirror else pad["angle"]
    net = pad["net"]
    job = panel.NET_JOB.get(net) if net else None
    cls = "pad" + (f" pj f-{job}" if job else "") + (" pnc" if net is None else "") + (" " + extra_cls if extra_cls else "")
    k = " ".join(tokens + ([f"n:{v.b['key']}:{net}"] if net else []))
    shape = pad["shape"]
    if shape == "circle" or (shape == "oval" and abs(w - h) < 0.01):
        el = f'<circle class="{cls}" cx="{cx:.1f}" cy="{cy:.1f}" r="{w / 2:.1f}"/>'
    else:
        rx = min(w, h) / 2 if shape == "oval" else (min(w, h) * 0.25 if shape == "roundrect" else 0)
        el = (f'<rect class="{cls}" x="{cx - w / 2:.1f}" y="{cy - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx:.1f}"'
              f' transform="rotate({ang:.1f} {cx:.1f} {cy:.1f})"/>')
    drill = ""
    if pad.get("drill"):
        drill = f'<circle class="drill" cx="{cx:.1f}" cy="{cy:.1f}" r="{pad["drill"] * v.s / 2:.1f}"/>'
    return f'<g data-k="{esc(k)}">{el}{drill}</g>'


def part_svg(v, part, label=True, side_layers=None):
    """A part: its body outline (fabrication layer), pads and its reference."""
    b = v.b["key"]
    tok = [f"p:{b}:{part['ref']}"]
    fab = "F.Fab" if part["side"] == "F" else "B.Fab"
    out = [f'<g data-k="{esc(tok[0])}" class="part-g">']
    body_cls = "body" + (" dnp" if part["dnp"] else "") + (" mhole-b" if part["ref"].startswith("H") else "")
    for g in part["graphics"].get(fab, []):
        out.append(prim_svg(v, g, body_cls))
    out.append("</g>")
    for pad in part["pads"]:
        out.append(pad_svg(v, pad, tok))
    if label:
        xs, ys = [], []
        for g in part["graphics"].get(fab, []) or []:
            pts = g.get("pts") or ([(g["c"][0] - g["r"], g["c"][1] - g["r"]), (g["c"][0] + g["r"], g["c"][1] + g["r"])] if g["k"] == "circle" else [])
            for p in pts:
                X, Y = v.xy(p)
                xs.append(X); ys.append(Y)
        if not xs:
            for pad in part["pads"]:
                X, Y = v.xy(pad["xy"]); xs.append(X); ys.append(Y)
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        span = max(max(xs) - min(xs), max(ys) - min(ys))
        fs = max(6.5, min(13.0, span * 0.32))
        out.append(f'<text class="t-ref{" dnp-t" if part["dnp"] else ""}" data-k="{esc(tok[0])}" x="{cx:.1f}" y="{cy + fs * 0.35:.1f}" '
                   f'text-anchor="middle" style="font-size:{fs:.1f}px">{esc(part["ref"])}</text>')
    return "".join(out)
