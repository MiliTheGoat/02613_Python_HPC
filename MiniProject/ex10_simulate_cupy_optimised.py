"""
Exercise 10: Optimised CuPy — fix the per-iteration GPU sync bottleneck.

THE PROBLEM (visible in nsys):
  In ex9, delta.item() forces a GPU→CPU sync on every single Jacobi
  iteration (up to 20 000 per building). The nsys CUDA API trace shows
  thousands of tiny DtoH cudaMemcpy calls keeping the GPU idle between
  kernel launches.

THE FIX:
  Check convergence only every CHECK_FREQ=100 iterations → 100x fewer
  synchronisations. The GPU can execute the intervening kernels
  asynchronously without stalling.

Usage: python ex10_simulate_cupy_optimised.py <N>
"""
import sys, time
from os.path import join
import numpy as np
import cupy as cp

LOAD_DIR   = "/dtu/projects/02613_2025/data/modified_swiss_dwellings/"
MAX_ITER   = 20_000
ABS_TOL    = 1e-4
CHECK_FREQ = 100    # ← only sync every 100 iterations
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
        u[1:-1,1:-1][mask] = u_new_int
        # Only pull delta to CPU every CHECK_FREQ steps
        if (i + 1) % check_freq == 0:
            delta = cp.abs(u[1:-1,1:-1][mask] - u_new_int).max()
            if delta.item() < atol:
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

# ── Main ──────────────────────────────────────────────────────────────────────
N = int(sys.argv[1]) if len(sys.argv) > 1 else 1

with open(join(LOAD_DIR, "building_ids.txt")) as f:
    ids = f.read().splitlines()[:N]

gpu_name = cp.cuda.runtime.getDeviceProperties(0)["name"].decode()
print(f"CuPy {cp.__version__} | GPU: {gpu_name} | CHECK_FREQ={CHECK_FREQ}", flush=True)
print(f"Processing {N} buildings\n", flush=True)

t0 = time.perf_counter()

rows = []
for bid in ids:
    u_cpu, mask_cpu = load_data(bid)
    u_gpu    = cp.asarray(u_cpu)
    mask_gpu = cp.asarray(mask_cpu)
    u_out    = jacobi_optimised(u_gpu, mask_gpu, MAX_ITER, ABS_TOL)
    rows.append((bid, summary_stats(u_out, mask_gpu)))

cp.cuda.Stream.null.synchronize()
elapsed = time.perf_counter() - t0

print(f"Time: {elapsed:.2f}s  |  {elapsed/N:.3f}s per building", flush=True)
print(f"Estimated for all {N_TOTAL} buildings: {elapsed/N*N_TOTAL/3600:.2f} h\n", flush=True)

keys = ["mean_temp", "std_temp", "pct_above_18", "pct_below_15"]
print("building_id," + ",".join(keys))
for bid, s in rows:
    print(f"{bid}," + ",".join(str(s[k]) for k in keys))
