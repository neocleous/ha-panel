"""The single data model behind the page: three KiCad boards, the bought modules, the Pi header and every lead.

Built from:
- the three .kicad_pcb files (pads, nets, outlines, bodies);
- hardware/main-board/gpio-leads.md (the 13 Pi signal wires: parsed, not copied);
- hardware/notes/bom-2026-11-17.csv (maker's part numbers and DigiKey lines);
- data/panel.py (modules, leads, colours, open points).
"""
from __future__ import annotations

import csv
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
HW = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "data"))

import panel  # noqa: E402
from kicad_extract import extract  # noqa: E402

BOARDS = {
    "main": ("Main board", "rev 3.3", os.path.join(HW, "main-board", "main-board.kicad_pcb")),
    "touch": ("Touch board", "rev E", os.path.join(HW, "touch-board", "touch-board.kicad_pcb")),
    "mic": ("Microphone strip", "rev 3, two of them", os.path.join(HW, "mic-strip", "mic-strip.kicad_pcb")),
}


def short_net(n):
    if n is None:
        return None
    if n.startswith("unconnected-"):
        return None
    return n.rsplit("/", 1)[-1]


def net_class(n):
    for cid, _label, _l, _d, nets in panel.NET_CLASSES:
        if n in nets:
            return cid
    return None


def parse_gpio_leads(path):
    """Rows of the lead table in gpio-leads.md: lead, housing, Pi pin, function, net, pad, colour."""
    rows = []
    for line in open(path, encoding="utf8"):
        m = re.match(r"\|\s*([AB]\d)\s*\|\s*(\d)\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(J\d\.\d+)\s*\|\s*([^|]+?)\s*\|", line)
        if m:
            rows.append({"wire": m.group(1), "housing": m.group(2), "pi": int(m.group(3)), "function": m.group(4),
                         "net_text": m.group(5), "pad": m.group(6), "colour": m.group(7)})
    if len(rows) != 13:
        raise SystemExit(f"gpio-leads.md: expected 13 lead rows, read {len(rows)}")
    return rows


def parse_bom(path):
    by_ref = {}
    for row in csv.DictReader(open(path, encoding="utf8")):
        board = row["Board"].lower()
        key = "main" if board.startswith("main") else "touch" if board.startswith("touch") else "mic" if board.startswith("mic") else None
        if not key:
            continue
        for ref in [r.strip() for r in row["References"].split(",")]:
            by_ref[(key, ref)] = row
    return by_ref


class Model:
    def __init__(self):
        self.boards = {}
        for key, (name, rev, path) in BOARDS.items():
            b = extract(path)
            b.update({"key": key, "name": name, "rev": rev})
            for p in b["parts"]:
                for pad in p["pads"]:
                    pad["net"] = short_net(pad["net"])
            self.boards[key] = b
        self.parts = {(k, p["ref"]): p for k, b in self.boards.items() for p in b["parts"]}
        self.bom = parse_bom(os.path.join(HW, "notes", "bom-2026-11-17.csv"))
        self.gpio = parse_gpio_leads(os.path.join(HW, "main-board", "gpio-leads.md"))
        self.leads = self._leads()
        self.cables = panel.CABLES

    # ------------------------------------------------------------------ pins
    def pad(self, board, ref, num):
        part = self.parts.get((board, ref))
        if not part:
            raise KeyError(f"{board}:{ref} is not on the board")
        hits = [p for p in part["pads"] if p["num"] == num]
        if not hits:
            raise KeyError(f"{board}:{ref}.{num} is not a pad of {ref}")
        return hits[0]

    def pin_info(self, pid):
        """(kind, label, net or None, role or None) for a pin id such as main:J1.1, radar:5, pi:8, micL:3."""
        dev, rest = pid.split(":", 1)
        if dev in self.boards:
            ref, num = rest.split(".", 1)
            pad = self.pad(dev, ref, num)
            return ("pad", f"{ref} pad {num}", pad["net"], None)
        if dev == "pi":
            n = int(rest)
            return ("pi", f"Pi pin {n} ({panel.PI_HEADER[n]})", None, panel.PI_PIN_ROLE.get(n))
        mod = panel.MODULES[dev]
        if rest not in mod["pins"]:
            raise KeyError(f"{pid}: {mod['name']} has no pin {rest}")
        label, role = mod["pins"][rest]
        net = None
        if "kicad" in mod:
            net = self.pad(mod["kicad"], mod["kicad_ref"], rest)["net"]
        return ("mod", f"{mod['name']} {label}", net, role)

    # ------------------------------------------------------------------ leads
    def _leads(self):
        leads = [dict(l) for l in panel.LEADS]
        bundles = {"1": (8, "Pi signal wires, bundle of 3"), "2": (9, "Pi signal wires, bundle of 6"), "3": (10, "Pi signal wires, bundle of 4")}
        for h, (n, name) in bundles.items():
            rows = [r for r in self.gpio if r["housing"] == h]
            leads.append({
                "n": n, "name": name, "free": 70, "stock": f"{len(rows)} wires of Adafruit 3141",
                "plug": f"housing {h}, {panel.PI_HOUSINGS[h]['shape']}, on Pi pins {rows[0]['pi']}–{rows[-1]['pi']}" if h != "1" else "housing 1, 1 × 3, on Pi pins 1-3-5",
                "mark": "", "housing": h,
                "wires": [(f"main:{r['pad']}", f"pi:{r['pi']}") for r in rows],
                "wire_names": {f"main:{r['pad']}": r["wire"] for r in rows},
                "colours": {f"main:{r['pad']}": r["colour"] for r in rows},
                "note": "wire pushed in from the back face, soldered on the door side",
            })
        return sorted(leads, key=lambda l: l["n"])

    # ------------------------------------------------------------------ connectivity
    def groups(self):
        """Connected groups across boards: KiCad nets are joined by lead wires and bridges."""
        parent = {}

        def find(x):
            parent.setdefault(x, x)
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            parent[find(a)] = find(b)

        def node(pid):
            kind, _label, net, _role = self.pin_info(pid)
            dev = pid.split(":", 1)[0]
            board = dev if dev in self.boards else panel.MODULES.get(dev, {}).get("kicad")
            if net and board:
                inst = dev if dev in self.boards else dev  # each strip is its own copy of the mic board
                union(pid, f"net:{inst}:{net}")
            return pid

        for l in self.leads:
            for a, b in l["wires"]:
                union(node(a), node(b))
            if l.get("bridge"):
                union(node(l["bridge"][0]), node(l["bridge"][1]))
        groups = defaultdict(set)
        for x in list(parent):
            groups[find(x)].add(x)
        return list(groups.values())
