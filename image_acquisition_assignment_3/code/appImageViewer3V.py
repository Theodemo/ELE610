#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# ../ELE610/py3/appImageViewer2.py
#
#  Extends appImageViewer1 by adding some more functionality using heritage.
#  Now program can capture an image from an IDS camera attached to the USB 
#  gate of the computer. This program also requires IDS pyueye package,
#  https://pypi.org/project/pyueye/ 
#  This program adds only some few methods to appImageViewer1,
#  methods that should make it possible to capture a single image. The new 
#     camera menu has actions for: Camera On, Get One Image, and Camera Off
#  Program tested using IDS XS camera (the small one at UiS, the larger one is CP)
#
#  appImageViewer1.py is basically developed by copying the file appImageViewer.py
#  and then make the wanted changes and additions. This may be a good way to 
#  make a new program, but it also has some disadvantages; if you want to keep and
#  improve the original program, the new improvements should probably also be
#  done in the copied file (appImageViewer1.py) and you thus have to maintain the
#  common code in two files. 
#  
#  A better way to copy functionality is to use heritage. This is the approach done here,
#  the main window in this file is imported from appImageViewer1.py, and then new
#  functionality is added, or existing functionality may be updated. 
#
#  The user manual for IDS camera uEye software development kit (SDK) is helpful
#  for finding and using the IDS interface functions, it used to be available on
#  https://en.ids-imaging.com/manuals/uEye_SDK/EN/uEye_Manual_4.91/index.html
#  but the requested page cannot be found any more (is it somewhere else, like:
#  https://en.ids-imaging.com/files/downloads/ids-software-suite/interfaces/release-notes/python-release-notes_EN.html 
#  https://en.ids-imaging.com/release-note/release-notes-ids-software-suite-4-90.html 
#  http://en.ids-imaging.com/ueye-interface-python.html  (??)
#  ** now it is installed when IDS SW is installed, on my (KS) laptop it is located:
# file:///C:/Program%20Files/IDS/uEye/Help/uEye_Manual/index.html#is_exposuresetexposure.html
#  Also, I have a copy of the SDK user manual September 2008 version on:
#  ...\Dropbox\ELE610\IDS camera\IDS_uEye_SDK_manual_enu*.pdf
#
# Karl Skretting, UiS, November 2018, February 2019, November 2020, June 2022

# Example on how to use file:
# (C:\...\Anaconda3) C:\..\py3> activate py38
# (py38) C:\..\py3> python appImageViewer2.py
# (py38) C:\..\py3> python appImageViewer2.py rutergray.png

_appFileName = "appImageViewer2V"
_author = "Jesus Sanchez && Theo" 
_version = "2022.06.27"

import sys
import os.path
import ctypes
import numpy as np
from time import sleep
import random
import cv2

try:
	from PyQt5.QtCore import Qt, QPoint, QRectF, QT_VERSION_STR
	from PyQt5.QtGui import QImage, QPixmap, QTransform
	from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QFileDialog, QLabel, 
			QGraphicsScene, QGraphicsPixmapItem, QMessageBox)
	from PyQt5.QtWidgets import QInputDialog

except ImportError:
	raise ImportError( f"{_appFileName}: Requires PyQt5." )
#end try, import PyQt5 classes

try:
	from pyueye import ueye
	from pyueye_example_camera import Camera
	from pyueye_example_utils import ImageData, ImageBuffer  # FrameThread, 
	ueyeOK = True
except ImportError:
	ueye_error = f"{_appFileName}: Requires IDS pyueye example files (and IDS camera)." 
	# raise ImportError(ueye_error)
	ueyeOK = False   # --> may run program even without pyueye
#end try, import pyueye

from appImageViewer1 import myPath, MainWindow as inheritedMainWindow 
from myImageTools import np2qimage
from clsHoughCirclesDialog import HoughCirclesDialog

class MainWindow(inheritedMainWindow):  
	"""MainWindow class for this image viewer is inherited from another image viewer."""

	
