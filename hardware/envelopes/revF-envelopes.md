# E0 envelope specification — rev F, issue 4 (2026-11-02, GPIO link option 1)

Checkpoint 2 deliverable of brief E0, reworked for the integrated-voice architecture (decision 2026-11-01 16:06, `claude/decision-voice-architecture-2026-11-01.md`) and the decisions of 2026-11-02: H1 pre-made leads only, H2a Pi powered through its own USB-C, D2a, D4a, and **GPIO link option 1** (Daniel, 2026-11-02 23:00: two custom Dupont plugs instead of the 40-pin ribbon, screen powered from the Pi; supersedes L1a). It is the handover for A1 (design) and B1 (electronics).

Sources were seen 2026-11-01/02. "Not verified" means no published source was found; those items are listed under "Measure" at the end.

## Conventions
- Units are mm.
- Each board has its own **board frame**: the origin is the lower-left corner seen from the stated face, X points right, Y points up, and Z is normal to that face.
- Placement in world coordinates stays A1's job, from handover §5 (frames per brief: +x = viewer's left, XC = −2.55).
- **Confidence levels:**
  - **D** = datasheet, official drawing or distributor listing.
  - **F** = manufacturer CAD file (KiCad, Eagle or STEP) parsed directly.
  - **S** = scaled from a drawing (±0.5 mm).
  - **P** = photo-estimated.
  - **E** = estimate or E0 design rule.

## What changed in issue 2
- **Removed:** VOICEPE_* (Voice PE retired), AMP_env (AA-AB32472 dropped), MUTE_sw (software mute only), DIST_env (replaced by MAIN_env).
- **Added:**
  - RESPEAKER_pcb, from Seeed's STEP model;
  - MAIN_env, a reserved main-board envelope;
  - a Leads section, since every lead is now a pre-made cable (H1).
- **Updated:**
  - MIC_strip: tuning parts on the back face; the cable now ends at the ReSpeaker's vacated mic pads.
  - PD_env: standalone at the inlet grommet with a 2-wire 20 V pigtail (architect log D13, 2026-11-02).
- **Issue 3 (block 3, 2026-11-02):**
  - MAIN_env default fixed (NID upright, 90 × 50, hole pattern) with candidate positions A/B against K5/K7;
  - 5807 inlet outline; K11 slack 50 mm;
  - details in `claude/E0-power-budget-2026-11-02.md` §6.
  - PI5_board: powered through its own USB-C; GPIO over a 40-pin ribbon.
  - LD2410C_env, TOUCH, SPK, BME680/VEML: lead exits added.
- **Issue 4 (Daniel, 2026-11-02 23:00, option 1):**
  - The 40-pin ribbon is gone. The GPIO link is two custom Dupont plugs on the Pi (A: 2 × 8 on pins 1–16; B: 2 × 3 on pins 35–40), built from 13 pre-crimped F-F leads in Daniel's own housings (PI5_board).
  - The LCD is powered from the Pi's pins 2/6, as in the current build. Its lead's 5 V and GND terminals are re-housed in plug A.
  - MAIN_env loses the 2 × 20 box header and the 1 × 4 LCD header; it gets a 13-position GPIO landing (headers or solder pads, B1).
  - Leads table, open issues 3/6/12/15 and Measure 2/3 updated. Note for the Architect: `claude/E0-power-budget-2026-11-02.md` §9.

## Summary
| Body | Outline L × W × T | Top-side max | Bottom-side max | Holes | Mass g | Conf. |
|---|---|---|---|---|---|---|
| PI5_board | 85.0 × 56.0 × PCB (1.6 per rev D, not on drawing) | USB/RJ45 stack, not on drawing | microSD, not on drawing | 4 × Ø2.7, 58 × 49 | not verified | D/S |
| PI5_cooler | 63.5 × 42.5 footprint | ≤ 13.7 above PCB top | — | 2 push pins | not verified | D/S |
| RESPEAKER_pcb | 82.02 × 34.01 × 1.51 (83.60 with the jack) | 6.83 (J2, unused) | 2.59; ≥ 3.0 at the reworked mic pads (E) | 2 × Ø2.2 | not verified | F |
| MAIN_env | reserved: ≈ 90 × 50 (NID upright) or ≈ 90 × 65 (NID flat) | ≤ 30 / ≤ 20 | ≤ 3.5 | 4 × Ø2.7 (suggested) | ≈ 58–62 | E |
| PD_env | PCB 20.32 × 23.495; 24.5 × 20.2 × 4.9 overall | USB-C (4.9 overall) | — | 2 × Ø2.5 plated | 2.2 | F/D |
| BUCK_env | 50.8 × 27.5 × 12 max (SIP-13) | — | pins 4.5 | none | 35 | D |
| MIC_strip_L/R | 30 × 6 × 0.8 (reserved) | front: mic LGA 1.0 | back: SR header 4.25 (4.9 mated) | 2 heat-stake pins (A1) | < 1 | D/E |
| LD2410C_env | 22 × 16 | not published | not published | none (5 pads 2.54) | not verified | D/E |
| BME680_env | CJMCU-680, not published | ~2 (SOT-23) | — | 2 | < 2 | P |
| VEML_env | VEML6030 board, not published | ~1 | — | 2 | < 2 | P |
| TOUCH_pcb | 90 × 44 × 1.6 after trim (100 as built) | flat (electrodes only) | — | none | ≈ 11 (FR-4 calc.) | F |
| TOUCH_components | back side | — | SOIC-14 1.75 max + wire joints | — | — | F |
| SPK_driver_L/R | frame 46.0 × 46.0, overall 29.1 | flange 3.0 + surround | basket Ø40 × 26.1 | 4 × Ø3.3 on Ø50.2 | 68 | D |
| USBC_port | 5807 receptacle, protrudes 1.0 beyond its PCB edge | — | — | — | — | F/D |
| SJ5012 | Ø12.70 × 3.50 | — | — | — | < 1 | D |

Leads are listed in their own section below.

---

## PI5_board — Raspberry Pi 5
Source: Raspberry Pi drawing RP-008347-DS-1 (https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-mechanical-drawing.pdf, which redirects to pip-assets.raspberrypi.com). Frame: top view as drawn — GPIO along the top long edge, USB/RJ45 on the right short edge, USB-C/micro-HDMI on the bottom long edge.

