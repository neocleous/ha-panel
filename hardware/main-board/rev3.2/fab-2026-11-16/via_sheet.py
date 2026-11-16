"""Before and after of every via the fab issue moved, door side up: pads (dark red) with their soldermask openings
(yellow), tracks (door side red, back blue), pours (light), vias (green, hole white). One pair of panels per via.
    python3 via_sheet.py <old board> <new board> <via-plan.json> <out.png>"""
import json
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon as MP
import pcbnew

TO = pcbnew.ToMM
U0, V0 = 43.5, 28.95


def uv(p):
    return (TO(p.x) - U0, V0 - TO(p.y))


def rings(sps):
    return [[uv(sps.Outline(k).CPoint(i)) for i in range(sps.Outline(k).PointCount())] for k in range(sps.OutlineCount())]


class Board:
    def __init__(self, path):
        b = self.b = pcbnew.LoadBoard(path)
        self.fill = []
        for z in b.Zones():
            if z.GetIsRuleArea():
                continue
            for lay, col in ((pcbnew.F_Cu, '#f5b7b1'), (pcbnew.B_Cu, '#aed6f1')):
                if z.IsOnLayer(lay):
                    sps = z.GetFilledPolysList(lay)
                    for k in range(sps.OutlineCount()):
                        o = sps.Outline(k)
                        holes = [[uv(sps.Hole(k, h).CPoint(i)) for i in range(sps.Hole(k, h).PointCount())] for h in range(sps.HoleCount(k))]
                        self.fill.append(([uv(o.CPoint(i)) for i in range(o.PointCount())], holes, col))
        self.tr = [(uv(t.GetStart()), uv(t.GetEnd()), TO(t.GetWidth()), t.GetLayer()) for t in b.GetTracks() if t.Type() != pcbnew.PCB_VIA_T and t.GetLayer() in (pcbnew.F_Cu, pcbnew.B_Cu)]
        self.vias = [(uv(t.GetPosition()), TO(t.GetWidth(pcbnew.F_Cu)), TO(t.GetDrillValue())) for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
        self.pads = []
        for f in b.GetFootprints():
            for p in f.Pads():
                cu, mk = [], []
                if p.IsOnLayer(pcbnew.F_Cu):
                    s = pcbnew.SHAPE_POLY_SET(); p.TransformShapeToPolygon(s, pcbnew.F_Cu, 0, pcbnew.FromMM(0.002), pcbnew.ERROR_INSIDE); cu = rings(s)
                if p.IsOnLayer(pcbnew.F_Mask):
                    s = pcbnew.SHAPE_POLY_SET(); p.TransformShapeToPolygon(s, pcbnew.F_Mask, p.GetSolderMaskExpansion(pcbnew.F_Mask), pcbnew.FromMM(0.002), pcbnew.ERROR_OUTSIDE); mk = rings(s)
                self.pads.append((uv(p.GetPosition()), cu, mk, '%s.%s' % (f.GetReference(), p.GetNumber())))

    def draw(self, ax, u0, v0, u1, v1, k):
        def near(c, m=2.5):
            return u0 - m <= c[0] <= u1 + m and v0 - m <= c[1] <= v1 + m
        for pts, holes, col in self.fill:
            if any(near(p, 0.5) for p in pts[::2]):
                ax.add_patch(MP(pts, closed=True, fc=col, ec='none', alpha=0.4, zorder=1))
                for h in holes:
                    if any(near(p, 0.5) for p in h[::2]):
                        ax.add_patch(MP(h, closed=True, fc='white', ec='none', zorder=1.1))
        for a, c, w, lay in self.tr:
            if near(a) or near(c):
                ax.plot([a[0], c[0]], [a[1], c[1]], color='#c0392b' if lay == pcbnew.F_Cu else '#2a6fba', lw=w * k, solid_capstyle='round', alpha=0.75, zorder=3 if lay == pcbnew.F_Cu else 2)
        for c, cu, mk, name in self.pads:
            if near(c, 4):
                for r in cu:
                    ax.add_patch(MP(r, closed=True, fc='#922b21', ec='none', alpha=0.8, zorder=4))
                for r in mk:
                    ax.add_patch(MP(r, closed=True, fc='none', ec='#f1c40f', lw=0.8, zorder=6))
                if u0 < c[0] < u1 and v0 < c[1] < v1:
                    ax.text(c[0], c[1], name, fontsize=4, ha='center', va='center', color='white', zorder=9)
        for c, d, h in self.vias:
            if near(c):
                ax.add_patch(Circle(c, d / 2, fc='#27ae60', ec='k', lw=0.3, alpha=0.8, zorder=7))
                ax.add_patch(Circle(c, h / 2, fc='white', ec='k', lw=0.3, zorder=8))
        ax.set_xlim(u0, u1); ax.set_ylim(v0, v1); ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([])


if __name__ == '__main__':
    old, new = Board(sys.argv[1]), Board(sys.argv[2])
    recs = json.load(open(sys.argv[3]))
    cols, half = 4, 1.9
    rows = (len(recs) + cols - 1) // cols
    size = 2.1
    fig, axs = plt.subplots(rows, cols * 2, figsize=(cols * 2 * size, rows * (size + 0.22)), dpi=130)
    k = 72 * size / (2 * half) * 0.97
    for i, r in enumerate(recs):
        cx = (r['old_uv'][0] + (r.get('new_uv') or r.get('twin_uv'))[0]) / 2
        cy = (r['old_uv'][1] + (r.get('new_uv') or r.get('twin_uv'))[1]) / 2
        for j, (bd, lab) in enumerate(((old, 'before'), (new, 'after'))):
            ax = axs[i // cols][(i % cols) * 2 + j]
            bd.draw(ax, cx - half, cy - half, cx + half, cy + half, k)
            what = 'taken out' if r['how'] == 'taken out' else 'moved %.2f' % r['move']
            ax.set_title('%s %s  %s' % (r['pad'], r['net'].split('/')[-1], lab) if j == 0 else '%s, mask %.2f' % (what, r['dam_new']), fontsize=6, pad=2)
            ax.plot(*r['old_uv'], marker='+', color='k', ms=5, mew=0.6, zorder=10)
    for i in range(len(recs), rows * cols):
        for j in range(2):
            axs[i // cols][(i % cols) * 2 + j].axis('off')
    fig.suptitle('Main board rev 3.2, fab issue 2026-11-16: the vias moved out of the pasted pads (each panel 3.8 x 3.8 mm; + = the old place)', fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.985))
    fig.savefig(sys.argv[4])
    print('wrote', sys.argv[4])
