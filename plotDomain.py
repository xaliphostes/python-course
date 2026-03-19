from mylib import costStylos, costVeins, Remote, openFractureFile
import matplotlib.pyplot as plt
import numpy as np

# ------------------------------------------------------------
# 2D cost map: R (x-axis) vs theta (y-axis)

stylolites = openFractureFile('stylolites.csv')
veins      = openFractureFile('veins.csv')

bestTheta = 169.0
bestR     = 0.744
minCost   = 0.050

nR = 50
nTheta = 90
Rs = np.linspace(0, 1, nR)
thetas = np.linspace(0, 180, nTheta)
costMap = np.zeros((nTheta, nR))

print('Computing cost map...')

for i, theta in enumerate(thetas):
    for j, R in enumerate(Rs):
        remote = Remote(theta, R)
        costMap[i, j] = (costStylos(stylolites, remote) + costVeins(veins, remote)) / 2

plt.figure()
plt.imshow(costMap, extent=[0, 1, 0, 180], origin='lower', aspect='auto', cmap='viridis')
plt.colorbar(label='Cost')
plt.contour(Rs, thetas, costMap, levels=10, colors='white', linewidths=0.5)
plt.xlabel('R')
plt.ylabel('Theta (degrees)')
plt.title('Cost map (veins + stylolites)')
plt.plot(bestR, bestTheta, 'r*', markersize=15, label=f'Best ({bestTheta:.1f}°, R={bestR:.3f})')
plt.legend()
plt.tight_layout()
plt.show()
