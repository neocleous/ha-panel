# Info pages, parts checklist, tests, harness and plates for the page, from the
# instructions, harness list, parts list and print sheet of 2026-11-27, with log h's rulings.

def P(img, caption, legend=None):
    return {"img": img, "caption": caption, "legend": legend or {}}

def C(i, text, fig=""):
    return {"id": i, "text": text, "fig": fig}

TR = ["trial"]; AB = ["abs"]; TA = ["trial", "abs"]; ALL = ["trial", "abs", "service"]

info = [
 dict(id="start", title="Before you start", phase="Read once", routes=TA, blocks=[
  {"t": "list", "h": "How this page works", "items": [
    "Choose the way through at the top: PLA trial, ABS build or Service. Back and Next walk the steps of that way.",
    "Pictures: the unit so far in grey, this step's parts in orange, blue arrows for the way in, numbered dots for screws, letters for places. Tap a picture to enlarge it; swipe for the next.",
    "Amber boxes are trial checks: type the reading in its field. Readings, at the top, copies every reading as text to send to the Architect.",
    "Ticks and readings are kept in this browser on this device only. Clearing the browser's data clears them; another device does not see them."]},
  {"t": "list", "h": "Order of work", "routes": TR, "items": [
    "Arrival checks, as the parts come in.",
    "The PLA calibration plate: measure it and send the readings. A short session makes the calibrated trial files.",
    "Print the PLA trial from the calibrated files.",
    "Build the trial with steps 1 to 28 and take the trial checks. No cloth glued, magnets dry, no long powered runs.",
    "The boards, when they arrive."]},
  {"t": "list", "h": "Order of work", "routes": AB, "items": [
    "The ABS calibration plate, then the adhesion test.",
    "The black ABS set from its calibrated files. Measure the cloth before the screen plate and the shell print.",
    "Write down the ABS boxes' and the shell's depth along their print height as they come off (print order page).",
    "Build with steps 1 to 28: cloth glued, magnets glued. Repeat trial checks T9, T10, T11 and T21.",
    "Tests 5, 7, 11, 12 and 13 again on the ABS parts."]},
  {"t": "list", "h": "Settled", "items": [
    "Nothing is staked or glued where a screw or a clamp holds. The magnets, the cloth and the hot-melt plug in each box's wire hole are the only adhesives.",
    "Every M2 × 6 is a flat head: drive until the head seats or bears, and stop.",
    "The cap goes on before the display module.",
    "The door comes off by the fingertips in the two scallops in the base plate's rear border. Never pull at the grommet.",
    "Lift the unit by the shell or under the base plate, never by the slab.",
    "No weight in the unit: it tips backward under 2.78 to 2.87 N at the glass's top edge."]},
  {"t": "list", "h": "Words and numbers", "items": [
    "Left and right are as seen from the front. Through the door opening you look from the back: the left speaker is on your right hand.",
    "Along the normal: square to the screen. The screen leans back 12°.",
    "Lengths in mm. Room: from a screw's tip to the floor of its hole. Thread: screw length in the plastic or the insert.",
    "Screen plate: the black plate that carries the slab. Lands: the faces of the four posts behind the screen. Lip: the rim round the door opening. Stops: the four raised pads round each box's front inserts."]}]),
 dict(id="arrival", title="Arrival checks", phase="As the parts come in", routes=TR, blocks=[
  {"t": "checks", "h": "Check each as it arrives", "items": [
    C("a-cloth", "Cloth: measure its thickness before the ABS screen plate and shell print", "0.7 assumed. Thicker: stop and ask. The PLA trial is not affected"),
    C("a-usb", "ADT-Link USB-A to USB-C (S3K-T2G; S3J-T2G spare)", "USB-C end: the sleeve no more than 18.96 from the shell's centre line on the cable's side; 238 to 250 between the plugs' bodies. Else stop and report"),
    C("a-adapter", "90° USB-C adapter, \"Right Angle\"", "in the Pi's power socket, Pi as on the base plate: its socket end toward the left-speaker side. Else the right variant is a second order"),
    C("a-m2", "M2 × 6 flat head", "head 3.8 across, 1.2 high, 90°. Else report"),
    C("a-vise", "Pin vise and 1.6 drill", "chuck end over its first 16: 10.8 across or less; the drill 17 or more out of the chuck"),
    C("a-feeler", "Feeler blades as listed", "0.02 to 0.10 by 0.01; 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.75, 1.00"),
    C("a-ties", "Cable ties pass the anchor slot (3 wide) and the holder's top-plate slot"),
    C("a-3141", "Adafruit 3141 contacts fit your Dupont housings", "note the strip's colours in the leads page"),
    C("a-feet", "Four feet picked alike", "12.7 ± 0.5"),
    C("a-vem", "Light sensor's board is the one measured 1.54", "any other board is measured and goes to the Architect"),
    C("a-psu", "Main board's supply module: its pin row as placed", "else report")]},
  {"t": "trial", "id": "Arrival", "title": "Arrival readings for the Architect", "how": "Measure as each part arrives.", "back": "Any bow in the touch board; both radar figures; anything reported above.",
   "fields": [["ins", "Ruthex M3 × 5.7: diameter of its leading end", "mm"], ["tw", "Tweezers: closed tips' width over the first 40", "mm"],
              ["vise", "Pin vise: chuck end across over its first 16", "mm"], ["cloth", "Cloth thickness", "mm"],
              ["touch", "Touch board: largest gap under a straightedge", "mm"], ["radar", "Radar board thickness (model 3.0)", "mm"],
              ["ant", "Where the radar's antennas sit, against the steel screw", ""], ["col", "3141 colours chosen: ground, SDA, SCL", ""]]}]),
 dict(id="tools", title="Tools", phase="Have at hand", routes=TR, blocks=[
  {"t": "table", "h": "Tools and what for", "rows": [["Tool", "For", "Note"],
    ["TS101 with Ruthex insert tips", "36 inserts a set", "handle 98 long, 16.8 across"],
    ["TS101 normal tip, solder, cutters, stripper", "the leads", ""],
    ["Wera ball-end key 2.0 × 101", "every M3 × 8, the Pi's M2.5 × 6, the carrier's M2.5 × 5", "ball end to 25°. Short arm in the screw: the 101 arm is the lever"],
    ["Wera ball-end key 2.5 × 112", "the four display screws; the cap's reserve screws", "ball end to 25°"],
    ["Precision screwdriver, Phillips", "all 11 M2 × 6", "shaft 3.0; at the cradle under 4.2"],
    ["Pin vise with the 1.6 drill", "cradle, holder and hood pilots", "drill 17 or more out of the chuck"],
    ["2.0 drill", "its shank gauges the calibration's 2.0 hole", "on no record of stock: see the parts list"],
    ["4 mm drill, by hand", "boxes' floor-boss holes; shell post mouths; a plate hole that will not start", "its shank gauges the wire holes"],
    ["Long-nose pliers", "speaker left plug; the USB-C plug in service", "tips 2.5 thick, 3 wide at most, about 160 long"],
    ["Tweezers", "ribbon latches; speaker left home; microphone coils", "closed tips 4 across at most"],
    ["Feeler gauges", "steps 14, 18, 19; tests 5, 11, 12, 13", "stacks below"],
    ["Calipers with depth rod", "step 2; test 7; calibration; cloth; arrival", "200 long for test 13"],
    ["Hot-melt gun", "the wire-hole plugs (step 14)", ""],
    ["Support about 8 high, 1.0 kg mass, folded soft cloth, glass sheet, lamp, room thermometer", "steps 2, 4, 18; tests", "torque driver optional (steps 11, 23)"]]},
  {"t": "table", "h": "Feeler stacks", "rows": [["Size", "Stack"], ["0.9", "0.50 + 0.40"], ["1.1", "1.00 + 0.10"], ["1.2", "1.00 + 0.20"],
    ["1.3", "1.00 + 0.30"], ["1.4", "1.00 + 0.40"], ["1.5", "1.00 + 0.50"], ["1.6", "1.00 + 0.50 + 0.10"]]}]),
 dict(id="parts", title="Parts checklist", phase="Tick what you have", routes=TA, blocks=[{"t": "parts"}]),
 dict(id="print", title="Print order", phase="Printing", routes=TA, blocks=[
  {"t": "diagram", "k": "print"},
  {"t": "list", "h": "Every plate", "items": [
    "Print only from the calibrated files (names with _cal). From today's files only the calibration plates print.",
    "PLA trial: Textured PEI for every plate, no glue.",
    "ABS: glue on every plate. Textured PEI, except slab, cap and grommet on the Engineering plate. Support for ABS on the auxiliary nozzle from its external spool.",
    "Files: ~/Documents/HA_panel_renders/print_files_v91/ on the Mac. The print sheet holds every plate's settings.",
    "The ABS shell (P3a) is held until its file is released. Do not print it before.",
    "Printing waits for the replacement printer."]},
  {"t": "trial", "id": "Depths", "routes": AB, "title": "The ABS boxes' and shell's depth along their print height",
   "how": "As they come off the printer. The ABS calibration session uses them to stretch the ABS door along its print height before the door prints.",
   "back": "Send both with the readings.", "fields": [["box", "Box depth (model 51.22)", "mm"], ["shell", "Shell depth (model 70.30)", "mm"]]}]),
 dict(id="calib", title="Calibration plate", phase="Printing", routes=TA, blocks=[
  {"t": "list", "h": "Before you print", "items": ["Mark the frame's X side with a pen.", "No brim. Let it cool on the printer before taking it off.",
    "You need: one Ruthex M3 × 5.7 (spent); one M2 × 6 and one M3 × 8 (used again); the shanks of the 2.0 and 4.0 drills; the 1.6 drill in the pin vise."]},
  {"t": "table", "h": "The second block's marks", "rows": [["Mark", "What"], ["P16a, P16b", "two upright pilots 1.6 across, 7.0 deep: the two holes at the block's left end"],
    ["P16L", "a lying pilot 1.6, 7.0 deep, opening in the long face toward the frame's front"], ["P27L", "a lying pilot 2.7, 9.0 deep, opening in the other long face"],
    ["H20", "a standing hole 2.0, through from the first layer: the small round hole near the middle"], ["H40W", "an insert hole 4.0, 6.5 deep, 1.6 of wall to the block's right end"]]},
  {"t": "list", "h": "Measure, and the pass figures", "ol": True, "items": [
    "Frame: outside and inside length, in X and in Y, at mid-height, away from the corners.", "Tower height.", "Tower width in X, at the first layer and at 15.",
    "Old block: the 4.0 shank to the bottom of both 4.0 holes by hand; an M3 passes both 3.4 holes; an M3 into the lug's 2.7 pilot and out, three times: no crack line.",
    "P16a, P16b: an M2 × 6 to its head and out, three times each. Pass: it tightens on its head each time, no crack line.",
    "P16L: the same. If it will not start by hand, one light pass with the 1.6 drill first, and say so.",
    "P27L: an M3 × 8 to its head and out, three times. Pass: firm, no crack line. Say if it needed a drill.",
    "H20: the 2.0 shank passes through by hand from the first-layer side.",
    "H40W: set an insert flush, drive an M3 × 8 into it. Pass: no crack line, no bulge on the 1.6 wall, the screw holds. A split wall goes to the Architect."]},
  {"t": "trial", "id": "T1", "abs": True, "title": "Calibration plate", "how": "Send these and nothing else; the session works out the numbers.",
   "back": "The 1.6 wall splits (item 9).", "fields": [["xo", "Frame X outside", "mm"], ["xi", "Frame X inside", "mm"], ["yo", "Frame Y outside", "mm"], ["yi", "Frame Y inside", "mm"],
    ["th", "Tower height", "mm"], ["w0", "Tower width X, first layer", "mm"], ["w15", "Tower width X, at 15", "mm"],
    ["i4", "Item 4 old block: yes/no", ""], ["i5", "Item 5 P16a, P16b: yes/no", ""], ["i6", "Item 6 P16L: yes/no, needed a pass?", ""],
    ["i7", "Item 7 P27L: yes/no, needed a pass? which drill", ""], ["i8", "Item 8 H20: yes/no", ""], ["i9", "Item 9 H40W: yes/no", ""]]},
  {"t": "trial", "id": "T2", "routes": AB, "title": "Adhesion test: the grille trees and the seat bars",
   "how": "Break the two trees off the grilles from inside; see the grilles' holes clear. Look at the three seat bars in each driver bay; pare any support mark flush.",
   "back": "A tree's foot does not come off a grille clean, or tears a web: before the ABS shell prints.", "fields": [["clean", "Clean? yes/no, and what you saw", ""]]}]),
 dict(id="after", title="After printing", phase="Printing", routes=TA, blocks=[
  {"t": "p", "text": "On every part: take the support out. No support may stay in any hole a part enters."},
  {"t": "plate", "title": "Base plate (P1a)", "pic": P("ap_p1a_base_plate", "The underside.", {"c": "a counterbore: its disc comes out"}),
   "items": ["ABS: peel the white ring off the rounded rim and note how it leaves the face.", "The disc in each of the 8 counterbores comes out.",
             "Check it flat on glass before anything is screwed to it: a 0.2 feeler does not pass under it anywhere."]},
  {"t": "plate", "title": "Speaker boxes (P1b)", "pic": P("ap_p1b_boxes", "Both boxes from behind.", {"W": "a wire hole", "B": "left box's lower screw bore", "U": "the plug pocket"}),
   "items": ["Each chamber's support out through the driver opening. Then shake the box: nothing rattles.",
             "The tree in the plug pocket (left box) comes out sideways, toward the middle of the unit. Pare any mark on the pocket's end wall flush, both faces.",
             "ABS: then look down the left box's lower screw bore from the rear face: clear to its seat.",
             "PLA: break each wire hole's trunk off at the rear face, lift the chamber's tree out, pass the 4.0 drill's shank through each wire hole.",
             "Clips: nothing."]},
  {"t": "plate", "title": "Carrier, cradle, hood (P2)", "pic": P("ap_p2_carrier_cradle", "", {"N": "carrier pilots: not reamed", "R": "cradle pilots: reamed in step 3"}),
   "items": ["Carrier: its two pilots are not reamed.", "Cradle: its two pilots are reamed in step 3.", "Hood: nothing."]},
  {"t": "plate", "title": "Holder and clamps (P7)", "pic": P("ap_p7_holder_clamps", "The radar holder.", {"H": "a pilot: one light pass in step 3"}),
   "items": ["Holder: lift its support out to the rear in one piece.", "Clamps: nothing."]},
  {"t": "plate", "title": "Screen plate (P3b)", "pic": P("ap_p3b_screen_plate", "The back.", {"W": "a raised border strip"}),
   "items": ["ABS: peel the white interface off the back of the raised border strips.",
             "Check it flat on glass before test 11: on its island, a 0.1 feeler does not pass under the island's edge."]},
  {"t": "plate", "title": "Shell (P3a)", "pic": P("ap_p3a_shell", "", {"G": "a grille: its tree breaks off from inside (ABS)", "P": "the hood's pilot: step 3"}),
   "items": ["ABS, tried first on the adhesion test: break the two trees off the grilles from inside; the grilles' holes clear. Pare any support mark on the three seat bars in each driver bay flush.",
             "Trim the brim off the chin's rounded edges.", "No support left in the four post holes; their mouths are reamed in step 2.",
             "The old radar pocket stays as printed.", "If the ABS shell is issued as sliced: pick the white skin out of the four upper lip pockets' mouths before the magnets."]},
  {"t": "plate", "title": "Slab, cap, grommet (P5, P4a, P4b)", "items": ["Slab, ABS: peel all the white support off the glass seat and the roll's edge.",
             "Cap: nothing; its pilots are not reamed.", "Grommet, ABS: peel the white tops off."]},
  {"t": "plate", "title": "Door (P6)", "pic": P("ap_p6_door", "", {"F": "the foot: trim the brim flush"}),
   "items": ["ABS: peel the white interface off the cut-out's top and the baffle's bottom.", "Trim the brim off the door's foot flush before fitting.",
             "Its pilots and its two peg holes are not reamed."]}]),
 dict(id="leads", title="The leads", phase="Harness", routes=ALL, blocks=[{"t": "diagram", "k": "harness"}, {"t": "harness"}]),
 dict(id="tests", title="Tests", phase="After the build", routes=TA, blocks=[{"t": "tests"}]),
 dict(id="svc", title="Service: before anything", phase="Service", routes=["service"], blocks=[
  {"t": "list", "h": "Every time", "items": [
    "Door off first: unit on its face on the folded cloth; 4 × M3 × 8 from below, counted; fingertips in the two scallops. Never at the grommet.",
    "Before any plug comes off: Pi power first.",
    "When the 20 V plug goes back: onto its marked socket, the middle of the three 2-way sockets.",
    "Every plug between the plate unit and the rest is off before they part: no exception."]},
  {"t": "p", "text": "Pick the job from the Steps list, or walk them with Next. The leads and the plug order follow at the end."}]),
 dict(id="plugs", title="Plug order on the main board", phase="Harness", routes=ALL, blocks=[{"t": "diagram", "k": "plugs"}]),
]
for i in info:
    i["kind"] = "info"