**Outline and holes**
- Outline 85.0 × 56.0 mm. PCB thickness isn't on the drawing; rev D and the handover use 1.6.
- Mounting holes: 4 × Ø2.7 (M2.5 clearance) at (3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5). **D**

**Connectors**
- **GPIO 2 × 20:** centre at (32.5, 52.5), 29 mm from the left hole column. **D**
  - By Raspberry Pi convention, pin 1 is at the left end on the inner row, and the 5 V pins 2/4 are on the edge row at the left end.
  - Derived pin columns (2.54 pitch about the centre): pins 1/2 at X ≈ 8.4, pins 39/40 at X ≈ 56.6.
  - **Use — option 1 (Daniel, 2026-11-02):** two custom Dupont plugs, built from pre-crimped F-F leads pushed into Daniel's own housings. No ribbon. The Pi is still not fed through its header; pin 2 only feeds the LCD from the Pi.

| Plug | Housing (X span, derived) | Pi pin | Signal (BCM) | Other end |
|---|---|---|---|---|
| A | 2 × 8 on pins 1–16 (X ≈ 7.1–27.4) | 1 | 3V3 | main board: TAS5756M DVDD/AVDD/CPVDD, 3.3 V sensor branch |
| | | 2 | 5 V | LCD lead's own 5 V terminal (re-housed) |
| | | 3 | GPIO2 SDA1 | main board I²C (TAS5756M, touch board, BME680, VEML6030) |
| | | 5 | GPIO3 SCL1 | main board I²C |
| | | 6 | GND | LCD lead's own GND terminal (re-housed) |
| | | 8 | GPIO14 TXD0 | main board → LD2410C RX |
| | | 9 | GND | main board |
| | | 10 | GPIO15 RXD0 | main board ← LD2410C TX |
| | | 12 | GPIO18 PCM_CLK (BCLK) | main board, TAS5756M |
| | | 14 | GND | main board; twist with pin 12's lead (E) |
| | | 15 | GPIO22 | main board, amp mute (`rpi-digiampplus`) |
| | | 4, 7, 11, 13, 16 | — | empty |
| B | 2 × 3 on pins 35–40 (X ≈ 50.3–57.9) | 35 | GPIO19 PCM_FS (LRCLK) | main board |
| | | 38 | GPIO20 PCM_DIN | main board (D4a Option B) |
| | | 39 | GND | main board |
| | | 40 | GPIO21 PCM_DOUT | main board, TAS5756M SDIN |
| | | 36, 37 | — | empty |

  - **13 leads** run to the main board: 9 from plug A and 4 from plug B. The LCD's two terminals are its own lead's.
  - **Orientation:** neither the Pi's header nor the housings are keyed. Daniel marks each plug (decided 2026-11-02).
    - Each plug sits flush with one end of the header, so the header end fixes its position along the row.
    - A plug A turned 180° would put the LCD's 5 V on pin 15 (GPIO22). That is the case the mark guards against.
  - **Housing sizes** come from Daniel's stock. If it has no 2 × 8, two 2 × 4 on pins 1–8 and 9–16 work the same way, with two marks.
  - **LCD SDA/SCL terminals: unused.** The overlay's default runs the panel's touch and backlight on the DSI-side I²C; the lead's SDA/SCL are only for the `i2c1` override "with jumper wires from GPIOs 2&3" (raspberrypi/firmware `boot/overlays/README`, `vc4-kms-dsi-waveshare-panel`, seen 2026-11-01). Daniel's panel exposes its backlight as `11-0045`, on bus 11, not bus 1 (handoff 2026-08-23). Insulate both terminals and tie them back.
  - Housings next to the cooler: see open issue 3.
- **Bottom edge:** USB-C power at X 11.2, micro-HDMI 0 at X 25.8, micro-HDMI 1 at X 39.2 (connector centres). **D**
  - **The USB-C is now the power input (H2a):** a 0.2 m USB-C cable from the main board plugs in here.
  - Plug keep-out beyond the bottom edge: overmold not measured. Reserve ≥ 30 for a straight plug and its bend (E).
  - **Conflict with K10 (open issue 14):** K10 turns this edge to the back (y −58). With the cooler up, the USB-C lands at world x ≈ −33.8. There the inner back wall is ≈ 22–23 behind the edge at floor level (interpolated from the rev E half-widths). A straight plug doesn't fit; a right-angle plug at the Pi end probably does.
- **Right edge:** USB stacks centred at Y 47.0 and Y 29.1, RJ45 at Y 10.2. All overhang the right edge by 3.0. **D**
  - One USB-A port takes the ReSpeaker's USB cable (owned A-to-C; A1 sets length and plug angle).
  - **Conflict with the rev E chambers (open issue 13):**
    - With K10's orientation and the cooler up, this edge is at world x 40 (rev E §5: x −45…40). The USB stacks sit at world y ≈ −11 and −29, inside the chamber zone (y > −38).
    - The chamber partition's inner face is at XC + 45.3 = 42.75, only 2.75 from the edge, while the stacks overhang 3.0.
    - So there's no room for a USB-A plug as planned.
- **MIPI CAM/DISP 0/1** (22-pin, 0.5 mm FPC, for the DSI cable): two vertical connectors between micro-HDMI 1 and the RJ45.
  - Centres X ≈ 48.6 and ≈ 54.4, spanning Y ≈ 0.5–16. **S**
  - FPC exit direction is not on the drawing; check on the board.
- **Cooler push-pin holes:** Ø3 at ≈ (60.7, 47.2) and a second hole near (3.5, 11.0). **S** These match the Active Cooler pin spacing of 57.2 × 36.2.

**Not on the drawing:** microSD position (underside, left short edge), USB/RJ45 stack height, header height, mass.

## PI5_cooler — Raspberry Pi Active Cooler
Source: Raspberry Pi drawing "Active Cooler for Raspberry Pi 5" (2023-10-19), hosted at https://media.elv.com/file/253864_bauzeichnung.pdf.
- **Footprint:** 63.50 × 42.50. **D**
- **Height:** 13.70 overall, measured from the top of the push-pin caps to the pin tip below the base. **D**
  - Installed height above the PCB is therefore **< 13.7**; the drawing doesn't give the installed value.
  - With the PCB top at z 12.1, the cooler top is at **z ≤ 25.8**. Architect log K7 assumed ≈ z 31.
