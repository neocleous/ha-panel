"""Assembly steppers: one per board, in hotplate order. Every surface-mount part goes on in one paste-and-reflow pass,
then the through-hole parts by iron, low to high. Sources: the boards' READMEs (How to assemble) and the stencil README.

Each step lights the parts it places on a drawing of the board; parts placed earlier stay drawn, later ones are faint.
"""
from __future__ import annotations

import re

import page as PG
import render as R
from svgboard import esc

hc = R.hc


def sm(ref):
    return f'<small class="ref">({esc(ref)})</small>'


def nice(value, ref):
    """'0.22u 50V' -> '0.22 µF 50 V'; '22.1k 1%' -> '22.1 kΩ 1 %'; '10u' on an L -> '10 µH'."""
    v = value.replace(" DNP", "")
    unit = {"R": "Ω", "C": "F", "L": "H"}.get(ref[0], "")
    m = re.match(r"^(\d+(?:\.\d+)?)([pnumkMR]?)(.*)$", v)
    if not m or not unit:
        return v
    num, mult, rest = m.groups()
    mult = {"u": "µ", "R": ""}.get(mult, mult)
    rest = rest.strip().replace("V", " V").replace("%", " %").strip()
    return f"{num} {mult}{unit}" + (f", {rest}" if rest else "")


def line(model, board, refs, extra=""):
    p = model.parts[(board, refs[0])]
    return f"{esc(nice(p['value'], refs[0]))}{extra}: " + " ".join(hc(r) for r in refs)


def group(model, board, refs):
    """Lines of 'value: refs', one per value, in the order the values first appear."""
    by, order = {}, []
    for r in refs:
        v = model.parts[(board, r)]["value"]
        if v not in by:
            by[v] = []
            order.append(v)
        by[v].append(r)
    return [line(model, board, sorted(by[v], key=lambda x: (len(x), x))) for v in order]


def board_svg(model, bkey):
    if bkey == "main":
        s = R.small_board_svg(model, "main", R.S_MAIN, "MAIN BOARD REV 3.3", "door side, parts up · 87.0 × 57.9 mm", False)
    elif bkey == "touch":
        s = R.small_board_svg(model, "touch", R.S_TOUCH, "TOUCH BOARD REV E", "back face up · 90 × 44 mm", True)
    else:
        s = R.small_board_svg(model, "mic", R.S_MIC, "MICROPHONE STRIP REV 3", "back face up · 28 × 6 mm", True)
    # Red rings on pin 1 of every part that has a way round (chips, diodes, the round capacitors, the power module).
    from svgboard import View
    scale = {"main": R.S_MAIN, "touch": R.S_TOUCH, "mic": R.S_MIC}[bkey]
    v = View(model.boards[bkey], scale, 40, 70, mirror=(bkey != "main"))
    rings = []
    for ref in POLAR[bkey]:
        pad = next(p for p in model.parts[(bkey, ref)]["pads"] if str(p["num"]) == "1")
        x, y = v.xy(pad["xy"])
        r = max(pad["size"]) * scale / 2 + 3.5
        rings.append(f'<circle class="p1ring" data-k="p:{bkey}:{ref}" cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"/>')
    s = s.replace("</svg>", "".join(rings) + "</svg>")
    # What each part's call-out says: its value, or a plain name where a value would not help.
    import json
    names = {}
    for p in model.boards[bkey]["parts"]:
        r = p["ref"]
        v = NAMES.get((bkey, r)) or NAMES.get(r)
        if v is None:
            v = nice(str(p["value"] or ""), r).split(",")[0]
            if bkey == "main" and r in ("C103",):
                v += ", 50 V"
            if bkey == "main" and r in ("C105", "C112", "C118", "C119", "C120"):
                v += ", 25 V"
        names[r] = v
    s = s.replace('<svg class="wd bd"', f"<svg data-names='{esc(json.dumps(names, ensure_ascii=False))}' class=\"wd bd asm\"", 1)
    return s


