"""
Exercise 10: Optimised CuPy – fix the per-iteration GPU sync bottleneck.

THE PROBLEM (visible in nsys cudaapisum):
  In ex9, delta.item() forces a GPU→CPU cudaMemcpy DtoH on EVERY Jacobi
  iteration. With up to 20 000 iterations per building this means up to
  20 000 blocking sync-points per building. The nsys trace confirms this:
  the unoptimised run (N=5) took 4.73 s/building while the GPU sat idle
  between each tiny scalar transfer.

THE FIX:
  Check convergence only every CHECK_FREQ=100 iterations so the GPU can
  run 100 kernels asynchronously before the CPU checks convergence.

  IMPORTANT – delta must be computed BEFORE updating u:
    delta = |u_old[mask] - u_new[mask]|
  If computed after the update, u[mask] == u_new_int always, giving
  delta == 0 and causing the solver to stop after just 100 iterations
  with a nearly unconverged result (wrong temperatures).

Usage: python ex10_simulate_cupy_optimised.py <N>
"""
import sys, time

import cupy_setup
import cupy as cp
from os.path import join
import numpy as np

LOAD_DIR   = "/dtu/projects/02613_2025/data/modified_swiss_dwellings/"
MAX_ITER   = 20_000
ABS_TOL    = 1e-4
CHECK_FREQ = 100
N_TOTAL    = 4571

def load_data(bid):
    u = np.zeros((514, 514), dtype=np.float32)
    u[1:-1, 1:-1] = np.load(join(LOAD_DIR, f"{bid}_domain.npy")).astype(np.float32)
    mask = np.load(join(LOAD_DIR, f"{bid}_interior.npy"))
    return u, mask

def jacobi_optimised(u, mask, max_iter, atol, check_freq=CHECK_FREQ):
    u = u.copy()
    for i in range(max_iter):
        u_new     = 0.25 * (u[1:-1,:-2] + u[1:-1,2:] + u[:-2,1:-1] + u[2:,1:-1])
        u_new_int = u_new[mask]

        # ── Compute delta BEFORE updating u ──────────────────────────────────
        # Only pay the GPU→CPU sync cost every check_freq steps.
        # Must be done here (before the assignment below) so we compare
        # the old interior values against the new ones, not 0 against 0.
        if (i + 1) % check_freq == 0:
            delta = cp.abs(u[1:-1,1:-1][mask] - u_new_int).max()
            converged = delta.item() < atol   # one sync per check_freq iters
        else:
            converged = False

        u[1:-1,1:-1][mask] = u_new_int        # ← update happens after check

        if converged:
            break
    return u

def summary_stats(u, mask):
    interior = u[1:-1,1:-1][mask]
    return {
        "mean_temp":    float(interior.mean()),
        "std_temp":     float(interior.std()),
        "pct_above_18": float(cp.sum(interior > 18) / interior.size * 100),
        "pct_below_15": float(cp.sum(interior < 15) / interior.size * 100),
    }

N = int(sys.argv[1]) if len(sys.argv) > 1 else 1

with open(join(LOAD_DIR, "building_ids.txt")) as f:
    ids = f.read().splitlines()[:N]

_w = cp.zeros(1); _w + _w; cp.cuda.Stream.null.synchronize(); del _w

gpu_name = cp.cuda.runtime.getDeviceProperties(0)["name"].decode()
print(f"CuPy {cp.__version__} | GPU: {gpu_name} | CHECK_FREQ={CHECK_FREQ}\n", flush=True)

t0 = time.perf_counter()
rows = []
for bid in ids:
    u_cpu, mask_cpu = load_data(bid)
    mask_gpu = cp.asarray(mask_cpu)
    u_out    = jacobi_optimised(cp.asarray(u_cpu), mask_gpu, MAX_ITER, ABS_TOL)
    rows.append((bid, summary_stats(u_out, mask_gpu)))

cp.cuda.Stream.null.synchronize()
elapsed = time.perf_counter() - t0

print(f"Time: {elapsed:.2f}s  |  {elapsed/N:.3f}s/building", flush=True)
print(f"Estimated for all {N_TOTAL}: {elapsed/N*N_TOTAL/3600:.2f} h\n", flush=True)

keys = ["mean_temp", "std_temp", "pct_above_18", "pct_below_15"]
print("building_id," + ",".join(keys))
for bid, s in rows:
    print(f"{bid}," + ",".join(str(s[k]) for k in keys))
