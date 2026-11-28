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
    return s.replace('<svg class="wd bd"', '<svg class="wd bd asm"', 1)


def _stamp(steps):
    """Give each step the parts it places (cur) and the parts already placed (done)."""
    done = []
    for st in steps:
        cur = st.pop("parts", [])
        st["data"] = {"cur": " ".join(cur), "done": " ".join(done)}
        done = done + cur
    return steps


def main_steps(model):
    smd = lambda *rs: list(rs)
    r0603 = ["R1", "R2", "R3", "R4", "R5", "R10", "R11", "R100", "R101", "R6", "R13", "R17", "R18", "R102", "R103", "R104",
             "R105", "R19", "R7", "R26", "R14", "R15", "R16"]
    c0603 = ["C2", "C4", "C9", "C100", "C121", "C3", "C104", "C108", "C111", "C115", "C103", "C105", "C112", "C118", "C119",
             "C120", "C106", "C107", "C113", "C114"]
    s0805 = ["R12", "C1", "C10", "C109", "C110", "C116", "C117", "C101", "C102", "C12", "C122", "C123"]
    steps = [
        {"title": "Measure the power module",
         "do": ["Put the power module (PS1) on the bench, pins down.", "Measure from its row of pins to its component side."],
         "note": "About 5.0 mm: carry on. About 8.3 mm: stop, the board is wrong for it. Anything else: stop.",
         "fields": [{"id": "ps1", "label": "Pins to component side", "expect": "about 5.0 mm"}]},
        {"title": "Check the bare board",
         "do": [f"Meter on ohms. From {hc('TP7')} (ground) to {hc('TP2')}, {hc('F5 pad 2')}, {hc('TP9')} and {hc('TP16')}."],
         "note": "Each reads open. Anything else: stop, the board is faulty."},
        {"title": "Open the bags on the day",
         "do": [f"Open the bags of the amplifier {hc('U100')}, the protection chip {hc('U1')} and the fuses {hc('F4')} {hc('F5')} today, not before."],
         "note": "Solder them within: U100 168 h; U1 a year; F4, F5 4 weeks; at 30 °C / 60 % or less. Older: bake them first (J-STD-033)."},
        {"title": "Paste the board",
         "do": ["Check the paste's date: Sn63/Pb37 no-clean, Chip Quik SMD291AXT4.",
                "Main board's own stencil, 0.12 mm, outline on outline. Tape it at one edge.",
                "One firm pass of the squeegee. Lift the stencil straight up."],
         "note": "Every pad but the test pads and the through-holes carries paste, the nine empty places too.",
         "tip": "Smeared or thin under the amplifier? Wipe the board clean with a dry cloth and paste again."},
        {"title": "Place the chips",
         "do": [f"{hc('U100')} amplifier, 48 pins; {hc('U1')} protection chip, 20 pins; {hc('U2')} 3.3 V regulator, 5 pins.",
                "Pin 1 at the red dot on the drawing."],
         "note": "Finest pitch first, while nothing is in the way of the tweezers.",
         "tip": "Set each chip down square in one go; nudge it on its pads, don't drag it through the paste.",
         "parts": smd("U100", "U1", "U2")},
        {"title": "Place the diodes",
         "do": [f"{hc('D1')} SMBJ22A; {hc('D2')} SMBJ6.0A-E.", "The band (cathode) to pad 1, the red dot."],
         "parts": smd("D1", "D2")},
        {"title": "Place the small resistors (0603)",
         "do": group(model, "main", r0603) + ["Leave empty: " + " ".join(hc(r) for r in ["R20", "R21", "R22", "R23", "R24", "R25", "R27"]) + "."],
         "tip": "One value at a time, straight from its tape, so no two values meet on the bench.",
         "parts": r0603},
        {"title": "Place the small capacitors (0603)",
         "do": group(model, "main", c0603),
         "note": "Capacitors carry no marking: keep each tape closed until its line.",
         "parts": c0603},
        {"title": "Place the 0805 parts",
         "do": group(model, "main", s0805) + [f"Leave empty: {hc('R8')} {hc('R9')}."],
         "parts": s0805},
        {"title": "Place the fuses and large capacitors",
         "do": [line(model, "main", ["C8", "C11"]), f"{hc('F4')} 0.2 A (1206); {hc('F5')} 2.6 A (2920).",
                f"{hc('F1')} 5 A, {hc('F2')} 10 A, {hc('F3')} 1 A."],
         "note": "F1, F2 and F3 look alike: read the marking on each before it goes down.",
         "parts": ["C8", "C11", "F4", "F5", "F1", "F2", "F3"]},
        {"title": "Place the inductors",
         "do": [line(model, "main", ["L100", "L101", "L102", "L103"]), f"{hc('L1')} 15 µH, last: the tallest part."],
         "parts": ["L100", "L101", "L102", "L103", "L1"]},
        {"title": "Check before heating",
         "do": ["Hold the board beside the drawing. Every pasted place has its part, but the nine left empty.",
                "Each part sits square on its pads. Chips: pin 1 at the dot."],
         "tip": "A photo now makes the inspection after the hotplate quicker."},
        {"title": "Hotplate",
         "do": ["Door side up; the back is bare, so the board lies flat.",
                "Follow the paste's profile: up to 150 °C, through 183 °C, peak 235 °C, about 240 s in all.",
                "Let it cool where it lies until the solder has set; then move it."],
         "note": "One pass. Don't touch or tap the board while the solder is liquid."},
        {"title": "Inspect and touch up",
         "do": [f"Under magnification: {hc('U100')} and {hc('U1')}, every pin, for bridges and lifted pins.", "Then every other joint."],
         "tip": "A bridge: flux on it, a clean iron tip along the pins, or wick. No washing: the paste is no-clean."},
        {"title": "Check the rails",
         "do": [f"Meter on ohms, from {hc('TP7')} to {hc('TP2')}, {hc('F5 pad 2')}, {hc('TP9')} and {hc('TP16')}."],
         "note": "None stays at 0 Ω. A reading that climbs while the capacitors charge is fine. 0 Ω: find the bridge before going on."},
        {"title": "Wire link",
         "do": [f"{hc('LK1')}: 1.0 mm tinned copper wire, from the door side. Solder on the back."],
         "note": "Through-hole parts from here on: in from the door side, soldered on the back, lowest first.",
         "tip": "Solder one end, check it lies flat, then the other.",
         "parts": ["LK1"]},
        {"title": "Pi power socket",
         "do": [f"{hc('J2')} USB-C socket, flat on the board.", "Solder all 16 contacts and the 4 shell stakes."],
         "note": "Its pin ends reach only 0.5 mm behind the board: work the joint from the back with a fine tip.",
         "parts": ["J2"]},
        {"title": "Plug sockets",
         "do": [f"2-way: {hc('J1')} 20 V, {hc('J8')} left speaker, {hc('J9')} right speaker.",
                f"4-way: {hc('J5')} radar, {hc('J6')} touch.",
                "Each flat and square on the outline drawn on the board.",
                f"With a fine marker: a mark beside {hc('J1')}, {hc('J5')} and {hc('J6')}."],
         "note": "J1 is the middle one of the three 2-way sockets.",
         "tip": "Solder one pin, check the socket sits flat, re-melt if not, then the rest.",
         "parts": ["J1", "J8", "J9", "J5", "J6"]},
        {"title": "Sensor headers",
         "do": [f"{hc('J10')} BME680, {hc('J11')} light sensor: 1 × 4 headers, short pins through the board.",
                f"A mark beside {hc('J10')} and {hc('J11')}: the headers have no key."],
         "parts": ["J10", "J11"]},
        {"title": "Small capacitor",
         "do": [f"{hc('C7')} 22 µF 35 V: + lead in pad 1, the red dot. The stripe on the can is −."],
         "parts": ["C7"]},
        {"title": "Large capacitors",
         "do": [f"{hc('C5')} {hc('C6')} 120 µF 63 V: + lead in pad 1. The stripe is −.", "Seated on the board."],
         "parts": ["C5", "C6"]},
        {"title": "Power module",
         "do": [f"{hc('PS1')}: pin 1 at the end the board marks “+Vo”.", "Seated flat; solder the two end pins, check, then the rest."],
         "parts": ["PS1"]},
        {"title": "Trim and finish",
         "do": [f"Cut the leads of {hc('C5')} {hc('C6')} {hc('C7')} and {hc('LK1')} to 1.5 mm or less behind the board.",
                f"{hc('J7')} stays empty. The Pi wires ({hc('J3')}, {hc('J4')}) go on under Leads."],
         "note": "Behind the board lie the ReSpeaker and the display lead: no pin end may stand out more than 4.0 mm."},
    ]
    return _stamp(steps)


