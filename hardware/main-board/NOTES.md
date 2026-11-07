# Main board — schematic notes (checkpoint 1, 2026-11-07; updated for decisions 1–5, 2026-11-07 20:45) — layout 2026-11-07 22:30: §7

KiCad **9.0.9**. Every value below is traced to a datasheet section or a project decision; sources and retrieval dates are at the end. "E" = engineering estimate, "not verified" = no source found.

## 1. 20 V inlet and eFuse (`inlet.kicad_sch`)

| Ref | Part / value | Why |
|---|---|---|
| J1 | JST B2B-XH-A | 5807 pigtail (D13): pin 1 = +20 V (5807 VOUT), pin 2 = GND. JST XH 3 A at 22 AWG; design peak 2.83 A (power budget §4). |
| F1 | Littelfuse 0453005.MR, 5 A | Decided part (order list decisions 27–31: "0453005.MR stays upstream" of the eFuse). The brief says "fuse (8 A per NID spec)"; Mean Well's 8 A is for the NID's own input. **Decision 1 (Daniel 2026-11-07 19:24): keep 5 A.** |
| C1, C2 | 1 µF 50 V X7R 0805, 100 nF 50 V X7R 0603 | eFuse input: ≥ 0.1 µF bypass at IN (SLVSET9G 8.3.9); ≥ 1 µF local input C with TVS (9.4.1). Total ≈ 1.1 µF ≪ USB PD cSnkBulk. |
| R1, R2, R3 | 412 k / 9.09 k / 22.1 k, 1 % | UVLO rising = 1.2 V × 443.2 k / 31.19 k = **17.05 V** (falling 1.122 V → 15.94 V); OVP rising = 1.2 V × 443.2 k / 22.1 k = **24.06 V** (release 22.5 V). V(UVLOR) = V(OVPR) = 1.2 V, V(UVLOF) = V(OVPF) = 1.122 V (SLVSET9G 6.5). Divider current 45 µA. |
| U1 | TI TPS16630PWPT | Decided (decision 31). Footprint: KiCad `HTSSOP-20-1EP_4.4x6.5mm_P0.65mm_EP3.4x6.5mm_Mask2.96x2.96mm_ThermalVias` = TI PWP0020T land pattern (pad 3.4 × 6.5, mask opening 2.96 × 2.96; SLVSET9G p. 42). |
| C3 | 47 nF 50 V X7R 0603 | t(dVdT) = 20.8 × 10³ × V_IN × C(dVdT) = 20.8e3 × 20 V × 47 nF = **19.6 ms** (SLVSET9G eq. 2); inrush = 385 µF × 20 V / 19.6 ms = **0.39 A**; P(inrush) = 0.5 × 20 V × 0.39 A = 3.9 W for 20 ms, inside the thermal-regulation loop (8.3.1.1). Turn-on delay after UVLO = 742 µs + 49.5 µs/nF × 47 = 3.1 ms (6.6). |
| R4 | 5.49 kΩ 1 % | I_OL = 18 / R(ILIM)[kΩ] = **3.28 A ±7 %** (table points 30 k → 0.6 A, 9 k → 2 A, 4.02 k → 4.5 A, 3 k → 6 A; SLVSET9G 6.5). Minimum 3.05 A > design peak 2.83 A; ≈ the 65 W contract (3.25 A). |
| R5 | 10 kΩ 1 % | V(IMON) = I × 27.9 µA/A × 10 kΩ = **0.279 V/A** (eq. 9); 0.79 V at 2.83 A, below the 4 V limit. Test pad TP3 = 20 V bus current without breaking the circuit. |
| R6 | 100 kΩ to +3V3 | ~FLT open-drain pull-up (SLVSET9G 5-1). |
| MODE | → GND | Auto-retry after a fault (SLVSET9G 8.4). |
| SHDN | open (TP6 only) | Internal 2.7 V open-circuit (6.5) = on. TP6 lets the bench pull it low. |
| PGOOD | → R7 0 Ω → NID R.C. | Open drain, 36–130 Ω pull-down, 60 V rated (6.5, 8.3.8). R.C. = open → NID on; < 0.4 V → off (NID spec). NID starts only once the eFuse FET is fully on. Remove R7 = NID free-running. |
| C4 | 100 nF 50 V X7R 0603 | eFuse OUT bypass. |
| D1 | Littelfuse SMBJ22A | Decided (power budget §3; order list). On the +20V bus (eFuse output). Output load is capacitive, so no reverse Schottky. |

