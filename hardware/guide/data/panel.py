"""Everything the page says that is not inside a KiCad file.

Rules for this file:
- A board pad is named, never described: its net, position and part come from the KiCad board.
- A bought module's pin is defined once, in MODULES, with the label printed on it (or the maker's pin name)
  and the source of that label. A lead wire joins one pin to another by those names.
- Facts the records do not give are listed in OPEN with how to find them; nothing here guesses them.

Sources (read 2026-11-28):
- harness list, seventh issue: Project doc claude/harness-list-2026-11-27.md (lead numbers, free lengths, stock, marks).
- hardware/main-board/gpio-leads.md: the 13 Pi signal wires (parsed at build time, not copied here).
- hardware/notes/pi-config.md: the Pi configuration.
- hardware/main-board/README.md: assembly order, moisture-sensitive parts, bring-up readings.
- hardware/mic-strip/README.md: the strip lead's conductor order and the ReSpeaker end.
- Hi-Link HLK-LD2410C manual v1.00 §4.2: radar pins 1 UART_Tx, 2 UART_Rx, 3 OUT, 4 GND, 5 VCC; module 16 × 22.
- Raspberry Pi 5 mechanical drawing RP-008347-DS-1: board 85 × 56, holes 58 × 49 at 3.5, header centred 29 from
  the first hole, USB-C power 11.2 from the corner.
- Seeed ReSpeakerLitev1.1.step: board 82.02 × 34.01; microphones U4 and U5 on the bottom face, 71.0 apart.
- Adafruit learn guide for product 5807: the output pads are marked + and −.
"""

# --------------------------------------------------------------------------------------------- net colours
# Each class keeps the meaning it has on the Haunted Manor page. Net names are KiCad's, sheet path stripped.
NET_CLASSES = [
    # (class id, legend label, css colour light, css colour dark, nets)
    ("vin", "20 V in, before the protection chip", "#dd7400", "#ffa640", ["VIN_PIGTAIL", "VIN_EF"]),
    ("v20", "20 V protected, amplifier supply", "#8a5a2b", "#d29b63", ["+20V", "PVDD", "NID_VIN"]),
    ("5v", "+5 V", "#cc2b25", "#ff6a61", ["+5V", "5V_PI_F", "VBUS_PI", "5V_RADAR", "LDO_IN", "PI_5V"]),
    ("3v3", "+3.3 V", "#bb2f8c", "#f27ccb", ["+3V3", "3V3_SENS", "3V3_AMP", "PI_3V3", "VDD_C", "VDD_MIC"]),
    ("gnd", "GND", "#262c30", "#d3dbdf", ["GND"]),
    ("sda", "I²C SDA", "#a87600", "#f0c24d", ["I2C_SDA", "SDA"]),
    ("scl", "I²C SCL", "#7a6200", "#d8b04a", ["I2C_SCL", "SCL"]),
    ("tx", "UART, Pi to radar", "#1c63c4", "#6ba8ff", ["PI_TXD"]),
    ("rx", "UART, radar to Pi", "#7442bf", "#b48cff", ["LD_TX", "PI_RXD"]),
    ("snd", "I²S and microphone clock and data", "#1f8655", "#5ed195",
     ["PI_BCLK", "PI_LRCLK", "PI_DOUT", "PI_DIN", "I2S_BCLK", "I2S_LRCLK", "I2S_DOUT",
      "CLK_C", "DATA_C", "SEL_C", "CLK_MIC", "DATA_MIC", "MIC_LR"]),
    ("spk", "Speaker", "#0b8282", "#4fd2d2", ["SPK_L_P", "SPK_L_N", "SPK_R_P", "SPK_R_N"]),
    ("ctl", "Control and status", "#566a7d", "#9fb3c6",
     ["AMP_MUTE_N", "EF_PGOOD", "EF_FLT_N", "AMP_FAULT_N", "NID_RC", "NID_TRIM", "EF_SHDN", "EF_IMON"]),
]

