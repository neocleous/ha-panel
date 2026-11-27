"""Checks the build runs. Any failure stops the build (non-zero exit) before a page is written."""
from __future__ import annotations

import re
from collections import Counter

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import polygonize, unary_union

import panel
from model import net_class

SUPPLY_CLASSES = {"class:3v3": "3v3", "class:5v": "5v"}
# Supplies are checked by class (a 3.3 V pin must land on a 3.3 V net); signals by their exact net.
ROLE_CLASS = {"+3V3": "class:3v3", "3V3_SENS": "class:3v3", "5V_RADAR": "class:5v"}


def _role_key(role):
    return ROLE_CLASS.get(role, role)


def _net_key(net):
    if net is None:
        return None
    c = net_class(net)
    if c in ("3v3", "5v") and net not in ("PI_3V3",):
        return f"class:{c}"
    return net


def _fn(label):
    """Function word of a microphone pin label: VDD, GND, CLK, DATA, SEL (L/R)."""
    last = label.split()[-1]
    return "SEL" if last in ("SEL", "L/R") else last


def _shape(prims):
    """A courtyard or body outline as one shapely polygon."""
    polys, lines = [], []
    for g in prims:
        if g["k"] == "poly":
            polys.append(Polygon(g["pts"]))
        elif g["k"] == "circle":
            polys.append(Point(g["c"]).buffer(g["r"]))
        elif g["k"] == "line":
            lines.append(LineString(g["pts"]))
        elif g["k"] == "arc":
            lines.append(LineString(g["pts"]))
    if lines:
        polys += list(polygonize(unary_union(lines)))
    return unary_union(polys) if polys else None


