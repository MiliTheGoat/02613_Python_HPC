"""
Exercise 1: Load and visualize input data for a few floorplans.
Saves figures to the figures/ directory.
Usage: python visualize_floorplans.py [N]
  N: number of floorplans to visualize (default: 6)
"""

import sys
import os
from os.path import join

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# ── Config ────────────────────────────────────────────────────────────────────
LOAD_DIR = "/dtu/projects/02613_2025/data/modified_swiss_dwellings/"
OUT_DIR  = "figures"
SIZE     = 512

os.makedirs(OUT_DIR, exist_ok=True)

N = int(sys.argv[1]) if len(sys.argv) > 1 else 6

# ── Load building IDs ─────────────────────────────────────────────────────────
with open(join(LOAD_DIR, "building_ids.txt"), "r") as f:
    building_ids = f.read().splitlines()

building_ids = building_ids[:N]
print(f"Visualizing {N} floorplans: {building_ids}")

# ── Helper: load one building ─────────────────────────────────────────────────
def load_data(load_dir, bid):
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask  = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask

# ── Figure 1: Domain grids (initial temperature conditions) ───────────────────
ncols = min(N, 4)
nrows = (N + ncols - 1) // ncols

fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4.5 * nrows))
axes = np.array(axes).reshape(-1)   # flatten for easy indexing

# Custom colormap: 0 → grey (exterior/unset), 5 → cold blue, 25 → hot red
cmap_domain = plt.cm.plasma
norm_domain  = mcolors.Normalize(vmin=0, vmax=25)

for idx, bid in enumerate(building_ids):
    u, interior_mask = load_data(LOAD_DIR, bid)
    domain = u[1:-1, 1:-1]          # strip padding → 512×512

    ax = axes[idx]
    im = ax.imshow(domain, cmap=cmap_domain, norm=norm_domain, origin="upper")
    ax.set_title(f"ID: {bid}", fontsize=11, fontweight="bold")
    ax.set_xlabel("x [grid]")
    ax.set_ylabel("y [grid]")
    plt.colorbar(im, ax=ax, label="Temperature (°C)", fraction=0.046, pad=0.04)

# Hide any unused axes
for idx in range(N, len(axes)):
    axes[idx].set_visible(False)

fig.suptitle(
    "Initial Conditions (domain)\n"
    "Inside walls = 25 °C  |  Load-bearing walls = 5 °C  |  Interior = 0 °C",
    fontsize=13, y=1.01
)
fig.tight_layout()
path_domain = join(OUT_DIR, "domain_initial_conditions.png")
fig.savefig(path_domain, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {path_domain}")

# ── Figure 2: Interior masks ───────────────────────────────────────────────────
fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4.5 * nrows))
axes = np.array(axes).reshape(-1)

cmap_mask = mcolors.ListedColormap(["#1a1a2e", "#e8e8e8"])   # dark exterior, light interior

for idx, bid in enumerate(building_ids):
    u, interior_mask = load_data(LOAD_DIR, bid)

    ax = axes[idx]
    ax.imshow(interior_mask.astype(float), cmap=cmap_mask, vmin=0, vmax=1, origin="upper")
    ax.set_title(f"ID: {bid}", fontsize=11, fontweight="bold")
    ax.set_xlabel("x [grid]")
    ax.set_ylabel("y [grid]")

    # Small legend patches
    from matplotlib.patches import Patch
    legend = [Patch(color="#e8e8e8", label="Interior (1)"),
              Patch(color="#1a1a2e", label="Wall / Exterior (0)")]
    ax.legend(handles=legend, loc="lower right", fontsize=8, framealpha=0.8)

for idx in range(N, len(axes)):
    axes[idx].set_visible(False)

fig.suptitle("Interior Masks\nWhite = interior room points that will be updated by Jacobi",
             fontsize=13, y=1.01)
fig.tight_layout()
path_mask = join(OUT_DIR, "interior_masks.png")
fig.savefig(path_mask, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {path_mask}")

# ── Figure 3: Side-by-side domain + mask for each building ───────────────────
fig, axes = plt.subplots(N, 2, figsize=(10, 4.5 * N))
if N == 1:
    axes = axes[np.newaxis, :]      # keep 2-D when N=1

for idx, bid in enumerate(building_ids):
    u, interior_mask = load_data(LOAD_DIR, bid)
    domain = u[1:-1, 1:-1]

    # Domain
    ax0 = axes[idx, 0]
    im = ax0.imshow(domain, cmap=cmap_domain, norm=norm_domain, origin="upper")
    ax0.set_title(f"ID {bid} — Domain", fontsize=10, fontweight="bold")
    ax0.axis("off")
    plt.colorbar(im, ax=ax0, label="°C", fraction=0.046, pad=0.04)

    # Mask
    ax1 = axes[idx, 1]
    ax1.imshow(interior_mask.astype(float), cmap=cmap_mask, vmin=0, vmax=1, origin="upper")
    ax1.set_title(f"ID {bid} — Interior Mask", fontsize=10, fontweight="bold")
    ax1.axis("off")

    # Annotate some quick stats
    n_interior = interior_mask.sum()
    frac       = n_interior / interior_mask.size * 100
    ax1.set_xlabel(
        f"Interior points: {n_interior:,}  ({frac:.1f}% of grid)",
        fontsize=8
    )
    ax1.xaxis.set_label_position("bottom")
    ax1.set_xlabel(
        f"Interior: {n_interior:,} pts  ({frac:.1f}%)",
        fontsize=9
    )

fig.suptitle("Wall Heating – Input Data Overview", fontsize=14, fontweight="bold")
fig.tight_layout()
path_combined = join(OUT_DIR, "domain_and_mask_combined.png")
fig.savefig(path_combined, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {path_combined}")

# ── Quick statistics printout ─────────────────────────────────────────────────
print("\n── Quick stats per floorplan ──────────────────────────────")
print(f"{'ID':>10}  {'Grid size':>10}  {'Interior pts':>13}  {'Interior %':>11}  "
      f"{'Wall pts (5°C)':>14}  {'Wall pts (25°C)':>15}")
print("-" * 85)
for bid in building_ids:
    u, interior_mask = load_data(LOAD_DIR, bid)
    domain = u[1:-1, 1:-1]
    n_int  = interior_mask.sum()
    n_cold = (domain == 5).sum()
    n_hot  = (domain == 25).sum()
    print(f"{bid:>10}  {SIZE}x{SIZE:>{4}}  {n_int:>13,}  {n_int/domain.size*100:>10.1f}%  "
          f"{n_cold:>14,}  {n_hot:>15,}")

print(f"\nAll figures saved to ./{OUT_DIR}/")