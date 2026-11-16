"""The four copper layers at the relief, before and after the pours were kept back: relief_picture.py old new out.png"""
import sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MP
import pcbnew
TO = pcbnew.ToMM; U0, V0 = 43.5, 28.95
def uv(p): return (TO(p.x) - U0, V0 - TO(p.y))
LAY = ((pcbnew.F_Cu, 'door side'), (pcbnew.In1_Cu, 'layer 2 (ground)'), (pcbnew.In2_Cu, 'layer 3 (amplifier supply)'), (pcbnew.B_Cu, 'back'))
fig, axs = plt.subplots(2, 4, figsize=(13, 13.5), dpi=120)
for row, (path, lab) in enumerate(((sys.argv[1], 'rev 3.2 of 2026-11-14: pours 0.30 from the edge'), (sys.argv[2], 'fab issue 2026-11-16: pours 0.50 from the relief'))):
    b = pcbnew.LoadBoard(path)
    outl = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(outl); o = outl.Outline(0); edge = [uv(o.CPoint(i)) for i in range(o.PointCount())]
    for col, (lay, name) in enumerate(LAY):
        ax = axs[row][col]
        ax.add_patch(MP(edge, closed=True, fc='#f4f1e8', ec='k', lw=1.0, zorder=0))
        for z in b.Zones():
            if z.GetIsRuleArea() or not z.IsOnLayer(lay): continue
            sps = z.GetFilledPolysList(lay)
            for k in range(sps.OutlineCount()):
                oo = sps.Outline(k); pts = [uv(oo.CPoint(i)) for i in range(oo.PointCount())]
                if max(p[0] for p in pts) > 38:
                    ax.add_patch(MP(pts, closed=True, fc='#d98880' if lay in (pcbnew.F_Cu, pcbnew.In2_Cu) else '#7fb3d5', ec='none', zorder=1))
                    for h in range(sps.HoleCount(k)):
                        hh = sps.Hole(k, h); ax.add_patch(MP([uv(hh.CPoint(i)) for i in range(hh.PointCount())], closed=True, fc='#f4f1e8', ec='none', zorder=1.1))
        for t in b.GetTracks():
            if t.Type() != pcbnew.PCB_VIA_T and t.GetLayer() == lay:
                a, c = uv(t.GetStart()), uv(t.GetEnd())
                if max(a[0], c[0]) > 38: ax.plot([a[0], c[0]], [a[1], c[1]], color='k', lw=TO(t.GetWidth()) * 72 * 3.1 / 5.0, solid_capstyle='round', alpha=0.55, zorder=2)
        ax.set_xlim(39.5, 44.0); ax.set_ylim(-1.5, 16.0); ax.set_aspect('equal'); ax.set_title(name + ('\n' + lab if col == 0 else '\n'), fontsize=8, loc='left'); ax.tick_params(labelsize=6)
        ax.axvline(42.0, color='g', lw=0.4, ls=':'); ax.axvline(41.8, color='r', lw=0.4, ls=':')
fig.suptitle('Main board rev 3.2: copper at the relief in the +u side edge (u, v in mm; green dots: the floor as drawn, u +42.0; red dots: the cut 0.2 deeper, u +41.8; tracks in grey)', fontsize=9)
fig.tight_layout(rect=(0, 0, 1, 0.97)); fig.savefig(sys.argv[3]); print('wrote', sys.argv[3])
