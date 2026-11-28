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
    return s.replace('<svg class="wd bd"', '<svg class="wd bd asm"', 1)


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


# End-on view of the open-frame module standing on its pins (Mean Well side view: parts face to module board 9,
# pins 4 from the board on the parts side, so 5.0 from the parts face; rev 3.2 holes matched about 8.3).
PS1_PIC = (
    '<svg class="ps1pic" viewBox="0 0 440 250" role="img" aria-label="The power module seen from one end, standing on its pins">'
    '<text class="t-ws" x="12" y="18">SEEN FROM ONE END OF THE PIN ROW</text>'
    # rule against the parts
    '<rect x="96" y="40" width="8" height="150" fill="var(--muted)"/>'
    '<text class="t-ws" x="88" y="36" text-anchor="end">steel rule</text>'
    # parts
    '<rect x="104" y="62" width="62" height="34" rx="3" fill="var(--body)" stroke="var(--ink)"/>'
    '<rect x="104" y="112" width="40" height="30" rx="3" fill="var(--body)" stroke="var(--ink)"/>'
    '<rect x="104" y="152" width="70" height="26" rx="3" fill="var(--body)" stroke="var(--ink)"/>'
    '<text class="t-ws" x="112" y="84">parts</text>'
    # module board
    '<rect x="266" y="44" width="14" height="148" fill="var(--pcb)" stroke="var(--ink)"/>'
    '<text class="t-ws" x="290" y="70">the module\'s own board</text>'
    # pins
    '<path d="M222,192 L222,234" stroke="var(--ink)" stroke-width="7"/>'
    '<text class="t-ws" x="232" y="230">pins</text>'
    # dimension
    '<path d="M104,214 L222,214" stroke="var(--accent)" stroke-width="2"/>'
    '<path d="M104,206 L104,222 M222,206 L222,222" stroke="var(--accent)" stroke-width="2"/>'
    '<text x="163" y="246" text-anchor="middle" style="font:700 14px var(--f-body);fill:var(--accent)">about 5.0 mm: carry on</text>'
    '</svg>')


