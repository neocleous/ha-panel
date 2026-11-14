"""The amplifier's supply (PVDD) copper: resistance from its fuse F5 to the amplifier chip's PVDD pins and to its bulk
capacitors, on two board files (rev 3.1 and rev 3.2), with the repository's solver (rev3.1/check/rnet.py).
    python3 pvdd_path.py <rev3.1/check dir> <board a> <board b>"""
import sys, time
sys.path.insert(0, sys.argv[1])
import pcb, rnet
NET = '/Amplifier/PVDD'
SRC = [('pad', 'F5', '2', 'F.Cu')]
AMP = [('pad', 'U100', n, 'F.Cu') for n in ('6', '7', '41', '42', '43')]
CAPS = [('pad', c, '1', 'F.Cu') for c in ('C100', 'C101', 'C102')]
for path in sys.argv[2:4]:
    b = pcb.load(path); t = time.time()
    r1 = rnet.Net(b, [NET], (50, 0, 87, 50), 0.1).solve(SRC, AMP)[0]
    r2 = rnet.Net(b, [NET], (50, 0, 87, 50), 0.1).solve(SRC, CAPS)[0]
    print('%s: PVDD, fuse F5 -> chip pins (tied) %.3f mohm; fuse F5 -> C100-C102 (tied) %.3f mohm  (%.0f s)' % (path, r1 * 1e3, r2 * 1e3, time.time() - t))
