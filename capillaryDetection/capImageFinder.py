import cv2
import numpy as np
import matplotlib.pyplot as plt

file = 'C:/users/kenneth1a/Pictures/capillary.png'
array = cv2.imread(file)
arrayGS = cv2.cvtColor(array, cv2.COLOR_BGR2GRAY)
sobelx = cv2.Sobel(arrayGS,cv2.CV_64F, 1, 0,ksize = 3)
sobely = cv2.Sobel(arrayGS, cv2.CV_64F, 0, 1, ksize=3)

magnitude = cv2.magnitude(sobelx,sobely)
print(magnitude)
plt.imshow(sobelx)
plt.show()
plt.imshow(sobely)
plt.show()
plt.imshow(magnitude)
plt.colorbar()
plt.show()

lap = cv2.Laplacian(arrayGS, cv2.CV_64F)
lapabs = cv2.convertScaleAbs(lap)

cv2.imshow('laplace', lapabs)
cv2.waitKey(0)
cv2.destroyAllWindows()

def filter(array, min):
    array2 = cv2.cvtColor(array, cv2.COLOR_BGR2GRAY)
    return np.where(array2 < min, 0, 255).astype(np.uint8)

arrayF = filter(array,10)

cv2.imshow('filter',arrayF)
cv2.waitKey(0)
cv2.destroyAllWindows()

lap2 = cv2.Laplacian(arrayF, cv2.CV_64F)
lapa2 = cv2.convertScaleAbs(lap2)

cv2.imshow('lap2',lapa2)
cv2.waitKey(0)
cv2.destroyAllWindows()