NAMES = {("main", "U100"): "amplifier", ("main", "U1"): "protection chip", ("main", "U2"): "3.3 V regulator",
         ("main", "D1"): "20 V surge diode", ("main", "D2"): "5 V surge diode", ("main", "F1"): "5 A fuse", ("main", "F2"): "10 A fuse",
         ("main", "F3"): "1 A fuse", ("main", "F4"): "0.2 A resettable", ("main", "F5"): "2.6 A resettable", ("main", "L1"): "15 µH",
         ("main", "PS1"): "5 V module", ("main", "LK1"): "wire link", ("main", "J1"): "20 V socket", ("main", "J2"): "Pi power socket",
         ("main", "J5"): "radar socket", ("main", "J6"): "touch socket", ("main", "J8"): "left speaker", ("main", "J9"): "right speaker",
         ("main", "J10"): "BME680 header", ("main", "J11"): "light-sensor header", ("main", "J7"): "stays empty",
         ("main", "TP7"): "ground", ("main", "TP2"): "20 V", ("main", "TP9"): "5 V", ("main", "TP16"): "3.3 V",
         ("touch", "U1"): "touch chip", ("mic", "U1"): "logic chip", ("mic", "MK1"): "microphone",
         ("mic", "D1"): "protection diode", ("mic", "D2"): "protection diode", ("mic", "D3"): "protection diode"}


POLAR = {"main": ["U100", "U1", "U2", "D1", "D2", "C5", "C6", "C7", "PS1"], "touch": ["U1"], "mic": ["U1", "D1", "D2", "D3"]}


def _stamp(steps):
    """Give each step the parts it places (cur) and the parts already placed (done)."""
    done = []
    for st in steps:
        cur = st.pop("parts", [])
        look = st.pop("look", [])
        st["data"] = {"cur": " ".join(cur), "done": " ".join(done), "look": " ".join(look)}
        done = done + cur
    return steps


def refs(*rs):
    return " ".join(hc(r) for r in rs)


SHORTS = (f"Meter on ohms, black probe on the ground test pad {sm('TP7')}. Red probe in turn on 20 V in {sm('TP1')}, "
          f"20 V {sm('TP2')}, 5 V {sm('TP9')}, 3.3 V {sm('TP16')} and the right-hand pad of the amplifier's fuse {sm('F5 pad 2')}.")
SHORTS_NOTE = "Pass: each reads open, or climbs toward open as the capacitors charge. Fail: a steady few ohms or less: find the short before going on."


