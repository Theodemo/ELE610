#!/usr/bin/env python
# -*- coding: utf-8 -*-

_appFileName = "appImageViewerX"
_version = "0.1"


import sys
import os.path
import numpy as np
from time import sleep

try:
	from PyQt5.QtCore import Qt, QPoint, QRectF, QT_VERSION_STR
	from PyQt5.QtGui import QImage, QPixmap, QTransform
	from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QFileDialog, QLabel, 
			QGraphicsScene, QGraphicsPixmapItem)
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
		camMenu = self.mainMenu.addMenu('&Camera')
		camMenu.addAction(self.qaCameraOn)
		camMenu.addAction(self.qaCameraInfo)
		camMenu.addAction(self.qaGetOneImage)
		camMenu.addAction(self.qaGetOneImageV2)
		camMenu.addAction(self.qaCameraOff)
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
		self.qaGetOneImage.setEnabled(ueyeOK and self.camOn)
		self.qaGetOneImageV2.setEnabled(ueyeOK and self.camOn)
		self.qaCameraOff.setEnabled(ueyeOK and self.camOn)
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
			# just set a camera option (parameter) even if it is not used here
			d = ueye.double()
			# d1 = ueye.double() 
			# d2 = ueye.double()
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
			fZR = ueye.IS_RECT()   # may be used to set focus ??
			retVal = ueye.is_Focus(self.cam.handle(), ueye.FOC_CMD_SET_ENABLE_AUTOFOCUS, ui1, 0)
			if retVal == ueye.IS_SUCCESS:
				print( f"  is_Focus( ENABLE ) is success      " )
			retVal = ueye.is_Focus(self.cam.handle(), ueye.FOC_CMD_GET_AUTOFOCUS_STATUS, ui1, 4)
			if retVal == ueye.IS_SUCCESS:
				print( f"  is_Focus( STATUS ) is success  ui1 = {ui1}" )
			# her slutter det jeg testet ekstra i 2021
			retVal = ueye.is_Exposure(self.cam.handle(), ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, d, 8)
			if retVal == ueye.IS_SUCCESS:
				print( f"  currently set exposure time            {float(d):8.3f} ms" )
			d =  ueye.double(5.0)
			retVal = ueye.is_Exposure(self.cam.handle(), ueye.IS_EXPOSURE_CMD_SET_EXPOSURE, d, 8)
			if retVal == ueye.IS_SUCCESS:
				print( f"  tried to changed exposure time to      {float(d):8.3f} ms" )
			retVal = ueye.is_Exposure(self.cam.handle(), ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, d, 8)
			if retVal == ueye.IS_SUCCESS:
				print( f"  currently set exposure time            {float(d):8.3f} ms" )
			#
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
	
	def findBlackDot(self):
		"""Find black dot in image."""
		if self.npImage.size == 0:
			return
		#
		# convert image to grayscale
		gray = cv2.cvtColor(self.npImage, cv2.COLOR_BGR2GRAY)
		# threshold the image to reveal light regions in the
		# blurred image
		thresh = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY)[1]
		# perform a series of erosions and dilations to remove
		# any small blobs of noise from the thresholded image
		thresh = cv2.erode(thresh, None, iterations=2)
		thresh = cv2.dilate(thresh, None, iterations=4)
		# find contours in the thresholded image
		cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)
		cnts = imutils.grab_contours(cnts)
		# loop over the contours
		for c in cnts:
			# compute the center of the contour
			M = cv2.moments(c)
			cX = int(M["m10"] / M["m00"])
			cY = int(M["m01"] / M["m00"])
			# draw the contour and center of the shape on the image
			cv2.drawContours(self.npImage, [c], -1, (0, 255, 0), 2)
			cv2.circle(self.npImage, (cX, cY), 7, (255, 255, 255), -1)
			cv2.putText(self.npImage, "center", (cX - 20, cY - 20),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
		# show the image
		cv2.imshow("Image", self.npImage)
		cv2.waitKey(0)
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
