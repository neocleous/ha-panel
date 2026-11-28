"""The revised page's own parts (D572, D573): plain names, job colours, steps, the wiring drawing."""
from __future__ import annotations

import json

import panel
from model import wire_words
from svgboard import esc


def job_of_net(net):
    return panel.NET_JOB.get(net)


def jt(job, text=None):
    """A job as a small colour tag."""
    name, colour, *_ = panel.JOBS[job]
    return f'<span class="jt"><i class="sw j-{job}"></i>{esc(text or name)}</span>'


def plain_net(net):
    return panel.NET_NAMES.get(net, net) if net else "not connected"


def lead_name(n):
    return panel.LEAD_NAMES[n]


def end_name(model, pid):
    """A wire end in plain words: 'the 20 V socket (J1), pin 1', 'radar, VCC', 'Pi pin 8'."""
    dev, rest = pid.split(":", 1)
    if dev == "main":
        ref, num = rest.split(".")
        return f'the {panel.SOCKET_NAMES.get(ref, ref)} <small>({ref})</small>, pin {num}'
    if dev == "pi":
        return f"Pi pin {rest}"
    mod = panel.MODULES[dev]
    label = mod["pins"][rest][0].replace("UART_", "")
    if dev == "respeaker":
        side, pad = rest.split(".")
        fn = label.split()[-1]
        return f"ReSpeaker, emptied pads with left/right at {'ground' if side == 'L' else '3.3 V'}: {fn}"
    if dev in ("micL", "micR"):
        return f"{mod['name'].lower()}, pad {rest}"
    return f"{mod['name']}, {label}"


def end_group(model, pids):
    """A plain heading for a column of wire ends when they share one place: 'Radar socket (J5)', 'Radar', 'Pi header'."""
    devs = {p.split(":")[0] for p in pids}
    if len(devs) != 1:
        return None
    dev = devs.pop()
    if dev == "main":
        refs = {p[5:].split(".")[0] for p in pids}
        if len(refs) == 1:
            r = refs.pop()
            n = panel.SOCKET_NAMES.get(r, r)
            return f"{n[0].upper()}{n[1:]} ({r})"
        return "Main board"
    if dev == "pi":
        return "Pi header"
    if dev == "respeaker":
        return "ReSpeaker pads"
    return panel.MODULES[dev]["name"]


def end_short(model, pid, head):
    if not head:
        return end_name(model, pid)
    dev, rest = pid.split(":", 1)
    if dev == "main":
        ref, num = rest.split(".")
        return f"pin {num}" if head != "Main board" else f"{panel.SOCKET_NAMES.get(ref, ref)} pin {num}"
    if dev == "pi":
        return f"pin {rest}"
    if dev == "respeaker":
        fn = panel.MODULES[dev]["pins"][rest][0].split()[-1]
        return f"pad {rest.split('.')[1]}, " + {"VDD": "3.3 V", "GND": "ground", "CLK": "clock", "L/R": "left/right", "DATA": "data"}[fn]
    if dev in ("micL", "micR"):
        return f"pad {rest}"
    return panel.MODULES[dev]["pins"][rest][0].replace("UART_", "")


# ------------------------------------------------------------------------------------------------ CSS
def css():
    def block(i):
        return "".join(f".j-{k}{{{{background:{v[i]}}}}}.s-{k}{{{{stroke:{v[i]}}}}}.f-{k}{{{{fill:{v[i]}}}}}.pad.pj.f-{k}{{{{fill:{v[i]}}}}}" for k, v in panel.JOBS.items())
    light, dark = block(2), block(3)
    return (light.replace("{{", "{").replace("}}", "}")
            + "@media (prefers-color-scheme: dark){:root:not([data-theme=light]) " + dark.replace("{{", "{").replace("}}", "}").replace("}.", "} :root:not([data-theme=light]) .") + "}"
            + ":root[data-theme=dark] " + dark.replace("{{", "{").replace("}}", "}").replace("}.", "} :root[data-theme=dark] .")
            + CSS_REST)