def main_steps(model):
    r0603 = ["R1", "R2", "R3", "R4", "R5", "R10", "R11", "R6", "R13", "R17", "R18", "R100", "R102", "R103", "R104", "R105",
             "R101", "R19", "R7", "R14", "R15", "R16", "R26"]
    c0603 = ["C2", "C4", "C9", "C100", "C121", "C3", "C104", "C108", "C111", "C115", "C103", "C105", "C112", "C118", "C119",
             "C120", "C106", "C107", "C113", "C114"]
    s0805 = ["R12", "C1", "C10", "C109", "C110", "C116", "C117", "C12", "C101", "C102", "C122", "C123"]
    steps = [
        {"title": "Test-fit the 5 V power module",
         "do": [f"Push the 5 V power module {sm('PS1')} into its 13 holes, pin 1 at the end marked “+Vo”. Don't solder.",
                "Hold it upright and look straight down."],
         "note": "Pass: the body stays inside its printed rectangle, clear of the outlines of the two large round capacitors and the coil. "
                 "Fail: stop; don't build this board.",
         "look": ["PS1", "C5", "C6", "L1"]},
        {"title": "Check the bare board for shorts",
         "do": [f"Meter on ohms, black probe on the ground test pad {sm('TP7')}.",
                f"Red probe in turn on 20 V {sm('TP2')}, 5 V {sm('TP9')}, 3.3 V {sm('TP16')} and the right-hand pad of the amplifier's fuse {sm('F5 pad 2')}."],
         "note": "Pass: each reads open. Fail: stop; the board is faulty.",
         "look": ["TP7", "TP2", "TP9", "TP16", "F5"]},
        {"title": "Paste the board",
         "do": ["Line the main board's stencil up on the pads; tape it down along one edge.",
                "Paste with one firm pass of the squeegee. Lift the stencil straight up."],
         "note": "Paste on every surface-mount pad, the empty places too; none on the test pads or the through-holes.",
         "tip": "Smeared or thin under the amplifier: wipe the board with IPA on a lint-free wipe, let it dry, paste again."},
        {"title": "Place the three chips",
         "do": [f"Place the amplifier chip {sm('U100')} and the 20 V protection chip {sm('U1')}: the dot at the red ring.",
                f"Place the 3.3 V regulator {sm('U2')}: three legs on the three-pad side; it fits one way."],
         "tip": "Set each chip down square in one go; nudge it on its pads, don't drag it through the paste.",
         "parts": ["U100", "U1", "U2"]},
        {"title": "Place the diodes",
         "do": [f"Place the 20 V surge diode {sm('D1')} and the 5 V surge diode {sm('D2')}, each straight from its own tape: they look alike.",
                "Turn each so the band is at the red ring."],
         "parts": ["D1", "D2"]},
        {"title": "Place the small resistors (0603), one value at a time",
         "do": [
                f"412 kΩ: {refs('R1')}", f"9.09 kΩ: {refs('R2')}", f"22.1 kΩ: {refs('R3')}", f"5.49 kΩ: {refs('R4')}",
                f"10 kΩ: {refs('R5', 'R10', 'R11')}", f"100 kΩ: {refs('R6', 'R13', 'R17', 'R18', 'R100', 'R102', 'R103', 'R104', 'R105')}",
                f"150 kΩ: {refs('R101')}", f"4.7 kΩ: {refs('R19')}", f"0 Ω: {refs('R7', 'R14', 'R15', 'R16', 'R26')}",
                f"Leave empty: {refs('R20', 'R21', 'R22', 'R23', 'R24', 'R25', 'R27')}"],
         "tip": "Straight from its tape; close the tape before the next.",
         "parts": r0603},
        {"title": "Place the small capacitors (0603), one value at a time",
         "do": [
                f"100 nF: {refs('C2', 'C4', 'C9', 'C100', 'C121')}", f"47 nF: {refs('C3')}", f"0.22 µF: {refs('C104', 'C108', 'C111', 'C115')}",
                f"1 µF, 50 V: {refs('C103')}", f"1 µF, 25 V: {refs('C105', 'C112', 'C118', 'C119', 'C120')}",
                f"2.2 µF: {refs('C106', 'C107', 'C113', 'C114')}"],
         "tip": "Capacitors carry no marking: straight from the tape, close it before the next.",
         "parts": c0603},
        {"title": "Place the 0805 parts, one value at a time",
         "do": [
                f"2.2 Ω: {refs('R12')}", f"1 µF: {refs('C1', 'C10')}", f"0.68 µF: {refs('C109', 'C110', 'C116', 'C117')}",
                f"4.7 µF: {refs('C12', 'C101', 'C102', 'C122', 'C123')}", f"Leave empty: {refs('R8', 'R9')}"],
         "parts": s0805},
        {"title": "Place the fuses and 1206 capacitors",
         "do": [f"Place 10 µF (1206): {refs('C8', 'C11')}",
                f"Place the resettable fuses: 0.2 A {sm('F4')}, the small one; 2.6 A {sm('F5')}, the large one.",
                f"Place the fuses: 5 A {sm('F1')}, 10 A {sm('F2')}, 1 A {sm('F3')}."],
         "note": "F1, F2 and F3 look alike: place each straight from its own tape.",
         "parts": ["C8", "C11", "F4", "F5", "F1", "F2", "F3"]},
        {"title": "Place the coils",
         "do": [f"Place 10 µH: {refs('L100', 'L101', 'L102', 'L103')}", f"Place the large 15 µH coil {sm('L1')} last."],
         "parts": ["L100", "L101", "L102", "L103", "L1"]},
        {"title": "Check before heating",
         "do": ["Compare the board with the drawing: every pasted place has its part, the nine empty places stay empty.",
                "Check each part sits square on its pads; chips and diodes match the red rings."],
         "tip": "A photo now makes the inspection after the hotplate quicker."},
        {"title": "Reflow on the hotplate",
         "do": ["Lay the board on the hotplate, door side up.",
                "Run the paste's profile: up to 150 °C, on through 183 °C, peak 235 °C, about 240 s in all.",
                "Let it cool where it lies until the solder has set."],
         "note": "One pass only."},
        {"title": "Inspect and touch up",
         "do": [f"Under magnification, check every pin of the amplifier and protection chips {sm('U100, U1')} for bridges and lifted pins.",
                "Check every other joint."],
         "tip": "A bridge: flux on it, then a clean iron tip along the pins, or wick. Leave the flux residue."},
        {"title": "Check the supplies for shorts", "do": [SHORTS], "note": SHORTS_NOTE},
        {"title": "Fit the wire link",
         "do": [f"Fit the wire link {sm('LK1')}: 1.0 mm tinned copper wire, in from the door side, soldered on the back. Every through-hole part goes in the same way."],
         "tip": "Solder one end, check it lies flat, then the other.",
         "parts": ["LK1"]},
        {"title": "Fit the Pi power socket",
         "do": [f"Fit the Pi power socket {sm('J2')} flat on the board.", "Solder all 16 contacts and the 4 shell stakes."],
         "tip": "Fine tip; fill each hole: the pins barely come through.",
         "parts": ["J2"]},
        {"title": "Fit the plug sockets",
         "do": [f"Fit the 2-way sockets: 20 V {sm('J1')} in the middle, left speaker {sm('J8')}, right speaker {sm('J9')}.",
                f"Fit the 4-way sockets: radar {sm('J5')}, touch {sm('J6')}.",
                "Each flat on the board, its outline on the printed one.",
                f"With a fine marker, beside each socket: 20 V {sm('J1')} a red dot; radar {sm('J5')} R; touch {sm('J6')} T."],
         "tip": "Solder one pin, check the socket sits flat, re-melt if not, then the rest.",
         "parts": ["J1", "J8", "J9", "J5", "J6"]},
        {"title": "Fit the sensor headers",
         "do": [f"Before fitting, mark beside each header's square pad (pin 1): BME680 {sm('J10')} B; light sensor {sm('J11')} L.",
                "Fit the two 1 × 4 pin headers, short pins through the board."],
         "parts": ["J10", "J11"]},
        {"title": "Fit the small capacitor",
         "do": [f"Fit 22 µF {sm('C7')}: the long (+) lead in the hole at the red ring. The stripe on the can marks −."],
         "parts": ["C7"]},
        {"title": "Fit the large capacitors",
         "do": [f"Fit 120 µF {sm('C5, C6')}: the long (+) lead in the hole at the red ring, seated on the board. The stripe marks −."],
         "parts": ["C5", "C6"]},
        {"title": "Fit the power module",
         "do": [f"Fit the 5 V power module {sm('PS1')}: pin 1 at the red ring, the end marked “+Vo”; upright and seated.",
                "Solder the two end pins, check it is upright, then the rest."],
         "parts": ["PS1"]},
        {"title": "Trim the leads",
         "do": [f"Cut the leads of the three round capacitors and the wire link {sm('C5, C6, C7, LK1')} as short as flush cutters go, 1.5 mm at most."],
         "note": f"The row of pads at the top left {sm('J7')} stays empty."},
        {"title": "Check the supplies again", "do": [SHORTS], "note": SHORTS_NOTE},
    ]
    return _stamp(steps)


