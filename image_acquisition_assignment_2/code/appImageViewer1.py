
_appFileName = "appImageViewer1"
_author = "Théo de Morais" 
_version = "2024.02.02"

import sys
import os.path
import numpy as np
try:
	import cv2
	cv2isOK = True
except:
	print( f"Error importing cv2, {_appFileName} run with cv2 options disabled." )
	cv2isOK = False
#

try:
	from PyQt5.QtCore import Qt, QPoint, QRect, QSize, QT_VERSION_STR, pyqtSignal  
	from PyQt5.QtGui import QImage, QPixmap, QTransform
	from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QFileDialog, QLabel, 
				QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QRubberBand)
except ImportError:
	raise ImportError( f"{_appFileName}: Requires PyQt5." )
#end try, import PyQt5 classes 

# some simple classes that define simple dialog windows
from clsEdgeDialog import EdgeDialog
from clsFilterDialog import FilterDialog
from clsThresholdDialog import ThresholdDialog
from clsResizeDialog import ResizeDialog
if cv2isOK:
	from clsHoughLinesDialog import HoughLinesDialog, getBestHoughLines, draw_lines
#
# some simple methods for image processing
from myImageTools import smoothFilter, qimage2np, np2qimage

try:
	from myTools import DBpath # my DropBox
	myPath = DBpath( "m610" )  # path where KS have some images
except:
	myPath = ""                # path where you may have some images
#end try, import DBpath  


class MyGraphicsView(QGraphicsView):
	"""This is the viewer where the pixmap is shown, it is a simple extension of QGraphicsView.
	
	Mouse events are processed in this class.
	To use rubber band: parent should set rubberBandActive to True, after this
	the rubber band is shown when mouse left button is pressed and moved until it is released.
	When mouse button is released a signal (that includes the rectangle) is emitted,
	this signal can be connected to a parent function, ex. cropEnd(rectangle),
	and processed further there.
	Note that this class uses some variables belonging to the parent (MainWindow object),
	this is to print information, and to set position information text.
	"""
	rubberBandRectGiven = pyqtSignal(QRect) 

	def __init__(self, scene, parent=None):
		"""Initialize, basically as for the inherited class 'QGraphicView', 
		but add mouse tracking and rubber band functionality."""
		super().__init__(scene, parent)
		self.setMouseTracking(True)
		self.pos1 = QPoint()
		self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
		self.rubberBand.hide()
		self.rubberBandActive = False
		return	# __init__(self)
		
	def mousePressEvent(self, event):
		"""Print where the mouse is when a mouse button is pressed.
		Perhaps, if self.rubberBandActive, also start to show the rubber band.
		Rubber band uses left mouse button and is activated by setting rubberBandActive to True.
		Note that event.pos() gives the location in the view, while (x,y) gives the
		location in the scene, which here corresponds to the pixel index of the pixmap.
		This method is a 'slot' that is called whenever a mouse button is pressed (in the view).
		"""
		p = self.parent()
		posScene = self.mapToScene(event.pos())
		(x,y) = (int(posScene.x()), int(posScene.y()))
		#
		if (event.button() == Qt.LeftButton):
			print( "MyGraphicsView.mousePressEvent: Press LeftButton at:  ", end='') 
			self.pos1 = event.pos()
			if self.rubberBandActive:
				self.rubberBand.setGeometry(QRect(event.pos(), QSize()))
				self.rubberBand.show()
		if (event.button() == Qt.RightButton):
			print( "MyGraphicsView.mousePressEvent: Press RightButton at: ", end='')
		print( f"{str(event.pos())}, in scene at (x,y) = ({x},{y})" )
		return 
		
	def mouseMoveEvent(self, event): 
		"""Displays position of mouse pointer and, from the QImage object, the pixel color. 
		Perhaps, if self.rubberBandActive, also updates the rubber band rectangle.
		This method is a 'slot' that is called whenever the mouse moves over the view.
		"""
		p = self.parent()
		if self.rubberBandActive:
			self.rubberBand.setGeometry(QRect(self.pos1, event.pos()).normalized())
		# 
		posScene = self.mapToScene(event.pos())
		(x,y) = (int(posScene.x()), int(posScene.y()))
		# p.pixmap and p.image should be same size
		if ((x >= 0) and (y >= 0) and (y < p.pixmap.height()) and (x < p.pixmap.width())):
			if not p.image.isNull():  
				col = p.image.pixelColor(x, y)
				if p.isAllGray: 
					p.posInfo.setText( f"(x,y) = ({x},{y}):  gray = {col.red()}" )   # or col.value()
				elif (p.image.format() == QImage.Format_Indexed8): 
					p.posInfo.setText( "(x,y) = ({x},{y}):  gray/index  = {col.value()}" )
				else: # QImage.Format_RGB32, or other
					(r,g,b,a) = (col.red(), col.green(), col.blue(), col.alpha())
					if (a == 255):
						p.posInfo.setText( f"(x,y) = ({x},{y}):  (r,g,b) = ({r},{g},{b})" )
					else:
						p.posInfo.setText( f"(x,y) = ({x},{y}):  (r,g,b,a) = ({r},{g},{b},{a})" )
			else: 
				p.posInfo.setText( f"(x,y) = ({x},{y})" )
		else:
			p.posInfo.setText(" ") 
		return

	def mouseReleaseEvent(self, event):
		"""Just print when the left mouse button is released.
		Perhaps, if self.rubberBandActive, a signal with the rubber band rectangle is emitted
		This method is a 'slot' that is called whenever a mouse button is 
		released (after being pressed in the view).
		"""
		if (event.button() == Qt.LeftButton):
			print("MyGraphicsView.mouseReleaseEvent():  Button pressed and released")
			if self.rubberBandActive:
				self.rubberBand.hide()
				self.rubberBandActive = False
				posScene = self.mapToScene(self.pos1)
				(x,y) = (int(posScene.x()), int(posScene.y()))
				posScene = self.mapToScene(event.pos())
				(w,h) = (int(posScene.x())-x, int(posScene.y())-y)
				self.rubberBandRectGiven.emit( QRect(x,y,w,h).normalized() )
				# without the signal we could assume that the connected function is known here and just call it
				# self.parent().cropEnd(QRect(x,y,w,h).normalized())
		#end if
		return
	#end class MyGraphicsView
	
	
