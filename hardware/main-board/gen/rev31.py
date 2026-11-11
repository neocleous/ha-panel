"""Main board rev 3.1: the changes to rev 3 asked for by the enclosure (claude/brief-electronics-step2-repeat-2026-11-11.md),
applied to the routed rev 3 board. Nothing is routed again that does not have to be.

Stages, each from a saved board to a saved board (KiCad's check runs between them, from the shell: rev31.sh):
  move    the top right hole, the two sensor headers and the small parts in their way go to their new places; the
          tracks that ended on them are taken out back to the next joint
  rip     tracks and vias that KiCad's check reports against the moved parts and the new hole are taken out
  route   one via for each moved ground pad, then every open connection (the repository's maze router)
  copper  wider copper for the Pi's 5 V and for the 20 V inlet
  finish  ground pours on both outer layers, stitching vias
  text    revision texts, the two connector names on the back
Run: python3 rev31.py <board in> <board out> <stage> [drc.json]
Positions are in the site's board frame (u to the right, v up, seen from the door); KiCad X = u + 43.5, Y = 28.95 - v.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pcbnew                      # noqa: E402
import mroute                      # noqa: E402
import pcb_rev3 as pb              # noqa: E402
import route_main as rm            # noqa: E402
import route_rev3 as rr            # noqa: E402

MM, TO = pcbnew.FromMM, pcbnew.ToMM
X, Y = pb.X, pb.Y
N5 = '/5 V supply and outputs/'
NEF = '/20 V inlet and eFuse/'
PLANE = rr.PLANE

HOLE = (19.2, 25.0)                       # H2, new centre (u, v); was (+30.0, +25.0)
MOVES = {                                 # ref: (u, v, rotation in degrees or None = keep) - footprint origin
    'R26': (21.9, 20.2, 180.0),           # below the new hole, pad 2 (amplifier logic rail) over C119
    'R27': (18.2, 20.2, 0.0),
    'F3': (-34.24, -11.2, 270.0),         # the radar's fuse, capacitor and test pad: between the radar socket and J10
    'C10': (-34.24, -16.1, 0.0),
    'TP12': (-34.24, -18.6, None),
}
SHIFTS = {                                # ref: (du, dv)
    'J10': (3.9, 0.0),                    # BME680 header: 3.9 further from the radar socket (3.7 or more asked)
    'J11': (0.0, -1.0),                   # VEML6030 header: 1.0 lower
    'F4': (1.1, 0.0), 'C11': (0.35, 0.0), 'TP3': (0.0, -0.5),
}


def xy(p):
    return (TO(p.x), TO(p.y))


def near(a, c, tol=0.02):
    return math.hypot(a[0] - c[0], a[1] - c[1]) <= tol


def pads_at(b, net, pt, skip=()):
    out = []
    P = pcbnew.VECTOR2I(MM(pt[0]), MM(pt[1]))
    for fp in b.GetFootprints():
        if fp.GetReference() in skip:
            continue
        for p in fp.Pads():
            if p.GetNetname() == net and p.HitTest(P, MM(0.02)):
                out.append(p)
    return out


def rip_chain(b, net, start, skip_refs=(), gone=None, max_len=1e9):
    """Take out the track that leaves `start` (a pad centre or a cut end) and follow it to the next joint: a pad of a
    part that stays, a branch, or (plane nets) a via into the plane; or until max_len of track is out. What is left
    beyond that stays as a stub for the router to land on (unused stubs go with the loose ends at the end).
    Returns the number of pieces removed."""
    gone = set() if gone is None else gone
    n = 0
    todo = [(start, True, 0.0)]
    while todo:
        q, first, acc = todo.pop()
        if acc >= max_len:
            continue
        items = [t for t in b.GetTracks() if t.GetNetname() == net and t.m_Uuid.AsString() not in gone]
        segs = [(t, xy(t.GetEnd()) if near(xy(t.GetStart()), q) else xy(t.GetStart())) for t in items
                if t.Type() != pcbnew.PCB_VIA_T and (near(xy(t.GetStart()), q) or near(xy(t.GetEnd()), q))]
        vias = [t for t in items if t.Type() == pcbnew.PCB_VIA_T and near(xy(t.GetPosition()), q)]
        if not first:
            if pads_at(b, net, q, skip_refs):
                continue                                   # a pad of a part that stays: the chain ends here
            if len(segs) >= 2:
                continue                                   # a branch: leave it
            if net in PLANE and vias:
                if not segs:                               # a via into the plane with nothing else on it
                    for v in vias:
                        gone.add(v.m_Uuid.AsString()); mroute.remove(b, v); n += 1
                continue
        for v in vias:
            if first or not segs or len(segs) == 1:
                gone.add(v.m_Uuid.AsString()); mroute.remove(b, v); n += 1
        for t, other in segs:
            gone.add(t.m_Uuid.AsString()); mroute.remove(b, t); n += 1
            todo.append((other, False, acc + math.hypot(other[0] - q[0], other[1] - q[1])))
    return n


def stage_move(b):
    moved = list(MOVES) + list(SHIFTS)
    old = []
    for ref in moved:
        fp = b.FindFootprintByReference(ref)
        for p in fp.Pads():
            if p.GetNetname() and not p.GetNetname().startswith('unconnected'):
                old.append((p.GetNetname(), xy(p.GetPosition()), 6.0 if ref in MOVES else 2.5))
    gone, n = set(), 0
    for net, pt, lim in old:
        n += rip_chain(b, net, pt, skip_refs=moved, gone=gone, max_len=lim)
    # the audio bit clock ran round the old hole on the back; with the hole gone the detour goes too
    k = 0
    for t in list(b.GetTracks()):
        if t.GetNetname() == 'I2S_BCLK' and t.Type() != pcbnew.PCB_VIA_T and t.GetLayer() == pcbnew.B_Cu:
            (x1, y1), (x2, y2) = xy(t.GetStart()), xy(t.GetEnd())
            if min(x1, x2) > X(26.0) and max(y1, y2) <= Y(21.6) + 1e-6:
                mroute.remove(b, t); k += 1
    print('tracks and vias taken out at the parts that move:', n, '| bit-clock detour round the old hole:', k)
    for ref, (u, v, rot) in MOVES.items():
        fp = b.FindFootprintByReference(ref)
        fp.SetPosition(pcbnew.VECTOR2I(MM(X(u)), MM(Y(v))))
        if rot is not None:
            fp.SetOrientationDegrees(rot)
    for ref, (du, dv) in SHIFTS.items():
        fp = b.FindFootprintByReference(ref)
        p = fp.GetPosition()
        fp.SetPosition(pcbnew.VECTOR2I(p.x + MM(du), p.y - MM(dv)))
    # the hole, with the same copper-free circles as the other three
    h = b.FindFootprintByReference('H2')
    h.SetPosition(pcbnew.VECTOR2I(MM(X(HOLE[0])), MM(Y(HOLE[1]))))
    for z in list(b.Zones()):
        if z.GetIsRuleArea() and z.GetZoneName().startswith('H2 '):
            b.Remove(z); mroute.GRAVE.append(z)
    pb.keepout(b, X(HOLE[0]), Y(HOLE[1]), 3.5, pcbnew.F_Cu, 'H2 screw head')
    pb.keepout(b, X(HOLE[0]), Y(HOLE[1]), 4.1, pcbnew.B_Cu, 'H2 post face')
    for ref in moved + ['H2']:
        fp = b.FindFootprintByReference(ref)
        c = fp.GetPosition()
        print('  %-5s u %+7.2f v %+7.2f rot %g   pads: %s' % (ref, TO(c.x) - pb.U0, pb.V0 - TO(c.y), fp.GetOrientationDegrees(),
              ' '.join('%s(%+.2f,%+.2f)' % (p.GetNumber(), TO(p.GetPosition().x) - pb.U0, pb.V0 - TO(p.GetPosition().y)) for p in fp.Pads() if p.GetNumber())))


RIP_TYPES = ('clearance', 'shorting_items', 'tracks_crossing', 'hole_clearance', 'items_not_allowed', 'solder_mask_bridge',
             'copper_edge_clearance', 'hole_to_hole', 'drill_out_of_range')


def stage_rip(b, drc_json):
    """Take out the tracks and vias that KiCad's check reports against the new places. Only the reported piece goes;
    the router joins the two ends round the obstacle, so the rest of the track stays as it was on rev 3."""
    d = json.load(open(drc_json))
    byid = {t.m_Uuid.AsString(): t for t in b.GetTracks()}
    hit = {}
    for v in d['violations']:
        if v['type'] not in RIP_TYPES:
            continue
        for it in v['items']:
            t = byid.get(it.get('uuid'))
            if t is not None:
                hit[t.m_Uuid.AsString()] = t
    for t in hit.values():
        mroute.remove(b, t)
    print('taken out against the new places:', len(hit))
    return len(hit)


def drop_points(b, shorter=0.01):
    """The router and the loose-end pass leave a few track pieces of (almost) no length. They join nothing.
    The amplifier's nets are left alone: their copper is rev 2.1's, piece for piece."""
    k = 0
    for t in list(b.GetTracks()):
        if t.GetNetname().startswith('/Amplifier/'):
            continue
        if t.Type() != pcbnew.PCB_VIA_T and (t.GetStart() - t.GetEnd()).EuclideanNorm() < MM(shorter):
            mroute.remove(b, t); k += 1
    return k


def stage_route(b):
    b.BuildConnectivity()
    n, bad = rr.stage_planes(b)
    print('vias into the planes added:', n, '| not placed:', bad)
    stats, failed = rr.stage_signals(b)
    print('connections:', stats, '| still open:', len(failed))
    for net, a, c, info in failed:
        print('  OPEN %s (%+.1f,%+.1f)-(%+.1f,%+.1f) %s' % (net.split('/')[-1], a[0] - pb.U0, pb.V0 - a[1], c[0] - pb.U0, pb.V0 - c[1], info))
    for t in rr.THIN:
        print('  THIN', t)
    print('pieces of no length removed:', drop_points(b))


VBUS_AREA = [(56.9, 39.0), (60.0, 39.0), (60.0, 45.0), (61.6, 46.7), (68.0, 46.7), (68.0, 49.3), (59.3, 49.3), (56.9, 45.6)]
VIN_AREA = [(29.7, 49.0), (32.3, 49.0), (32.3, 53.4), (29.7, 53.4)]


def area(b, net, layer, pts, name):
    z = rm.zone(b, net, layer, pts, prio=2, thermal=False, clearance=0.2, minw=0.25)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    z.SetZoneName(name)
    return z


def stage_copper(b):
    """Wider copper on the two supply paths that the 5 V check found narrow (rev3.1/README.md, section 4).
    The tracks of rev 3 stay inside the new areas, so every joint is still a track joint."""
    w = {'vbus': 0, 'link': 0, 'f2': 0, 'j1': 0}
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            continue
        n, lay, tw = t.GetNetname(), t.GetLayer(), TO(t.GetWidth())
        if n == N5 + 'VBUS_PI' and lay == pcbnew.B_Cu and abs(tw - 0.6) < 1e-3:
            t.SetWidth(MM(0.7)); w['vbus'] += 1               # entries into the socket's pin pairs: the pad's width
        elif n == N5 + 'VBUS_PI' and lay == pcbnew.B_Cu and abs(tw - 0.4) < 1e-3:
            t.SetWidth(MM(0.7)); w['link'] += 1               # links from the A pin to the B pin
        elif n == N5 + '5V_PI_F' and lay == pcbnew.F_Cu and abs(tw - 1.5) < 1e-3:
            t.SetWidth(MM(F2_W)); w['f2'] += 1                # fuse F2 to the wire link
        elif n == NEF + 'VIN_PIGTAIL' and lay == pcbnew.F_Cu and abs(tw - 1.0) < 1e-3:
            t.SetWidth(MM(2.0)); w['j1'] += 1                 # 20 V socket to its fuse
    area(b, N5 + 'VBUS_PI', pcbnew.B_Cu, VBUS_AREA, 'Pi 5 V, wire link to socket')
    area(b, NEF + 'VIN_EF', pcbnew.F_Cu, VIN_AREA, '20 V, fuse to protection chip')
    print('widened:', w, '| areas added: 2')


F2_W = 2.2


def stage_finish(b):
    """Ground pours on both outer layers over the whole board (rev 3 was saved without them), one stitching via
    into the ground plane for every poured piece that has none, then the pieces still without a via are dropped."""
    zs = []
    for lay in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = rm.zone(b, 'GND', lay, pb.FULL, prio=0, thermal=True, clearance=0.3)
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_NEVER)
        zs.append(z)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    total = 0
    for _ in range(3):
        mroute.RES = 0.05
        k = len(mroute.stitch(b, rr.CLASSES))
        total += k
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        if not k:
            break
    for z in zs:
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    print('stitch vias', total)


def stage_text(b, drc_json=None):
    tb = b.GetTitleBlock()
    tb.SetRevision('3.1')
    tb.SetComment(0, 'Rev 3.1: top right hole, BME680 and VEML6030 headers moved; supply copper widened; ground pours '
                     '(claude/brief-electronics-step2-repeat-2026-11-11.md)')
    for d in b.GetDrawings():
        if d.GetClass() != 'PCB_TEXT':
            continue
        if d.GetText().startswith('REV 3 '):
            d.SetText(d.GetText().replace('REV 3 ', 'REV 3.1 '))
        elif d.GetText() == 'BME680':
            d.Move(pcbnew.VECTOR2I(MM(SHIFTS['J10'][0]), MM(-SHIFTS['J10'][1])))
        elif d.GetText() == 'VEML6030':
            d.Move(pcbnew.VECTOR2I(MM(SHIFTS['J11'][0]), MM(-SHIFTS['J11'][1])))
    hidden = []
    if drc_json:                      # part names that now lie on a pad or on another name: hidden, as 48 others are
        import re
        d = json.load(open(drc_json))
        for v in d['violations']:
            if v['type'] in ('silk_overlap', 'silk_over_copper'):
                for it in v['items']:
                    m = re.match(r'Reference field of (\w+)', it['description'])
                    if m and m.group(1) not in hidden:
                        hidden.append(m.group(1))
                        break
        for ref in hidden:
            b.FindFootprintByReference(ref).Reference().SetVisible(False)
    print('part names hidden:', hidden)
    print('pieces of no length removed:', drop_points(b))


def main(src, dst, stage, extra=None):
    if src != dst:
        import shutil
        shutil.copy(src, dst)
        if os.path.exists(src.replace('.kicad_pcb', '.kicad_pro')):
            shutil.copy(src.replace('.kicad_pcb', '.kicad_pro'), dst.replace('.kicad_pcb', '.kicad_pro'))
    b = pcbnew.LoadBoard(dst)
    pb.rules(b)
    if stage == 'move':
        stage_move(b)
    elif stage == 'rip':
        stage_rip(b, extra)
    elif stage == 'route':
        stage_route(b)
    elif stage == 'copper':
        stage_copper(b)
    elif stage == 'finish':
        stage_finish(b)
    elif stage == 'text':
        stage_text(b, extra)
    else:
        raise SystemExit('unknown stage ' + stage)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(dst, b)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
