import sys
import numpy as np
from numpy.lib.format import open_memmap

def mandelbrot_escape_time(c):
    z = 0j
    for i in range(100):
        z = z**2 + c
        if abs(z) > 2.0:
            return i
    return 100

def generate_mandelbrot_set(size, output_path="mandelbrot.npy"):
    if size < 1:
        raise ValueError("size must be at least 1")

    xmin, xmax = -2.0, 2.0
    ymin, ymax = -2.0, 2.0
    max_iter = 100

    x_values = np.linspace(xmin, xmax, size)
    y_values = np.linspace(ymin, ymax, size)

    escape_times = open_memmap(
        output_path,    
        mode="w+",
        dtype=np.uint16,
        shape=(size, size),
    )

    for row_index, y_value in enumerate(y_values):
        c = x_values + 1j * y_value
        z = np.zeros_like(c, dtype=np.complex128)
        row = np.zeros(size, dtype=np.uint16)
        active = np.ones(size, dtype=bool)

        for iteration in range(max_iter):
            z[active] = z[active] ** 2 + c[active]
            escaped = np.abs(z) > 2.0
            newly_escaped = active & escaped
            row[newly_escaped] = iteration
            active &= ~escaped
            if not active.any():
                break

        row[active] = max_iter
        escape_times[row_index] = row

    escape_times.flush()
    return escape_times

if __name__ == "__main__":
    size = int(sys.argv[1])
    mandelbrot_set = generate_mandelbrot_set(size)
    print(f"Saved Mandelbrot array with shape {mandelbrot_set.shape} to mandelbrot.npy")
