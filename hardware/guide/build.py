#!/usr/bin/env python3
"""Build the HA panel electronics page: model -> checks -> page. Fails (exit 1) on any check.

    python3 hardware/guide/build.py            # writes hardware/guide/ha-panel-electronics.html
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))
sys.path.insert(0, os.path.join(HERE, "data"))

import checks  # noqa: E402
import panel  # noqa: E402
import render as R  # noqa: E402
from model import Model, net_class  # noqa: E402
from svgboard import esc  # noqa: E402

OUT = os.path.join(HERE, "ha-panel-electronics.html")
POSITIONS = os.path.join(HERE, "data", "positions.json")


def section(title, body, note=None, cls=""):
    n = f'<p class="sect-note">{note}</p>' if note else ""
    return f'<section class="{cls}"><h2>{esc(title)}</h2>{n}{body}</section>'


def table(head, rows, cls=""):
    th = "".join(f"<th>{esc(h)}</th>" for h in head)
    return f'<div class="tw"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>' + "".join(
        "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table></div>"


def tp_where(m, ref):
    """A test pad's place, from the board file: mm from the left edge and from the bottom (socket) edge, seen from the door."""
    p = m.parts[("main", ref)]
    x, y = p["pads"][0]["xy"]
    b = m.boards["main"]["bbox"]
    return f"{ref} ({x - b[0]:.1f} from the left, {b[3] - y:.1f} up)"


