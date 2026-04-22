import argparse
import os
import tempfile
from pathlib import Path
from statistics import mean
from time import perf_counter
import sys
import pandas as pd


def load_save_pq(location_file):
    df = pd.read_csv(location_file)
    pq_path = location_file.replace(".csv", ".parquet")
    df.to_parquet(pq_path)
    return 0

def main():
    path = str(sys.argv[1])
    time1 = perf_counter()
    load_save_pq(path)
    time1_1 = perf_counter() - time1
    print(time1_1)

if __name__ == "__main__":
    main()