# Plain names for nets, used in tables (the KiCad name is shown beside it).
NET_NAMES = {
    "VIN_PIGTAIL": "20 V from the inlet board", "VIN_EF": "20 V after F1", "+20V": "20 V protected",
    "PVDD": "amplifier supply", "NID_VIN": "5 V module input", "+5V": "+5 V", "5V_PI_F": "Pi 5 V after F2",
    "VBUS_PI": "Pi 5 V at J2", "5V_RADAR": "radar 5 V", "LDO_IN": "3.3 V regulator input", "+3V3": "+3.3 V",
    "3V3_SENS": "sensor 3.3 V", "3V3_AMP": "amplifier logic 3.3 V", "PI_3V3": "Pi 3.3 V (sense only)",
    "GND": "GND", "I2C_SDA": "I²C SDA", "I2C_SCL": "I²C SCL", "PI_TXD": "Pi TXD", "PI_RXD": "Pi RXD",
    "LD_TX": "radar TX", "PI_BCLK": "I²S bit clock", "PI_LRCLK": "I²S frame clock", "PI_DOUT": "I²S out",
    "PI_DIN": "I²S in", "AMP_MUTE_N": "amplifier mute", "SPK_L_P": "left speaker +", "SPK_L_N": "left speaker −",
    "SPK_R_P": "right speaker +", "SPK_R_N": "right speaker −", "VDD_C": "microphone 3.3 V",
    "CLK_C": "microphone clock", "DATA_C": "microphone data", "SEL_C": "left/right select",
    "SDA": "I²C SDA", "SCL": "I²C SCL", "PI_5V": "Pi 5 V (header pins 2, 4)", "I2S_BCLK": "I²S bit clock at the amplifier", "I2S_LRCLK": "I²S frame clock at the amplifier", "I2S_DOUT": "I²S out at the amplifier",
}

# --------------------------------------------------------------------------------------------- modules
# pins: id -> (label as printed or by the maker, role)
# role: the net the pin must end up on, written as a KiCad net name (or None for "must stay unconnected").
# This is what the build checks each lead against; it comes from the module's own documentation,
# not from the lead table.
MODULES = {
    "inlet": {
        "name": "USB-C inlet board", "part": "Adafruit 5807 (HUSB238), set to 20 V",
        "size": None, "source": "Adafruit learn guide, product 5807: output marked + and −",
        "pins": {"+": ("+", "VIN_PIGTAIL"), "-": ("−", "GND")},
    },
    "spkL": {
        "name": "Left speaker", "part": "Dayton Audio DMA45-4",
        "size": None, "source": "tab marking on the driver (to read on the part)",
        "pins": {"+": ("+ tab", "SPK_L_P"), "-": ("− tab", "SPK_L_N")},
    },
    "spkR": {
        "name": "Right speaker", "part": "Dayton Audio DMA45-4",
        "size": None, "source": "tab marking on the driver (to read on the part)",
        "pins": {"+": ("+ tab", "SPK_R_P"), "-": ("− tab", "SPK_R_N")},
    },
    "radar": {
        "name": "Radar", "part": "Hi-Link HLK-LD2410C",
        "size": (16.0, 22.0), "source": "HLK-LD2410C manual v1.00 §4.2 and figure 5",
        "pins": {"1": ("UART_Tx", "LD_TX"), "2": ("UART_Rx", "PI_TXD"), "3": ("OUT", None),
                 "4": ("GND", "GND"), "5": ("VCC", "5V_RADAR")},
    },
    "touchbd": {
        "name": "Touch board", "part": "touch board rev E (this repo)", "kicad": "touch",
        "pins": {"1": ("VCC", "+3V3"), "2": ("GND", "GND"), "3": ("SDA", "I2C_SDA"), "4": ("SCL", "I2C_SCL")},
        "kicad_ref": "J1",
    },
    "bme680": {
        "name": "BME680 sensor board", "part": "CJMCU-680",
        "size": None, "source": "the board's printed labels (order not in the records)",
        "pins": {"VCC": ("VCC", "3V3_SENS"), "GND": ("GND", "GND"), "SDA": ("SDA", "I2C_SDA"), "SCL": ("SCL", "I2C_SCL")},
    },
    "veml6030": {
        "name": "VEML6030 sensor board", "part": "VEML6030 board in the cap (maker not in the records)",
        "size": None, "source": "the board's printed labels (board and order not in the records)",
        "pins": {"VCC": ("VCC / VIN", "3V3_SENS"), "GND": ("GND", "GND"), "SDA": ("SDA", "I2C_SDA"), "SCL": ("SCL", "I2C_SCL")},
    },
    "respeaker": {
        "name": "ReSpeaker Lite", "part": "Seeed 107990273, USB firmware",
        "size": (82.02, 34.01), "source": "Seeed ReSpeakerLitev1.1.step; pad functions per the MSM261D3526H1CPM datasheet",
        # The two microphone footprints, emptied. Pad functions are the fitted microphone's; their places inside each
        # footprint are confirmed with a meter (OPEN).
        "pins": {f"{m}.{p}": (f"{lab}, pad {p} {fn}", None) for m, lab in (("L", "footprint with L/R at GND"), ("R", "footprint with L/R at VDD"))
                 for p, fn in (("1", "VDD"), ("2", "CLK"), ("3", "DATA"), ("4", "GND"), ("5", "L/R"), ("6", "GND"))},
        "mics": {"U4": (44.40 - 40.24, 89.20 - 73.95 + 0.0, 47.05 - 40.24, 92.71 - 73.95),
                 "U5": (115.40 - 40.24, 89.20 - 73.95, 118.05 - 40.24, 92.71 - 73.95)},
    },
    "micL": {"name": "Left microphone strip", "part": "mic strip rev 3", "kicad": "mic", "kicad_ref": "J1",
             "pins": {"1": ("VDD", "VDD_C"), "2": ("GND", "GND"), "3": ("CLK", "CLK_C"), "4": ("SEL", "SEL_C"), "5": ("DATA", "DATA_C")}},
    "micR": {"name": "Right microphone strip", "part": "mic strip rev 3", "kicad": "mic", "kicad_ref": "J1",
             "pins": {"1": ("VDD", "VDD_C"), "2": ("GND", "GND"), "3": ("CLK", "CLK_C"), "4": ("SEL", "SEL_C"), "5": ("DATA", "DATA_C")}},
    "display": {
        "name": "Display", "part": "Waveshare 8inch DSI LCD (C)",
        "size": None, "source": "Waveshare wiki: 5 V 4.75–5.30 V, at least 0.5 A; header pin order not published",
        "pins": {"5V": ("5V", "PI_5V"), "GND": ("GND", "GND")},
    },
}

