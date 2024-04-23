import sim
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt

# Params
iter = 0#25
# Params

# Metrics
M_satisf = np.zeros((iter))
# Metrics

eff2price = lambda x:7-(7000-61*x)/1600
a, b = 1, 1
f = lambda x:a*x+b

for i in tqdm(range(iter)):
    M_satisf[i] = np.mean([sim.run(crousEff=f(i), crousPrice=eff2price(f(i)), showResults=False) for _ in range(7)])

X1 = f(np.arange(0, iter, 1))
X2 = eff2price(f(X1))
print(list(M_satisf))
print(list(X1))
print(list(X2))

M_satisf = [4.173083578167331, 4.224190040946287, 4.334373850479056, 4.436843111442558, 4.506991826980399, 4.595320149723729, 4.616670556085177, 4.747105179800772, 4.8181400679060635, 4.839298878207309, 4.851198491014993, 4.834856602223697, 4.830968298507701, 4.772611827021055, 4.73450438849549, 4.728476013256147, 4.727419278479155, 4.6407770814696905, 4.635235235996836, 4.623238536556442, 4.531071257722313, 4.505684213521732, 4.518628647575626, 4.430469823470132, 4.443127502934151]

X1 = np.arange(0, 25, 1)
X2 = [2.70125, 2.739375, 2.7775, 2.815625, 2.85375, 2.8918749999999998, 2.9299999999999997, 2.9681249999999997, 3.00625, 3.044375, 3.0825, 3.120625, 3.15875, 3.196875, 3.235, 3.273125, 3.31125, 3.349375, 3.3875, 3.425625, 3.46375, 3.501875, 3.54, 3.578125, 3.61625]

for i in range(int(len(X1)/2)):
    plt.text(X1[2*i+1], M_satisf[2*i+1], str(round(X2[2*i+1],1))+" €",
             horizontalalignment='center',
             verticalalignment='top')
plt.text(X1[np.argmax(M_satisf)],
        np.max(M_satisf),
        str(round(X2[np.argmax(M_satisf)],1))+" €",
        horizontalalignment='center',
        verticalalignment='bottom',weight='bold')

plt.plot(X1, M_satisf, c="red")
plt.show()