- **Position on the board** (derived from the pin spacing, **S**):
  - Cooler bounding box X 0.7–64.2, Y 7.9–50.4.
  - 30 × 30 fan at X 27.4–57.4, Y 19.3–50.4. Inlet Ø ≈ 21.5, hub ≈ (41.9, 34.9).
  - Fin block X 0.7–27.4.
- **Airflow:** in through the top of the fan, out through the fin block (−X side and top).
- **Keep-out:** architect log K7 governs: ≥ 10 mm clear above the cooler fan, and nothing over the fan's intake footprint within 10 mm. Issue 1's E0 rule (≥ 5) is withdrawn. With the cooler top at z ≤ 25.8, anything above the fan starts at z ≥ 35.8.
- **GPIO plugs A/B:** the cooler's edge (Y 50.4, S) is ≈ 0.8 from the header's inner pin row (Y 51.23). Plug A sits beside the fin block (X 0.7–27.4), plug B beside the fan (X 27.4–57.4). See open issue 3.

## RESPEAKER_pcb — Seeed ReSpeaker Lite (board only, no XIAO)
Source: Seeed STEP model `ReSpeakerLitev1.1.step` (https://files.seeedstudio.com/wiki/respeakerv3/ReSpeakerLitev1.1.step), parsed with OCP: solid bounding boxes, and cylindrical faces in the PCB solid for the holes. **F.** Part names are from the STEP where it gives them; others are marked.

**Frame:** viewed from the **connector side** (STEP +Z: J2, 3.5 mm jack, USB-C, empty XIAO footprint). The origin is at the PCB's lower-left corner, with X along the long edge; the jack, J2 and USB-C sit at the right end. **The mic side is the underside** (−Z).

**Outline and holes**
- **PCB:** 82.02 × 34.01 × 1.51, corners R1.27.
  - Seeed's listing gives 35 × 86. Measure on arrival (open issue 1).
- **Mounting holes:** **2 × Ø2.2** at (2.49, 31.58) and (60.20, 2.66), diagonal to each other. Ø2.2 clears M2, not M2.5 (open issue 5).
- **Jack locating pegs:** 2 × Ø1.2 at (73.06, 6.50) and (80.10, 6.50).
- **Empty XIAO footprint:** 2 × 7 holes Ø0.89 at 2.54 pitch, X 2.93–18.17, rows at Y 9.39 and 24.63 (15.24 apart).
- **Other holes:** 13 × Ø0.89 at 2.00 pitch along Y 1.79: X 4.48–18.48 (8 holes) and X 22.22–30.22 (5 holes). Function not documented.

**Connector side (top, +Z)**
| Part | X | Y | Height above PCB top | Notes |
|---|---|---|---|---|
| J2 speaker out, JST PH 2-pin SMD top entry (STEP: B2B-PH-SM4-TB) | 73.94–80.94 incl. tails (body 75.94–80.94) | 13.04–20.99 | **6.83** (tallest) | Unused in the build; bench test 1.3 only |
| 3.5 mm jack | 69.00–83.60 | 2.18–10.83 | 5.44 | Opening +X. Overhangs the right edge by 1.58, and dips 0.52 below the PCB top beyond it. Unused. |
| USB-C, mid-mount | 75.48–82.88 | 23.29–32.23 | 3.40 | Opening +X, overhangs by 0.86. Cable to the Pi's USB-A. |
| Everything else | — | — | ≤ 2.3 | — |

**Mic side (bottom, −Z)**
| Part | X | Y | Depth below PCB bottom | Notes |
|---|---|---|---|---|
| Two parts, each 4.6 × 3.2 (not named in the STEP; probably the buttons, P) | 1.23–5.83 and 8.92–13.52 | 4.11–7.36 | **2.59** | — |
| U4 mic, MSM261D3526H1CPM | 4.16–6.81 | 15.25–18.75 | 1.28 | Removed in the rework. Centre (5.49, 17.00). |
| U5 mic, MSM261D3526H1CPM | 75.16–77.81 | 15.25–18.75 | 1.28 | Removed in the rework. Centre (76.49, 17.00), 71.00 from U4. Directly beneath J2's tail end (plan overlap 1.9 with J2's body). |
| Small parts near (41, 16) | 39.90–42.00 | 14.27–17.95 | ≤ 1.19 | — |
| Everything else | — | — | ≤ 0.65 | — |

**After the mic rework** (bench plan, "ReSpeaker mic rework"):
- The strip cables are soldered to the vacated U4/U5 pads, on the mic side. Allow **≥ 3.0 below the bottom face** around each footprint for the joints and cable (E).
- **A1:** a zip-tie anchor within ~10 mm of each footprint, on the side the cable leaves (decision 15). The tie takes any pull, not the pads.
- The cable can be cut to any length up to 305 at this end.

**Notes for A1**
- The board can sit anywhere the 305 mm mic cables and the USB cable reach. The LED and buttons are on the mic side and aren't needed.
- **Keep-outs:** if the connector side faces a surface, keep it clear to 7.0 (J2). Leave a USB-C plug keep-out beyond the right end (overmold not measured).
- **Voice PE slot:** rev E §5 had the Voice PE vertical at y −63.4, z 35–94 (78 × 59 PCB). The ReSpeaker is longer (83.60 with the jack) and shorter (34.01). Check the width if A1 reuses that slot.
- **Mass:** not verified.

**D4a tap (only if Option B is populated; open issue 4)**
- Where the XU316's I²S and I²C can be tapped is unknown: there is no schematic (risk review R2/R3; U7/U15).
- The likely place is the empty XIAO footprint. This is an inference: Seeed's I²S firmware talks to a XIAO through it.
- Two ways to connect without crimping (H1):
  - solder Dupont jumper cut ends straight into the footprint holes, which stays flat;
  - fit 2.54 male headers and plug the jumpers on, which adds ≈ 16.5 plus the lead bend on the connector side (E). Headers aren't in the basket.

