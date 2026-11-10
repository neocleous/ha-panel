### Holes
| Hole | u | v | Band (site section 2) | Nearest display mounting point |
|---|---|---|---|---|
| H1 | -37.00 | +22.00 | top band v +18.0...+25.5 | 18.2 |
| H2 | +30.00 | +25.00 | top band v +18.0...+25.5 | 9.1 |
| H3 | -31.00 | -25.25 | bottom band v -25.25 +/- 0.2 | 12.1 |
| H4 | +31.00 | -25.25 | bottom band v -25.25 +/- 0.2 | 8.1 |

### Connectors
| Ref | Lead | Type | Pin 1 (u, v) | Last pin (u, v) | Box on the board u | Box v | Mating | Plugged |
|---|---|---|---|---|---|---|---|---|
| J9 | Speaker right | JST B2B-XH-A, through-hole, top entry | -40.25, -25.00 | -37.75, -25.00 | -43.24...-34.76 | -28.95...-22.11 | plug toward the board (-w) | in place, door off |
| J3 | Pi signal leads, 9 (10 pads) | wire pads 2 x 5, 2.54 pitch, hole dia 1.0 | -25.30, -27.00 | -15.14, -24.46 | -26.45...-13.99 | -28.15...-23.31 | wires soldered | bench |
| J1 | 20 V from the inlet board | JST B2B-XH-A | -1.25, -25.00 | +1.25, -25.00 | -4.25...+4.25 | -28.95...-22.11 | plug toward the board (-w) | in place, door off |
| J4 | Pi signal leads, 4 | wire pads 2 x 2, 2.54 pitch | +5.65, -27.00 | +8.19, -24.46 | +4.50...+9.34 | -28.15...-23.31 | wires soldered | bench |
| J6 | Touch board | JST B4B-XH-A, long side along v | +12.30, -25.94 | +12.30, -18.44 | +9.40...+16.25 | -28.93...-15.45 | plug toward the board (-w) | in place, door off |
| J2 | Pi power | GCT USB4085-GF-A, through-hole, door-side face | +18.65, -20.34 | +24.60, -20.34 | +16.30...+26.95 | -29.50...-19.23 | plug upward (+v) into the bottom edge | in place, door off |
| J8 | Speaker left | JST B2B-XH-A | +37.50, -25.00 | +40.00, -25.00 | +34.51...+42.99 | -28.95...-22.11 | plug toward the board (-w) | in place, door off |
| J5 | Radar | JST B4B-XH-A, long side along v | -40.30, -17.60 | -40.30, -10.10 | -43.20...-36.35 | -20.59...-7.11 | plug toward the board (-w) | in place, door off |
| J10 | BME680 | 1 x 4 pin header 2.54, for a 1 x 4 Dupont housing | -34.30, -10.30 | -34.30, -17.92 | -36.12...-32.48 | -19.73...-8.48 | housing toward the board (-w) | in place, door off |
| J11 | VEML6030 | 1 x 4 pin header 2.54, for a 1 x 4 Dupont housing | -4.50, -12.00 | +3.12, -12.00 | -6.32...+4.93 | -13.81...-10.19 | housing toward the board (-w) | in place, cap held above, door off |
| J7 | Echo-reference tap to the ReSpeaker (second option only) | wire pads 1 x 8, 2.54 pitch | -29.50, +24.20 | -11.72, +24.20 | -30.65...-10.57 | +23.05...+25.35 | wires soldered | bench, only if the second option is built |

