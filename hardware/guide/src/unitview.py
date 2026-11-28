"""The unit section: a wiring diagram (not to scale) and two to-scale views from the model, one lead at a time.

To scale: boards and modules from the model's outlines (version 91), light, each named once; sockets as dots in
their job colours. A lead is drawn only when chosen: each conductor a thin line in its job colour (a marked black
wire as a black line with its mark at both ends), on a square path that follows the lead's route in the model,
without its coils or slack.
"""
from __future__ import annotations

import json

from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import substring, unary_union

import panel
import page as PG
from svgboard import esc

K = 3.6                       # px per mm
PAD = 34
VIEWS = {
    # name: (title, axis index for v, (u0, u1), (v0, v1))
    "back": ("From behind, door off", 2, (-101, 99), (-139, 45)),
    "plan": ("From above", 1, (-101, 99), (-113, 3)),
}
LEAD_BODY = {1: "LEAD_PIGTAIL_20V", 2: "LEAD_SPK_L", 3: "LEAD_SPK_R", 4: "LEAD_RADAR", 5: "LEAD_TOUCH", 6: "LEAD_BME680",
             7: "LEAD_VEML", 8: "LEAD_GPIO_A1", 9: "LEAD_GPIO_A2", 10: "LEAD_GPIO_B", 11: "LEAD_LCD_5V", 12: "LEAD_DSI",
             13: "LEAD_MIC_L", 14: "LEAD_MIC_R", 15: "LEAD_PI_POWER", 16: "LEAD_USB_RESP"}
# The two ends: a main-board socket ("main") or a model body.
LEAD_ENDS = {1: ("main", "PD_5807_env"), 2: ("main", "SPK_L"), 3: ("main", "SPK_R"), 4: ("main", "LD2410C_env_F"),
             5: ("main", "TOUCH_PCB"), 6: ("main", "BME680_env"), 7: ("main", "VEML_env"), 8: ("main", "GPIO_plugA_env"),
             9: ("main", "GPIO_plugA_env"), 10: ("main", "GPIO_plugB_env"), 11: ("GPIO_plugA_env", "LCD_glass"),
             12: ("PI5_F", "LCD_glass"), 13: ("RESP_pcb", "MIC_strip_L_env"), 14: ("RESP_pcb", "MIC_strip_R_env"),
             15: ("main:J2", "PI5_F"), 16: ("PI5_F", "RESP_usbc_plug_env")}
# Boards and modules drawn, in plain words; plugs stand for the body they sit on.
UNIT_PARTS = [("LCD_glass", "Display"), ("MAIN_pcb", "Main board"), ("RESP_pcb", "ReSpeaker Lite"), ("PI5_F", "Raspberry Pi 5"),
              ("TOUCH_PCB", "Touch board"), ("LD2410C_env_F", "Radar"), ("PD_5807_env", "Inlet board"),
              ("SPK_L", "Left speaker"), ("SPK_R", "Right speaker"), ("BME680_env", "BME680 board"),
              ("VEML_env", "Light sensor"), ("MIC_strip_L_env", "Left microphone strip"), ("MIC_strip_R_env", "Right microphone strip")]
STANDS_FOR = {"GPIO_plugA_env": "PI5_F", "GPIO_plugB_env": "PI5_F", "RESP_usbc_plug_env": "RESP_pcb", "main": "MAIN_pcb",
              "main:J2": "MAIN_pcb"}
# Free length and spare: harness list, seventh issue (2026-11-27), section 1.
LEAD_LEN = {1: ("90 mm", "about 16 mm spare, in a bow"), 2: ("about 135 mm, 35 of it inside the box", "about 11 mm spare, in a bow"),
            3: ("about 127 mm, 35 of it inside the box", "spare in a bow; its length is not in the records"),
            4: ("118 mm", "about 15 mm spare: 10 behind the radar, 5 in the run"), 5: ("87 mm", "about 15 mm spare, in a bow"),
            6: ("93 mm", "about 15 mm spare, in a bow"), 7: ("116 mm", "about 15 mm spare, in a bow"),
            8: ("70 mm", "about 12 mm spare, in a bow"), 9: ("70 mm", "about 12 mm spare, in a bow"),
            10: ("70 mm", "about 12 mm spare, in a bow"), 11: ("180 mm", "about 14 mm spare"),
            12: ("200 mm, bought", "an arch over the Pi's connector, 3.8 mm high at most"),
            13: ("230 mm", "about 160 mm spare, in a bound coil of three turns behind the screen plate"),
            14: ("230 mm", "about 164 mm spare, in a bound coil of three turns behind the screen plate"),
            15: ("200 mm, bought", "about 135 mm spare, in one upright lap behind its plug"),
            16: ("238 to 250 mm, bought", "108 to 120 mm spare, in a flat roll behind the left speaker box")}
