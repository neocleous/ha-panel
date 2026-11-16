"""Main board rev 3.2, fab issue 2026-11-16: the changes made with the fab files, applied to rev 3.2 as left on
2026-11-14 (claude/brief-electronics-fab-files-rev3-2-2026-11-16.md). Copper, texts and the stack-up only: no part,
pad, hole or outline changes, so main-board-rev3.2.step stands.

    gen/fab32.sh <rev 3.2 of 2026-11-14 .kicad_pcb> <work dir> [pad ...]      runs the planner, this script and the checks
    python3 fab32.py <rev 3.2 of 2026-11-14 .kicad_pcb> <via plan .json> <board out .kicad_pcb>   (the board out beside
                                                                              main-board.kicad_pro, see fab32_vias.rules)

  1. vias     the plan of fab32_vias.py: the vias that stood in or at pasted pads are moved clear of them.
  2. relief   the pours are kept RELIEF_KEEP back from the relief in the +u side edge (rule area on all four copper
              layers; pours only, tracks and vias are not touched). The board's rule is 0.30 to any edge; JLC's is
              0.2 with a routing tolerance of +-0.2 (capabilities page, read 2026-11-16). With the cut 0.2 deeper
              the pours now end 0.30 from the edge there instead of 0.10. Asked for by D151 item 6.
  3. text     title block and the back-face revision text carry the fab issue's date.
  4. stackup  JLC04161H-7628 written into the board file (the Python library has no call for it, so the saved file
              is edited as text and read back by KiCad): JLC's 4-layer stack for 1.6 mm, 1 oz outside, 0.5 oz inside
              (jlcpcb.com/impedance, read 2026-11-16).
Then every pour is refilled. KiCad 9's Python; PYTHONHASHSEED=0.
"""
import json
import os
import shutil
import sys

GEN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, GEN)
import pcbnew                      # noqa: E402
import fab32_vias                  # noqa: E402
from shapely.geometry import LineString, box   # noqa: E402
from shapely.ops import unary_union            # noqa: E402

MM, TO = pcbnew.FromMM, pcbnew.ToMM
U0, V0 = 43.5, 28.95
RELIEF_KEEP = 0.50                 # pours to the relief's edge
ISSUE = '2026-11-16'

# JLC04161H-7628, layer by layer (mm; relative permittivity as JLC's page gives it). Soldermask: JLC gives "at least
# 10 um" for the ink; KiCad's own default of 0.01 is kept.
STACKUP = '''		(stackup
			(layer "F.SilkS"
				(type "Top Silk Screen")
			)
			(layer "F.Paste"
				(type "Top Solder Paste")
			)
			(layer "F.Mask"
				(type "Top Solder Mask")
				(thickness 0.01)
			)
			(layer "F.Cu"
				(type "copper")
				(thickness 0.035)
			)
			(layer "dielectric 1"
				(type "prepreg")
				(thickness 0.2104)
				(material "7628")
				(epsilon_r 4.4)
				(loss_tangent 0)
			)
			(layer "In1.Cu"
				(type "copper")
				(thickness 0.0152)
			)
			(layer "dielectric 2"
				(type "core")
				(thickness 1.065)
				(material "FR4 core")
				(epsilon_r 4.6)
				(loss_tangent 0)
			)
			(layer "In2.Cu"
				(type "copper")
				(thickness 0.0152)
			)
			(layer "dielectric 3"
				(type "prepreg")
				(thickness 0.2104)
				(material "7628")
				(epsilon_r 4.4)
				(loss_tangent 0)
			)
			(layer "B.Cu"
				(type "copper")
				(thickness 0.035)
			)
			(layer "B.Mask"
				(type "Bottom Solder Mask")
				(thickness 0.01)
			)
			(layer "B.Paste"
				(type "Bottom Solder Paste")
			)
			(layer "B.SilkS"
				(type "Bottom Silk Screen")
			)
			(copper_finish "ENIG")
			(dielectric_constraints no)
		)
'''


def stage_relief(b):
    outl = pcbnew.SHAPE_POLY_SET()
    b.GetBoardPolygonOutlines(outl)
    board = unary_union(fab32_vias.polys(outl))
    # the relief's contour: the part of the outline inside u +41.5 ... +43.45, v +0.45 ... +14.05 (floor, arcs, side walls)
    win = box(41.5 + U0, V0 - 14.05, 43.45 + U0, V0 - 0.45)
    relief = board.exterior.intersection(win)
    assert 15.4 < relief.length < 15.7, 'relief contour not found: %.3f' % relief.length
    # the round ends of the band reach 0.5 round the two points where the side walls meet the old edge
    whole = board.exterior.intersection(box(41.5 + U0, V0 - 14.05, 43.6 + U0, V0 - 0.45))
    band = whole.buffer(RELIEF_KEEP, 24).simplify(0.001)
    z = pcbnew.ZONE(b)
    z.SetIsRuleArea(True)
    ls = pcbnew.LSET()
    for l in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu):
        ls.AddLayer(l)
    z.SetLayerSet(ls)
    z.SetZoneName('relief: pours %.2f from the edge' % RELIEF_KEEP)
    z.SetDoNotAllowCopperPour(True)
    z.SetDoNotAllowTracks(False)
    z.SetDoNotAllowVias(False)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    ol = z.Outline()
    ol.NewOutline()
    pts = list(band.exterior.coords)[:-1]
    for x, y in pts:
        ol.Append(MM(x), MM(y))
    b.Add(z)
    print('relief: rule area "%s" on four copper layers, %d corners, u %+.2f ... %+.2f, v %+.2f ... %+.2f' % (
        z.GetZoneName(), len(pts), band.bounds[0] - U0, band.bounds[2] - U0, V0 - band.bounds[3], V0 - band.bounds[1]))


def stage_text(b):
    tb = b.GetTitleBlock()
    tb.SetRevision('3.2')
    tb.SetDate(ISSUE)
    tb.SetComment(2, 'Fab issue %s: vias moved out of the pasted pads; pours %.2f from the relief; stack-up JLC04161H-7628 '
                     '(claude/brief-electronics-fab-files-rev3-2-2026-11-16.md)' % (ISSUE, RELIEF_KEEP))
    n = 0
    for d in b.GetDrawings():
        if d.GetClass() == 'PCB_TEXT' and d.GetText().startswith('REV 3.2 '):
            d.SetText('REV 3.2 ' + ISSUE)
            n += 1
    assert n == 1, 'revision text not found once'
    print('revision text: REV 3.2 %s' % ISSUE)


def stage_stackup(path):
    s = open(path).read()
    assert '(stackup' not in s
    i = s.index('(setup')
    j = s.index('\n', i) + 1
    s = s[:j] + STACKUP + s[j:]
    open(path, 'w').write(s)
    b = pcbnew.LoadBoard(path)                 # KiCad reads it and writes it back in its own form
    fab32_vias.rules(b)
    assert b.GetDesignSettings().m_HasStackup
    pcbnew.SaveBoard(path, b)
    t = open(path).read()
    for want in ('(thickness 0.2104)', '(thickness 1.065)', '(thickness 0.0152)', '(copper_finish "ENIG")'):
        assert want in t, want
    print('stack-up: JLC04161H-7628 in the board file, read back by KiCad')


def main(src, plan, dst):
    shutil.copy(src, dst)                      # dst lies beside main-board.kicad_pro (gen/fab32.sh)
    b = pcbnew.LoadBoard(dst)
    fab32_vias.rules(b)
    print('vias changed: %d' % fab32_vias.apply(b, json.load(open(plan))))
    stage_relief(b)
    stage_text(b)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(dst, b)
    stage_stackup(dst)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
