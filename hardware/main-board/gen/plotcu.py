"""Plot the copper of a board for inspection: front and back seen from the front (door side), board frame u/v.
Run: python3 plotcu.py <board.kicad_pcb> <out.png> [u0 v0 u1 v1] [drc.json]"""
import json
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
from matplotlib.collections import LineCollection
import pcbnew

U0, V0 = 43.5, 28.95
T = 1e-6


def uv(p):
    return p.x * T - U0, V0 - p.y * T


def main(path, out, win=None, drc=None):
    b = pcbnew.LoadBoard(path)
    win = win or (-U0 - 1, -V0 - 1, U0 + 1, V0 + 1)
    w_mm, h_mm = win[2] - win[0], win[3] - win[1]
    k = min(9.0 / w_mm, 11.0 / h_mm) if w_mm < 60 else 0.105
    fig, axs = plt.subplots(1, 2, figsize=(2 * w_mm * k + 0.6, h_mm * k + 0.5), dpi=170)
    lays = (('F.Cu (door side)', pcbnew.F_Cu, '#c0392b'), ('B.Cu (back, seen through the board)', pcbnew.B_Cu, '#2a6fba'))
    ptpx = 72.0 * k / 25.4 * 25.4     # points per mm at this scale
    ptpx = 72.0 * k
    edge = pcbnew.SHAPE_POLY_SET()                   # the board's own outline (rev 3.2: with the relief in the +u edge)
    b.GetBoardPolygonOutlines(edge)
    outline = [uv(edge.Outline(0).CPoint(j)) for j in range(edge.Outline(0).PointCount())]
    for ax, (name, lid, col) in zip(axs, lays):
        ax.set_aspect('equal'); ax.set_xlim(win[0], win[2]); ax.set_ylim(win[1], win[3])
        ax.add_patch(Polygon(outline, closed=True, fc='#fbfbf6', ec='black', lw=0.8))
        for z in b.Zones():
            if z.GetIsRuleArea() or not z.IsOnLayer(lid) or z.GetNetname() == 'GND':
                continue
            ps = z.GetFilledPolysList(lid)
            for i in range(ps.OutlineCount()):
                ch = ps.Outline(i)
                ax.add_patch(Polygon([uv(ch.CPoint(j)) for j in range(ch.PointCount())], fc=col, ec='none', alpha=0.35))
        for fp in b.GetFootprints():
            for p in fp.Pads():
                if not p.IsOnLayer(lid):
                    continue
                bb = p.GetBoundingBox()
                x0, y1 = uv(pcbnew.VECTOR2I(bb.GetX(), bb.GetY())); x1, y0 = uv(pcbnew.VECTOR2I(bb.GetRight(), bb.GetBottom()))
                gnd = p.GetNetname() == 'GND'
                ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc='#9a9a9a' if gnd else '#e0a030', ec='none', alpha=0.9))
                if p.HasHole():
                    c = uv(p.GetPosition())
                    ax.add_patch(Circle(c, p.GetDrillSize().x * T / 2, fc='white', ec='none'))
            if lid == pcbnew.F_Cu:
                c = uv(fp.GetPosition())
                bb = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
                cx, cy = uv(bb.Centre())
                if win[0] < cx < win[2] and win[1] < cy < win[3]:
                    ax.text(cx, cy, fp.GetReference(), fontsize=3.2 if w_mm > 60 else 5, ha='center', va='center', color='#103010')
        segs, ws, cols = [], [], []
        for t in b.GetTracks():
            if t.GetClass() == 'PCB_VIA':
                c = uv(t.GetPosition())
                ax.add_patch(Circle(c, t.GetWidth(lid) * T / 2, fc='#6a3d9a' if t.GetNetname() != 'GND' else '#777', ec='none'))
                ax.add_patch(Circle(c, t.GetDrillValue() * T / 2, fc='white', ec='none'))
            elif t.GetLayer() == lid:
                segs.append([uv(t.GetStart()), uv(t.GetEnd())]); ws.append(t.GetWidth() * T * ptpx)
                cols.append('#555' if t.GetNetname() == 'GND' else col)
        ax.add_collection(LineCollection(segs, linewidths=ws, colors=cols, capstyle='round'))
        ax.set_title(name, fontsize=7); ax.tick_params(labelsize=5)
        ax.grid(True, lw=0.15, color='#ccc')
    if drc:
        d = json.load(open(drc))
        for u in d.get('unconnected_items', []):
            its = u['items']
            if len(its) >= 2:
                a, c = its[0]['pos'], its[1]['pos']
                for ax in axs:
                    ax.plot([a['x'] - U0, c['x'] - U0], [V0 - a['y'], V0 - c['y']], color='#00a000', lw=0.35)
    fig.tight_layout()
    fig.savefig(out)


if __name__ == '__main__':
    a = sys.argv
    win = tuple(float(x) for x in a[3:7]) if len(a) >= 7 else None
    drc = a[7] if len(a) >= 8 else (a[3] if len(a) == 4 else None)
    main(a[1], a[2], win, drc)
