import pandas as pd
import sys
import zipfile
from time import perf_counter



def total_precip(pandasdf, chunk_size):
    total_precip = 0
    chunked = pd.read_csv(pandasdf, chunksize = chunk_size)
    for chunk in chunked:
        total_precip += chunk.loc[chunk["parameterId"] == "precip_past10min", "value"].sum()
    return total_precip

def unzip_file(zipped_file, csv_path):
    with zipfile.ZipFile(zipped_file, 'r') as zip_ref:
        zip_ref.extract(csv_path)

def main():
    path = sys.argv[1]
    chunk_size = int(sys.argv[2])
    csv_path = "2023_01.csv"
    unzip_file(path, csv_path)

    print(total_precip(csv_path, chunk_size))

if __name__ == "__main__":
    main()