CSS_REST = """
.jt{display:inline-flex;align-items:center;gap:7px;white-space:nowrap} .jt .sw{width:18px;height:6px;border-radius:3px;box-shadow:0 0 0 1px var(--muted) inset}
td small,.end small{font:12px var(--f-mono);color:var(--muted)}
@media (max-width:600px){table.stack{min-width:0}.stack thead{display:none}.stack tr{display:grid;padding:8px 0;border-bottom:1px solid var(--rule)}
.stack td{display:block;border:0;padding:2px 12px;white-space:normal}.stack td:empty{display:none}
.stack td[data-l]::before{content:attr(data-l);display:block;font:600 11px var(--f-mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}}
/* steps */
section > *{min-width:0} .steps-card > *,.step > *{min-width:0}
.steps-card{min-width:0;background:var(--panel);border:1px solid var(--rule);border-radius:12px;padding:18px 20px;display:grid;gap:14px}
.sc-top{display:flex;justify-content:space-between;gap:12px;align-items:baseline;flex-wrap:wrap}
.sc-pos{font:600 12px var(--f-mono);color:var(--muted)}
.sc-list{width:min(100%,420px);font:15px var(--f-body);border:1px solid var(--rule);border-radius:8px;padding:6px 8px;background:var(--panel);color:var(--ink);max-width:100%}
.step{display:none;gap:12px} .step.on{display:grid}
.step h3{margin:0;font-size:21px}
.sh{font:700 12px var(--f-mono);letter-spacing:.06em;text-transform:uppercase;margin:4px 0 2px}
.sh.do{color:var(--ink)} .sh.note{color:var(--accent)} .sh.tip{color:var(--muted)}
.step ol{margin:0;padding-left:1.4em;display:grid;gap:6px;max-width:70ch} .step ol li::marker{font:600 13px var(--f-mono);color:var(--accent)}
.step p{margin:0;max-width:70ch}
.note-box{background:var(--warnbg);border-left:3px solid var(--accent);padding:10px 12px;border-radius:2px 6px 6px 2px}
.reading{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;margin-top:6px}
.reading label{font:600 13px var(--f-mono)} .reading input{font:16px var(--f-mono);width:8.5em;padding:6px 8px;border:1px solid var(--rule);border-radius:6px;background:var(--panel);color:var(--ink)}
.reading .exp{color:var(--muted);font-size:13px}
.sc-nav{display:flex;gap:10px;justify-content:space-between;align-items:center}
.sc-nav button{font:600 15px var(--f-body);border-radius:10px;border:1px solid var(--rule);background:var(--panel);color:var(--ink);padding:10px 16px;min-height:48px;cursor:pointer}
.sc-nav .next{background:var(--ink);color:var(--panel);border-color:var(--ink);font-size:17px;padding:12px 26px;flex:0 1 260px}
.sc-nav button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
/* wiring */
.wiring{background:var(--panel);border:1px solid var(--rule);border-radius:10px;overflow-x:auto;padding:8px}
.wiring svg{display:block;width:100%;height:auto}
.wb{fill:var(--pcb);stroke:var(--pcbline);stroke-width:1.5} .wsock{fill:var(--body);stroke:var(--ink);stroke-width:1.2}
.wmod{fill:var(--modbg);stroke:var(--ink);stroke-width:1.3} .wcable{fill:none;stroke:var(--muted);stroke-width:5;stroke-linecap:round;stroke-dasharray:1 0}
.ww{fill:none;stroke-width:4.5;stroke-linecap:square} .wwh{fill:none;stroke:var(--ink);stroke-width:6.5;stroke-linecap:square}
.wport{fill:var(--panel);stroke:var(--ink);stroke-width:1.1}
.band{stroke:var(--panel);stroke-width:1} .band-black{fill:#23282b} .band-brown{fill:#7a4b2a}
.t-w{font:600 12px var(--f-body);fill:var(--ink)} .t-ws{font:11px var(--f-mono);fill:var(--muted)} .t-wp{font:600 10.5px var(--f-mono);fill:var(--ink)}
.t-wt{font:700 13px var(--f-display);letter-spacing:.06em;fill:var(--muted)}
svg.wire .lead{transition:opacity .18s}
svg.wire[data-show]:not([data-show="all"]) .lead:not(.on){opacity:.1}
svg.wire[data-show]:not([data-show="all"]) .hub:not(.on){opacity:.3}
@media (prefers-reduced-motion: reduce){svg.wire .lead{transition:none}}
.wlegend{display:flex;flex-wrap:wrap;gap:6px 18px;list-style:none;margin:0;padding:0;font:13px var(--f-body);color:var(--muted)}
.wlegend li{display:flex;align-items:center;gap:7px} .wlegend .sw{width:22px;height:6px;border-radius:3px;box-shadow:0 0 0 1px var(--muted) inset}
.bandkey{display:inline-block;width:22px;height:6px;border-radius:3px;background:linear-gradient(90deg,#23282b 0 6px,#d3302a 6px 16px,#23282b 16px)}
"""


