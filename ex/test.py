import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0,10,100)

def generate(power):
    return x**power

fig, ax = plt.subplots()

for power in [0, 1, 1.5, 2]:
    ax.plot(x, generate(power), label=f'power {power}')

ax.legend()
fig.tight_layout()
plt.show()
