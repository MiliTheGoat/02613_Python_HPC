import sys
import numpy as np
p = []
for i in range(len(sys.argv)-1):
    p.append(float(sys.argv[i+1]))
par = np.array(p)
magnitude = np.linalg.norm(par)
print(magnitude)