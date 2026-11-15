# Assembly audit — the front shell's split (2026-11-15)

Brief: `claude/brief-assembly-audit-split-2026-11-15.md`. Report: `claude/report-assembly-audit-split-2026-11-15.md`.
Hand-over: `claude/handover-assembly-audit-split-2026-11-15.md`. New issue of the instructions: `claude/assembly-instructions-2026-11-15.md`.

**Model:** "HA Panel v5 - tapered" **version 64 (g19)**, unchanged by the audit.
- Every check ran read-only.
- The picture calls added `AUD_*` templates, deleted afterwards. The document was then closed without saving and version 64 opened again.
- Guard volumes and counts were the same at the end as at the start.

**Verdict:** buildable and serviceable at version 64 with Daniel's tools: **yes with the findings listed** (F44 to F50).

## Files
| File | What |
|---|---|
| `aud5x_lib.py` | Small additions to `aud4_lib.py` for this audit. Contents: items from body names and crops; the tool-line check with a time limit; the box-top screw lines and heads; the plate's box-top insert as a body |
| `aud5p_pictures.py` | The three pictures of the new issue (`step19_plate`, `step21_key`, `step23_notches`) and the copies of five earlier ones under their new step numbers. Not read-only: templates `AUD_*`, deleted after use |
| `aud5_calls.py` | A typed record of the calls. Blocks 0 and 1 are described with their result keys; blocks 2 to 4 are copied, condensed |
| `cloth_edge.py` | Where the cloth's side edge must end on a side wall's rounded front corner to stay 0.1 behind the screen plate's back (F47), for cloth 0.7, 1.0 and 1.2 thick |

The libraries are loaded from `docs` by git blob hash under fresh module names: `aud5k`, `aud5m`, `aud5`, `aud5x`, `aud5p` (see `aud5_calls.py`).

The pictures are on the Mac in `~/Documents/HA_panel_renders/audit-split/` and were sent in the chat. They are not in the repo: the connector writes text files only.

## Lessons
- **187** The connector stops waiting after 80 s, but the script runs on, and every later call queues behind it (Fusion runs scripts one at a time); status polls time out too. Booleans against the one-piece shell's eight slabs cost 2 to 4 s each. Rules:
  - put a time check inside every loop;
  - keep each result in `R` as it comes, so that the same call resumes where it stopped.
- **188** The enclosure chat's box-top line (BOXTOP p0, left) lies 0.047 off version 63's true hole axis: the iron came out at +2.41 against the print re-check's +2.36. Reproduce a template on the model's own hole axes (`k.holes_of`), not on a document's line.
- **189** `k.holes_of(body, rmin, rmax)` takes **radii**, not diameters. Called with (4.0, 4.3) for Ø4 holes, it returned the Ø8.0 to 8.6 cylinders instead: the lip's ten magnet pockets, the eight driver-screw head pockets and three K5 lane holes. Called with (7.9, 8.8) it returned nothing. Print the radius of what it returns before using it. Reading cylinder faces directly also works: radius, axis, and the centres of the two circular edges for mouth and floor. One of the ten pockets has split edges and was taken as its mirror.
- **190** Parts that touch by design (driver flanges on the shell, the base plate's rim) give a minimum distance of 0 whatever the play. To find play in one direction, step the part in small steps and look for volume (`X.xv`), not distance.
- **191** Keep-out bodies drawn for a screw's tool path do not move when the screw's seat moves. At version 64 the display screws' heads came 1.0 forward (thinner seat), and the four `KO_K5_*` keep-outs still start at the old head. Check keep-outs against the current head before using them as the tool's path (F50).
- **192** Bounding boxes of temporary bodies are in the design's frame, not the world frame of the reports. Convert with `k.W` before comparing them with world numbers, or compare boxes only with boxes.
- **193** `viewport.saveAsImageFile` writes the picture on the Mac. The local Filesystem server's `read_media_file` brings that file, at its full size, into the cloud session to be sent in the chat. The connector's screenshot query gives only the viewport at its own size.
