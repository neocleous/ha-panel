# Hardware

The panel's three custom boards and the paste stencil, with what is needed to order and build them.

## The boards
| Board | What it does | Size and layers | Per panel | Folder |
|---|---|---|---|---|
| Main board rev 3.2 | 20 V in from the USB-C inlet board; 5 V for the Pi and the radar, 3.3 V for the sensors; the TAS5756M amplifier for the two speakers; sockets for the touch board, radar and sensors | 87.0 × 57.9 × 1.6 mm, 4 layers | 1 | [`main-board/`](main-board/) |
| Mic strip | one MEMS microphone (IM69D120), wired to the ReSpeaker Lite | 28 × 6 × 0.8 mm, 2 layers | 2 | [`mic-strip/`](mic-strip/) |
| Touch board rev D | four touch keys under the chin (AT42QT1070, I²C 0x1B) | 90 × 44 × 1.6 mm, 2 layers | 1 | [`touch-board/`](touch-board/) |
| Paste stencil | one stencil for the main board's door side and the touch board's back | 190 × 190 mm, 0.12 mm | 1 | [`stencil/`](stencil/) |

The touch board of the first panel (v1), rev C, is in [`rev-c/`](rev-c/).

## How to order
All four go to JLC as bare boards and one stencil line: no assembly service. Each upload has an order sheet beside it
with every option and its reason.

| Upload | sha256 | Order sheet |
|---|---|---|
| `main-board/fab/main-board-rev3.2-jlc-2026-11-16.zip` | `fc4588531ea277c1fc3e9009db38fae190042080e065443b0a663f34fa7449bd` | [`main-board/fab/ORDER-SHEET.md`](main-board/fab/ORDER-SHEET.md) |
| `mic-strip/fab/mic-strip-jlc-2026-11-09.zip` | `f405cc567fab336cf9e0fb4b0da1def971ca79bae3d6d8b02ea9bce7e5584564` | [`mic-strip/fab/ORDER-SHEET.md`](mic-strip/fab/ORDER-SHEET.md) |
| `touch-board/fab/touch-board-jlc-2026-11-09.zip` | `2d62d7eca9126be672a78bb0a46d35bbd1463b2dc3d9a8c736272d2777056a34` | [`touch-board/fab/ORDER-SHEET.md`](touch-board/fab/ORDER-SHEET.md) |
| `stencil/fab/stencil-main-rev3.2-touch-revD-jlc-2026-11-16.zip` | `f83d86d130e1cd6dd12528dfa11b598b52d56163d8d25fc2e75cec845d8e9dc2` | [`stencil/fab/ORDER-SHEET.md`](stencil/fab/ORDER-SHEET.md) |

- The three boards are black with white silkscreen and ENIG, "Remove Mark", 5 pieces each.
- JLC's capability figures and the export settings: [`notes/jlc-fab.md`](notes/jlc-fab.md).
- **Parts:** the DigiKey lines are in [`notes/digikey-bom.md`](notes/digikey-bom.md), with a quick-add list in
  `notes/digikey-bom.csv`. Every part on the boards, board by board: [`notes/bom-2026-11-17.md`](notes/bom-2026-11-17.md).

## How to build
- **Surface-mount parts on one face of each board; through-hole connectors by iron.** Nothing smaller than 0603.
- **Paste:** Sn63/Pb37 no-clean (Chip Quik SMD291AX). Through the stencil for the main board and the touch board; by
  syringe for the mic strips.
- **Reflow:** one hotplate pass per board, with the paste maker's profile. The profile and the order of work are in
  [`main-board/README.md`](main-board/README.md); each board's README has its own steps and checks.
- **Bring-up:** [`main-board/README.md`](main-board/README.md), "Bring-up", with the Pi's settings in
  [`notes/pi-config.md`](notes/pi-config.md).
- **Into the enclosure:** the panel's assembly instructions hold those steps; they are not in this repo yet.

## Tools
[`main-board/tools/`](main-board/tools/) exports and checks the fab sets and the stencil, and draws the main board's
assembly drawing (KiCad 9.0.9).