# ------------------------------------------------------------------------------------------------ colour table
def colour_tables(model):
    legend_rows = []
    for k, (name, colour, *_r) in panel.JOBS.items():
        legend_rows.append([jt(k), esc(colour)])
    rows = []
    for l in model.leads:
        first = True
        for a, b in l["wires"]:
            s = model.wire_spec(l, a, b)
            rows.append([f"<b>{esc(lead_name(l['n'])[0].upper() + lead_name(l['n'])[1:])}</b>" if first else "", end_name(model, a), end_name(model, b), jt(s["job"], plain_net(s["net"])), esc(wire_words(s))])
            first = False
    return legend_rows, rows


# ------------------------------------------------------------------------------------------------ steps
def step_html(i, n, sid, st):
    out = [f'<div class="step{" on" if i == 0 else ""}" data-i="{i}"' + (f' data-show="{st["show"]}"' if st.get("show") else "") + ">",
           f'<h3>{esc(st["title"])}</h3>']
    if st.get("picture"):
        out.append(st["picture"])
    if st.get("do"):
        out.append('<div class="sh do">Do</div><ol>' + "".join(f"<li>{d}</li>" for d in st["do"]) + "</ol>")
    if st.get("table"):
        out.append(st["table"])
    if st.get("note") or st.get("fields"):
        body = f"<p>{st['note']}</p>" if st.get("note") else ""
        for f in st.get("fields", []):
            body += (f'<div class="reading"><label for="{sid}-{f["id"]}">{f["label"]}</label>'
                     f'<input id="{sid}-{f["id"]}" data-key="{sid}-{f["id"]}" inputmode="decimal" autocomplete="off"><span class="exp">{f["expect"]}</span></div>')
        out.append(f'<div class="sh note">Note</div><div class="note-box">{body}</div>')
    if st.get("tip"):
        out.append(f'<div class="sh tip">Tip</div><p class="muted">{st["tip"]}</p>')
    out.append("</div>")
    return "".join(out)


def stepper(sid, section_name, steps, stage=""):
    n = len(steps)
    opts = "".join(f'<option value="{i}">{i + 1}. {esc(s["title"])}</option>' for i, s in enumerate(steps))
    body = "".join(step_html(i, n, sid, s) for i, s in enumerate(steps))
    return f"""<div class="steps-card" id="{sid}" data-stepper>
<div class="sc-top"><span class="sc-pos">{esc(section_name)} · step <b class="cur">1</b> of {n}</span><select class="sc-list" aria-label="Go to a step">{opts}</select></div>
{stage}{body}
<div class="sc-nav"><button type="button" class="back">Back</button><button type="button" class="next">Next step</button></div></div>"""


