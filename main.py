import sim
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt

# Params
iter = 0
# Params

# Metrics
M_satisf = np.zeros((iter))
# Metrics

eff2price = lambda x:7-(7000-40*x)/1600
a, b = 1, 1
f = lambda x:a*x+b

for i in tqdm(range(iter)):
    M_satisf[i] = np.mean([sim.run(crousEff=f(i), crousPrice=eff2price(f(i)), showResults=False) for _ in range(7)])

X1 = f(np.arange(0, iter, 1))
X2 = eff2price(f(X1))
print(M_satisf)
print(X1)
print(X2)

M_satisf = [4.1643869,  4.2395051,  4.34872672, 4.42266389, 4.56803816, 4.58800654,
 4.70508411, 4.78719723, 4.90705102, 4.94910626, 4.93821393, 4.97099607,
 4.90697391, 4.91874851, 4.89920856, 4.8730871, 4.90698035, 4.86396334,
 4.85108083, 4.80991994]
X1 = np.arange(0, 20, 1)
X2 = [2.675, 2.7, 2.725, 2.75, 2.775, 2.8, 2.825, 2.85, 2.875, 2.9, 2.925, 2.95, 2.975, 3.,
      3.025, 3.05, 3.075, 3.1, 3.125, 3.15]

for i in range(int(len(X1)/2)):
    plt.text(X1[2*i], M_satisf[2*i], str(round(X2[2*i],1))+" €",
             horizontalalignment='center',
             verticalalignment='top')
plt.text(X1[np.argmax(M_satisf)],
        np.max(M_satisf),
        str(round(X2[np.argmax(M_satisf)],1))+" €",
        horizontalalignment='center',
        verticalalignment='bottom',weight='bold')

plt.plot(X1, M_satisf, c="red")
plt.show()