def run(model):
    fails, passes = [], []

    # 1. The page's lead table against the KiCad nets: gpio-leads.md names the net at each pad.
    for r in model.gpio:
        ref, num = r["pad"].split(".")
        net = model.pad("main", ref, num)["net"]
        first = re.split(r"[\s←→(]", r["net_text"].strip())[0]
        if first != net:
            fails.append(f"gpio-leads.md says {r['pad']} is {first}; the board says {net}")
    passes.append("13 Pi signal wires: pad nets in gpio-leads.md agree with the board file")

    # 2. Every wire end exists, and no pin or hole takes two wires.
    ends = Counter()
    for l in model.leads:
        for a, b in l["wires"]:
            for pid in (a, b):
                model.pin_info(pid)  # raises on an unknown pad or pin
                ends[pid] += 1
    twice = [p for p, c in ends.items() if c > 1]
    for p in twice:
        fails.append(f"{p} takes {ends[p]} wires")
    passes.append(f"{sum(ends.values())} wire ends land on {len(ends)} distinct pads and pins; none used twice")

    # 3. Shorts and wrong landings: inside one connected group every role and every board net must agree.
    groups = model.groups()
    for g in groups:
        main_nets = {x.split(":", 2)[2] for x in g if x.startswith("net:main:")}
        if len(main_nets) > 1:
            fails.append(f"short: {sorted(main_nets)} are joined by {sorted(x for x in g if not x.startswith('net:'))}")
        keys = {_net_key(n) for n in main_nets}
        fns = set()
        for pid in g:
            if pid.startswith("net:"):
                continue
            kind, label, net, role = model.pin_info(pid)
            if role is not None:
                keys.add(_role_key(role))
            if pid.split(":")[0] in ("micL", "micR", "respeaker"):
                fns.add(_fn(label))
        keys.discard(None)
        if len(keys) > 1:
            fails.append(f"wrong landing: {sorted(keys)} meet in {sorted(x for x in g if not x.startswith('net:'))}")
        if len(fns) > 1:
            fails.append(f"microphone functions differ: {sorted(fns)} in {sorted(g)}")
    passes.append(f"{len(groups)} connected groups across boards and modules: no short, every pin on the net it is made for")

    # 4. Split or missing: every pin that must carry a net is wired; every pin that must stay free is free.
    for dev, mod in panel.MODULES.items():
        for pin, (label, role) in mod["pins"].items():
            pid = f"{dev}:{pin}"
            wired = ends[pid] > 0 or any(pid in (l.get("bridge") or ()) for l in model.leads)
            if role is not None and not wired:
                fails.append(f"split: {mod['name']} {label} ({role}) has no wire")
            if role is None and dev not in ("respeaker",) and wired:
                fails.append(f"{mod['name']} {label} must stay unwired")
    for ref in ("J1", "J3", "J4", "J5", "J6", "J8", "J9", "J10", "J11"):
        for pad in model.parts[("main", ref)]["pads"]:
            pid = f"main:{ref}.{pad['num']}"
            if pad["net"] and not ends[pid]:
                fails.append(f"split: main board {ref} pad {pad['num']} ({pad['net']}) has no wire")
            if not pad["net"] and ends[pid]:
                fails.append(f"main board {ref} pad {pad['num']} is a spare and must stay empty")
    for n, role in panel.PI_PIN_ROLE.items():
        if n == 4:
            continue  # the display lead takes pin 2 or 4; one of the two is wired
        if not ends[f"pi:{n}"]:
            fails.append(f"split: Pi pin {n} ({role}) has no wire")
    passes.append("every module pin and socket pad that carries a net is wired; spares and the radar's OUT stay free")

    # 5. Pi housings: each wire sits in its own housing's pins.
    for l in model.leads:
        h = l.get("housing")
        if not h:
            continue
        allowed = set(panel.PI_HOUSINGS[h]["pins"])
        for a, b in l["wires"]:
            n = int(b.split(":")[1])
            if n not in allowed:
                fails.append(f"lead {l['n']}: Pi pin {n} is outside housing {h}")
    passes.append("Pi signal wires: each in its own housing's pins")

    # 6. Main board: nothing under a screw head; no two part bodies on top of each other.
    parts = [p for k, p in model.parts.items() if k[0] == "main"]
    heads = []
    for p in parts:
        if p["ref"].startswith("H"):
            circles = [g for g in p["graphics"].get("F.Fab", []) if g["k"] == "circle"]
            if not circles:
                fails.append(f"{p['ref']}: no screw-head circle on the fabrication layer")
                continue
            heads.append((p["ref"], Point(circles[0]["c"]).buffer(circles[0]["r"]), circles[0]["r"] * 2))
    bodies = {}
    for p in parts:
        if p["ref"].startswith("H"):
            continue
        layer = "F.CrtYd" if p["side"] == "F" else "B.CrtYd"
        shp = _shape(p["graphics"].get(layer, []))
        if shp is not None and not shp.is_empty:
            bodies[p["ref"]] = shp
    for ref, head, d in heads:
        for other, shp in bodies.items():
            a = head.intersection(shp).area
            if a > 0.01:
                fails.append(f"{other} lies under the M3 head at {ref} ({a:.2f} mm²)")
    refs = sorted(bodies)
    overlaps = 0
    for i, a in enumerate(refs):
        for b in refs[i + 1:]:
            ar = bodies[a].intersection(bodies[b]).area
            if ar > 0.01:
                overlaps += 1
                fails.append(f"main board: courtyards of {a} and {b} overlap by {ar:.2f} mm²")
    passes.append(f"main board: {len(heads)} M3 heads (Ø{heads[0][2]:.1f}) clear of all {len(bodies)} courtyards; no two courtyards overlap")

    # 7. Plug order: the 20 V plug goes on first, onto the middle of the three alike 2-way sockets.
    xh2 = sorted([p for p in parts if "B2B-XH" in p["lib"] or "XH_B2B" in p["lib"]], key=lambda p: p["at"][0])
    if len(xh2) != 3 or xh2[1]["ref"] != "J1" or panel.PLUG_ORDER[0] != "J1":
        fails.append(f"the 2-way sockets left to right are {[p['ref'] for p in xh2]}; J1 must be the middle one and first in the order")
    passes.append("the three 2-way sockets left to right (seen from the door) are " + ", ".join(p["ref"] for p in xh2) + "; J1 in the middle, plugged first")
    return fails, passes
