"""
Exercise 9: Jacobi solver on GPU with CuPy.
Usage: python ex9_simulate_cupy.py <N>
"""
import sys, time

# ── Must come before 'import cupy' ───────────────────────────────────────────
import cupy_setup   # sets CUDA_PATH so nvrtc can find the right headers

import cupy as cp
from os.path import join
import numpy as np

LOAD_DIR = "/dtu/projects/02613_2025/data/modified_swiss_dwellings/"
MAX_ITER = 20_000
ABS_TOL  = 1e-4
N_TOTAL  = 4571

def load_data(bid):
    u = np.zeros((514, 514), dtype=np.float32)
    u[1:-1, 1:-1] = np.load(join(LOAD_DIR, f"{bid}_domain.npy")).astype(np.float32)
    mask = np.load(join(LOAD_DIR, f"{bid}_interior.npy"))
    return u, mask

def jacobi(u, mask, max_iter, atol):
    u = u.copy()
    for i in range(max_iter):
        u_new     = 0.25 * (u[1:-1,:-2] + u[1:-1,2:] + u[:-2,1:-1] + u[2:,1:-1])
        u_new_int = u_new[mask]
        delta     = cp.abs(u[1:-1,1:-1][mask] - u_new_int).max()
        u[1:-1,1:-1][mask] = u_new_int
        if delta.item() < atol:   # .item() = GPU→CPU sync every iter (see ex10)
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

# Warm-up: trigger kernel compilation once before timing
_w = cp.zeros(1); _w + _w; cp.cuda.Stream.null.synchronize(); del _w

gpu_name = cp.cuda.runtime.getDeviceProperties(0)["name"].decode()
print(f"CuPy {cp.__version__} | CUDA_PATH={__import__('os').environ.get('CUDA_PATH','?')}", flush=True)
print(f"GPU: {gpu_name} | N={N}\n", flush=True)

t0 = time.perf_counter()
rows = []
for bid in ids:
    u_cpu, mask_cpu = load_data(bid)
    u_out = jacobi(cp.asarray(u_cpu), cp.asarray(mask_cpu), MAX_ITER, ABS_TOL)
    rows.append((bid, summary_stats(u_out, cp.asarray(mask_cpu))))

cp.cuda.Stream.null.synchronize()
elapsed = time.perf_counter() - t0

print(f"Time: {elapsed:.2f}s  |  {elapsed/N:.3f}s/building", flush=True)
print(f"Estimated for all {N_TOTAL}: {elapsed/N*N_TOTAL/3600:.2f} h\n", flush=True)

keys = ["mean_temp", "std_temp", "pct_above_18", "pct_below_15"]
print("building_id," + ",".join(keys))
for bid, s in rows:
    print(f"{bid}," + ",".join(str(s[k]) for k in keys))
