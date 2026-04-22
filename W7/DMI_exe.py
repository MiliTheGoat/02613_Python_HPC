import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from time import perf_counter
import zipfile
from pyarrow import csv

FOLDER = "/dtu/projects/02613_2025/data/dmi/2023_01.csv.zip"

def df_memsize(df: pd.DataFrame) -> int:
    return int(df.memory_usage(index=True, deep=True).sum())

def unzip_then_read(zip_path: str, csv_path: str) -> pd.DataFrame:
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extract(csv_path)
    return pd.read_csv(csv_path)

def reduce_dmi_df(df):
    out = df.copy()
    for col in ("parameterId", "stationId"):
        if col in out.columns and out[col].dtype == "object":
            out[col] = out[col].astype("category")
    for col in ("created", "observed"):
        if col in out.columns and out[col].dtype == "object":
            out[col] = pd.to_datetime(out[col], errors="coerce")

    return out

def pyarrow_read(path):
    pyarrow_table = csv.read_csv(path)
    return pyarrow_table

def pyarrow_to_pandas(path):
    pyarrow_table = csv.read_csv(path)
    pyarrow_df = pyarrow_table.to_pandas()
    return pyarrow_df

def unzip(path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extract(csv_path)
    return csv_path

def main():
    time_start = perf_counter()
    df = pd.read_csv(FOLDER)
    time_end = perf_counter()
    elapsed = time_end - time_start
    mem_size = df_memsize(df)
    print(f"Elapsed time for ziped and reading with Pandas: {elapsed:.4f} seconds")
    print(f"Memory size: {mem_size} bytes")

    #time_start = perf_counter()
    #df_unzip = unzip_then_read(FOLDER, "2023_01.csv")
    #time_end = perf_counter()
    #elapsed_unzip = time_end - time_start
    #print(f"Elapsed time (unzip then read): {elapsed_unzip:.4f} seconds")

    df_reduced = reduce_dmi_df(df)
    mem_size_reduced = df_memsize(df_reduced)
    print(f"Memory size after reduction: {mem_size_reduced} bytes")
    
    csv_path = "2023_01.csv"

    t1 = perf_counter()
    table = pyarrow_read(csv_path)
    t2 = perf_counter()
    tarr = t2-t1
    print(f"Time to get to arrow table: {tarr} seconds ")
    t3 = perf_counter()
    df_arrow = pyarrow_to_pandas(csv_path)
    t4 = perf_counter()
    tarr_df = t4-t3
    print(f"Time to convert arrow table to pandas DataFrame: {tarr_df} seconds")


if __name__ == "__main__":
    main()