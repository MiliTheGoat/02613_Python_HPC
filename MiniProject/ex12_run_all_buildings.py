"""
Exercise 12 – Part A: Run optimised CuPy Jacobi on all 4571 buildings.
CSV is flushed every batch so progress is not lost if wall-time is hit.

Usage: python ex12_run_all_buildings.py
"""
import time
from os.path import join

import cupy_setup   # sets CUDA_PATH before cupy import
import cupy as cp
import numpy as np

LOAD_DIR   = "/dtu/projects/02613_2025/data/modified_swiss_dwellings/"
OUT_CSV    = "results/ex12_all_results.csv"
MAX_ITER   = 20_000
ABS_TOL    = 1e-4
CHECK_FREQ = 100
BATCH_SIZE = 50

def load_data(bid):
    u = np.zeros((514, 514), dtype=np.float32)
    u[1:-1, 1:-1] = np.load(join(LOAD_DIR, f"{bid}_domain.npy")).astype(np.float32)
    mask = np.load(join(LOAD_DIR, f"{bid}_interior.npy"))
    return u, mask

def jacobi(u, mask, max_iter, atol, check_freq):
    u = u.copy()
    for i in range(max_iter):
        u_new     = 0.25 * (u[1:-1,:-2] + u[1:-1,2:] + u[:-2,1:-1] + u[2:,1:-1])
        u_new_int = u_new[mask]
        u[1:-1,1:-1][mask] = u_new_int
        if (i + 1) % check_freq == 0:
            if cp.abs(u[1:-1,1:-1][mask] - u_new_int).max().item() < atol:
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

import os; os.makedirs("results", exist_ok=True)

# warm-up
_w = cp.zeros(1); _w + _w; cp.cuda.Stream.null.synchronize(); del _w

with open(join(LOAD_DIR, "building_ids.txt")) as f:
    ids = f.read().splitlines()
N_TOTAL = len(ids)

gpu_name = cp.cuda.runtime.getDeviceProperties(0)["name"].decode()
print(f"GPU: {gpu_name}  |  Buildings: {N_TOTAL}", flush=True)

keys = ["mean_temp", "std_temp", "pct_above_18", "pct_below_15"]
t0 = time.perf_counter()

with open(OUT_CSV, "w") as f:
    f.write("building_id," + ",".join(keys) + "\n")
    for start in range(0, N_TOTAL, BATCH_SIZE):
        batch = ids[start : start + BATCH_SIZE]
        for bid in batch:
            u_cpu, mask_cpu = load_data(bid)
            mask_gpu = cp.asarray(mask_cpu)
            u_out    = jacobi(cp.asarray(u_cpu), mask_gpu, MAX_ITER, ABS_TOL, CHECK_FREQ)
            s        = summary_stats(u_out, mask_gpu)
            f.write(f"{bid}," + ",".join(str(s[k]) for k in keys) + "\n")
        f.flush()
        n_done = start + len(batch)
        elapsed = time.perf_counter() - t0
        eta = (N_TOTAL - n_done) / n_done * elapsed / 60
        print(f"{n_done}/{N_TOTAL} ({n_done/N_TOTAL*100:.1f}%) "
              f"| {elapsed/60:.1f} min elapsed | ETA {eta:.1f} min", flush=True)

print(f"\nDone in {(time.perf_counter()-t0)/3600:.2f} h  →  {OUT_CSV}", flush=True)