# The Raspberry Pi 5 header. Functions are the Pi's own; the overlays in pi-config.md use the ones marked.
PI_HEADER = {
    1: "3V3", 2: "5V", 3: "GPIO2 SDA1", 4: "5V", 5: "GPIO3 SCL1", 6: "GND", 7: "GPIO4", 8: "GPIO14 TXD0", 9: "GND",
    10: "GPIO15 RXD0", 11: "GPIO17", 12: "GPIO18 PCM_CLK", 13: "GPIO27", 14: "GND", 15: "GPIO22", 16: "GPIO23",
    17: "3V3", 18: "GPIO24", 19: "GPIO10", 20: "GND", 21: "GPIO9", 22: "GPIO25", 23: "GPIO11", 24: "GPIO8", 25: "GND",
    26: "GPIO7", 27: "ID_SD", 28: "ID_SC", 29: "GPIO5", 30: "GND", 31: "GPIO6", 32: "GPIO12", 33: "GPIO13", 34: "GND",
    35: "GPIO19 PCM_FS", 36: "GPIO16", 37: "GPIO26", 38: "GPIO20 PCM_DIN", 39: "GND", 40: "GPIO21 PCM_DOUT",
}
# What each used header pin must carry, from the configuration (pi-config.md rows 3 and 4, and I²C1 on):
# the overlay rpi-digiampplus uses GPIO18/19/20/21 for I²S and GPIO22 for mute; uart0 is GPIO14/15; I²C1 is GPIO2/3.
PI_PIN_ROLE = {1: "PI_3V3", 2: "PI_5V", 3: "I2C_SDA", 4: "PI_5V", 5: "I2C_SCL", 6: "GND", 8: "PI_TXD", 9: "GND",
               10: "PI_RXD", 12: "PI_BCLK", 14: "GND", 15: "AMP_MUTE_N", 35: "PI_LRCLK", 38: "PI_DIN", 39: "GND",
               40: "PI_DOUT"}
# Pi 5 mechanical drawing: board 85 × 56, mounting holes Ø2.7 at 3.5 from two edges, 58 × 49 apart;
# header centred 29 right of the first hole (x 32.5), its rows 3.5 ± 1.27 from the top edge, pin 1 in the inner row.
PI5 = {"size": (85.0, 56.0), "holes": [(3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)], "hole_d": 2.7,
       "header_centre_x": 32.5, "header_row_y": {"odd": 3.5 + 1.27, "even": 3.5 - 1.27}, "usbc_x": 11.2}

# The three Dupont housings at the Pi end, and the display lead's own housing (harness list §2; gpio-leads.md).
PI_HOUSINGS = {
    "1": {"pins": [1, 3, 5], "shape": "1 × 3"},
    "2": {"pins": list(range(7, 17)), "shape": "2 × 5"},
    "3": {"pins": list(range(35, 41)), "shape": "2 × 3"},
    "display": {"pins": [2, 4, 6], "shape": "1 × 3, the display lead's own"},
}

