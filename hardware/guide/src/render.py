"""Generate the electronics page from the model. Run: python3 build.py"""
from __future__ import annotations

import json
import re
from collections import defaultdict

import panel
from model import net_class
from svgboard import View, esc, part_svg, prim_svg

S_MAIN, S_TOUCH, S_MIC = 12.0, 8.0, 28.0
MARGIN = 150  # px around the main board for lead stubs and tags


def nt(net):
    """A net as a coloured tag."""
    if not net:
        return '<span class="nt nc">not connected</span>'
    c = net_class(net)
    name = panel.NET_NAMES.get(net, net)
    return f'<span class="nt{" f-" + c if c else ""}">{esc(name)}</span>' + (f' <span class="via">{esc(net)}</span>' if name != net else "")


def hc(x):
    return f'<code class="hc">{esc(x)}</code>'


# ----------------------------------------------------------------------------------------------------- CSS
def css():
    light = "".join(f"--n-{c}:{l};" for c, _n, l, _d, _ in panel.NET_CLASSES)
    dark = "".join(f"--n-{c}:{d};" for c, _n, _l, d, _ in panel.NET_CLASSES)
    netcls = "".join(f".f-{c}{{color:var(--n-{c})}}.c-{c}{{fill:var(--n-{c})}}.pad.pn.c-{c}{{fill:var(--n-{c})}}.n-{c}{{stroke:var(--n-{c})}}.sw.f-{c}{{background:var(--n-{c})}}" for c, *_ in panel.NET_CLASSES)
    base_l = ("--bg:#f1f4f2;--panel:#ffffff;--ink:#1b2321;--muted:#596763;--rule:#cfd8d4;--accent:#c4581a;--warnbg:#fbece2;"
              "--pcb:#fbfaf6;--pcbline:#a9b3ae;--pad:#ead7a2;--padring:#b08f43;--drill:#5a4f3f;--silk:#3a4140;"
              "--body:#f4f1ea;--modbg:#eef2f6;--term:#a9cfe9;")
    base_d = ("--bg:#101614;--panel:#18201d;--ink:#e2e9e5;--muted:#93a29c;--rule:#2e3a36;--accent:#f08a3c;--warnbg:#2a1c13;"
              "--pcb:#1c2225;--pcbline:#46524d;--pad:#5a4d2c;--padring:#a08548;--drill:#0b0d0d;--silk:#b9c3bf;"
              "--body:#2a3134;--modbg:#222a30;--term:#2b5574;")
    return f"""
:root{{{base_l}{light}
--f-display:"IBM Plex Sans Condensed","Arial Narrow",system-ui,sans-serif;--f-body:"IBM Plex Sans",system-ui,sans-serif;--f-mono:"IBM Plex Mono",ui-monospace,Menlo,monospace}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{{base_d}{dark}color-scheme:dark}}}}
:root[data-theme="dark"]{{{base_d}{dark}color-scheme:dark}}
*{{box-sizing:border-box}}
body{{background:var(--bg);color:var(--ink);font:15px/1.55 var(--f-body);margin:0}}
.wrap{{max-width:1240px;margin:0 auto;padding-block:28px 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:grid;gap:34px}}
header{{display:grid;gap:14px}}
.eyebrow{{font:600 12px/1 var(--f-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--accent)}}
h1{{font:700 clamp(30px,5vw,46px)/1.05 var(--f-display);margin:0;text-wrap:balance;letter-spacing:-.01em}}
h2{{font:700 22px/1.2 var(--f-display);margin:0 0 4px;text-wrap:balance}}
h3{{font:700 17px/1.25 var(--f-display);margin:18px 0 4px;text-wrap:balance}}
.dek{{max-width:68ch;color:var(--muted);margin:0}}
.facts{{display:flex;flex-wrap:wrap;gap:8px 22px;margin:4px 0 0;padding:0;list-style:none;font:13px/1.4 var(--f-mono)}}
.facts b{{color:var(--ink);font-weight:600}} .facts li{{color:var(--muted)}}
.warn{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px}}
.warn div{{background:var(--warnbg);border-left:3px solid var(--accent);padding:12px 14px;border-radius:2px 6px 6px 2px;min-width:0}}
.warn b{{display:block;font:700 15px/1.3 var(--f-display);margin-bottom:3px}}
.warn p{{margin:0;font-size:14px}}
section{{display:grid;gap:12px;min-width:0}}
.sect-note{{color:var(--muted);margin:0;max-width:78ch;font-size:14px}}
.diagram{{background:var(--panel);border:1px solid var(--rule);border-radius:10px;overflow-x:auto;padding:10px}}
.legend{{display:flex;flex-wrap:wrap;gap:6px 18px;list-style:none;margin:0;padding:0;font:12.5px/1.4 var(--f-mono);color:var(--muted)}}
.legend li{{display:flex;align-items:center;gap:7px}}
.sw{{width:22px;height:4px;border-radius:2px;display:inline-block;background:currentColor}}
.tw{{overflow-x:auto;border:1px solid var(--rule);border-radius:8px;background:var(--panel)}}
table{{border-collapse:collapse;width:100%;font-size:14px;min-width:560px}}
th{{text-align:left;font:600 11.5px/1.3 var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);padding:10px 12px;border-bottom:1px solid var(--rule)}}
td{{padding:9px 12px;border-bottom:1px solid var(--rule);vertical-align:top;font-variant-numeric:tabular-nums}}
tr:last-child td{{border-bottom:0}}
td:first-child{{white-space:nowrap}}
.nt{{font:600 13px/1 var(--f-mono);white-space:nowrap}} .nt.nc{{color:var(--muted)}}
.via{{color:var(--muted);font:11.5px var(--f-mono)}} .muted{{color:var(--muted)}}
.two{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr));gap:24px;align-items:start}}
.two > *{{min-width:0}}
ol.steps{{margin:0;padding-left:1.4em;display:grid;gap:8px;max-width:80ch}}
ol.steps li::marker{{font:600 13px var(--f-mono);color:var(--accent)}}
code{{font:13px var(--f-mono)}}
.hc{{font:600 12.5px var(--f-mono);background:color-mix(in srgb,var(--accent) 12%,transparent);color:var(--ink);padding:1px 4px;border-radius:3px;white-space:nowrap}}
.mono td:nth-child(3),.mono td:nth-child(4){{font-family:var(--f-mono);font-size:13px}}
/* svg */
svg.wd{{display:block;width:100%;height:auto;font-family:var(--f-body)}}
.pcb{{fill:var(--pcb);stroke:var(--pcbline);stroke-width:1.5}}
.pad{{fill:var(--pad);stroke:var(--padring);stroke-width:.8}} .pad.pn{{stroke:var(--ink);stroke-width:.6;fill-opacity:.85}} .pad.pnc{{fill:var(--panel);stroke:var(--muted)}}
.drill{{fill:var(--drill)}}
.body{{fill:var(--body);fill-opacity:.55;stroke:var(--ink);stroke-width:1.1}} line.body,path.body{{fill:none}}
.body.dnp{{fill:none;stroke:var(--muted);stroke-dasharray:3 3}}
.mhole-b{{fill:none;stroke:var(--ink);stroke-dasharray:4 3;stroke-width:1.2}}
.t-ref{{font-weight:700;fill:var(--ink);paint-order:stroke;stroke:var(--pcb);stroke-width:3px;font-family:var(--f-mono)}} .t-ref.dnp-t{{fill:var(--muted)}}
.t-board{{font:700 16px var(--f-display);letter-spacing:.1em;fill:var(--ink)}} .t-boardsub{{font:600 13px var(--f-body);fill:var(--muted)}}
.t-silk{{font:600 11px var(--f-mono);fill:var(--silk)}}
.t-edge{{font:700 11px var(--f-mono);letter-spacing:.14em;fill:var(--muted)}}
.fw{{fill:none;stroke-width:4.2;stroke-linecap:round;stroke-linejoin:round}} .fhalo{{fill:none;stroke:var(--panel);stroke-width:8;stroke-linecap:round}}
.wtag{{fill:var(--panel);stroke:var(--ink);stroke-width:1.3}} .t-wtag{{font:700 12.5px var(--f-mono);fill:var(--ink)}}
.t-wsub{{font:600 11px var(--f-mono);fill:var(--muted)}}
.first{{fill:none;stroke:var(--accent);stroke-width:3;stroke-dasharray:6 4}} .t-first{{font:700 12px var(--f-body);fill:var(--accent)}}
.scale{{stroke:var(--ink);stroke-width:1.5}} .t-scale{{font:600 11px var(--f-mono);fill:var(--muted)}}
.elec{{fill:var(--pad);fill-opacity:.35;stroke:var(--padring);stroke-dasharray:4 3}}
.pin-used{{stroke:var(--ink);stroke-width:1}} .pin-free{{fill:var(--panel);stroke:var(--muted);stroke-width:1}}
.t-pin{{font:12px var(--f-mono);fill:var(--ink)}} .t-pin.off{{fill:var(--muted)}} .t-pinb{{font:700 11px var(--f-mono);fill:var(--panel)}}
.housing{{fill:none;stroke:var(--accent);stroke-width:2;stroke-dasharray:5 3}} .t-house{{font:700 12px var(--f-mono);fill:var(--accent)}}
.part{{fill:var(--panel);stroke:var(--ink);stroke-width:1.4}} .t-part{{font:600 14px var(--f-body);fill:var(--ink)}} .t-sub{{font:12px var(--f-body);fill:var(--muted)}}
.modbox{{fill:var(--modbg);stroke:var(--ink);stroke-width:1.4}} .modbox.unk{{stroke-dasharray:6 4}}
/* focus viewer */
.bleed{{width:min(1500px,calc(100vw - 32px));margin-left:calc((100% - min(1500px,calc(100vw - 32px))) / 2)}}
.viewer{{display:grid;gap:12px}}
.vbar{{display:flex;flex-wrap:wrap;gap:10px 22px;align-items:center;justify-content:space-between}}
.vgroups{{display:flex;flex-wrap:wrap;gap:8px 20px}}
.vg{{display:flex;flex-wrap:wrap;gap:6px;align-items:center}}
.vgl{{font:600 11px var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-right:2px}}
.chip,.vnav button{{font:600 13px var(--f-mono);padding:6px 11px;border-radius:999px;border:1px solid var(--rule);background:var(--panel);color:var(--ink);cursor:pointer;min-height:34px}}
.chip:hover,.vnav button:hover{{border-color:var(--ink)}}
.chip[aria-pressed="true"]{{background:var(--ink);color:var(--panel);border-color:var(--ink)}}
.chip:focus-visible,.vnav button:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
.vnav{{display:flex;gap:6px;align-items:center}}
.vpos{{font:600 12px var(--f-mono);color:var(--muted);min-width:64px;text-align:center}}
.vmain{{display:grid;grid-template-columns:minmax(0,1fr) 380px;gap:14px;align-items:start}}
@media (max-width:1150px){{.vmain{{grid-template-columns:1fr}}}}
.vdiag svg{{min-width:0}} .diagram svg.wide{{min-width:900px}}
@media (max-width:760px){{.vdiag svg.bd{{min-width:720px}}}}
.vpanel{{background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:14px 16px;position:sticky;top:12px;max-height:calc(100vh - 24px);overflow:auto;min-width:0}}
.fh{{font:700 18px/1.25 var(--f-display);margin-bottom:2px}} .fref{{font-family:var(--f-mono);color:var(--accent)}}
.fsub{{font:12.5px var(--f-mono);color:var(--muted);margin-bottom:8px}}
.ffit{{font-size:14px;margin:0 0 10px}} .fnote{{font-size:13px;color:var(--muted);margin:8px 0 0}}
.ft{{min-width:0;font-size:13px}} .ft td,.ft th{{padding:6px 6px}} .ft td:first-child{{white-space:normal}}
svg.bd [data-k]{{cursor:pointer}}
svg.bd.focus [data-k]{{opacity:.12;transition:opacity .18s}}
svg.bd.focus [data-k].on{{opacity:1}}
svg.bd.focus g.self > .body{{stroke:var(--accent);stroke-width:2.6}}
@media (prefers-reduced-motion: reduce){{svg.bd.focus [data-k]{{transition:none}}}}
{netcls}
.u-case{{fill:var(--rule);fill-opacity:.45;stroke:var(--muted);stroke-width:.8}} .u-board{{fill:var(--pcb);stroke:var(--pcbline);stroke-width:1.4}}
.u-mod{{fill:var(--modbg);fill-opacity:.9;stroke:var(--ink);stroke-width:1}} .u-lead{{fill:var(--ink);fill-opacity:.85;stroke:none}}
.t-uname{{font:600 11px var(--f-body);fill:var(--ink);paint-order:stroke;stroke:var(--panel);stroke-width:3.5px}}
svg.bd.focus .u-lead.on{{fill:var(--accent);fill-opacity:1}}
.checks li{{font-size:14px}} .checks li::marker{{color:var(--n-snd)}}
"""


