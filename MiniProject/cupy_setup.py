"""
cupy_setup.py – import this BEFORE importing cupy in any script.

Fixes the nvrtc 'invalid value for --gpu-architecture' error on DTU HPC by
locating the CUDA toolkit that was loaded via `module load cuda/11.8` and
setting CUDA_PATH/CUDA_HOME before CuPy's compiler is initialised.
"""
import os
import subprocess

def setup_cuda():
    # 1. Already set by our job script (CUDA_ROOT from the module system)
    if os.environ.get("CUDA_PATH"):
        return

    # 2. Try CUDA_ROOT (set by `module load cuda/11.8` on DTU HPC)
    cuda_root = os.environ.get("CUDA_ROOT", "")
    if cuda_root and os.path.isdir(cuda_root):
        os.environ["CUDA_PATH"] = cuda_root
        os.environ["CUDA_HOME"] = cuda_root
        return

    # 3. Find nvcc on PATH and derive the toolkit root from it
    try:
        nvcc = subprocess.check_output(["which", "nvcc"],
                                       stderr=subprocess.DEVNULL).decode().strip()
        # nvcc lives at <cuda_root>/bin/nvcc
        cuda_root = os.path.dirname(os.path.dirname(nvcc))
        if os.path.isdir(cuda_root):
            os.environ["CUDA_PATH"] = cuda_root
            os.environ["CUDA_HOME"] = cuda_root
            return
    except Exception:
        pass

    # 4. Hard-coded fallback for DTU HPC CUDA 11.8
    for path in ["/appl/cuda/11.8.0", "/usr/local/cuda-11.8", "/usr/local/cuda"]:
        if os.path.isdir(path):
            os.environ["CUDA_PATH"] = path
            os.environ["CUDA_HOME"] = path
            return

    print("WARNING: Could not locate CUDA toolkit; CuPy may fail to compile kernels.")

setup_cuda()