# Two initialization methods used when an object is created
	def __init__(self, fName="", parent=None):
		# print( f"File {_appFileName}: (debug) first line in MainWindow.__init__()" )
		super().__init__(fName, parent)  # use inherited __init__ with extension as follows
		# 
		# set appFileName as it should be, it is set wrong in super()...
		self.appFileName = _appFileName 
		if self.pixmap.isNull(): 
			self.setWindowTitle(self.appFileName)
			self.npImage = np.array([])  # size == 0  
		else:
			self.setWindowTitle( f"{self.appFileName} : {fName}" ) 
			self.pixmap2image2np()   # function defined in appImageViewer1.py
		# 
		self.cam = None
		self.camOn = False
		self.eyes = None
		#
		# I had some trouble finding a good way to inherit (and add modifications to) 
		# functions 'initMenu' and 'setMenuItems' from appImageViewer1
		# To avoid any complications the corresponding functions are given new names here,
		# thus risking that the inherited (or the new ones) are not executed whenever they should be.
		self.initMenu2()
		self.setMenuItems2()
		# print(f"File {_appFileName}: (debug) last line in MainWindow.__init__()")
		return
	
	def initMenu2(self):
		"""Initialize Camera menu."""
		# print( f"File {_appFileName}: (debug) first line in initMenu2()" ) 
		a = self.qaCameraOn = QAction('Camera on', self)
		a.triggered.connect(self.cameraOn)
		#
		a = self.qaCameraInfo = QAction('Print camera info', self)
		a.triggered.connect(self.printCameraInfo)
		#
		a = self.qaFindFocus = QAction('Find focus', self)
		a.triggered.connect(self.findFocus)
		#
		a = self.qaGetOneImage = QAction('Get one image', self)
		a.setShortcut('Ctrl+N')
		a.triggered.connect(self.getOneImage)
		#
		a = self.qaGetOneImageV2 = QAction('Get one image (ver.2 2022)', self)
		a.triggered.connect(self.getOneImageV2)
		#
		a = self.qaCameraOff = QAction('Camera off', self)
		a.triggered.connect(self.cameraOff)
		#
		a = self.qaBlackDots = QAction('Black dots', self)
		a.triggered.connect(self.blackDots)
		#
		a = self.qaHoughCircles = QAction('Hough Circles', self)
		a.triggered.connect(self.houghCircles)
		#
		a = self.qaCountEyes = QAction('Count Eyes', self)
		a.triggered.connect(self.countEyes)
		#
		a = self.qaDetectDiceColor = QAction('Detect Dice Color', self)
		a.triggered.connect(self.detectDiceColor)
		#


		a = self.qaSetExposure = QAction('Set Exposure', self)
		a.triggered.connect(self.setCameraExposure)


		
		camMenu = self.mainMenu.addMenu('&Camera')
		camMenu.addAction(self.qaCameraOn)
		camMenu.addAction(self.qaCameraInfo)
		camMenu.addAction(self.qaFindFocus)
		camMenu.addAction(self.qaGetOneImage)
		camMenu.addAction(self.qaGetOneImageV2)
		camMenu.addAction(self.qaCameraOff)
		camMenu.addAction(self.qaSetExposure)


		daisMenu = self.mainMenu.addMenu('&Dais')
		daisMenu.addAction(self.qaBlackDots)
		daisMenu.addAction(self.qaHoughCircles)
		daisMenu.addAction(self.qaCountEyes)
		daisMenu.addAction(self.qaDetectDiceColor)
		# print( "File {_appFileName}: (debug) last line in initMenu2()" ) 
		return
	
# Some methods that may be used by several of the menu actions
	def setMenuItems2(self):
		"""Enable/disable menu items as appropriate."""
		# should the 'inherited' function be used, first check if it exists 
		setM = getattr(super(), "setMenuItems", None)  # both 'self' and 'super()' seems to work as intended here
		if callable(setM):
			# print("setMenuItems2(): The 'setMenuItems' function is inherited.")
			setM()  # and run it
		# self.setMenuItems() 
		self.qaCameraOn.setEnabled(ueyeOK and (not self.camOn))
		self.qaCameraInfo.setEnabled(ueyeOK and self.camOn)
		self.qaFindFocus.setEnabled(ueyeOK and self.camOn)
		self.qaGetOneImage.setEnabled(ueyeOK and self.camOn)
		self.qaGetOneImageV2.setEnabled(ueyeOK and self.camOn)
		self.qaCameraOff.setEnabled(ueyeOK and self.camOn)
		self.qaCountEyes.setEnabled(self.eyes is not None)
		return
		
	def copy_image(self, image_data):
		"""Copy an image from camera memory to numpy image array 'self.npImage'."""
		tempBilde = image_data.as_1d_image()
		if np.min(tempBilde) != np.max(tempBilde):
			self.npImage = np.copy(tempBilde[:,:,[0,1,2]])  # or [2,1,0] ??  RGB or BGR?
			print( ("copy_image(): 'self.npImage' is an ndarray" + 
			        f" of {self.npImage.dtype.name}, shape {str(self.npImage.shape)}.") )
		else: 
			self.npImage = np.array([])  # size == 0
		#end if 
		image_data.unlock()  # important action
		return 
		