# --------------------------------------------------------------------------------------------- leads
# Lead numbers, free lengths, stock and marks: harness list, seventh issue (2026-11-27), sections 1 to 3.
# A wire is (from, to). "main:J1.1" is pad 1 of J1 on the main board; "inlet:+" is a module pin above;
# "pi:8" is Pi header pin 8. Leads 8 to 10 are generated from gpio-leads.md at build time.
LEADS = [
    {"n": 1, "name": "20 V", "free": 90, "stock": "2 halves of JST ASXHSXH22K305, black 22 AWG", "plug": "XHP-2 on J1",
     "mark": "a mark on the plug and beside J1: the middle of the three 2-way sockets",
     "wires": [("main:J1.1", "inlet:+"), ("main:J1.2", "inlet:-")], "first": True},
    {"n": 2, "name": "Left speaker", "free": 135, "stock": "2 halves of JST ASXHSXH22K305", "plug": "XHP-2 on J8",
     "mark": "", "wires": [("main:J8.1", "spkL:+"), ("main:J8.2", "spkL:-")],
     "note": "about 35 inside the box; hot-melt round the lead in the box's 4.0 hole; plugged and pulled with long-nose pliers"},
    {"n": 3, "name": "Right speaker", "free": 127, "stock": "2 halves of JST ASXHSXH22K305", "plug": "XHP-2 on J9",
     "mark": "", "wires": [("main:J9.1", "spkR:+"), ("main:J9.2", "spkR:-")],
     "note": "about 35 inside the box; hot-melt round the lead in the box's 4.0 hole"},
    {"n": 4, "name": "Radar", "free": 118, "stock": "4 halves of JST ASXHSXH22K305", "plug": "XHP-4 on J5",
     "mark": "a mark on the housing and beside J5",
     "wires": [("main:J5.1", "radar:5"), ("main:J5.2", "radar:4"), ("main:J5.3", "radar:1"), ("main:J5.4", "radar:2")],
     "note": "radar OUT (pin 3) is not wired; tied through the slot in the holder's top plate"},
    {"n": 5, "name": "Touch", "free": 87, "stock": "4 halves of JST ASXHSXH22K305", "plug": "XHP-4 on J6",
     "mark": "a mark on the housing and beside J6: this lead reaches the radar socket",
     "wires": [("main:J6.1", "touchbd:1"), ("main:J6.2", "touchbd:2"), ("main:J6.3", "touchbd:3"), ("main:J6.4", "touchbd:4")]},
    {"n": 6, "name": "BME680", "free": 93, "stock": "4 wires of Adafruit 3141", "plug": "1 × 4 Dupont housing on J10",
     "mark": "a mark on the housing and beside J10: the header has no key",
     "wires": [("main:J10.1", "bme680:VCC"), ("main:J10.2", "bme680:GND"), ("main:J10.3", "bme680:SDA"), ("main:J10.4", "bme680:SCL")],
     "note": "a plug of 2 mm foam round the lead in the tray's slot"},
    {"n": 7, "name": "VEML6030", "free": 116, "stock": "4 wires of Adafruit 3141", "plug": "1 × 4 Dupont housing on J11",
     "mark": "a mark on the housing and beside J11",
     "wires": [("main:J11.1", "veml6030:VCC"), ("main:J11.2", "veml6030:GND"), ("main:J11.3", "veml6030:SDA"), ("main:J11.4", "veml6030:SCL")]},
    # 8, 9, 10: from gpio-leads.md
    {"n": 11, "name": "Display power", "free": 180, "stock": "the display's own lead, extended with 2 wires of Adafruit 3141 under heat-shrink",
     "plug": "the lead's own 1 × 3 housing on Pi pins 2-4-6", "mark": "",
     "wires": [("display:5V", "pi:2"), ("display:GND", "pi:6")],
     "note": "5 V on pin 2 or 4, GND on pin 6. Pins 2 and 4 are both 5 V: check the row before pressing home"},
    {"n": 13, "name": "Left microphone", "free": 230, "stock": "JST A05SR05SR30K305B, both housings cut off", "plug": "soldered both ends",
     "mark": "", "wires": [("micL:1", "respeaker:L.1"), ("micL:2", "respeaker:L.4"), ("micL:3", "respeaker:L.2"),
                          ("micL:4", "respeaker:L.5"), ("micL:5", "respeaker:L.3")],
     "bridge": ("respeaker:L.4", "respeaker:L.6"),
     "note": "to the emptied footprint whose L/R pad (5) is at GND: that makes this strip the left channel"},
    {"n": 14, "name": "Right microphone", "free": 230, "stock": "JST A05SR05SR30K305B, both housings cut off", "plug": "soldered both ends",
     "mark": "", "wires": [("micR:1", "respeaker:R.1"), ("micR:2", "respeaker:R.4"), ("micR:3", "respeaker:R.2"),
                          ("micR:4", "respeaker:R.5"), ("micR:5", "respeaker:R.3")],
     "bridge": ("respeaker:R.4", "respeaker:R.6"),
     "note": "to the emptied footprint whose L/R pad (5) is at VDD: that makes this strip the right channel"},
]
# Cables bought as they are (no pins to map on this page).
CABLES = [
    {"n": 12, "name": "DSI ribbon", "what": "Waveshare 200 mm, 22-way at the Pi, 15-way at the display, black shielding film", "ends": ("display DSI", "Pi DSI")},
    {"n": 15, "name": "Pi power", "what": "USB-C to USB-C 5 A, 0.2 m, through the CableCreation 90° adapter", "ends": ("main board J2", "Pi USB-C")},
    {"n": 16, "name": "ReSpeaker USB", "what": "ADT-Link S3K-T2G flat cable, 25 cm (S3J-T2G the spare)", "ends": ("Pi lower blue USB-A", "ReSpeaker USB-C")},
]

