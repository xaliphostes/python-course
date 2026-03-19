from mylib import costVeins, costStylos, Remote, openFractureFile
import numpy as np

def monteCarlo(nIter, veins, stylolites):
    bestCost = 1e32
    bestTheta = 0
    bestR = 0

    for i in range(0, nIter):
        theta  = np.random.uniform(0.0, 180.0)
        R      = np.random.uniform(0.0, 1.0)
        remote = Remote(theta, R)
        costS  = costStylos(stylolites, remote)
        costV  = costVeins(veins, remote)
        cost   = ( costV + costS) / 2

        if cost < bestCost :
            bestCost  = cost
            bestTheta = theta
            bestR     = R

    return bestCost, bestTheta, bestR

veins      = openFractureFile("veins.csv")
stylolites = openFractureFile("stylolites.csv")

cost, theta, R = monteCarlo(10000, veins, stylolites)
print(f'Best cost : {cost:.2f}')
print(f'Best fit  : {(1-cost)*100:.0f}%')
print(f'Best theta: {theta:.0f}°')
print(f'Best R    : {R:.2f}')
