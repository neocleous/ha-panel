"""Debug plot of a board region: python3 plotreg.py <board> <out.png> x0 y0 x1 y1 [layers=F,B,In2] [label_nets]"""
import math
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle
import pcbnew

TOMM = 1e-6
COL = {'F': '#d62728', 'B': '#1f77b4', 'In1': '#2ca02c', 'In2': '#9467bd'}
LID = {'F': pcbnew.F_Cu, 'B': pcbnew.B_Cu, 'In1': pcbnew.In1_Cu, 'In2': pcbnew.In2_Cu}


def chain_pts(ch):
    return [(ch.CPoint(i).x * TOMM, ch.CPoint(i).y * TOMM) for i in range(ch.PointCount())]


def seg_poly(x0, y0, x1, y1, w):
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1e-9
    nx, ny = -dy / L * w / 2, dx / L * w / 2
    return [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]


def main():
    bpath, out = sys.argv[1], sys.argv[2]
    x0, y0, x1, y1 = map(float, sys.argv[3:7])
    layers = (sys.argv[7] if len(sys.argv) > 7 else 'F,B,In2').split(',')
    label = set((sys.argv[8].split(',')) if len(sys.argv) > 8 else [])
    b = pcbnew.LoadBoard(bpath)
    fig, ax = plt.subplots(figsize=(14, 14 * (y1 - y0) / (x1 - x0)))
    for z in b.Zones():
        for ln in layers:
            if z.IsOnLayer(LID[ln]) and z.IsFilled() and ln in ('In1', 'In2'):
                ps = z.GetFilledPolysList(LID[ln])
                for i in range(ps.OutlineCount()):
                    ax.add_patch(Polygon(chain_pts(ps.Outline(i)), closed=True, fc=COL[ln], alpha=0.12, ec=COL[ln], lw=0.4))
                    for h in range(ps.HoleCount(i)):
                        ax.add_patch(Polygon(chain_pts(ps.Hole(i, h)), closed=True, fc='white', alpha=0.9, ec=COL[ln], lw=0.3))
    for t in b.GetTracks():
        if t.GetClass() == 'PCB_VIA':
            p = t.GetPosition()
            ax.add_patch(Circle((p.x * TOMM, p.y * TOMM), t.GetWidth(pcbnew.F_Cu) * TOMM / 2, fc='#777', ec='k', lw=0.3, alpha=0.8))
            continue
        ln = {pcbnew.F_Cu: 'F', pcbnew.B_Cu: 'B', pcbnew.In1_Cu: 'In1', pcbnew.In2_Cu: 'In2'}.get(t.GetLayer())
        if ln not in layers:
            continue
        s, e = t.GetStart(), t.GetEnd()
        ax.add_patch(Polygon(seg_poly(s.x * TOMM, s.y * TOMM, e.x * TOMM, e.y * TOMM, t.GetWidth() * TOMM), closed=True,
                             fc=COL[ln], alpha=0.55, lw=0))
    for fp in b.GetFootprints():
        for p in fp.Pads():
            bb = p.GetBoundingBox()
            on = [ln for ln in ('F', 'B') if p.IsOnLayer(LID[ln]) and ln in layers]
            if not on:
                continue
            ln = on[0] if len(on) == 1 else 'F'
            ax.add_patch(Rectangle((bb.GetX() * TOMM, bb.GetY() * TOMM), bb.GetWidth() * TOMM, bb.GetHeight() * TOMM,
                                   fc='none', ec=COL[ln], lw=0.6))
            nn = p.GetNetname().split('/')[-1]
            if nn in label or fp.GetReference() in label:
                c = p.GetPosition()
                ax.text(c.x * TOMM, c.y * TOMM, '%s.%s\n%s' % (fp.GetReference(), p.GetNumber(), nn), fontsize=5, ha='center', va='center')
        r = fp.GetPosition()
        if x0 <= r.x * TOMM <= x1 and y0 <= r.y * TOMM <= y1:
            ax.text(r.x * TOMM, r.y * TOMM, fp.GetReference(), fontsize=7, color='k', alpha=0.6,
                    style='italic' if fp.GetLayer() == pcbnew.B_Cu else 'normal')
    ax.set_xlim(x0, x1); ax.set_ylim(y1, y0); ax.set_aspect('equal')
    ax.set_xticks([x for x in range(int(x0), int(x1) + 1)]); ax.set_yticks([y for y in range(int(y0), int(y1) + 1)])
    ax.tick_params(labelsize=6); ax.grid(lw=0.2)
    fig.tight_layout(); fig.savefig(out, dpi=110)


main()