# Main-board sockets that take a plug, in the plugging order (your ruling: the 20 V plug first, on the middle socket).
PLUG_ORDER = ["J1", "J9", "J8", "J6", "J5", "J10", "J11", "J2"]

# --------------------------------------------------------------------------------------------- open points
OPEN = [
    ("ReSpeaker microphone pads", "The records give the pad functions (1 VDD, 2 CLK, 3 DATA, 4 and 6 GND, 5 L/R) but not where pad 1 sits in each emptied footprint, nor which of U4 and U5 has its L/R pad at GND.",
     "Before wiring: meter in beep mode from the USB-C shell. Pads 4 and 6 beep (GND). With the ReSpeaker on USB and the microphones off, pad 1 reads about 3.3 V. Of the rest, the pad next to 4 and 6 strapped to a rail is L/R (5). Note what you find for each footprint."),
    ("VEML6030 board", "Which board it is, and the order of its pads.", "Wire by the board's printed labels: VCC (or VIN), GND, SDA, SCL."),
    ("BME680 board pad order", "The CJMCU-680's pad order.", "Wire by its printed labels: VCC, GND, SDA, SCL. SDO and CS stay unwired."),
    ("Display power lead", "Which wires of the display's own lead carry 5 V and GND, their colours, and the lead's own length.",
     "Plug the lead onto the display, then meter beep mode from the display's GND (a mounting screw's metal) to each housing contact: that one is GND. Of the other two wired contacts, the one that reads 5 V at the display when the Pi is powered is 5 V."),
    ("Adafruit 3141 colours", "The strip's colours are blank until it arrives.", "Fill in the harness list's colour table on arrival."),
    ("Speaker + tab", "The DMA45-4's polarity marking.", "Read the + mark on the driver. If none: a 1.5 V cell across the tabs for a moment; the tab on the cell's + when the cone moves out is +."),
    ("Bought modules' outlines in the unit", "The inlet board, display, BME680 and VEML6030 boards and the drivers have no published outline here.", "Their envelopes come from the model, version 91, once Fusion answers."),
]
OPEN.append(("Microphone strip jig", "The mic strip README: the strip lies front-down in a jig flush with the surface round it for pasting; no jig is drawn yet.",
             "A pocket of the strip's size (28 × 6, as deep as the strip and the Kapton), or spare strips laid round it."))
OPEN.append(("Harness list against the board", "The harness list (2026-11-27, §2) gives J6 pin 1 as 3V3_SENS; rev 3.3 moved J6 onto +3V3, ahead of F4 (main board README). The page follows the board file.",
             "For the Architect: correct the harness list at its next issue."))
OPEN.append(("Touch board revision in the harness list", "The harness list names the touch board rev D; the repo's board is rev E (rev D's copper, wider silk).",
             "For the Architect: rev E at the harness list's next issue."))
OPEN.append(("Plugging order in the records", "The harness list and the main board README put the speakers before the 20 V plug; your ruling puts the 20 V plug first, on the middle socket. The page follows the ruling.",
             "For the Architect: bring the harness list and README in line."))

# ============================================================================================ revision of 2026-11-28
# D572, D573 and Daniel's rulings of 2026-11-28 13:12 on the colour table:
#  - the strip's ten colours are black, brown, red, orange, yellow, green, blue, purple, grey, white (1a);
#  - the two sensor grounds are brown strip wire with a black mark at both ends, drawn black (2a);
#  - speakers: + red, − black ("they are obviously distinct from power and ground").