def main_steps(model):
    smd = lambda *rs: list(rs)
    r0603 = ["R1", "R2", "R3", "R4", "R5", "R10", "R11", "R100", "R101", "R6", "R13", "R17", "R18", "R102", "R103", "R104",
             "R105", "R19", "R7", "R26", "R14", "R15", "R16"]
    c0603 = ["C2", "C4", "C9", "C100", "C121", "C3", "C104", "C108", "C111", "C115", "C103", "C105", "C112", "C118", "C119",
             "C120", "C106", "C107", "C113", "C114"]
    s0805 = ["R12", "C1", "C10", "C109", "C110", "C116", "C117", "C101", "C102", "C12", "C122", "C123"]
    steps = [
        {"title": "Check the 5 V power module",
         "picture": PS1_PIC,
         "do": ["The 5 V power module <small class=\"ref\">(PS1)</small> is the small board, 51 × 28 mm, with 13 pins along one long edge and its parts on one face. Stand it on its pins and look along the row of pins from one end.",
                "Lay a steel rule flat across the tops of the parts.",
                "With calipers, measure from the rule to the middle of the pins."],
         "note": "About 5.0 mm: carry on. About 8.3 mm: stop, the holes on this board don't match it. Anything else: stop.",
         "fields": [{"id": "ps1", "label": "Rule to pins", "expect": "about 5.0 mm"}],
         "look": ["PS1"]},
        {"title": "Check the bare board",
         "do": ["Meter on ohms. Black probe on the ground test pad <small>(TP7)</small>.",
                "Red probe in turn on the test pads for 20 V <small>(TP2)</small>, 5 V <small>(TP9)</small> and 3.3 V <small>(TP16)</small>, and on the right-hand pad of the amplifier's fuse <small>(F5 pad 2)</small>."],
         "note": "Each reads open. Anything else: stop, the board is faulty.",
         "look": ["TP7", "TP2", "TP9", "TP16", "F5"]},
        {"title": "Moisture-sensitive parts",
         "do": ["Keep these sealed until the day you solder: the amplifier chip <small>(U100)</small>, the protection chip <small>(U1)</small> and the two resettable fuses <small>(F4, F5)</small>."],
         "note": "Once open, solder within: amplifier 168 h; protection chip a year; fuses 4 weeks. Open longer: bake as the bag's label says.",
         "look": ["U100", "U1", "F4", "F5"]},
        {"title": "Paste the board",
         "do": ["Paste: Chip Quik SMD291AXT4, inside its date.",
                "The main board's own stencil: line its openings up on the pads and tape it down along one edge.",
                "One firm pass of the squeegee. Lift the stencil straight up."],
         "note": "Paste goes on every surface-mount pad, the nine places left empty too; none on the test pads or the through-holes.",
         "tip": "Smeared or thin under the amplifier? Wipe the board clean with a dry cloth and paste again."},
        {"title": "Place the three chips",
         "do": [f"The amplifier chip {sm('U100')}, 48 pins.", f"The 20 V protection chip {sm('U1')}, 20 pins.", f"The 3.3 V regulator {sm('U2')}, 5 pins.",
                "Pin 1 (the dot or bevel on the chip) at the red ring on the drawing."],
         "note": "Finest pitch first, while nothing is in the way of the tweezers.",
         "tip": "Set each chip down square in one go; nudge it on its pads, don't drag it through the paste.",
         "parts": smd("U100", "U1", "U2")},
        {"title": "Place the diodes",
         "do": [f"The 20 V surge diode {sm('D1')}, marked SMBJ22A; the 5 V surge diode {sm('D2')}, SMBJ6.0A-E.", "The band on the body at the red ring on the drawing."],
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
         "do": [line(model, "main", ["C8", "C11"]), f"Resettable fuses: 0.2 A {sm('F4')}, the small one; 2.6 A {sm('F5')}, the large one.",
                f"Fuses: 5 A {sm('F1')}, 10 A {sm('F2')}, 1 A {sm('F3')}."],
         "note": "F1, F2 and F3 look alike: read the marking on each before it goes down.",
         "parts": ["C8", "C11", "F4", "F5", "F1", "F2", "F3"]},
        {"title": "Place the inductors",
         "do": [line(model, "main", ["L100", "L101", "L102", "L103"]), f"The large 15 µH coil {sm('L1')} last: the tallest part."],
         "parts": ["L100", "L101", "L102", "L103", "L1"]},
        {"title": "Check before heating",
         "do": ["Hold the board beside the drawing. Every pasted place has its part, but the nine left empty.",
                "Each part sits square on its pads. Chips and diodes match the red rings."],
         "tip": "A photo now makes the inspection after the hotplate quicker."},
        {"title": "Hotplate",
         "do": ["Door side up; the back is bare, so the board lies flat.",
                "The paste's profile: up to 150 °C, on through 183 °C (the solder melts), peak 235 °C, about 240 s in all.",
                "Let it cool where it lies until the solder has set; then move it."],
         "note": "One pass only."},
        {"title": "Inspect and touch up",
         "do": [f"Under magnification: every pin of the amplifier and protection chips {sm('U100, U1')}, for solder bridges and lifted pins.", "Then every other joint."],
         "tip": "A bridge: flux on it, then a clean iron tip along the pins, or wick. Leave the flux residue: the paste is no-clean."},
        {"title": "Check the supplies for shorts",
         "do": [f"Meter on ohms, black on the ground test pad {sm('TP7')}; red on 20 V {sm('TP2')}, 5 V {sm('TP9')}, 3.3 V {sm('TP16')} and the right-hand pad of the amplifier's fuse {sm('F5 pad 2')}."],
         "note": "None stays at 0 Ω; a reading that climbs as the capacitors charge is fine. 0 Ω: find the bridge before going on."},
        {"title": "Wire link",
         "do": [f"The wire link {sm('LK1')}: 1.0 mm tinned copper wire, from the door side. Solder on the back."],
         "note": "From here on, the through-hole parts: each goes in from the door side and is soldered on the back, lowest part first.",
         "tip": "Solder one end, check it lies flat, then the other.",
         "parts": ["LK1"]},
        {"title": "Pi power socket",
         "do": [f"The Pi power socket {sm('J2')}, USB-C, flat on the board.", "Solder all 16 contacts and the 4 shell stakes."],
         "note": "Its pins stand only 0.5 mm out of the back: a fine tip, and enough solder to fill each hole.",
         "parts": ["J2"]},
        {"title": "Plug sockets",
         "do": [f"2-way: 20 V {sm('J1')}, left speaker {sm('J8')}, right speaker {sm('J9')}.",
                f"4-way: radar {sm('J5')}, touch {sm('J6')}.",
                "Each flat on the board, its outline matching the one printed on the board.",
                "With a fine marker: a mark beside the 20 V, radar and touch sockets."],
         "note": "The 20 V socket is the middle one of the three 2-way sockets.",
         "tip": "Solder one pin, check the socket sits flat, re-melt if not, then the rest.",
         "parts": ["J1", "J8", "J9", "J5", "J6"]},
        {"title": "Sensor headers",
         "do": [f"BME680 {sm('J10')} and light sensor {sm('J11')}: 1 × 4 pin headers, short pins through the board.",
                "A mark beside each: the headers have no key."],
         "parts": ["J10", "J11"]},
        {"title": "Small capacitor",
         "do": [f"22 µF 35 V {sm('C7')}: the long (+) lead in the hole at the red ring. The stripe on the can marks −."],
         "parts": ["C7"]},
        {"title": "Large capacitors",
         "do": [f"120 µF 63 V {sm('C5, C6')}: the long (+) lead in the hole at the red ring. The stripe marks −.", "Seated on the board."],
         "parts": ["C5", "C6"]},
        {"title": "Power module",
         "do": [f"The 5 V power module {sm('PS1')}: its pin 1 at the red ring, the end the board marks “+Vo”.", "Upright and seated; solder the two end pins, check, then the rest."],
         "parts": ["PS1"]},
        {"title": "Trim and finish",
         "do": [f"Cut the leads of the three round capacitors and the wire link {sm('C5, C6, C7, LK1')} to 1.5 mm or less behind the board.",
                f"The row of pads at the top left {sm('J7')} stays empty. The Pi wires go on under Leads."],
         "note": "The ReSpeaker and the display lead lie behind the board: no pin end may stand out more than 4.0 mm."},
    ]
    return _stamp(steps)


