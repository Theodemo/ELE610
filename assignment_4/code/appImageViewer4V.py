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
			QGraphicsPixmapItem, QInputDialog, QMessageBox)  # QColorDialog, 
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

		# Guardar una copia limpia de la imagen original sin modificar
		self.original_img = img.copy()

		# Convertir a escala de grises
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		# Aplicar un umbral para obtener una imagen binaria (blanco o negro)
		_, binary_img = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)  # Invertir blanco y negro

		# Detectar el círculo grande
		circles = cv2.HoughCircles(binary_img, cv2.HOUGH_GRADIENT, dp=1.2, minDist=100,
									param1=50, param2=30, minRadius=400, maxRadius=450)

		if circles is not None:
			circles = np.uint16(np.around(circles))
			for (x, y, r) in circles[0, :]:
				# Almacenar la información del centro y el radio
				self.disk_center = (x, y)
				self.inner_radius = int(r * 0.9)  # Radio del círculo interior

		# Convertir a RGB antes de mostrar en Qt
		img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		h, w, ch = img.shape
		bytesPerLine = ch * w
		qImg = QImage(img.data, w, h, bytesPerLine, QImage.Format_RGB888)
		self.pixmap = QPixmap.fromImage(qImg)
		self.curItem.setPixmap(self.pixmap)
		return


		
	def findRedSector(self):
		"""Find the red sector center in the disk and store it as self.sectorCenter1 (angle in degrees)."""
		# Asegurarse de que tenemos los datos de la función findDisk
		if hasattr(self, 'disk_center') and hasattr(self, 'inner_radius'):
			x, y = self.disk_center
			inner_radius = self.inner_radius

			# Usar la imagen original sin modificaciones (sin círculos dibujados)
			img = self.original_img.copy()

			# Convertir a escala de grises
			gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
			_, binary_img = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

			# Crear una máscara para la región circular
			mask = np.zeros_like(binary_img)
			cv2.circle(mask, (x, y), inner_radius, 255, -1)  # Crear una máscara con el círculo

			# Inicializar las variables para el primer y último punto blanco
			first_white_point = None
			last_white_point = None

			# Buscar puntos blancos dentro del círculo (y en la máscara)
			for angle in range(360):
				theta = np.radians(angle)
				x_p = int(x + inner_radius * np.cos(theta))
				y_p = int(y + inner_radius * np.sin(theta))

				if 0 <= x_p < img.shape[1] and 0 <= y_p < img.shape[0] and mask[y_p, x_p] == 255:
					if binary_img[y_p, x_p] == 255:  # blanco
						if first_white_point is None:
							first_white_point = (x_p, y_p)
						last_white_point = (x_p, y_p)

			# Calcular el ángulo medio entre el primer y el último punto blanco
			if first_white_point and last_white_point:
				# Calcular los ángulos en radianes para los dos puntos
				angle1 = np.arctan2(first_white_point[1] - y, first_white_point[0] - x)
				angle2 = np.arctan2(last_white_point[1] - y, last_white_point[0] - x)

				# Convertir los ángulos a grados
				angle1_deg = np.degrees(angle1) % 360
				angle2_deg = np.degrees(angle2) % 360

				# Calcular el ángulo medio
				mid_angle = (angle1_deg + angle2_deg) / 2

				# Asegurarse de que el ángulo está dentro del rango [0, 360)
				if mid_angle >= 360:
					mid_angle -= 360
				elif mid_angle < 0:
					mid_angle += 360

				# Almacenar el ángulo medio
				self.sectorCenter1 = mid_angle

				# Mostrar el ángulo medio como texto en la imagen (opcional)
				msg = QMessageBox()
				msg.setIcon(QMessageBox.Information)
				msg.setWindowTitle("Angle of the red sector")
				msg.setText(f"The angle of the red sector is: {self.sectorCenter1:.2f} degrees")
				msg.setInformativeText("This is the avarage angle of the red sector")
				msg.setStandardButtons(QMessageBox.Ok)
				msg.exec_()

			# Dibujar el punto medio en la imagen
			if first_white_point and last_white_point:
				mid_x = (first_white_point[0] + last_white_point[0]) // 2
				mid_y = (first_white_point[1] + last_white_point[1]) // 2
				cv2.circle(img, (mid_x, mid_y), 5, (0, 255, 255), -1)  # Punto medio en amarillo

			# Convertir a RGB antes de mostrar en Qt
			img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
			h, w, ch = img.shape
			bytesPerLine = ch * w
			qImg = QImage(img.data, w, h, bytesPerLine, QImage.Format_RGB888)
			self.pixmap = QPixmap.fromImage(qImg)
			self.curItem.setPixmap(self.pixmap)





		
	def findSpeed(self):
		"""Find speed for disk using ??."""
		print("This function is not ready yet.")
		print("Different approaches may be used, here we sketch one alternative that may (or may not) work.")
		
		self.findDisk()
		self.findRedSector()
		if not hasattr(self, 'sectorCenter1'):
			print('Can not calculate the angle of the first image')
			return

		angle1 = self.sectorCenter1
		print(f"Angle of the first image: {angle1:.2f} degrees")
  
		file_name, _ = QFileDialog.getOpenFileName(self, "Open second image", "", "Image Files (*.png *.jpg *.bmp)")
		if not file_name:
			print("No image selected")
			return

		self.openFile(file_name)
		self.findDisk()
		self.findRedSector()
		if not hasattr(self, 'sectorCenter1'):
			print('Can not calculate the angle of the second image')
			return

		angle2 = self.sectorCenter1
		print(f"Angle of the second image: {angle2:.2f} degrees")
  
		angle_diff = abs(angle2 - angle1)
		if angle_diff > 180:
			angle_diff = 360 - angle_diff
  
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Information)
		msg.setWindowTitle("Angle difference")
		msg.setText(f"The difference between the angle of both images is: {angle_diff:.2f} degrees")
		msg.setStandardButtons(QMessageBox.Ok)
		msg.exec()
  
		time_diff, ok = QInputDialog.getDouble(self, "Time difference", "Enter the time difference between the two images (in seconds):", min=0.0)
		if not ok:
			print("No time difference provided")
			return

		angular_speed = angle_diff / time_diff
		print(f"Angular speed: {angular_speed:.2f} degrees per second")

		msg = QMessageBox()
		msg.setIcon(QMessageBox.Information)
		msg.setWindowTitle("Angular speed")
		msg.setText(f"The angular speed of the disk is: {angular_speed:.2f} degrees per second")
		msg.setStandardButtons(QMessageBox.Ok)
		msg.exec()

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
	