## MAIN_env — main board (reserved; B1 lays it out)
Replaces DIST_env and AMP_env (decision 2026-11-01; H2a, D4a on 2026-11-02; GPIO option 1 on 2026-11-02 23:00).

**What it does**
- 20 V in from the 5807 → NID100-5 5 V rail → the Pi (USB-C out, H2a) and the LD2410C. The LCD no longer has a branch here: it hangs off the Pi's pins 2/6 (option 1).
- The Pi's 3.3 V (pin 1) → TAS5756M logic supplies and the sensor branch.
- 20 V → TAS5756M amp, with BTL outputs to the speakers.
- Pi I/O fan-out from the 13 GPIO leads of plugs A/B.
- Branch fuses, PTCs and TVS.
- D4a 0 Ω links.

**Parts that set the envelope**
| Part | Plan size | Height above board | Source / note |
|---|---|---|---|
| Mean Well NID100-5 | 50.8 × 12 upright; 50.8 × 27.5 flat | 27.5 + standoff upright; ≈ 12 flat | D (BUCK_env). Keep ≥ 5 air around it (E). |
| Panasonic EEU-FR1J121B 120 µF 63 V | Ø10 × 16, radial, 5 mm lead pitch | 16 upright; ≈ 10 laid flat | D (onlinecomponents.com listing) |
| TI TAS5756M, HTSSOP-48 | 12.50 × 6.10 body | 1.2 max | D (SLAS988B) |
| 4 × LC-filter inductor, 10 µH (provisional: CODACA CSBA0850-100M) | 8.70 × 8.50 each | 5.10 max | D (DigiKey). TI SLAA701B: 10 µH + 0.68 µF for 4 Ω BTL. |
| NID EMC input inductor, 15 µH (provisional: Bourns SRR1260-150M) | 12.5 × 12.5 | 6.5 max | D (DigiKey) |
| 20 V eFuse, TI TPS16630PWPT (decided 2026-11-03) | 20-HTSSOP | ≤ 1.2 (E) | D (DigiKey) |
| GPIO landing, 13 positions (option 1) | 2.54 pitch; pattern B1's choice | ≈ 16.5 with Dupont housings on 2.54 male headers (E); flat if soldered | B1 chooses: male headers, with the leads' main-board ends in Daniel's housings, or solder pads with the terminal cut off. Header part, if any, is sourced once B1 names the pattern. |
| GCT USB4105-GF-A | — | not obtained | At a board edge, opening outward |
| JST B2B-XH-A / B4B-XH-A | 7.4 / 12.4 long | **9.8 mated** | D (JST XH catalog). The leads leave the plug vertically. |
| Fuses, PTCs, TVS, 0 Ω links | small | ≤ ~3 (E) | — |

**Reserved envelope (E)** — part-area tally × 1.2 for routing.

| Option | Board | Above the board top | Below the board | Holes | Mass |
|---|---|---|---|---|---|
| **U — NID upright (decided 2026-11-03, order list decision 33)** | ≈ 90 × 50 | ≤ 30 (NID 27.5) | ≤ 3.5 (THT tails, cut) | 4 × Ø2.7 for M2.5 at (3.5, 3.5), (86.5, 3.5), (3.5, 46.5), (86.5, 46.5): an 83 × 43 pattern (inserts owned) | ≈ 58 g |
| F — NID flat | ≈ 90 × 65 | ≤ 20, with the 120 µF laid flat; the plug zones still need lead-bend room (see below) | ≤ 3.5 | same | ≈ 62 g |

- **Plug zones in option F:** lead-bend room is needed above the XH plugs (9.8 mated) and, if B1 uses headers, the GPIO Dupont housings (≈ 16.5).
- **Mass estimate:** NID 35 g + FR-4 (1.85 g/cm³ × 90 × 50 × 1.6 = 13.3 g, or 17.3 g at 90 × 65) + parts ≈ 10 g.

**Placement constraints (A1)**
- **20 V inlet (D13):** the 5807 stays at the inlet grommet and feeds the board through a 22 AWG pigtail (≤ 300 mm, cut to length) into a B2B-XH-A. The main board is free of the inlet.
- **Cable reach:**
  - Pi power: the USB4105 must reach the Pi's USB-C (bottom edge, X 11.2) on a **0.2 m** cable, including both plug overmolds and bends.
  - Pi signals (option 1): the GPIO landing must reach the Pi's header, on the Pi's **front** edge (K10), on the 13 pre-crimped leads. Length is sourced in block 4 (20 cm assumed; fixed by the enclosure design). Single leads route more freely than a 51-wide ribbon, but K7 still applies to the loom over the fan.
  - LCD 5 V: no longer a main-board constraint. The LCD's own lead runs from the LCD to the Pi's pins 2/6 and must reach the Pi header (length not measured; Measure 2).
  - The 300 mm XH single-head leads to the speakers, radar and touch board are cut at the far end, so they don't limit placement.
  - **K11 slack (architect log 2026-11-02):** pre-made cables need ≥ 50 mm beyond the routed path (was 80). The 0.2 m USB-C cable therefore leaves ≤ ~150 of routed path, less the plug lengths. The GPIO leads' length is chosen to give the same ≥ 50. E0 can source longer pre-made cables if A1 needs them.
- **Keep-outs:** stay out of the sealed speaker chambers, keep air around the NID, and keep the TAS5756M's heat away from the BME680.
- **Candidate positions (block 3; details in `claude/E0-power-budget-2026-11-02.md` §6):**
  1. **A — vertical in the freed Voice PE plane. Default (decided 2026-11-03).**
     - PCB at y −65.0…−63.4, spanning x XC ± 45 and z 34–84; parts reach forward to y ≈ −33.4.
     - Interior 135 → 113 wide over that height.
     - K5: the −x lower lane's underside is ≥ z 84.9, so keep everything ≤ z 84.
     - K7: the NID stays at z ≥ 35.8 or outside x −17.6…12.4.
  2. **B — horizontal above the Pi.**
     - At z ≥ 35.8, between the partitions (0.3 per side).
     - It throttles the fan's air path and crosses the DSI FPC route.
  3. **Rejected — behind the Pi at floor level.** Only ≈ 24 deep and ≈ 95 wide at y −75.