class MainWindow(QMainWindow):  
	"""MainWindow class for this simple image viewer."""
	
# Two initialization methods used when an object is created
	def __init__(self, fName="", parent=None):
		"""Initialize the main window object with title, location and size,
		an empty image (represented both as pixmap and image and numpy array), 
		empty scene and empty view, labels for status and position information.
		A file name 'fName' may be given as input (from command line when program is started)
		and if so the file (an image) will be opened and displayed.
		"""
		# print( "File {_appFileName}: (debug) first line in MainWindow.__init__()" )
		super().__init__(parent) 
		self.appFileName = _appFileName 
		self.setGeometry(150, 50, 1400, 800)  # initial window position and size
		self.scaleUpFactor = np.sqrt(2.0)
		#
		self.pixmap = QPixmap()      # a null pixmap
		self.prevPixmap = QPixmap()  # another (for previous pixmap)
		self.image = QImage()        # a null image
		self.isAllGray = False       # true when self.image.allGray(), function is slow for images without color table
		self.npImage = np.array([])  # size == 0 
		self.cropActive = False
		#
		self.scene = QGraphicsScene()
		self.curItem = None          # (a pointer to) pixmap on scene
		self.view = MyGraphicsView(self.scene, parent=self)
		self.view.rubberBandRectGiven.connect(self.cropEnd)
		self.status = QLabel('Open image to display it.', parent = self)
		self.posInfo = QLabel(' ', parent = self)
		#
		self.initMenu()  # menu is needed before (!) self.openFile(..)
		#
		if isinstance(fName, str) and (fName != ""):
			self.openFile(fName)
		#
		if (not self.pixmap.isNull()): 
			self.setWindowTitle( f"{self.appFileName} : {fName}" )
		else:
			self.setWindowTitle(self.appFileName)
		#
		self.setMenuItems()
		# print( f"File {_appFileName}:  (debug) last line in MainWindow.__init__()" )
		return
	#end function __init__  
	
	def initMenu(self):
		"""Initialize File, Scale, and Edit menus."""
		# print( f"File {_appFileName}:  (debug) first line in MainWindow.initMenu()" )
		#
		a = qaOpenFileDlg = QAction('Open file', self)
		a.setShortcut('Ctrl+O')
		a.triggered.connect(self.openFileDlg)
		a = self.qaSaveFileDlg = QAction('Save file', self)
		a.setShortcut('Ctrl+S')
		a.triggered.connect(self.saveFileDlg)
		a = self.qaClearImage = QAction('Clear image', self)
		a.setShortcut('Ctrl+C')
		a.setToolTip('Remove the current pixmap item from scene.')
		a.triggered.connect(self.removePixmapItem)
		a = qaPrintInfo = QAction('print Info', self)
		a.setShortcut('Ctrl+I')
		a.triggered.connect(self.printInfo)
		a = qaQuitProgram = QAction('Quit', self)
		a.setShortcut('Ctrl+Q')
		a.setToolTip('Close and quit program')
		a.triggered.connect(self.quitProgram)
		#
		a = self.qaScaleOne = QAction('scale 1', self)
		a.setShortcut('Ctrl+1')
		a.triggered.connect(self.scaleOne)
		a = self.qaScaleUp = QAction('scale Up', self)
		a.setShortcut('Ctrl++')
		a.triggered.connect(self.scaleUp)
		a = self.qaScaleDown = QAction('scale Down', self)
		a.setShortcut('Ctrl+-')
		a.triggered.connect(self.scaleDown)
		#
		a = self.qaCrop = QAction('Crop image', self)
		a.triggered.connect(self.cropStart)
		a.setToolTip('Crop the current pixmap, start by indicating rectangle to keep.')
		a.setShortcut('Ctrl+Y')  # as in IrfanView
		a = self.qaResize = QAction('Resize image', self)
		a.triggered.connect(self.resizeImage)
		a.setToolTip('Resize the current npImage (and pixmap)')
		a.setShortcut('Ctrl+R')  # as in IrfanView
		a = self.qaToGray = QAction('to Gray', self)
		a.triggered.connect(self.toGray)
		a.setToolTip('Convert the current (numpy) BGR image to gray scale, and display it as pixmap.')
		a.setShortcut('Ctrl+G')
		a = self.qaToEdges = QAction('to Edges', self)
		a.triggered.connect(self.toEdges)
		a.setToolTip('Use Sobel filters and low-pass filter and find edges.')
		a.setShortcut('Ctrl+E')
		a = self.qaFilter = QAction('Filter image', self)
		a.triggered.connect(self.filterImage)
		a.setToolTip('Define a filter plus a low-pass filter and filter image.')
		a.setShortcut('Ctrl+F')
		a = self.qaToBinary = QAction('to Binary', self)
		a.triggered.connect(self.toBinary)
		a.setToolTip('Threshold image to make binary image.')
		a.setShortcut('Ctrl+B')
		a = self.qaFindLines = QAction('find Lines', self)
		a.triggered.connect(self.findHoughLines)
		a.setToolTip('Find lines using HoughLines or HoughLinesP.')
		a.setShortcut('Ctrl+L')
		a = self.qaUndoLast = QAction('Undo last', self)
		a.setShortcut('Ctrl+Z')
		a.triggered.connect(self.undoLast)
		#
		# menuBar is a function in QMainWindow class, returns a QMenuBar object
		self.mainMenu = self.menuBar()  
		self.fileMenu = self.mainMenu.addMenu('&File')
		self.fileMenu.addAction(qaOpenFileDlg)
		self.fileMenu.addAction(self.qaSaveFileDlg)
		self.fileMenu.addAction(self.qaClearImage)
		self.fileMenu.addAction(qaPrintInfo)
		self.fileMenu.addAction(qaQuitProgram)
		self.fileMenu.setToolTipsVisible(True)
		#
		scaleMenu = self.mainMenu.addMenu('&Scale')
		scaleMenu.addAction(self.qaScaleOne)
		scaleMenu.addAction(self.qaScaleUp)
		scaleMenu.addAction(self.qaScaleDown)
		#
		editMenu = self.mainMenu.addMenu('&Edit')
		editMenu.addAction(self.qaCrop)
		editMenu.addAction(self.qaResize)
		editMenu.addAction(self.qaToGray)
		editMenu.addAction(self.qaToEdges)
		editMenu.addAction(self.qaFilter)
		editMenu.addAction(self.qaToBinary)
		editMenu.addAction(self.qaFindLines)
		editMenu.addAction(self.qaUndoLast)
		editMenu.setToolTipsVisible(True)
		# print( f"File {_appFileName}: (debug) last line in MainWindow.initMenu()" )
		return
	#end function initMenu
	
