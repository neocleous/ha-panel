# Mic strip

A small board that carries one MEMS microphone (Infineon IM69D120) in the panel's top cap. The panel has two, left and
right: two boards of this one design. Each strip is wired by a five-way lead to the ReSpeaker Lite, the panel's voice
front end, in place of the ReSpeaker's own microphones.

**State (2026-11-21):** rev 3, fab set issued on 2026-11-21 after the pre-order review: the vias are out of the soldered
pads and the silk lines are 0.15 wide ("The board"). The set of 2026-11-09 (rev 1) is in `fab/superseded/` and must not
be ordered. Rev 2 (31.4 long, 2026-11-19) was not built; its name is not reused.
In the cap the strip is held by a printed clamp that presses on two areas of its back; its two holes only locate it
on the cap's pins ("The board"). Not built or tested yet.

**Checks (KiCad 9.0.9, 2026-11-21):** schematic 0 errors, 0 warnings (`erc-report.txt`); board (all severities)
0 violations, 0 unconnected, 0 footprint errors, schematic parity clean (`drc-report.txt`). The check "footprint differs
from library" is set to ignore: U1's and MK1's silk marks at the board edge were removed on purpose. A fresh export
gives the zip of 2026-11-21 file for file.

## Files
| File | What |
|---|---|
| `mic-strip.kicad_pro`, `.kicad_sch`, `.kicad_pcb` | the design, KiCad 9.0.9. Project libraries: `lib/ha_panel.kicad_sym` (IM69D120) and `lib/ha_panel.pretty` (IM69D120 land pattern, 5-pad wire column, and the footprint the two locating holes are drawn with) |
| `mic-strip-schematic.pdf` | the schematic |
| `mic-strip-assembly.pdf` | the assembly drawing (the back, as seen from the back) |
| `mic-strip-3d.png`, `mic-strip-copper-F-B.png` | a render of rev 1 (front = gasket side, back = parts; the moved vias do not show at its size) and both copper layers of rev 3 (back mirrored) |
| `erc-report.txt`, `drc-report.txt` | KiCad's checks |
| [`fab/`](fab/) | **what goes to JLC:** `mic-strip-rev3-jlc-2026-11-21.zip`, the files unzipped in `gerbers/`, the hole list, the check of the set, and the order sheet; `superseded/` holds rev 1's set, which must not be ordered |

## How to order
- **Upload** `fab/mic-strip-rev3-jlc-2026-11-21.zip` to JLC as a bare board. sha256
  `0e378603bf06f547f44f3cb741d6ad13222e0321c87d36a35d0614bcfe94b095`. It replaces the zip of 2026-11-09.
- **Options in short:** 2 layers, 28 × 6 mm, 0.8 mm, black with white silkscreen, ENIG (the page's default for 2 layers
  is OSP: change it), vias tented, deburring on, via class "0.3mm/(0.4/0.45mm)", 5 pieces (2 needed). Every option:
  [`fab/ORDER-SHEET.md`](fab/ORDER-SHEET.md).
- **No stencil:** the strip is pasted by syringe.

## Parts
Every part with its DigiKey line: [`../notes/bom-2026-11-17.md`](../notes/bom-2026-11-17.md), section "Mic strip".

| Ref | Part | Why |
|---|---|---|
| J1 | 5 SMD wire pads 2.0 × 0.7, 1.1 mm pitch, one column across the strip | A JST BM05B-SRSS-TB connector (8.89 mm courtyard) does not fit beside the parts, so the lead is soldered on. Lead: JST A05SR05SR30K305B with both housings cut off, conductors in cable order **1 VDD, 2 GND, 3 CLK, 4 SEL, 5 DATA**; hot-melt strain relief over the pads. The pads are also the test points. |
| D1–D3 | TI ESD321DYAR, SOD-523 | ESD protection on VDD, CLK and DATA next to the pads. 0.9 pF typ / 1.1 pF max, VRWM 3.6 V above the 3.3 V lines. **Pin 1 = GND, pin 2 = IO**, the reverse of the TPD1E05U06 it replaced, so the footprints are turned 180°. Pin 1 is the end marked by the dot (TI marks the DYA pin 1 with a circular notch, not a line); it goes to the closed end of the silk bracket, the GND pad at x 19.8. |
| R1 | 100 Ω 0603 | VDD RC filter with C1: f_c = 159 Hz; drop ≈ 0.1 V at the microphone's 980 µA. |
| C1, C2 | 10 µF 10 V X5R 0603, 100 nF 50 V X7R 0603 | Microphone decoupling; C2 next to MK1's VDD pin. |
| U1 | TI SN74LVC1G17DCKR, SC-70-5 | Schmitt buffer that re-drives CLK next to the microphone. C3 100 nF at VCC. To bypass it on the bench: remove U1 and bridge its pads 2–4 with wire. |
| R2 | 100 kΩ 0603 | Weak pull-down on the buffer input (CLK may be tri-stated when muted — inference). |
| MK1 | Infineon IM69D120V01XTSA1 | Bottom port, −26 dBFS ±1, SNR 69 dB(A), 3.072 MHz inside its 2.9–3.3 MHz range, clock duty 48–52 %, 980 µA typ, VDD 1.62–3.6 V (datasheet rev 1.0, 2017-12-20). |
| R4 | 33 Ω 0603 | DATA source termination (100 Ω as a bench alternative). |
| R5 | 0 Ω 0603 | **Left/right from the lead's SEL wire,** strapped at the ReSpeaker end: GND = left, VDD = right. Must be fitted on both strips; there is no strap on the board. |

