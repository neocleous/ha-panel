"""STEP file of the populated rev 3 main board for the enclosure model.

KiCad's own exporter does the work. Parts whose footprint has a model in KiCad's library come out with that model.
Parts without one get an envelope block (their outline on the fabrication layer, as tall as the height table of
rev3/sitecheck.py says), written here with OpenCascade and attached to a copy of the board. The checked board file is
not touched.

    python3 gen/step_rev3.py main-board.kicad_pcb main-board-rev3.step [work dir]

Frame of the STEP file: X = u, Y = v (origin in the middle of the board), Z up out of the door-side face.
"""
import os
import subprocess
import sys

import pcbnew
from OCP.Bnd import Bnd_Box
from OCP.BRep import BRep_Builder
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Reader, STEPControl_Writer
from OCP.TopoDS import TopoDS_Compound

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'rev3'))
import sitecheck as SC                                   # noqa: E402  (height table)

TO = pcbnew.ToMM
MODELS = '/usr/share/kicad/3dmodels'
FOOTPRINTS = '/usr/share/kicad/footprints'
T = 1.6                                                  # board thickness
NO_BODY = ('TestPoint', 'MountingHole', 'WirePads')      # nothing stands on these
SAME_PACKAGE = {                                         # footprint name starts with: library model of the same package
    'HTSSOP-20-1EP_4.4x6.5mm_P0.65mm_EP3.4x6.5mm':
        '${KICAD9_3DMODEL_DIR}/Package_SO.3dshapes/HTSSOP-20-1EP_4.4x6.5mm_P0.65mm_EP3.4x6.5mm.step',
}


def resolve(name):
    p = name
    for v in ('${KICAD9_3DMODEL_DIR}', '${KICAD8_3DMODEL_DIR}', '${KICAD7_3DMODEL_DIR}', '${KICAD6_3DMODEL_DIR}'):
        p = p.replace(v, MODELS)
    for q in (p, os.path.splitext(p)[0] + '.step', os.path.splitext(p)[0] + '.stp'):
        if q.lower().endswith(('.step', '.stp')) and os.path.exists(q):
            return q
    return None


def lib_footprint(fp):
    nick = fp.GetFPID().GetLibNickname().wx_str()
    name = fp.GetFPID().GetLibItemName().wx_str()
    d = os.path.join(HERE, '..', 'lib', 'ha_panel.pretty') if nick == 'ha_panel' else os.path.join(FOOTPRINTS, nick + '.pretty')
    return pcbnew.FootprintLoad(d, name)


def fab_box(lf):
    """Outline on the fabrication layer of the library footprint (unrotated, at the origin): x0, y0, x1, y1."""
    xs, ys = [], []
    for g in lf.GraphicalItems():
        if g.GetLayer() == pcbnew.F_Fab and g.GetClass() == 'PCB_SHAPE':
            bb = g.GetBoundingBox()
            xs += [TO(bb.GetX()), TO(bb.GetRight())]
            ys += [TO(bb.GetY()), TO(bb.GetBottom())]
    if not xs:
        bb = lf.GetCourtyard(pcbnew.F_CrtYd).BBox()
        xs, ys = [TO(bb.GetX()), TO(bb.GetRight())], [TO(bb.GetY()), TO(bb.GetBottom())]
    return min(xs), min(ys), max(xs), max(ys)


class quiet:
    """OpenCascade prints a page of statistics per file read or written."""
    def __enter__(self):
        sys.stdout.flush()
        self.keep = os.dup(1)
        self.null = os.open(os.devnull, os.O_WRONLY)
        os.dup2(self.null, 1)

    def __exit__(self, *a):
        os.dup2(self.keep, 1)
        os.close(self.null)
        os.close(self.keep)


_TOP = {}


def model_top(path):
    """Highest point of a model above the board face it stands on."""
    if path not in _TOP:
        with quiet():
            r = STEPControl_Reader()
            r.ReadFile(path)
            r.TransferRoots()
            bx = Bnd_Box()
            BRepBndLib.AddOptimal_s(r.OneShape(), bx, False, False)
        _TOP[path] = bx.CornerMax().Z()
    return _TOP[path]


def write_block(path, box, h, pins=(), below=0.0, round_dia=None):
    """Block over box (footprint x/y, y down) from the board face to h, or a cylinder of round_dia in the middle of
    the box; square 0.64 pins from the face to `below` beyond the back face."""
    x0, y0, x1, y1 = box
    comp = TopoDS_Compound()
    bld = BRep_Builder()
    bld.MakeCompound(comp)
    if round_dia:
        ax = gp_Ax2(gp_Pnt((x0 + x1) / 2, -(y0 + y1) / 2, 0.0), gp_Dir(0, 0, 1))
        bld.Add(comp, BRepPrimAPI_MakeCylinder(ax, round_dia / 2, h).Shape())
    else:
        bld.Add(comp, BRepPrimAPI_MakeBox(gp_Pnt(x0, -y1, 0.0), gp_Pnt(x1, -y0, h)).Shape())
    for px, py in pins:
        bld.Add(comp, BRepPrimAPI_MakeBox(gp_Pnt(px - 0.32, -py - 0.32, -(T + below)), gp_Pnt(px + 0.32, -py + 0.32, 0.0)).Shape())
    with quiet():
        w = STEPControl_Writer()
        w.Transfer(comp, STEPControl_AsIs)
        w.Write(path)