**Not yet chosen (B1):** inductor and bulk-capacitor parts, the D4a ReSpeaker connector, mounting-hole positions, the GPIO landing (headers or pads, and its pattern).

## PD_env — Adafruit 5807 (HUSB238)
Source: Eagle board `adafruit/Adafruit-USB-Type-C-Power-Delivery-Dummy-Breakout-PCB` @ 53c602e, `Adafruit HUSB238 USB-C PD Breakout.brd`, parsed. Product page https://www.adafruit.com/product/5807.
- **Size:** PCB 20.32 × 23.495. Product overall 24.5 × 20.2 × 4.9 (the 24.5 includes the USB-C protruding ≈ 1.0 past the PCB edge). Mass 2.2 g.
- **Holes:** 2 × Ø2.5 plated at (2.413, 20.955) and (17.653, 20.955), near the USB-C edge.
- **USB-C:** CUI CUSB31-CFM2AX-01 at X 10.16, package origin Y 19.558. Opening +Y through the top edge.
- **Output:**
  - 3.5 mm terminal-block pads X4 centred (10.16, 4.572) on the bottom edge (+/− marked).
  - JP3/JP4 1 × 3 pads at Y 2.54 (X 5.08 and 15.24).
- **Configuration:** cut the **5V** voltage jumper and the **1A** current jumper. All voltage jumpers open = 20 V; both current jumpers open = 3.25 A request. With Daniel's 5 A e-marked cable that gives 65 W.
- **Mounting (D13, 2026-11-02): a separate board at the inlet grommet.**
  - Lie it perpendicular to the back wall, receptacle face at or just inside the outer cloth surface (USBC_port).
  - The 2 × Ø2.5 holes take **M2**, not M2.5. Block 4 adds 2 × M2 to the M2 hardware.
- **Pigtail:** a 22 AWG lead from the XH 2P lot, soldered to X4 (VOUT X4-1, GND X4-2; Eagle parse). It leaves the edge opposite the receptacle; allow ≥ 10 for the bend (E). The other end goes into a B2B-XH-A on the main board.
- **Output switch:** the 5807 switches VBUS onto VOUT through P-FET Q1 (AONR21307; gate R4 5.1 kΩ / R5 49.9 kΩ; Eagle parse). The turn-on inrush into the main board's bulk is uncontrolled; see the power budget §3.6.
- **A1 check:** at rev C/D's inlet position (x XC ± 10, receptacle z ≈ 18) the board reaches y ≈ −59.5. That is at the Pi's DSI fold zone (DSI connectors at world x 3.6–9.4 on the y −58 edge, ≥ 7.5 fold space per K10).

## BUCK_env — Mean Well NID100-5
Source: https://www.meanwell.com/Upload/PDF/NID100/NID100-SPEC.PDF (NID100-SPEC 2024-10-30), mechanical page.
- **Body:** 50.8 (L) × 27.5 (H, upright from the pin exit) × 12 max (T); the main body is 9.
- **Pins:** 13 × 0.64 sq, 4.5 long, 2.54 pitch.
  - Pin 1 is 1.24 from the left end (derived: 50.8 − 1.3 − 48.26).
  - Pins 1–6 at 0–12.70, pins 7–13 at 33.02–48.26 (relative to pin 1). Pin 13 is 1.3 from the right end.
  - The pin row is 4.0 from the back face.
  - Pinout: 1–4 +Vo, 5–8 Com, 9–10 +Vin, 11 NC, 12 Trim (optional), 13 R.C.
- **Mounting:** on the main board (MAIN_env).
  - Upright it occupies 50.8 × 12 of board area and stands **27.5 + standoff** tall.
  - Lying flat it's ≈ 12 tall, with pins bent 90° or carried on a riser.
- **Cooling and protection:** free-air convection (derating curve on page 2), so keep ≥ 5 mm air around it (E). Recommended input fuse 8 A.
- Mass 35 g.

## MIC_strip_L/R
- **Strip:** 30 × 6 × 0.8 reserved (handover). B1 confirms the parts below fit.
- **Front face** (toward the housing port, on the 1 mm foam gasket, rev D): **the mic only**. Keep other parts off the gasket area (E).
  - **Mic:** MEMSensing MSM261DHP006 (LCSC C22390138), LGA-8 4.00 × 3.00 × 1.00, top port Ø0.325. Datasheet rev 1.0 (2022-09-27), hosted by LCSC.
  - Pinout 1 VDD, 2 L/R, 3 CLK, 4 DATA, 5–8 GND. VDD 1.6–3.6 V; it runs at 3.3 V here.
  - The port position on the package isn't given. Copy the Voice PE footprint `Misc:MIC8P-0.85-4X3X1MM` (risk review R5).
- **Back face, per strip** (order list rev 3.7; review R5/R6):

| Part | Package | Height | Role |
|---|---|---|---|
| JST BM05B-SRSS-TB, top entry | 7.0 × 2.9 (+0.7 tails), contacts 4.0 span | 4.25; 4.9 mated | Cable connector. Lay the 7.0 along the strip. |
| TI SN74LVC1G17DCKR | SC70-5, 2.0 × 2.1 incl. leads | 1.1 max | CLK Schmitt buffer, with a 0 Ω bypass |
| TI TPD1E05U06DPYR × 3 | X1SON, 0402 size | 0.45 max | ESD on CLK, DATA, VDD |
| YAGEO CC0402MPX5R5BB106 10 µF + owned 100 nF | 0402 | 0.70 max | Mic decoupling |
| 33 Ω (100 Ω alternative), 100 Ω, 0 Ω | 0402 | — | DATA source termination, VDD RC filter, buffer bypass |
| L/R solder jumper | 3 pads | — | One strip to GND, one to VDD, matching the ReSpeaker pad map (U7) |
| Weak pull-down footprint on the buffer input | 0402 | — | Holds CLK if the ReSpeaker tri-states it when muted (bench plan, stage 2; inference) |
| Test pads + ground point | pads | — | CLK/DATA, in case a scope must be borrowed (bench plan 2.4) |

  Sources: JST SR catalog, TI datasheets (DCK0005A, DPY0002A), order list.
