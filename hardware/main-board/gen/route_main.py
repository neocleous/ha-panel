"""Main board: net classes, plane zones (In1 GND, In2 +5V/+20V/PVDD), Specctra export, Freerouting, SES import,
outer GND pours. Run: python3 route_main.py <board> [passes]"""
import os
import subprocess
import sys
import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcb_main as pm
import fanout as fo

MM = pm.MM
JAVA = '/usr/lib/jvm/java-25-openjdk-amd64/bin/java'
FR = '/home/claude/tools/fr/fr_g.jar'      # Freerouting 2.5.0 executable (Maven Central mirror, SHA-1 checked)

CLASSES = {   # name: (track, clearance, via_d, via_drill, nets) - widths that still escape 0.5 mm-pitch pins
    'PWR5': (0.8, 0.2, 0.8, 0.4, ['+5V', '/5 V supply and outputs/5V_PI_F', '/5 V supply and outputs/VBUS_PI']),
    'PWR20': (0.8, 0.2, 0.8, 0.4, ['+20V', '/20 V inlet and eFuse/VIN_PIGTAIL', '/20 V inlet and eFuse/VIN_EF',
                                   '/5 V supply and outputs/NID_VIN']),
    'PV': (0.3, 0.15, 0.6, 0.3, ['/Amplifier/PVDD']),
    'SPK': (0.4, 0.15, 0.6, 0.3, ['/Amplifier/OUT_AP', '/Amplifier/OUT_AN', '/Amplifier/OUT_BP', '/Amplifier/OUT_BN',
                                  '/Amplifier/SPK_L_P', '/Amplifier/SPK_L_N', '/Amplifier/SPK_R_P', '/Amplifier/SPK_R_N']),
    'BST': (0.25, 0.15, 0.6, 0.3, ['/Amplifier/BST_AP', '/Amplifier/BST_AN', '/Amplifier/BST_BP', '/Amplifier/BST_BN']),
    'GNDC': (0.3, 0.15, 0.6, 0.3, ['GND']),
    'SUP': (0.25, 0.15, 0.6, 0.3, ['+3V3', '3V3_AMP', '5V_RADAR', '/3.3 V, Pi link, sensors, radar, echo-ref/3V3_SENS',
                                   '/3.3 V, Pi link, sensors, radar, echo-ref/LDO_IN', '/3.3 V, Pi link, sensors, radar, echo-ref/PI_3V3',
                                   '/Amplifier/GVDD', '/Amplifier/DVDD_REG', '/Amplifier/CPVSS', '/Amplifier/CP', '/Amplifier/CN']),
}
P5 = [(0.6, 0.6), (72.5, 0.6), (72.5, 8.8), (62.2, 8.8), (62.2, 14.6), (58.9, 14.6), (58.9, 20.4), (47.2, 20.4),
      (47.2, 14.6), (39.6, 14.6), (39.6, 27.6), (34.6, 27.6), (34.6, 14.6), (20.6, 14.6), (20.6, 40.0), (0.6, 40.0)]
P20 = [(21.2, 15.2), (34.0, 15.2), (34.0, 28.2), (44.0, 28.2), (44.0, 40.5), (21.2, 40.5)]
PPV = [(62.8, 9.4), (89.4, 9.4), (89.4, 34.6), (47.2, 34.6), (47.2, 21.0), (59.5, 21.0), (59.5, 15.2), (62.8, 15.2)]
FULL = [(0.4, 0.4), (89.6, 0.4), (89.6, 49.6), (0.4, 49.6)]


def zone(board, net, layer, pts, prio=0, thermal=False, clearance=0.3, minw=0.25):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(board.FindNet(net))
    ol = z.Outline()
    ol.NewOutline()
    for x, y in pts:
        ol.Append(MM(x), MM(y))
    z.SetAssignedPriority(prio)
    z.SetLocalClearance(MM(clearance))
    z.SetMinThickness(MM(minw))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL if thermal else pcbnew.ZONE_CONNECTION_FULL)
    z.SetThermalReliefGap(MM(0.4))
    z.SetThermalReliefSpokeWidth(MM(0.6))
    board.Add(z)
    return z


def setup(board):
    ns = board.GetDesignSettings().m_NetSettings
    ns.ClearNetclassPatternAssignments()
    ns.ClearNetclasses()
    for name, (tw, cl, vd, vdr, nets) in CLASSES.items():
        nc = pcbnew.NETCLASS(name)
        nc.SetTrackWidth(MM(tw)); nc.SetClearance(MM(cl)); nc.SetViaDiameter(MM(vd)); nc.SetViaDrill(MM(vdr))
        ns.SetNetclass(name, nc)
        for n in nets:
            ns.SetNetclassPatternAssignment(n.replace('+', '\\+').replace('.', '\\.'), name)
    ns.RecomputeEffectiveNetclasses()
    board.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
    board.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_POWER)
    zone(board, 'GND', pcbnew.In1_Cu, FULL, prio=0, thermal=False)
    zone(board, '+5V', pcbnew.In2_Cu, P5, prio=1)
    zone(board, '+20V', pcbnew.In2_Cu, P20, prio=1)
    zone(board, '/Amplifier/PVDD', pcbnew.In2_Cu, PPV, prio=1)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())


def outer_pours(board):
    for lay in (pcbnew.F_Cu, pcbnew.B_Cu):
        zone(board, 'GND', lay, FULL, prio=0, thermal=True, clearance=0.3)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())


def usb_links(board):
    """J2 USB4085: tie the VBUS pin pairs (A4-B9, A9-B4) on the back with short locked links."""
    j2 = board.FindFootprintByReference('J2')
    pos = {p.GetNumber(): p.GetPosition() for p in j2.Pads()}
    net = board.FindNet('/5 V supply and outputs/VBUS_PI')
    for a, c in (('A4', 'B9'), ('A9', 'B4')):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pos[a]); t.SetEnd(pos[c]); t.SetWidth(MM(0.6)); t.SetLayer(pcbnew.B_Cu); t.SetNet(net); t.SetLocked(True)
        board.Add(t)


def autoroute(board_path, passes=40):
    b = pcbnew.LoadBoard(board_path)
    for t in list(b.GetTracks()):
        b.Remove(t)
    for z in list(b.Zones()):
        if not z.GetIsRuleArea():
            b.Remove(z)
    setup(b)
    usb_links(b)
    added, failed = fo.fanout(b, {'+5V': P5, '+20V': P20, '/Amplifier/PVDD': PPV})
    print('fanout vias', added, 'failed', failed)
    pcbnew.SaveBoard(board_path, b)
    dsn = board_path.replace('.kicad_pcb', '.dsn')
    ses = board_path.replace('.kicad_pcb', '.ses')
    pcbnew.ExportSpecctraDSN(b, dsn)
    r = subprocess.run([JAVA, '-jar', FR, '-de', dsn, '-do', ses, '-mp', str(passes)], capture_output=True, text=True,
                       timeout=3000)
    log = [l for l in (r.stdout + r.stderr).splitlines() if 'INFO' in l or 'WARN' in l or 'ERROR' in l]
    b = pcbnew.LoadBoard(board_path)
    ok = pcbnew.ImportSpecctraSES(b, ses)
    outer_pours(b)
    pcbnew.SaveBoard(board_path, b)
    return ok, log


if __name__ == '__main__':
    ok, log = autoroute(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 40)
    print('import', ok)
    for l in log[-12:]:
        print(l[:220])