NET_NAMES.update({
    "AMP_FAULT_N": "amplifier fault", "AMP_GPIO0": "amplifier setting 0", "AMP_GPIO1": "amplifier setting 1",
    "AMP_GPIO2": "amplifier setting 2", "BST_AN": "amplifier boost, A−", "BST_AP": "amplifier boost, A+",
    "BST_BN": "amplifier boost, B−", "BST_BP": "amplifier boost, B+", "CN": "charge pump −", "CP": "charge pump +",
    "CPVSS": "charge-pump supply", "DAC_A": "amplifier DAC A", "DAC_B": "amplifier DAC B", "DVDD_REG": "amplifier core supply",
    "EF_DVDT": "protection chip ramp", "EF_FLT_N": "protection chip fault", "EF_ILIM": "current limit setting",
    "EF_IMON": "current monitor", "EF_OVP": "over-voltage setting", "EF_PGOOD": "power good", "EF_SHDN": "protection chip on/off",
    "EF_UVLO": "under-voltage setting", "GVDD": "amplifier gate supply", "INA_N": "amplifier input A−", "INA_P": "amplifier input A+",
    "INB_N": "amplifier input B−", "INB_P": "amplifier input B+", "NID_RC": "5 V module on/off", "NID_TRIM": "5 V trim",
    "OUT_AN": "amplifier output A−", "OUT_AP": "amplifier output A+", "OUT_BN": "amplifier output B−", "OUT_BP": "amplifier output B+",
    "PI_CC1": "Pi USB-C CC1", "PI_CC2": "Pi USB-C CC2", "RS_BCLK": "echo tap, bit clock", "RS_LRCLK": "echo tap, frame clock",
    "RS_OUT": "echo tap, data", "RS_REF": "echo tap, reference", "RS_SCL": "echo tap, I²C clock", "RS_SDA": "echo tap, I²C data",
    "SPK_GAIN": "speaker gain setting", "E0": "touch pad 1", "E1": "touch pad 2", "E2": "touch pad 3", "E3": "touch pad 4",
    "KEY0": "touch line 1", "KEY1": "touch line 2", "KEY2": "touch line 3", "KEY3": "touch line 4",
    "CLK_MIC": "clock at the microphone", "DATA_MIC": "data at the microphone", "MIC_LR": "left/right select at the microphone",
    "VDD_MIC": "3.3 V at the microphone", "+5V": "5 V", "+3V3": "3.3 V", "3V3_SENS": "3.3 V for the sensors",
    "VBUS_PI": "5 V for the Pi", "5V_PI_F": "5 V for the Pi, after its fuse", "5V_RADAR": "5 V for the radar",
    "PI_3V3": "the Pi's 3.3 V (sense)", "VIN_PIGTAIL": "20 V in", "VIN_EF": "20 V in, after the first fuse",
    "+20V": "20 V protected", "PVDD": "20 V for the amplifier", "NID_VIN": "20 V for the 5 V module", "LDO_IN": "5 V for the 3.3 V regulator",
    "3V3_AMP": "3.3 V for the amplifier", "VDD_C": "3.3 V for the microphone", "CLK_C": "microphone clock", "DATA_C": "microphone data",
    "SEL_C": "left/right select", "PI_TXD": "serial, Pi to radar", "LD_TX": "serial, radar to Pi", "PI_RXD": "serial, radar to Pi",
    "PI_BCLK": "I²S bit clock", "PI_LRCLK": "I²S frame clock", "PI_DOUT": "I²S out", "PI_DIN": "I²S in", "I2C_SDA": "I²C data",
    "I2C_SCL": "I²C clock", "SDA": "I²C data", "SCL": "I²C clock", "AMP_MUTE_N": "amplifier mute",
    "I2S_BCLK": "I²S bit clock", "I2S_LRCLK": "I²S frame clock", "I2S_DOUT": "I²S out",
    "SPK_L_P": "left speaker +", "SPK_L_N": "left speaker −", "SPK_R_P": "right speaker +", "SPK_R_N": "right speaker −",
    "GND": "ground", "PI_5V": "the Pi's 5 V",
})