STEP_JS = r"""
(() => {
const S = Array.from(document.querySelectorAll('[data-stepper]'));
const store = { get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }, set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} } };
S.forEach((card, si) => {
  const steps = Array.from(card.querySelectorAll('.step'));
  const cur = card.querySelector('.cur'), list = card.querySelector('.sc-list'), stage = card.querySelector('svg.wire');
  let i = 0;
  function show(k, scroll) {
    i = Math.max(0, Math.min(steps.length - 1, k));
    steps.forEach((s, j) => s.classList.toggle('on', j === i));
    cur.textContent = i + 1; list.value = i;
    card.querySelector('.back').disabled = i === 0 && si === 0;
    card.querySelector('.next').textContent = (i === steps.length - 1) ? (si < S.length - 1 ? 'Next section' : 'Done') : 'Next step';
    if (stage) { const sh = steps[i].dataset.show || 'all'; stage.setAttribute('data-show', sh);
      stage.querySelectorAll('.lead').forEach(g => g.classList.toggle('on', g.dataset.lead === sh));
      stage.querySelectorAll('.hub').forEach(g => g.classList.toggle('on', g.dataset.leads.split(' ').indexOf(sh) >= 0));
      if (!stage._full) stage._full = stage.getAttribute('viewBox');
      const lit = stage.querySelector('.lead.on');
      if (lit && stage.clientWidth < 700) { const b = lit.getBBox(), p = 30;
        stage.setAttribute('viewBox', [b.x - p, b.y - p, b.width + 2 * p, b.height + 2 * p].map(n => n.toFixed(1)).join(' ')); }
      else stage.setAttribute('viewBox', stage._full); }
    store.set('hae-' + card.id, String(i));
    if (scroll) card.scrollIntoView({ block: 'start', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  }
  card.querySelector('.next').addEventListener('click', () => {
    if (i < steps.length - 1) show(i + 1, true);
    else if (si < S.length - 1) { S[si + 1]._show(0, true); }
  });
  card.querySelector('.back').addEventListener('click', () => {
    if (i > 0) show(i - 1, true); else if (si > 0) { const p = S[si - 1]; p._show(p._n - 1, true); }
  });
  list.addEventListener('change', () => show(+list.value, false));
  card.querySelectorAll('input[data-key]').forEach(inp => { const v = store.get('hae-' + inp.dataset.key); if (v) inp.value = v;
    inp.addEventListener('input', () => store.set('hae-' + inp.dataset.key, inp.value)); });
  card._show = show; card._n = steps.length;
  const saved = parseInt(store.get('hae-' + card.id) || '0', 10);
  show(isNaN(saved) ? 0 : saved, false);
});
})();
"""


# ------------------------------------------------------------------------------------------------ wiring drawing
SOCK_SHORT = {"J1": "20 V", "J2": "Pi power", "J3": "Pi pads", "J4": "Pi pads", "J5": "Radar", "J6": "Touch", "J8": "Left speaker",
              "J9": "Right speaker", "J10": "BME680", "J11": "Light sensor"}


def pin_label(lab):
    return lab.split()[0].replace("UART_", "")