def touch_steps(model):
    steps = [
        {"title": "Check the bare board", "do": ["Meter on ohms: VCC to GND on the HOST pads."], "note": "Open."},
        {"title": "Paste the back",
         "do": ["Board front-down: the four touch pads underneath, the back up.",
                "Shared stencil, the touch board's pattern. Tape over the strip's pattern.",
                "One pass; lift straight up."],
         "note": "The HOST pads get no paste.", "tip": "The pattern is already mirrored."},
        {"title": "Place the chip",
         "do": [f"{hc('U1')} AT42QT1070, 14 pins: pin 1 at the chamfered corner, the red dot."],
         "parts": ["U1"]},
        {"title": "Place the resistors and capacitors",
         "do": [line(model, "touch", ["R1", "R2", "R3", "R4"]), line(model, "touch", ["C1"]), line(model, "touch", ["C2"])],
         "parts": ["R1", "R2", "R3", "R4", "C1", "C2"]},
        {"title": "Hotplate",
         "do": ["Front down on a clean sheet; the front has no parts.", "The main board's profile: peak 235 °C, about 240 s.",
                "Let it cool where it lies."]},
        {"title": "Inspect and check",
         "do": [f"Under magnification: {hc('U1')}'s pins for bridges.", "Meter: VCC to GND on the HOST pads."],
         "note": "Not 0 Ω. The touch lead goes on under Leads."},
    ]
    return _stamp(steps)