- **Back-side max:** 4.25 (4.9 mated). The cable leaves perpendicular to the strip, so reserve **≥ 10 behind the strip** for the bend (E).
  - If A1 needs the cable to run along the strip instead, the catalog side-entry part is SM05B-SRSS-TB: 2.9 tall, 4.25 deep, same cable. It isn't ordered.
- **Holes:** 2 heat-stake pins; A1 sets position and Ø (rev C pins Ø1.8).
- **Cable:** JST A05SR05SR30K305B, 305 mm, pin 1–1. Pinout (B1): VDD, GND, CLK, GND, DATA.
  - The strip end plugs in. The ReSpeaker end is cut and soldered to the vacated pads: VDD → 1, CLK → 2, DATA → 3, both grounds → 4 and 6. L/R is not carried.
  - Route away from the Pi, the DSI FPC, the backlight converter and the speaker leads (review R6).

## LD2410C_env — Hi-Link HLK-LD2410C
Source: HLK-LD2410C manual v1.00 (2022-11-07), https://www.sudo.is/docs/esphome/components/ld2410/HLK-LD2410C_manual_v1.00.pdf.
- **Outline:** 16 × 22. **D**
- **Thickness:** not published; estimate **≤ 3.0 without header** (E, measure on arrival).
- **Pads:** 5 × Ø0.9 at 2.54 pitch.
  - Pin 1 UART_Tx, 2 UART_Rx, 3 OUT, 4 GND, 5 VCC.
  - Which edge carries them isn't stated in the manual text; take it from the board.
- **Lead (H1):** XH 4P single-head, 26 AWG, 300 mm. Its cut end is soldered to pins 1, 2, 4 and 5; OUT (pin 3) is not wired. The XH end goes to the main board's B4B-XH-A (Pi UART, GPIO14/15).
- **Electrical:** VCC 5 V (5–12 V allowed); supply must provide **≥ 200 mA**, 79 mA average. IO 3.3 V, 256000 8N1.
- **Antenna:** detection ±60°. "Antenna facing the area to be detected"; keep the space in front clear, avoid moving objects behind it, and a metal backplane reduces the back lobe (manual §5.5).
- **Keep-out:** no carbon-filled or metal material in front of the antenna (K13 coupon test). The antenna face is the side without components (P, check on the board).

