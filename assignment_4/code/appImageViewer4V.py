#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ../ELE610/py3/appImageViewer4.py    (disk)
#
#  Extends appImageViewer2 by adding some more functionality using heritage.
#  Some (skeleton) methods for locating disc in image and finding the
#  angle for rotation to estimate disk speed.
#  Disk menu has actions for: locating disc, finding read sector and its angle, ...
#
# Karl Skretting, UiS, November 2020, June 2022

# Example on how to use file:
# (C:\...\Anaconda3) C:\..\py3> activate py38
# (py38) C:\..\py3> python appImageViewer4.py
# (py38) C:\..\py3> python appImageViewer4.py DarkCrop10ms.bmp

_appFileName = "appImageViewer4"
_author = "Karl Skretting, UiS" 
_version = "2022.06.27"

import sys
import os.path
#from math import hypot, pi, atan2, cos, sin    # sqrt, cos, sin, tan, log, ceil, floor 
import numpy as np
import cv2

try:
	from PyQt5.QtCore import Qt, QPoint, QT_VERSION_STR  
	from PyQt5.QtGui import QImage, QPixmap, QTransform, QColor
	from PyQt5.QtWidgets import (QApplication, QAction, QFileDialog, QLabel, 
			QGraphicsPixmapItem, QInputDialog)  # QColorDialog, 
except ImportError:
	raise ImportError( f"{_appFileName}: Requires PyQt5." )
#end try, import PyQt5 classes 

from appImageViewer2 import myPath, MainWindow as inheritedMainWindow 

class MainWindow(inheritedMainWindow):  
	"""MainWindow class for this image viewer is inherited from another image viewer."""
	
# Two initialization methods used when an object is created
	def __init__(self, fName="", parent=None):
		# print( f"File {_appFileName}: (debug) first line in __init__()" ) 
		super().__init__(fName, parent)# use inherited __init__ with extension as follows
		#
		# set appFileName as it should be, it is set wrong in super()...
		self.appFileName = _appFileName 
		if (not self.pixmap.isNull()): 
			self.setWindowTitle( f"{self.appFileName} : {fName}" ) 
		else:
			self.setWindowTitle(self.appFileName)
		# 
		# self.view.rubberBandRectGiven.connect(self.methodUsingRubberbandEnd)  
		# # signal is already connected to cropEnd (appImageViewer1), and can be connected to more
		# self.methodUsingRubberbandActive = False    # using this to check if rubber band is to be used here
		#
		self.initMenu4()
		self.setMenuItems4()
		# print( f"File {_appFileName}: (debug) last line in __init__()" )
		return
	#end function __init__
	
	def initMenu4(self):
		"""Initialize Disk menu."""
		# print( f"File {_appFileName}: (debug) first line in initMenu4()" )
		a = self.qaFindDisk = QAction('Find disk', self)
		a.triggered.connect(self.findDisk)
		a.setToolTip("Find disk using cv2.HoughCircles (TODO)")
		a = self.qaFindRedSector = QAction('Find red sector', self)
		a.triggered.connect(self.findRedSector)
		a.setToolTip("Find angle for red sector center (TODO)")
		a = self.qaFindSpeed = QAction('Find speed', self)
		a.triggered.connect(self.findSpeed)
		a.setToolTip("Find speed for rotating disk (TODO)")
		#
		diskMenu = self.mainMenu.addMenu("Disk")
		diskMenu.addAction(self.qaFindDisk)
		diskMenu.addAction(self.qaFindRedSector)
		diskMenu.addAction(self.qaFindSpeed)
		diskMenu.setToolTipsVisible(True)
		return
	#end function initMenu4
	
# Some methods that may be used by several of the menu actions
	def setMenuItems4(self):
		"""Enable/disable menu items as appropriate."""
		pixmapOK = ((not self.pixmap.isNull()) and isinstance(self.curItem, QGraphicsPixmapItem))
		#
		#self.qaFindDisk.setEnabled(pixmapOK)   
		#self.qaFindDisk.setEnabled(pixmapOK)   
		#self.qaFindDisk.setEnabled(pixmapOK)
		return
		