# One colour for one job, everywhere on the page (light, dark).
JOBS = {
    "vplus": ("V+, and speaker +", "red", "#d3302a", "#ff6a61"),
    "gnd": ("Ground, and speaker −", "black", "#23282b", "#d3dbdf"),
    "sda": ("I²C data", "blue", "#1c63c4", "#6ba8ff"),
    "scl": ("I²C clock", "yellow", "#d9a400", "#f0c24d"),
    "tx": ("Serial, Pi to radar", "green", "#1f8655", "#5ed195"),
    "rx": ("Serial, radar to Pi", "purple", "#7442bf", "#b48cff"),
    "aclk": ("Audio clock", "white", "#f4f4f1", "#f4f4f1"),
    "adat": ("Audio data", "orange", "#e07000", "#ffa640"),
    "ctl": ("Control", "grey", "#8a9399", "#a9b3b8"),
}
# Speakers: + red, − black (Daniel, 2026-11-28 13:12).
NET_JOB = {
    "VIN_PIGTAIL": "vplus", "5V_RADAR": "vplus", "+3V3": "vplus", "3V3_SENS": "vplus", "PI_3V3": "vplus", "PI_5V": "vplus", "VDD_C": "vplus",
    "SPK_L_P": "vplus", "SPK_R_P": "vplus",
    "GND": "gnd", "SPK_L_N": "gnd", "SPK_R_N": "gnd",
    "I2C_SDA": "sda", "I2C_SCL": "scl", "PI_TXD": "tx", "LD_TX": "rx", "PI_RXD": "rx",
    "PI_BCLK": "aclk", "PI_LRCLK": "aclk", "CLK_C": "aclk", "PI_DOUT": "adat", "PI_DIN": "adat", "DATA_C": "adat",
    "AMP_MUTE_N": "ctl", "SEL_C": "ctl",
}
# The ten colours of the Adafruit 3141 strip (Daniel, 1a) and how many of each it has.
STRIP_COLOURS = ["black", "brown", "red", "orange", "yellow", "green", "blue", "purple", "grey", "white"]
STRIP_PER_COLOUR = 4
# What each lead is cut from: "black" = all-black pre-crimped jumpers; "strip" = the Adafruit 3141 strip.
LEAD_STOCK = {1: "black", 2: "black", 3: "black", 4: "black", 5: "black", 13: "black", 14: "black",
              6: "strip", 7: "strip", 8: "strip", 9: "strip", 10: "strip", 11: "strip"}

# Plain names (D572).
LEAD_NAMES = {1: "20 V lead", 2: "left speaker lead", 3: "right speaker lead", 4: "radar lead", 5: "touch lead",
              6: "BME680 lead", 7: "light-sensor lead", 8: "Pi wires: power and I²C", 9: "Pi wires: serial, audio clock and mute",
              10: "Pi wires: audio data", 11: "display power lead", 12: "display ribbon", 13: "left microphone lead",
              14: "right microphone lead", 15: "Pi power cable", 16: "ReSpeaker USB cable"}
LEAD_SHORT = {1: "20 V", 2: "Left speaker", 3: "Right speaker", 4: "Radar", 5: "Touch", 6: "BME680", 7: "Light sensor",
              8: "Pi: power and I²C", 9: "Pi: serial, audio clock, mute", 10: "Pi: audio data", 11: "Display power", 12: "Ribbon", 13: "Left mic",
              14: "Right mic", 15: "Pi power", 16: "ReSpeaker USB"}
SOCKET_NAMES = {"J1": "20 V socket", "J2": "Pi power socket", "J3": "Pi wire pads", "J4": "Pi wire pads, I²S",
                "J5": "radar socket", "J6": "touch socket", "J7": "echo tap pads", "J8": "left speaker socket",
                "J9": "right speaker socket", "J10": "BME680 header", "J11": "light-sensor header"}
MODULES["veml6030"]["name"] = "Light sensor"
MODULES["bme680"]["name"] = "BME680 board"
MODULES["inlet"]["name"] = "Inlet board"
MODULES["display"]["name"] = "Display"