## BME680_env — CJMCU-680 (Daniel's board)
Listing: https://www.aliexpress.com/item/1005007530190637.html (SAILSTART Choice Store).
- **Board:** purple, 1.6 mm (robu.in listing). The BME680 sits on a slotted tab (thermal isolation) at one corner.
- **Holes and header:** 2 mounting holes. 6-pin 2.54 header on one edge: VCC, GND, SCL, SDA, SDO, CS.
- **Regulator:** onboard 3.3 V LDO; the listing says 5 V supply.
- **I²C address:** 0x77 needs SDO tied to VCC (0x76 if SDO is low).
- **Outline, hole Ø and positions: not published** (the listing's AI text says "20 × 15 × 3 cm", which is unusable). **P.** Caliper needed.
- **Keep-out:** air path to the sensor tab; keep it away from the Pi/NID/amp heat (A1 places it back-right, behind cloth slots).
- **Lead (H1):** Dupont F-F jumpers. The female end goes on the header pins; the cut end is soldered to a touch-board cluster.
  - On straight header pins, the Dupont housing adds ≈ 2.5 + 14 above the board (E). Rev C/D gave the BME680 6 mm (z 5.5–11.5).
  - If A1 needs it flat, solder cut jumper ends to the board's pads at both ends. That is still pre-made wire (H1).

## VEML_env — VEML6030 board (Daniel's board)
Listing: https://www.aliexpress.com/item/1005010560871926.html (Great IT Electronic Components).
- **Layout:** square board, 2 mounting holes at the top corners. 5-pin 2.54 header on the bottom edge: GND, 3.3V, SDA, SCL, INT. ADDR solder jumper (0x10 / 0x48).
- **Supply:** 3.3 V only, no regulator.
- **Outline:** ≈ 12 × 13 (listing text) vs ≈ 15 × 15 (photo scaled to the 10.16 header span). **Unresolved, P.** Caliper needed.
- **Optical:** the sensor window faces the Ø2 lux port in the top (handover §5).
- **Lead (H1):** as BME680_env — Dupont F-F to a touch-board cluster, with the same height note.

## TOUCH_pcb / TOUCH_components — rev C (trimmed 100 → 90)
Source: `neocleous/ha-panel` branch `docs` @ 954846f, `hardware/rev-c/ha_touch_revC.kicad_pcb` and README, parsed.
- **As built:** 100 × 44 × 1.6, R2 corners, **no holes**.
  - Front: 4 electrodes Ø12 at KiCad X 14/38/62/86, Y 13 from the top edge.
  - Back: U1 AT42QT1070 SOIC-14 at (50, 27); R1–R4 0402; C1 0402; C2 0603.
  - Wire-pad clusters J3/J2/J1/J4 at X 14/38/62/86, Y 39.8 from the top edge. Pads 2 × 3 mm at 3.5 pitch (VCC GND SDA SCL).
- **Rev F state** (cut 5 mm off each end, rotated 180°; front-view frame with origin at the lower-left of the 90 × 44 board):
  - Electrodes E0/E1/E2/E3 at X 9/33/57/81, Y 13 (copper 7–19). Key order reverses → remap in `at42qt1070.py` (handover).
  - U1 at (45, 27), on the back.
  - Wire clusters at Y 39.8 from the bottom (4.2 below the top edge): J4 at X 9, J1 at X 33, J2 at X 57, J3 at X 81.
- **Leads (H1):**
  - The HOST cluster takes an XH 4P single-head lead to the main board (cut end soldered).
  - Two clusters take the Dupont cut ends from the BME680 and the VEML6030.
  - All leads leave along the top edge.
- **Back-side max:** SOIC-14 1.75 (JEDEC max) plus solder joints and wire bends. Allow ≥ 3.0 (E).
- **Mass:** ≈ 11 g after trim (FR-4 1.85 g/cm³ × 90 × 44 × 1.6, calculated).

## SPK_driver_L/R — Dayton Audio DMA45-4
Source: Dayton spec sheet https://doc.soundimports.nl/pdf/brands/Dayton%20Audio/DMA45-4/pdf_Dayton%20Audio_DMA45-4_1.pdf (drawing). Mass from Audiophonics.
- **Frame:** 46.0 × 46.0 square, flange 3.0 thick.
- **Holes:** 4 × Ø3.3 on Ø50.2 (= ±17.75 square ✓ handover).
- **Basket:** Ø40.0, 26.1 behind the flange; overall 29.1. Cutout Ø40.
- **Terminals:** 2 tabs at the rear (drawing dims 5.2 / 2.8).
- **Lead (H1):** XH 2P single-head, 22 AWG UL1007, 300 mm.
  - The cut end is soldered to the tabs.
  - The lead leaves the sealed chamber through its back partition (rev C/D had Ø5 holes at XC±75, z 18). Seal it after assembly (E).
- **Magnet Ø:** not dimensioned.
- **Front:** the surround/cone dome rises slightly above the flange face (not dimensioned).
- Mass 68 g.
- **K6 (chin fillet):**
  - Hole bosses sit at r 25.1 (hole edge r 26.75); the frame corner is at r 32.5.
  - Geometrically, a ≤ 4 mm-leg corner clip keeps ≥ 2 mm material around the holes. But the frame material and strength aren't specified, so E0 recommends **not** modifying the driver.
  - Use K6's frame-face y ≤ 2.0 option instead.
- **Volume (V5):** 115 cm³ net → Qtc 0.74, F3 192 Hz. Minimum 81.6 cm³ for Qtc ≤ 0.8.

## USBC_port
- **Port:** the 5807's receptacle, CUI CUSB31-CFM2AX-01, which protrudes ≈ 1.0 past the 5807's PCB edge.
- **Mounting:** the 5807 sits at the back wall with the port through the grommet (handover §5), as a separate board (D13; PD_env).
- **Plug engagement:** the receptacle face must sit **at or just inside the outer cloth surface** for full plug engagement. With 2.5 wall + 0.7 cloth, that means a local wall recess or the PCB edge inside the cutout.
- **Cutout:** must pass the cable's plug overmold. Daniel's 5 A e-marked cable overmold isn't measured → **measure it** (E).

## SJ5012
- 3M Bumpon SJ-5012 black: Ø12.70 × 3.50, tapered cylinder (DigiKey SJ5012-0-ND listing).
- Handover recess Ø13 × 0.5 ✓.

---

## Leads — pre-made only (H1)
Cables and listings are in the order list's Harness section. "Cut" means that end of the pre-made cable is cut and soldered.

| Lead | From → to | Pre-made cable | Length | Ends | Envelope notes |
|---|---|---|---|---|---|
| Pi power (H2a) | main board USB4105 → Pi USB-C (bottom edge, X 11.2) | USB-C to C, 5 A / 240 W | 0.2 m | plug / plug | Overmolds not measured. Reserve ≥ 30 beyond each receptacle for a straight plug + bend (E). |
| Pi signals, plug A (option 1) | main-board GPIO landing → Pi pins 1, 3, 5, 8, 9, 10, 12, 14, 15 | 9 pre-crimped Dupont F-F leads (block 4), in Daniel's 2 × 8 housing at the Pi | 20 cm assumed (fixed by enclosure design) | Dupont / header or cut | Mark the orientation. Twist 12 with 14 (E). K7 applies over the fan. Cooler fit: open issue 3. |
| Pi signals, plug B (option 1) | main-board GPIO landing → Pi pins 35, 38, 39, 40 | 4 pre-crimped Dupont F-F leads (block 4), in a 2 × 3 housing | as plug A | Dupont / header or cut | Mark the orientation |
| ReSpeaker USB | Pi USB-A (right edge) → ReSpeaker USB-C (+X end) | owned USB-A to C | A1 | plug / plug | A1 sets length and plug angle |
| Mic L / R | strip SR header → ReSpeaker U4 / U5 pads | JST A05SR05SR30K305B | 305 | SR plug / cut | Cut to length at the ReSpeaker; zip-tie anchor; route per R6 |
| Speaker L / R | main board B2B-XH-A → DMA45-4 tabs | XH 2P single-head, 22 AWG UL1007 | 300 | XH / cut | Through the chamber's back partition; seal |
| Radar | main board B4B-XH-A → LD2410C pins 1, 2, 4, 5 | XH 4P single-head, 26 AWG | 300 | XH / cut | OUT not wired |
| Touch board | main board B4B-XH-A → HOST cluster | XH 4P single-head, 26 AWG | 300 | XH / cut | Leaves along the touch board's top edge |
| BME680, VEML6030 | breakout header pins → touch-board clusters | Dupont F-F jumpers | 300 | Dupont / cut | ≈ 16.5 above the breakout on straight pins (E); cut both ends to stay flat |
| LCD 5 V (option 1) | Pi pin 2 (5 V) and pin 6 (GND), inside plug A → LCD | the LCD's own 4-pin lead; its 5 V and GND terminals re-housed in plug A | not measured | Dupont / LCD | SDA/SCL terminals unused (DSI-side I²C), insulated and tied back. The lead must reach the Pi header. |
| DSI | Pi CAM/DISP → LCD 15-pin | FPC 22 → 15 pin (B) | 300 | FPC / FPC | Unchanged |
| 20 V pigtail (D13) | 5807 X4 at the inlet → main board B2B-XH-A | XH 2P single-head, 22 AWG UL1007 | ≤ 300 (cut to length) | cut / XH | JST XH rated 3 A at AWG 22; design peak 2.83 A (power budget §4) |
| D4a (Option B only) | main board → ReSpeaker tap | Dupont F-F (spares from the 40) | 300 | — | Open issue 4 |

---

## Changes vs rev D / handover / architect log
Issue 4 (2026-11-02 23:00, option 1):
- **GPIO link:** 40-pin IDC ribbon → two custom Dupont plugs on the Pi (A 2 × 8 on pins 1–16, B 2 × 3 on pins 35–40), 13 pre-crimped F-F leads. Supersedes the ribbon in architect log D10/D11/K11.
- **LCD power:** main-board 1 × 4 header (L1a, D12) → the Pi's pins 2/6, as in Daniel's current build.
- **MAIN_env:** 2 × 20 box header and 1 × 4 header removed; 13-position GPIO landing added (B1).

Issue 2 (2026-11-02):
1. **Voice PE, AA-AB32472 and EG1249** are out of the build. Their envelopes and the PE-specific items (holes, J3 radar pins, jack detect, Grove) are gone.
2. **RESPEAKER_pcb:** 82.02 × 34.01 × 1.51, 2 × Ø2.2 holes; connector side 6.83, mic side 2.59.
3. **MAIN_env:** replaces DIST_env (≤ 70 × 45) and AMP_env. Reserved ≈ 90 × 50 × 30 (NID upright) or ≈ 90 × 65 × 20 (NID flat).
4. **MIC strip:** tuning parts on the back face. The cable ends at the ReSpeaker's vacated pads.
5. **PI5:** powered through its own USB-C. The GPIO carries signals only, over a 40-pin ribbon (ribbon superseded by issue 4).
6. **LD2410C:** on the Pi UART through the main board (XH 4P lead).
7. **PI5_cooler keep-out:** aligned to K7 (≥ 10 clear above the fan). Issue 1's E0 rule was ≥ 5.

Still valid from issue 1:

8. **PD_env:** 25 × 22 → **20.32 × 23.495 PCB** (24.5 including the USB-C) × 4.9. Holes 2 × Ø2.5.
9. **PI5_cooler:** top ≈ z 31 (K7) → **≤ z 25.8** (13.7 overall per the official drawing).
10. **BUCK_env:** NID100-5 is 50.8 × 27.5 × 12. Upright it's 27.5 tall.
11. **MIC strip:**
    - VDD 3.3 V (was 1.8 V).
    - The SR header (7.0 wide) runs along the strip. Issue 1 called it "SH"; it is JST SR.
    - The L/R strap now follows the ReSpeaker pad map (U7).
12. **DMA45-4:** confirmed. Holes are Ø3.3, overall depth 29.1.

## Open issues
1. **ReSpeaker outline.** The STEP (v1.1) gives 82.02 × 34.01 × 1.51; Seeed's listing gives 35 × 86. Measure on arrival (wave 1) before A1 freezes the mount.
2. **Main-board placement in rev E (A1).** Candidate A is the decided default (2026-11-03); A1 confirms it in the model. See MAIN_env and the power budget §6.
3. **GPIO plugs vs Active Cooler (option 1).**
   - A 2-row Dupont housing (≈ 5.1 wide, 2 × 2.54, E) centred on the header (Y 52.5) reaches Y ≈ 50.0.
   - The cooler outline is scaled to Y 50.4 (S, ±0.5), so the housings may touch the cooler by up to ≈ 0.4–0.9: plug A along the fin block, plug B along the fan.
   - Test-fit plugs A/B in A2 (Measure 3); Daniel has the Pi, the cooler and the housings, so it needs no order. The fallback is a GPIO stacking header to lift the housings (not in the basket).
4. **D4a tap on the ReSpeaker** (B1, from U7/U15). The likely place is the XIAO footprint (inference). If headers are used, the connector side gains ≈ 16.5 (E).
5. **ReSpeaker fasteners.** The Ø2.2 holes take M2, and nothing M2 is in the basket. A1 chooses screws into bosses or clips; E0 adds the part in block 5 once A1 says which.
6. **LCD 4-pin lead length** (owned, not measured). Since option 1 it must reach from the LCD to the Pi header, not to the main board.
7. **USB-C plug overmolds:** Daniel's 5 A inlet cable, the new 0.2 m cable (on arrival), and the ReSpeaker's A-to-C cable.
8. **BME680 and VEML6030 boards:** outline, hole Ø and hole positions need a caliper measurement (photo-only so far).
9. **LD2410C:** thickness and antenna face need measuring on arrival.
10. **Pi 5:** the USB/RJ45 stack height, header height, MIPI connector positions and FPC exit, and the microSD position aren't on the official drawing. Measure the board or import a Pi 5 STEP.
11. **Mic-strip fit.**
    - B1 confirms the mic plus ~12 back-face parts and the test pads fit 30 × 6 (E0's area tally says they do, E).
    - The MSM261DHP006's port position comes from the Voice PE footprint.
    - A clock rise-time limit for this mic is still not established (review R6). The Schmitt buffer covers it.
12. **Main-board height not obtained:** the GCT USB4105-GF-A. B1 takes it from the GCT drawing, which couldn't be read here. (The Würth 61204021621 box header left the design with option 1.)
13. **Pi USB-A end vs the chamber partition (A1).**
    - The USB stacks overhang the partition gap by 0.25, and a USB-A plug for the ReSpeaker needs far more room (≈ 30–40 straight, E).
    - Resolving the layout is A1's job. On request, E0 can source a pre-made right-angle USB-A-to-C cable.
14. **Pi USB-C plug vs the back wall (A1, E0 block 5).**
    - There is ≈ 22–23 of room behind the Pi's edge, while a straight plug needs ≥ 30 (E).
    - The plug shape of the basket's 0.2 m cable isn't recorded: AliExpress blocks fetching, so it needs a browser check.
    - E0 checks it in block 5 and, if it's straight, proposes a pre-made right-angle 5 A C-to-C cable.
15. **K11 slack vs cable lengths (A1).** The routed path from the main board to the Pi's USB-C must stay ≤ ~150 (200 − 50 slack, architect log 2026-11-02), less the plug lengths. The GPIO leads (option 1) are bought to A1's routed length + 50; 20 cm is the current assumption.

## Measure (Daniel, calipers — ≈ 15 min)
1. **ReSpeaker Lite (on arrival):** L × W and hole centres from one corner, to compare with the STEP. Mass too, if a scale is handy.
2. **LCD 4-pin lead:** length from the LCD connector to the Dupont end.
3. **Pi 5 + cooler + plugs A/B:** do 2 × 8 and 2 × 3 Dupont housings seat fully on pins 1–16 and 35–40 with the cooler fitted? Yes/no.
4. **USB-C plug overmolds (W × H × L):** the 5 A cable, the new 0.2 m cable, the ReSpeaker's A-to-C cable.
5. **BME680 board:** L × W, hole Ø and centres from one corner.
6. **VEML6030 board:** L × W, hole Ø and centres.
7. **Pi 5:** USB/RJ45 stack height above the PCB top.
