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

    # Run parallel reduction
    t = time()
    if chunk < 2:
        chunk = 2
    if chunk % 2 != 0:
        chunk += 1

    n_images = len(arr)
    active = n_images

    with mp.Pool(n_processes, initializer=init, initargs=(shared_arr,)) as pool:
        while active > 1:
            pair_region = active - (active % 2)
            tasks = [(i, min(i + chunk, pair_region), elemshape)
                     for i in range(0, pair_region, chunk)]

            # One reduction level per pool.map call.
            if tasks:
                pool.map(reduce_step, tasks, chunksize=1)

            n_pairs = pair_region // 2

            # Compact partial sums to the front for the next level.
            if n_pairs > 0:
                arr[:n_pairs] = arr[0:pair_region:2]

            if active % 2 == 1:
                arr[n_pairs] = arr[active - 1]

            active = n_pairs + (active % 2)

    # Write output
    print(time() - t)
    final_image = arr[0] / n_images
    Image.fromarray(
        (255 * final_image.astype(float)).astype('uint8')
    ).save('result.png')