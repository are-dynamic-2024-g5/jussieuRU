import sim
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt

# Params
iter = 20
# Params

# Metrics
M_satisf = np.zeros((iter))
# Metrics

eff2price = lambda x:7-(7000-40*2*x)/1600
a, b = 1, 1
f = lambda x:a*x+b

for i in tqdm(range(iter)):
    M_satisf[i] = np.mean([sim.run(crousEff=f(i)*2, crousPrice=eff2price(f(i)), showResults=False) for _ in range(7)])

print(M_satisf)
X = f(np.arange(0, iter, 1))
print(X)
plt.plot(X, M_satisf)
plt.show()