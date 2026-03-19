import math
import numpy as np
import pandas as pd

# ------------------------------------------------

def deg2rad(a):
    """Convert degrees to radians."""
    return a/180*math.pi

# ------------------------------------------------

def dot(a: list, b: list):
    return a[0]*b[0] + a[1]*b[1]

# ------------------------------------------------

def openFractureFile(filename):
    """Open a csv file and read the strike column and return the unit normal vectors."""
    def between0_180(a):
        if a > 180:
            return a - 180
        else:
            return a
    
    df = pd.read_csv(filename, sep=';')
    strikes = df['strike'].apply(between0_180).apply(deg2rad).to_numpy()
    return np.column_stack([np.cos(strikes), -np.sin(strikes)])

# ------------------------------------------------

class Remote:
    theta: float
    R: float
    dirS1: list = None
    dirS3: list = None
    S1: float = None
    S3: float = None

    def __init__(self, theta: float, R: float): # constructor
        self.theta = theta
        self.R = R
        a = deg2rad(self.theta)
        c = math.cos(a)
        s = math.sin(a)
        self.dirS1 = [s, c]
        self.dirS3 = [c, -s]
        self.S1 = 1
        self.S3 = self.R

# ------------------------------------------------

def costVein(n: list, remote: Remote):
    return 1 - math.fabs(dot(n, remote.dirS3))

def costVeins(normals: list, remote: Remote):
    cost = 0
    for normal in normals:
        cost  = cost + costVein(normal, remote)
    return cost / len(normals)

# ------------------------------------------------

def costStylo(n: list, remote: Remote):
    return 1 - math.fabs(dot(n, remote.dirS1))

def costStylos(normals: list, remote: Remote):
    cost = 0
    for normal in normals:
        cost  = cost + costStylo(normal, remote)
    return cost / len(normals)
# ------------------------------------------------