# ----------------------------------------------------------------------------------------------------- helpers
def net_pads(board):
    m = defaultdict(list)
    for p in board["parts"]:
        for pad in p["pads"]:
            if pad["net"]:
                m[pad["net"]].append((p["ref"], pad["num"]))
    return m


def bom_row(model, board, ref):
    return model.bom.get((board, ref))


def lead_ends(model):
    """pin id -> (lead, other end) for every wire end."""
    out = {}
    for l in model.leads:
        for a, b in l["wires"]:
            out[a] = (l, b)
            out[b] = (l, a)
    return out


def pin_text(model, pid):
    kind, label, net, role = model.pin_info(pid)
    return label


# ----------------------------------------------------------------------------------------------------- focus panels
def part_panel(model, bkey, part, npads, ends):
    row = bom_row(model, bkey, part["ref"])
    pn = row.get("Maker's part number", "") if row else ""
    maker = f"{row['Maker']} {pn}" if row else ""
    dk = row["DigiKey number"] if row and row["DigiKey number"] else ""
    sub = [part["value"]]
    if row:
        sub.append(row["Package"])
    sub.append("door side" if (bkey == "main" and part["side"] == "F") else ("back face" if part["side"] == "B" else "front face"))
    h = [f'<div class="fh"><span class="fref">{esc(part["ref"])}</span> {esc(part["value"])}</div>',
         f'<div class="fsub">{esc(" · ".join(s for s in sub if s))}</div>']
    if maker.strip():
        h.append(f'<p class="ffit">{esc(maker)}' + (f' · DigiKey <code>{esc(dk)}</code>' if dk else "") + "</p>")
    if part["dnp"]:
        h.append('<p class="ffit"><b>Leave empty.</b> Its pads get paste like the others.</p>')
    rows = []
    for pad in sorted(part["pads"], key=lambda p: (len(p["num"]), p["num"])):
        net = pad["net"]
        pid = f"{bkey}:{part['ref']}.{pad['num']}"
        joins = ""
        if pid in ends:
            l, other = ends[pid]
            joins = f"lead {l['n']} → {esc(pin_text(model, other))}"
        elif net and net != "GND":
            others = [f"{r}.{n}" for r, n in npads[net] if r != part["ref"]]
            joins = ", ".join(others[:8]) + (" …" if len(others) > 8 else "")
        elif net == "GND":
            joins = "common ground"
        rows.append(f"<tr><td>{esc(pad['num'])}</td><td>{nt(net)}</td><td>{joins}</td></tr>")
    # Collapse repeated thermal-pad rows (same number) to one.
    seen, uniq = set(), []
    for r in rows:
        k = r.split("</td>")[0]
        if k not in seen:
            seen.add(k); uniq.append(r)
    h.append('<div class="tw"><table class="ft"><thead><tr><th>Pad</th><th>Net</th><th>Joins</th></tr></thead><tbody>' + "".join(uniq) + "</tbody></table></div>")
    return "".join(h)