def wiring_svg(model):
    """Schematic of every lead: the main board's sockets on its edges in their order, each wire square and straight
    to the far end's pin, drawn in its job's colour; black or brown insulation shown as bands at both ends."""
    main = model.boards["main"]
    bx0, by0, bx1, by1 = main["bbox"]
    BX, BY, BW, BH = 330, 330, 600, 330
    kx = BW / (bx1 - bx0)
    ky = BH / (by1 - by0)
    PIT = 18

    def pad_xy(ref, num):
        x, y = model.pad("main", ref, num)["xy"]
        return BX + (x - bx0) * kx, BY + (y - by0) * ky

    # Which socket exits which edge.
    edge = {"J9": "bottom", "J3": "bottom", "J1": "bottom", "J4": "bottom", "J6": "bottom", "J2": "bottom", "J8": "bottom",
            "J5": "left", "J10": "left", "J11": "top"}
    wires_at = {}
    for l in model.leads:
        for a, b in l["wires"]:
            if a.startswith("main:"):
                ref, num = a[5:].split(".")
                wires_at.setdefault(ref, []).append((int(num), l, a, b))
    # Ports, packed along each edge in the sockets' true order.
    ports = {}

    def pack(refs, axis, gap=30):
        items = []
        for ref in refs:
            n = len(wires_at.get(ref, [])) or 1
            cs = [pad_xy(ref, p["num"]) for p in model.parts[("main", ref)]["pads"]]
            c = sum((x if axis == "x" else y) for x, y in cs) / len(cs)
            items.append([ref, c - (n - 1) * PIT / 2, n])
        items.sort(key=lambda t: t[1])
        for j in range(1, len(items)):
            prev = items[j - 1]
            lo = prev[1] + (prev[2] - 1) * PIT + gap
            if items[j][1] < lo:
                items[j][1] = lo
        return items

    out_w, out_m, out_s = [], [], []
    MX0, MX1 = 960, 1150
    bottom = pack([r for r, e in edge.items() if e == "bottom"], "x")
    left = pack([r for r, e in edge.items() if e == "left"], "y", gap=72)
    over = left[-1][1] + (left[-1][2] - 1) * PIT - (BY + BH - 80)
    if over > 0:
        for it in left:
            it[1] -= over
    top = pack([r for r, e in edge.items() if e == "top"], "x")
    W = 1280
    H = 1080
    svg = [f'<svg class="wire" viewBox="0 0 {W} {H}" role="img" aria-label="Every lead from its socket to its far end, in the colour of its job">']
    svg.append('<g class="hub" data-leads="1 2 3 4 5 6 7 8 9 10 15">')
    svg.append(f'<rect class="wb" x="{BX}" y="{BY}" width="{BW}" height="{BH}" rx="10"/>'
               f'<text class="t-wt" x="{BX + BW / 2}" y="{BY + BH / 2 - 8}" text-anchor="middle">MAIN BOARD</text>'
               f'<text class="t-ws" x="{BX + BW / 2}" y="{BY + BH / 2 + 12}" text-anchor="middle">from the door side · sockets in their real order</text>')
    svg.append('</g>')

    def sock_label(ref, x, y, anchor="middle"):
        nm = SOCK_SHORT.get(ref, ref)
        if anchor == "middle":           # keep the label inside the board's outline
            half = 3.6 * (len(nm) + len(ref) + 1) + 4
            x = min(max(x, BX + 8 + half), BX + BW - 8 - half)
        return f'<text class="t-w" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}">{esc(nm)} <tspan class="t-ws">{ref}</tspan></text>'

    def band(x, y, vertical, ins):
        if ins not in ("black", "brown"):
            return ""
        return (f'<rect class="band band-{ins}" x="{x - (3.5 if vertical else 7):.1f}" y="{y - (7 if vertical else 3.5):.1f}" '
                f'width="{7 if vertical else 14}" height="{14 if vertical else 7}" rx="2"/>')

    def wire(path, spec, ends):
        """ends: list of (x, y, vertical) where the insulation band goes."""
        c = spec["draw"]
        job = spec["job"]
        halo = '<path class="wwh" d="%s"/>' % path if job in ("aclk",) else ""
        bands = "".join(band(x, y, v, spec["insulation"] if spec["insulation"] != c else None) for x, y, v in ends)
        return f'{halo}<path class="ww s-{job}" d="{path}"/>{bands}'

    def module_box(x, y, w, h, title, sub=""):
        return (f'<rect class="wmod" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="6"/>'
                f'<text class="t-w" x="{x + 8:.1f}" y="{y + 17:.1f}">{esc(title)}</text>' + (f'<text class="t-ws" x="{x + 8:.1f}" y="{y + 31:.1f}">{esc(sub)}</text>' if sub else ""))

    groups = {}

    def g(n):
        return groups.setdefault(n, [])

    # ---- bottom edge: straight down to the far ends.
    row_a, row_b = BY + BH + 120, BY + BH + 250
    pi_ports = {}
    for bi, (ref, x0, n) in enumerate(bottom):
        ws = sorted(wires_at.get(ref, []), key=lambda t: t[0])
        xs = [x0 + k * PIT for k in range(max(n, 1))]
        sx0, sx1 = xs[0] - 10, xs[-1] + 10
        lead_n = ws[0][1]["n"] if ws else (15 if ref == "J2" else None)
        grp = g(lead_n) if lead_n else out_s
        grp.append(f'<rect class="wsock" x="{sx0:.1f}" y="{BY + BH - 16:.1f}" width="{sx1 - sx0:.1f}" height="16" rx="2"/>')
        grp.append(sock_label(ref, (sx0 + sx1) / 2, BY + BH - (26 if bi % 2 == 0 else 46)))
        if ref == "J2":
            pi_ports["usb"] = (xs[0], BY + BH)
            continue
        for k, (num, l, a, b) in enumerate(ws):
            x = xs[k]
            spec = model.wire_spec(l, a, b)
            g(l["n"]).append(f'<text class="t-wp" x="{x:.1f}" y="{BY + BH - 4:.1f}" text-anchor="middle">{num}</text>')
            if b.startswith("pi:"):
                pi_ports[int(b[3:])] = (x, spec, l)
                continue
            y1 = row_a
            g(l["n"]).append(wire(f"M{x:.1f},{BY + BH} L{x:.1f},{y1}", spec, [(x, BY + BH + 12, True), (x, y1 - 12, True)]))
            g(l["n"]).append(f'<circle class="wport" cx="{x:.1f}" cy="{y1}" r="4"/>')
        # far-end module for this socket
        if ws and not ws[0][3].startswith("pi:"):
            l = ws[0][1]
            dev = ws[0][3].split(":")[0]
            mod = panel.MODULES[dev]
            w = max(sx1 - sx0 + 16, 60)
            cx = (sx0 + sx1) / 2
            g(l["n"]).append(module_box(cx - w / 2, row_a, w, 70, "", ""))
            g(l["n"]).append(f'<text class="t-w" x="{cx:.1f}" y="{row_a + 88:.1f}" text-anchor="middle">{esc(mod["name"])}</text>')
            for k, (num, l2, a, b) in enumerate(ws):
                lab = pin_label(mod["pins"][b.split(":")[1]][0])
                g(l["n"]).append(f'<text class="t-wp" x="{xs[k] + 4:.1f}" y="{row_a + 14:.1f}" transform="rotate(90 {xs[k] + 4:.1f} {row_a + 14:.1f})">{esc(lab)}</text>')
    # ---- the Pi: housings directly under the wires; display lead from the left; Pi power cable.
    if pi_ports:
        pins = sorted(k for k in pi_ports if isinstance(k, int))
        x_lo = min(pi_ports[k][0] for k in pins) - 150
        x_hi = pi_ports["usb"][0] + 40 if "usb" in pi_ports else max(pi_ports[k][0] for k in pins) + 40
        out_m.append('<g class="hub" data-leads="8 9 10 11 12 15 16">' + module_box(x_lo, row_b, x_hi - x_lo, 92, "", ""))
        out_m.append(f'<text class="t-w" x="{x_lo + 8:.1f}" y="{row_b + 20}">Raspberry Pi 5</text><text class="t-ws" x="{x_lo + 8:.1f}" y="{row_b + 34}">header pins</text></g>')
        for p in pins:
            x, spec, l = pi_ports[p]
            g(l["n"]).append(wire(f"M{x:.1f},{BY + BH} L{x:.1f},{row_b}", spec, [(x, BY + BH + 12, True), (x, row_b - 12, True)]))
            g(l["n"]).append(f'<circle class="wport" cx="{x:.1f}" cy="{row_b}" r="4"/><text class="t-wp" x="{x:.1f}" y="{row_b + 50}" text-anchor="middle">{p}</text>')
        for h in ("1", "2", "3"):
            hp = [p for p in pins if p in panel.PI_HOUSINGS[h]["pins"]]
            if hp:
                xs = [pi_ports[p][0] for p in hp]
                n = next(pi_ports[p][2]["n"] for p in hp)
                g(n).append(f'<rect class="housing" x="{min(xs) - 6:.1f}" y="{row_b + 6}" width="{max(xs) - min(xs) + 12:.1f}" height="28" rx="4"/>')
        if "usb" in pi_ports:
            x, y = pi_ports["usb"]
            g(15).append(f'<path class="wcable" d="M{x:.1f},{y} L{x:.1f},{row_b}"/><text class="t-wp" x="{x:.1f}" y="{row_b + 50}" text-anchor="middle">USB-C</text>')
        # display lead: display box at the far left of row B, into Pi pins 2 and 6.
        dl = next(l for l in model.leads if l["n"] == 11)
        dx = x_lo + 20
        ys = {2: row_b + 62, 6: row_b + 78}
        g(11).append(f'<rect class="housing" x="{dx + 80:.1f}" y="{row_b + 52}" width="34" height="34" rx="4"/>')
        for a, b in dl["wires"]:
            spec = model.wire_spec(dl, a, b)
            p = int(b[3:])
            y = ys[p]
            g(11).append(wire(f"M{x_lo - 120:.1f},{y} L{dx + 96:.1f},{y}", spec, [(x_lo - 108, y, False), (dx + 84, y, False)]))
            g(11).append(f'<text class="t-wp" x="{dx + 104:.1f}" y="{y + 4}">{p}</text>')
        g(11).append(module_box(x_lo - 250, row_b + 40, 130, 52, "Display", "its 4-pin header"))
        # the DSI ribbon: display to the Pi's DSI socket, a bought cable
        yr = row_b + 48
        g(12).append(f'<path class="wcable" d="M{x_lo - 120:.1f},{yr} L{x_lo:.1f},{yr}"/>'
                     f'<text class="t-wp" x="{x_lo + 6:.1f}" y="{yr + 4}">DSI</text>')
        # the ReSpeaker's USB cable: Pi USB-A, round the right, up into the ReSpeaker's USB-C
        yu, xr = row_b + 46, MX1 + 40
        g(16).append(f'<path class="wcable" d="M{x_hi:.1f},{yu} L{xr},{yu} L{xr},{442}"/>'
                     f'<text class="t-wp" x="{x_hi + 8:.1f}" y="{yu - 8}">USB-A</text>'
                     f'<text class="t-wp" x="{xr - 8}" y="{434}" text-anchor="end">USB-C</text>')
    # ---- left edge: straight left to the radar and the BME680 board.
    for ref, y0, n in left:
        ws = sorted(wires_at.get(ref, []), key=lambda t: t[0])
        ys = [y0 + k * PIT for k in range(n)]
        l = ws[0][1]
        g(l["n"]).append(f'<rect class="wsock" x="{BX:.1f}" y="{ys[0] - 10:.1f}" width="16" height="{ys[-1] - ys[0] + 20:.1f}" rx="2"/>')
        g(l["n"]).append(sock_label(ref, BX + 24, (ys[0] + ys[-1]) / 2 - 2, "start"))
        mx = 90
        dev = ws[0][3].split(":")[0]
        mod = panel.MODULES[dev]
        g(l["n"]).append(module_box(mx - 10, ys[0] - 30, 130, ys[-1] - ys[0] + 44, ""))
        g(l["n"]).append(f'<text class="t-w" x="{mx - 4}" y="{ys[0] - 36:.1f}">{esc(mod["name"])}</text>')
        for k, (num, l2, a, b) in enumerate(ws):
            y = ys[k]
            spec = model.wire_spec(l2, a, b)
            g(l["n"]).append(wire(f"M{BX},{y:.1f} L{mx + 120},{y:.1f}", spec, [(BX - 12, y, False), (mx + 132, y, False)]))
            lab = pin_label(mod["pins"][b.split(":")[1]][0])
            g(l["n"]).append(f'<text class="t-wp" x="{mx + 2}" y="{y + 4:.1f}">{esc(lab)}</text><text class="t-wp" x="{BX + 4}" y="{y + 4:.1f}">{num}</text>')
    # ---- top edge: straight up to the light sensor.
    for ref, x0, n in top:
        ws = sorted(wires_at.get(ref, []), key=lambda t: t[0])
        xs = [x0 + k * PIT for k in range(n)]
        l = ws[0][1]
        g(l["n"]).append(f'<rect class="wsock" x="{xs[0] - 10:.1f}" y="{BY}" width="{xs[-1] - xs[0] + 20:.1f}" height="16" rx="2"/>')
        g(l["n"]).append(sock_label(ref, (xs[0] + xs[-1]) / 2, BY + 32))
        ty = BY - 150
        dev = ws[0][3].split(":")[0]
        mod = panel.MODULES[dev]
        g(l["n"]).append(module_box(xs[0] - 20, ty - 50, xs[-1] - xs[0] + 40, 62, ""))
        g(l["n"]).append(f'<text class="t-w" x="{(xs[0] + xs[-1]) / 2:.1f}" y="{ty - 58}" text-anchor="middle">{esc(mod["name"])}</text>')
        for k, (num, l2, a, b) in enumerate(ws):
            x = xs[k]
            spec = model.wire_spec(l2, a, b)
            g(l["n"]).append(wire(f"M{x:.1f},{BY} L{x:.1f},{ty + 12}", spec, [(x, BY - 12, True), (x, ty + 24, True)]))
            lab = pin_label(mod["pins"][b.split(":")[1]][0])
            g(l["n"]).append(f'<text class="t-wp" x="{x + 4:.1f}" y="{ty + 8}" transform="rotate(-90 {x + 4:.1f} {ty + 8})">{esc(lab)}</text><text class="t-wp" x="{x:.1f}" y="{BY + 12}" text-anchor="middle">{num}</text>')
    # ---- microphone leads: each strip straight across to its ReSpeaker pads, in cable order.
    for k, n in enumerate((13, 14)):
        l = next(x for x in model.leads if x["n"] == n)
        y0 = 126 + k * 170
        strip = panel.MODULES["micL" if n == 13 else "micR"]
        g(n).append(module_box(MX0 - 110, y0 - 30, 100, len(l["wires"]) * PIT + 46, strip["name"].replace(" microphone strip", " strip")))
        for j, (a, b) in enumerate(l["wires"]):
            y = y0 + j * PIT + 6
            spec = model.wire_spec(l, a, b)
            g(n).append(wire(f"M{MX0 - 10},{y:.1f} L{MX1 - 70},{y:.1f}", spec, [(MX0 + 2, y, False), (MX1 - 82, y, False)]))
            pa = a.split(":")[1]
            pb = b.split(".")[-1]
            fn = {"VDD": "3.3 V", "GND": "ground", "CLK": "clock", "L/R": "left/right", "DATA": "data"}[panel.MODULES["respeaker"]["pins"][b.split(":")[1]][0].split()[-1]]
            g(n).append(f'<text class="t-wp" x="{MX0 - 24}" y="{y + 4:.1f}" text-anchor="end">{pa}</text><text class="t-wp" x="{MX1 - 64}" y="{y + 4:.1f}">{pb} {esc(fn)}</text>')
        b4, b6 = l["bridge"]
        g(n).append(f'<text class="t-ws" x="{MX1 - 64}" y="{y0 + len(l["wires"]) * PIT + 14:.1f}">bridge 4 to 6</text>')
    out_m.append('<g class="hub" data-leads="13 14 16">' + module_box(MX1 - 74, 62, 140, 380, "", ""))
    out_m.append(f'<text class="t-w" x="{MX1 - 66}" y="80">ReSpeaker</text>')
    out_m.append(f'<text class="t-ws" x="{MX1 - 66}" y="100">pads with left/right</text><text class="t-ws" x="{MX1 - 66}" y="112">at ground</text>'
                 f'<text class="t-ws" x="{MX1 - 66}" y="270">pads with left/right</text><text class="t-ws" x="{MX1 - 66}" y="282">at 3.3 V</text></g>')
    svg += out_m + out_s
    for n, parts in sorted(groups.items(), key=lambda t: t[0]):
        svg.append(f'<g class="lead" data-lead="{n}">' + "".join(parts) + "</g>")
    svg.append("</svg>")
    return "".join(svg)


def wiring_legend():
    items = "".join(f'<li><i class="sw j-{k}"></i>{esc(v[0])}</li>' for k, v in panel.JOBS.items())
    return (f'<ul class="wlegend">{items}<li><span class="bandkey"></span>black ends: a black wire, marked in the line\'s colour</li>'
            '<li><i class="sw" style="background:var(--muted)"></i>bought cable</li></ul>')