# where each info page sits on each way through
order = {
 "trial": ["start", "arrival", "tools", "parts", "print", "calib", "after", "leads", "STEPS", "plugs", "tests"],
 "abs": ["start", "parts", "print", "calib", "after", "leads", "STEPS", "plugs", "tests"],
 "service": ["svc", "SERVICE", "leads", "plugs"],
}
info = {"pages": info, "order": order}

plates = {
 "trial": [
  ["gate", "PLA calibration plate", "44.7", "50.3", "28.51 g", "Measure; send the readings. A short session makes the _cal files."],
  ["P1a", "base plate", "125.4", "131.0", "31.62 g", ""], ["P1b", "both boxes, both clips", "178.1", "183.7", "78.12 g", "released with the _cal files, with its after-print line"],
  ["P2", "carrier, cradle, hood", "35.9", "41.6", "16.74 g", ""], ["P7", "both clamps, radar holder", "22.9", "28.5", "4.34 g", ""],
  ["P3b", "screen plate", "75.3", "80.9", "82.95 g", ""], ["P3a", "shell, chin down", "455.7", "461.3", "170.62 g", "one expected warning: 2 overhang regions (the chin's top band)"],
  ["P5", "slab, glass side down", "187.7", "193.3", "36.38 g", ""], ["P4a", "cap, top face down", "46.9", "52.5", "9.66 g", ""],
  ["P4b", "grommet", "20.0", "25.7", "1.72 g", ""], ["P6", "door, standing", "125.2", "130.8", "52.53 g", ""],
  ["end", "Build the trial; take the trial checks", "", "", "", ""]],
 "abs": [
  ["gate", "ABS calibration plate", "60.5", "78.1", "22.81 g", "Measure; send the readings."],
  ["gate", "Adhesion test: the shell's first 8.0", "113.7", "148.4", "27.63 g + 2.17 g", "Try the shell's after-print lines on it first. A tree that does not come off a grille clean goes to the Architect."],
  ["P1a", "base plate", "141.4", "174.2", "27.36 g + 3.21 g", ""], ["P1b", "both boxes, both clips", "214.6", "289.7", "80.72 g + 4.20 g", "write down the boxes' depth as they come off"],
  ["P2", "carrier, cradle, hood", "41.8", "59.4", "13.40 g", ""], ["P7", "both clamps, radar holder", "32.9", "83.8", "11.46 g + 1.74 g", ""],
  ["P3b", "screen plate", "89.8", "110.1", "67.05 g + 1.38 g", "measure the cloth first"], ["P3a", "shell (held until released)", "627.4", "783.9", "211.58 g + 19.96 g", "measure the cloth first; write down its depth as it comes off"],
  ["P5", "slab (Engineering plate)", "197.7", "223.0", "28.55 g + 4.23 g", ""], ["P4a", "cap (Engineering plate)", "48.1", "65.7", "7.73 g", ""],
  ["P4b", "grommet (Engineering plate)", "23.8", "74.3", "8.30 g + 0.47 g", ""], ["P6", "door", "198.0", "234.4", "48.24 g + 0.59 g", "after the session has used the depths"],
  ["end", "Build the ABS unit", "", "", "", ""]]}

