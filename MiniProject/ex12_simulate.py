"""
Exercise 12 – Script 1/3: ex12_simulate.py
Simulates one slice of buildings using the optimised Jacobi from Exercise 10.
Called by the job array in ex12_run.sh with <start> <end> arguments.

Output: results/ex12_<start>_<end>.csv

Usage: python ex12_simulate.py <start> <end>
"""
import sys, time, os
from os.path import join

import cupy_setup          # sets CUDA_PATH before cupy import
import cupy as cp
import numpy as np

LOAD_DIR   = "/dtu/projects/02613_2025/data/modified_swiss_dwellings/"
MAX_ITER   = 20_000
ABS_TOL    = 1e-4
CHECK_FREQ = 100

if len(sys.argv) != 3:
    print("Usage: python ex12_simulate.py <start> <end>")
    sys.exit(1)

START = int(sys.argv[1])
END   = int(sys.argv[2])

# ── Jacobi from Exercise 10 ───────────────────────────────────────────────────
def jacobi_optimised(u, mask):
    """Sync only every CHECK_FREQ iterations. Delta computed BEFORE update."""
    u = u.copy()
    n_syncs = 0
    for i in range(MAX_ITER):
        u_new     = 0.25 * (u[1:-1,:-2] + u[1:-1,2:] + u[:-2,1:-1] + u[2:,1:-1])
        u_new_int = u_new[mask]
        if (i + 1) % CHECK_FREQ == 0:
            delta     = cp.abs(u[1:-1,1:-1][mask] - u_new_int).max()
            converged = delta.item() < ABS_TOL
            n_syncs  += 1
        else:
            converged = False
        u[1:-1,1:-1][mask] = u_new_int   # update AFTER delta check
        if converged:
            break
    return u, n_syncs

def load_data(bid):
    u = np.zeros((514, 514), dtype=np.float32)
    u[1:-1, 1:-1] = np.load(join(LOAD_DIR, f"{bid}_domain.npy")).astype(np.float32)
    mask = np.load(join(LOAD_DIR, f"{bid}_interior.npy"))
    return u, mask

def summary_stats(u, mask):
    interior = u[1:-1,1:-1][mask]
    return {
        "mean_temp":    float(interior.mean()),
        "std_temp":     float(interior.std()),
        "pct_above_18": float(cp.sum(interior > 18) / interior.size * 100),
        "pct_below_15": float(cp.sum(interior < 15) / interior.size * 100),
    }

# ── Setup ─────────────────────────────────────────────────────────────────────
os.makedirs("results", exist_ok=True)
OUT_CSV = f"results/ex12_{START}_{END}.csv"

with open(join(LOAD_DIR, "building_ids.txt")) as f:
    ids = f.read().splitlines()[START:END]
N = len(ids)

# GPU warm-up so first building isn't penalised by JIT compile
_w = cp.zeros(1); _w + _w; cp.cuda.Stream.null.synchronize(); del _w

gpu_name = cp.cuda.runtime.getDeviceProperties(0)["name"].decode()
print(f"GPU    : {gpu_name}", flush=True)
print(f"Slice  : [{START}, {END})  =  {N} buildings", flush=True)
print(f"Output : {OUT_CSV}\n", flush=True)

# ── Simulate ──────────────────────────────────────────────────────────────────
keys = ["mean_temp", "std_temp", "pct_above_18", "pct_below_15"]
t0   = time.perf_counter()

with open(OUT_CSV, "w") as f:
    f.write("building_id," + ",".join(keys) + "\n")
    for i, bid in enumerate(ids):
        u_cpu, mask_cpu = load_data(bid)
        mask_gpu        = cp.asarray(mask_cpu)
        u_out, _        = jacobi_optimised(cp.asarray(u_cpu), mask_gpu)
        s               = summary_stats(u_out, mask_gpu)
        f.write(f"{bid}," + ",".join(str(s[k]) for k in keys) + "\n")

        if (i + 1) % 100 == 0:
            elapsed = time.perf_counter() - t0
            eta     = (N - i - 1) / (i + 1) * elapsed / 60
            print(f"  {i+1}/{N} ({(i+1)/N*100:.1f}%) "
                  f"| {elapsed/60:.1f} min elapsed | ETA {eta:.1f} min", flush=True)

elapsed = time.perf_counter() - t0
print(f"\nDone in {elapsed/60:.1f} min  →  {OUT_CSV}", flush=True)
