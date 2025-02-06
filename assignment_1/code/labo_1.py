import cv2
import numpy as np
import matplotlib.pyplot as plt
from bf_tools import mpl_plot, cv_plot



#A = np.zeros((300,400),dtype=np.uint8)
#A = cv2.line(A, (10,10), (10,50), 255)
#A = cv2.rectangle(A, (20,10), (50,60), 255, thickness=-1)
#A = cv2.ellipse(A, (120,50), (40,40), angle=360, \
#startAngle=0, endAngle=360, color=255, thickness=2)
#mpl_plot(A, "Black image with some white shapes")


#(cx,cy,r) = (100,200,40)
#yRange = np.arange( np.floor(cy-r-1.0), np.ceil(cy+r+1.0001), 1.0)
#xRange = np.arange( np.floor(cx-r-1.0), np.ceil(cx+r+1.0001), 1.0)
#yD2 = np.power(abs(yRange + 0.5 - cy), 2)
#xD2 = np.power(abs(xRange + 0.5 - cx), 2)
#xyD = np.sqrt(np.dot(yD2.reshape(len(yD2),1), np.ones((1,len(xD2)))) +
#np.dot(np.ones((len(yD2),1)), xD2.reshape(1,len(xD2))))
#
#for y in range(len(yD2)):
#    for x in range(len(xD2)):
#        b = xyD[y,x]
#        if (b < (r-0.7)):
#            xyD[y,x] = 255
#        elif (b > (r+0.7)):
#            xyD[y,x] = 0
#        else: # r-0.7 < b < r+0.7, 0 < r+0.7-b < 1.4
#            xyD[y,x] = int(np.floor(182.1*(r+0.7-b)))
#
#A[int(yRange[0]):int(yRange[-1]+1),int(xRange[0]):int(xRange[-1]+1)] = xyD
#mpl_plot(A, "Gray scale image with some more shapes")


#Make a circle in upper left quadrant of the image A, center at x=140 and y=90 and radius=40.
#A = np.zeros((300,400),dtype=np.uint8)
#A= cv2.circle(A, (140,90),40, 255,thickness = -1)



#Add a filled white rectangle where upper corner is in (x,y) = (250,50) 
# and size is (w,h) = (100,50), i.e. in upper right quadrant of the image.

#A= cv2.rectangle(A, (250,50),(350,100), 255,thickness = -1)


#Add a line from (100,200) to (200,250), i.e. in lower left quadrant of the image.

#A = cv2.line(A, (100,200), (200,250), 255, thickness = 2)

#Add a (filled) triangle with corners at points (x,y): (250,250), (350,250)
#and (300,163.4), i.e in lower right quadrant of image. You don’t need to
#do “anti-aliasing” as in the numpy circle example. But, if you want some
#extra challenges, you may do this too.

#pts = np.array([[250,250],[350,250],[300,163.4]], np.int32) # triangle points
#pts = pts.reshape((-1,1,2)) # reshape to 3x1x2

#np.set_printoptions(threshold=np.inf)
#A = cv2.polylines(A,[pts],isClosed = True, color = 255, thickness = 2) # draw the triangle
#A = cv2.fillPoly(A,[pts],color = 255) # fill the triangle
#mpl_plot(A, "")



#img = cv2.imread('chessboard.jpg')
#
#height, width = img.shape[:2]
#
#startX = (height) // 3
#stratY = (width) // 3
#
#
#endX = height - startX
#endY = width - stratY
#
#
#cropped_img = img[startX:endX, stratY:endY]
#
#cv2.imwrite("cropped_chessboard.jpg", cropped_img)
#
#cv2.imshow("Cropped Image", cropped_img)
#cv2.waitKey(0)
#cv2.destroyAllWindows()

img = cv2.imread('cropped_chessboard.jpg')

