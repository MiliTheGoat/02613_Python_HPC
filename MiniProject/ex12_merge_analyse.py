"""
Exercise 12 – Script 2/3: ex12_merge_analyse.py
Merges the 7 slice CSVs produced by the job array, then answers all
sub-questions with printed results and saved figures.

Questions answered:
  Q1  Distribution of mean temperatures (histogram saved to figures/)
  Q2  Average mean temperature
  Q3  Average temperature standard deviation
  Q4  Buildings with >= 50% area above 18 °C
  Q5  Buildings with >= 50% area below 15 °C

Usage: python ex12_merge_analyse.py
"""
import glob, os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

os.makedirs("figures", exist_ok=True)
os.makedirs("results", exist_ok=True)

# ── Step 1: Merge ─────────────────────────────────────────────────────────────
slices  = sorted(glob.glob("results/ex12_[0-9]*_[0-9]*.csv"))
print(f"Found {len(slices)} slice files:")

dfs     = []
skipped = []
for path in slices:
    if os.path.getsize(path) == 0:
        print(f"  SKIPPED (empty)  : {path}")
        skipped.append(path)
        continue
    try:
        df = pd.read_csv(path)
        if df.empty:
            print(f"  SKIPPED (no rows): {path}")
            skipped.append(path)
        else:
            print(f"  OK  {len(df):>4} rows   : {path}")
            dfs.append(df)
    except Exception as e:
        print(f"  SKIPPED ({e})    : {path}")
        skipped.append(path)

if skipped:
    print(f"\nWARNING: {len(skipped)} slice(s) could not be read — results will be incomplete.")

if not dfs:
    raise RuntimeError("No readable slice files found.")

merged  = pd.concat(dfs, ignore_index=True).sort_values("building_id").reset_index(drop=True)
MERGED_CSV = "results/ex12_all_results.csv"
merged.to_csv(MERGED_CSV, index=False)
print(f"\nMerged {len(merged)} buildings → {MERGED_CSV}")

if len(merged) != 4571:
    print(f"WARNING: expected 4571 buildings, got {len(merged)}.")
    print("Some slice jobs may not have finished. Re-run missing indices.")
else:
    print("All 4571 buildings present.")

# ── Step 2: Analyse ───────────────────────────────────────────────────────────
df = merged
N  = len(df)
print(f"\n{'='*52}")
print("  DESCRIPTIVE STATISTICS")
print(f"{'='*52}")
print(df[["mean_temp","std_temp","pct_above_18","pct_below_15"]].describe().round(3).to_string())

# Q2 & Q3
avg_mean = df["mean_temp"].mean()
avg_std  = df["std_temp"].mean()

# Q4 & Q5
n_above  = (df["pct_above_18"] >= 50).sum()
n_below  = (df["pct_below_15"] >= 50).sum()

print(f"\n{'='*52}")
print("  ANSWERS")
print(f"{'='*52}")
print(f"  Q2  Avg mean temperature       : {avg_mean:.3f} °C")
print(f"  Q3  Avg temperature std dev    : {avg_std:.3f} °C")
print(f"  Q4  Buildings >=50% above 18°C : {n_above}/{N}  ({n_above/N*100:.1f}%)")
print(f"  Q5  Buildings >=50% below 15°C : {n_below}/{N}  ({n_below/N*100:.1f}%)")
print(f"{'='*52}")

# ── Q1: Histograms ────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 4, figsize=(16, 4))
fig.suptitle("Distribution of simulation statistics – all 4571 buildings",
             fontsize=12, fontweight="bold")

configs = [
    ("mean_temp",    "Mean temperature (°C)",       "#e07b39"),
    ("std_temp",     "Std dev of temperature (°C)", "#4c72b0"),
    ("pct_above_18", "% area above 18 °C",          "#2ca02c"),
    ("pct_below_15", "% area below 15 °C",          "#d62728"),
]
for ax, (col, xlabel, color) in zip(axes, configs):
    data = df[col].dropna()
    ax.hist(data, bins=60, color=color, edgecolor="white", linewidth=0.3, alpha=0.88)
    ax.axvline(data.mean(), color="black", linestyle="--", lw=1.3,
               label=f"mean = {data.mean():.2f}")
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel("# buildings", fontsize=9)
    ax.legend(fontsize=8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
hist_path = "figures/ex12_distributions.png"
fig.savefig(hist_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"\nHistogram saved → {hist_path}")

# ── Extra scatter ─────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
sc = ax.scatter(df["mean_temp"], df["std_temp"],
                c=df["pct_above_18"], cmap="RdYlGn",
                s=4, alpha=0.5, rasterized=True)
fig.colorbar(sc, ax=ax, label="% area above 18 °C")
ax.set_xlabel("Mean temperature (°C)")
ax.set_ylabel("Temperature std dev (°C)")
ax.set_title("Mean vs Std Dev — colour = % above 18 °C")
ax.grid(alpha=0.3)
plt.tight_layout()
scatter_path = "figures/ex12_mean_vs_std.png"
fig.savefig(scatter_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"Scatter saved    → {scatter_path}")