# Some functions that may be used by several of the menu actions
	def setMenuItems(self):
		"""Enable/disable menu items as appropriate."""
		pixmapOK = ((not self.pixmap.isNull()) and isinstance(self.curItem, QGraphicsPixmapItem))
		self.qaSaveFileDlg.setEnabled(pixmapOK)
		self.qaClearImage.setEnabled(pixmapOK)
		self.qaScaleOne.setEnabled(pixmapOK)
		self.qaScaleUp.setEnabled(pixmapOK)
		self.qaScaleDown.setEnabled(pixmapOK)
		#
		self.qaCrop.setEnabled(cv2isOK and pixmapOK and (not self.cropActive))
		self.qaResize.setEnabled(cv2isOK and pixmapOK and (not self.cropActive))
		self.qaToGray.setEnabled(cv2isOK and pixmapOK and (not self.isAllGray))
		self.qaToEdges.setEnabled(cv2isOK and pixmapOK and self.isAllGray)
		self.qaFilter.setEnabled(cv2isOK and pixmapOK and self.isAllGray)
		self.qaToBinary.setEnabled(cv2isOK and pixmapOK and self.isAllGray)
		self.qaFindLines.setEnabled(cv2isOK and pixmapOK and self.isAllGray)
		self.qaUndoLast.setEnabled(not self.prevPixmap.isNull())
		return
	
	def setIsAllGray(self, value=-1):
		"""Set variable 'self.isAllGray', usually by calling method 'QImage.allGray', 
		but value may be given as input argument 'value' as well; ==0 for False, and >0 for True
		"""
		if (value == 0):
			self.isAllGray = False
		elif (value > 0):
			self.isAllGray = True
		else:
			if (not self.image.isNull()): 
				self.isAllGray = self.image.allGray()
			else:
				self.isAllGray = False
			#
		#
		self.setMenuItems()
		return
		
	def pixmap2image2np(self):
		"""Display 'self.pixmap' on scene and copy it to 'self.image' and to 'self.npImage'."""
		if self.curItem: 
			self.scene.removeItem(self.curItem)
		self.curItem = QGraphicsPixmapItem(self.pixmap)
		self.scene.addItem(self.curItem)
		(w, h) = (self.pixmap.width(), self.pixmap.height())
		self.scene.setSceneRect(0, 0, w, h)
		#
		self.image = self.pixmap.toImage()
		self.setIsAllGray()
		self.npImage = qimage2np(self.image)
		if self.isAllGray and (len(self.npImage.shape) == 3):   # gray and 3D ?
			self.npImage = self.npImage[:,:,0]
		#
		self.status.setText( f"pixmap: (w,h) = ({w},{h})" )
		self.scaleOne() 
		return
	#end function pixmap2image2np
		
	def np2image2pixmap(self, B, numpyAlso=True):
		"""Copy image 'B' (numpy array) to 'self.image' and to 'self.pixmap'.
		If argument 'numpyAlso' is True (default) 'self.npImage' is set to 'B'.
		"""
		if not isinstance(B, np.ndarray):
			print("np2image2pixmap: argument 'B' is not numpy array.")
			return
		#
		self.image = np2qimage(B) 
		if (not self.image.isNull()):
			self.pixmap = QPixmap.fromImage(self.image)
			if self.curItem: 
				self.scene.removeItem(self.curItem)
			self.curItem = QGraphicsPixmapItem(self.pixmap)
			self.scene.addItem(self.curItem)
			self.scene.setSceneRect(0, 0, self.pixmap.width(), self.pixmap.height())
		#
		if numpyAlso:
			self.npImage = B
		#
		self.setIsAllGray()
		return
	#end function np2image2pixmap
	