## The board
- **28 × 6 × 0.8 mm, 2 layers.** x = 0 at the outer (port) end. Every part sits on the **back** (inner side); the front
  faces the 1.0 mm gasket and carries only the ground pour and short crossings.
- **Port:** unplated Ø0.8 at (2.0, 3.0), under MK1's sound port.
- **Locating holes:** unplated Ø2.0 at (7.5, 3.0) and (26.0, 3.0). They sit on the cap's Ø1.8 pins; nothing is melted or
  screwed through them. On the back a Ø3.6 ring round each hole has no copper. In the KiCad files the holes keep the
  footprint `HeatStake_D2.0mm_Head3.6mm` and the rings the zone names "stake head 1" and "stake head 2", from when the
  pins were to be melted; only the names are left.
- **Press areas for the clamp's toes** (back, symmetric about y 3.0, one over each hole):
  - outer x 6.5–8.5 and inner x 25.7–27.7, both y 2.0–4.0, for toes of 2.0 × 2.0;
  - nothing under them but the holes; a corner of the inner area lies over ground pour under soldermask;
  - nearest: U1's pad 1.120 from the outer area, C2 1.275, R4 1.445; J1's pads 1.650 from the inner area, which ends 0.3
    from the board's inner end;
  - room to move or grow at the same clearances (1.0 to any part, 1.5 to J1): x 6.23–8.62 and 25.56–27.70, out to 0.3
    from the long edges.
- **Heights on the back,** the makers' maximums without the solder under each part: MK1 1.3, the tallest, at the outer
  end; C2 0.9 beside it; between the press areas U1 1.1, C1 1.0, C3 0.9, D1–D3 0.77, the resistors 0.55. The lead's
  wires at J1 are 0.54–0.58 across their insulation.
- One design for both sides: the left strip is the right one turned 180° in the cap's plane (port end outward, gasket
  side up).
- **Rules:** tracks 0.2 (0.25–0.3 for supply and ground), clearance 0.15, copper to edge 0.3; vias 0.5/0.3, ring 0.10;
  hole clearance 0.25, hole to hole 0.25;
  silk lines 0.15, JLC's minimum (0.12 until 2026-11-21).
- **Vias: 24 × 0.5/0.3, all tented.** On 2026-11-09, 28 × 0.45/0.2 became 25 × 0.5/0.3: JLC's order page states its free
  0.2 mm holes only for multilayer boards; 0.3 mm holes are the free class on 2 layers.
- **Vias out of the soldered pads (2026-11-21).** Thirteen via holes lay inside pads that take solder, one wholly inside
  MK1's SELECT pad, and one more ended 0.014 from U1's pin 4. Molten solder runs into an open hole, and the joints under
  MK1 cannot be seen or reworked. Thirteen of these vias moved 0.21 to 0.80, each joined to its pad by a short track on
  the back; the front tracks followed. U1's pin 3 lost its via: the pin already reaches the ground via at (12.925, 2.525)
  through its track to R2.2. Placement, parts, pads, outline, holes and port did not change, and no via lies in the clamp's
  press areas or their room (nearest 0.41 from the outer room, 0.59 from the outer area).
  - Every via hole is now **0.217 or more** from the opening of every pad that takes paste. J1.2's ground via still lies
    partly in its wire pad, which takes no paste; it is left as it is.
  - Achieved: ring 0.10; via hole to hole ≥ 0.40; via hole to unplated hole ≥ 0.86; via hole to other-net track ≥ 0.27
    and to other-net pad ≥ 0.27 (rule 0.25). JLC's figures: [`../notes/jlc-fab.md`](../notes/jlc-fab.md).

## How to assemble
Build two identical strips. Drawing: `mic-strip-assembly.pdf`. One hotplate pass, parts side up.

