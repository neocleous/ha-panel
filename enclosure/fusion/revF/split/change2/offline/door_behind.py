# change2/offline/door_behind.py - what lies behind the door (seen from behind, rays along +y): the shell's lip and the nearest parts.
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import model as M, numpy as np
import matplotlib.pyplot as plt
R = M.raw()
xs = np.arange(-80, 80.01, 1.0); zs = np.arange(2, 158.01, 1.0)
X, Z = np.meshgrid(xs, zs)
org = np.c_[X.ravel(), np.full(X.size, -120.0), Z.ravel()]; dr = np.tile([0, 1.0, 0], (len(org), 1))


def hits(name, mode='first', after=None):
    m = M.mesh(name, 'w')
    loc, ray, tri = m.ray.intersects_location(org, dr, multiple_hits=True)
    f = np.full(len(org), np.nan)
    if len(ray):
        y = loc[:, 1]
        for l, r in zip(y, ray):
            if after is not None and not (l > after[r] + 0.05):
                continue
            if np.isnan(f[r]) or (l < f[r] if mode == 'first' else l > f[r]):
                f[r] = l
    return f


dl = hits('HOUSING_F_door', 'last')
sh = hits('HOUSING_F_front', 'first', after=dl - 5.0)
names = [n for n in R if n not in ('HOUSING_F_door', 'REF_F_outer', 'HOUSING_F_front', 'GROMMET_usbc_F') and not n.startswith('KO_')]
best = np.full(len(org), np.nan); who = np.full(len(org), -1)
for i, n in enumerate(names):
    f = hits(n, 'first')
    upd = (~np.isnan(f)) & (np.isnan(best) | (f < best))
    best[upd] = f[upd]; who[upd] = i
sp = X.shape
gap = (best - dl).reshape(sp); lipgap = (sh - dl).reshape(sp); who = who.reshape(sp)
np.savez(os.path.join(M.D, 'door_behind.npz'), xs=xs, zs=zs, gap=gap, who=who, lipgap=lipgap, dl=dl.reshape(sp), names=np.array(names))
fig, ax = plt.subplots(1, 2, figsize=(20, 10))
im = ax[0].imshow(np.clip(lipgap, -1, 30), origin='lower', extent=[xs[0], xs[-1], zs[0], zs[-1]], cmap='viridis'); plt.colorbar(im, ax=ax[0], shrink=0.7)
ax[0].set_title('shell behind the door: distance from the door inner face (mm, clipped 30); small = lip')
im = ax[1].imshow(np.clip(gap, 0, 40), origin='lower', extent=[xs[0], xs[-1], zs[0], zs[-1]], cmap='magma'); plt.colorbar(im, ax=ax[1], shrink=0.7)
ax[1].set_title('first part behind the door: distance from the door inner face (mm, clipped 40)')
for a in ax:
    a.set_xticks(np.arange(-80, 81, 10)); a.set_yticks(np.arange(0, 160, 10)); a.grid(True, lw=0.3)
fig.tight_layout(); fig.savefig(os.path.join(M.D, '..', 'img', 'door_behind.png'), dpi=70)
for (x0, x1, z0, z1) in ((-36, 36, 54, 66), (-36, 36, 66, 110), (-36, 36, 110, 118), (-45, -25, 66, 110), (25, 45, 66, 110)):
    sel = (X >= x0) & (X <= x1) & (Z >= z0) & (Z <= z1) & ~np.isnan(gap)
    if sel.any():
        g = np.where(sel, gap, np.inf); jj = np.unravel_index(np.argmin(g), g.shape)
        print((x0, x1, z0, z1), 'nearest part behind: %.1f mm, %s at x %.0f z %.0f; median %.1f' % (gap[jj], names[who[jj]], X[jj], Z[jj], np.nanmedian(gap[sel])))
# lip inner edge: for each z the x range where no shell lies within 6 mm behind the door
for z in (50, 56, 60, 66, 80, 96, 100, 104, 108, 110, 112, 114, 116, 120, 126):
    j = int(round(z - zs[0])); row = lipgap[j]
    free = np.where(np.isnan(row) | (row > 6.0))[0]
    has = np.where(~np.isnan(dl.reshape(sp)[j]))[0]
    inner = [i for i in free if i in set(has)]
    print('z', z, 'door x %.0f..%.0f' % (xs[has[0]], xs[has[-1]]), 'open behind (no shell within 6): x %.0f..%.0f' % (xs[inner[0]], xs[inner[-1]]) if inner else 'none')