def touch_steps(model):
    steps = [
        {"title": "Check the bare board", "do": ["Meter on ohms across the lead's pads marked VCC and GND."], "note": "Pass: open."},
        {"title": "Paste the back",
         "do": ["Lay the board face-down, the four touch pads underneath.",
                "Line up the touch board's openings on the second stencil; tape over the strip's openings.",
                "Paste with one pass of the squeegee; lift the stencil straight up."],
         "note": "The lead's four pads get no paste. Use the stencil as it comes; don't turn it over."},
        {"title": "Place the chip", "do": [f"Place the touch chip {sm('U1')}: the dot at the red ring."], "parts": ["U1"]},
        {"title": "Place the resistors and capacitors",
         "do": [f"Place 4.7 kΩ: {refs('R1', 'R2', 'R3', 'R4')}", f"Place 100 nF: {refs('C1')}", f"Place 10 µF: {refs('C2')}"],
         "parts": ["R1", "R2", "R3", "R4", "C1", "C2"]},
        {"title": "Reflow on the hotplate",
         "do": ["Lay the board face-down on a clean sheet on the hotplate.", "Run the same profile as the main board: peak 235 °C, about 240 s.",
                "Let it cool where it lies."]},
        {"title": "Inspect and check",
         "do": ["Under magnification, check the touch chip's pins for bridges.", "Meter on ohms across the lead's pads VCC and GND."],
         "note": "Pass: no bridges; VCC–GND not 0 Ω."},
    ]
    return _stamp(steps)


