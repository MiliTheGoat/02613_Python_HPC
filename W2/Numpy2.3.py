import sys, numpy as np
p = []
for i in range(len(sys.argv)-1):
    p.append(float(sys.argv[i+1]))
diag_ele = np.array(p)
diag_matrix = np.diag(diag_ele)
np.save("diag_matrix.npy", diag_matrix)