# leads: [no, name, from, to, free, spare, notes]
harness = [
 [1, "20 V", "Inlet board", "J1, the middle 2-way", "90", "16, a bow", "Marked plug and socket. Plugged first."],
 [2, "Speaker left", "Left driver, connector up", "J8", "about 135 (35 in the box)", "about 11", "Hot-melt plug in the wire hole. Through the USB roll. Pliers on and off."],
 [3, "Speaker right", "Right driver, connector up", "J9", "about 127 (35 in the box)", "a bow", "Hot-melt plug in the wire hole."],
 [4, "Radar", "Radar board, tied on the holder", "J5", "118", "15: 10 behind the radar, 5 free", "Cut from a 152 half jumper. Marked. Across over the Pi."],
 [5, "Touch", "Touch board HOST pads", "J6", "87", "15", "Marked: it reaches the radar's socket."],
 [6, "BME680", "Sensor in its tray", "J10, 1 × 4", "93", "15", "Foam plug round it in the slot. Marked: no key."],
 [7, "VEML6030", "Sensor in the cap", "J11, 1 × 4", "116", "15", "Marked: no key."],
 [8, "Pi wires, 3", "J3 pads", "Pi pins 1-3-5", "70", "12", "First notch."],
 [9, "Pi wires, 6", "J3 pads", "Pi pins 7–16", "70", "12", "First notch, side by side."],
 [10, "Pi wires, 4", "J4 pads", "Pi pins 35–40", "70", "12", "Second notch."],
 [11, "Display power", "Display's 4-pin header", "Pi pins 2-4-6", "180", "14", "Laid under the main board. Pins 2 and 4 are 5 V."],
 [12, "DSI ribbon", "Display, 15-way", "Pi, 22-way", "200 stock", "arch over the Pi's connector", "Three creases at the bench; a spare."],
 [13, "Mic left", "Left strip in the cap", "ReSpeaker", "230", "about 160, a coil", "Coil behind the screen plate."],
 [14, "Mic right", "Right strip in the cap", "ReSpeaker", "230", "about 164, a coil", "As the left."],
 [15, "Pi power", "J2", "Pi USB-C via 90° adapter", "200", "135, one lap 40 across", "Plugged last; first out."],
 [16, "ReSpeaker USB", "Pi USB-A, lower blue port", "ReSpeaker USB-C", "238 to 250", "108 to 120, a roll", "Fold 2 at 6.6, fold 1 at 15.0. Roll 0.93 from the shell."],
]