# Methods for actions on the File-menu
	def openFileDlg(self):
		"""Use the Qt open file name dialog to select an image to open."""
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog     # make dialog appear the same on all systems
		flt = "All jpg files (*.jpg);;All bmp files (*.bmp);;All png files (*.png);;All files (*)"
		(fName, used_filter) = QFileDialog.getOpenFileName(parent=self, caption="Open image file", 
				directory=myPath, filter=flt, options=options)
		self.openFile(fName)
		return
		
	def openFile(self, fName):   
		"""Open the (image) file both as image (QImage) and pixmap (QPixmap).
		The pixmap is added as an item to the graphics scene which is shown in the graphics view.
		The view is scaled to unity.
		"""
		if (fName == ""):
			print( f"MainWindow.openFile( {fName} )  input is empty string" )
		else:
			self.removePixmapItem()
			self.pixmap.load(fName) 
			if self.pixmap.isNull(): 
				self.setWindowTitle( f"MainWindow.openFile: error for file {fName}" )  
			else:
				self.setWindowTitle( f"{self.appFileName} : {fName}" )
				self.pixmap2image2np()
		# end if
		self.setMenuItems() 
		return
	#end function openFile
	
	def saveFileDlg(self):
		"""Use the Qt save file name dialog to select file to save image into."""
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog     # make dialog appear the same on all systems
		flt = "All jpg files (*.jpg);;All bmp files (*.bmp);;All png files (*.png);;All files (*)"
		(fName, used_filter) = QFileDialog.getSaveFileName(parent=self, caption="Save image file as", 
				directory=myPath, filter=flt, options=options)
		self.saveFile(fName)
		return
	#end function saveFileDlg
		
	def saveFile(self, fName):   
		"""Save the current image into file given by 'fName'."""
		if (fName != ""):
			if self.pixmap.save(fName):
				print(f"Saved pixmap image into file {fName}")
				self.setWindowTitle(f"{self.appFileName} : {fName}")
			else:
				print("Failed to save pixmap image into file {fName}")
			#end if
		#end if  
		return
	#end function saveFile
		
	def removePixmapItem(self):
		"""Removes the current pixmap from the scene if it exists."""
		if self.curItem: 
			self.prevPixmap = self.pixmap
			self.scene.removeItem(self.curItem)
			self.curItem = None
		self.setWindowTitle(self.appFileName)
		self.status.setText('No pixmap (image) on scene.')
		self.setMenuItems()
		return
	#end function removePixmapItem
	
	def printInfo(self):
		"""Print some general (debug) information for the program and the image."""
		print( "Print some elements of MainWindow(QMainWindow) object.")
		print( f"myPath             = {str(myPath)}" )
		print( f"self               = {str(self)}" )
		print( f"  .parent()          = {str(self.parent())}" )
		print( f"  .appFileName       = {str(self.appFileName)}" )
		print( f"  .pos()             = {str(self.pos())}" )
		print( f"  .size()            = {str(self.size())}" )
		print( f"  .isAllGray         = {str(self.isAllGray)}" )
		print( f"  .cropActive        = {str(self.cropActive)}" )
		print( f"  .scaleUpFactor     = {str(self.scaleUpFactor)}" )
		print( f"  .curItem           = {str(self.curItem)}" )
		if isinstance(self.curItem, QGraphicsPixmapItem):
			print( f"    .parentWidget()    = {str(self.curItem.parentWidget())}" )
			print( f"    .parentObject()    = {str(self.curItem.parentObject())}" )
			print( f"    .parentItem()      = {str(self.curItem.parentItem())}" )
		#
		print( f"self.view          = {str(self.view)}" )
		print( f"  .parent()          = {str(self.view.parent())}" )
		print( f"  .scene()           = {str(self.view.scene())}" )
		print( f"  .pos()             = {str(self.view.pos())}" )
		print( f"  .size()            = {str(self.view.size())}" )
		t = self.view.transform()
		print( f"  .transform()       = {str(t)}" )
		print( f"    .m11, .m12, .m13   = [{t.m11():5.2f}, {t.m12():5.2f}, {t.m13():5.2f}, " )
		print( f"    .m21, .m22, .m23   =  {t.m21():5.2f}, {t.m22():5.2f}, {t.m23():5.2f}, " )
		print( f"    .m31, .m32, .m33   =  {t.m31():5.2f}, {t.m32():5.2f}, {t.m33():5.2f} ]" )
		print( f"self.scene         = {str(self.scene)}" )
		print( f"  .parent()          = {str(self.scene.parent())}" )
		print( f"  .sceneRect()       = {str(self.scene.sceneRect())}" )
		print( f"  number of items    = {len(self.scene.items())}" )
		if len(self.scene.items()):
			print( f"  first item         = {str(self.scene.items()[0])}" )
		print( f"self.pixmap        = {str(self.pixmap)}" )
		if not self.pixmap.isNull():
			print( f"  .size()            = {str(self.pixmap.size())}" )
			print( f"  .width()           = {str(self.pixmap.width())}" )
			print( f"  .height()          = {str(self.pixmap.height())}" )
			print( f"  .depth()           = {str(self.pixmap.depth())}" )
			print( f"  .hasAlpha()        = {str(self.pixmap.hasAlpha())}" ) 
			print( f"  .isQBitmap()       = {str(self.pixmap.isQBitmap())}" )
		#end if pixmap
		print( f"self.prevPixmap    = {str(self.prevPixmap)}" )
		print( f"self.image         = {str(self.image)}" )
		if not self.image.isNull():
			if (self.image.format() == 3):
				s2 = "3 (QImage.Format_Indexed8)"
			elif (self.image.format() == 4):
				s2 = "4 (QImage.Format_RGB32)"
			elif (self.image.format() == 5):
				s2 = "5 (QImage.Format_ARGB32)"
			else:
				s2 = "{self.image.format()}" 
			#end
			print( f"  .size()            = {str(self.image.size())}" )
			print( f"  .width()           = {str(self.image.width())}" )
			print( f"  .height()          = {str(self.image.height())}" )
			print( f"  .depth()           = {str(self.image.depth())}" )
			print( f"  .hasAlphaChannel() = {str(self.image.hasAlphaChannel())}" )
			print( f"  .format()          = {s2}" )
			print( f"  .allGray()         = {str(self.image.allGray())}" )
		#end if image
		if isinstance(self.npImage, np.ndarray):   # also print information on this numpy array
			print( (f"self.npImage()       = "
			        f"numpy {len(self.npImage.shape)}D array " + 
			        f"of {self.npImage.dtype.name}, shape {str(self.npImage.shape)}") )
		return
	
	def quitProgram(self):
		"""Quit program."""
		print( "Close the main window and quit program." )
		self.close()   # the correct way to quit, is as (upper right) window frame symbol "X" 
		return
		
