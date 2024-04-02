import sim
import numpy as np
from tqdm import tqdm

# Params
iter = 5
# Params

# Metrics
M_satisf = np.zeros((iter))
# Metrics

for i in tqdm(range(iter)):
    M_satisf[i] = sim.run()

print(M_satisf)