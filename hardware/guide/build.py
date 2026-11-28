#!/usr/bin/env python3
"""Build the HA panel electronics page: model -> checks -> page. Fails (exit 1) on any check.

    python3 hardware/guide/build.py            # writes hardware/guide/ha-panel-electronics.html

Revision of 2026-11-28 (D572, D573): plain names, one colour per job, Do/Note/Tip steps, wiring drawn again.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))
sys.path.insert(0, os.path.join(HERE, "data"))

import checks  # noqa: E402
import page as PG  # noqa: E402
import panel  # noqa: E402
import render as R  # noqa: E402
import unitview as UV  # noqa: E402
import assembly as ASM  # noqa: E402
from model import Model, wire_words  # noqa: E402
from svgboard import esc  # noqa: E402

OUT = os.path.join(HERE, "ha-panel-electronics.html")
POSITIONS = os.path.join(HERE, "data", "positions.json")


def section(title, body, note=None, sid=None):
    n = f'<p class="sect-note">{note}</p>' if note else ""
    i = f' id="{sid}"' if sid else ""
    return f'<section{i}><h2>{esc(title)}</h2>{n}{body}</section>'


def table(head, rows, cls="", stack=True):
    th = "".join(f"<th>{esc(h)}</th>" for h in head)
    return f'<div class="tw"><table class="{"stack " if stack else ""}{cls}"><thead><tr>{th}</tr></thead><tbody>' + "".join(
        "<tr>" + "".join(f'<td data-l="{esc(head[i])}">{c}</td>' for i, c in enumerate(r)) + "</tr>" for r in rows) + "</tbody></table></div>"


def build():
    m = Model()
    fails, passes = checks.run(m)
    f2, p2, _used = checks.run_colours(m)
    fails += f2
    passes += p2
    f3 = ASM.check(m)
    fails += f3
    if not f3:
        passes.append("assembly: every fitted part placed once, empty places left empty, surface-mount before through-hole")
    if fails:
        print("BUILD FAILED: the checks found problems", file=sys.stderr)
        for f in fails:
            print("  -", f, file=sys.stderr)
        sys.exit(1)
    ends = R.lead_ends(m)
    main = m.boards["main"]
    dnp = [p["ref"] for p in main["parts"] if p["dnp"]]
    hc = R.hc

    def where(ref):
        r, _, n = ref.partition(".")
        pad = m.pad("main", r, n) if n else m.parts[("main", r)]["pads"][0]
        x, y = pad["xy"]
        b = main["bbox"]
        return f"{x - b[0]:.0f} mm from the left, {b[3] - y:.0f} mm up"

    # ------------------------------------------------------------------ header and warnings
    head = """<header>