def mic_steps(model):
    steps = [
        {"title": "Check the bare strips",
         "do": ["Both strips: hold each to the light. The 0.8 mm sound hole is open.", "Meter: pads 1 to 2 on J1 read open."],
         "note": "Do every step on both strips: they are alike."},
        {"title": "Open the diode bag on the day",
         "do": [f"Open the bag of {hc('D1')}–{hc('D3')} (ESD321) today, not before."],
         "note": "Solder within 168 h at 30 °C / 60 % or less. Older: bake first."},
        {"title": "Tape the sound hole",
         "do": ["Kapton over the sound hole on the front (gasket side)."],
         "note": "Flux, paste, water, IPA and air must not reach the hole."},
        {"title": "Set the strip in a jig",
         "do": ["Strip front-down, held flush with the surface round it: a 0.8 mm pocket, or spare strips laid round it."],
         "note": "No jig is drawn yet.", "tip": "Flush matters: the stencil must lie flat over the strip."},
        {"title": "Paste the back",
         "do": ["Shared stencil, the strip's pattern. Tape over the touch board's pattern.", "One pass; lift straight up."],
         "note": "No paste in the sound hole or inside the microphone's ring. Any there: wipe the strip and paste again."},
        {"title": "Place the logic chip",
         "do": [f"{hc('U1')} SN74LVC1G17, 5 pins: pin 1 at the chamfer, the red dot."], "parts": ["U1"]},
        {"title": "Place the diodes",
         "do": [f"{hc('D1')} {hc('D2')} {hc('D3')}: pin 1 (dot or notch) is ground, at the closed end of the bracket."],
         "parts": ["D1", "D2", "D3"]},
        {"title": "Place the resistors and capacitors",
         "do": [line(model, "mic", ["R1"]), line(model, "mic", ["R2"]), line(model, "mic", ["R4"]),
                line(model, "mic", ["R5"], " (required)"), line(model, "mic", ["C1"]), line(model, "mic", ["C2", "C3"])],
         "parts": ["R1", "R2", "R4", "R5", "C1", "C2", "C3"]},
        {"title": "Place the microphone",
         "do": [f"{hc('MK1')} IM69D120, last: lid up, its port over the hole.", "Hold it by the lid only."],
         "parts": ["MK1"]},
        {"title": "Hotplate",
         "do": ["Front down, in the jig or on a clean sheet. The main board's profile: peak 235 °C, about 240 s.",
                "Let it cool where it lies."],
         "note": "One pass. The microphone takes 3 reflows in all, and a rework counts as one."},
        {"title": "Untape and check",
         "do": ["Cool: take the Kapton off. Leave the residue; no washing.",
                f"Diode mode on {hc('D1')}–{hc('D3')}: red on ground, black on the signal pad: conducts; reversed: open.",
                f"VDD to GND (J1 pads 1, 2): not 0 Ω. {hc('R5')} is there."],
         "note": "The microphone leads go on under Leads."},
    ]
    return _stamp(steps)


ASM_CSS = """
svg.asm [data-k].todo{opacity:.18}
svg.asm .hl{fill:none;stroke:var(--accent);stroke-width:2.6;pointer-events:none}
svg.asm .t-ref.cur{fill:var(--accent)}
.asm-h{margin:26px 0 10px;font:700 22px var(--f-display)}
.asm-jump{display:inline-flex;align-items:center;min-height:44px;padding:0 18px;border-radius:999px;background:var(--ink);color:var(--panel);font:600 15px var(--f-body);text-decoration:none;margin:0 8px 12px 0}
.asm-stage{background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:6px;margin:0 0 14px}
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
    const cur = (st.dataset.cur || '').split(' ').filter(Boolean), done = (st.dataset.done || '').split(' ').filter(Boolean);
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
    svg.setAttribute('viewBox', full);
    if (any && svg.clientWidth < 700) {
      let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
      els.forEach(([e, r]) => { if (cur.indexOf(r) < 0 || !e.getBBox) return; const b = e.getBBox();
        x0 = Math.min(x0, b.x); y0 = Math.min(y0, b.y); x1 = Math.max(x1, b.x + b.width); y1 = Math.max(y1, b.y + b.height); });
      const f = full.split(' ').map(Number), w = Math.max(x1 - x0 + 80, f[2] * 0.45), h = Math.max(y1 - y0 + 80, f[3] * 0.45);
      const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
      svg.setAttribute('viewBox', [cx - w / 2, cy - h / 2, w, h].map(n => n.toFixed(1)).join(' '));
    }
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
    stage = f'<div class="asm-stage">{board_svg(model, bkey)}</div>'
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
