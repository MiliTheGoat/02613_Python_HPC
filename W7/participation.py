import pandas as pd
import sys
import zipfile
from time import perf_counter



def total_precip(pandasdf):
    total_precip = pandasdf.loc[pandasdf["parameterId"] == "precip_past10min", "value"].sum()
    return total_precip

def main():
    path = sys.argv[1]
    df1 = pd.read_csv(path)
    print(total_precip(df1))

if __name__ == "__main__":
    main()