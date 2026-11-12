# rev F k1b (2026-11-12): fix pass, block 1 - a relief in the front face of each box tab, round the screw hole: dia 5.2, 1.0 deep along
#   the screw's line. It takes up the rim of the shell's insert if that rim stands proud of the boss face (a tilted insert pressed with a
#   tip whose shoulder is wider than the hole stops 0.5 short at its centre, 0.9 at the high side of its rim), so that the tab always
#   seats flat on the boss. The current box body is replaced in place (the _v55 backup of block 1 stays the backup).
#   main(X, apply=False): k1a's namespace must be in k.c['k1a'].
RELIEF_R = 2.6; RELIEF_T = 1.0


def main(X, apply=False):
    ns = k.c['k1a']; out = {}
    for name, sx in (('SPKBOX_L', 1), ('SPKBOX_R', -1)):
        b = X.body(name); new = X.cp(b)
        m = ns['mouth'](sx); a = ns['a_in'](sx)
        X.dif(new, X.cyl(k.along(m, a, 0.5), k.along(m, a, -RELIEF_T), RELIEF_R))
        rem = X.cp(b); X.dif(rem, new)
        out[name] = {'vol old/new': [round(b.volume * 1000.0, 1), round(X.vol(new), 1)], 'lumps': new.lumps.count, 'removed': X.lumps(rem)}
        if apply:
            if X.body(name + '_v55') is None:
                raise RuntimeError('no backup of ' + name)
            vis = b.isLightBulbOn; like = X.body(name + '_v55')
            b.deleteMe()
            nb = X.add(new, name, like=like, show=vis)
            out[name]['applied'] = [round(nb.volume * 1000.0, 1), nb.lumps.count]
        print(name, out[name])
    if apply:
        print('purged', k.purge(['SPKBOX_']), 'dups', X.dups(), 'bodies', len(X.names()))
    return out
