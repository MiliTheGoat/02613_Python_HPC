#If SIZE is 40, how many bytes does the row vector mat = np.random.rand(1, SIZE) occupy?
Size = 35
import numpy as np
mat = np.random.rand(Size, Size)
print(mat.nbytes)