<div class="eyebrow">HA Touch Panel · electronics</div>
<h1>HA panel electronics</h1>
<p class="dek">The boards, every lead and its colours, and first power.</p>
</header>
<div class="warn">
<div><b>The 20 V plug goes on first, on the middle socket</b><p>The three 2-way sockets look the same. On a speaker socket, 20 V can destroy the board.</p></div>
<div><b>Test-fit the power module before you solder anything</b><p>Its body must sit on the rectangle printed for it, clear of the two large capacitors and the coil. If not: stop.</p></div>
<div><b>Pi pins 2 and 4 are both 5 V</b><p>The display power lead's ground goes on pin 6. Check the row before you press the housing home.</p></div>
</div>"""

    # ------------------------------------------------------------------ the unit
    label_report = []
    unit = section("The unit", UV.unit_section(m, json.load(open(POSITIONS)), label_report), "Tap a lead to see it alone.")

    # ------------------------------------------------------------------ main board viewer (kept; plain names)
    items = R.board_items(m, "main", ends)
    for l in m.leads:
        if any(a.startswith("main:") for a, _ in l["wires"]):
            toks = [f"l:{l['n']}"] + [f"p:main:{a[5:].split('.')[0]}" for a, _ in l["wires"] if a.startswith("main:")]
            items.append({"id": f"L{l['n']}", "label": panel.LEAD_NAMES[l["n"]], "tokens": sorted(set(toks)), "own": [f"l:{l['n']}"], "html": R.lead_panel(m, l)})
    SHORT = {"J1": "20 V", "J9": "Right speaker", "J8": "Left speaker", "J6": "Touch", "J5": "Radar", "J10": "BME680", "J11": "Light sensor",
             "J2": "Pi power", "J3": "Pi pads", "J4": "Pi pads, I²S", "J7": "Echo tap"}
    chips = [(g, [(f"main:{r}", f"{SHORT[r]} · {r}" if r in SHORT else r) for r in refs]) for g, refs in R.GROUPS_MAIN]
    chips.append(("Leads", [(f"L{l['n']}", panel.LEAD_SHORT[l["n"]]) for l in m.leads if any(a.startswith("main:") for a, _ in l["wires"])]))
    default = ('<div class="fh">Main board</div><div class="fsub">rev 3.3 · from the door side</div>'
               '<p class="ffit">Tap a part or a lead. Its pads light up with every pad they join.</p>'
               '<p class="fnote">Dashed: left empty. Dashed circles: screw heads.</p>')
    mainview = section("Main board", '<div class="asm-jumps">' + ASM.jump("main") + "</div>" + R.viewer(m, "main", R.main_board_svg(m, ends), chips, items, default) + ASM.card(m, "main"),
                       "To scale. Pads in their job's colour. The assembly steps follow the drawing.")

    t_items = R.board_items(m, "touch", {})
    touch_chips = [("Touch board", [(f"touch:{p['ref']}", p["ref"]) for p in m.boards["touch"]["parts"] if not p["ref"].startswith("E")])]
    touchview = R.viewer(m, "touch", R.small_board_svg(m, "touch", R.S_TOUCH, "TOUCH BOARD REV E", "back face, from the back · 90 × 44 mm", True),
                         touch_chips, t_items, '<div class="fh">Touch board</div><div class="fsub">rev E</div><p class="ffit">Every part is on the back. The four touch pads are on the front.</p>', legend=False)
    mic_items = R.board_items(m, "mic", {})
    mic_chips = [("Microphone strip", [(f"mic:{p['ref']}", p["ref"]) for p in m.boards["mic"]["parts"]])]
    micview = R.viewer(m, "mic", R.small_board_svg(m, "mic", R.S_MIC, "MICROPHONE STRIP REV 3", "back face, from the back · 28 × 6 mm · two alike", True),
                       mic_chips, mic_items, '<div class="fh">Microphone strip</div><div class="fsub">rev 3 · two alike</div><p class="ffit">Every part is on the back. The microphone goes on last.</p>', legend=False)
    smalls = section("Touch board and microphone strips", '<div class="asm-jumps">' + ASM.jump("touch") + ASM.jump("mic") + "</div>" + touchview + ASM.card(m, "touch") + micview + ASM.card(m, "mic"),
                     "To scale, from the back. Each board's assembly steps follow its drawing.")

    # ------------------------------------------------------------------ colours (Daniel's OK, 2026-11-28 13:12)
    legend_rows, _crow = PG.colour_tables(m)
    colours = section("Wire colours", table(["Job", "Colour"], legend_rows),
                      "One colour for one job. A black wire that is not ground gets a mark in its job's colour at both ends. Each lead's wires are in its step, under Make the leads.", sid="colours")


    # ------------------------------------------------------------------ leads: drawing + one step per lead
    lead_steps = []
    for l in m.leads:
        st = panel.LEAD_STEPS.get(l["n"])
        if not st:
            continue
        rows = []
        head_a, head_b = PG.end_group(m, [a for a, _ in l["wires"]]), PG.end_group(m, [b for _, b in l["wires"]])
        for a, b in l["wires"]:
            s = m.wire_spec(l, a, b)
            rows.append([PG.end_short(m, a, head_a), PG.end_short(m, b, head_b), PG.jt(s["job"], esc(wire_words(s)))])
        if l.get("bridge"):
            rows.append(["", "the two ground pads", "a solder bridge"])
        nm = panel.LEAD_NAMES[l["n"]]
        lead_steps.append({"title": nm[0].upper() + nm[1:], "show": str(l["n"]), "do": st["do"],
                           "table": table([head_a or "From", head_b or "To", "Wire"], rows), "note": st["note"], "tip": st["tip"]})
    stage = PG.wiring_legend() + '<div class="wiring">' + PG.wiring_svg(m) + "</div>"
    leads = section("Make the leads", PG.stepper("leads", "Make the leads", lead_steps, stage=stage), sid="leads")

    # ------------------------------------------------------------------ Pi header (lookup)
    pifig = section("Pi header", '<div class="diagram">' + R.pi_header_svg(m) + "</div>",
                    "Configuration: <code>dtoverlay=rpi-digiampplus,auto_mute_amp</code> · <code>dtparam=uart0=on</code> · <code>usb_max_current_enable=1</code> · EEPROM <code>PSU_MAX_CURRENT=5000</code> · I²C on.")

    # ------------------------------------------------------------------ first power: steps with readings
    TP_NAMES = {"TP1": "20 V in, before the protection chip", "TP2": "20 V, after the protection chip", "TP3": "20 V current monitor",
                "TP4": "protection chip fault", "TP6": "protection chip shutdown", "TP8": "5 V module input", "TP9": "5 V module output",
                "TP10": "5 V after the Pi fuse", "TP11": "5 V at the Pi power socket", "TP12": "radar 5 V", "TP13": "5 V module trim",
                "TP16": "3.3 V", "TP19": "amplifier fault", "F5.2": "amplifier supply, F5's right-hand pad"}

    sm = ASM.sm

    def tpf(ref, expect):
        return {"id": ref.replace(".", "_"), "label": f"{TP_NAMES[ref]} <small>({ref.replace('.', ' pad ')}) · {where(ref)}</small>", "expect": expect}
    power_steps = [
        {"title": "20 V only",
         "do": ["Main board on the bench. Charger off.", "Plug only the 20 V lead, its inlet board on the charger.",
                f"Black probe on the ground test pad {sm('TP7')}.",
                "Charger on."],
         "note": "Each pad below: mm from the left edge and up from the socket edge, door side up. Any reading out of range: charger off, stop.",
         "fields": [tpf("TP1", "about 20 V"), tpf("TP2", "about 20 V"), tpf("TP8", "about 20 V"), tpf("F5.2", "about 20 V"),
                    tpf("TP6", "about 2.7 V"), tpf("TP9", "4.90–5.10 V"), tpf("TP10", "4.90–5.10 V"), tpf("TP11", "4.90–5.10 V"),
                    tpf("TP12", "4.90–5.10 V"), tpf("TP16", "about 0 V"), tpf("TP19", "about 0 V"), tpf("TP4", "about 0 V")]},
        {"title": "Pi on",
         "do": ["Charger off.", "Plug the three Pi housings, the display power lead and the display ribbon, then the Pi power cable.", "Charger on."],
         "note": "Pass: <code>vcgencmd get_throttled</code> reads <code>0x0</code>, and the readings below.",
         "fields": [tpf("TP16", "3.21–3.34 V"), tpf("TP4", "about 3.3 V"), tpf("TP19", "about 3.3 V")]},
        {"title": "5 V under load",
         "do": ["Display on; run <code>stress-ng --cpu 4 --timeout 120</code>.",
                f"While it runs, read <code>vcgencmd pmic_read_adc EXT5V_V</code> and the 5 V at the Pi power socket {sm('TP11')}."],
         "note": "Pass: both 4.87 V or more. Lower: stop; the 5 V needs trimming before use.", "fields": [tpf("TP11", "4.87 V or more")]},
        {"title": "Configure and plug the sensors",
         "do": ["Set in <code>config.txt</code>: <code>dtoverlay=rpi-digiampplus,auto_mute_amp</code>, <code>dtparam=uart0=on</code>, <code>usb_max_current_enable=1</code>; I²C on. EEPROM: <code>PSU_MAX_CURRENT=5000</code>.",
                "Shut the Pi down; charger off.", "Plug the BME680, light-sensor, touch and radar leads.", "Charger on."],
         "note": "Pass: the Pi boots first time. No boot, or a restart: stop.", "fields": [tpf("TP9", "4.90–5.10 V")]},
        {"title": "The buses",
         "do": ["Run <code>sudo i2cdetect -y 1</code>.",
                "Pi under full load, radar running: <code>stty -F /dev/ttyAMA0 256000 raw; timeout 10 xxd /dev/ttyAMA0</code>."],
         "note": "Pass: I²C shows <code>1b</code> touch, <code>48</code> light sensor, <code>UU</code> at <code>4c</code> amplifier, <code>76</code> or <code>77</code> BME680. "
                 "Radar: every frame starts <code>F4 F3 F2 F1</code> and ends <code>F8 F7 F6 F5</code>; none broken.",
         },
        {"title": "Microphones",
         "do": ["ReSpeaker's USB cable in the Pi.", "Run <code>arecord -l</code>."], "note": "Pass: the ReSpeaker is listed."},
    ]
    firstpower = section("First power", PG.stepper("power", "First power", power_steps), sid="power")

    # ------------------------------------------------------------------ fit in the unit (after first power)
    order = " → ".join(f'{panel.SOCKET_NAMES[r]} <small>({r})</small>' for r in panel.PLUG_ORDER)
    fit_steps = [
        {"title": "Speaker leads through the boxes", "show": "2",
         "do": ["Thread each speaker lead's contacts from inside its box out through the hole in its rear wall.",
                "Hot-melt round the lead in the hole, from outside.",
                "Push the contacts into a 2-way XH housing: + (the red-marked wire) in the place over the speaker socket's square pad. Tug each wire: it stays."],
         "note": "Beep each wire from the housing to its tab: + in the place over the square pad. Fail: re-seat. Keep the left lead clear of the ReSpeaker USB cable while the left box slides back."},
        {"title": "Radar lead on its holder", "show": "4",
         "do": ["Tie the radar lead through the slot in the holder's top plate, 10 mm behind the radar.", "Run it over the Pi to the board."]},
        {"title": "BME680 lead in its tray", "show": "6",
         "do": ["Thread the lead through the tray's slot.", "Wrap a plug of 2 mm foam round it in the slot."]},
        {"title": "Plug the leads", "show": "all",
         "do": [f"Plug in this order: {order}.", "Match each plug's mark to the mark beside its socket."],
         "note": "The 20 V plug goes first, on the middle 2-way socket. The Pi power cable goes last.",
         "tip": "Speaker plugs: long-nose pliers on the housing's top and bottom; press home with closed tweezers."},
        {"title": "Coil the microphone leads", "show": "13",
         "do": ["Once the module is home: coil each microphone lead's spare in three turns, about 19 mm across.", "Bind each coil with tape; lay it behind the screen plate."]},
        {"title": "Speakers",
         "do": ["Charger on; wait for the Pi to boot.", "Run <code>speaker-test -c 2 -t wav -l 1</code>."],
         "note": "Pass: “Front Left” from the left speaker, “Front Right” from the right."},
    ]
    fstage = PG.wiring_legend() + '<div class="wiring">' + PG.wiring_svg(m) + "</div>"
    fitunit = section("Fit in the unit", PG.stepper("fit", "Fit in the unit", fit_steps, stage=fstage), sid="fit")

    # ------------------------------------------------------------------ parts (lookup)
    def parts_rows(bkey):
        rows = []
        for p in m.boards[bkey]["parts"]:
            r = m.bom.get((bkey, p["ref"]))
            if p["ref"].startswith(("TP", "H", "E", "HS")) or p["ref"] in ("J3", "J4", "J7") or (bkey != "main" and p["ref"] == "J1"):
                continue
            pn = (r or {}).get("Maker's part number", "")
            rows.append([hc(p["ref"]), esc(p["value"]), esc((r or {}).get("Maker", "") + " " + pn), esc((r or {}).get("DigiKey number", "")),
                         "leave empty" if p["dnp"] else ("iron" if p["type"] == "through_hole" else "hotplate")])
        return rows
    head_p = ["On the board", "Value", "Part", "DigiKey", "Fit"]
    plist = section("Parts", "<h3>Main board</h3>" + table(head_p, parts_rows("main"), "mono", stack=False) + "<h3>Touch board</h3>" + table(head_p, parts_rows("touch"), "mono", stack=False)
                    + "<h3>Microphone strip, each</h3>" + table(head_p, parts_rows("mic"), "mono", stack=False), "LK1 is 1.0 mm tinned copper wire.")

    # ------------------------------------------------------------------ not in the records (D575)
    open_plain = [
        ("ReSpeaker microphone pads", "Where pad 1 is in each emptied footprint, and which footprint has left/right at ground.",
         "Meter on beep from the USB-C shell: pads 4 and 6 beep. ReSpeaker on USB, microphones off: pad 1 reads about 3.3 V. Pad 5 beeps to ground in one footprint (left strip) and reads 3.3 V in the other (right strip)."),
        ("Light sensor board", "Which board, and its pad order.", "Solder by its printed labels."),
        ("BME680 board pad order", "Not recorded.", "Solder by its printed labels. SDO and CS stay free."),
        ("Display power lead", "Which wires carry 5 V and ground; their colours; the lead's length.",
         "Plug it on the display. Beep from a display screw to each contact: that one is ground. Pi on: the one reading 5 V is 5 V."),
        ("Speaker + tab", "The driver's polarity mark.", "Read the + mark. None: touch a 1.5 V cell to the tabs; the tab on + when the cone moves out is +."),
        ("Microphone strip jig", "Not drawn.", "A pocket the strip's size (28 × 6, its depth plus the tape), or spare strips laid round it."),
    ]
    openp = section("Not in the records", table(["What", "Missing", "How to find it"], [[f"<b>{esc(a)}</b>", esc(b), esc(c)] for a, b, c in open_plain]))

    body = "\n".join([head, unit, mainview, smalls, colours, leads, pifig, firstpower, fitunit, plist, openp])
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>HA panel electronics</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=IBM+Plex+Sans+Condensed:wght@600;700&family=IBM+Plex+Sans:wght@400;600&display=swap" rel="stylesheet">
<style>{R.css()}{PG.css()}{UV.UNIT_CSS}{ASM.ASM_CSS}</style></head><body><div class="wrap">
{body}
</div><script>{R.JS}{PG.STEP_JS}{UV.UNIT_JS}{ASM.ASM_JS}</script></body></html>"""
    open(OUT, "w", encoding="utf8").write(page)
    print(f"wrote {OUT} ({len(page) // 1024} KiB); checks passed: {len(passes)}")
    for p in passes:
        print("  +", p)
    for r in label_report:
        print("  label:", r)


if __name__ == "__main__":
    build()