tests = [
 [1, "microSD card behind the right box", "Comes out and goes in with a flat finger or tweezers in a channel 18 wide, 13 high, Pi and cooler in place.", ""],
 [2, "DSI ribbon into the Pi with the real cooler on", "6.3 of the ribbon's 11.5 free above the connector; the wide part stays above the cooler; both ends of the latch can be worked with tweezers.", ""],
 [3, "USB plug at the Pi", "The hand that sends the cable toward the door; the plug seats before its sleeve meets the Ethernet jack; tape on its back; fold 2 made; the left box slides home with nothing bearing on plug or cable.", ""],
 [4, "Only on the cap's way back", "The 2.0 ball end holds at 22 to 23° in the button heads without camming out; if not, the cap-head screws and the 2.5 key.", ""],
 [5, "Shell onto the plate unit (step 19)", "Held against the boxes' backs, it goes down without catching and centres itself; slides back and stops. At home, the largest feeler stack at each box's back (model 1.60): the Architect judges. Box-top screws start by hand; the rim even. Then again with a strip of cloth turned under one side wall.", "abs"],
 [6, "ReSpeaker's USB cable", "USB-C seats beside the cut-back edge; fold 1 at least 1 off the lip; the module rides in with the slack drawn back; the spare rolls without a kink, the left speaker lead through it; the cable slides in the tie; the plug pulled and put back with the pliers, shell seated.", ""],
 [7, "Inserts: screen plate's two, shell's four", "Posts: flush with the land or the peg's end, or up to 0.3 below, never proud; the plate drops onto both pegs by its own weight (else file the peg tips flat). Plate: flush with the front face and 1.66 to 1.84 out of the back (mean of two edges). An M3 × 8 starts by hand in all six.", "abs"],
 [8, "The spare lengths by hand", "Each microphone coil goes over the board's top edge with tweezers and stays behind the plate; the Pi power lap of 40 without strain; the display's power lead flat under the board.", ""],
 [9, "Each box holds air on the driver's foam", "Wire hole plugged: the cone pushed in and held does not creep further in, and comes straight back. Nothing is pressed onto the cone's middle: it is thin aluminium and dents. A look at the trial, no figure: write down what you see.", ""],
 [10, "DSI ribbon's way, your own ribbon", "Contacts on the same face at both ends; where the stiff end piece ends; three creases flat without cracking; on edge below the USB plug, beside the left box, the arch, into the Pi without a kink; the left speaker plug on with the pliers.", ""],
 [11, "The gap round the screen plate", "Plate screws firm, by feeler, three points along each edge. Top and bottom: slit 0.1 to 0.3; with the module in, the gap behind the slab 0.9 to 1.1. Each side, before cloth: 1.2 slides in as far as the plate's step, 1.6 stops before. Sides differ by 0.2 or more: loosen, push toward the side that reads less, tighten, read again. These bands are set again after the calibration.", "abs"],
 [12, "The screen plate's give", "Door off, unit on its back on the frame's legs, top supported, every screw in. Steel ruler on edge along the glass's top edge, 1.0 kg below the ruler's middle: the gap grows by 0.40 or less. Along the bottom edge: 0.35 or less. Beyond that the joint goes to the Architect.", "abs"],
 [13, "The open shell under stretched cloth", "Cloth stretched and taped, no adhesive: the plate drops onto both pegs, its screws start by hand, slit 0.1 to 0.3 at the top band and the rail; top posts' and pegs' spacing change by 0.2 or less (calipers 200). If it fails, the plate goes on as a brace while the cloth is glued.", "abs"],
 ["T20", "The hood's way out with the main board in", "Trial check: one screw at the ear; lift 3.5 off its pins; 56 or more toward the middle before drawing it back.", ""],
 ["T23", "The band at the screen's bottom edge", "Trial check: the gap there against the gap at the top edge, by test 11's method. Back to the Architect if the bottom reads about 0.2 wider. Judge it on the ABS shell.", "abs"],
 ["Mic", "The microphone gaskets' seal", "After the trial, with the cap apart: an unbroken print of the cap's pad round each port on each gasket. Then, on the built unit, compare the two microphones' levels.", ""],
 ["BME", "BME680 against a room thermometer", "In the ABS unit, Pi idle and unit warm. If they differ, set an offset in the BME680's configuration.", "absonly"],
 ["WiFi", "The Pi's Wi-Fi", "Write down the signal on the bare base plate and in the built unit. No pass figure.", ""],
]

