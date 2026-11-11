import sys, json
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDF import TDF_Label
from OCP.collections import Sequence_TDF_Label as TDF_LabelSequence
from OCP.TDataStd import TDataStd_Name
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.TopLoc import TopLoc_Location
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.IFSelect import IFSelect_RetDone

def name_of(label):
    n = TDataStd_Name()
    if label.FindAttribute(TDataStd_Name.GetID_s(), n):
        return n.Get().ToExtString()
    return ''

path = sys.argv[1]
doc = TDocStd_Document(TCollection_ExtendedString('x'))
rd = STEPCAFControl_Reader(); rd.SetNameMode(True)
assert rd.ReadFile(path) == IFSelect_RetDone
rd.Transfer(doc)
st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
free = TDF_LabelSequence(); st.GetFreeShapes(free)
rows = []
def walk(label, loc, depth, inst=''):
    if st.IsAssembly_s(label):
        comps = TDF_LabelSequence(); st.GetComponents_s(label, comps)
        for i in range(1, comps.Length() + 1):
            c = comps.Value(i)
            ref = TDF_Label()
            cl = st.GetLocation_s(c)
            if st.GetReferredShape_s(c, ref):
                walk(ref, loc.Multiplied(cl), depth + 1, name_of(c))
    else:
        shp = st.GetShape_s(label).Moved(loc)
        ex = TopExp_Explorer(shp, TopAbs_SOLID); ns = 0
        while ex.More():
            ns += 1; ex.Next()
        b = Bnd_Box(); b.SetGap(0.0); BRepBndLib.AddOptimal_s(shp, b, False, False)
        p0 = b.CornerMin(); p1 = b.CornerMax(); x0, y0, z0, x1, y1, z1 = p0.X(), p0.Y(), p0.Z(), p1.X(), p1.Y(), p1.Z()
        g = GProp_GProps(); BRepGProp.VolumeProperties_s(shp, g)
        rows.append({'name': name_of(label), 'inst': inst, 'solids': ns, 'box': [round(v, 3) for v in (x0, x1, y0, y1, z0, z1)], 'vol': round(g.Mass(), 2)})
for i in range(1, free.Length() + 1):
    walk(free.Value(i), TopLoc_Location(), 0)
json.dump(rows, open(sys.argv[2], 'w'))
print(len(rows), 'leaf shapes,', sum(r['solids'] for r in rows), 'solids')
bx = [min(r['box'][0] for r in rows), max(r['box'][1] for r in rows), min(r['box'][2] for r in rows), max(r['box'][3] for r in rows), min(r['box'][4] for r in rows), max(r['box'][5] for r in rows)]
print('overall', bx)