**V19 (HUSB238 / PD sink bulk capacitance → dV/dt and OVP):** the HUSB238A's GATE pin is an open-drain driver for an *external* VBUS switch (Hynetek HUSB238A datasheet Rev. 1.0, pin 15); the datasheet publishes no GATE switching time. The design therefore does not rely on it: UVLO at 17.05 V keeps the eFuse **off on the 5 V default contract** and through negotiation, so the source sees only C1 + C2 ≈ 1.1 µF; the 385 µF behind the eFuse is charged at 0.39 A over 19.6 ms once 20 V is up. OVP 24.06 V (±2 %) sits below the TAS5756M recommended PVDD maximum 26.4 V and absolute maximum 30 V (SLAS988B 7.1/7.3).

## 2. 5 V supply and outputs (`supply_5v.kicad_sch`)

| Ref | Part / value | Why |
|---|---|---|
| C5, C6 | Panasonic EEU-FR1J121B 120 µF 63 V | Mean Well EMC circuit C1/C2 120 µF/63 V (NID100-SPEC 2024-10-30). C5 also = 20 V bus bulk. |
| L1 | Bourns SRR1260-150M 15 µH | EMC circuit L1 15 µH (NiZn). SRR1260-150M: 15 µH ±20 %, Isat 4.60 A, I_rms 5.00 A, RDC 27 mΩ max, core "Ferrite DR and RI" (Bourns REV. 03/26). Single winding in +Vin: the NID is non-isolated, input and output share Com. **V18:** see §6. |
| PS1 | Mean Well NID100-5 | Decided. Pins: 1–4 +Vout, 5–8 Com, 9–10 +Vin, 11 NC, 12 Trim (optional), 13 R.C. (spec "Pin Configuration"). Switching 200 kHz typ. |
| C7 | Würth 860160572003 22 µF 35 V | EMC circuit C3 (decision 29). External C on +5V = C7 22 + C8 10 (1206 X7R) + C9 + C10 + the LDO path behind 2.2 Ω ≈ 35 µF ≪ the 100 µF limit (spec). |
| D2 | Littelfuse SMBJ6.0A-E | Decided (decision 27). |
| R8, R9 | 0805, **DNP** | **V20 trim network:** R8 Trim → Com (raises Vout), R9 Trim → +Vout (lowers). Mean Well lists pin 12 as "Trim (optional)" and gives no formula; the direction assumes the usual feedback-divider tap (not published). On arrival: measure R(pin 12–Com) unpowered, then clip a trimmer from TP13 to GND and read Vout before fitting R8. No response → the alternative-regulator decision of D23. |
| R7 | 0 Ω | eFuse PGOOD → R.C. (see §1). |
| F2 | Littelfuse 0453010.MR 10 A | Decided (decision 28), 5.6 mΩ cold. |
| LK1 | wire link, 1.0 mm tinned Cu, 7.62 mm pitch, footprint `ha_panel:WireLink_P7.62mm_D1.3mm` (pads 1/2; the stock bridge footprint has both pads numbered 1) | Bench 2.7: remove and put the 10 A meter in series with the Pi branch. |
| J2 | GCT **USB4085-GF-A** (THT) | **Decision 3A** (replaces the SMD USB4105 under the 19:24 rule: back-side parts are THT). Source-only port: VBUS + CC, no data. "Dip Type, PCB Top Mount", 16 contacts + 4 shell stakes, 5.00 A VBUS / 6.25 A GND, 48 V; **3.46 mm** above the board (fits MAIN_back_env 3.5), receptacle axis **1.88 mm** (USB4105: 1.73), body 8.94 × 9.17; signal tails 1.60, shell stakes 2.10 (GCT drawing USB4085 rev B, 2023-02-28). Mounted on the door side, mouth flush with the bottom edge so the plug stays at z 14.0–33.9 as modelled; GCT's recommended layout puts the PCB edge 2.51 mm behind the mouth (overhang), which would move the plug 2.5 mm down. Soldered from the Pi side. |
| R10, R11 | 10 kΩ 1 % to VBUS | Rp to 5 V on CC1/CC2 = 3.0 A advertisement (USB Type-C Rp table); the Pi runs with `PSU_MAX_CURRENT=5000`. |
| C8, C9 | 10 µF 25 V X7R 1206, 100 nF | Local VBUS decoupling at the receptacle. |
| F3 | Littelfuse 0453001.MR 1 A | Decided (decision 30), 153 mΩ cold; LD2410C needs ≥ 200 mA, 79 mA avg (envelope sheet). |
| C10 | 1 µF 50 V X7R 0805 | Radar branch decoupling (E). |

