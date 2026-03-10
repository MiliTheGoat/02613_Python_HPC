import sys, numpy as np
import time
path = sys.argv[1]
p = int(sys.argv[2])
A = np.load(path)
time1 = time.time()
power = p+1
mult_matrix = np.linalg.matrix_power(A, power)
time2 = time.time()
print(time2 - time1)
np.save("mult_matrix.npy", mult_matrix)