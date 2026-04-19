import multiprocessing
import numpy as np
import matplotlib.pyplot as plt

def mandelbrot_escape_time(c):
    z = 0
    for i in range(100):
        z = z**2 + c
        if np.abs(z) > 2.0:
            return i
    return 100
def compute_escape_times_chunk(chunk):
    return np.array([mandelbrot_escape_time(c) for c in chunk], dtype=np.int32)

def generate_mandelbrot_set(points, num_processes):
    if num_processes < 1:
        raise ValueError("num_processes must be at least 1")

    total_points = len(points)
    if total_points == 0:
        return np.array([], dtype=np.int32)

    # Split points as evenly as possible across workers.
    base_chunk = total_points // num_processes
    remainder = total_points % num_processes

    chunks = []
    start = 0
    for i in range(num_processes):
        end = start + base_chunk + (1 if i < remainder else 0)
        if start < end:
            chunks.append(points[start:end])
        start = end

    with multiprocessing.Pool(processes=num_processes) as pool:
        chunk_results = pool.map(compute_escape_times_chunk, chunks)

    escape_times = np.concatenate(chunk_results)
    return escape_times


def generate_mandelbrot_set_chunks(points, num_processes, chunk_size=1000):
    if num_processes < 1:
        raise ValueError("num_processes must be at least 1")
    if chunk_size < 1:
        raise ValueError("chunk_size must be at least 1")

    total_points = len(points)
    if total_points == 0:
        return np.array([], dtype=np.int32)

    # Ensure more chunks than workers whenever it is possible.
    if total_points > num_processes:
        max_chunk_for_extra_work = max(1, total_points // (num_processes + 1))
        chunk_size = min(chunk_size, max_chunk_for_extra_work)

    chunks = [points[i:i + chunk_size] for i in range(0, total_points, chunk_size)]

    with multiprocessing.Pool(processes=num_processes) as pool:
        results_async = [pool.apply_async(compute_escape_times_chunk, (chunk,)) for chunk in chunks]
        chunk_results = [result.get() for result in results_async]

    return np.concatenate(chunk_results)

    
def plot_mandelbrot(escape_times):
    plt.imshow(escape_times, cmap='hot', extent=(-2, 2, -2, 2))
    plt.axis('off')
    plt.savefig('figures/mandelbrot.png', bbox_inches='tight', pad_inches=0)

if __name__ == "__main__":
    width = 800
    height = 800
    xmin, xmax = -2, 2
    ymin, ymax = -2, 2
    num_proc = 4

    # Precompute points
    x_values = np.linspace(xmin, xmax, width)
    y_values = np.linspace(ymin, ymax, height)
    points = np.array([complex(x, y) for x in x_values for y in y_values])

    # Compute set
    mandelbrot_set = generate_mandelbrot_set(points, num_proc)

    # Save set as image
    mandelbrot_set = mandelbrot_set.reshape((height, width))
    plot_mandelbrot(mandelbrot_set)