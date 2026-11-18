# rev F g22: design-for-FDM fixes (version 66 -> 67)

2026-11-18. Brief: `claude/brief-enclosure-fdm-fixes-2026-11-18.md` (project). Governing input: `claude/handover-fdm-design-audit-v66-2026-11-18.md`.

**Not for print. No print file was exported.** Saved as "rev F WIP 2026-11-18 g22: FDM fixes (FDM2-FDM13, D222-D228) - not for print" = version 67; archive `~/Documents/HA Panel v5 - tapered revF-g22.f3d`.

| File | What |
|---|---|
| `c3_lib.py` | sections, pictures, face lists, delta and outer-skin helpers |
| `c3_fix.py` | door bars, base noses, boxes and clips (pilot), cap slots, cradle bezel (not kept) |
| `c3_shell.py` | inner-skin tool, lip layer, shell work copy |
| `c3_calls.py` | the shell steps as run, the right box's rear slot, the cap's repair, guard volumes of version 67 |

Load in Fusion: `c3k` = `floor_plate/fusion/v5f_k_lib.py`, `k.K4NS` = `v5f_k4a_unit_checks.py`, then `c3` = the three `c3_*.py` files by commit sha (the loader keeps its URL inside the function, lesson 223).

## Lessons (continue from 222)
223. Connector scripts share one global namespace. A later script's global replaced one a stored function had closed over. Keep constants inside functions.
224. A script that raises takes its document changes back (bodies it added included). What it stored in Python memory stays.
225. Delete-face with heal on the shell took 55 s and removed 3,456 mm3 and 34 faces. Not used.
226. Two volume reads of the shell differ by up to 15 mm3. Quote what a fix adds from the tool's own boolean, not from two reads.
227. `shellFeatures` on a copy of INNER_E gives the existing inner-skin tools exactly (2.1: 194,500.267).
228. A plane's `geometry.normal` is not the face's outward normal. Use `face.evaluator.getNormalAtPoint`.
229. Shell booleans with ring-shaped skin tools take 25 to 50 s each, with small tools under 1 s; `lumps` on the shell 30 s; deleting a body 30 s. One heavy step per call. The connector gives up after 80 s while Fusion carries on: never send the call again, read the state.
230. Extruding a planar face of a real body as a new body gives exact prisms for fills and cuts. Positive distance runs along the outward normal; prove the direction with "prism minus body".
231. A seam of no width survives "union a box, subtract the box's outside part": the outside part carries the hairline. Extrude the seam face both ways and union.
232. Thin slit between two levels: tool = (slice beyond) AND (slice before), stacked through the slit. It fills only air that has solid on both sides.
233. A seat floor that meets an inclined wall leaves an acute groove under the wall's edge. Moving the floor past that edge removes it (shell, y -55.0 -> -55.2).
234. A cut box across a pocket's footprint took v66 material with it and left the cap in 5 lumps. Rebuild from the backup plus the fill's own shape.
235. The cap's corner pins are the microphone strips' seats at z 177.6. Fills beside them end at 177.6, not at the rim's 177.5.
236. The outer-skin check caught the cradle's bezel 0.05 further out (10.924 -> 15.921). Put back; the bezel stays 0.80.
237. `findBRepUsingRay` takes 0.1 s a ray on this model. No good for sampling gaps.
238. The folder-access request was refused. Pictures were read through the Filesystem connector (lesson 204).
239. The base plate's noses sit over the shell's lips (lip top 4.05, nose underside 4.35), not under them.
240. The cloth groove is 1.5 wide. It was 1.3 deep and is 0.8 deep now.
241. Bodies committed with `swap` go to the end of the body list, so pair keys of the interference table swap order. Compare with unordered pairs.
