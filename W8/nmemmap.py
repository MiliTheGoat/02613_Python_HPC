import sys
import numpy as np

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

    # Use raw memmap (not .npy format) so the file contains only int32 data.
    escape_times = np.memmap(
        output_path,    
        mode="w+",
        dtype=np.int32,
        shape=(size, size),
    )

    # Keep axis order consistent with earlier weeks: first axis follows x-values.
    for row_index, x_value in enumerate(x_values):
        c = x_value + 1j * y_values
        z = np.zeros_like(c, dtype=np.complex128)
        row = np.zeros(size, dtype=np.int32)
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
