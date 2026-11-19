# Notes for ordering and building the boards

| File | What it holds | Use it when |
|---|---|---|
| [`bom-2026-11-17.md`](bom-2026-11-17.md), `bom-2026-11-17.csv` | every part on the three boards, board by board, set against the DigiKey lines; the parts that are not DigiKey lines; why some values differ from the datasheets' tables | checking what goes where and what to buy |
| [`digikey-bom.md`](digikey-bom.md) | the panel's 55 DigiKey lines: need, quantity, price and stock (read 2026-11-16; the capacitor line 2026-11-17), the parts not bought, and how the basket changed | ordering at DigiKey |
| `digikey-bom.csv` | the same lines as a DigiKey quick-add list | filling DigiKey's basket |
| [`jlc-fab.md`](jlc-fab.md) | the four JLC uploads with their sha256, JLC's capability figures, the export settings, and the quotes of 2026-11-09 | ordering at JLC; making a fab set again |
| [`pi-config.md`](pi-config.md) | the Raspberry Pi settings the new hardware needs (power, amplifier overlay, radar UART, display) and the checks after the first boot | bring-up; the software on `main` |

Prices and stock are as read on the dates given. Read them again before you order.

The set these lists count is one main board, two mic strips and one touch board. The rest of the panel's parts (the
Raspberry Pi, the display, the ReSpeaker, the speakers, the leads, fasteners, filament) are in the panel's overall parts
list, which is kept outside the repo.
