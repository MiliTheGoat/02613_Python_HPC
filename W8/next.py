import sys

import numpy as np
from PIL import Image


def save_downsampled_mandelbrot(array_path, size, step, output_path="mandelbrot.png"):
    if size < 1:
        raise ValueError("size must be at least 1")
    if step < 1:
        raise ValueError("step must be at least 1")

    mandelbrot = np.memmap(array_path, dtype=np.int32, mode="r", shape=(size, size))
    downsampled = mandelbrot[::step, ::step]

    # The Mandelbrot values are iteration counts, so they can be written directly as grayscale.
    image = Image.fromarray(downsampled.astype(np.uint8), mode="L")
    image.save(output_path)


def main():
    if len(sys.argv) != 4:
        raise SystemExit(
            "Usage: python next.py <mandelbrot_array> <size> <step>"
        )

    array_path = sys.argv[1]
    size = int(sys.argv[2])
    step = int(sys.argv[3])

    save_downsampled_mandelbrot(array_path, size, step)


if __name__ == "__main__":
    main()