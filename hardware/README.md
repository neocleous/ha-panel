# Hardware

The panel's three custom boards and the two paste stencils, with what is needed to order and build them.

## The boards
| Board | What it does | Size and layers | Per panel | Folder |
|---|---|---|---|---|
| Main board rev 3.3 | 20 V in from the USB-C inlet board; 5 V for the Pi and the radar, 3.3 V for the sensors; the TAS5756M amplifier for the two speakers; sockets for the touch board, radar and sensors | 87.0 × 57.9 × 1.6 mm, 4 layers | 1 | [`main-board/`](main-board/) |
| Mic strip rev 3 | one MEMS microphone (IM69D120), wired to the ReSpeaker Lite | 28 × 6 × 0.8 mm, 2 layers | 2 | [`mic-strip/`](mic-strip/) |
| Touch board rev E | four touch keys under the chin (AT42QT1070, I²C 0x1B) | 90 × 44 × 1.6 mm, 2 layers | 1 | [`touch-board/`](touch-board/) |
| Paste stencils | one for the main board's door side; one for the touch board's back and the mic strip's back | 100 × 100 mm each, 0.12 mm | 2 | [`stencil/`](stencil/) |

The touch board of the first panel (v1), rev C, is in [`rev-c/`](rev-c/).

## How to order
The three boards go to JLC as bare boards, and the two stencils as stencil lines: no assembly service. Each upload has an order sheet beside it
with every option and its reason.

| Upload | sha256 | Order sheet |
|---|---|---|
| `main-board/fab/main-board-rev3.3-jlc-2026-11-21.zip` | `26ff743470ad6834af4412218b2413478ce8ec22a962c775d0f4b1875617acdd` | [`main-board/fab/ORDER-SHEET.md`](main-board/fab/ORDER-SHEET.md) |
| `mic-strip/fab/mic-strip-rev3-jlc-2026-11-21.zip` | `0e378603bf06f547f44f3cb741d6ad13222e0321c87d36a35d0614bcfe94b095` | [`mic-strip/fab/ORDER-SHEET.md`](mic-strip/fab/ORDER-SHEET.md) |
| `touch-board/fab/touch-board-revE-jlc-2026-11-21.zip` | `12641c710499f8dab67cd457623986f8389a1c9a527aa9ff06c9db64083fa4ec` | [`touch-board/fab/ORDER-SHEET.md`](touch-board/fab/ORDER-SHEET.md) |
| `stencil/fab/stencil-main-rev3.3-jlc-2026-11-21.zip` | `e0097f6055bd09322dac74cab5a10de7c6d13a2cca149c6fb7ec895b5aba6ffe` | [`stencil/fab/ORDER-SHEET.md`](stencil/fab/ORDER-SHEET.md) |
| `stencil/fab/stencil-touch-revE-strip-rev3-jlc-2026-11-21.zip` | `599ac64241dd84a9f7ddcb3c070b1c8a13831d882f812d0e3574a1854434f42c` | [`stencil/fab/ORDER-SHEET.md`](stencil/fab/ORDER-SHEET.md) |

- The three boards are black with white silkscreen and ENIG, "Remove Mark", 5 pieces each.
- These sets of 2026-11-21 replace those of 2026-11-16 and 2026-11-09 (after the pre-order review); each folder keeps
  the old ones in `fab/superseded/`, not to be ordered.
- JLC's capability figures and the export settings: [`notes/jlc-fab.md`](notes/jlc-fab.md).
- **Parts:** the DigiKey lines are in [`notes/digikey-bom.md`](notes/digikey-bom.md), with a quick-add list in
  `notes/digikey-bom.csv`. Every part on the boards, board by board: [`notes/bom-2026-11-17.md`](notes/bom-2026-11-17.md).

## How to build
- **Surface-mount parts on one face of each board; through-hole connectors by iron.** Nothing smaller than 0603.
- **Paste:** Sn63/Pb37 no-clean (Chip Quik SMD291AX), through the stencils: the main board on its own sheet; the touch
  board and the mic strips on the second, the strips in a jig (not drawn yet).
- **Reflow:** one hotplate pass per board, with the paste maker's profile. The profile and the order of work are in
  [`main-board/README.md`](main-board/README.md); each board's README has its own steps and checks.
- **Bring-up:** [`main-board/README.md`](main-board/README.md), "Bring-up", with the Pi's settings in
  [`notes/pi-config.md`](notes/pi-config.md).
- **Into the enclosure:** the panel's assembly instructions hold those steps; they are not in this repo yet.

## Tools
[`main-board/tools/`](main-board/tools/) exports and checks the fab sets and the stencil, and draws the main board's
assembly drawing (KiCad 9.0.9).
