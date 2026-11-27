"""Read a KiCad 9 board (and its schematic sheets) into plain data for the guide.

Every pad position, net, outline, body and hole on the page comes from here. Nothing about a
board is typed by hand anywhere else in the generator.

Coordinates stay in KiCad's board frame (mm, x right, y down, as seen from the front copper).
"""
from __future__ import annotations

import glob
import math
import os
import re

from kiutils.board import Board


def _rot(x, y, deg):
    """KiCad's rotation of a footprint-local point (y down, angle counter-clockwise on screen)."""
    a = math.radians(deg or 0.0)
    c, s = math.cos(a), math.sin(a)
    return x * c + y * s, -x * s + y * c


def _abs(fp, x, y):
    dx, dy = _rot(x, y, fp.position.angle)
    return round(fp.position.X + dx, 4), round(fp.position.Y + dy, 4)


def _dnp_refs(sch_dir):
    refs = set()
    for f in glob.glob(os.path.join(sch_dir, "*.kicad_sch")):
        s = open(f, encoding="utf8").read()
        for m in re.finditer(r'\(symbol\s+\(lib_id "[^"]+"\)(.*?)\(property "Reference" "([^"]+)"', s, re.S):
            if "(dnp yes)" in m.group(1):
                refs.add(m.group(2))
    return refs


def _graphic(fp, g):
    """One footprint graphic as an absolute primitive, or None."""
    t = type(g).__name__
    if t == "FpLine":
        return {"k": "line", "pts": [_abs(fp, g.start.X, g.start.Y), _abs(fp, g.end.X, g.end.Y)], "w": g.stroke.width if g.stroke else 0.1}
    if t == "FpRect":
        x0, y0, x1, y1 = g.start.X, g.start.Y, g.end.X, g.end.Y
        return {"k": "poly", "pts": [_abs(fp, x0, y0), _abs(fp, x1, y0), _abs(fp, x1, y1), _abs(fp, x0, y1)], "w": g.stroke.width if g.stroke else 0.1, "fill": bool(g.fill and g.fill != "none")}
    if t == "FpCircle":
        cx, cy = _abs(fp, g.center.X, g.center.Y)
        r = math.hypot(g.end.X - g.center.X, g.end.Y - g.center.Y)
        return {"k": "circle", "c": (cx, cy), "r": round(r, 4), "w": g.stroke.width if g.stroke else 0.1, "fill": bool(g.fill and g.fill not in ("none", "no"))}
    if t == "FpArc":
        return {"k": "arc", "pts": [_abs(fp, g.start.X, g.start.Y), _abs(fp, g.mid.X, g.mid.Y), _abs(fp, g.end.X, g.end.Y)], "w": g.stroke.width if g.stroke else 0.1}
    if t == "FpPoly":
        return {"k": "poly", "pts": [_abs(fp, p.X, p.Y) for p in g.coordinates], "w": g.stroke.width if g.stroke else 0.1, "fill": bool(g.fill and g.fill not in ("none", "no"))}
    return None


def _outline(board):
    segs = []
    for g in board.graphicItems:
        if getattr(g, "layer", "") != "Edge.Cuts":
            continue
        t = type(g).__name__
        if t == "GrLine":
            segs.append({"k": "line", "pts": [(g.start.X, g.start.Y), (g.end.X, g.end.Y)]})
        elif t == "GrArc":
            segs.append({"k": "arc", "pts": [(g.start.X, g.start.Y), (g.mid.X, g.mid.Y), (g.end.X, g.end.Y)]})
        elif t == "GrRect":
            x0, y0, x1, y1 = g.start.X, g.start.Y, g.end.X, g.end.Y
            segs += [{"k": "line", "pts": [a, b]} for a, b in [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]]
        elif t == "GrCircle":
            segs.append({"k": "circle", "c": (g.center.X, g.center.Y), "r": math.hypot(g.end.X - g.center.X, g.end.Y - g.center.Y)})
    return segs


def _chain(segs):
    """Order outline segments into one closed path of points (arcs kept as start/mid/end)."""
    if not segs:
        return []
    rest = segs[:]
    path = [rest.pop(0)]
    def close(a, b):
        return abs(a[0] - b[0]) < 1e-3 and abs(a[1] - b[1]) < 1e-3
    while rest:
        end = path[-1]["pts"][-1]
        for i, s in enumerate(rest):
            if close(s["pts"][0], end):
                path.append(rest.pop(i)); break
            if close(s["pts"][-1], end):
                s = dict(s); s["pts"] = list(reversed(s["pts"])); rest.pop(i); path.append(s); break
        else:
            raise ValueError("board outline does not close")
    return path


def extract(pcb_path):
    board = Board.from_file(pcb_path)
    dnp = _dnp_refs(os.path.dirname(pcb_path))
    parts = []
    for fp in board.footprints:
        props = fp.properties
        ref = props["Reference"]
        side = "F" if fp.layer == "F.Cu" else "B"
        pads = []
        for p in fp.pads:
            x, y = _abs(fp, p.position.X, p.position.Y)
            pads.append({
                "num": str(p.number),
                "xy": (x, y),
                "shape": p.shape,
                "size": (p.size.X, p.size.Y),
                "angle": (p.position.angle or 0.0),
                "type": p.type,
                "drill": (p.drill.diameter if p.drill and p.drill.diameter else None),
                "net": (p.net.name if p.net else None),
                "layers": list(p.layers),
            })
        gr = {}
        for g in fp.graphicItems:
            if type(g).__name__ == "FpText":
                continue
            prim = _graphic(fp, g)
            if prim:
                gr.setdefault(g.layer, []).append(prim)
        parts.append({
            "ref": ref,
            "value": props.get("Value", ""),
            "lib": fp.libId,
            "side": side,
            "at": (fp.position.X, fp.position.Y),
            "rot": fp.position.angle or 0.0,
            "type": fp.attributes.type,
            "dnp": ref in dnp,
            "pads": pads,
            "graphics": gr,
        })
    texts = []
    for g in board.graphicItems:
        if type(g).__name__ == "GrText":
            texts.append({"layer": g.layer, "text": g.text, "xy": (g.position.X, g.position.Y), "angle": g.position.angle or 0.0})
    outline = _chain(_outline(board))
    xs = [p[0] for s in outline for p in s["pts"]]
    ys = [p[1] for s in outline for p in s["pts"]]
    return {
        "file": os.path.relpath(pcb_path, os.path.join(os.path.dirname(__file__), "..", "..")),
        "outline": outline,
        "bbox": (min(xs), min(ys), max(xs), max(ys)),
        "parts": sorted(parts, key=lambda p: (re.sub(r"\d+", "", p["ref"]), int(re.sub(r"\D", "", p["ref"]) or 0))),
        "texts": texts,
    }