**Before you start**
- **Paste:** the same Sn63/Pb37 no-clean as the main board, dispensed by syringe.
- **D1–D3 (ESD321DYAR) are moisture-sensitive, level 3:** once their bag is open, solder them within 168 hours at 30 °C /
  60 % humidity or less (TI's package information); open the bag on the day, or bake them per J-STD-033 first.
- **Bare strip:** hold it against the light: the Ø0.8 port hole must be open. Meter: VDD–GND (J1 pads 1–2) open.
- **The port:** Infineon's datasheet (rev 1.0) gives only the reflow qualification: 3 reflows, peak 260 °C, IPC/JEDEC
  J-STD-020D-01; it has no handling, flux or washing rules. Other makers' bottom-port MEMS guides agree on these:
  TDK/InvenSense: water must not reach the port when washing, no blow-off, no ultrasonic cleaning; InvenSense AN-100: the
  port is sensitive to solder flux; ST: seal the port with tape during soldering. So: no-clean paste, **no washing, no
  IPA or air near the port**, and Kapton tape over the hole on the front while soldering.

**Order**
1. Kapton over the port hole on the front (gasket side).
2. Small paste dots on the back pads. Nothing in or next to the port hole.
3. Place:
   - D1–D3 ESD321: pin 1 = GND (dot or notch on the body), at the closed end of the silk bracket;
   - C1 10 µF, C2 100 nF, C3 100 nF;
   - R1 100 Ω, R2 100 kΩ, R4 33 Ω, R5 0 Ω (**required**);
   - U1 SN74LVC1G17 (pin 1 at the chamfer);
   - MK1 last, lid up, port over the hole. Handle it by the lid only.
4. Hotplate with the front (gasket side) down, the same profile as the main board
   ([`../main-board/README.md`](../main-board/README.md)). One pass: the IM69D120 is qualified for 3 reflows, and a
   rework pass counts as one.
5. Remove the Kapton when the strip is cool. Leave the no-clean residue.
6. **Checks, meter only:**
   - D1–D3 in diode mode: red on the GND pad, black on the signal pad → conducts; reversed → open.
   - VDD–GND not shorted.
   - R5 present.
7. **Lead:** JST A05SR05SR30K305B with both housings cut off, free length 230 mm (harness list of 2026-11-14).
   - Strip end: solder the conductors in cable order to J1 pads 1–5: 1 VDD, 2 GND, 3 CLK, 4 SEL, 5 DATA. Pad 1 is at
     the top in the drawing.
   - **The wires lie on their pads with their tips toward the inner end, so that the lead leaves J1 over its outer end**
     (toward D1–D3), never over the inner end: the inner press area starts 1.65 beyond it.
   - Lay the five wires toward the long edge that faces the screen in the cap, and lead them off the board there, over
     D1–D3 (x 19 to 22). Nothing of the lead goes toward the other long edge: the clamp is on that side.
   - Hot-melt strain relief over the pads: a thin bead, no higher than U1 (1.1 from the board) and not past the pads'
     inner end (x 24.05).
   - ReSpeaker end, by function: VDD → pad 1, CLK → 2, DATA → 3, GND → 4 (and 6), SEL → 5. SEL is static and sits
     between CLK and DATA in the cable.
   - SEL strap at the ReSpeaker end: one strip to GND (left), the other to VDD (right).

## Bring-up
No stand-alone power test. With both strips on the ReSpeaker, run `arecord -l`. The pass mark is the audio bench test:
click count, noise floor and false-reject rate. If it fails, the options are: bypass U1 (remove it, wire pads 2–4), or
change R4 from 33 Ω to 100 Ω.

## How it changed
Rev 3 (2026-11-21): the vias out of the soldered pads and silk 0.15, after the pre-order review; nothing else moved.
Rev 2 (31.4 long, holes for M2 screws, 2026-11-19) was not built: the clamp took its place, and rev 1 stood until rev 3.
During the design the JST connector, the on-board strap JP1 and four test pads were dropped for the wire pads, R3 (a
0 Ω bypass) for space; the MSM261DHP006 microphone was replaced by the IM69D120, and the TPD1E05U06DYAR diodes by the
ESD321DYAR (DigiKey: 0 in stock, 26 weeks, 2026-11-08). The scripts that generated the schematic and the layout are in
the history ([`hardware/main-board/gen/` at commit 45a38e4](https://github.com/neocleous/ha-panel/tree/45a38e49d72cf125aab3f4aa91dd065b3bc4f7ee/hardware/main-board/gen));
the KiCad files are the source.

## Sources
- Infineon IM69D120 datasheet rev 1.0 (2017-12-20), including table 6 "Reflow Solder".
- TI SN74LVC1G17, SCES351Y — https://www.ti.com/lit/ds/symlink/sn74lvc1g17.pdf
- TI TPD1E05U06, SLVSBO7O — https://www.ti.com/lit/ds/symlink/tpd1e05u06.pdf
- TI ESD321 datasheet rev C, 2025-06-04 (table 4-2) — https://www.ti.com/lit/ds/symlink/esd321.pdf; TI E2E on the DYA
  pin-1 mark — https://e2e.ti.com/support/interface-group/interface/f/interface-forum/1410599/esd321-pin1-position,
  https://e2e.ti.com/support/interface-group/interface/f/interface-forum/1449663/esd321-pin-1-clarify (read 2026-11-08)
- TDK/InvenSense T5837 DS-000447 rev 1.2 §9 (board wash) — https://www.manualslib.com/manual/3421793/Tdk-T5837.html?page=20
- InvenSense AN-100 rev 1.1 (port sensitive to flux) — https://www.cdiweb.com/datasheets/invensense/MEMS-Microphone-Handling-Guide.pdf
- ST community answer on MEMS microphone soldering (seal the port with tape; no ultrasonic cleaning) — https://community.st.com/t5/mems-sensors/what-are-the-recommended-soldering-parameters-i-e-solder-paste/td-p/469500
- JLC capabilities — https://jlcpcb.com/capabilities
