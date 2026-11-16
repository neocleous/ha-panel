"""For every via of the plan: the pours of its own net it stood in before, and whether it stands in them after.
usage: via_planes.py old.kicad_pcb new.kicad_pcb plan.json"""
import sys, json
sys.path.insert(0, 'gen')
import pcbnew
from shapely.geometry import Point
import fab32_vias as F
old, new = pcbnew.LoadBoard(sys.argv[1]), pcbnew.LoadBoard(sys.argv[2]); recs = json.load(open(sys.argv[3]))
def fills(b):
    out = {}
    for z in b.Zones():
        if z.GetIsRuleArea(): continue
        for l in F.LAYERS:
            if z.IsOnLayer(l):
                g = F.unary_union(F.polys(z.GetFilledPolysList(l)))
                out[(l, z.GetNetname())] = out[(l, z.GetNetname())].union(g) if (l, z.GetNetname()) in out else g
    return out
fo, fn = fills(old), fills(new); lost = kept = 0; gained = 0
for r in recs:
    if r['how'] != 'moved': continue
    po, pn = Point(r['old']), Point(r['new'])
    for l in F.LAYERS:
        k = (l, r['net'])
        before = k in fo and fo[k].buffer(0.01).contains(po)
        after = k in fn and fn[k].buffer(0.01).contains(pn)
        if before and after: kept += 1
        elif before and not after:
            lost += 1; print('centre no longer in the fill: %s %s on %s%s' % (r['pad'], r['net'], old.GetLayerName(l), ' (joined to it by the back-face track from its old place)' if r.get('bstub') and l == pcbnew.B_Cu else ''))
        elif after and not before: gained += 1
print('moved vias: %d; via centres in a pour of their own net: kept %d, no longer %d, new %d' % (sum(1 for r in recs if r['how'] == 'moved'), kept, lost, gained))
# areas of every pour, old -> new
for k in sorted(set(fo) | set(fn)):
    a, c = (fo[k].area if k in fo else 0), (fn[k].area if k in fn else 0)
    print('   %-8s %-34s %9.2f -> %9.2f mm2 (%+.2f)' % (old.GetLayerName(k[0]), k[1], a, c, c - a))
