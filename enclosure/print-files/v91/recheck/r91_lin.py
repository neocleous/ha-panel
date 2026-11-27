#!/usr/bin/env python3
# Print re-check's second look on version 85: arcs in the G-code made straight for the readers. Pure Python 3, outside Fusion.
# Bambu Studio 02.09.02.62 writes support lines as arcs (G2/G3 with I, J); 02.09.01.70 wrote them as straight moves. Part C's
# index (cgq.index_gcode) reads an arc as its chord and drops a full circle, so every reading of support built on it would be
# short. This writes, beside a job's plate_1.gcode, a copy plate_1.lin.gcode in which every EXTRUDING arc is replaced by straight
# moves that stay within `tol` of the arc (the filament shared out evenly), and builds the job's index.pkl from that copy.
# The slicer's own file is not changed. Arcs that do not extrude (the spiral lift) are passed on as they are.
#   lin  args: job (slice folder), tol (0.005)
#   A list of commands may follow a 'lin' in one call: any other 'cmd' is part C's own (stat, ovh, mis ...), run in this process.
import sys, os, json, math, time
PC = os.path.expanduser('~/Documents/HA_panel_renders/adversarial_audit_v69/c')
sys.path.insert(0, PC)
import cgq                                                    # noqa: E402
TWO_PI = 2.0 * math.pi


def cmd_lin(a):
    t0 = time.time(); job = a['job']; tol = a.get('tol', 0.005)
    gp = os.path.join(job, 'plate_1.gcode'); lp = os.path.join(job, 'plate_1.lin.gcode'); ip = os.path.join(job, 'index.pkl')
    x = y = 0.0; feat = 'none'; S = {}; rel = True
    with open(gp, errors='replace') as f, open(lp, 'w') as o:
        for ln in f:
            c2 = ln[:3]
            if c2 == 'G1 ' or c2 == 'G0 ':
                sc = ln.find(';'); body = ln if sc < 0 else ln[:sc]
                for tok in body.split()[1:]:
                    if tok[0] == 'X':
                        x = float(tok[1:])
                    elif tok[0] == 'Y':
                        y = float(tok[1:])
                o.write(ln); continue
            if c2 == 'G2 ' or c2 == 'G3 ':
                sc = ln.find(';'); body = ln if sc < 0 else ln[:sc]
                nx = x; ny = y; I = J = 0.0; e = None
                for tok in body.split()[1:]:
                    k = tok[0]
                    if k == 'X':
                        nx = float(tok[1:])
                    elif k == 'Y':
                        ny = float(tok[1:])
                    elif k == 'I':
                        I = float(tok[1:])
                    elif k == 'J':
                        J = float(tok[1:])
                    elif k == 'E':
                        e = float(tok[1:])
                if e is None or e <= 0:
                    o.write(ln); x = nx; y = ny; continue
                if not rel:
                    raise RuntimeError('an extruding arc with absolute E: not handled')
                cx = x + I; cy = y + J; r = math.hypot(I, J); chord = math.hypot(nx - x, ny - y)
                a0 = math.atan2(y - cy, x - cx); a1 = math.atan2(ny - cy, nx - cx); sg = 1.0 if c2 == 'G3 ' else -1.0
                if chord < 1e-6:
                    sw = TWO_PI
                else:
                    sw = (sg * (a1 - a0)) % TWO_PI
                    if sw < 1e-6:
                        sw = chord / max(r, 1e-9)
                step = 2.0 * math.acos(max(-1.0, 1.0 - tol / r)) if r > tol else math.pi / 2
                n = max(1, int(math.ceil(sw / step)))
                for i in range(1, n + 1):
                    if i == n:
                        px, py = nx, ny
                    else:
                        an = a0 + sg * sw * i / n; px = cx + r * math.cos(an); py = cy + r * math.sin(an)
                    o.write('G1 X%.3f Y%.3f E%.5f\n' % (px, py, e / n))
                s = S.setdefault(feat, [0, 0, 0.0, 0.0, 0, 0.0])
                s[0] += 1; s[1] += n; s[2] += r * sw; s[3] += chord; s[4] += (chord < 1e-6); s[5] = max(s[5], math.degrees(sw))
                x = nx; y = ny; continue
            if ln.startswith('; FEATURE: '):
                feat = ln[11:].strip()
            elif ln.startswith('M82'):
                rel = False
            elif ln.startswith('M83'):
                rel = True
            o.write(ln)
    ix = cgq.index_gcode(lp, ip)
    tot = [sum(s[i] for s in S.values()) for i in range(5)]
    print('lin %s: extruding arcs %d -> %d straight moves; arc length %.1f mm, their chords %.1f mm (%.1f mm short), full circles %d | index: %d layers, %d moves | %.1f s' % (
        os.path.basename(job), tot[0], tot[1], tot[2], tot[3], tot[2] - tot[3], tot[4], len(ix['layers']), ix['moves'], time.time() - t0))
    for k in sorted(S):
        s = S[k]
        print('   %-20s arcs %6d, length %9.1f mm, chords %9.1f mm, full circles %d, widest sweep %.0f deg' % (k, s[0], s[2], s[3], s[4], s[5]))
    json.dump({'job': os.path.basename(job), 'by': {k: {'arcs': s[0], 'moves': s[1], 'arc_mm': round(s[2], 1), 'chord_mm': round(s[3], 1), 'full': s[4], 'widest_deg': round(s[5], 1)} for k, s in S.items()}},
              open(os.path.join(job, 'lin.json'), 'w'), indent=1)


if __name__ == '__main__':
    arg = sys.argv[2]
    A = json.load(open(arg)) if os.path.exists(arg) else json.loads(arg)
    for a in (A if isinstance(A, list) else [A]):
        try:
            if a.get('cmd', 'lin') == 'lin':
                cmd_lin(a)
            else:                                             # part C's own commands, run on the index made here
                cgq.CMDS[a['cmd']](a)
        except Exception:
            import traceback
            print('ERROR', json.dumps(a)[:300]); traceback.print_exc()
        sys.stdout.flush()
# END r91_lin.py