# parts checklist: sections of [id, item, per unit, note]
parts = [
 ["Lines for you (nothing ordered)", [
  ["p-ins", "Ruthex M3 × 5.7: need 66 for two sets and both calibration plates", "", "record 64: short 2. Check the stock."],
  ["p-d20", "Drill 2.0 (its shank gauges the calibration's H20)", "", "on no record of stock"],
  ["p-eva", "0.5 EVA foam tape (AliExpress order 2)", "", "last recorded in a basket on 2026-11-16"],
  ["p-s77", "3M Super 77 spray adhesive (digitec)", "", "last recorded in a basket on 2026-11-16"],
  ["p-uhu", "UHU Kontakt, 120 g (digitec)", "", "last recorded in a basket on 2026-11-16"]]],
 ["Printed parts, 17 a set", [
  ["p-bp", "Base plate (P1a)", "1", ""], ["p-box", "Left and right speaker boxes (P1b)", "2", ""], ["p-clip", "Touch clip (P1b), printed twice", "2", ""],
  ["p-p2", "Carrier, cradle, BME680 hood (P2)", "3", ""], ["p-p7", "Microphone clamps left and right, radar holder (P7)", "3", ""],
  ["p-sp", "Screen plate (P3b)", "1", ""], ["p-sh", "Shell (P3a)", "1", ""], ["p-slab", "Slab (P5)", "1", ""], ["p-cap", "Cap (P4a)", "1", ""],
  ["p-gr", "USB-C grommet (P4b)", "1", ""], ["p-door", "Door (P6)", "1", ""]]],
 ["Filament", [
  ["p-pla", "Bambu PLA Basic, black", "513 g", "one 1 kg spool"], ["p-abs", "Bambu ABS, black", "555 g", "one 1 kg spool"],
  ["p-sup", "Bambu Support for ABS", "38 g", ""], ["p-tpu", "TPU 95A, 1.75: one length for the spline", "", "in stock"]]],
 ["Screws", [
  ["p-m38", "M3 × 8 button head, ISO 7380", "35", "55 in stock"], ["p-m26", "M2 × 6 flat head, Phillips, for plastic", "11", "100 in stock"],
  ["p-m256", "M2.5 × 6 cap head (Pi)", "4", ""], ["p-m35", "M3 × 5 cap head (display)", "4", ""], ["p-m255", "M2.5 × 5 cap head (carrier)", "4", ""],
  ["p-m38c", "M3 × 8 cap head, reserve for the cap", "4", "only on the way back"]]],
 ["Inserts, per set", [["p-i3", "Ruthex M3 × 5.7", "32", "see the line above"], ["p-i25", "Ruthex M2.5", "4", "8 in stock"]]],
 ["Bought parts", [
  ["p-pi", "Raspberry Pi 5, Active Cooler, microSD", "1", ""], ["p-lcd", "Waveshare 8\" DSI LCD (C), 4-pin power lead", "1", ""],
  ["p-resp", "Seeed ReSpeaker Lite", "1", ""], ["p-5807", "Adafruit 5807 inlet board", "1 + spare", ""], ["p-drv", "Dayton Audio DMA45-4", "2 + spare", ""],
  ["p-radar", "Hi-Link HLK-LD2410C", "1", ""], ["p-bme", "CJMCU-680 (BME680)", "1", ""], ["p-veml", "VEML6030 board, the one measured 1.54", "1", ""],
  ["p-pcb", "Main board rev 3.3, touch board rev D, 2 microphone strips, stencil", "1 each", ""], ["p-bom", "Main board's parts", "as its BOM", ""],
  ["p-mag2", "Magnets N52 Ø8 × 2", "10 + spare", ""], ["p-mag1", "Magnets N52 Ø8 × 1", "10", ""], ["p-feet", "3M SJ-5012 feet, picked alike", "4", ""],
  ["p-cloth", "Cloth, NO.3 Knit, colour 13, 160 × 45 cm", "1 + spare", ""]]],
 ["Leads and stock", [
  ["p-xh", "JST ASXHSXH22K305 jumpers (halved)", "7", "10"], ["p-xhp2", "JST XHP-2 housings", "3", ""], ["p-xhp4", "JST XHP-4 housings", "2", ""],
  ["p-3141", "Adafruit 3141 strip", "23 wires", ""], ["p-sr", "JST A05SR05SR30K305B", "2", ""], ["p-dup", "Dupont housings 1 × 3, 2 × 5, 2 × 3, two 1 × 4", "", ""],
  ["p-sull", "Sullins PRPC004SAAN-RC headers", "2", ""], ["p-dsi", "Waveshare 200 mm DSI ribbon", "1 + spare", ""],
  ["p-adt", "ADT-Link S3K-T2G (S3J-T2G spare)", "1", ""], ["p-usbc", "USB-C to USB-C 5 A, 0.2 m", "1", ""], ["p-90", "CableCreation 90° adapter, \"Right Angle\"", "1", ""]]],
 ["Consumables", [
  ["p-tie", "Cable ties 2.5 × 150", "4", ""], ["p-cr1", "1 mm CR foam tape (gaskets)", "", ""], ["p-cr2", "2 mm CR foam tape (BME680 foam, the lead's plug)", "", ""],
  ["p-hm", "Hot-melt sticks", "", ""], ["p-ca", "Cyanoacrylate", "", "ABS set only"], ["p-tape", "Polyimide, ordinary and masking tape", "", ""],
  ["p-hs", "Heat-shrink", "", ""], ["p-paste", "Solder; paste Sn63/Pb37 (check its date)", "", ""], ["p-glue", "Glue for the ABS plates", "", ""]]],
]