def build():
    m = Model()
    fails, passes = checks.run(m)
    if fails:
        print("BUILD FAILED: the checks found problems", file=sys.stderr)
        for f in fails:
            print("  -", f, file=sys.stderr)
        sys.exit(1)
    ends = R.lead_ends(m)
    main = m.boards["main"]
    dnp = [p["ref"] for p in main["parts"] if p["dnp"]]
    tht = [p["ref"] for p in main["parts"] if p["type"] == "through_hole"]

    # ------------------------------------------------------------------ header and warnings
    head = f"""<header>
<div class="eyebrow">HA Touch Panel · electronics</div>
<h1>HA panel electronics</h1>
<p class="dek">A USB-C charger feeds 20 V through the inlet board to the main board. The main board protects it, makes 5 V for the Pi and the radar and 3.3 V for the sensors, and drives two speakers from a TAS5756M. The Pi talks to the amplifier, the touch board and both sensors on one I²C bus, to the radar over UART0, and sends audio over I²S. The ReSpeaker Lite takes the two microphone strips and reaches the Pi over USB.</p>
<ul class="facts"><li><b>Supply</b> 20 V, USB-C PD</li><li><b>Rails</b> 5 V (NID100-5) · 3.3 V (TPS70933)</li><li><b>I²C1</b> GPIO2 / GPIO3: 1b, 48, 4c, 76/77</li><li><b>UART0</b> GPIO14 / 15, 256000 8N1</li><li><b>I²S</b> GPIO18–21</li><li><b>Mute</b> GPIO22</li><li><b>Boards</b> main rev 3.3 · touch rev E · mic strip rev 3 × 2</li></ul>
</header>
<div class="warn">
<div><b>20 V goes on first, on the middle socket</b><p>J9, J1 and J8 are three identical 2-way sockets in one row. J1 is the middle one. A 20 V plug on a speaker socket can destroy the board. Mark the 20 V plug and the board beside J1.</p></div>
<div><b>Measure the power module before soldering it</b><p>From PS1's row of pins to its component side: about 5.0 mm, carry on. About 8.3 mm, stop: the board is wrong for it. Anything else, stop.</p></div>
<div><b>Pins 2 and 4 on the Pi are both 5 V</b><p>The display's power lead goes on pins 2-4-6, GND on pin 6. Check the row before pressing the housing home.</p></div>
</div>"""

    # ------------------------------------------------------------------ the unit
    if os.path.exists(POSITIONS):
        unit = section("The unit, to scale", R.unit_viewer(m, json.load(open(POSITIONS))),
                       "Every board, module and lead at its place in the model (version 91), drawn from the bodies' own outlines. Above: from behind with the door off. Below: from above. The numbers are the leads.")
    else:
        unit = section("The unit, to scale, door off", '<p class="sect-note"><b>Waiting for the model.</b> The places of the boards and modules in the unit come from the model, version 91. They are not on this page yet.</p>')

    # ------------------------------------------------------------------ main board viewer
    items = R.board_items(m, "main", ends)
    for l in m.leads:
        if any(a.startswith("main:") for a, _ in l["wires"]):
            toks = [f"l:{l['n']}"] + [f"p:main:{a[5:].split('.')[0]}" for a, _ in l["wires"] if a.startswith("main:")]
            items.append({"id": f"L{l['n']}", "label": f"lead {l['n']}", "tokens": sorted(set(toks)), "own": [f"l:{l['n']}"], "html": R.lead_panel(m, l)})
    chips = [(g, [(f"main:{r}", r) for r in refs]) for g, refs in R.GROUPS_MAIN]
    chips.append(("Leads", [(f"L{l['n']}", f"L{l['n']}") for l in m.leads if any(a.startswith("main:") for a, _ in l["wires"])]))
    default = ('<div class="fh">Main board</div><div class="fsub">rev 3.3 · 120 names · every part on the door side</div>'
               '<p class="ffit">Tap a part, a pad or a lead tag. Its pads light up with every pad on the same net, and this panel lists what each pad joins.</p>'
               '<p class="fnote">Dashed outlines: places left empty (' + ", ".join(dnp) + '). Dashed circles: the M3 screw heads (Ø5.7).</p>')
    mainview = section("Main board, to scale", R.viewer(m, "main", R.main_board_svg(m, ends), chips, items, default),
                       "Seen from the door side, the way it stands behind the display: sockets along the bottom edge, the left speaker's side on the right. Places are the board's own reference names. Pads are coloured by net. L1 to L10 are the leads that leave the board; tap one to see both of its ends.")

    # ------------------------------------------------------------------ touch board and mic strip
    t_items = R.board_items(m, "touch", {})
    for it in t_items:
        if it["id"] == "touch:J1":
            it["html"] += '<p class="fnote">Lead 5 lands here: VCC, GND, SDA, SCL as labelled, from J6 on the main board.</p>'
    touch_chips = [("Touch board", [(f"touch:{p['ref']}", p["ref"]) for p in m.boards["touch"]["parts"] if not p["ref"].startswith("E")])]
    touchview = R.viewer(m, "touch", R.small_board_svg(m, "touch", R.S_TOUCH, "TOUCH BOARD REV E", "back face, seen from the back · 90 × 44 mm · electrodes on the front, drawn faint", True),
                         touch_chips, t_items, '<div class="fh">Touch board</div><div class="fsub">rev E · AT42QT1070 at I²C 0x1B</div><p class="ffit">Every part is on the back. Tap one.</p>', legend=False)
    mic_items = R.board_items(m, "mic", {})
    for it in mic_items:
        if it["id"] == "mic:J1":
            it["html"] += '<p class="fnote">Leads 13 and 14 land here in cable order: 1 VDD, 2 GND, 3 CLK, 4 SEL, 5 DATA. Pad 1 is at the top in the drawing.</p>'
    mic_chips = [("Microphone strip", [(f"mic:{p['ref']}", p["ref"]) for p in m.boards["mic"]["parts"]])]
    micview = R.viewer(m, "mic", R.small_board_svg(m, "mic", R.S_MIC, "MICROPHONE STRIP REV 3", "back face, seen from the back · 28 × 6 mm · build two alike; the left one sits turned 180°", True),
                       mic_chips, mic_items, '<div class="fh">Microphone strip</div><div class="fsub">rev 3 · two alike · IM69D120 bottom port</div><p class="ffit">Every part is on the back. MK1 goes on last, lid up, port over the hole.</p>', legend=False)
    smalls = section("Touch board and microphone strips, to scale", touchview + micview,
                     "Both are drawn from the back, where their parts are. The touch board's four electrodes are copper on the front face, behind the shell's chin.")

    # ------------------------------------------------------------------ before you solder
    pre = """<ol class="steps">
<li><b>Power module PS1 first:</b> measure from its row of pins to its component side. About 5.0 mm: carry on. About 8.3 mm: stop, the board is wrong for it. Anything else: stop and look again.</li>
<li><b>Open moisture-sensitive bags on the day.</b> U100 TAS5756M, level 3: within 168 h. U1 TPS16630, level 2: 1 year. F4 and F5, level 2a: 4 weeks. On each mic strip D1–D3 ESD321, level 3: 168 h. All at 30 °C / 60 % or less; a part open longer is baked per J-STD-033 first.</li>
<li><b>Bare main board, meter on ohms:</b> """ + ", ".join(R.hc(x) for x in ("TP2", "F5 pad 2", "TP9", "TP16")) + " each read open to " + R.hc("TP7") + """ (ground). Bare touch board: VCC to GND on the HOST pads open. Bare strip: J1 pads 1–2 open, and the Ø0.8 port hole open against the light.</li>
<li><b>Paste:</b> Sn63/Pb37 no-clean (Chip Quik SMD291AXT4), check its date. Main board through its own stencil, outline to outline. Touch board and strips through their shared stencil, lying front-down; its patterns are already mirrored. The strip needs a flush jig; Kapton over its port hole on the front.</li>
<li><b>Leave empty:</b> """ + " ".join(R.hc(r) for r in dnp) + """ and the wire pads J7. Their pads still get paste.</li>
<li><b>Polarity:</b> D1 and D2 band (cathode) to pad 1. U1, U2, U100 pin 1 at the red dot on the drawing. C5, C6, C7: + lead in pad 1, the stripe on the can is −. F1, F2 and F3 share one body (5 A, 10 A, 1 A): read the marking. On the strips: D1–D3 pin 1 is GND; U1 pin 1 at the chamfer; MK1 last, lid up.</li>
<li><b>Hotplate:</b> one pass per board, parts side up (touch board and strips front-down on a clean sheet). Follow the paste's profile, about 240 s, peak 235 °C. No washing.</li>
<li><b>Through-hole parts by iron, low to high:</b> LK1 (1.0 mm tinned copper wire) · J2 (all 16 contacts and the 4 shell stakes) · J1, J8, J9, J5, J6 · J10, J11 · C7 · C5, C6 · PS1, pin 1 at the end marked "+Vo". Cut the leads of C5, C6, C7 and LK1 to 1.5 mm or less behind the board.</li>
<li><b>Pi signal wires on J3 and J4:</b> cut the contact off the board end, push the wire in from the back face (marked "PI 1-15" and "PI 35-40") and solder it on the door side. Seen from the back the board is mirrored.</li>
</ol>"""
    before = section("Before you solder", pre)

    # ------------------------------------------------------------------ leads table
    def dev_text(pid):
        dev = pid.split(":")[0]
        if dev == "main":
            return "main board " + pid[5:].split(".")[0]
        if dev == "pi":
            return "Pi header"
        return panel.MODULES[dev]["name"]
    lrows = []
    allrows = []
    for l in m.leads:
        fr = sorted({dev_text(a) for a, _ in l["wires"]})
        to = sorted({dev_text(b) for _, b in l["wires"]})
        if l.get("housing"):
            pins = panel.PI_HOUSINGS[l["housing"]]["pins"]
            to = [f"Pi header, housing {l['housing']} ({panel.PI_HOUSINGS[l['housing']]['shape']}, pins {pins[0]}–{pins[-1]})"]
        allrows.append((l["n"], [f"<b>{l['n']}</b>", esc(l["name"]), esc(", ".join(fr)), esc(", ".join(to)), f"{l['free']}", esc(l["stock"]), esc(l.get("mark") or "")]))
    for c in m.cables:
        allrows.append((c["n"], [f"<b>{c['n']}</b>", esc(c["name"]), esc(c["ends"][0]), esc(c["ends"][1]), "stock", esc(c["what"]), ""]))
    lrows = [r for _, r in sorted(allrows, key=lambda x: x[0])]
    leads = section("Leads", table(["#", "Lead", "From", "To", "Free mm", "Cut from", "Mark"], lrows),
                    "Free length is between the two fixed ends, without what each solder joint takes. Leads 1 to 5 are all black wire: mark pin 1 at both ends. Nothing is crimped and no wire is bought.")

    # ------------------------------------------------------------------ wiring by lead (pin to pin)
    wrows = []
    for l in m.leads:
        for a, b in l["wires"]:
            n = m.pin_info(a)[2] or m.pin_info(b)[2]
            col = l.get("colours", {}).get(a, "")
            wrows.append([f"L{l['n']}" + (f" {esc(l.get('wire_names', {}).get(a, ''))}" if l.get("wire_names") else ""), esc(R.pin_text(m, a)), esc(R.pin_text(m, b)), R.nt(n) if n else "", esc(col)])
        if l.get("bridge"):
            wrows.append([f"L{l['n']}", esc(R.pin_text(m, l["bridge"][0])), esc(R.pin_text(m, l["bridge"][1])), "solder bridge", ""])
    wiring = section("Every wire, end to end", table(["Lead", "From", "To", "Net", "Colour"], wrows),
                     "Generated from the same data as the drawings and checked by the build: no pin takes two wires, and every wire lands on the pin made for its net.")

    # ------------------------------------------------------------------ Pi header, modules
    pifig = section("Pi header as fitted", '<div class="diagram">' + R.pi_header_svg(m) + "</div>", "Seen from above with the header's edge row at the top. Filled pins are wired; the dashed boxes are the housings. Configuration that goes with it: <code>dtoverlay=rpi-digiampplus,auto_mute_amp</code>, <code>dtparam=uart0=on</code> (radar on <code>/dev/ttyAMA0</code>), <code>usb_max_current_enable=1</code>, EEPROM <code>PSU_MAX_CURRENT=5000</code>, I²C1 on.")
    modfig = section("Bought modules, as wired", '<div class="diagram">' + R.modules_svg(m) + "</div>", "Dashed outlines: no published outline in the records; their size comes from the model once it answers. Labels are the makers' own; wire by the label, not by position.")

    # ------------------------------------------------------------------ first power-up
    def where(ref):
        r, _, n = ref.partition(".")
        pad = m.pad("main", r, n) if n else m.parts[("main", r)]["pads"][0]
        x, y = pad["xy"]; b = m.boards["main"]["bbox"]
        return f"{x - b[0]:.1f} / {b[3] - y:.1f}"
    def tprow(refs, expect):
        refs = refs.split()
        probe = " ".join(R.hc(r.replace(".", " pad ")) for r in refs)
        wh = " · ".join(where(r) for r in refs)
        return [probe, f'<span class="via">{wh}</span>', expect]
    s1 = table(["Probe", "Where, mm from left / up", "Expect"], [
        tprow("TP1 TP2 TP8 F5.2", "about 20 V, all equal"),
        tprow("TP3", "0.279 V per amp of bus current: write it down"),
        tprow("TP6", "about 2.7 V"),
        tprow("TP9 TP10 TP11 TP12", "4.90 to 5.10 V, all about equal"),
        tprow("TP13", "write it down (5 V trim)"),
        tprow("TP16 TP19 TP4", "about 0 V: the 3.3 V regulator waits for the Pi's 3.3 V on wire A1"),
    ])
    s2 = table(["Probe", "Where, mm from left / up", "Expect"], [
        tprow("TP16", "3.21 to 3.34 V"),
        tprow("TP4 TP19", "about 3.3 V: no fault at the protection chip or the amplifier"),
        ["<code>vcgencmd get_throttled</code>", "", "<code>0x0</code>"],
        tprow("TP11", "with <code>vcgencmd pmic_read_adc EXT5V_V</code>, all cores busy, display on: 4.87 V or more. Lower: stop; R8 is found on the bench at TP13 first"),
    ])
    power = f"""<h3>Stage 1 · 20 V only</h3><p class="sect-note">Main board on the bench, the inlet board and its charger on J1, nothing else plugged. Meter ground on TP7.</p>{s1}
<h3>Stage 2 · Pi on</h3><p class="sect-note">Lead 15 from J2 to the Pi, the three signal housings, the display lead on pins 2-4-6.</p>{s2}
<h3>Stage 3 · configuration and buses</h3>
<ol class="steps"><li>Apply the Pi configuration (above, with the header), then plug the BME680 (J10), VEML6030 (J11), touch (J6) and radar (J5).</li>
<li>Switch the 20 V off and on with everything plugged: {R.hc("TP9")} rises to 4.90–5.10 V once, without the module restarting, and the Pi boots.</li>
<li><code>sudo i2cdetect -y 1</code> shows <code>1b</code> touch, <code>48</code> VEML6030, <code>UU</code> at <code>4c</code> amplifier (held by its driver), and the BME680 at <code>76</code> or <code>77</code>.</li>
<li>Radar: read {R.hc("TP12")} with the radar running and the Pi under full load; no invalid frame at 256000 8N1 on <code>/dev/ttyAMA0</code>.</li>
<li>Microphones: with both strips on the ReSpeaker, <code>arecord -l</code> lists it; then the audio bench test.</li></ol>"""
    firstpower = section("First power-up", power, "A meter is enough. Ground: TP7, TP15, TP17 or TP20. Where: mm from the main board's left edge / up from its bottom (socket) edge, seen from the door. The test pads are bare 1.5 mm pads on the door side.")

    # ------------------------------------------------------------------ connections by net
    npads = R.net_pads(main)
    groups = m.groups()
    off = defaultdict(list)
    for g in groups:
        mn = [x.split(":", 2)[2] for x in g if x.startswith("net:main:")]
        if not mn:
            continue
        for pid in g:
            if not pid.startswith(("net:", "main:")):
                off[mn[0]].append(R.pin_text(m, pid))
    nrows = []
    order = [n for c, *_rest, nets in panel.NET_CLASSES for n in nets]
    for net in sorted(npads, key=lambda n: (order.index(n) if n in order else 999, n)):
        if net_class(net) is None:
            continue
        pads = npads[net]
        if net == "GND":
            path = f"{len(pads)} pads on the main board, layer 2 a solid ground plane"
        else:
            path = " · ".join(f"{r}.{p}" for r, p in pads)
        o = sorted(set(off.get(net, [])))
        nrows.append([R.nt(net), esc(path), esc(" · ".join(o))])
    nets = section("Every connection, by net", table(["Net", "Main board pads", "Off the board"], nrows),
                   "The nets that carry power, buses and audio. The amplifier's and the protection chip's internal nets are in the part panels above.")

    # ------------------------------------------------------------------ parts lists
    def parts_rows(bkey):
        rows = []
        for p in m.boards[bkey]["parts"]:
            r = m.bom.get((bkey, p["ref"]))
            if p["ref"].startswith(("TP", "H", "E", "HS")) or p["ref"] in ("J3", "J4", "J7") or (bkey != "main" and p["ref"] == "J1"):
                continue
            pn = (r or {}).get("Maker's part number", "")
            rows.append([R.hc(p["ref"]), esc(p["value"]), esc((r or {}).get("Maker", "") + " " + pn), esc((r or {}).get("DigiKey number", "")),
                         "leave empty" if p["dnp"] else ("through-hole" if p["type"] == "through_hole" else "surface")])
        return rows
    plist = section("Parts", "<h3>Main board</h3>" + table(["Ref", "Value", "Part", "DigiKey", "Fit"], parts_rows("main"), "mono")
                    + "<h3>Touch board</h3>" + table(["Ref", "Value", "Part", "DigiKey", "Fit"], parts_rows("touch"), "mono")
                    + "<h3>Microphone strip (each)</h3>" + table(["Ref", "Value", "Part", "DigiKey", "Fit"], parts_rows("mic"), "mono"),
                    "From the board files and the parts list of 2026-11-17 (rev 3.3 changed no part). LK1 is a piece of 1.0 mm tinned copper wire, not from DigiKey.")

    # ------------------------------------------------------------------ open points and checks
    orows = [[f"<b>{esc(a)}</b>", esc(b), esc(c)] for a, b, c in panel.OPEN]
    openp = section("Not in the records", table(["What", "Missing", "How to find it"], orows), "Nothing on this page fills these in by guessing.")
    chk = section("Checks this page passed", '<ul class="checks">' + "".join(f"<li>{esc(p)}</li>" for p in passes) + "</ul>",
                  "The build stops on any short, split net, pin or hole used twice, wrong landing, or part under a screw head.")

    body = "\n".join([head, unit, mainview, smalls, before, leads, wiring, pifig, modfig, firstpower, nets, plist, openp, chk])
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>HA panel electronics</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=IBM+Plex+Sans+Condensed:wght@600;700&family=IBM+Plex+Sans:wght@400;600&display=swap" rel="stylesheet">
<style>{R.css()}</style></head><body><div class="wrap">
{body}
</div><script>{R.JS}</script></body></html>"""
    open(OUT, "w", encoding="utf8").write(page)
    print(f"wrote {OUT} ({len(page) // 1024} KiB); checks passed: {len(passes)}")


if __name__ == "__main__":
    build()
