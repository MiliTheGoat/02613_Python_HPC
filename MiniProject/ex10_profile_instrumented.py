"""
Exercise 10 – Profiling: 4 cases, clean summary table.

Runs:
  1. Unoptimised  N=50
  2. Unoptimised  N=100
  3. Optimised    N=50
  4. Optimised    N=100

Prints a comparison table at the end so speed-up is immediately obvious.

Usage: python ex10_profile_instrumented.py
"""
import time
from os.path import join

import cupy_setup
import cupy as cp
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

def jacobi_unoptimised(u, mask):
    """Sync every iteration via delta.item()."""
    u = u.copy()
    n_syncs = 0
    for i in range(MAX_ITER):
        u_new     = 0.25 * (u[1:-1,:-2] + u[1:-1,2:] + u[:-2,1:-1] + u[2:,1:-1])
        u_new_int = u_new[mask]
        delta     = cp.abs(u[1:-1,1:-1][mask] - u_new_int).max()
        u[1:-1,1:-1][mask] = u_new_int
        n_syncs += 1
        if delta.item() < ABS_TOL:
            break
    return u, n_syncs

def jacobi_optimised(u, mask):
    """Sync only every CHECK_FREQ iterations. Delta computed BEFORE update."""
    u = u.copy()
    n_syncs = 0
    for i in range(MAX_ITER):
        u_new     = 0.25 * (u[1:-1,:-2] + u[1:-1,2:] + u[:-2,1:-1] + u[2:,1:-1])
        u_new_int = u_new[mask]
        if (i + 1) % CHECK_FREQ == 0:
            delta = cp.abs(u[1:-1,1:-1][mask] - u_new_int).max()
            converged = delta.item() < ABS_TOL
            n_syncs += 1
        else:
            converged = False
        u[1:-1,1:-1][mask] = u_new_int
        if converged:
            break
    return u, n_syncs

def run_case(label, jacobi_fn, N, ids):
    """Run one case and return timing stats."""
    # warm-up
    _w = cp.zeros(1); _w + _w; cp.cuda.Stream.null.synchronize(); del _w

    total_syncs = 0
    t0 = time.perf_counter()

    for bid in ids[:N]:
        u_cpu, mask_cpu = load_data(bid)
        _, n_s = jacobi_fn(cp.asarray(u_cpu), cp.asarray(mask_cpu))
        total_syncs += n_s

    cp.cuda.Stream.null.synchronize()
    elapsed = time.perf_counter() - t0

    print(f"  [{label:22s}  N={N:3d}]  "
          f"total={elapsed:6.1f}s  "
          f"per_bld={elapsed/N:.3f}s  "
          f"syncs/bld={total_syncs//N:5d}  "
          f"est_all={elapsed/N*N_TOTAL/3600:.2f}h",
          flush=True)

    return elapsed, total_syncs // N

# ── Main ──────────────────────────────────────────────────────────────────────
with open(join(LOAD_DIR, "building_ids.txt")) as f:
    ids = f.read().splitlines()

gpu_name = cp.cuda.runtime.getDeviceProperties(0)["name"].decode()
print(f"\nGPU: {gpu_name}")
print(f"MAX_ITER={MAX_ITER}  ABS_TOL={ABS_TOL}  CHECK_FREQ={CHECK_FREQ}\n")

results = {}
for N in [50, 100]:
    for label, fn in [("Unoptimised", jacobi_unoptimised),
                      ("Optimised",   jacobi_optimised)]:
        key = (label, N)
        elapsed, syncs_per_bld = run_case(label, fn, N, ids)
        results[key] = (elapsed, elapsed / N, syncs_per_bld)

# ── Summary table ─────────────────────────────────────────────────────────────
print()
print("=" * 70)
print("  PROFILING SUMMARY – Exercise 10")
print("=" * 70)
print(f"  {'':22s}  {'N=50':>18}  {'N=100':>18}")
print(f"  {'':22s}  {'time  s/bld  sync/bld':>18}  {'time  s/bld  sync/bld':>18}")
print("-" * 70)

for label in ["Unoptimised", "Optimised"]:
    r50  = results[(label,  50)]
    r100 = results[(label, 100)]
    print(f"  {label:22s}  "
          f"{r50[0]:5.1f}s  {r50[1]:.3f}s  {r50[2]:5d}    "
          f"{r100[0]:5.1f}s  {r100[1]:.3f}s  {r100[2]:5d}")

print("-" * 70)
for N in [50, 100]:
    u = results[("Unoptimised", N)]
    o = results[("Optimised",   N)]
    speedup = u[0] / o[0]
    print(f"  Speed-up  (N={N:3d})               {speedup:.2f}×")

print("=" * 70)
u_best = results[("Unoptimised", 100)]
o_best = results[("Optimised",   100)]
print(f"  Estimated time for all {N_TOTAL} buildings:")
print(f"    Unoptimised : {u_best[1]*N_TOTAL/3600:.2f} h")
print(f"    Optimised   : {o_best[1]*N_TOTAL/3600:.2f} h")
print("=" * 70)
print(f"\n  Main issue: unoptimised has {results[('Unoptimised',50)][2]}x more GPU→CPU syncs per building.")
print(f"  Fix: check convergence every {CHECK_FREQ} iters → "
      f"{results[('Unoptimised',50)][2] // results[('Optimised',50)][2]}× fewer syncs.\n")