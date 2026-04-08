def standardize_rows(data, mean, std):
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            data[i,j] = (data[i,j] - mean[j]) / std[j]
    return data
#test

def outer(v1, v2):
    resutlt = np.zeros((v1.shape[0], v2.shape[0]))
    for i in range(v1.shape[0]):
        for j in range(v2.shape[0]):
            resutlt[i,j] = v1[i] * v2[j]
    return resutlt

def distmat_1d(x,y):
    return abs(x[:, None] - y[None, :])

f = 100/120
t_1 = 20/120

t_p = (1-f)*t_1 + (f/10)*t_1

t_p = 1/((1-f)+(f/10))
print(t_p)