def touch_steps(model):
    steps = [
        {"title": "Check the bare board", "do": ["Meter on ohms across the lead's pads marked VCC and GND."], "note": "Open."},
        {"title": "Paste the back",
         "do": ["Board face-down: the four touch pads underneath, the back up.",
                "The second stencil carries the touch board and the strip: line up the touch board's openings and tape over the strip's.",
                "One pass of the squeegee; lift the stencil straight up."],
         "note": "The lead's four pads get no paste.", "tip": "The stencil is made for the board lying face-down: use it as it comes."},
        {"title": "Place the chip",
         "do": [f"The touch chip {sm('U1')}, AT42QT1070, 14 pins: pin 1 (the bevelled long edge, or a dot) at the red ring."],
         "parts": ["U1"]},
        {"title": "Place the resistors and capacitors",
         "do": [line(model, "touch", ["R1", "R2", "R3", "R4"]), line(model, "touch", ["C1"]), line(model, "touch", ["C2"])],
         "parts": ["R1", "R2", "R3", "R4", "C1", "C2"]},
        {"title": "Hotplate",
         "do": ["Face-down on a clean sheet; the front has no parts.", "The same profile as the main board: peak 235 °C, about 240 s.",
                "Let it cool where it lies."]},
        {"title": "Inspect and check",
         "do": ["Under magnification: the touch chip's pins, for solder bridges.", "Meter on ohms across the lead's pads VCC and GND."],
         "note": "Not 0 Ω. The touch lead goes on under Leads."},
    ]
    return _stamp(steps)


