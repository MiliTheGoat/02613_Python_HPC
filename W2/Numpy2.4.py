import sys, numpy as np
path = sys.argv[1]
matrix = np.load(path)
col_means = np.mean(matrix, axis=0)
row_means = np.mean(matrix, axis=1)
np.save("cols.npy", col_means)
np.save("rows.npy", row_means)