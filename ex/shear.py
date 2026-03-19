import numpy as np
import matplotlib.pyplot as plt
import math

def deg2rad(d):
    """Convertit des degrés en radians."""
    return d * math.pi / 180

def shear(xx, xy, yy, theta):
    """Calcule la matrice de cisaillement pour les éléments xx, xy, yy et un angle theta."""
    theta_in_rad = 2*deg2rad(theta)
    return 1/2*(yy-xx)*math.sin(theta_in_rad) + xy * math.cos(theta_in_rad)

def normal(xx, xy, yy, theta):
    """Calcule la matrice de contrainte normale pour les éléments xx, xy, yy et un angle theta."""
    theta_in_rad = 2*deg2rad(theta)
    return 1/2*(xx+yy) + 1/2*(xx-yy)*math.cos(theta_in_rad) + xy*math.sin(theta_in_rad)

# -----------------------------------------------------

x = np.linspace(0,90,91)
y_shear = [shear(0, 0, 1, theta) for theta in x]
y_normal = [normal(0, 0, 1, theta) for theta in x]

fig, ax = plt.subplots()
ax.plot(x, y_shear, label='shear')
ax.plot(x, y_normal, label='normal')

ax.set_xlabel('Angle (°)')
ax.set_ylabel('Stress')
ax.legend()
plt.show()