def mic_steps(model):
    steps = [
        {"title": "Check the bare strips",
         "do": ["Hold each strip back up, sound-hole end to the right: pad 1 is the top pad of the five.",
                "Hold each strip to the light.", "Meter on ohms across pads 1 and 2."],
         "note": "Pass: light through the sound hole; pads 1–2 open. Every step from here is for both strips."},
        {"title": "Tape the sound hole",
         "do": ["Put Kapton tape over the sound hole on the plain face, the one that meets the gasket."],
         "note": "Keep flux, paste, water, alcohol and compressed air away from the hole."},
        {"title": "Set the strip in a jig",
         "do": ["Lay the strip face-down in a pocket its size, or ringed by spare strips each on a layer of Kapton, its back level with them."]},
        {"title": "Paste the back",
         "do": ["Line up the strip's openings on the second stencil; tape over the touch board's.",
                "Paste with one pass of the squeegee; lift the stencil straight up."],
         "note": "No paste in the sound hole or inside the microphone's ring-shaped pad. Any there: wipe the strip clean and paste again."},
        {"title": "Place the logic chip",
         "do": [f"Place the logic chip {sm('U1')}: three legs on the three-pad side; it fits one way."], "parts": ["U1"]},
        {"title": "Place the diodes",
         "do": [f"Place the three protection diodes {sm('D1, D2, D3')}: the end with the dot or notch at the red ring, the closed end of the printed bracket."],
         "parts": ["D1", "D2", "D3"]},
        {"title": "Place the resistors and capacitors",
         "do": [f"Place 100 Ω: {refs('R1')}", f"Place 100 kΩ: {refs('R2')}", f"Place 33 Ω: {refs('R4')}", f"Place 0 Ω: {refs('R5')}",
                f"Place 10 µF: {refs('C1')}", f"Place 100 nF: {refs('C2', 'C3')}"],
         "parts": ["R1", "R2", "R4", "R5", "C1", "C2", "C3"]},
        {"title": "Place the microphone",
         "do": [f"Place the microphone {sm('MK1')} last: lid up, its sound port over the hole. Hold it by the lid only."],
         "parts": ["MK1"]},
        {"title": "Reflow on the hotplate",
         "do": ["Lay the strip face-down on the hotplate, as it lay for pasting.", "Run the same profile as the main board: peak 235 °C, about 240 s.",
                "Let it cool where it lies."],
         "note": "One pass. Rework only if you must: the microphone takes only two more heatings."},
        {"title": "Untape and check",
         "do": ["Once cool, peel off the Kapton; no washing.",
                "Meter on diode test: red on pad 2, black in turn on pads 1, 3 and 5; then reversed.",
                "Meter on ohms across pads 1 and 2.", f"Look: the 0 Ω link {sm('R5')} is fitted."],
         "note": "Pass: each conducts one way and is open the other (pad 1 climbs to open); pads 1–2 not 0 Ω."},
    ]
    return _stamp(steps)


ASM_CSS = """
svg.asm [data-k].todo{opacity:.18}
svg.asm .p1ring{fill:none;stroke:#e0392b;stroke-width:2.2} svg.asm .p1ring.todo{opacity:0} svg.asm .pad{fill:var(--pad)!important;stroke:var(--padring)!important}
svg.asm .cline{fill:none;stroke:var(--accent);stroke-width:1.4} svg.asm .clab{font:700 17px var(--f-body);fill:var(--ink);paint-order:stroke;stroke:var(--panel);stroke-width:4px} svg.asm .cref{fill:var(--accent)} svg.asm .cval{font-weight:500}
svg.asm .hl{fill:none;stroke:var(--accent);stroke-width:2.6;pointer-events:none}
svg.asm .t-ref.cur{fill:var(--accent)}
.asm-h{margin:26px 0 10px;font:700 22px var(--f-display)}
.asm-jump{display:inline-flex;align-items:center;min-height:44px;padding:0 18px;border-radius:999px;background:var(--ink);color:var(--panel);font:600 15px var(--f-body);text-decoration:none;margin:0 8px 12px 0}
.asm-stage{background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:6px;margin:0 0 14px;overflow-x:auto}
@media (max-width:700px){.asm-stage svg{min-width:900px}}
.asm-key{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;margin:4px 8px 6px;font:13px var(--f-body);color:var(--muted)}
.asm-key span{display:inline-block;width:18px;height:12px;border-radius:3px;margin-left:8px}
.asm-key .k-box{border:2.4px solid var(--accent)} .asm-key .k-solid{background:var(--ink)} .asm-key .k-faint{background:var(--ink);opacity:.18}
.ps1pic{display:block;max-width:440px;width:100%;height:auto;margin:6px 0 12px}
.asm-stage svg{display:block;width:100%;height:auto}
"""

