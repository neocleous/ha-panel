"""Reads the STEP files back and compares them with the board files. Changes nothing.

    python3 step_check.py <rev 3 board> <rev 3 step> <rev 3.1 board> <rev 3.1 step> <rev 3.1 plug envelopes step>

What it checks:
  1. the board's solid: its box, and the four holes (cylinders of 1.6 radius) against the hole positions in the board file;
  2. every part of the rev 3.1 file against the board file: the middle of the part's box in the STEP file moved, from the
     rev 3 file to the rev 3.1 file, by what the part moved on the board (chip parts are symmetric, so this also holds
     for the parts that were turned);
  3. the heights above the door-side face and the pin ends beyond the back face that the file contains, against the
     table in sitecheck.py;
  4. the plug envelopes against the connector boxes of floorplan.json.
Frame of the files: X = u, Y = v, Z up out of the door-side face. Where Z = 0 lies is printed (section 1).
"""
import json
import os
import sys

import pcbnew
from OCP.Bnd import Bnd_Box
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepBndLib import BRepBndLib
from OCP.collections import Sequence_TDF_Label
from OCP.GeomAbs import GeomAbs_Cylinder
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.STEPControl import STEPControl_Reader
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TDF import TDF_Label
from OCP.TDocStd import TDocStd_Document
from OCP.TopAbs import TopAbs_FACE, TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import sitecheck as SC                                   # noqa: E402  (height table)

TO = pcbnew.ToMM
T = 1.6


class quiet:
    def __enter__(self):
        sys.stdout.flush()
        self.keep = os.dup(1)
        self.null = os.open(os.devnull, os.O_WRONLY)
        os.dup2(self.null, 1)

    def __exit__(self, *a):
        os.dup2(self.keep, 1)
        os.close(self.null)
        os.close(self.keep)


def box(shape):
    bx = Bnd_Box()
    BRepBndLib.AddOptimal_s(shape, bx, False, False)
    a, b = bx.CornerMin(), bx.CornerMax()
    return (a.X(), a.Y(), a.Z(), b.X(), b.Y(), b.Z())


def name(lab):
    n = TDataStd_Name()
    return n.Get().ToExtString() if lab.FindAttribute(TDataStd_Name.GetID_s(), n) else '?'


def read(path):
    """{name: (box, shape, model name)} of the parts of a STEP file written by KiCad."""
    with quiet():
        doc = TDocStd_Document(TCollection_ExtendedString('XmlOcaf'))
        r = STEPCAFControl_Reader()
        r.SetNameMode(True)
        r.ReadFile(path)
        r.Transfer(doc)
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    free = Sequence_TDF_Label()
    st.GetFreeShapes(free)
    comps = Sequence_TDF_Label()
    XCAFDoc_ShapeTool.GetComponents_s(free.Value(1), comps, False)
    out = {}
    for i in range(1, comps.Length() + 1):
        lab = comps.Value(i)
        ref = TDF_Label()
        model = name(ref) if XCAFDoc_ShapeTool.GetReferredShape_s(lab, ref) else ''
        sh = XCAFDoc_ShapeTool.GetShape_s(lab)
        out[name(lab)] = (box(sh), sh, model)
    return out


def holes(shape):
    """Centres of the cylinders of 1.6 radius that run through the board's solid."""
    found = set()
    ex = TopExp_Explorer(shape, TopAbs_FACE)
    while ex.More():
        s = BRepAdaptor_Surface((getattr(TopoDS, 'Face_s', None) or TopoDS.Face)(ex.Current()))   # OCP 7 / OCP 8
        if s.GetType() == GeomAbs_Cylinder and abs(s.Cylinder().Radius() - 1.6) < 0.01:
            p = s.Cylinder().Location()
            found.add((round(p.X(), 3), round(p.Y(), 3)))
        ex.Next()
    return sorted(found)


def board_parts(path):
    b = pcbnew.LoadBoard(path)
    out = {}
    for fp in b.GetFootprints():
        p = fp.GetPosition()
        out[fp.GetReference()] = (TO(p.x) - 43.5, 28.95 - TO(p.y), fp.GetOrientationDegrees(), fp.GetFPID().GetLibItemName().wx_str(), fp)
    return out