def main(board_path, out, work):
    os.makedirs(work, exist_ok=True)
    b = pcbnew.LoadBoard(board_path)
    report = []
    lower = {}                                           # library models lower than the part: replaced by a block
    for fp in sorted(b.GetFootprints(), key=lambda f: f.GetReference()):
        name = fp.GetFPID().GetLibItemName().wx_str()
        ref = fp.GetReference()
        if name.startswith(NO_BODY):
            report.append((ref, name, 'no body'))
            continue
        have = [resolve(m.m_Filename) for m in fp.Models() if resolve(m.m_Filename)]
        h_tab = SC.lookup(SC.HEIGHT, name, (None, None))[0]
        short = have and h_tab and h_tab >= 3.0 and model_top(have[0]) < h_tab - 0.3
        if have and not short:
            report.append((ref, name, 'library model'))
            continue
        if short:
            lower.setdefault(name, (model_top(have[0]), h_tab))
        same = [v for k, v in SAME_PACKAGE.items() if name.startswith(k)]
        if same:
            ms = fp.Models()
            ms.clear()
            m = pcbnew.FP_3DMODEL()
            m.m_Filename = same[0]
            ms.push_back(m)
            report.append((ref, name, 'library model of the same package'))
            continue
        h, src = SC.lookup(SC.HEIGHT, name, (None, None))
        if h is None:
            raise SystemExit('no height for %s (%s)' % (ref, name))
        lf = lib_footprint(fp)
        pins, below = [], 0.0
        prot = SC.lookup(SC.PROTRUSION, name)
        if prot:
            below = prot[0]
            pins = [(TO(p.GetPosition().x), TO(p.GetPosition().y)) for p in lf.Pads() if p.HasHole()]
        path = os.path.join(work, name + '_envelope.step')
        if not os.path.exists(path):
            if name.startswith('CP_Radial_D'):           # round can between its two leads
                dia = float(name.split('_D')[1].split('mm')[0])
                xs = [TO(p.GetPosition().x) for p in lf.Pads()]
                ys = [TO(p.GetPosition().y) for p in lf.Pads()]
                write_block(path, (min(xs), min(ys), max(xs), max(ys)), h, pins, below, round_dia=dia)
            else:
                write_block(path, fab_box(lf), h, pins, below)
        ms = fp.Models()
        ms.clear()
        m = pcbnew.FP_3DMODEL()
        m.m_Filename = path
        ms.push_back(m)
        report.append((ref, name, 'envelope block %.2f tall (%s)' % (h, src)))
    tmp = os.path.join(work, 'main-board-step.kicad_pcb')
    pcbnew.SaveBoard(tmp, b)
    dnp = sorted(f.GetReference() for f in b.GetFootprints() if f.IsDNP())
    r = subprocess.run(['kicad-cli', 'pcb', 'export', 'step', '--force', '--subst-models', '--no-dnp', '--user-origin', '43.5x28.95mm',
                        '-o', out, tmp], capture_output=True, text=True)
    print((r.stdout + r.stderr).strip().splitlines()[-1])
    kinds = {}
    for ref, name, how in report:
        kinds.setdefault(how.split(' (')[0] if how.startswith('envelope') else how, []).append(ref)
    for k, v in kinds.items():
        print('%-40s %3d  %s' % (k, len(v), ' '.join(v[:14]) + (' ...' if len(v) > 14 else '')))
    print('not fitted (left out):', len(dnp), ' '.join(dnp))
    for name, (top, h) in lower.items():
        print('library model lower than the part, block used instead: %s  model %.2f, part %.2f' % (name, top, h))
    plug_envelopes(b, os.path.splitext(out)[0] + '-plug-envelopes.step')


def plug_envelopes(b, out):
    """Second file, same frame: over each socket that is plugged in place, a block up to the height its plug and the
    bend of its lead need (rev3/sitecheck.py PLUGGED; the Pi power plug leaves downward and is not in it)."""
    comp = TopoDS_Compound()
    bld = BRep_Builder()
    bld.MakeCompound(comp)
    rows = []
    for ref, (what, h) in sorted(SC.PLUGGED.items()):
        if ref == 'J2':
            continue
        fp = b.FindFootprintByReference(ref)
        bb = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
        u0, u1 = TO(bb.GetX()) - 43.5, TO(bb.GetRight()) - 43.5
        v0, v1 = 28.95 - TO(bb.GetBottom()), 28.95 - TO(bb.GetY())
        bld.Add(comp, BRepPrimAPI_MakeBox(gp_Pnt(u0, v0, T), gp_Pnt(u1, v1, T + h)).Shape())
        rows.append('%s %s: u %.2f...%.2f, v %.2f...%.2f, w 0...%.1f' % (ref, what, u0, u1, v0, v1, h))
    with quiet():
        w = STEPControl_Writer()
        w.Transfer(comp, STEPControl_AsIs)
        w.Write(out)
    print('plug envelopes:', os.path.basename(out))
    for r in rows:
        print('  ' + r)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else '/tmp/step_rev3')
