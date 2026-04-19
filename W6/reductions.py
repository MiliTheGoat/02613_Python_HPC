import ctypes
import multiprocessing as mp
import sys
from time import perf_counter as time
import numpy as np
from PIL import Image


def init(shared_arr_):
    global shared_arr
    shared_arr = shared_arr_


def tonumpyarray(mp_arr):
    return np.frombuffer(mp_arr, dtype='float32')


def reduce_step(args):
    b, e, elemshape = args
    arr = tonumpyarray(shared_arr).reshape((-1,) + elemshape)
    # First reduction step: sum neighbors into every second element.
    for i in range(b, e, 2):
        arr[i] += arr[i + 1]


if __name__ == '__main__':
    n_processes = 1
    chunk = 2

    # Create shared array
    data = np.load(sys.argv[1])
    elemshape = data.shape[1:]
    shared_arr = mp.RawArray(ctypes.c_float, data.size)
    arr = tonumpyarray(shared_arr).reshape(data.shape)
    np.copyto(arr, data)
    del data

    # Run parallel sum
    t = time()
    pool = mp.Pool(n_processes, initializer=init, initargs=(shared_arr,))

    # First reduction step in parallel: (0+1), (2+3), ... in-place.
    if chunk < 2:
        chunk = 2
    if chunk % 2 != 0:
        chunk += 1

    n_pairs_region = len(arr) - (len(arr) % 2)
    tasks = [(i, min(i + chunk, n_pairs_region), elemshape)
             for i in range(0, n_pairs_region, chunk)]
    pool.map(reduce_step, tasks, chunksize=1)

    # Write output
    print(time() - t)
    final_image = arr[0]
    # final_image /= len(arr) # For mean
    Image.fromarray(
        (255 * final_image.astype(float)).astype('uint8')
    ).save('result.png')