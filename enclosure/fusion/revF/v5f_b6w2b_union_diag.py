# rev F block 6w-2b (2026-11-05), read-only: B6w-2 stopped at its TemporaryBRep union gate (ASM_INCONS_FACE, nothing
#   joined). Which part, and which region of its fill, fails? Fill built exactly as in B6w-2 (build_fill). Per part: whole
#   union on a body copy. Per region (body copy and fill piece both cropped to the region box, the body with 3 mm margin):
#   chin y > −3; lower sides / door y < −3, z 6.5–60; upper sides / door z 60–160; top band z 160–175.3. Reports ok / error,
#   lumps, the piece's volume and tight world box.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b6w2_fill.py')).read())
import traceback
REG = {'chin_y>-3': (-3.0, 250.0, 0.0, 260.0), 'low_z<60': (-250.0, -3.0, 0.0, 60.0), 'mid_z60-160': (-250.0, -3.0, 60.0, 160.0),
       'top_z>160': (-250.0, -3.0, 160.0, 260.0)}


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        fpart, dpart = build_fill(X, out)
        out['t_fill_s'] = round(time.time() - t0, 1)
        for name, part in (('front', fpart), ('door', dpart)):
            body = X.body('HOUSING_F_' + name)
            q = X.tbm.copy(body)
            try:
                X.union(q, X.tbm.copy(part)); out[name + '_whole'] = ['ok', q.lumps.count, round(q.volume, 4)]
            except Exception as e:
                out[name + '_whole'] = ['fail', str(e)[:70]]
            reg = {}
            for rn, (y0, y1, z0, z1) in REG.items():
                pc = X.tbm.copy(part); inter(X, pc, X.wbox(-250, 250, y0, y1, z0, z1))
                if pc.volume <= 0:
                    reg[rn] = 'empty'; continue
                row = [round(pc.volume * 1000, 3), pc.lumps.count, [round(v, 1) for v in wbb(X, pc)]]
                bc = X.tbm.copy(body); inter(X, bc, X.wbox(-250, 250, y0 - 3, y1 + 3, z0 - 3, z1 + 3))
                try:
                    X.union(bc, pc); row += ['ok', bc.lumps.count]
                except Exception as e:
                    row += ['fail', str(e)[:50]]
                reg[rn] = row
            out[name + '_regions_[mm3, lumps, bbox, union, lumps]'] = reg
            out['t_%s_s' % name] = round(time.time() - t0, 1)
            log('v5f_b6w2b_union_diag', name, {k: out[k] for k in out if k.startswith(name)})
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b6w2b_union_diag', 'diag', out)
    print(json.dumps(out, separators=(',', ':')))
