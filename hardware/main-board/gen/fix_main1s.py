"""Fixes applied to the single-sided main board after route_main.py (run s1, 2026-11-08 00:05), in this order:
fix1s (J4 wire-landing courtyard, F5 down 0.45 off J6's courtyard, VIN_EF ties, R1 link, min track 0.10),
fix1s_b (PI_LRCLK re-route round F5's moved pad), fix1s_c (C4 GND). Then the tab was cut off (it carried nothing)
and silk.place re-run. Kept for provenance: the KiCad board is the source of truth."""

# ---- fix1s ----
import sys
sys.path.insert(0,'/home/claude/work/gen')
import pcbnew, mroute, route_main as rm
T=1e-6; MM=pcbnew.FromMM
b=pcbnew.LoadBoard(sys.argv[1])
b.GetDesignSettings().m_TrackMinWidth = MM(0.10)       # Freerouting necks at the 0.65/0.5 mm pins (JLC 0.10/0.10)
# 1. J4 is a wire landing (no header body): courtyard = pads + 0.25
j4=b.FindFootprintByReference('J4')
for g in list(j4.GraphicalItems()):
    if g.GetLayer()==pcbnew.F_CrtYd: j4.Remove(g); mroute.GRAVE.append(g)
pts=[(43.92,33.89),(48.66,33.89),(48.66,38.63),(43.92,38.63)]
for a,c in zip(pts,pts[1:]+pts[:1]):
    s=pcbnew.PCB_SHAPE(j4); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.F_CrtYd); s.SetWidth(MM(0.05))
    s.SetStart(pcbnew.VECTOR2I(MM(a[0]),MM(a[1]))); s.SetEnd(pcbnew.VECTOR2I(MM(c[0]),MM(c[1]))); j4.Add(s)
# 2. F5 down 0.45 mm (clear of J6's courtyard); drag the track ends that sit in its pads
f5=b.FindFootprintByReference('F5'); dy=MM(0.45)
rects={p.GetNetname():p.GetBoundingBox() for p in f5.Pads()}
moved=0
for t in b.GetTracks():
    n=t.GetNetname()
    if n not in rects: continue
    bb=rects[n]
    if t.GetClass()=='PCB_VIA':
        continue
    for get,set_ in ((t.GetStart,t.SetStart),(t.GetEnd,t.SetEnd)):
        q=get()
        if bb.Contains(q):
            set_(pcbnew.VECTOR2I(q.x,q.y+dy)); moved+=1
f5.Move(pcbnew.VECTOR2I(0,dy))
print('F5 moved, track ends dragged', moved)
# 3. VIN_EF: tie the inlet run (back) to the U1 pin 1-3 group and to the pin-6 / C2 group on the front
net=b.FindNet('/20 V inlet and eFuse/VIN_EF')
def trk(a,c,w,lay):
    t=pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(MM(a[0]),MM(a[1]))); t.SetEnd(pcbnew.VECTOR2I(MM(c[0]),MM(c[1])))
    t.SetWidth(MM(w)); t.SetLayer(lay); t.SetNet(net); t.SetLocked(True); b.Add(t)
trk((34.45,41.91),(34.45,43.12),0.8,pcbnew.B_Cu)
v=pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(MM(34.45),MM(43.12))); v.SetWidth(MM(0.8)); v.SetDrill(MM(0.4))
v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); v.SetNet(net); v.SetLocked(True); b.Add(v)
trk((34.73,41.9),(34.73,43.12),0.4,pcbnew.F_Cu)
print('R1', mroute.route(b,'/20 V inlet and eFuse/VIN_EF',(38.02,43.61),(36.98,42.42),0.3,rm.CLASSES))
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
print('stitch', len(mroute.stitch(b, rm.CLASSES)))
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(sys.argv[1],b)

# ---- fix1s_b ----
import sys
sys.path.insert(0,'/home/claude/work/gen')
import pcbnew, mroute, route_main as rm
b=pcbnew.LoadBoard(sys.argv[1])
n='/3.3 V, Pi link, sensors, radar, echo-ref/PI_LRCLK'
print('rm', mroute.remove_segments(b,n,[(39.80,31.56,41.10,32.86),(41.10,32.86,41.10,33.03),(41.10,33.03,41.97,33.89)]))
print('LRCLK', mroute.route(b,n,(39.80,31.56),(41.97,33.89),0.2,rm.CLASSES))
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
print('stitch', len(mroute.stitch(b, rm.CLASSES)))
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(sys.argv[1],b)

# ---- fix1s_c ----
import sys
sys.path.insert(0,'/home/claude/work/gen')
import pcbnew, mroute, route_main as rm
b=pcbnew.LoadBoard(sys.argv[1])
ok=mroute.drop_via(b,'GND',(35.75,33.30),rm.CLASSES,w=0.3,via=(0.45,0.2),layer='F',margin=3.0)
print('C4 GND via', ok)
if not ok[0]:
    print('C4 GND to U1.12', mroute.route(b,'GND',(35.75,33.30),(39.27,35.54),0.25,rm.CLASSES))
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(sys.argv[1],b)