def lead_panel(model, l):
    h = [f'<div class="fh"><span class="fref">Lead {l["n"]}</span> {esc(l["name"])}</div>',
         f'<div class="fsub">free length {l["free"]} mm · {esc(l["stock"])}</div>',
         f'<p class="ffit">{esc(l["plug"])}' + (f'. {esc(l["mark"])}' if l.get("mark") else "") + "</p>"]
    rows = []
    for a, b in l["wires"]:
        _, la, na, _ = model.pin_info(a)
        _, lb, nb, _ = model.pin_info(b)
        net = na or nb
        name = l.get("wire_names", {}).get(a, "")
        rows.append(f"<tr><td>{esc(name)}</td><td>{esc(la)}</td><td>{esc(lb)}</td><td>{nt(net)}</td></tr>")
    h.append('<div class="tw"><table class="ft"><thead><tr><th></th><th>From</th><th>To</th><th>Net</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>")
    if l.get("note"):
        h.append(f'<p class="fnote">{esc(l["note"])}.</p>')
    return "".join(h)


# ----------------------------------------------------------------------------------------------------- board viewers
GROUPS_MAIN = [
    ("Sockets", ["J1", "J9", "J8", "J6", "J5", "J10", "J11", "J2"]),
    ("Pi pads", ["J3", "J4", "J7"]),
    ("20 V", ["F1", "U1", "D1", "C1", "C2", "C3", "C4", "R1", "R2", "R3", "R4", "R5", "R6"]),
    ("5 V", ["L1", "C5", "C6", "PS1", "C7", "D2", "F2", "LK1", "F3", "R7", "R8", "R9", "R10", "R11"]),
    ("3.3 V", ["U2", "F4", "C11", "C12", "R12", "R13"]),
    ("Amplifier", ["U100", "F5", "L100", "L101", "L102", "L103"]),
]


def viewer(model, bkey, view_svg, chips, items, default_html, legend=True):
    chips_html = "".join(
        f'<div class="vg"><span class="vgl">{esc(g)}</span>' + "".join(
            f'<button class="chip" type="button" data-id="{esc(i)}" aria-pressed="false">{esc(lbl)}</button>' for i, lbl in ids) + "</div>"
        for g, ids in chips)
    data = {"order": [i["id"] for i in items], "items": items}
    leg = ""
    if legend:
        leg = '<ul class="legend">' + "".join(f'<li><span class="sw f-{c}"></span>{esc(n)}</li>' for c, n, *_ in panel.NET_CLASSES) + "</ul>"
    return f"""{leg}<div class="viewer bleed" data-viewer="{bkey}">
<div class="vbar"><div class="vgroups">{chips_html}</div>
<div class="vnav"><button type="button" data-nav="prev" aria-label="Previous">←</button><span class="vpos">all parts</span><button type="button" data-nav="next" aria-label="Next">→</button><button type="button" data-nav="all">Whole view</button></div></div>
<div class="vmain"><div class="diagram vdiag">{view_svg}</div><aside class="vpanel">{default_html}</aside></div>
<script type="application/json" class="focus-data">{json.dumps(data).replace("</", "<\\/")}</script></div>"""


def board_items(model, bkey, ends, extra_tokens=None):
    b = model.boards[bkey]
    npads = net_pads(b)
    items = []
    for p in b["parts"]:
        toks = [f"p:{bkey}:{p['ref']}"]
        for pad in p["pads"]:
            if pad["net"] and pad["net"] != "GND":
                toks.append(f"n:{bkey}:{pad['net']}")
            pid = f"{bkey}:{p['ref']}.{pad['num']}"
            if pid in ends:
                toks.append(f"l:{ends[pid][0]['n']}")
        items.append({"id": f"{bkey}:{p['ref']}", "label": p["ref"], "tokens": sorted(set(toks)), "own": [f"p:{bkey}:{p['ref']}"],
                      "html": part_panel(model, bkey, p, npads, ends)})
    return items


def main_board_svg(model, ends):
    b = model.boards["main"]
    W = (b["bbox"][2] - b["bbox"][0]) * S_MAIN
    H = (b["bbox"][3] - b["bbox"][1]) * S_MAIN
    ox, oy = MARGIN, 70
    v = View(b, S_MAIN, ox, oy)
    out = [f'<svg class="wd bd" viewBox="0 0 {W + 2 * MARGIN:.0f} {H + oy + MARGIN + 40:.0f}" role="img" aria-label="Main board to scale, seen from the door side, every part on its pads">']
    out.append(f'<text class="t-board" x="{ox}" y="30">MAIN BOARD REV 3.3</text><text class="t-boardsub" x="{ox}" y="50">seen from the door side, as it stands behind the display · 87.0 × 57.9 mm · 1 mm = {S_MAIN:g} px</text>')
    out.append(f'<path class="pcb" d="{v.path_outline()}"/>')
    for t in b["texts"]:
        if t["layer"] == "F.SilkS" and t["text"] != "+":
            X, Y = v.xy(t["xy"])
            out.append(f'<text class="t-silk" x="{X:.1f}" y="{Y:.1f}" text-anchor="middle">{esc(t["text"])}</text>')
    for p in b["parts"]:
        out.append(part_svg(v, p))
    # Lead stubs: from each wired pad of an edge socket, straight down or left past the board edge, to a tag.
    edge_y = oy + H
    by_lead = defaultdict(list)
    for pid, (l, other) in ends.items():
        if pid.startswith("main:"):
            by_lead[l["n"]].append(pid)
    bx0, by0, bx1, by1 = model.boards["main"]["bbox"]
    for n, pids in sorted(by_lead.items()):
        l = next(x for x in model.leads if x["n"] == n)
        pts = []
        for pid in pids:
            ref, num = pid[5:].split(".")
            pad = model.pad("main", ref, num)
            X, Y = v.xy(pad["xy"])
            pts.append((X, Y, pad))
        mx = min(p[2]["xy"][0] for p in pts) - bx0
        my = by1 - max(p[2]["xy"][1] for p in pts)
        side = "left" if mx < 6 else ("down" if my < 6 else "none")
        # Wires that leave pads in line with each other fan out side by side, so none hides another.
        lanes = defaultdict(list)
        for X, Y, pad in pts:
            lanes[round(Y if side == "left" else X, 0)].append((X, Y, pad))
        fan = {}
        for key, row in lanes.items():
            row.sort(key=lambda t: (t[0], t[1]) if side == "left" else (t[1], t[0]))
            for i, t in enumerate(row):
                fan[id(t[2])] = (i - (len(row) - 1) / 2) * 9
        for X, Y, pad in pts:
            c = net_class(pad["net"]) or "gnd"
            if side == "none":
                continue
            o = fan[id(pad)]
            if side == "left":
                d = f"M{X:.1f},{Y:.1f} L{X - 10:.1f},{Y + o:.1f} L{ox - 40:.1f},{Y + o:.1f}"
            else:
                d = f"M{X:.1f},{Y:.1f} L{X + o:.1f},{Y + 10:.1f} L{X + o:.1f},{edge_y + 50:.1f}"
            out.append(f'<g data-k="l:{n}"><path class="fhalo" d="{d}"/><path class="fw n-{c}" d="{d}"/></g>')
        xs = [X for X, _, _ in pts]; ys = [Y for _, Y, _ in pts]
        if side == "left":
            tx, ty = ox - 40 - 26, sum(ys) / len(ys)
        elif side == "down":
            tx, ty = sum(xs) / len(xs), edge_y + 50 + 16
        else:  # an interior header: the tag sits just above it, the plug goes straight out toward the door
            tx, ty = sum(xs) / len(xs), min(ys) - 30
        out.append(f'<g data-k="l:{n}"><rect class="wtag" x="{tx - 22:.1f}" y="{ty - 12:.1f}" width="44" height="24" rx="12"/>'
                   f'<text class="t-wtag" x="{tx:.1f}" y="{ty + 4.5:.1f}" text-anchor="middle">L{n}</text></g>')
    # The first plug: 20 V on the middle socket.
    j1 = model.parts[("main", "J1")]
    xs = [v.xy(p["xy"])[0] for p in j1["pads"]]
    ys = [v.xy(p["xy"])[1] for p in j1["pads"]]
    out.append(f'<rect class="first" x="{min(xs) - 34:.1f}" y="{min(ys) - 30:.1f}" width="{max(xs) - min(xs) + 68:.1f}" height="{edge_y + 84 - (min(ys) - 30):.1f}" rx="8"/>'
               f'<text class="t-first" x="{(min(xs) + max(xs)) / 2:.1f}" y="{edge_y + 100:.1f}" text-anchor="middle">20 V · plugged first · the middle socket</text>')
    # Edge names and a 10 mm scale bar.
    out.append(f'<text class="t-edge" x="{ox + W / 2:.1f}" y="{edge_y + 128:.1f}" text-anchor="middle">BOTTOM EDGE · SOCKETS · TOWARD THE BASE</text>')
    out.append(f'<text class="t-edge" x="{ox - 10:.1f}" y="{oy - 10:.1f}" text-anchor="end">← RIGHT SPEAKER</text><text class="t-edge" x="{ox + W + 10:.1f}" y="{oy - 10:.1f}">LEFT SPEAKER →</text>')
    sx, sy = ox + W - 10 * S_MAIN, oy - 22
    out.append(f'<line class="scale" x1="{sx:.1f}" y1="{sy}" x2="{sx + 10 * S_MAIN:.1f}" y2="{sy}"/><text class="t-scale" x="{sx - 6:.1f}" y="{sy + 4}" text-anchor="end">10 mm</text>')
    out.append("</svg>")
    return "".join(out)


def small_board_svg(model, bkey, scale, title, sub, mirror):
    b = model.boards[bkey]
    W = (b["bbox"][2] - b["bbox"][0]) * scale
    H = (b["bbox"][3] - b["bbox"][1]) * scale
    ox, oy = 40, 70
    v = View(b, scale, ox, oy, mirror=mirror)
    out = [f'<svg class="wd bd" viewBox="0 0 {W + 2 * ox:.0f} {H + oy + 50:.0f}" role="img" aria-label="{esc(title)}">']
    out.append(f'<text class="t-board" x="{ox}" y="30">{esc(title)}</text><text class="t-boardsub" x="{ox}" y="50">{esc(sub)}</text>')
    out.append(f'<path class="pcb" d="{v.path_outline()}"/>')
    for p in b["parts"]:
        if p["ref"].startswith("E"):  # touch electrodes are on the far face: drawn ghosted
            for pad in p["pads"]:
                cx, cy = v.xy(pad["xy"])
                w = pad["size"][0] * scale
                out.append(f'<rect class="elec" data-k="p:{bkey}:{p["ref"]}" x="{cx - w / 2:.1f}" y="{cy - w / 2:.1f}" width="{w:.1f}" height="{w:.1f}" rx="{2 * scale:.1f}"/>'
                           f'<text class="t-silk" x="{cx:.1f}" y="{cy + w / 2 - 6:.1f}" text-anchor="middle">{esc(p["ref"])} (front)</text>')
            continue
        out.append(part_svg(v, p))
    sx, sy = ox + W - 10 * scale, oy + H + 26
    out.append(f'<line class="scale" x1="{sx:.1f}" y1="{sy}" x2="{sx + 10 * scale:.1f}" y2="{sy}"/><text class="t-scale" x="{sx - 6:.1f}" y="{sy + 4}" text-anchor="end">10 mm</text>')
    out.append("</svg>")
    return "".join(out)


# ----------------------------------------------------------------------------------------------------- Pi header
def pi_header_svg(model):
    wired = {}
    for l in model.leads:
        for a, b in l["wires"]:
            for x, y in ((a, b), (b, a)):
                if x.startswith("pi:"):
                    n = int(x[3:])
                    net = model.pin_info(y)[2] or model.pin_info(y)[3]
                    wired[n] = (l, l.get("wire_names", {}).get(y, f"L{l['n']}"), net)
    P, X0 = 50, 110
    yE, yO = 120, 175
    out = ['<svg class="wd wide" viewBox="0 0 1150 300" role="img" aria-label="Raspberry Pi 5 header as fitted">',
           '<text class="t-part" x="70" y="34">Raspberry Pi 5 header, from above</text><text class="t-sub" x="70" y="54">edge row (even pins) at the top · pin 1 is the square pad at the left of the inner row, next to the mounting hole</text>']
    for n in range(1, 41):
        col = (n - 1) // 2
        x = X0 + col * P
        y = yE if n % 2 == 0 else yO
        if n in wired:
            l, name, net = wired[n]
            c = net_class(net) or "gnd"
            shape = f'<rect class="pin-used c-{c}" x="{x - 13}" y="{y - 13}" width="26" height="26" rx="{2 if n == 1 else 13}"/>'
            lab = f'<text class="t-pinb" x="{x}" y="{y + 4}" text-anchor="middle">{n}</text>'
            ty = y - 22 if n % 2 == 0 else y + 34
            tag = f'<text class="t-pin" x="{x}" y="{ty}" text-anchor="middle">{esc(name)}</text>'
            fn = panel.PI_HEADER[n].split()[-1]
            fy = y - 38 if n % 2 == 0 else y + 50
            tag += f'<text class="t-pin off" x="{x}" y="{fy}" text-anchor="middle" style="font-size:10px">{esc(fn)}</text>'
            out.append(f'<g data-k="l:{l["n"]}">{shape}{lab}{tag}</g>')
        else:
            out.append(f'<rect class="pin-free" x="{x - 11}" y="{y - 11}" width="22" height="22" rx="{2 if n == 1 else 11}"/><text class="t-pin off" x="{x}" y="{y + 4}" text-anchor="middle" style="font-size:10px">{n}</text>')
    for h, d in panel.PI_HOUSINGS.items():
        pins = d["pins"]
        cols = sorted({(p - 1) // 2 for p in pins})
        rows = {p % 2 for p in pins}
        x0 = X0 + cols[0] * P - 21
        x1 = X0 + cols[-1] * P + 21
        y0 = (yE if 0 in rows else yO) - 21
        y1 = (yO if 1 in rows else yE) + 21
        out.append(f'<rect class="housing" x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="5"/>')
        if h == "display":
            out.append(f'<text class="t-house" x="{x0 - 8}" y="{y0 + 26}" text-anchor="end">display</text><text class="t-house" x="{x0 - 8}" y="{y0 + 40}" text-anchor="end">lead</text>')
        else:
            out.append(f'<text class="t-house" x="{(x0 + x1) / 2}" y="{y1 + 62}" text-anchor="middle">housing {h}</text>')
    out.append("</svg>")
    return "".join(out)


# ----------------------------------------------------------------------------------------------------- modules
def modules_svg(model):
    ends = lead_ends(model)
    out = ['<svg class="wd wide" viewBox="0 0 1180 740" role="img" aria-label="Bought modules and their wired pins">']

    def pin_row(x, y, pins, dev, vertical=False, gap=34):
        s = []
        for i, (pin, (label, role)) in enumerate(pins):
            pid = f"{dev}:{pin}"
            px, py = (x, y + i * gap) if vertical else (x + i * gap, y)
            if pid in ends:
                l, other = ends[pid]
                net = model.pin_info(other)[2] or model.pin_info(pid)[2] or role
                c = net_class(net) or "gnd"
                s.append(f'<g data-k="l:{l["n"]}"><circle class="pin-used c-{c}" cx="{px}" cy="{py}" r="9"/></g>')
                tag = f"L{l['n']}"
            else:
                s.append(f'<circle class="pin-free" cx="{px}" cy="{py}" r="8"/>')
                tag = "—"
            if vertical:
                s.append(f'<text class="t-pin" x="{px + 16}" y="{py + 4}">{esc(label)}</text><text class="t-pin off" x="{px + 120}" y="{py + 4}">{tag}</text>')
            else:
                s.append(f'<text class="t-pin" x="{px}" y="{py + 28}" text-anchor="middle" style="font-size:11px">{esc(label.split()[0])}</text><text class="t-pin off" x="{px}" y="{py + 44}" text-anchor="middle" style="font-size:11px">{tag}</text>')
        return "".join(s)

    # Radar, to scale ×6 (16 × 22 mm).
    k = 6
    out.append(f'<rect class="modbox" x="40" y="70" width="{16 * k}" height="{22 * k}" rx="4"/><text class="t-part" x="40" y="40">Radar HLK-LD2410C</text><text class="t-sub" x="40" y="58">16 × 22 mm, ×6 · pins by the maker\'s numbering</text>')
    rp = list(panel.MODULES["radar"]["pins"].items())
    out.append(pin_row(170, 80, rp, "radar", vertical=True, gap=30))
    out.append('<text class="t-sub" x="40" y="230">5 holes, 2.54 pitch, along one edge;</text><text class="t-sub" x="40" y="246">read the labels printed beside them</text>')

    # Inlet, speakers, sensors, display: labels only (no outline in the records).
    def unk(x, y, w, h, title, sub, dev, pins):
        return (f'<rect class="modbox unk" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/><text class="t-part" x="{x}" y="{y - 26}">{esc(title)}</text>'
                f'<text class="t-sub" x="{x}" y="{y - 10}">{esc(sub)}</text>' + pin_row(x + 22, y + 26, list(pins.items()), dev, vertical=True, gap=30))
    out.append(unk(390, 70, 200, 70, "Inlet board, Adafruit 5807", "output pads + and −", "inlet", panel.MODULES["inlet"]["pins"]))
    out.append(unk(660, 70, 200, 130, "BME680 board, CJMCU-680", "wire by the printed labels", "bme680", panel.MODULES["bme680"]["pins"]))
    out.append(unk(930, 70, 200, 130, "VEML6030 board", "wire by the printed labels", "veml6030", panel.MODULES["veml6030"]["pins"]))
    out.append(unk(390, 300, 200, 70, "Left speaker, DMA45-4", "connector up, toward the box roof", "spkL", panel.MODULES["spkL"]["pins"]))
    out.append(unk(660, 300, 200, 70, "Right speaker, DMA45-4", "connector up, toward the box roof", "spkR", panel.MODULES["spkR"]["pins"]))
    out.append(unk(930, 300, 200, 70, "Display, 4-pin power header", "lead 11 to Pi pins 2 (or 4) and 6", "display", panel.MODULES["display"]["pins"]))

    # ReSpeaker Lite to scale ×4.6 from Seeed's STEP; microphone footprints on the bottom face, seen through.
    k = 4.6
    x0, y0 = 40, 500
    rs = panel.MODULES["respeaker"]
    out.append(f'<text class="t-part" x="{x0}" y="{y0 - 26}">ReSpeaker Lite, from above</text><text class="t-sub" x="{x0}" y="{y0 - 10}">82.0 × 34.0 mm, ×4.6 · U4 and U5 are the microphone footprints on the bottom face: the microphones come off, their pads take leads 13 and 14</text>')
    out.append(f'<rect class="modbox" x="{x0}" y="{y0 + 20}" width="{82.02 * k:.1f}" height="{34.01 * k:.1f}" rx="6"/>')
    for name, (a, b, c, d) in rs["mics"].items():
        out.append(f'<rect class="body" style="stroke-dasharray:4 3" x="{x0 + a * k:.1f}" y="{y0 + 20 + b * k:.1f}" width="{(c - a) * k:.1f}" height="{(d - b) * k:.1f}"/>'
                   f'<text class="t-pin" x="{x0 + (a + c) / 2 * k:.1f}" y="{y0 + 20 + b * k - 8:.1f}" text-anchor="middle">{name}</text>')
    out.append(f'<rect class="body" x="{x0 + 75.10 * k:.1f}" y="{y0 + 20 + 1.77 * k:.1f}" width="{7.78 * k:.1f}" height="{8.95 * k:.1f}"/><text class="t-pin" x="{x0 + 70 * k:.1f}" y="{y0 + 20 + 7 * k:.1f}" text-anchor="end">USB-C → lead 16</text>')
    out.append(f'<text class="t-sub" x="{x0 + 82.02 * k + 30:.1f}" y="{y0 + 60:.1f}">Lead 13, left strip: to the footprint whose pad 5 is at GND.</text><text class="t-sub" x="{x0 + 82.02 * k + 30:.1f}" y="{y0 + 80:.1f}">Lead 14, right strip: to the one whose pad 5 is at VDD.</text><text class="t-sub" x="{x0 + 82.02 * k + 30:.1f}" y="{y0 + 110:.1f}">Pads by function: 1 VDD, 2 CLK, 3 DATA, 4 and 6 GND</text><text class="t-sub" x="{x0 + 82.02 * k + 30:.1f}" y="{y0 + 128:.1f}">(bridge them), 5 L/R. Where pad 1 sits: find it with a meter</text><text class="t-sub" x="{x0 + 82.02 * k + 30:.1f}" y="{y0 + 146:.1f}">(see "Not in the records").</text>')
    out.append("</svg>")
    return "".join(out)


JS = r"""
(() => {
document.querySelectorAll('.viewer').forEach(V => {
  const F = JSON.parse(V.querySelector('.focus-data').textContent);
  const byId = Object.fromEntries(F.items.map(i => [i.id, i]));
  const order = F.order;
  const svg = V.querySelector('svg.bd');
  const panel = V.querySelector('.vpanel');
  const pos = V.querySelector('.vpos');
  const def = panel.innerHTML;
  const chips = Array.from(V.querySelectorAll('.chip[data-id]'));
  const nodes = Array.from(svg.querySelectorAll('[data-k]')).map(e => ({ e, k: e.getAttribute('data-k').split(' ') }));
  const full = svg.getAttribute('viewBox').split(/\s+/).map(Number);
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let cur = null, raf = null;
  const setVB = v => svg.setAttribute('viewBox', v.map(n => n.toFixed(1)).join(' '));
  function animateTo(t) {
    if (raf) cancelAnimationFrame(raf);
    const s = svg.getAttribute('viewBox').split(/\s+/).map(Number);
    if (reduce) { setVB(t); return; }
    const t0 = performance.now(), D = 340;
    const step = now => { let p = Math.min(1, (now - t0) / D); p = p < .5 ? 2*p*p : 1 - Math.pow(-2*p + 2, 2) / 2;
      setVB(s.map((v, i) => v + (t[i] - v) * p)); if (p < 1) raf = requestAnimationFrame(step); };
    raf = requestAnimationFrame(step);
  }
  function select(id) {
    const it = byId[id]; if (!it) return clear();
    cur = id;
    const on = new Set(it.tokens), own = new Set(it.own);
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    svg.classList.add('focus');
    for (const n of nodes) {
      const lit = n.k.some(t => on.has(t));
      n.e.classList.toggle('on', lit);
      const self = n.k.some(t => own.has(t));
      n.e.classList.toggle('self', self);
      if (self) { const b = n.e.getBBox(); if (b.width || b.height) { x0 = Math.min(x0, b.x); y0 = Math.min(y0, b.y); x1 = Math.max(x1, b.x + b.width); y1 = Math.max(y1, b.y + b.height); } }
    }
    if (isFinite(x0)) {
      const pad = 60, ar = full[2] / full[3];
      let w = Math.max(x1 - x0 + 2 * pad, full[2] * 0.35), h = Math.max(y1 - y0 + 2 * pad, full[3] * 0.35);
      if (w / h > ar) h = w / ar; else w = h * ar;
      w = Math.min(w, full[2]); h = Math.min(h, full[3]);
      const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
      animateTo([Math.max(full[0], Math.min(cx - w / 2, full[0] + full[2] - w)), Math.max(full[1], Math.min(cy - h / 2, full[1] + full[3] - h)), w, h]);
    }
    panel.innerHTML = it.html;
    chips.forEach(c => c.setAttribute('aria-pressed', c.dataset.id === id ? 'true' : 'false'));
    const i = order.indexOf(id);
    pos.textContent = i >= 0 ? `${i + 1} of ${order.length}` : it.label;
  }
  function clear() {
    cur = null; svg.classList.remove('focus'); nodes.forEach(n => n.e.classList.remove('on', 'self'));
    animateTo(full); panel.innerHTML = def; chips.forEach(c => c.setAttribute('aria-pressed', 'false')); pos.textContent = 'all parts';
  }
  function stepBy(d) { const i = order.indexOf(cur); select(order[i < 0 ? (d > 0 ? 0 : order.length - 1) : (i + d + order.length) % order.length]); }
  chips.forEach(c => c.addEventListener('click', () => (cur === c.dataset.id ? clear() : select(c.dataset.id))));
  V.querySelector('[data-nav=prev]').addEventListener('click', () => stepBy(-1));
  V.querySelector('[data-nav=next]').addEventListener('click', () => stepBy(1));
  V.querySelector('[data-nav=all]').addEventListener('click', clear);
  svg.addEventListener('click', ev => {
    const g = ev.target.closest('[data-k]'); if (!g) return;
    const k = g.getAttribute('data-k').split(' ');
    const p = k.find(x => x.startsWith('p:'));
    if (p && byId[p.slice(2)]) { select(p.slice(2)); return; }
    const l = k.find(x => x.startsWith('l:'));
    if (l && byId['L' + l.slice(2)]) { select('L' + l.slice(2)); }
  });
  V.addEventListener('keydown', ev => { if (ev.key === 'Escape') clear(); });
});
})();
"""


# ----------------------------------------------------------------------------------------------------- the unit
UNIT_BODIES = [
    # (body, what it is, kind, lead number or None)
    ("FLOOR_PLATE", "Base plate", "case", None), ("SLAB_frame", "Display slab", "case", None), ("LCD_glass", "Display", "case", None),
    ("HOUSING_F_cap", "Cap", "case", None), ("SPKBOX_L", "Left speaker box", "case", None), ("SPKBOX_R", "Right speaker box", "case", None),
    ("RESP_CARRIER", "Carrier", "case", None), ("RADAR_HOLDER", "Radar holder", "case", None), ("CRADLE_5807", "Inlet cradle", "case", None),
    ("BME_HOOD", "BME680 hood", "case", None),
    ("MAIN_pcb", "Main board", "board", None), ("MAIN_PS1", "Main board: power module", "board", None),
    ("TOUCH_PCB", "Touch board", "board", None), ("MIC_strip_L_env", "Left microphone strip", "board", None), ("MIC_strip_R_env", "Right microphone strip", "board", None),
    ("RESP_pcb", "ReSpeaker Lite (behind the main board)", "module", None), ("RESP_top_env", "ReSpeaker Lite", "module", None),
    ("PI5_F", "Raspberry Pi 5", "module", None), ("PI5_F_cooler", "Pi cooler", "module", None),
    ("GPIO_plugA_env", "Pi housings 1, 2 and display lead", "module", None), ("GPIO_plugB_env", "Pi housing 3", "module", None),
    ("PD_5807_env", "Inlet board", "module", None), ("LD2410C_env_F", "Radar", "module", None), ("BME680_env", "BME680 board", "module", None),
    ("VEML_env", "VEML6030 board", "module", None), ("SPK_L", "Left driver", "module", None), ("SPK_R", "Right driver", "module", None),
    ("MAIN_J2_plug_env", "Pi power plug", "module", None), ("RESP_usbc_plug_env", "ReSpeaker USB plug", "module", None),
    ("LEAD_PIGTAIL_20V", "Lead 1", "lead", 1), ("LEAD_SPK_L", "Lead 2", "lead", 2), ("LEAD_SPK_R", "Lead 3", "lead", 3),
    ("LEAD_RADAR", "Lead 4", "lead", 4), ("LEAD_TOUCH", "Lead 5", "lead", 5), ("LEAD_BME680", "Lead 6", "lead", 6),
    ("LEAD_VEML", "Lead 7", "lead", 7), ("LEAD_GPIO_A1", "Lead 8", "lead", 8), ("LEAD_GPIO_A2", "Lead 9", "lead", 9),
    ("LEAD_GPIO_B", "Lead 10", "lead", 10), ("LEAD_LCD_5V", "Lead 11", "lead", 11), ("LEAD_DSI", "Lead 12", "lead", 12),
    ("LEAD_MIC_L", "Lead 13", "lead", 13), ("LEAD_MIC_R", "Lead 14", "lead", 14), ("LEAD_PI_POWER", "Lead 15", "lead", 15),
    ("LEAD_USB_RESP", "Lead 16", "lead", 16),
]
UNIT_GROUPS = {
    "Main board": ["MAIN_pcb", "MAIN_PS1"], "ReSpeaker Lite": ["RESP_pcb", "RESP_top_env"], "Raspberry Pi 5": ["PI5_F", "PI5_F_cooler"],
}


def _poly_path(polys, X, Y):
    d = []
    for poly in polys:
        for ring in poly:
            d.append("M" + " L".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in ring) + " Z")
    return " ".join(d)


def unit_svg(model, pos):
    B = pos["bodies"]
    k = 3.6
    x0m, x1m = -104, 100
    zb0, zb1 = -146, 48
    yp0, yp1 = -114, 4
    W = (x1m - x0m) * k
    pad = 40
    back_h = (zb1 - zb0) * k
    plan_h = (yp1 - yp0) * k
    X = lambda x: pad + (x - x0m) * k
    Zb = lambda z: 80 + (zb1 - z) * k
    plan_top = 80 + back_h + 90
    Yp = lambda y: plan_top + (yp1 - y) * k
    H = plan_top + plan_h + 40
    out = [f'<svg class="wd bd" viewBox="0 0 {W + 2 * pad:.0f} {H:.0f}" role="img" aria-label="The unit to scale from the back with the door off, and from above">']
    out.append(f'<text class="t-board" x="{pad}" y="34">FROM THE BACK, DOOR OFF</text><text class="t-boardsub" x="{pad}" y="54">model version 91 · 1 mm = {k:g} px · the left speaker is on the right, as you stand behind the unit</text>')
    out.append(f'<text class="t-board" x="{pad}" y="{plan_top - 40:.0f}">FROM ABOVE</text><text class="t-boardsub" x="{pad}" y="{plan_top - 20:.0f}">the screen at the top, the door at the bottom</text>')
    kinds = {"case": "u-case", "board": "u-board", "module": "u-mod", "lead": "u-lead"}
    # Back view: draw far to near (a viewer behind the unit sees the most negative y first).
    def order_back(item):
        return -B[item[0]]["bbox"][4]
    def order_plan(item):
        return B[item[0]]["bbox"][5]
    for view, Yf, key, order in (("back", Zb, "back", order_back), ("plan", Yp, "plan", order_plan)):
        for name, label, kind, lead in sorted([u for u in UNIT_BODIES if u[0] in B], key=order):
            tok = f"l:{lead}" if lead else f"u:{name}"
            d = _poly_path(B[name][key], X, Yf)
            out.append(f'<path class="{kinds[kind]}{" lead-" + str(lead) if lead else ""}" data-k="{tok}" d="{d}"><title>{esc(label)}</title></path>')
        # lead numbers at each lead's middle
        for name, label, kind, lead in UNIT_BODIES:
            if lead and name in B:
                bb = B[name]["bbox"]
                cx = X((bb[0] + bb[3]) / 2)
                cy = Yf((bb[2] + bb[5]) / 2) if view == "back" else Yf((bb[1] + bb[4]) / 2)
                out.append(f'<g data-k="l:{lead}"><circle class="wtag" cx="{cx:.1f}" cy="{cy:.1f}" r="11"/><text class="t-wtag" x="{cx:.1f}" y="{cy + 4.5:.1f}" text-anchor="middle" style="font-size:11px">{lead}</text></g>')
    # Names of boards and modules (back view only, where they stand).
    for name, label, kind, lead in UNIT_BODIES:
        if kind in ("board", "module") and name in B and name not in ("RESP_top_env", "PI5_F_cooler", "MAIN_PS1", "MAIN_J2_plug_env", "RESP_usbc_plug_env", "GPIO_plugA_env", "GPIO_plugB_env"):
            bb = B[name]["bbox"]
            view_y = Zb(bb[5]) - 4 if name not in ("PI5_F", "PD_5807_env") else None
            if name in ("PI5_F", "PD_5807_env", "SPK_L", "SPK_R"):
                cx, cy = X((bb[0] + bb[3]) / 2), Yp((bb[1] + bb[4]) / 2) + 22
            elif name == "RESP_pcb":
                cx, cy = X((bb[0] + bb[3]) / 2), Zb((bb[2] + bb[5]) / 2)
            elif name == "MAIN_pcb":
                cx, cy = X(bb[0]) + 50, Zb(bb[5]) + 16
            else:
                cx, cy = X((bb[0] + bb[3]) / 2), view_y
            out.append(f'<text class="t-uname" data-k="u:{name}" x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle">{esc(label)}</text>')
    sx = X(x1m) - 20 * k
    out.append(f'<line class="scale" x1="{sx:.1f}" y1="70" x2="{sx + 20 * k:.1f}" y2="70"/><text class="t-scale" x="{sx - 6:.1f}" y="74" text-anchor="end">20 mm</text>')
    out.append("</svg>")
    return "".join(out)


def unit_viewer(model, pos):
    ends = lead_ends(model)
    items = []
    for l in model.leads:
        items.append({"id": f"U{l['n']}", "label": f"lead {l['n']}", "tokens": [f"l:{l['n']}"], "own": [f"l:{l['n']}"], "html": lead_panel(model, l)})
    for c in model.cables:
        items.append({"id": f"U{c['n']}", "label": f"lead {c['n']}", "tokens": [f"l:{c['n']}"], "own": [f"l:{c['n']}"],
                      "html": f'<div class="fh"><span class="fref">Lead {c["n"]}</span> {esc(c["name"])}</div><div class="fsub">bought as it is</div><p class="ffit">{esc(c["what"])}: {esc(c["ends"][0])} to {esc(c["ends"][1])}.</p>'})
    items.sort(key=lambda i: int(i["id"][1:]))
    chips = [("Leads", [(i["id"], str(int(i["id"][1:]))) for i in items])]
    default = ('<div class="fh">The unit</div><div class="fsub">model version 91 · read-only</div>'
               '<p class="ffit">Every board, module and lead at its place. Tap a lead, or a number, to light it in both views and see both of its ends.</p>'
               '<p class="fnote">Grey: printed parts. Light: circuit boards. Blue-grey: bought modules. Dark: leads.</p>')
    return viewer(model, "unit", unit_svg(model, pos), chips, items, default, legend=False)
