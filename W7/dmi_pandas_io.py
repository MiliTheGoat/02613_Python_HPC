import argparse
import os
import subprocess
import tempfile
from time import perf_counter

import pandas as pd


def df_memsize(df: pd.DataFrame) -> int:
    """Return total DataFrame memory usage in bytes (including object columns)."""
    return int(df.memory_usage(index=True, deep=True).sum())


def reduce_dmi_df(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with lower-memory dtypes for common DMI columns."""
    out = df.copy()

    # Repeated ids are efficient as categorical values.
    for col in ("parameterId", "stationId"):
        if col in out.columns and out[col].dtype == "object":
            out[col] = out[col].astype("category")

    # Timestamps are compact and fast when stored as datetime64.
    for col in ("created", "observed"):
        if col in out.columns and out[col].dtype == "object":
            out[col] = pd.to_datetime(out[col], errors="coerce")

    # Downcast float columns used in DMI records.
    for col in ("coordsx", "coordsy", "value"):
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce", downcast="float")

    return out


def read_direct(zip_path: str) -> tuple[pd.DataFrame, float]:
    t0 = perf_counter()
    df = pd.read_csv(zip_path)
    elapsed = perf_counter() - t0
    return df, elapsed


def unzip_then_read(zip_path: str) -> tuple[pd.DataFrame, float]:
    with tempfile.TemporaryDirectory() as tmpdir:
        t0 = perf_counter()
        subprocess.run(
            ["unzip", "-qq", "-o", zip_path, "-d", tmpdir],
            check=True,
        )

        csv_files = [
            os.path.join(tmpdir, f)
            for f in os.listdir(tmpdir)
            if f.lower().endswith(".csv")
        ]
        if not csv_files:
            raise FileNotFoundError("No CSV file found after unzip")

        df = pd.read_csv(csv_files[0])
        elapsed = perf_counter() - t0
        return df, elapsed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--zip-path",
        default="/dtu/projects/02613_2025/data/dmi/2023_01.csv.zip",
        help="Path to 2023_01.csv.zip",
    )
    args = parser.parse_args()

    df_unzip, t_unzip = unzip_then_read(args.zip_path)
    mem_unzip = df_memsize(df_unzip)

    df_direct, t_direct = read_direct(args.zip_path)
    mem_direct = df_memsize(df_direct)
    df_reduced = reduce_dmi_df(df_direct)
    mem_reduced = df_memsize(df_reduced)

    print(f"rows: {len(df_direct)}")
    print(f"cols: {len(df_direct.columns)}")
    print(f"unzip_then_read_s: {t_unzip:.4f}")
    print(f"read_zip_direct_s: {t_direct:.4f}")
    print(f"mem_unzip_bytes: {mem_unzip}")
    print(f"mem_direct_bytes: {mem_direct}")
    print(f"mem_reduced_bytes: {mem_reduced}")

    faster = "unzip_then_read" if t_unzip < t_direct else "read_zip_direct"
    print(f"faster_method: {faster}")


if __name__ == "__main__":
    main()