### Parts 5 mm or taller on the door-side face
| Part | What | u | v | Height w | Allowed there | Limit from | Source of the height |
|---|---|---|---|---|---|---|---|
| PS1 | NID100-5 | -37.4...+14.0 | -4.6...+8.0 | 27.5 | 28.9 | cap side-screw key path | NID100-SPEC 2024-10-30 (27.5 +/- 1) |
| C5 | 120u 63V | -8.3...+2.3 | +8.6...+19.2 | 16.0 | 33.0 | door | EEU-FR1J121B dia 10 x 16 (MAIN_env rev 2.1) |
| C6 | 120u 63V | -32.3...-21.7 | +8.6...+19.2 | 16.0 | 24.0 | cap back-screw key path | EEU-FR1J121B dia 10 x 16 (MAIN_env rev 2.1) |
| C7 | 22u 35V | +5.7...+11.3 | +8.6...+14.2 | 12.5 | 35.0 | door | Wurth 860160572003, 12.5 max (MAIN_env rev 2.1) |
| L1 | 15u SRR1260 | -21.5...-8.5 | +8.6...+21.7 | 6.5 | 32.0 | door | MAIN_env rev 2.1 (KiCad model: 6.0) |
| L100 | 10u | +30.6...+40.8 | -19.0...-9.4 | 5.4 | 40.0 | door | MAIN_env rev 2.1 (CODACA: body 5.1) |
| L101 | 10u | +30.6...+40.8 | -9.4...+0.2 | 5.4 | 33.0 | door | MAIN_env rev 2.1 (CODACA: body 5.1) |
| L102 | 10u | +20.4...+30.6 | -9.4...+0.2 | 5.4 | 35.0 | cap side-screw key path | MAIN_env rev 2.1 (CODACA: body 5.1) |
| L103 | 10u | +20.4...+30.6 | -19.0...-9.4 | 5.4 | 42.0 | door | MAIN_env rev 2.1 (CODACA: body 5.1) |
| J1 | 20 V in socket | -4.2...+4.2 | -28.9...-22.1 | 7.00 bare; 9.8 mated (JST); 20 with the lead bend | 51.0 | door | JST XH top-entry header, KiCad model (plug mated 9.8, JST catalogue) |
| J8 | speaker left socket | +34.5...+43.0 | -28.9...-22.1 | 7.00 bare; 9.8 mated (JST); 20 with the lead bend | 44.0 | door | JST XH top-entry header, KiCad model (plug mated 9.8, JST catalogue) |
| J9 | speaker right socket | -43.2...-34.8 | -28.9...-22.1 | 7.00 bare; 9.8 mated (JST); 20 with the lead bend | 46.0 | door | JST XH top-entry header, KiCad model (plug mated 9.8, JST catalogue) |
| J6 | touch board socket | +9.4...+16.2 | -28.9...-15.4 | 7.00 bare; 9.8 mated (JST); 20 with the lead bend | 48.0 | door | JST XH top-entry header, KiCad model (plug mated 9.8, JST catalogue) |
| J5 | radar socket | -43.2...-36.4 | -20.6...-7.1 | 7.00 bare; 9.8 mated (JST); 20 with the lead bend | 40.0 | door | JST XH top-entry header, KiCad model (plug mated 9.8, JST catalogue) |
| J10 | BME680 socket | -36.1...-32.5 | -19.7...-8.5 | 8.65 bare; about 16.5 with the housing (estimate); 25 with the lead bend | 41.9 | cap side-screw key path | pin header, KiCad model (with a Dupont housing about 16.5, estimate) |
| J11 | VEML6030 socket | -6.3...+4.9 | -13.8...-10.2 | 8.65 bare; about 16.5 with the housing (estimate); 25 with the lead bend | 47.0 | door | pin header, KiCad model (with a Dupont housing about 16.5, estimate) |
| J2 | Pi power socket | +16.3...+26.9 | -29.5...-19.2 | 3.46 bare; 3.46; the plug hangs below the edge; n/a with the lead bend | 48.0 | door | GCT drawing USB4085 rev B |

