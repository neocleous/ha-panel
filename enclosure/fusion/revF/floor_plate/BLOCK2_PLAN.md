# Floor plate pass – block 2 plan (2026-11-10, after Daniel's "1 a, 2 a" at 14:22)

Decisions: the base plate is the whole underside out to the edge and the speakers ride on it (1 a); the main board goes
behind the display on a new carrier, confirmed in the model first, fallback = bracket on the plate (2 a).
State of the model when this was written: version 42, modified only by the seven hidden `AUD_*` templates, nothing cut.
Delete the `AUD_*` bodies before the first write (rebuilt for block 4 with `v5f_f0c_aud_tools.py`).

All numbers below are from the model (f1a/f1b/f1c/f1d) unless marked "choice".

## Changes to the concept sketch found while planning
1. **No plate screws at the back corners.** The sketch put a post on the side wall at (±75, −49.5) inside the box's
   footprint; the box rises past it from below, so it would need a full-height notch. Behind the boxes (y < −52) the only
   shell material is the 1.2 lip; the door's bottom flange (z 2.8–3.6, inner line (74.6, −55.3) → (72.9, −57.1) →
   (69.4, −60.2)) and the box's rear face leave no room for a post rooted in the wall. The plate is tied to the shell by
   the two box-top screws (through the boxes), the front tongues, and to the door by its four screws. Load path when the
   unit is lifted by the shell: tongues and tab screws carry the weight; the rear-heavy moment is taken by the tab screws
   (axial) against the driver frames on their stops.
2. **Slide.** Wall clearance at the boxes' rear-outboard corners is 0.48 (box 1.2 off INNER_E, D1 layer 0.7), and moving
   a box back by d closes 0.60 d there: the boxes can sit at most 0.4–0.5 behind their final place during the lift.
   The plate slides 2.0 (tongues), so the box screws sit in slots in the plate (choice: 2.4 of travel): lift with the
   plate 2.0 back and the boxes 0.4 back, push the plate forward, the boxes stop on the driver stops after 0.4 and the
   plate travels on; tab screws, then the box-bottom screws.

## Parts
### FLOOR_PLATE (new)
- Blank: REF_F_outer ∩ z 0…2.5 (the body's own bottom 2.5 mm, rim = lower part of the R6 edge).
- Carried over from the floor (positions from the shell): foot recesses Ø13 × 0.5 at (±80, −11.5), (±30, −69); door-screw
  holes Ø3.4 + Ø6.5 × 1.0 at (19, −74.5), (−19, −77), (±50, −67) with the Ø8 pads to z 2.8; intake field (475 × Ø2 on 3.0,
  centres read from the shell); Pi posts Ø7.6 to z 8.0 with Ø4.0 holes at (18.35, −5.5), (−39.65, −5.5), (18.35, −54.5),
  (−39.65, −54.5); cradle posts at (6.5, −72.5), (−1.5, −72.5); zip-tie anchors (±58.5, −56.5). Not carried: bracket bosses
  (49.5, −58), (−65, −57).
- New: box pads to z 3.7 (the boxes keep their bottom at z 3.7) with slotted holes and slotted counterbores at about
  (±51, −12), (64, −45), (−72, −38), plus one plain pad per box; two tongues at x ±28 (upstand y −0.9…1.2, nose into a slot
  z 3.3–4.5 in the chin block).
### HOUSING_F_front
- Cut below z 2.8; floor-standing features removed; the cove removed along the sides and rear-front (|x| ≥ 46, y ≤ −3) so
  the boxes pass (shell edge there 1.46 wide: print orientation is an open issue), kept at the chin centre.
- Tongue slots; tab bosses with Ø4.0 insert holes on the wall behind the screen at (±57.5, z 79.5) (lane edge 53.55 on +x,
  LCD opening's lower edge at Zd −57.4); baffle: stop pads moved off the frame corners, pockets for the driver-screw heads.
### SPKBOX_L / SPKBOX_R
- Bottom unchanged (z 3.7, on the plate's pads); two floor bosses with Ruthex M3 from below.
- Through-tubes and rear-wall bores removed; four front bosses with Ø2.5 pilots at the frame holes (52.8 / 88.2, z 10.2 /
  45.7) for DIN 912 M3 × 10 self-tapping (the type already in the schedule); pegs removed.
- Top tab at |x| 57.5, y −6.2…−3.7, hole Ø3.6 at z 79.5 (round: positive vertical hold), two print ribs beside the key
  lane. −x box: the key lane (Ø5 at z 79.5) crosses the hump (front band y −24…−10, inboard band x −56.9…−46): notch it.
- Touch-board clips stay as they are (screwed to the box ears from the back after the lift-in).
### Display stack
- RESP_CARRIER v2: plate as today on the LCD's Pi standoffs, ReSpeaker bosses 4 mm lower (Zd −48…−14), four Ø7 posts with
  Ø4.0 holes (Ruthex M2.5) at x_rel 2.55 ± 41.5, Zd −9.5 / −52.5, to depth 23.7 behind the LCD PCB (design Y −31.1).
- Main board: centre (x_rel 2.55, Zd −28.5), back face at design Y −31.1 (0.5 over the ReSpeaker's 6.83 J2), parts toward
  the door, same way up; fitted from the back. f1d (back face at Y −32.0): NID100 to the lip ≈ 1.5, crosses the cap's
  back-right key lane, board corners 1 mm into the display-screw lanes.
- MAIN_BRACKET retired. Leads re-routed and measured in block 3 (to the Architect).

## Order of work
f2a inventory probe (read-only) → f2x main-board fit (read-only) → f2b delete AUD, back up originals as `<name>_v42`,
plate + shell → f2c boxes → f2d shell additions → f2e carrier, ReSpeaker, main board → f2f interference of every changed
part against every current body, lanes, door; lift-in sweep (plate 2.0 back, boxes 0.4 back; then the slide) → f2g save
"rev F WIP 2026-11-10 f2: base plate … (Claude)" + f3d.
