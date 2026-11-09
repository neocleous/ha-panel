"""Mic strip: re-route with 0.3 mm via holes (D63 = b, Daniel 2026-11-09).

JLC's free via class is "0.3mm/(0.4/0.45mm)"; its 0.2 mm exemption is stated only for multilayer boards, and the strip
is 2 layers. A plain re-drill of the 0.2/0.45 vias breaks the board's 0.10 mm via ring and 0.25 mm hole clearance, so
the strip is re-routed instead:
- placement, footprints (incl. the ESD321 180-degree turn of decision 10.1), purchase fields, silk, rule areas and
  pours are kept from the current board;
- every track and via is removed and the routing of pcb_mic.py runs again (same connections, same order, same widths)
  with vias 0.5 / 0.3 (ring 0.10), less the two GND items in SKIP_DROP / SKIP_CONN (fewer vias, see below);
- new holes keep >= 0.3 mm edge to edge from every hole (mroute.hole_mask).
Run: python3 reroute_strip_vias.py <in.kicad_pcb> <out.kicad_pcb> [via_cost_mm] [noskip] [forbid]
<out>'s folder must hold the strip's .kicad_pro under the same name (zone refill takes the 0.3 mm copper-to-edge rule
from it; KiCad's default is 0.5)."""
import os
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mroute
import pcb_mic as pmic

MM = pcbnew.FromMM
VIA = (0.5, 0.3)
# The router rasterises the outline at 0.05 mm and can read up to 0.0625 mm too much edge distance: the routing put
# one /MIC_LR F.Cu vertex 0.275 from the bottom edge (rule 0.3). A wider router margin or a keep-out re-routes other
# nets (SEL_C then needs two vias and D3's ground via finds no spot), so the routing is kept and every track vertex
# closer than EDGE_MIN to an edge is moved inward instead (a segment is nearest a straight edge at an end point).
EDGE_MIN = 0.325
FORBID = {'/MIC_LR': [('F', -1.0, 5.55, 29.0, 7.0)]}     # tried, not used by default (see above)
SKIP_ENABLED = True


def nudge_from_edges(b, w_board, h_board, gap=EDGE_MIN):
    """Move track end points (and the coincident ends of same-net, same-layer tracks) inward so that the copper keeps
    `gap` from the rectangular outline. Returns the moves made."""
    tracks = [t for t in b.GetTracks() if t.GetClass() == 'PCB_TRACK']
    moves = []
    for t in tracks:
        for end in ('start', 'end'):
            p = t.GetStart() if end == 'start' else t.GetEnd()
            x, y, r = pcbnew.ToMM(p.x), pcbnew.ToMM(p.y), pcbnew.ToMM(t.GetWidth()) / 2
            nx = min(max(x, gap + r), w_board - gap - r)
            ny = min(max(y, gap + r), h_board - gap - r)
            if (nx, ny) == (x, y):
                continue
            q = pcbnew.VECTOR2I(MM(nx), MM(ny))
            for u in tracks:
                if u.GetNetCode() == t.GetNetCode() and u.GetLayer() == t.GetLayer():
                    if u.GetStart() == p:
                        u.SetStart(q)
                    if u.GetEnd() == p:
                        u.SetEnd(q)
            moves.append((t.GetNetname(), t.GetLayerName(), (round(x, 3), round(y, 3)), (round(nx, 3), round(ny, 3))))
    return moves
# Fewer vias where a route allows it (D63): R2 (100 k pull-down on the buffer input) carries no current and reaches
# GND through U1's ground on the back, so it gets no via of its own (this was the 0.24 mm GND pair); and C1's ground
# joins the rest through its own via and both pours, so the back-side GND route from R2 to C1 (two vias) is dropped.
SKIP_DROP = {(13.75, 3.00)}
SKIP_CONN = {('GND', (13.75, 3.00), (16.88, 1.25))}


def main(src, dst, via_cost=1.5, skip=True, forbid=False):
    global SKIP_ENABLED
    SKIP_ENABLED = skip
    b = pcbnew.LoadBoard(src)
    for t in list(b.GetTracks()):
        mroute.remove(b, t)
    nc = b.GetDesignSettings().m_NetSettings.GetDefaultNetclass()
    nc.SetViaDiameter(MM(VIA[0])); nc.SetViaDrill(MM(VIA[1]))
    box = (-1, -1, pmic.W + 1, pmic.H + 1)
    fails = []
    for net, a, c, w in pmic.CONN:
        if SKIP_ENABLED and (net, a, c) in SKIP_CONN:
            print('skip route', net, a, c)
            continue
        ok, info = mroute.route(b, net, a, c, w, pmic.CLASSES, via=VIA, box=box, via_cost_mm=via_cost,
                                forbid=FORBID.get(net, ()) if forbid else ())
        print('route', net, ok, info)
        if not ok:
            fails.append((net, a, c))
    print('edge nudges', nudge_from_edges(b, pmic.W, pmic.H))
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    for tgt in ((12.06, 1.97), (4.75, 2.23), (2.81, 3.00), (13.75, 3.00)):   # C3's ground onto the rest
        ok, info = mroute.route(b, 'GND', (11.95, 5.00), tgt, 0.25, pmic.CLASSES, via=VIA, box=box,
                                via_cost_mm=via_cost)
        print('route GND C3', tgt, ok, info)
        if ok:
            break
    for p in pmic.GND_PADS:                      # every GND pad gets its own via to the front pour, except SKIP_DROP
        if SKIP_ENABLED and p in SKIP_DROP:
            print('skip gnd via', p)
            continue
        ok, info = mroute.drop_via(b, 'GND', p, pmic.CLASSES, w=0.25, via=VIA, layer='B', margin=2.5)
        print('gnd via', p, ok, info)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    for _ in range(2):
        print('stitch', len(mroute.stitch(b, pmic.CLASSES, via=VIA)))
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    vias = [t for t in b.GetTracks() if t.GetClass() == 'PCB_VIA']
    print('vias', len(vias), 'tracks', sum(t.GetClass() == 'PCB_TRACK' for t in b.GetTracks()), 'route fails', fails)
    pcbnew.SaveBoard(dst, b)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 1.5,
         'noskip' not in sys.argv[4:], 'forbid' in sys.argv[4:])