# Methods for actions on the Scale-menu, which modify the view transform
	def scaleOne(self):
		"""Scale to 1, i.e. set the transform to identity matrix"""
		if not self.pixmap.isNull():
			self.view.setTransform(QTransform())  # identity
		return
	
	def scaleUp(self):
		"""Scale up the view by factor set by 'self.scaleUpFactor'"""
		if not self.pixmap.isNull():
			self.view.scale(self.scaleUpFactor, self.scaleUpFactor)  
		return
		
	def scaleDown(self):
		"""Scale down the view by factor set by 1.0/'self.scaleUpFactor'"""
		if not self.pixmap.isNull():
			self.view.scale(1.0/self.scaleUpFactor, 1.0/self.scaleUpFactor)  
		return
	
# Methods for actions on the Edit-menu
	def cropStart(self):
		"""Set crop active and turn rubber band on."""
		self.cropActive = True
		self.view.rubberBandActive = True
		self.setMenuItems()
		print("MainWindow.cropStart(): Use rubber band to indicate the rectangle to keep, or just click to cancel crop.")
		return
		
	def cropEnd(self, rectangle):
		"""Crop the current pixmap using the input rectangle (in image pixels).
		
		A (hidden) functionality is included. If the rectangle is small, a special 
		function is performed on image: A black frame, if it is present, is cut out.
		It would be more user friendly (intuitive) if this functionality was behind
		a new action in the menu system. 
		To crop a (very) small rectangle should do nothing.
		"""
		if not self.cropActive: 
			return
		#
		self.cropActive = False
		p2 = rectangle.topLeft()
		p3 = rectangle.bottomRight()
		(w, h) = (rectangle.width(), rectangle.height())
		if (w > 5) and (h > 5):
			print( (f"cropImage(): Rectangle from (x,y)=({p2.x()},{p2.y()})" +
			        f" and (w,h)=({w},{h})") )
			self.prevPixmap = self.pixmap
			self.pixmap = self.prevPixmap.copy(p2.x(), p2.y(), w, h)
			self.pixmap2image2np()
			self.setWindowTitle( f"{self.appFileName} : cropped image" )
		else: 
			A = self.npImage   # just use a short name for image in this part of program
			print( "cropImage(): Rubber band rectangle is small  --> Special case")
			print( "  Cut out any frame of black rows and columns.")
			print( f"  A = npImage is an array of {A.dtype.name}, shape {str(A.shape)}." )
			# find what to crop,  
			(left,right,top,bottom) = (0,0,0,0)
			if (len(A.shape) == 3) and (A.shape[2] >= 3):  # color img
				print("  This is a color image")
				for column in range(0,A.shape[1]):
					if ((A[:,column,0].max() > 0) or 
						(A[:,column,1].max() > 0) or 
						(A[:,column,2].max() > 0)): break
					else: left += 1
				for column in range(A.shape[1]-1,-1,-1):
					if ((A[:,column,0].max() > 0) or 
						(A[:,column,1].max() > 0) or 
						(A[:,column,2].max() > 0)): break
					else: right += 1
				for row in range(0,A.shape[0]):
					if ((A[row,:,0].max() > 0) or 
						(A[row,:,1].max() > 0) or 
						(A[row,:,2].max() > 0)): break
					else: top += 1
				for row in range(A.shape[0]-1,-1,-1):
					if ((A[row,:,0].max() > 0) or 
						(A[row,:,1].max() > 0) or 
						(A[row,:,2].max() > 0)): break
					else: bottom += 1
				print( f"  end using   (left,right,top,bottom) = ({left},{right},{top},{bottom})" )
			else:  # grayscale img
				print( "  This is a gray scale image")
				print( "  start using (left,right,top,bottom) = ({left},{right},{top},{bottom})" )
				for column in range(0, A.shape[1]):
					if (A[:,column].max() > 0): break
					else: left += 1
				for column in range(A.shape[1]-1,-1,-1):
					if (A[:,column].max() > 0): break
					else: right += 1
				for row in range(0,A.shape[0]):
					if (A[row,:].max() > 0): break
					else: top += 1
				for row in range(A.shape[0]-1,-1,-1):
					if (A[row,:].max() > 0): break
					else: bottom += 1
				print( f"  end using   (left,right,top,bottom) = ({left},{right},{top},{bottom})" )
			# 
			w = A.shape[1] - left - right
			h = A.shape[0] - top - bottom
			if max((left,right,top,bottom)):
				if (w <= 0) or (h <= 0):
					print( ("cropImage(): Don't crop since (left,right,top,bottom)" +
					        f" = ({left},{right},{top},{bottom})") )
				else:
					print( ("cropImage(): Crop outside of rectangle from (x,y)" +
					        f"=({left},{top}) and (w,h)=({w},{h})") )
					self.prevPixmap = self.pixmap 
					if (len(A.shape) == 3) and (A.shape[2] >= 3):  # color img
						print("cropImage(): Crop color")
						B = A[top:top+w,left:left+w,:].copy() 
						self.np2image2pixmap(B, numpyAlso=True)
					else:
						print("cropImage(): Crop gray")
						B = A[top:top+w,left:left+w].copy()
						self.np2image2pixmap(B, numpyAlso=True)
					self.setWindowTitle( f"{self.appFileName} : Black frame cut from image" )
					self.setIsAllGray()
			else:
				print( "cropImage(): No black rows or black columns to crop." )
			#
		# 
		self.setMenuItems()
		return
	#end function cropImage
	
	def resizeImage(self):
		"""Resize the current numpy color or gray scale image
		and copy (move) it back to current pixmap
		"""
		B = self.npImage
		oldPixmap = self.prevPixmap
		self.prevPixmap = self.pixmap
		d = ResizeDialog(parent=self)   # create object (but does not run it)
		(newWidth, newHight) = d.getValues()   # display dialog and return values
		if d.result():   # 1 if accepted (OK), 0 if rejected (Cancel)
			B = cv2.resize(B, (newWidth, newHight), interpolation= cv2.INTER_LINEAR)
			self.np2image2pixmap(B, numpyAlso=True)
			(w, h) = (self.pixmap.width(), self.pixmap.height())
			self.scene.setSceneRect(0, 0, w, h)
			self.status.setText( f"pixmap: (w,h) = ({w},{h})" )
			self.setWindowTitle( f"{self.appFileName} : resized image" )
		else:
			self.prevPixmap = oldPixmap
		# 
		self.setMenuItems()
		return
		
	def toGray(self):
		"""Convert the current numpy color image into a gray scale image
		and copy (move) it back to current pixmap
		"""
		if (len(self.npImage.shape) == 3) and (self.npImage.shape[2] >= 3):
			self.prevPixmap = self.pixmap
			if (self.npImage.shape[2] == 3):
				B = cv2.cvtColor(self.npImage, cv2.COLOR_BGR2GRAY)
			if (self.npImage.shape[2] == 4):
				B = cv2.cvtColor(self.npImage, cv2.COLOR_BGRA2GRAY)
			self.np2image2pixmap(B, numpyAlso=True)
			self.setWindowTitle( f"{self.appFileName} : gray scale image" )
		else:
			print( "toGray: npImage is (most likely already) a gray scale image." )
		#
		self.setMenuItems()
		print( (f"toGray: npImage is an array of {self.npImage.dtype.name}," + 
		        f" shape {str(self.npImage.shape)}.") )
		return 
	#end function toGray
	
	# Note that edge dialog is in another file: clsEdgeDialog.py
	def tryEdges(self, valK, valS):
		"""This method may be started from the edge dialog 
		to (quickly) show results of new edge filter values.
		"""
		B = self.npImage
		# B = cv2.GaussianBlur(B, 11, 2.5)  # sizeK and sigma ??
		# Eh = cv2.Sobel(B, ddepth=cv2.CV_16S, dx=0, dy=1, ksize=valK)
		# Ev = cv2.Sobel(B, ddepth=cv2.CV_16S, dx=1, dy=0, ksize=valK)
		# Eh = Eh.astype(np.float32)
		# Ev = Ev.astype(np.float32) 
		Eh = cv2.Sobel(B, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=valK)
		Ev = cv2.Sobel(B, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=valK)
		# print( f"tryEdges: Eh is an array of {Eh.dtype.name}, shape {str(Eh.shape)}" )
		B = np.sqrt( 1 + np.power(Eh,2) + np.power(Ev,2) )
		# B = cv2.Sobel(B, ddepth=cv2.CV_16S, dx=1, dy=1, ksize=valK)  # hmmm
		if (valS > 1):
			a = smoothFilter(len=valS)
			B = cv2.sepFilter2D(B, ddepth=-1, kernelX=a, kernelY=a)
		B = np.floor(B * (255/np.max(B))).astype(np.uint8)
		self.np2image2pixmap(B, numpyAlso=False)   # note: self.npImage is not updated
		return
	#end function tryEdges()
		
	def toEdges(self):
		"""Show the edge dialog, and process the (gray scale) image 
		according to the values returned from the dialog.
		Use Sobel filters and separable low-pass filter and find edges.
		Result is put into 'self.image' and 'self.pixmap'
		"""
		B = self.npImage
		oldPixmap = self.prevPixmap
		self.prevPixmap = self.pixmap
		d = EdgeDialog(parent=self)   # create object (but does not run it)
		(valK,valS) = d.getValues()   # display dialog and return values
		if d.result():   # 1 if accepted (OK), 0 if rejected (Cancel)
			Eh = cv2.Sobel(B, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=valK)
			Ev = cv2.Sobel(B, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=valK)
			B = np.sqrt( 1 + np.power(Eh,2) + np.power(Ev,2) )
			if (valS > 1):
				a = smoothFilter(len=valS)
				B = cv2.sepFilter2D(B, ddepth=-1, kernelX=a, kernelY=a)
			# print( f"toEdges: B is an array of {B.dtype.name}, shape {str(B.shape)}" )
			# print( f"         min(B) {np.min(B):8.2f},  max(B) {np.max(B):8.2f}" )
			B = np.floor(B * (255/np.max(B))).astype(np.uint8)
			self.np2image2pixmap(B, numpyAlso=True)
			self.setWindowTitle( f"{self.appFileName} : edge image" )
		else:
			self.pixmap = self.prevPixmap   # restore 
			self.pixmap2image2np()
			self.prevPixmap = oldPixmap
		#
		self.setMenuItems()
		return
	#end function toEdges()
		
	# Note that filter dialog is in another file: clsFilterDialog.py
	def tryFilter(self, h, valS):
		"""This method may be started from the filter dialog 
		to (quickly) show results of new filter values.
		"""
		if (len(h) > 1):
			B = cv2.filter2D(self.npImage, ddepth=cv2.CV_16S, kernel=h).astype(np.float32) 
		else:
			B = self.npImage.astype(np.float32)
		if (valS > 1):
			a = smoothFilter(len=valS)
			B = cv2.sepFilter2D(B, ddepth=-1, kernelX=a, kernelY=a)
		B = B - np.min(B)
		B = np.floor(B * (255/np.max(B))).astype(np.uint8)
		self.np2image2pixmap(B, numpyAlso=False)   # note: self.npImage is not updated
		return
	#end function tryFilter()
		
	def filterImage(self):  # filter (gray scale) image, use FilterDialog to get filter
		"""Show the filter dialog, and filter the (gray scale) image 
		according to the values returned from the dialog.
		OpenCV function cv2.filter2D(..) do the actual work.
		Result is put into 'self.image' and 'self.pixmap'
		"""
		B = self.npImage
		oldPixmap = self.prevPixmap
		self.prevPixmap = self.pixmap   
		d = FilterDialog(parent=self)   # create object (but does not run it)
		(h,valS) = d.getValues()   # display dialog and return values
		if d.result():   # 1 if accepted (OK), 0 if rejected (Cancel)
			if (len(h) > 1):
				B = cv2.filter2D(B, ddepth=cv2.CV_16S, kernel=h).astype(np.float32)
			else:
				B = self.npImage.astype(np.float32)
			if (valS > 1):
				a = smoothFilter(len=valS)
				B = cv2.sepFilter2D(B, ddepth=-1, kernelX=a, kernelY=a)
			B = B - np.min(B)
			B = np.floor(B * (255/np.max(B))).astype(np.uint8)
			self.np2image2pixmap(B, numpyAlso=True)
			self.setWindowTitle( f"{self.appFileName} : filtered image" ) 
		else:
			self.pixmap = self.prevPixmap   # restore 
			self.pixmap2image2np()
			self.prevPixmap = oldPixmap
		#
		self.setMenuItems()
		return
	#end function filterImage()
		
	# Note that threshold dialog is in another file: clsThresholdDialog.py
	def tryBinary(self, t=0):
		"""This method may be started from the threshold dialog 
		to (quickly) show results of threshold 't'.
		"""
		B = self.npImage
		if (t < 2):
			(used_thr,B) = cv2.threshold(B, thresh=1, maxval=255, type=cv2.THRESH_OTSU)
			print( f"tryBinary: The used Otsu threshold value is {used_thr}" ) 
		else:
			(used_thr,B) = cv2.threshold(B, thresh=t, maxval=255, type=cv2.THRESH_BINARY)
		#
		self.np2image2pixmap(B, numpyAlso=False)   # note: self.npImage is not updated
		return
	#end function tryBinary()
	
	def toBinary(self):
		"""Show the threshold dialog, and convert gray scale image 
		to a binary image using the returned threshold.
		The current gray scale image, stord in a numpy array, is processed in OpenCV
		and result is put into 'self.image' and 'self.pixmap'
		"""
		B = self.npImage
		oldPixmap = self.prevPixmap
		self.prevPixmap = self.pixmap   
		d = ThresholdDialog(parent=self)   # create object (but does not run it)
		t = d.getValues()   # display dialog and return values
		if d.result():   # 1 if accepted (OK), 0 if rejected (Cancel)
			if (t < 2):
				(used_thr,B) = cv2.threshold(B, thresh=1, maxval=255, type=cv2.THRESH_OTSU)
			else:
				(used_thr,B) = cv2.threshold(B, thresh=t, maxval=255, type=cv2.THRESH_BINARY)
			#
			print( f"toBinary: The used threshold value is {used_thr}" )
			self.np2image2pixmap(B, numpyAlso=True)
			self.setWindowTitle( f"{self.appFileName} : binary image" )
		else:
			self.pixmap = self.prevPixmap   # restore 
			self.pixmap2image2np()
			self.prevPixmap = oldPixmap
		#
		self.setMenuItems()
		return
	#end function toBinary()
		
	# Note that dialog is in another file: clsHoughLinesDialog.py
	def tryHoughLines(self, t):
		"""This method may be started from the HoughLines dialog 
		to (quickly) show results of parameters in tuple t.
		"""
		B = self.npImage
		print("tryHoughLines(): now called using:")
		if (B.ndim == 2):
			imgBGR = cv2.cvtColor(B, cv2.COLOR_GRAY2BGR)
		else:
			imgBGR = B.copy()
		#
		if (len(t) == 5):
			(rho, theta, threshold, nofLines, distLines) = t
			print( f"argument t = ({rho=}, {theta=}*pi/180, {threshold=})" )
			linesFound = cv2.HoughLines(B, rho=rho, theta=theta*np.pi/180.0, \
					threshold=threshold)
		elif (len(t) == 7): 
			(rho, theta, threshold, minLineLength, maxLineGap, nofLines, distLines) = t
			print( f"argument t = ({rho=}, {theta=}*pi/180, {threshold=}, " + \
			       f"{minLineLength=}, {maxLineGap=})" )
			linesFound = cv2.HoughLinesP(B, rho=rho, theta=theta*np.pi/180.0, \
					threshold=threshold, minLineLength=minLineLength, \
					maxLineGap=maxLineGap)
		else:
			print( "tryHoughLines: argument 't', dialog response, has not expected length." )
			linesFound = None
		#
		if isinstance(linesFound, np.ndarray):
			draw_lines(linesFound, imgBGR)
			self.np2image2pixmap(imgBGR, numpyAlso=False)
			self.setWindowTitle( f"{self.appFileName} : Find lines and [Try it]-button. " + \
					f"All the {linesFound.shape[0]} found lines are shown." )
		# 
		return
	#end function tryHoughLines()
	
	def findHoughLines(self):
		"""Show the HoughLines dialog, and indicate where lines where found.
		The current binary image, stored in a numpy array, is processed in OpenCV
		and result is put into 'self.image' and 'self.pixmap'
		"""
		B = self.npImage
		oldPixmap = self.prevPixmap
		self.prevPixmap = self.pixmap   
		d = HoughLinesDialog(self)
		t = d.getValues()   # display dialog and return values
		if d.result():   # 1 if accepted (OK), 0 if rejected (Cancel)
			if (B.ndim == 2):
				imgBGR = cv2.cvtColor(B, cv2.COLOR_GRAY2BGR)
			else:
				imgBGR = B.copy()
			#
			if (len(t) == 5):
				(rho, theta, threshold, nofLines, distLines) = t
				print( f"Should do HoughLines({rho=:.2f}, {theta=:.2f}*pi/180, {threshold=})" )
				linesFound = cv2.HoughLines(B, rho=rho, theta=theta*np.pi/180.0, \
						threshold=threshold)
			elif (len(t) == 7): 
				(rho, theta, threshold, minLineLength, maxLineGap, nofLines, distLines) = t
				print( f"Should do HoughLinesP({rho=:.2f}, {theta=:.2f}*pi/180, {threshold=}, " + \
					   f"{minLineLength=:.2f}, {maxLineGap=:.2f})" )
				linesFound = cv2.HoughLinesP(B, rho=rho, theta=theta*np.pi/180.0, \
						threshold=threshold, minLineLength=minLineLength, \
						maxLineGap=maxLineGap)
			else:
				print( "findHoughLines: dialog response 't'  has not expected length." )
				linesFound = None
			#
			if isinstance(linesFound, np.ndarray):
				print( f"{linesFound.shape = }, {linesFound.ndim = }" )
				# 
				# apply nofLines and distLines to show only some of the found lines
				if (distLines <= 0.0):  
					linesToDraw = linesFound[:nofLines] 
				else:
					# should sort lines by importance and remove lines close to each other
					linesToDraw = getBestHoughLines(linesFound, B, nofLines, distLines)
				#
				draw_lines(linesToDraw, imgBGR)
				#
				self.np2image2pixmap(imgBGR, numpyAlso=True)
				self.setWindowTitle( f"{self.appFileName} : Find lines " + \
						f"shows {linesToDraw.shape[0]} lines, " + \
						f"found {linesFound.shape[0]} lines." )
			else:
				self.setWindowTitle( f"{self.appFileName} : Unexpected result from HoughLines." )
				self.np2image2pixmap(B, numpyAlso=True)
		else:
			self.pixmap = self.prevPixmap   # restore 
			self.pixmap2image2np()
			self.prevPixmap = oldPixmap
		#
		self.setMenuItems()
		return
	#end function findHoughLines()
		
	def undoLast(self):
		"""Undo last (edit) operation."""
		(w, h) = (self.prevPixmap.width(), self.prevPixmap.height())
		if (w > 0) and (h > 0):
			self.pixmap.swap(self.prevPixmap)  
			self.pixmap2image2np()
			self.setWindowTitle( f"{self.appFileName} : previous image" )
		# 
		self.setMenuItems()
		return
	#end function undoLast
	
# Finally, some methods used as slots for common actions
	def resizeEvent(self, arg1):
		"""Make the size of the view follow any changes in the size of the main window.
		This method is a 'slot' that is called whenever the size of the main window changes.
		"""
		self.view.setGeometry( 0, 20, self.width(), self.height()-50 ) 
		self.status.setGeometry(5, self.height()-29, (self.width()//2)-10, 28) 
		self.posInfo.setGeometry((self.width()//2)+5, self.height()-29, (self.width()//2)-10, 28) 
		return
	
	def mousePressEvent(self, event):
		"""Just print which mouse button has been pressed in the main window.
		Note that the view catches most mouse events, so this does only happen
		when mouse is on the bottom of the main window; the status line.
		Normally we are fine if this function does nothing (is not included here).
		This method is a 'slot' that is called whenever a mouse button is pressed 
		(in the main window).
		"""
		if (event.button() == Qt.LeftButton):
			print("MainWindow: Press LeftButton at:  " + str(event.pos()))
		if (event.button() == Qt.RightButton):
			print("MainWindow: Press RightButton at: " + str(event.pos()))
		return
	#end function mousePressEvent

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