# The steps for each lead (D572: Do, Note, Tip). Facts: harness list 2026-11-27 §1–§5.
# Which wire goes where, its colour and its mark come from the model and are tabled under each step; they are not typed here.
MARK = "Mark each wire at both ends as in the table."
LEAD_STEPS = {
    1: {"do": ["Cut one black jumper in half.", MARK, "Solder the cut ends to the inlet board's + and − pads. 90 mm free.",
               "Mark the plug, and the board beside the 20 V socket."],
        "note": "This plug goes on the middle of the three 2-way sockets, and goes on first. On a speaker socket it can destroy the board.",
        "tip": "Mark before you cut: the two halves look the same."},
    2: {"do": ["Cut one black jumper in half.", MARK, "Solder to the driver's tabs before the driver goes into its box. Connector pointing up, toward the box roof.",
               "Run 35 mm inside the box to the 4 mm hole in its rear wall, out through it, and hot-melt round the lead in the hole. About 135 mm free."],
        "note": "Keep it clear of the ReSpeaker USB cable while the left box slides back.",
        "tip": "Plug and pull it with long-nose pliers on the housing's top and bottom; press it home with closed tweezers."},
    3: {"do": ["Cut one black jumper in half.", MARK, "Solder to the driver's tabs before the driver goes into its box. Connector pointing up.",
               "Run 35 mm inside the box to the 4 mm hole, out through it, and hot-melt round the lead in the hole. About 127 mm free."],
        "note": "", "tip": ""},
    4: {"do": ["Cut two black jumpers in half; take four halves.", MARK, "Solder to the radar by its printed labels. Its OUT pin stays free. 118 mm free.",
               "Tie the lead through the slot in the holder's top plate, 10 mm behind the radar; run it over the Pi.",
               "Mark the housing, and the board beside the radar socket."],
        "note": "", "tip": "In service the BME680 plug comes off first, then this one."},
    5: {"do": ["Cut two black jumpers in half; take four halves.", MARK, "Solder to the touch board's HOST pads by their labels. 87 mm free.",
               "Mark the housing, and the board beside the touch socket."],
        "note": "This lead also reaches the radar socket. Check the mark before you plug it.", "tip": ""},
    6: {"do": ["Take the four strip wires in the table.", MARK, "Cut the contacts off one end and solder to the BME680 board by its labels. 93 mm free.",
               "Push the other contacts into a 1 × 4 housing in the table's order.", "Thread the lead through the tray's slot, with a plug of 2 mm foam round it there.",
               "Mark the housing, and the board beside the BME680 header."],
        "note": "The header has no key. The red wire goes on pin 1.", "tip": ""},
    7: {"do": ["Take the four strip wires in the table.", MARK, "Cut the contacts off one end and solder to the light sensor by its labels. 116 mm free.",
               "Push the other contacts into a 1 × 4 housing in the table's order.", "Mark the housing, and the board beside the light-sensor header."],
        "note": "The header has no key. The red wire goes on pin 1.", "tip": ""},
    8: {"do": ["Take the three strip wires in the table.", "Cut the contacts off one end. Push each wire in from the board's back face and solder it on the door side. 70 mm free.",
               "Push the other contacts into a 1 × 3 housing for Pi pins 1, 3 and 5."],
        "note": "", "tip": "Solder these before the board goes on its carrier."},
    9: {"do": ["Take the six strip wires in the table.", "Cut the contacts off one end; in from the back face, soldered on the door side. 70 mm free.",
               "Push the other contacts into a 2 × 5 housing for Pi pins 7 to 16. Pins 7, 11, 13 and 16 stay empty."],
        "note": "", "tip": ""},
    10: {"do": ["Take the four strip wires in the table.", "Cut the contacts off one end; in from the back face, soldered on the door side. 70 mm free.",
                "Push the other contacts into a 2 × 3 housing for Pi pins 35 to 40. Pins 36 and 37 stay empty."],
         "note": "The two orange wires are not alike: I²S in goes to Pi pin 38, I²S out to pin 40.", "tip": "Tag the I²S out wire before you cut its contact."},
    11: {"do": ["Plug the display's own lead onto its 4-pin header.", "Find its 5 V and ground wires with the meter (see Not in the records).",
                "Splice the two strip wires in the table onto them, under heat-shrink. 180 mm in all.",
                "Put their contacts into the lead's own 1 × 3 housing, on Pi pins 2 and 6."],
         "note": "Pins 2 and 4 are both 5 V. Check the row before you press the housing home.", "tip": "Insulate the lead's two unused wires."},
    13: {"do": ["Cut both housings off one 5-way cable.", MARK, "Solder one end to the left strip's pads 1 to 5.",
                "Solder the other end to the ReSpeaker's emptied microphone pads whose left/right pad reads ground. Bridge the two ground pads. 230 mm free."],
         "note": "Coil the spare in three turns, about 19 mm across, behind the screen plate.", "tip": "Find the pads with the meter first (see Not in the records)."},
    14: {"do": ["Cut both housings off one 5-way cable.", MARK, "Solder one end to the right strip's pads 1 to 5.",
                "Solder the other end to the emptied pads whose left/right pad reads 3.3 V. Bridge the two ground pads. 230 mm free."],
         "note": "", "tip": ""},
}
# Ruling 2a: the sensor leads' grounds are brown strip wire with a black mark (the strip has four black wires, the leads need six grounds).
SENSOR_GROUND_LEADS = {6, 7}
