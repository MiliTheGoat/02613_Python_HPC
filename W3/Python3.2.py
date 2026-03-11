from time import perf_counter as time

import numpy as np

# Only row
ns = np.ceil(np.logspace(2, 8, 30))
trows = []
n_repeat = int(1e2)
for n in ns:
    n = int(n)
    mat = np.random.rand(1, n)
    trow = time()
    for _ in range(n_repeat):
        mat[0, :] * 2
    trow = time() - trow
    trows.append(trow / n_repeat)

print('ns =', list(ns))
print('trows =', trows)