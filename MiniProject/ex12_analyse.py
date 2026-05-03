"""
Exercise 12 – Part B: Analyse results with pandas, answer all sub-questions.

Q1  Distribution of mean temperatures (histogram)
Q2  Average mean temperature
Q3  Average temperature standard deviation
Q4  Buildings with >= 50% area above 18 C
Q5  Buildings with >= 50% area below 15 C

Usage: python ex12_analyse.py          (reads results/ex12_all_results.csv)
       python ex12_analyse.py my.csv   (custom path)
"""
import sys, os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

CSV = sys.argv[1] if len(sys.argv) > 1 else "results/ex12_all_results.csv"
os.makedirs("figures", exist_ok=True)

df = pd.read_csv(CSV)
N  = len(df)
print(f"Loaded {N} buildings from {CSV}\n")
print(df[["mean_temp","std_temp","pct_above_18","pct_below_15"]].describe().round(3))
print()

# ── Q2 & Q3 ──────────────────────────────────────────────────────────────────
avg_mean = df["mean_temp"].mean()
avg_std  = df["std_temp"].mean()

# ── Q4 & Q5 ──────────────────────────────────────────────────────────────────
n_above = (df["pct_above_18"] >= 50).sum()
n_below = (df["pct_below_15"] >= 50).sum()

print("=" * 50)
print(f"Q2  Avg mean temperature       : {avg_mean:.3f} °C")
print(f"Q3  Avg temperature std dev    : {avg_std:.3f} °C")
print(f"Q4  Buildings ≥50% above 18°C  : {n_above} / {N}  ({n_above/N*100:.1f}%)")
print(f"Q5  Buildings ≥50% below 15°C  : {n_below} / {N}  ({n_below/N*100:.1f}%)")
print("=" * 50)

# ── Q1: Histograms ────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 4, figsize=(16, 4))
fig.suptitle("Distribution of simulation statistics – all buildings",
             fontsize=12, fontweight="bold")

configs = [
    ("mean_temp",    "Mean temperature (°C)",      "#e07b39"),
    ("std_temp",     "Std dev of temperature (°C)","#4c72b0"),
    ("pct_above_18", "% area above 18 °C",          "#2ca02c"),
    ("pct_below_15", "% area below 15 °C",          "#d62728"),
]

for ax, (col, xlabel, color) in zip(axes, configs):
    data = df[col].dropna()
    ax.hist(data, bins=60, color=color, edgecolor="white", linewidth=0.3, alpha=0.88)
    ax.axvline(data.mean(), color="black", linestyle="--", lw=1.3,
               label=f"mean={data.mean():.2f}")
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel("# buildings", fontsize=9)
    ax.legend(fontsize=8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
out = "figures/ex12_distributions.png"
fig.savefig(out, dpi=150, bbox_inches="tight")
plt.close()
print(f"\nHistogram saved → {out}")

# ── Extra: viability scatter ──────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
sc = ax.scatter(df["mean_temp"], df["std_temp"],
                c=df["pct_above_18"], cmap="RdYlGn",
                s=4, alpha=0.5, rasterized=True)
fig.colorbar(sc, ax=ax, label="% area above 18 °C")
ax.set_xlabel("Mean temperature (°C)")
ax.set_ylabel("Temperature std dev (°C)")
ax.set_title("Mean vs Std Dev (colour = % above 18 °C)")
ax.grid(alpha=0.3)
plt.tight_layout()
out2 = "figures/ex12_mean_vs_std.png"
fig.savefig(out2, dpi=150, bbox_inches="tight")
plt.close()
print(f"Scatter saved    → {out2}")
