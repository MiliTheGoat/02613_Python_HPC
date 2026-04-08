def standardize_rows(data, mean, std):
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            data[i,j] = (data[i,j] - mean[j]) / std[j]
    return data
#test
data = np.array([[1, 2, 3], [4, 5, 6]])
mean = np.array([0.5, 1, 3])
std = np.array([1, 2, 3])
standardized_data = standardize_rows(data, mean, std)
print(standardized_data)

def outer(v1, v2):
    resutlt = np.zeros((v1.shape[0], v2.shape[0]))
    for i in range(v1.shape[0]):
        for j in range(v2.shape[0]):
            resutlt[i,j] = v1[i] * v2[j]
    return resutlt

def distmat_1d(x,y):
    return abs(x[:, None] - y[None, :])