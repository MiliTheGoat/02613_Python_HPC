import numpy as np
import matplotlib.pyplot as plt
import time

SIZE = 100

mat = np.random.rand(SIZE, SIZE)


times_1000 = []
for i in range(1000):
    start_time = time.time()
    double_column = 2 * mat[:, 0]
    double_row = 2 * mat[0, :]
    end_time = time.time()
    times_1000.append(end_time - start_time)

plt.hist(times_1000, bins=30, edgecolor='black')
plt.title('Time taken for 1000 iterations')
plt.xlabel('Time (seconds)')
plt.ylabel('Frequency')
plt.savefig('figures/histogram.png')