SPACING = 3.0                 # px between conductors
CABLE = {12: "ribbon", 15: "cable", 16: "cable"}
CABLE_ENDS = {12: ("the display", "the Pi's DSI socket"), 15: ("the Pi power socket <small>(J2)</small>", "the Pi's USB-C socket"),
              16: ("the Pi's lower blue USB-A port", "the ReSpeaker's USB-C socket")}


def _polys(entry):
    out = []
    for poly in entry:
        ring = poly[0]
        if len(ring) >= 3:
            p = Polygon(ring)
            if not p.is_valid:
                p = p.buffer(0)
            if not p.is_empty:
                out.append(p)
    return unary_union(out) if out else None


def _exteriors(geom):
    gs = getattr(geom, "geoms", [geom])
    return [g for g in gs if g.geom_type == "Polygon"]


class Frame:
    def __init__(self, view):
        self.title, self.vi, (self.u0, self.u1), (self.v0, self.v1) = VIEWS[view]
        self.view = view
        self.W = (self.u1 - self.u0) * K + 2 * PAD
        self.top = 46
        self.H = self.top + (self.v1 - self.v0) * K + PAD

    def xy(self, u, v):
        return PAD + (u - self.u0) * K, self.top + (self.v1 - v) * K

    def geom(self, g):
        from shapely.affinity import affine_transform
        # x' = K u + (PAD - K u0); y' = -K v + (top + K v1)
        return affine_transform(g, [K, 0, 0, -K, PAD - K * self.u0, self.top + K * self.v1])


def _main_pts(model, pids, frame):
    """Main-board pads in the model frame: x = KiCad x - 43.55, z = 1.5 - KiCad y; sockets stand about 36 mm deep."""
    pts = []
    for pid in pids:
        ref, num = pid.split(":")[1].split(".")
        x, y = model.pad("main", ref, num)["xy"]
        u = x - 43.55
        v = (1.5 - y) if frame.vi == 2 else -36.0
        pts.append((u, v))
    return pts


def _route(a, b, lead_geom):
    """Square path from a to b that keeps inside the lead's own outline as much as it can."""
    (ax, ay), (bx, by) = a, b
    zone = lead_geom.buffer(2.0) if lead_geom is not None else None
    cands = [[a, (bx, ay), b], [a, (ax, by), b]]
    if lead_geom is not None:
        x0, y0, x1, y1 = lead_geom.bounds
        for i in range(1, 12):
            t = x0 + (x1 - x0) * i / 12
            cands.append([a, (t, ay), (t, by), b])
            t = y0 + (y1 - y0) * i / 12
            cands.append([a, (ax, t), (bx, t), b])
    best, bs = None, None
    for c in cands:
        pts = [c[0]] + [p for i, p in enumerate(c[1:]) if (abs(p[0] - c[i][0]) + abs(p[1] - c[i][1])) > 1e-6]
        if len(pts) < 2:
            continue
        ls = LineString(pts)
        out = ls.length - (ls.intersection(zone).length if zone is not None else 0)
        s = out * 3 + 2.0 * (len(pts) - 2) + ls.length * 0.05
        if bs is None or s < bs:
            best, bs = pts, s
    return best


def _far_point(lead_geom, target, away_from):
    """Where the lead meets a body: of the lead's outline points nearest the body, the one farthest from the other end."""
    pts = []
    for p in _exteriors(lead_geom):
        pts += list(p.exterior.coords)
    ds = [target.distance(Point(p)) for p in pts]
    lo = min(ds)
    cand = [p for p, d in zip(pts, ds) if d <= lo + 2.0]
    p = max(cand, key=lambda q: Point(q).distance(Point(away_from)))
    if not target.contains(Point(p)):
        from shapely.ops import nearest_points
        q = nearest_points(target, Point(p))[0]
        p = (q.x, q.y)
    return p