# Methods for actions on the Disk-menu
	def findDisk(self):
		"""Find the large disk in the center of the image."""
		image = self.pixmap.toImage()
		width, height = image.width(), image.height()
		ptr = image.bits()
		ptr.setsize(height * width * 4)
		img = np.array(ptr, dtype=np.uint8).reshape((height, width, 4))
		img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

		# Convertir a escala de grises
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		# Aplicar un umbral para obtener una imagen binaria (blanco o negro)
		_, binary_img = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)  # Invertir blanco y negro

		# Mostrar la imagen binaria para verificar la detección
		cv2.imshow('Binary Image', binary_img)  # Mostrar la imagen binaria
		cv2.waitKey(0)  # Esperar hasta que se cierre la ventana
		cv2.destroyAllWindows()

		# Detectar el círculo grande
		circles = cv2.HoughCircles(binary_img, cv2.HOUGH_GRADIENT, dp=1.2, minDist=100,
									param1=50, param2=30, minRadius=400, maxRadius=450)

		if circles is not None:
			circles = np.uint16(np.around(circles))
			for (x, y, r) in circles[0, :]:
				cv2.circle(img, (x, y), r, (0, 255, 0), 2)  # Círculo grande en verde
				cv2.circle(img, (x, y), 2, (255, 0, 0), 3)  # Centro en azul

				# Radio del círculo interno
				inner_radius = int(r * 0.9)
				cv2.circle(img, (x, y), inner_radius, (255, 0, 0), 2)  # Círculo interno en rojo

				# Crear una máscara para la región circular donde buscaremos los puntos
				mask = np.zeros_like(binary_img)
				cv2.circle(mask, (x, y), inner_radius, 255, -1)  # Círculo blanco en la máscara

				# Inicializar las variables para el primer y último punto blanco
				first_white_point = None
				last_white_point = None
				first_angle = None
				last_angle = None

				# Buscar puntos blancos dentro del círculo pequeño
				for angle in range(360):
					theta = np.radians(angle)
					x_p = int(x + inner_radius * np.cos(theta))
					y_p = int(y + inner_radius * np.sin(theta))

					# Verificar que el punto está dentro de la imagen y dentro de la máscara
					if 0 <= x_p < width and 0 <= y_p < height and mask[y_p, x_p] == 255:
						# Si el píxel es blanco (en la imagen binaria)
						if binary_img[y_p, x_p] == 255:  # 255 significa blanco en la imagen binaria
							# Guardar el primer y último punto blanco encontrado
							if first_white_point is None:
								first_white_point = (x_p, y_p)
								first_angle = angle
							last_white_point = (x_p, y_p)
							last_angle = angle

				# Ahora que tenemos el primer y el último punto blanco, calculamos el ángulo medio
				if first_white_point is not None and last_white_point is not None:
					# Calcular el ángulo medio entre el primer y el último punto
					middle_angle = (first_angle + last_angle) / 2
					# Asegurarse de que el ángulo esté entre 0 y 360 grados
					if middle_angle >= 360:
						middle_angle -= 360

					# Calcular las coordenadas del punto medio
					middle_x = int(x + inner_radius * np.cos(np.radians(middle_angle)))
					middle_y = int(y + inner_radius * np.sin(np.radians(middle_angle)))

					# Marcar el punto medio con un círculo rojo
					cv2.circle(img, (middle_x, middle_y), 5, (0, 0, 255), -1)  # Rojo para el punto medio

		# Convertir a RGB antes de mostrar en Qt
		img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		h, w, ch = img.shape
		bytesPerLine = ch * w
		qImg = QImage(img.data, w, h, bytesPerLine, QImage.Format_RGB888)
		self.pixmap = QPixmap.fromImage(qImg)
		self.curItem.setPixmap(self.pixmap)
		return







		
	def findRedSector(self):
		"""Find red sector for disc in active image using ??."""
		print("This function is not ready yet.")
		print("Different approaches may be used, here we sketch one alternative that may (or may not) work.")
		#
		# -- your code may be written in between the comment lines below --
		# Check color for pixels in a given distance from center [0.75, 0.95]*radius and for all angles [0,1,2, 359]
		# and give 'score' based on how red the pixel is, red > threshold and red > blue and red > green ??
		# (score may be adjusted by position, based on illumination of disk)
		# Find the weighted (based on score) mean position (x,y) for all checked pixels
		# Find, and print perhaps also show on image, the angle of this mean
		return
		
	def findSpeed(self):
		"""Find speed for disk using ??."""
		print("This function is not ready yet.")
		print("Different approaches may be used, here we sketch one alternative that may (or may not) work.")
		#
		# -- your code may be written here --
		#
		return
		
#end class MainWindow

if __name__ == '__main__':
	print( f"{_appFileName}: (version {_version}), path for images is: {myPath}" )
	print( f"{_appFileName}: Using Qt {QT_VERSION_STR}" )
	mainApp = QApplication(sys.argv)
	if (len(sys.argv) >= 2):
		fn = sys.argv[1]
		if not os.path.isfile(fn):
			fn = myPath + os.path.sep + fn   # alternative location
		if os.path.isfile(fn):
			mainWin = MainWindow(fName=fn)
		else:
			mainWin = MainWindow()
	else:
		mainWin = MainWindow()
	mainWin.show()
	sys.exit(mainApp.exec_())
	