ASM_JS = r"""
(() => {
document.querySelectorAll('[data-stepper]').forEach(card => {
  const svg = card.querySelector('svg.asm'); if (!svg) return;
  const steps = Array.from(card.querySelectorAll('.step'));
  const full = svg.getAttribute('viewBox');
  const els = Array.from(svg.querySelectorAll('[data-k]')).map(e => {
    const t = e.getAttribute('data-k').split(' ').find(x => x.indexOf('p:') === 0); return t ? [e, t.split(':')[2]] : null; }).filter(Boolean);
  function paint() {
    const st = steps.find(s => s.classList.contains('on')); if (!st) return;
    const cur = ((st.dataset.cur || '') + ' ' + (st.dataset.look || '')).split(' ').filter(Boolean), done = (st.dataset.done || '').split(' ').filter(Boolean);
    const any = cur.length > 0;
    els.forEach(([e, r]) => { const c = cur.indexOf(r) >= 0, d = done.indexOf(r) >= 0;
      e.classList.toggle('cur', c); e.classList.toggle('todo', !c && !d); });
    let hl = svg.querySelector('g.hls'); if (!hl) { hl = document.createElementNS('http://www.w3.org/2000/svg', 'g'); hl.setAttribute('class', 'hls'); svg.appendChild(hl); }
    hl.innerHTML = '';
    const boxes = {};
    els.forEach(([e, r]) => { if (cur.indexOf(r) < 0 || e.tagName === 'text') return; const b = e.getBBox(); const o = boxes[r];
      boxes[r] = o ? [Math.min(o[0], b.x), Math.min(o[1], b.y), Math.max(o[2], b.x + b.width), Math.max(o[3], b.y + b.height)] : [b.x, b.y, b.x + b.width, b.y + b.height]; });
    Object.values(boxes).forEach(b => { const r = document.createElementNS('http://www.w3.org/2000/svg', 'rect'), p = 4;
      r.setAttribute('x', b[0] - p); r.setAttribute('y', b[1] - p); r.setAttribute('width', b[2] - b[0] + 2 * p); r.setAttribute('height', b[3] - b[1] + 2 * p);
      r.setAttribute('rx', 3); r.setAttribute('class', 'hl'); hl.appendChild(r); });
    // Call-outs: each lit part gets its name in large type in a column beside the board, with a leader line.
    const names = JSON.parse(svg.getAttribute('data-names') || '{}');
    const pcb = svg.querySelector('path.pcb').getBBox();
    const mid = pcb.x + pcb.width / 2, FS = 17, GAP = 25;
    const cols = { L: [], R: [] };
    Object.entries(boxes).forEach(([r, b]) => { const cy = (b[1] + b[3]) / 2; cols[(b[0] + b[2]) / 2 < mid ? 'L' : 'R'].push({ r, b, cy }); });
    let lx0 = 1e9, ly0 = 1e9, lx1 = -1e9, ly1 = -1e9;
    ['L', 'R'].forEach(side => {
      const col = cols[side].sort((a, b) => a.cy - b.cy);
      col.forEach((it, i) => { it.y = Math.max(it.cy, i ? col[i - 1].y + GAP : -1e9); });
      const over = col.length ? col[col.length - 1].y - (pcb.y + pcb.height + 40) : 0;
      if (over > 0) col.forEach(it => { it.y -= over; });
      for (let i = col.length - 2; i >= 0; i--) col[i].y = Math.min(col[i].y, col[i + 1].y - GAP);
      const x = side === 'L' ? pcb.x - 26 : pcb.x + pcb.width + 26;
      col.forEach(it => {
        const ns = 'http://www.w3.org/2000/svg', g = document.createElementNS(ns, 'g');
        const ex = side === 'L' ? it.b[0] - 4 : it.b[2] + 4;
        const ln = document.createElementNS(ns, 'polyline');
        ln.setAttribute('points', `${ex},${it.cy} ${side === 'L' ? x + 8 : x - 8},${it.y} ${x},${it.y}`); ln.setAttribute('class', 'cline');
        const t = document.createElementNS(ns, 'text');
        t.setAttribute('x', side === 'L' ? x - 4 : x + 4); t.setAttribute('y', it.y + FS * 0.35); t.setAttribute('class', 'clab');
        t.setAttribute('text-anchor', side === 'L' ? 'end' : 'start');
        const a = document.createElementNS(ns, 'tspan'); a.textContent = it.r; a.setAttribute('class', 'cref');
        const v = document.createElementNS(ns, 'tspan'); v.textContent = names[it.r] ? '  ' + names[it.r] : ''; v.setAttribute('class', 'cval');
        if (side === 'L') { t.appendChild(v); t.insertBefore(a, v); } else { t.appendChild(a); t.appendChild(v); }
        g.appendChild(ln); g.appendChild(t); hl.appendChild(g);
        const bb = t.getBBox(); lx0 = Math.min(lx0, bb.x); ly0 = Math.min(ly0, bb.y); lx1 = Math.max(lx1, bb.x + bb.width); ly1 = Math.max(ly1, bb.y + bb.height);
      });
    });
    const f = full.split(' ').map(Number);
    const x0 = Math.min(f[0], lx0 - 8), y0 = Math.min(f[1], ly0 - 8), x1 = Math.max(f[0] + f[2], lx1 + 8), y1 = Math.max(f[1] + f[3], ly1 + 8);
    svg.setAttribute('viewBox', [x0, y0, x1 - x0, y1 - y0].map(n => n.toFixed(1)).join(' '));
  }
  const mo = new MutationObserver(paint); steps.forEach(s => mo.observe(s, { attributes: true, attributeFilter: ['class'] }));
  paint();
});
})();
"""