# Methods for actions on the Camera-menu
# dette gir ikke samme muligheter som IDS program, autofokus for XS kamera virker ikke her
	def cameraOn(self):
		"""Turn IDS camera on."""
		if ueyeOK and (not self.camOn):
			self.cam = Camera()
			self.cam.init()  # gives error when camera not connected
			self.cam.set_colormode(ueye.IS_CM_BGR8_PACKED)
			# This function is currently not supported by the camera models USB 3 uEye XC and XS.
			self.cam.set_aoi(0, 0, 720, 1280)  # but this is the size used
			self.cam.alloc(3)  # argument is number of buffers
			self.camOn = True
			self.setMenuItems2()
			print( f"{self.appFileName}: cameraOn() Camera started ok" )
		#
		return
	
	def printCameraInfo(self):
		"""Print some information on camera."""
		if ueyeOK and self.camOn:
			print("printCameraInfo(): print (test) state and settings.")
			d = ueye.double()
			ui1 = ueye.uint()
			retVal = ueye.is_SetFrameRate(self.cam.handle(), 2.0, d)
			if retVal == ueye.IS_SUCCESS:
				print( f"  frame rate set to                      {float(d):8.3f} fps" )
			retVal = ueye.is_Exposure(self.cam.handle(), 
			                          ueye.IS_EXPOSURE_CMD_GET_EXPOSURE_DEFAULT, d, 8)
			if retVal == ueye.IS_SUCCESS:
				print( f"  default setting for the exposure time  {float(d):8.3f} ms" )
			retVal = ueye.is_Exposure(self.cam.handle(), 
			                          ueye.IS_EXPOSURE_CMD_GET_EXPOSURE_RANGE_MIN, d, 8)
			if retVal == ueye.IS_SUCCESS:
				print( f"  minimum exposure time                  {float(d):8.3f} ms" )
			retVal = ueye.is_Exposure(self.cam.handle(), 
			                          ueye.IS_EXPOSURE_CMD_GET_EXPOSURE_RANGE_MAX, d, 8)
			if retVal == ueye.IS_SUCCESS:
				print( f"  maximum exposure time                  {float(d):8.3f} ms" )
			# 
			print( f"  sys.getsizeof(d) returns   {sys.getsizeof(d)}  (??)" )
			print( f"  sys.getsizeof(ui1) returns {sys.getsizeof(ui1)}  (??)" )
			retVal = ueye.is_Focus(self.cam.handle(), ueye.FDT_CMD_GET_CAPABILITIES, ui1, 4)
			if ((retVal == ueye.IS_SUCCESS) and (ui1 & ueye.FOC_CAP_AUTOFOCUS_SUPPORTED)):
				print( "  autofocus supported" )
			if retVal == ueye.IS_SUCCESS:
				print( f"  is_Focus() is success          ui1 = {ui1}" )
			else:
				print( f"  is_Focus() is NOT success   retVal = {retVal}" )
			fZR = ueye.IS_RECT()  
			retVal = ueye.is_Focus(self.cam.handle(), ueye.FOC_CMD_SET_ENABLE_AUTOFOCUS, ui1, 0)
			if retVal == ueye.IS_SUCCESS:
				print( f"  is_Focus( ENABLE ) is success      " )
			retVal = ueye.is_Focus(self.cam.handle(), ueye.FOC_CMD_GET_AUTOFOCUS_STATUS, ui1, 4)
			if retVal == ueye.IS_SUCCESS:
				print( f"  is_Focus( STATUS ) is success  ui1 = {ui1}" )
			retVal = ueye.is_Exposure(self.cam.handle(), ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, d, 8)
			if retVal == ueye.IS_SUCCESS:
				print( f"  currently set exposure time            {float(d):8.3f} ms" )
		return
		
	def getOneImageV2(self):
		"""Get one image from IDS camera, version 2, autumn 2022."""
		if not(ueyeOK and self.camOn): 
			# pass  # ignore action
			#else:  
			return
		#
		self.view.setMouseTracking(False)
		print( f"{self.appFileName}: getOneImageV2() try to capture one image" )
		imBuf = ImageBuffer()  # used to get return pointers
		self.cam.freeze_video(True)
		# some sleep does not help
		# sleep(2.5)
		# self.cam.freeze_video(False)
		# sleep(2.5)
		# self.cam.freeze_video(True)
		# function below obsolete in UDS 4.95 -->
		# use is_ImageQueue(), see: https://en.ids-imaging.com/release-note/release-notes-ids-software-suite-4-95.html
		retVal = ueye.is_WaitForNextImage(self.cam.handle(), 1000, imBuf.mem_ptr, imBuf.mem_id)
		if retVal == ueye.IS_SUCCESS:
			print( f"  ueye.IS_SUCCESS: image buffer id = {imBuf.mem_id}" )
			self.copy_image( ImageData(self.cam.handle(), imBuf) )  # copy image_data 
			if (self.npImage.size > 0): # ok 
				self.image = np2qimage(self.npImage)
				if (not self.image.isNull()):
					self.pixmap = QPixmap.fromImage(self.image)
					if self.curItem: 
						self.scene.removeItem(self.curItem)
					self.curItem = QGraphicsPixmapItem(self.pixmap)
					self.scene.addItem(self.curItem)
					self.scene.setSceneRect(0, 0, self.pixmap.width(), self.pixmap.height())
					self.setWindowTitle( f"{self.appFileName} : Camera image" ) 
					(w,h) = (self.pixmap.width(), self.pixmap.height())
					self.status.setText( f"pixmap: (w,h) = ({w},{h})" )
					self.scaleOne()
					self.view.setMouseTracking(True)
				else:
					self.pixmap = QPixmap()
				#end
			else:  # empty image self.npImage
				self.image = QImage()
				self.pixmap = QPixmap()
				print( "  no image in buffer " + str(imBuf) )
			#
		else: 
			self.setWindowTitle( "{self.appFileName}: getOneImage() error retVal = {retVal}" )
		#end if
		self.setIsAllGray()
		self.setMenuItems2()
		return
	
	def getOneImage(self):
		"""Get one image from IDS camera."""
		if ueyeOK and self.camOn:
			self.view.setMouseTracking(False)
			print( f"{self.appFileName}: getOneImage() try to capture one image" )
			imBuf = ImageBuffer()  # used to get return pointers
			self.cam.freeze_video(True)
			retVal = ueye.is_WaitForNextImage(self.cam.handle(), 1000, imBuf.mem_ptr, imBuf.mem_id)
			if retVal == ueye.IS_SUCCESS:
				print( f"  ueye.IS_SUCCESS: image buffer id = {imBuf.mem_id}" )
				self.copy_image( ImageData(self.cam.handle(), imBuf) )  # copy image_data 
				if (self.npImage.size > 0): # ok 
					self.image = np2qimage(self.npImage)
					if (not self.image.isNull()):
						self.pixmap = QPixmap.fromImage(self.image)
						if self.curItem: 
							self.scene.removeItem(self.curItem)
						self.curItem = QGraphicsPixmapItem(self.pixmap)
						self.scene.addItem(self.curItem)
						self.scene.setSceneRect(0, 0, self.pixmap.width(), self.pixmap.height())
						self.setWindowTitle( f"{self.appFileName} : Camera image" ) 
						(w,h) = (self.pixmap.width(), self.pixmap.height())
						self.status.setText( f"pixmap: (w,h) = ({w},{h})" )
						self.scaleOne()
						self.view.setMouseTracking(True)
					else:
						self.pixmap = QPixmap()
					#end
				else:  # empty image self.npImage
					self.image = QImage()
					self.pixmap = QPixmap()
					print( "  no image in buffer " + str(imBuf) )
				#
			else: 
				self.setWindowTitle( "{self.appFileName}: getOneImage() error retVal = {retVal}" )
			#end if
			self.setIsAllGray()
			self.setMenuItems2()
		#else:  
		#	pass  # ignore action
		return
		
	def cameraOff(self):
		"""Turn IDS camera off and print some information."""
		if ueyeOK and self.camOn:
			self.cam.exit()
			self.camOn = False
			self.setMenuItems2()
			print( f"{self.appFileName}: cameraOff() Camera stopped ok" )
		return
	
	def setCameraExposure(self):
			"""Set the exposure time of the camera."""
			if not (ueyeOK and self.camOn):
				return
		
			d = ueye.double()
			retVal = ueye.is_Exposure(self.cam.handle(), ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, d, 8)
			if retVal == ueye.IS_SUCCESS:
				current_exposure = float(d)
			else:
				print("Failed to get current exposure time.")
				return
		
			new_exposure, ok = QInputDialog.getDouble(self, "Set Exposure", "Enter new exposure time (ms):", current_exposure, 0.1, 9999.0, 2)
			if ok:
				d = ueye.double(new_exposure)
				retVal = ueye.is_Exposure(self.cam.handle(), ueye.IS_EXPOSURE_CMD_SET_EXPOSURE, d, 8)
				if retVal == ueye.IS_SUCCESS:
					print(f"Exposure time successfully set to {new_exposure:.2f} ms")
				else:
					print("Failed to set new exposure time.")



	def findFocus(self):
		"""Find focus."""
		if ueyeOK and self.camOn:
			num_images = random.randint(15, 25)
			print(f" Capturing {num_images} images to find focus.")
   
		# Capture images
		for i in range(num_images):
			print(f" Capturing image {i + 1} / {num_images}...")
			self.getOneImage()
   
		# Asume focus was found
		print(f"{self.appFileName}: FindFocus() - Focus found.")
		return
	
	def blackDots(self):
		"""Detect black dots on a dice."""
		if ueyeOK and self.camOn:
			if self.npImage.size == 0:
				print(f"{self.appFileName}: blackDots() no image in buffer")
				return

		print(f"{self.appFileName}: BlackDots() - Detecting black dots on the dice.")
  
		
		self.toGray()
		self.toBinary()

		# Convert QPixmap to QImage
		qimage = self.pixmap.toImage()
		
		# Convert QImage to numpy array
		width = qimage.width()
		height = qimage.height()
		channels = 4 if qimage.hasAlphaChannel() else 3
		image_data = qimage.bits().asarray(height * width * channels)
		
		# Reshape numpy array to OpenCV format
		img = np.frombuffer(image_data, dtype=np.uint8).reshape((height, width, channels))
		
		# Convert from RGB(A) to BGR (OpenCV format)
		if channels == 4:
			img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
		else:
			img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

  
		nDots = np.sum(img == 0)
  
		print(f"Number of black dots: {nDots}")
  
	def prepareHoughCirclesA(self):
		"""Make self.A the gray scale image to detect circles in"""
		if (self.A.size == 0):
			# make self.A a gray scale image
			if (len(self.npImage.shape) == 3):
				if (self.npImage.shape[2] == 3):
					self.A = cv2.cvtColor(self.npImage, cv2.COLOR_BGR2GRAY )
					self.B = self.npImage.copy()
				elif (self.npImage.shape[2] == 4):
					self.A = cv2.cvtColor(self.npImage, cv2.COLOR_BGRA2GRAY )
					self.B = cv2.cvtColor(self.npImage, cv2.COLOR_BGRA2BGR )   
				else:
					print("prepareHoughCircles(): numpy 3D image is not as expected. --> return")
					return
				#end
			elif (len(self.npImage.shape) == 2):
				self.A = self.npImage.copy()
				self.B = cv2.cvtColor(self.npImage, cv2.COLOR_GRAY2BGR )   
			else:
				print("prepareHoughCircles(): numpy image is not as expected. --> return")
				return
			#end
		return

	def prepareHoughCirclesB(self):
		"""Make self.B the BGR image to draw detected circles in"""
		if (len(self.npImage.shape) == 3):
			if (self.npImage.shape[2] == 3):
				self.B = self.npImage.copy()
			elif (self.npImage.shape[2] == 4):
				self.B = cv2.cvtColor(self.npImage, cv2.COLOR_BGRA2BGR )   
			#end
		elif (len(self.npImage.shape) == 2):
			self.B = cv2.cvtColor(self.npImage, cv2.COLOR_GRAY2BGR )   
		#end
		return

	def checkColor(self):
		"""Check colors for image and set menu items according to active image."""
		self.setIsAllGray()   # check color state on self.image (=self.pixmap, and usually also self.npImage)
		self.setMenuItems()
		return
  
	def houghCircles (self):
		oldPixmap = self.prevPixmap
		self.prevPixmap = self.pixmap
		self.A = np.array([])
		self.prepareHoughCirclesA()
		d = HoughCirclesDialog(self, title="Select parameters that locate the dice eyes")
		(dp, minDist, param1, param2, minRadius, maxRadius, maxCircles) = d.getValues()
		if d.result():
			C = cv2.HoughCircles(self.A, cv2.HOUGH_GRADIENT, dp=dp, minDist=minDist, param1=param1, param2=param2, 
			                     minRadius=minRadius, maxRadius=maxRadius)
			self.prepareHoughCirclesB()
   
			self.eyes = 0
			if C is not None:
				C = np.int16(np.around(C))
				self.detectedCircles = C
				self.eyes = min(maxCircles, C.shape[1]) # Save number of eyes found
				print(f"  'C'  is ndarray of {C.dtype.name}, shape: {str(C.shape)}")
				for i in range(min(maxCircles, C.shape[1])):
					(x,y,r) = ( C[0,i,0], C[0,i,1], C[0,i,2] )  # center and radius
					# cv2.circle(self.B, (x,y), 1, (0, 100, 100), 3)  # indicate center 
					cv2.circle(self.B, (x,y), r, (255, 0, 255), 3) # and circle outline 

			self.A = np.array([])
			self.np2image2pixmap(self.B, numpyAlso=True)
			self.B = np.array([])
			self.setWindowTitle(f"{self.appFileName} : indicate found circles")
			self.checkColor()
   
		else:
			self.pixmap = self.prevPixmap
			self.pixmap2image2np()
			self.prevPixmap = oldPixmap

		print(f"Number of eyes found: {self.eyes}")
		return


	def countEyes(self):
		"""Count the number of eyes found."""
		if hasattr(self, 'eyes'):
			msg = f"Number of eyes found: {self.eyes}"
		else:
			msg = "Something went wrong when counting eyes."

		print(msg)
		QMessageBox.information(self, "Number of eyes", msg)
  
		return

	def detectDiceColor(self):
		"""Detect the color of the dice based on the pixels next to the dice eyes"""
		if not hasattr(self, 'eyes') or self.eyes == 0:
			QMessageBox.warning(self, "No eyes detected", "No eyes detected, can not determine the dice color")

		rgb_image = cv2.cvtColor(self.npImage, cv2.COLOR_BGR2RGB)
		color_counts = {}
  
		COLOR_RANGES_RGB = {
			"White": [(200, 200, 200), (255, 255, 255)],  # White
			"Red": [(120, 0, 0), (255, 100, 100)],         # Red
			"Green": [(0, 100, 0), (100, 255, 100)],      # Green
			"Blue": [(0, 0, 100), (100, 100, 255)],       # Blue
			"Yellow": [(130, 130, 0), (255, 255, 150)],   # Yellow
			"Black": [(0, 0, 0), (50, 50, 50)],           # Black
		}



		for color in COLOR_RANGES_RGB.keys():
			color_counts[color] = 0
   
		# Loop through all detected eyes
		for i in range(self.eyes):
			x, y, r = self.detectedCircles[0, i]
   
			for angle in range(0,360, 30):
				angle_rad = np.deg2rad(angle)
				x_sample = int(x + (r +5) * np.cos(angle_rad))
				y_sample = int(y + (r +5) * np.sin(angle_rad))
    
				if 0 <= x_sample < rgb_image.shape[1] and 0 <= y_sample < rgb_image.shape[0]:
					pixel_rgb = rgb_image[y_sample, x_sample]

					for color, (lower, upper) in COLOR_RANGES_RGB.items():
						lower = np.array(lower, dtype=np.uint8)
						upper = np.array(upper, dtype=np.uint8)
      
						if np.all(pixel_rgb >= lower) and np.all(pixel_rgb <=upper):
							color_counts[color] += 1

		# Determine dominant color
		dominant_color = max(color_counts, key=color_counts.get)
  
		# Special case for red  (since it's split in HSV space)
		if dominant_color == "Red2":
			dominant_color = "Red"
   
		print(f"Detected dice color: {dominant_color}")
		QMessageBox.information(self, "Dice color", f"Detected dice color: {dominant_color}")
   

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
		mainWin = MainWindow(fName=fn)
	else:
		mainWin = MainWindow()
	mainWin.show()
	sys.exit(mainApp.exec_())  # single_trailing_underscore_ is used for avoiding conflict with Python keywords

