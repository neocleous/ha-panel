"""rev F e6 (2026-11-09), offline (python3 + scipy): pull between two coaxial, axially magnetised disc magnets with
uniform magnetisation (surface-charge model, as R1): F = sum over the four face pairs of +-pi mu0 M^2 a^2
int_0^inf J1(ka)^2 e^(-kd) / k dk. Reproduces R1's 3.8 / 4.1 N (Br 1.42 / 1.48 T, D8 x 1.5 pair, 1.4 apart).
Prints the V24 table: per-pair pull and the door's pull-off force (sum of pull x |n_y| over the 10 stations, e6a2)."""
import numpy as np
from scipy import integrate, special
MU0 = 4e-7 * np.pi
NY = [0.7402, 0.777, 0.8354, 0.9101, 0.9385, 0.7402, 0.7769, 0.837, 0.91, 0.9386]   # |n_y| of the 10 wall normals


def f_pair(a1, a2, d):
    g = lambda k: special.j1(k * a1) * special.j1(k * a2) * np.exp(-k * d) / k
    return np.pi * a1 * a2 * integrate.quad(g, 0, np.inf, limit=500)[0]


def pull(D1, t1, D2, t2, gap, Br=1.45):
    """attractive force (N) between discs D1 x t1 and D2 x t2 (mm) whose facing faces are `gap` mm apart"""
    a1, a2, t1, t2, g = D1 / 2e3, D2 / 2e3, t1 / 1e3, t2 / 1e3, gap / 1e3
    k = MU0 * (Br / MU0) ** 2
    return k * (f_pair(a1, a2, g) + f_pair(a1, a2, g + t1 + t2) - f_pair(a1, a2, g + t1) - f_pair(a1, a2, g + t2))


if __name__ == '__main__':
    print('R1 check: D8 x 1.5 pair at 1.4: %.2f / %.2f N' % (pull(8, 1.5, 8, 1.5, 1.4, 1.42), pull(8, 1.5, 8, 1.5, 1.4, 1.48)))
    base = pull(8, 1.5, 8, 1.5, 1.60, 1.42)
    for name, t1, t2, g in (('1.5 + 1.5 (designed)', 1.5, 1.5, 1.60), ('2 + 1 (chosen)', 2.0, 1.0, 1.149),
                            ('2 + 2', 2.0, 2.0, 1.149), ('1 + 1', 1.0, 1.0, 1.60)):
        f = [pull(8, t1, 8, t2, g, b) for b in (1.42, 1.48)]
        print('%-22s faces %.3f apart: %.2f-%.2f N per pair (%3.0f %%), door pull-off %.0f-%.0f N'
              % (name, g, f[0], f[1], 100 * f[0] / base, sum(NY) * f[0], sum(NY) * f[1]))
