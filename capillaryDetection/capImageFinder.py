import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, least_squares
from sklearn.cluster import k_means

def filter(array:np.ndarray, min=10):
    array2 = cv2.cvtColor(array, cv2.COLOR_BGR2GRAY)
    return np.where(array2 < min, 0, 255).astype(np.uint8)

def getcapedge(array:np.ndarray,min=10):
    a = filter(array, min=min)
    lap = cv2.Laplacian(a, cv2.CV_64F)
    lapa = cv2.convertScaleAbs(lap)
    return lapa

def linear(x, m, c):
    return m*x + c

def fitcapillary(array:np.ndarray,min=10):
    a = filter(array,min)
    popt,pcov = least_squares(linear,a[1],a[0])
    return popt

def getedgeequation(lapimage):
    scatter = np.where(lapimage > 0)
    x = scatter[0]
    y = scatter[1]

def doublelinear_opt(x,y, m1, m2, c1,c2):
    yfit1 = linear(x,m1,c1)
    yfit2 = linear(x,m2,c2)
    yfitall = np.append(yfit1,yfit2)

def cluster(x,y, ngroups=3):
    return k_means(np.array([x,y]).transpose(), n_clusters=ngroups)