def main(b3, s3, b31, s31, plugs):
    P3, P31 = board_parts(b3), board_parts(b31)
    S3, S31 = read(s3), read(s31)
    bad = 0

    print('== 1. The board solid and the holes')
    for tag, S, P in (('rev 3', S3, P3), ('rev 3.1', S31, P31)):
        brd = [k for k in S if k not in P]
        print('%-8s parts in the file: %d, of them on the board file: %d, others: %s' % (tag, len(S), len(S) - len(brd), brd))
        bx, sh, _ = S[brd[0]]
        print('         solid: X %.3f...%.3f  Y %.3f...%.3f  Z %.3f...%.3f  (thickness %.3f)' % (bx[0], bx[3], bx[1], bx[4], bx[2], bx[5], bx[5] - bx[2]))
        hs = holes(sh)
        want = sorted((round(P[h][0], 3), round(P[h][1], 3)) for h in ('H1', 'H2', 'H3', 'H4'))
        ok = len(hs) == 4 and all(abs(a[0] - w[0]) < 0.005 and abs(a[1] - w[1]) < 0.005 for a, w in zip(hs, want))
        bad += not ok
        print('         holes of 3.2 in the solid: %s  board file: %s  %s' % (hs, want, 'agree' if ok else 'DIFFERENT'))
    zb0, zb1 = [S31[k] for k in S31 if k not in P31][0][0][2], [S31[k] for k in S31 if k not in P31][0][0][5]
    seat = min(v[0][2] for k, v in S31.items() if k in P31 and P31[k][3].startswith(('R_0603', 'C_0603')))
    print('rev 3.1: the chip parts stand on Z %.3f; the solid ends at Z %.3f; a 1.6 board under the parts starts at Z %.3f' % (seat, zb1, seat - T))

    print('\n== 2. Every part: moved in the STEP file by what it moved on the board')
    worst, n, moved = 0.0, 0, []
    for ref in sorted(S31):
        if ref not in P31:
            continue
        if ref not in S3:
            print('  %s is not in the rev 3 file' % ref)
            bad += 1
            continue
        a, c = S3[ref][0], S31[ref][0]
        ds = ((c[0] + c[3]) / 2 - (a[0] + a[3]) / 2, (c[1] + c[4]) / 2 - (a[1] + a[4]) / 2)
        db = (P31[ref][0] - P3[ref][0], P31[ref][1] - P3[ref][1])
        turned = abs(P31[ref][2] - P3[ref][2]) > 0.01
        err = max(abs(ds[0] - db[0]), abs(ds[1] - db[1]))
        n += 1
        if abs(db[0]) > 0.001 or abs(db[1]) > 0.001 or turned:
            moved.append('  %-5s board %+7.2f %+7.2f%s   STEP %+7.2f %+7.2f   difference %.3f' % (ref, db[0], db[1], ' turned' if turned else '', ds[0], ds[1], err))
        if err > 0.011:
            bad += 1
            print('  DIFFERENT: %s board %+.3f %+.3f  STEP %+.3f %+.3f' % (ref, db[0], db[1], ds[0], ds[1]))
        worst = max(worst, err)
    print('\n'.join(moved))
    gone = sorted(k for k in S3 if k in P3 and k not in S31)
    print('parts compared: %d; largest difference %.3f; parts moved or turned: %d; in rev 3 only: %s' % (n, worst, len(moved), gone))
    nobody = sorted(r for r in P31 if r not in S31)
    print('on the board, not in the file (no body, or not fitted): %d  %s' % (len(nobody), ' '.join(nobody)))

    print('\n== 3. Heights and pin ends in the rev 3.1 file (door-side face = Z %.3f, back face = Z %.3f)' % (seat, seat - T))
    print('  part   model                                        u                 v                top w   table   pin end   table')
    for ref in ('PS1', 'C5', 'C6', 'C7', 'L1', 'L100', 'J1', 'J5', 'J6', 'J8', 'J9', 'J10', 'J11', 'J2', 'LK1', 'F3', 'F5'):
        bx, _, model = S31[ref]
        fpn = P31[ref][3]
        h = SC.lookup(SC.HEIGHT, fpn, (None, None))[0]
        pr = SC.lookup(SC.PROTRUSION, fpn)
        top, below = bx[5] - seat, (seat - T) - bx[2]
        print('  %-5s  %-40s  %7.2f...%-7.2f  %7.2f...%-7.2f  %6.2f  %6s  %7s  %6s' % (
            ref, model[:40], bx[0], bx[3], bx[1], bx[4], top, '%.2f' % h if h else '-', '%.2f' % below if below > 0.05 else '-', '%.1f' % pr[0] if pr else '-'))
    tall = sorted(((v[0][5] - seat, k) for k, v in S31.items() if k in P31), reverse=True)[:3]
    print('  tallest three: %s' % ', '.join('%s %.2f' % (k, h) for h, k in tall))

    print('\n== 4. Plug envelopes')
    with quiet():
        r = STEPControl_Reader()
        r.ReadFile(plugs)
        r.TransferRoots()
        sh = r.OneShape()
    got = []
    ex = TopExp_Explorer(sh, TopAbs_SOLID)
    while ex.More():
        got.append(box(ex.Current()))
        ex.Next()
    plan = json.load(open(os.path.join(HERE, '..', 'floorplan.json')))['parts']
    for ref, (what, h) in sorted(SC.PLUGGED.items()):
        if ref == 'J2':
            continue
        b = plan[ref]['crt']
        m = [g for g in got if abs(g[0] - b[0]) < 0.06 and abs(g[1] - b[1]) < 0.06 and abs(g[3] - b[2]) < 0.06 and abs(g[4] - b[3]) < 0.06]
        ok = len(m) == 1 and abs(m[0][2] - T) < 0.001 and abs(m[0][5] - T - h) < 0.001
        bad += not ok
        print('  %-4s %-14s plan box u %.2f...%.2f v %.2f...%.2f, %.0f tall: %s' % (
            ref, what, b[0], b[2], b[1], b[3], h, 'block Z %.2f...%.2f, agrees' % (m[0][2], m[0][5]) if ok else 'DIFFERENT'))
    print('  blocks in the file: %d' % len(got))
    print('\n%s' % ('ALL AGREE' if not bad else '%d DIFFERENCES' % bad))


if __name__ == '__main__':
    main(*sys.argv[1:6])