## 3. 3.3 V, Pi link, XH headers, D4a (`io.kicad_sch`)

| Ref | Part / value | Why |
|---|---|---|
| U2 | TI TPS70933DBVR (new part) | **V17:** Raspberry Pi publishes no current rating for the Pi 5 header 3V3 pins (documentation `power-supplies.adoc` lists only "GPIO pins (combined) 50 mA maximum" as typical draw; HAT+ spec gives none) → brief item 4 fallback: LDO on the main board. TPS709: 2.7–30 V in, 150 mA, ±1 % at 3.3 V, EN high ≥ 0.9 V, shutdown 150 nA (SBVS186H Electrical Characteristics). 30 V input survives the NID's output OVP (6.4–7.5 V). |
| R12, C11 | 2.2 Ω 0805, 10 µF 25 V X7R 1206 | RC pre-filter: f_c = 7.2 kHz, ≈ 29 dB at the NID's 200 kHz. Drop 0.19 V at 85 mA keeps U2 out of dropout. |
| C12 | 4.7 µF 16 V X7R 0805 | ≥ 2.0 µF effective output C (SBVS186H 8.1.1). |
| R13 | 100 kΩ | EN pull-down; EN = Pi 3V3 (lead A1). In Pi STANDBY (5 V on, 3V3 off — HAT+ spec) the LDO is off, so nothing back-feeds the Pi's I²C pins, and the amp stays muted (R17). |
| Load | ≈ 85 mA | TAS5756M DVDD + AVDD + CPVDD ≈ 35 mA (SLAS988B 7.12, idle) + touch/BME680/VEML6030 ≈ 50 mA (brief). U2 dissipation (5.0 − 0.19 − 3.3) V × 85 mA = 0.13 W. |
| R26, R27 | 0 Ω 0603; R27 **DNP** | Amp logic rail 3V3_AMP (TAS DVDD/AVDD/CPVDD, C105/C119, R102). TAS5756M digital inputs need VIH ≥ 0.9 × DVDD (SLAS988B 7.3) and TI advises driving them from the DVDD supply (note 2); the Pi drives I²S/I²C/GPIO22 from its own 3V3, whose tolerance is not published. Default R26 = board LDO (±1 %); option R27 = the Pi 3V3 (lead A1 then carries ≈ 35 mA). Bench: compare TP16 with the Pi 3V3 at J3.1. |
| F4 | Bel 0ZCJ0020FF2E 0.2 A PTC | Decided (decision 30), sensor/touch branch. |
| J3, J4 | wire pads 2 × 5 + 2 × 2 | GPIO landing, 13 leads — see `gpio-leads.md`. |
| R14–R16 | 0 Ω 0603 | I²S series positions (BCLK, LRCLK, DOUT): spin-1 lever, 22–47 Ω if the edges ring over the 150 mm leads (E). |
| R17 | 100 kΩ | AMP_MUTE_N pull-down: muted unless GPIO22 drives high. |
| R18 | 100 kΩ | PI_DIN pull-down (lead B2 unused in topology A). |
| J5 | JST B4B-XH-A | LD2410C: 1 VCC 5 V, 2 GND, 3 LD TX, 4 LD RX (envelope sheet: lead soldered to LD2410C pins 1, 2, 4, 5; OUT not wired). |
| R19 | 4.7 kΩ | LD TX → Pi RXD. Replaces the provisional 1 kΩ: limits current into an unpowered Pi (radar stays on 5 V when the Pi is off) to 0.64 mA; with ≈ 10 pF the RC is 47 ns ≪ 3.9 µs bit time at 256000 Bd. |
| J6 | JST B4B-XH-A | Touch board rev D (`hardware/touch-board`, decision 5A) HOST pads: VCC, GND, SDA, SCL. No INT (CHANGE# unused, as on rev C). |
| J10 | wire pads, 2 × 4 at 2.54 | **Decision 5A:** the BME680 (CJMCU-680) and VEML6030 Dupont leads land here instead of on the touch board: odd column BME680 (3V3_SENS, GND, SDA, SCL), even column VEML6030 (same). 3V3_SENS through F4. |
| J7 | 1 × 8 wire pads | D4a ReSpeaker tap, to the XIAO footprint (Seeed pinout): 1 GND, 2 I2S_BCLK, 3 I2S_LRCLK, 4 → I2S_DIN_SEC(dout) (reference into the XU316), 5 ← I2S_DIN_XIAO(din) (XU316 output), 6 GND, 7 SDA, 8 SCL. |
| R20–R25 | 0 Ω 0603, **DNP** | Topology A (USB reference, default): all open. Topology B (bench 2.2): fit R20–R23 (+R24/R25 to reach the XU316 over I²C), I²S firmware, Pi as I²S clock consumer (custom overlay). |
| H1–H4 | Ø2.7 NPTH | Fixed interface: 83 × 43 pattern, M2.5 into ruthex inserts in the bracket bosses. |

## 4. Amplifier (`amplifier.kicad_sch`)

TAS5756M per TI SLAS988B Figure 79 (stereo BTL) and Table 22, wired like the Raspberry Pi DigiAMP+ so the stock `rpi-digiampplus` overlay drives it (see `gpio-leads.md`).

| Ref | Part / value | Why |
|---|---|---|
| U100 | TI TAS5756MDCAR | Decided (D1 = a). I²C 0x4C: ADR0 (26) = ADR1 (20) = GND (pin table: GND = address bit 0). PVDD 4.5–26.4 V recommended, 30 V absolute (7.3/7.1). MCLK (22) = GND: the pcm512x driver runs the PLL from BCLK when no MCLK is given (overlay has no clock). GPIO0–2 held low by R103–R105 (unused). |
| F5 | Littelfuse 2920L260/33DR | Decided. Hold 2.6 A at 25 °C (1.81 A at 60 °C). Amp average at 2 × 10 W into 4 Ω ≈ 1.2 A from 20 V (E, 85 % efficiency). |
| C13 | EEU-FR1J121B 120 µF 63 V | PVDD bulk behind the PTC (power budget). |
| C100, C121 | 0.1 µF 50 V X7R **0603** | Table 22 (0402 there; moved to 0603 for hand assembly, D42). At PVDD pins 6/7 and 41–43. |
| C101, C102, C122, C123 | Cal-Chip GMC21X5R226M35NT 22 µF 35 V X5R 0805 | Table 22 PVDD bulk; voltage > 1.45 × PVDD (Table 22 note). |
| C103 | Taiyo Yuden UMK107AB7105KA-T 1 µF 50 V 0603 | GVDD_REG (> 16 V required). |
| R100, R101 | 100 kΩ to GND, 150 kΩ to GVDD_REG, 1 % 0603 | V(SPK_GAIN/FREQ) = GVDD × 100/250 = 2.8 V at GVDD 7.0 V → **20 dBV, f_SW = 8 × f_SYNC = 768 kHz at 48 kHz** (Table 15 window 2.33–3.10 V, held for GVDD 5.83–7.75 V). D22's −4.0 dBFS software ceiling keeps 10 W into 4 Ω. |
| C104, C108, C111, C115 | Samsung CL10B224KB8NNNC 0.22 µF 50 V 0603 | Bootstrap, Table 22. |
| L100–L103 | CODACA CSBA0850-100M 10 µH | LC filter, type 2 (Fig. 79). CODACA datasheet (revised 2026-03-16): 10 µH ±20 %, DCR 27.5 typ / 31.6 max mΩ, **Isat 3.50 A at −10 % L / 8.00 A at −30 % L**, Irms 5.60 A (ΔT 50 °C), body 8.7 × 8.5 × 5.1, composite core, MSL 1; land 2 × 3.0 × 3.0, gap 3.6. Normal peak 2.6 A (10 W/4 Ω 2.24 A + 0.33 A ripple at 768 kHz) < 3.5 A; at the 7.5 A OCE threshold L ≈ 7 µH ≥ 4.7 µH nominal / 1 µH min for the short-circuit LC (SLAS988B 7.3). DigiKey's "Isat 8 A" is the −30 % value. |
| C109, C110, C116, C117 | Samsung CL21B684KBFVPNE 0.68 µF 50 V X7R 0805 | **Type 2** filter (one C per leg to GND) as in Fig. 79 and SLAA701B §1.3.2 for BD modulation. The power budget cited §1.3.4.1's type 1 (differential C); same part count, now to GND. f₀ = 1 / (2π √(20 µH × 0.34 µF)) = **61 kHz**, Q = 4 Ω × √(0.34 µF / 20 µH) = **0.52** (−0.8 dB at 20 kHz). Voltage > 1.8 × PVDD. |
| C106, C113 | 2.2 µF 25 V X7R **0603** | DAC_OUTx → SPK_INx+ coupling (Fig. 79; Table 22 0402 → 0603). |
| C107, C114 | 2.2 µF 25 V X7R **0603** | SPK_INx− to GND (Fig. 79). |
| C105, C118, C119, C120 | 1 µF 25 V X7R **0603** | AVDD, DVDD_REG, DVDD/CPVDD, CPVSS (Table 22: 1 µF, ≥ 6.3 V; 0402 → 0603). |
| C112 | 1 µF 25 V X7R 0603 | Charge-pump flying cap CP–CN (Fig. 79). |
| R102 | 100 kΩ to 3V3_AMP | ~SPK_FAULT open-drain pull-up (TP19). |
| J8, J9 | JST B2B-XH-A | Speaker L = channel A (+x side, viewer's left), speaker R = channel B. |

Thermal pad (pin 49): via array and paste windows at 70–80 % of the pad area (SLAS988B 11.1.3.2) — built into the custom footprint in block 2.

## 5. Test pads (bench plan rev 3.5)
All test pads are bare SMD pads Ø1.5 on the **back** (door side, `TestPoint_Pad_D1.5mm`): nothing to solder, probed with the door off, and no front-side area (layout density, decision 6).

| Pad | Net | Bench use |
|---|---|---|
| TP1 VIN | before the eFuse | 20 V present / OVP behaviour |
| TP2 20V | +20V bus | "20 V bus" |
| TP3 IMON | eFuse current monitor | 0.279 V/A — 20 V bus current, no meter in series |
| TP4 FLT, TP5 PG, TP6 SHDN | eFuse status / control | fault, NID enable, forced off |
| TP8 NID_IN | NID input (after L1) | "NID in" |
| TP9 5V | NID output | "NID out", 2.6/2.7, 2.11 start-up |
| TP10 5V_F | after F2 | 2.7 fuse drop |
| TP11 EXT5V | VBUS at J2 (USB4085) | 2.6/2.7 "EXT5V at the USB4105" |
| TP12 RADAR | radar 5 V after F3 | 2.12 radar VCC |
| TP13 TRIM, TP14 RC | NID pins 12 and 13 | V20 trim check, NID enable |
| TP16 3V3, TP19 FAULT | rails / amp status | bring-up (PVDD: probe F5 pin 2 on the back – TP18 dropped in layout, no free back spot on the PVDD side) |
| TP7, TP15, TP17, TP20 | GND | probe returns |
| LK1 | Pi branch link | 2.7 series current |

## 6. Verify items answered in this block

- **V10** — USB4105-GF-A: 3.31 mm above the board face, plug centre 1.73 mm, body 8.94 × 7.35, front flush with the board edge (GCT drawing rev B4, 2023-12-18).
- **V17** — no published Pi 5 header 3V3 rating → TPS70933 LDO on the main board (§3).
- **V18** — Bourns states only "Ferrite DR and RI" for the SRR1260 core; NiZn is not confirmable from Bourns. Würth's WE-PD 7447709150 (15 µH, 12 × 12 × 10 mm) datasheet states no core material either (rev 006.001, 2024-05-08). Kept SRR1260-150M: it meets the circuit's 15 µH and carries the ≈ 3 A worst-case NID input current (55 W / 93 % / 20 V) below its 4.6 A Isat; Mean Well's circuit is for Class B (the NID meets Class A without it).
- **V19** — §1.
- **V20** — trim network R8/R9 DNP + TP13 (§2); trim function unverified on stock units.

## 7. Layout (block 2, 2026-11-07)
- **Stack (4 layers, 1.6 mm; JLC stack-up picked in block 3):** L1 front parts + signals; In1 GND plane; In2 split power planes +5V, +20V and PVDD; L4 back parts + signals. F/B GND pours with stitching vias to In1.
- **Rules (JLC capability page, checked 2026-11-07: 0.10/0.10 track/space, via 0.2/0.45 without surcharge):** tracks ≥ 0.15 mm except two 0.125 mm necks on CN at the TAS fan-out; clearance 0.15 (signals, PVDD, outputs) / 0.20 (default, 20 V); vias 0.45/0.2 signals, 0.6/0.3 power, 0.8/0.4 on the 20 V inlet; copper to edge 0.3.
- **TAS5756M escape:** signal pins on two staggered via rows 0.5 and 1.25 mm beyond the pin tips; GND pins stubbed onto the exposed land; PVDD pins bridged (6–7, 41–43) to one 0.6/0.3 via each with the 0.1 µF (C100, C121) directly behind on the back; bootstrap caps C104/C115 over pins 4–5 / 44–45 and C108/C111 upright beside pins 1/48 (moved from the placement for this); outputs 0.6 mm on the front to the inductors; footprint courtyard trimmed to body + land tongues.
- **Routing:** hand/maze pre-routes for the amplifier outputs, PVDD and the 20 V inlet (`gen/amp.py`, `gen/route_main.py` PREROUTES) → Freerouting 2.5.0 for the signals → maze-router fixes for what it left (POSTROUTES) → pours, stitching, dangling-via clean-up, silk placement. The KiCad board is the source of truth: Freerouting's result depends on the board's item order (random footprint UUIDs per placement run), so a regeneration routes differently and the POSTROUTES list fits this result only.
- **Moves made in layout:** R14 (PI_BCLK series position) to the J3 landing on the back (60.5, 39.5) – source termination at the source and two short hops instead of a 65 mm detour round the amplifier; TP18 dropped (PVDD at F5 pin 2).
- **Silkscreen:** 88 references on silk, 27 hidden where no clear spot exists (D1, U2, C1–C3, C10, C101, C112–C115, C118, C120, C122, R1, R3, R5, R6, R18, R26, R102, R104, R105, TP5–TP7, TP9, TP10); the block 3 assembly drawing (fab layers) carries every reference.
- **DRC (KiCad 9.0.9, `drc-report.txt`):** 0 errors, 0 unconnected, schematic parity clean; 1 warning – J2's footprint differs from the library copy because its outline past the board edge was removed from the silkscreen.

## Sources (read 2026-11-07 unless noted)
- TI TAS5756M, SLAS988B — https://www.ti.com/lit/ds/symlink/tas5756m.pdf
- TI TPS1663, SLVSET9G (rev. April 2026) — https://www.ti.com/lit/ds/symlink/tps1663.pdf
- TI TPS709, SBVS186H — https://www.ti.com/lit/ds/symlink/tps709.pdf
- TI SLAA701 rev B, LC filter design — https://www.ti.com/lit/an/slaa701/slaa701.pdf
- Mean Well NID100-SPEC 2024-10-30 — https://www.meanwell.com/Upload/PDF/NID100/NID100-SPEC.PDF
- GCT USB4105 drawing rev B4 (2023-12-18) — https://gct.co/files/drawings/usb4105.pdf; spec — https://gct.co/files/specs/usb4105-spec.pdf
- GCT USB4085 drawing rev B (2023-02-28), 3 sheets incl. recommended PCB layout — https://gct.co/files/drawings/usb4085.pdf
- CODACA CSBA0850 datasheet (revised 2026-03-16) — https://www.codaca.com/Private/Pdf/CSBA0850.pdf (via the DigiKey product page)
- Bourns SRR1260, REV. 03/26 — https://www.bourns.com/docs/product-datasheets/srr1260.pdf
- Würth WE-PD 7447709150, rev 006.001 — https://www.we-online.com/components/products/datasheet/7447709150.pdf
- Hynetek HUSB238A datasheet Rev. 1.0 (PDF dated 2024-08-07), www.hynetek.com
- Littelfuse 451/453 NANO2 — https://www.farnell.com/datasheets/1788341.pdf (power budget 2026-11-02)
- Littelfuse SMBJ — link in `claude/E0-power-budget-2026-11-02.md` (rev 06/03/20)
- Littelfuse 2920L, Bel 0ZCJ — links in `claude/E0-power-budget-2026-11-02.md`
- Raspberry Pi documentation, `computers/raspberry-pi/power-supplies.adoc` @ 21d772e (2026-11-05) — https://github.com/raspberrypi/documentation
- Raspberry Pi HAT+ specification — https://datasheets.raspberrypi.com/hat/hat-plus-specification.pdf
- raspberrypi/linux `arch/arm/boot/dts/overlays/rpi-digiampplus-overlay.dts`, `iqaudio-dacplus-overlay.dts`, `sound/soc/bcm/iqaudio-dac.c` — https://github.com/raspberrypi/linux
- Seeed ReSpeaker Lite repository (XIAO footprint pinout image `doc/images/pinout.png`) — https://github.com/respeaker/ReSpeaker_Lite
- DigiKey part numbers in the symbol fields: `claude/E0-order-list-2026-11-01.md` rev 4 §2.2 (seen 2026-11-01…03); new parts get theirs in block 3.