def mic_steps(model):
    steps = [
        {"title": "Check the bare strips",
         "do": ["Both strips: hold each to the light. The 0.8 mm sound hole is open.", "Meter on ohms across the lead's pads 1 and 2 (supply and ground): open."],
         "note": "Every step from here is for both strips: they are alike."},
        {"title": "Moisture-sensitive parts",
         "do": [f"Keep the protection diodes {sm('D1–D3')}, ESD321, sealed until the day you solder."],
         "note": "Once open, solder within 168 h. Open longer: bake as the bag's label says."},
        {"title": "Tape the sound hole",
         "do": ["Kapton tape over the sound hole on the plain face, the one that meets the gasket."],
         "note": "Keep flux, paste, water, alcohol and compressed air away from the hole."},
        {"title": "Set the strip in a jig",
         "do": ["Strip face-down, its back level with the surface round it: spare strips laid round it, or a 0.8 mm deep pocket."],
         "note": "No jig is drawn yet.", "tip": "Level matters: the stencil must lie flat over the strip."},
        {"title": "Paste the back",
         "do": ["The second stencil: line up the strip's openings and tape over the touch board's.", "One pass of the squeegee; lift the stencil straight up."],
         "note": "No paste in the sound hole or inside the microphone's ring-shaped pad. Any there: wipe the strip clean and paste again."},
        {"title": "Place the logic chip",
         "do": [f"The logic chip {sm('U1')}, SN74LVC1G17, 5 pins: pin 1 (the dot or bevel) at the red ring."], "parts": ["U1"]},
        {"title": "Place the diodes",
         "do": [f"The three protection diodes {sm('D1, D2, D3')}: the end with the dot or notch at the red ring, the closed end of the bracket printed on the strip."],
         "parts": ["D1", "D2", "D3"]},
        {"title": "Place the resistors and capacitors",
         "do": [line(model, "mic", ["R1"]), line(model, "mic", ["R2"]), line(model, "mic", ["R4"]),
                line(model, "mic", ["R5"], " (required)"), line(model, "mic", ["C1"]), line(model, "mic", ["C2", "C3"])],
         "parts": ["R1", "R2", "R4", "R5", "C1", "C2", "C3"]},
        {"title": "Place the microphone",
         "do": [f"The microphone {sm('MK1')}, last: lid up, its sound port over the hole.", "Hold it by the lid only."],
         "parts": ["MK1"]},
        {"title": "Hotplate",
         "do": ["Face-down, as it lay for pasting. The same profile as the main board: peak 235 °C, about 240 s.",
                "Let it cool where it lies."],
         "note": "One pass. The microphone stands three heatings in all, and any rework counts as one."},
        {"title": "Untape and check",
         "do": ["Once cool, take the Kapton off. Leave the flux residue; no washing.",
                f"Meter on diode test, across each protection diode {sm('D1–D3')}: red on its ground end, black on the other: it conducts; reversed: open.",
                f"Meter on ohms across the lead's pads 1 and 2: not 0 Ω. The 0 Ω link {sm('R5')} is there."],
         "note": "The microphone leads go on under Leads."},
    ]
    return _stamp(steps)


ASM_CSS = """
svg.asm [data-k].todo{opacity:.18}
svg.asm .p1ring{fill:none;stroke:#e0392b;stroke-width:2.2} svg.asm .p1ring.todo{opacity:0} svg.asm .pad{fill:var(--pad)!important;stroke:var(--padring)!important}
svg.asm .hl{fill:none;stroke:var(--accent);stroke-width:2.6;pointer-events:none}
svg.asm .t-ref.cur{fill:var(--accent)}
.asm-h{margin:26px 0 10px;font:700 22px var(--f-display)}
.asm-jump{display:inline-flex;align-items:center;min-height:44px;padding:0 18px;border-radius:999px;background:var(--ink);color:var(--panel);font:600 15px var(--f-body);text-decoration:none;margin:0 8px 12px 0}
.asm-stage{background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:6px;margin:0 0 14px}
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
