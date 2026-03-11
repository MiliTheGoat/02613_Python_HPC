import os
import sys
import blosc
import numpy as np
from time import perf_counter as time

def write_numpy(arr, file_name):
    np.save(f"{file_name}.npy", arr)
    os.sync()


def write_blosc(arr, file_name, cname="lz4"):
    b_arr = blosc.pack_array(arr, cname=cname)
    with open(f"{file_name}.bl", "wb") as w:
        w.write(b_arr)
    os.sync()


def read_numpy(file_name):
    return np.load(f"{file_name}.npy")


def read_blosc(file_name):
    with open(f"{file_name}.bl", "rb") as r:
        b_arr = r.read()
    return blosc.unpack_array(b_arr)


if __name__ == "__main__":
    n = int(sys.argv[1])
    zero_three_dim = np.zeros((n, n, n), dtype=np.uint8)
    time1 = time()
    write_numpy(zero_three_dim, "zero_three_dim")
    time1_1 = time() - time1
    print(time1_1)
    time2 = time()
    write_blosc(zero_three_dim, "zero_three_dim")
    time2_1 = time() - time2
    print(time2_1)
    time3 = time()
    read_numpy("zero_three_dim")
    time3_1 = time() - time3
    print(time3_1)
    time4 = time()
    read_blosc("zero_three_dim")
    time4_1 = time() - time4
    print(time4_1)