CARDS = {"main": ("asm-main", "Assemble the main board", main_steps),
         "touch": ("asm-touch", "Assemble the touch board", touch_steps),
         "mic": ("asm-mic", "Assemble the microphone strips", mic_steps)}


def card(model, bkey):
    sid, name, fn = CARDS[bkey]
    stage = (f'<div class="asm-stage">{board_svg(model, bkey)}'
             '<p class="asm-key"><span class="k-box"></span>this step <span class="k-solid"></span>already on the board <span class="k-faint"></span>not yet</p></div>')
    return f'<h3 class="asm-h" id="{sid}-h">{esc(name)}</h3>' + PG.stepper(sid, name.replace("Assemble the ", "").capitalize(), fn(model), stage)


def jump(bkey):
    sid, name, _fn = CARDS[bkey]
    return f'<a class="asm-jump" href="#{sid}-h">{esc(name)} — step by step ↓</a>'


def check(model):
    """Every fitted part of each board is placed in exactly one step; nothing empty is placed; surface-mount before through-hole."""
    fails = []
    for bkey, fn in (("main", main_steps), ("touch", touch_steps), ("mic", mic_steps)):
        placed = []
        seen_tht = False
        for st in fn(model):
            for r in st["data"]["cur"].split():
                p = model.parts.get((bkey, r))
                if p is None:
                    fails.append(f"{bkey}: {r} is not on the board")
                    continue
                if p["dnp"]:
                    fails.append(f"{bkey}: {r} is left empty but placed")
                if p["type"] == "through_hole":
                    seen_tht = True
                elif seen_tht:
                    fails.append(f"{bkey}: {r} (surface-mount) comes after a through-hole part")
                placed.append(r)
        dup = {r for r in placed if placed.count(r) > 1}
        if dup:
            fails.append(f"{bkey}: placed twice: {sorted(dup)}")
        skip = {"J3", "J4", "J7"} if bkey == "main" else {"J1"}
        need = {r for (b, r), p in model.parts.items() if b == bkey and p["type"] in ("smd", "through_hole") and not p["dnp"]
                and r not in skip and not r.startswith("E")}
        missing = need - set(placed)
        if missing:
            fails.append(f"{bkey}: never placed: {sorted(missing)}")
    return fails
