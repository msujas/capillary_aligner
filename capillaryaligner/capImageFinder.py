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


def centerimages(i1:np.ndarray,i2:np.ndarray, xcenter:int, motorpos:float,calibration,  minpixel=10):
    popt1 = fitcapillary(i1, min=minpixel)
    popt2 = fitcapillary(i2, min=minpixel)

    y1 = linear(xcenter, popt1[0],popt1[1])
    y2 = linear(xcenter,popt2[0], popt2[1])
    ycenter = (y1+y2)/2
    ymove = ycenter - y1
    motormove = ymove * calibration
    return motormove + motorpos