### Through-hole pin ends on the back face
| Part | Pin ends at u | at v | Beyond the back face | Allowed there | Zone | Basis |
|---|---|---|---|---|---|---|
| C5 | -5.5...-0.5 | +13.9...+13.9 | 1.5 | 4.0 | over the ReSpeaker | leads cut after soldering (assumed, to be kept to on the bench) |
| C6 | -29.5...-24.5 | +13.9...+13.9 | 1.5 | 4.0 | over the ReSpeaker | leads cut after soldering (assumed, to be kept to on the bench) |
| C7 | +7.5...+9.5 | +11.4...+11.4 | 1.5 | 4.0 | over the ReSpeaker | leads cut after soldering (assumed, to be kept to on the bench) |
| J1 | -1.2...+1.2 | -25.0...-25.0 | 1.9 | 12.0 | bottom band | post 3.48 below the seating plane (KiCad model of JST XH) - 1.6 |
| J2 | +17.3...+25.9 | -24.7...-20.3 | 0.5 | 4.0 | over the ReSpeaker | shell stakes 2.10, signal tails 1.60 (GCT drawing) - 1.6 |
| J3 | -25.3...-15.1 | -27.0...-24.5 | 1.5 | 12.0 | bottom band | wire pads: wire end or solder cone (assumed); the lead itself may leave this face |
| J4 | +5.7...+8.2 | -27.0...-24.5 | 1.5 | 12.0 | bottom band | wire pads: wire end or solder cone (assumed); the lead itself may leave this face |
| J5 | -40.3...-40.3 | -17.6...-10.1 | 1.9 | 4.0 | over the ReSpeaker | post 3.48 below the seating plane (KiCad model of JST XH) - 1.6 |
| J6 | +12.3...+12.3 | -25.9...-18.4 | 1.9 | 4.0 | over the ReSpeaker | post 3.48 below the seating plane (KiCad model of JST XH) - 1.6 |
| J7 | -29.5...-11.7 | +24.2...+24.2 | 1.5 | 5.0 | top band | wire pads (second echo-reference option only) |
| J8 | +37.5...+40.0 | -25.0...-25.0 | 1.9 | 12.0 | bottom band | post 3.48 below the seating plane (KiCad model of JST XH) - 1.6 |
| J9 | -40.2...-37.8 | -25.0...-25.0 | 1.9 | 12.0 | bottom band | post 3.48 below the seating plane (KiCad model of JST XH) - 1.6 |
| J10 | -34.3...-34.3 | -17.9...-10.3 | 1.5 | 4.0 | over the ReSpeaker | pin 3.11 below the seating plane (KiCad model) - 1.6 |
| J11 | -4.5...+3.1 | -12.0...-12.0 | 1.5 | 4.0 | over the ReSpeaker | pin 3.11 below the seating plane (KiCad model) - 1.6 |
| LK1 | +6.9...+14.5 | -11.2...-11.2 | 1.5 | 4.0 | over the ReSpeaker | wire cut after soldering (assumed) |
| PS1 | -35.8...+12.5 | -0.3...-0.3 | 2.9 | 4.0 | over the ReSpeaker | pins 4.5 long (NID100-SPEC) - 1.6 |

### Plugged connectors: nearest part taller than the mated plug
| Connector | Plug top w | Nearest taller part | Its height | Gap between the boxes | Direction from the connector |
|---|---|---|---|---|---|
| J9 | 9.8 | J10 | 16.5 | 2.4 | above (+v) |
| J1 | 9.8 | J11 | 16.5 | 8.3 | above (+v) |
| J6 | 9.8 | J11 | 16.5 | 4.8 | above (+v) toward -u |
| J8 | 9.8 | PS1 | 27.5 | 26.9 | above (+v) toward -u |
| J5 | 9.8 | J10 | 16.5 | 0.2 | toward +u |
| J10 | 16.5 | PS1 | 27.5 | 3.9 | above (+v) |
| J11 | 16.5 | PS1 | 27.5 | 5.6 | above (+v) |

### Runs on the board (pad to pad, along u plus along v)
| Run | From - to | Length |
|---|---|---|
| 20 V in to the inlet protection | J1.1 - F1.1 ; F1.2 - U1.1 | 13 |
| Inlet protection to the 20 V filter | U1.19 - C5.1 ; C5.1 - L1.1 ; L1.2 - C6.1 ; C6.1 - PS1.9 | 72 |
| 5 V to the Pi power socket | PS1.1 - F2.1 ; F2.2 - LK1.1 ; LK1.2 - J2.A9 | 33 |
| 20 V to the amplifier | C5.1 - F5.1 ; F5.2 - U100.6 | 55 |
| Speaker left, filter to socket | L100.2 - J8.1 | 12 |
| Speaker right, filter to socket | L103.2 - J9.1 | 73 |
| Bit clock, Pi pad to amplifier | J3.6 - U100.23 | 92 |
| Radar supply | F3.2 - J5.1 | 18 |
