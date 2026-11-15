# rev F — the front shell split (2026-11-14 / 15)

Brief: `claude/brief-enclosure-front-shell-split-2026-11-14.md` (D140, D141). Print side: `claude/finding-front-shell-split-2026-11-14.md`.
Closing report: `claude/report-enclosure-split-2026-11-15.md`. Block 1 study and questions: `claude/report-enclosure-split-block1-2026-11-14.md`.

**Model:** "HA Panel v5 - tapered" version 63 (g18) → **version 64 (g19)**, archive `~/Documents/HA Panel v5 - tapered revF-g19.f3d` (183,015,526 bytes).
Not for print.

## Decisions (Daniel)
- **1a** — the boxes' top screws go into the screen plate (2026-11-15 01:18).
- **2a** — thin screen plate (the slab's seat only, back d 12.8), **printed black**, showing as an **even 1 mm shadow gap all round** (2026-11-15 01:18 / 11:59).
- **3a** — plate on the shell first; the display module rides in as now (2026-11-14 23:15).

## What the model now holds
| Body | What | Volume mm³ |
|---|---|---|
| `HOUSING_F_plate` (new, black) | the seat in front of d 12.8 inside x ±98.75, up −89.93…34.77; LCD opening, notches, 4 LCD screw holes; box-top insert holes Ø4.0 through on the 10° lines; 4 × Ø3.4 plate-screw holes; Ø7.25 pocket (left bottom), 8.75 × 7.25 slot (right bottom), both 1.4 deep | 68,255.48 |
| `HOUSING_F_front` (the rest of the shell) | the one-piece shell minus the plate, minus the 2 mm layer between the side walls, nothing in front of d 13.0 (frame's back edge d 12.0: 1 mm gap all round), old box-top bosses gone; 4 bosses Ø9 (top two columns d 12.8…26, bottom two d 12.8…19.4 on webs to the side walls with Ø7.0 × 1.2 pegs), Ruthex holes Ø4.0 × 6.35; lip top 0.15 lower at the tongues | 104,428.62 |
| `SPKBOX_L` / `SPKBOX_R` | top lug moved 3.168 along its screw line (front y −0.78, 0.3 behind the plate at z 84), 45° gusset under the overhang, pocket Ø5.2 for the insert's end (0.59 in, 0.1 short), clearance Ø3.6 | 26,086.63 / 26,807.97 |
| `FLOOR_PLATE` | 0.4 × 45° lead-in chamfer under both tongue noses (x ±24.7…35.3) | 32,450.57 |
| `*_v63` (hidden) | the four bodies as at version 63; `HOUSING_F_front_v63` is the one-piece fallback | — |

## Files
| File | What |
|---|---|
| `lib/split_lib.py` | sections of model bodies by planes (x, z, slab-parallel d), DP-simplified |
| `s0_preflight.py`, `s0b_finding_numbers.py` | block 0: counts; the finding's chin face and plate back |
| `s1_*.py`, `s1p_add.py`, `b1_pictures.py`, `label.py`, `data/` | block 1: sections, candidate checks, picture templates and drawings |
| `s2_split_calls.py` | block 2: the split, the lugs and noses, save g19, archive |
| `s3_check_calls.py` | block 3: interference against the measured reference, ride-in, A1–A3, key lines, masses |
| `img/` | the pictures shown to Daniel (`p1`…`p4` are the re-asked questions) |

## Lessons
- **181** aud4_lib's `tl()` caches a body's temporary copies by name only (`R[('tl', name)]`), and its crops are built from them. After a body changes under the same name, pop that key and its crops, or the check runs against the old body: the first ride-in reported 0.08 "to the shell" at the old wall's back face.
- **182** The rev 3.2 pass's namespaces (`r32.k4`, `r32a`) carry their own `v5f_k` instance. `k.budget()` on `sys.modules['v5f_k']` does not reach them: call `r32.k4['k'].budget(n)` / `r32a.k.budget(n)`. A stale deadline makes every slab build and matrix pair "late" at once (the matrix stopped after 8 s with 548 left).
- **183** A leaning face (the plate's back, 12°) against a square one (a box lug): set the clearance at the square face's extreme height, not at the screw's: 0.3 at z 80 was 0.54 into the plate at the lug's top (z 84).
- **184** Cutting a slab-parallel band out of the shell also takes the side walls' fronts. Keep what runs on behind the band: take the section just behind it (d 14.85…15.65), extrude it forward (four copies 0.8 apart) and subtract that from the band before removing it. A picture template made without this showed a dark gap that the model does not have.
- **185** An even visible gap to a frame whose back edge is at one depth all round is one cut: remove everything of the shell in front of a single depth inside the frame's footprint, then add the deliberate lands back (here 101.0 mm³ in front of d 12.99: four lands and two pegs).
- **186** Questions to Daniel: name the parts he knows and show them in 3D from where he would look (from behind through the door opening, from the side); two-dimensional sections with new part names were not understood.