def _lead_items(model):
    """(n, name, conductors) for every lead and cable; conductors = [(spec or None, main pid or None)]."""
    from model import wire_spec
    out = []
    for l in model.leads:
        cs = []
        for a, b in l["wires"]:
            s = wire_spec(model, l, a, b)
            cs.append((s, a if a.startswith("main:") else (b if b.startswith("main:") else None)))
        out.append((l["n"], cs))
    for c in model.cables:
        out.append((c["n"], [(None, None)]))
    return sorted(out)


def scale_svg(model, pos, view, label_report):
    B = pos["bodies"]
    F = Frame(view)
    key = view
    body_geom = {n: _polys(B[n][key]) for n, _ in UNIT_PARTS if n in B}
    for n in ("GPIO_plugA_env", "GPIO_plugB_env", "RESP_usbc_plug_env"):
        body_geom[n] = _polys(B[n][key])
    leads = _lead_items(model)
    ends_of = {}                       # body -> lead numbers ending there
    for n, _cs in leads:
        for e in LEAD_ENDS[n]:
            ends_of.setdefault(STANDS_FOR.get(e, e), set()).add(n)

    # ---------------------------------------------------------------- paths in the model frame
    paths, socket_dots = {}, []
    for n, cs in leads:
        lg = _polys(B[LEAD_BODY[n]][key])
        ea, eb = LEAD_ENDS[n]
        if ea == "main":
            pids = [p for _s, p in cs if p]
            pts = _main_pts(model, pids, F)
            a = (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
            for (s, pid), (u, v) in zip(cs, pts):
                socket_dots.append((u, v, s["job"], n))
            b = _far_point(lg, body_geom[eb], a)
        elif ea == "main:J2":
            pids = [f"main:J2.{p['num']}" for p in model.parts[("main", "J2")]["pads"]]
            pts = _main_pts(model, pids, F)
            a = (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
            socket_dots.append((a[0], a[1], None, n))
            b = _far_point(lg, body_geom[eb], a)
        else:
            c = body_geom[ea].centroid
            b = _far_point(lg, body_geom[eb], (c.x, c.y))
            a = _far_point(lg, body_geom[ea], b)
        paths[n] = _route(a, b, lg)

    # ---------------------------------------------------------------- screen geometry
    out = [f'<svg class="uscale" data-view="{view}" viewBox="0 0 {F.W:.0f} {F.H:.0f}" role="img" aria-label="{esc(F.title)}, to scale">']
    out.append(f'<text class="t-utitle" x="{PAD}" y="26">{esc(F.title.upper())}</text>')
    sub = "the left speaker is on your right" if view == "back" else "screen at the top, door at the bottom"
    out.append(f'<text class="t-usub" x="{PAD + 7.6 * len(F.title) + 14:.0f}" y="26">{sub}</text>')
    sx = F.W - PAD - 20 * K
    out.append(f'<line class="scale" x1="{sx:.1f}" y1="34" x2="{sx + 20 * K:.1f}" y2="34"/><text class="t-scale" x="{sx - 6:.1f}" y="38" text-anchor="end">20 mm</text>')
    obstacles_lines = [LineString([(PAD, 12), (F.W - PAD, 12)])]          # nothing above the title row
    title_box = box(PAD - 2, 10, F.W - PAD + 2, 42)
    # bodies, far to near
    # far to near: from behind, the most negative depth last; from above, the highest top last
    order = sorted([n for n, _ in UNIT_PARTS if n in B], key=lambda n: -B[n]["bbox"][4] if view == "back" else B[n]["bbox"][5])
    screen_body = {}
    for n in order:
        g = F.geom(body_geom[n])
        screen_body[n] = g
        toks = " ".join([f"u:{n}"] + [f"l:{x}" for x in sorted(ends_of.get(n, []))])
        d = " ".join("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in p.exterior.coords) + " Z" for p in _exteriors(g))
        cls = "ub ub-board" if n in ("MAIN_pcb", "TOUCH_PCB", "MIC_strip_L_env", "MIC_strip_R_env") else "ub"
        if n == "LCD_glass":
            cls += " ub-back"
        out.append(f'<path class="{cls}" data-k="{toks}" d="{d}"><title>{esc(dict(UNIT_PARTS)[n])}</title></path>')
        for p in _exteriors(g):
            obstacles_lines.append(p.exterior)
    # leads (hidden until chosen)
    lead_lines = {}
    for n, cs in leads:
        pts = [F.xy(u, v) for u, v in paths[n]]
        ls = LineString(pts) if len(pts) >= 2 else LineString([pts[0], (pts[0][0] + 0.1, pts[0][1])])
        nc = len(cs)
        width = (nc - 1) * SPACING
        lead_lines[n] = (ls, width)
        g = [f'<g class="ulead" data-lead="{n}">']
        d0 = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in ls.coords)
        if n in CABLE:
            w = 7 if CABLE[n] == "ribbon" else 4.5
            g.append(f'<path class="ucable" style="stroke-width:{w}" d="{d0}"/>')
            for x, y in (ls.coords[0], ls.coords[-1]):
                g.append(f'<circle class="uend" cx="{x:.1f}" cy="{y:.1f}" r="3.2"/>')
        else:
            g.append(f'<path class="uhalo" style="stroke-width:{width + 4.2:.1f}" d="{d0}"/>')
            for i, (s, _pid) in enumerate(cs):
                off = (i - (nc - 1) / 2) * SPACING
                c = ls if abs(off) < 1e-6 else ls.offset_curve(off, join_style="mitre", mitre_limit=4)
                if c.is_empty or c.geom_type != "LineString":
                    c = ls
                d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in c.coords)
                if s["insulation"] == "black" and s["mark"]:
                    g.append(f'<path class="uc s-black" d="{d}"/>')
                    m = min(9.0, c.length / 3)
                    for seg in (substring(c, 0, m), substring(c, c.length - m, c.length)):
                        if seg.length > 0:
                            g.append(f'<path class="uc um s-{s["job"]}" d="M' + " L".join(f"{x:.1f},{y:.1f}" for x, y in seg.coords) + '"/>')
                else:
                    g.append(f'<path class="uc s-{s["job"]}" d="{d}"/>')
            # far-end dots (the module's own pins), in job colours
            for i, (s, pid) in enumerate(cs):
                off = (i - (nc - 1) / 2) * SPACING
                c = ls if abs(off) < 1e-6 else ls.offset_curve(off, join_style="mitre", mitre_limit=4)
                if c.is_empty or c.geom_type != "LineString":
                    c = ls
                ends = [c.coords[-1]] if pid else [c.coords[0], c.coords[-1]]
                for x, y in ends:
                    g.append(f'<circle class="udot ufar f-{s["job"]}" cx="{x:.1f}" cy="{y:.1f}" r="1.9"/>')
        g.append("</g>")
        out += g
    # socket dots on the main board (always shown)
    for u, v, job, n in socket_dots:
        x, y = F.xy(u, v)
        cls = f"udot f-{job}" if job else "udot uplug"
        out.append(f'<circle class="{cls}" data-k="l:{n}" cx="{x:.1f}" cy="{y:.1f}" r="{2.6 if job else 4:.1f}"><title>{esc(panel.LEAD_SHORT[n])}</title></circle>')

    # ---------------------------------------------------------------- names: once each, clear of every line and dot
    blockers = [title_box]
    for n, (ls, w) in lead_lines.items():
        blockers.append(ls.buffer(w / 2 + 4.5, cap_style=2, join_style=2))
    for u, v, _j, _n in socket_dots:
        x, y = F.xy(u, v)
        blockers.append(Point(x, y).buffer(5))
    from shapely.prepared import prep
    line_block = prep(unary_union([l.buffer(1.0) for l in obstacles_lines]))
    block = prep(unary_union(blockers))
    placed = []
    names = []
    by_size = sorted([n for n, _ in UNIT_PARTS if n in screen_body], key=lambda n: screen_body[n].area)
    for n in by_size:
        lab = dict(UNIT_PARTS)[n]
        g = screen_body[n]
        smaller = [screen_body[o] for o in screen_body if o != n and screen_body[o].area <= g.area]
        tw, th = 6.9 * len(lab) + 4, 15
        x0, y0, x1, y1 = g.bounds
        c = g.representative_point()
        best = None
        y = y0 - 34
        while y <= y1 + 34:
            x = x0 - tw / 2 - 30
            while x <= x1 + tw / 2 + 30:
                r = box(x - tw / 2, y - th / 2, x + tw / 2, y + th / 2)
                x += 6
                if r.bounds[0] < 4 or r.bounds[2] > F.W - 4 or r.bounds[1] < 44 or r.bounds[3] > F.H - 4:
                    continue
                if any(r.intersects(q) for q in smaller):
                    continue
                inside = g.contains(r)
                dist = 0 if inside else r.distance(g)
                if not inside and dist > 14:
                    continue
                score = (0 if inside else 1000) + dist * 10 + r.centroid.distance(c) * (0.2 if inside else 1)
                if best is not None and score >= best[0]:
                    continue
                if line_block.intersects(r) or block.intersects(r) or any(r.intersects(q) for q in placed):
                    continue
                best = (score, r)
            y += 6
        if best:
            r = best[1]
            placed.append(r.buffer(3))
            px, py = r.centroid.x, r.centroid.y
            toks = " ".join([f"u:{n}"] + [f"l:{x}" for x in sorted(ends_of.get(n, []))])
            names.append(f'<text class="t-uname" data-k="{toks}" x="{px:.1f}" y="{py + 4.5:.1f}" text-anchor="middle">{esc(lab)}</text>')
        else:
            label_report.append(f"{view}: {lab} kept in the list only")
    out += names
    out.append("</svg>")
    return "".join(out), ends_of


def lead_panel_html(model, n):
    from model import wire_words
    name = panel.LEAD_NAMES[n]
    length, spare = LEAD_LEN[n]
    h = [f'<div class="fh">{esc(name[0].upper() + name[1:])}</div>', f'<div class="fsub">{esc(length)}</div>',
         f'<p class="ffit">{esc(spare[0].upper() + spare[1:])}.</p>']
    l = next((x for x in model.leads if x["n"] == n), None)
    if l:
        rows = []
        for a, b in l["wires"]:
            s = model.wire_spec(l, a, b)
            rows.append(f"<li>{PG.jt(s['job'], esc(wire_words(s)))}<span>{PG.end_name(model, a)} → {PG.end_name(model, b)}</span></li>")
        h.append('<ul class="uwires">' + "".join(rows) + "</ul>")
    else:
        c = next(x for x in model.cables if x["n"] == n)
        a, b = CABLE_ENDS[n]
        h.append(f'<p class="ffit">From {a} to {b}.</p><p class="fnote">{esc(c["what"])}.</p>')
    return "".join(h)


UNIT_CSS = """
.uview{display:grid;gap:10px}
.utabs{display:flex;flex-wrap:wrap;gap:6px}
.utabs button{font:600 14px var(--f-body);border:1px solid var(--rule);background:var(--panel);color:var(--ink);border-radius:999px;padding:8px 14px;min-height:40px;cursor:pointer}
.utabs button[aria-selected=true]{background:var(--ink);color:var(--panel);border-color:var(--ink)}
.umain{display:grid;grid-template-columns:minmax(0,1fr) 290px;gap:12px 14px;align-items:start}
.ulist{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:5px;min-width:0;align-items:center}
.ulist .vgl{margin:0 6px 0 0}
.ulist .brk{flex-basis:100%;height:2px}
.ulist button{font:13.5px var(--f-body);border:1px solid var(--rule);background:var(--panel);color:var(--ink);border-radius:999px;padding:4px 11px;min-height:32px;cursor:pointer;display:flex;gap:7px;align-items:center}
.ulist button:hover{border-color:var(--ink)} .ulist button[aria-pressed=true]{background:var(--ink);color:var(--panel);border-color:var(--ink)}
.ulist .ldot{flex:none;width:9px;height:9px;border-radius:50%;box-shadow:0 0 0 1px var(--muted)} .ulist .ldot:not([class*="j-"]){background:var(--muted)}
.ustage{background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:8px;overflow-x:auto;min-width:0}
.upane{display:none} .upane.on{display:block}
.upane svg{display:block;width:100%;height:auto;margin:0 auto} .upane svg.uscale{max-width:920px}
.uview svg.wire .t-wp{font-size:11.5px} .uview svg.wire .t-w{font-size:13px}
.umain .vpanel{position:sticky;top:12px}
.ub{fill:var(--modbg);fill-opacity:.55;stroke:var(--muted);stroke-width:1;transition:opacity .18s}
.ub-board{fill:var(--pcb);fill-opacity:.7;stroke:var(--pcbline)}
.ub-back{fill:none;stroke-dasharray:4 4}
.ulead{display:none} .ulead.on{display:inline}
.uc{fill:none;stroke-width:2;stroke-linecap:butt;stroke-linejoin:miter} .um{stroke-width:2.4}
.uc.s-black{stroke:#23282b}
.uhalo{fill:none;stroke:var(--muted);stroke-opacity:.3;stroke-linejoin:miter}
.ucable{fill:none;stroke:var(--muted);stroke-linejoin:miter;stroke-linecap:butt}
.uend{fill:var(--panel);stroke:var(--ink);stroke-width:1.2}
.udot{stroke:var(--ink);stroke-width:.6;cursor:pointer} .uplug{fill:var(--panel);stroke:var(--muted);stroke-width:1.4}
.ufar{stroke:none}
.t-uname{font:600 12px var(--f-body);fill:var(--ink);paint-order:stroke;stroke:var(--panel);stroke-width:3px;cursor:pointer}
.t-utitle{font:700 13px var(--f-display);letter-spacing:.06em;fill:var(--muted)} .t-usub{font:12px var(--f-body);fill:var(--muted)}
svg.uscale[data-show] .ub:not(.on),svg.uscale[data-show] .udot:not(.on),svg.uscale[data-show] .t-uname:not(.on){opacity:.22}
svg.uscale .ub.on{stroke:var(--ink);stroke-width:1.6}
.uwires{list-style:none;margin:10px 0 0;padding:0;display:grid;gap:9px}
.uwires li{display:grid;gap:2px;font-size:14px;border-top:1px solid var(--rule);padding-top:7px} .uwires li > span:last-child{color:var(--muted);font-size:13px}
.ukey{display:flex;flex-wrap:wrap;gap:6px 18px;font:13px var(--f-body);color:var(--muted);margin:0;padding:0;list-style:none}
.ukey li{display:flex;align-items:center;gap:7px}
.markkey{display:inline-block;width:22px;height:4px;background:linear-gradient(90deg,#d3302a 0 5px,#23282b 5px 17px,#d3302a 17px)}
@media (max-width:900px){.umain{grid-template-columns:minmax(0,1fr)} .umain .vpanel{position:static}}
@media (max-width:700px){.upane[data-pane=wire] svg{min-width:920px} .upane[data-pane=back] svg,.upane[data-pane=plan] svg{min-width:660px}}
@media (prefers-reduced-motion: reduce){.ub{transition:none}}
"""

UNIT_JS = """
(function(){
document.querySelectorAll('.uview').forEach(function(U){
  var data = JSON.parse(U.querySelector('.udata').textContent);
  var panelEl = U.querySelector('.vpanel'), dflt = panelEl.innerHTML, cur = null;
  var tabs = U.querySelectorAll('.utabs button'), panes = U.querySelectorAll('.upane');
  function tab(t){ tabs.forEach(function(b){ b.setAttribute('aria-selected', b.dataset.tab === t ? 'true' : 'false'); });
    panes.forEach(function(p){ p.classList.toggle('on', p.dataset.pane === t); }); reveal(); }
  function reveal(){
    var p = U.querySelector('.upane.on'), st = U.querySelector('.ustage'); if (!p || !cur) return;
    var lit = p.querySelector('.ulead.on, .lead.on'); if (!lit || st.scrollWidth <= st.clientWidth) return;
    var r = lit.getBoundingClientRect(), s = st.getBoundingClientRect();
    st.scrollLeft += (r.left + r.width / 2) - (s.left + s.width / 2);
  }
  function select(id){
    if (cur === id) id = null; cur = id;
    var it = id ? data.items[id] : null, leads = it ? it.leads : [];
    U.querySelectorAll('.ulist button').forEach(function(b){ b.setAttribute('aria-pressed', b.dataset.id === id ? 'true' : 'false'); });
    U.querySelectorAll('svg.wire').forEach(function(s){
      if (id) s.setAttribute('data-show', 'sel'); else s.removeAttribute('data-show');
      s.querySelectorAll('.lead').forEach(function(g){ g.classList.toggle('on', leads.indexOf(+g.dataset.lead) >= 0); });
      s.querySelectorAll('.hub').forEach(function(g){ g.classList.toggle('on', g.dataset.leads.split(' ').some(function(x){ return leads.indexOf(+x) >= 0; })); });
    });
    U.querySelectorAll('svg.uscale').forEach(function(s){
      if (id) s.setAttribute('data-show', id); else s.removeAttribute('data-show');
      s.querySelectorAll('.ulead').forEach(function(g){ g.classList.toggle('on', id && id.indexOf('l:') === 0 && +g.dataset.lead === +id.slice(2)); });
      s.querySelectorAll('[data-k]').forEach(function(e){ e.classList.toggle('on', !!id && e.getAttribute('data-k').split(' ').indexOf(id) >= 0); });
    });
    panelEl.innerHTML = it ? it.html : dflt;
    reveal();
  }
  tabs.forEach(function(b){ b.addEventListener('click', function(){ tab(b.dataset.tab); }); });
  U.querySelectorAll('.ulist button').forEach(function(b){ b.addEventListener('click', function(){ select(b.dataset.id); }); });
  U.querySelector('.ustage').addEventListener('click', function(ev){
    var g = ev.target.closest('[data-k], .lead'); if (!g) return;
    if (g.classList.contains('lead')) { select('l:' + g.dataset.lead); return; }
    var k = g.getAttribute('data-k').split(' '); select(k[0]);
  });
  U.addEventListener('keydown', function(ev){ if (ev.key === 'Escape') select(null); });
});
})();
"""


def unit_section(model, pos, report):
    leads = _lead_items(model)
    back, ends_of = scale_svg(model, pos, "back", report)
    plan, _ = scale_svg(model, pos, "plan", report)
    wire = PG.wiring_svg(model)
    items = {}
    for n, cs in leads:
        items[f"l:{n}"] = {"leads": [n], "html": lead_panel_html(model, n)}
    for b, lab in UNIT_PARTS:
        ls = sorted(ends_of.get(b, []))
        names = "".join(f"<li>{esc(panel.LEAD_NAMES[n][0].upper() + panel.LEAD_NAMES[n][1:])}</li>" for n in ls)
        items[f"u:{b}"] = {"leads": ls, "html": f'<div class="fh">{esc(lab)}</div>' + (f'<ul class="flist">{names}</ul>' if ls else '<p class="fnote">No lead.</p>')}

    def first_job(cs):
        jobs = [s["job"] for s, _p in cs if s]
        for j in jobs:
            if j not in ("gnd", "vplus"):
                return j
        return "vplus" if "vplus" in jobs else None
    lb = []
    for n, cs in leads:
        j = first_job(cs)
        dot = f'<i class="ldot{" j-" + j if j else ""}"></i>'
        lb.append(f'<button type="button" data-id="l:{n}" aria-pressed="false">{dot}{esc(panel.LEAD_SHORT[n])}</button>')
    mb = [f'<button type="button" data-id="u:{b}" aria-pressed="false">{esc(lab)}</button>' for b, lab in UNIT_PARTS]
    key = ("".join(f'<li><i class="sw j-{k}"></i>{esc(v[0])}</li>' for k, v in panel.JOBS.items())
           + '<li><span class="bandkey"></span>diagram: black ends = black wire, marked in the line\'s colour</li>'
           + '<li><span class="markkey"></span>to scale: black wire, its mark at both ends</li>'
           + '<li><i class="sw" style="background:var(--muted)"></i>bought cable</li>')
    default = ('<div class="fh">Choose a lead</div>'
               '<p class="ffit">Tap a lead in the list, a socket dot, or a wire. Tap it again to clear.</p>'
               '<p class="fnote">The diagram is for reading the wiring; the two drawings to scale show where things are.</p>')
    data = json.dumps({"items": items}).replace("</", "<\\/")
    return f"""<div class="uview bleed" id="unit">
<ul class="ukey wlegend">{key}</ul>
<div class="utabs" role="tablist"><button type="button" data-tab="wire" aria-selected="true">Wiring diagram</button><button type="button" data-tab="back" aria-selected="false">From behind, door off</button><button type="button" data-tab="plan" aria-selected="false">From above</button></div>
<div class="umain"><nav class="ulist" aria-label="Leads, boards and modules"><span class="vgl">Leads</span>{"".join(lb)}<span class="brk"></span><span class="vgl">Boards and modules</span>{"".join(mb)}</nav>
<div class="ustage"><div class="upane on" data-pane="wire">{wire}</div><div class="upane" data-pane="back">{back}</div><div class="upane" data-pane="plan">{plan}</div></div>
<aside class="vpanel">{default}</aside></div>
<script type="application/json" class="udata">{data}</script></div>"""
