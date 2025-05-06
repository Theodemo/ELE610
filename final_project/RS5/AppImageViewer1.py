# My own image viewer app

_appFileName = "ImageViewer"
_author = "Théo de Morais" 
_version = "2025.01.31"

import sys
import os.path
import numpy as np
import cv2
import matplotlib.pyplot as plt
from pyzbar.pyzbar import decode


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
from utils.clsThresholdDialog import ThresholdDialog
from utils.clsResizeDialog import ResizeDialog

#
# some simple methods for image processing
from utils.myImageTools import smoothFilter, qimage2np, np2qimage


myPath = "C:\Raph Stockage\Courses\Applied Robot Technology\Assignment\Images"		# path where the images are stored



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
            # print( "MyGraphicsView.mousePressEvent: Press LeftButton at:  ", end='') 
            self.pos1 = event.pos()
            if self.rubberBandActive:
                self.rubberBand.setGeometry(QRect(event.pos(), QSize()))
                self.rubberBand.show()
        # if (event.button() == Qt.RightButton):
            # print( "MyGraphicsView.mousePressEvent: Press RightButton at: ", end='')
        # print( f"{str(event.pos())}, in scene at (x,y) = ({x},{y})" )
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
            # print("MyGraphicsView.mouseReleaseEvent():  Button pressed and released")
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
        self.setGeometry(150, 50, 1400, 800 )  # initial window position and size
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
        
        
        a = self.qaFlipImage = QAction('Flip image', self)
        a.setShortcut('Ctrl+F')
        a.triggered.connect(self.flip_image)
        #
        a = self.qaCrop = QAction('Crop image', self)
        a.triggered.connect(self.cropStart)
        a.setToolTip('Crop the current pixmap, start by indicating rectangle to keep.')
        a.setShortcut('Ctrl+Y')  # as in IrfanView
        a = self.qaResize = QAction('Resize image', self)
        a.triggered.connect(self.resizeImage)
        a.setToolTip('Resize the current npImage (and pixmap)')
        a.setShortcut('Ctrl+R')  # as in IrfanView
        #
        #
        a = self.qaToGray = QAction('to Gray', self)
        a.triggered.connect(self.toGray)
        a.setToolTip('Convert the current (numpy) BGR image to gray scale, and display it as pixmap.')
        a.setShortcut('Ctrl+G')
       
        a = self.qaToBinary = QAction('to Binary', self)
        a.triggered.connect(self.toBinary)
        a.setToolTip('Threshold image to make binary image.')
        a.setShortcut('Ctrl+B')
        
        a = self.qaToContrast = QAction('Increase contrast', self)
        a.triggered.connect(self.increaseContrast)
        a.setToolTip('Increase contrast of the image')
        a.setShortcut('Ctrl+K')
        
        a = self.qaToNoise = QAction('Reduce noise', self)
        a.triggered.connect(self.reduceNoise)
        a.setToolTip('Reduce noise in the image')
        a.setShortcut('Ctrl+N')
        
        a = self.qaToQRcode = QAction('Detect QR code', self)
        a.triggered.connect(self.detectQRCodeCenter)
        a.setToolTip('Detect QR code(s) in the image')
        a.setShortcut('Ctrl+D')
        #
        #
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
        editMenu.addAction(self.qaUndoLast)
        editMenu.addAction(self.qaFlipImage)

        editMenu.setToolTipsVisible(True)
        #
        functionMenu = self.mainMenu.addMenu('&Function')
        functionMenu.addAction(self.qaToGray)
        functionMenu.addAction(self.qaToBinary)
        functionMenu.addAction(self.qaToContrast)
        functionMenu.addAction(self.qaToNoise)
        functionMenu.addAction(self.qaToQRcode)
        functionMenu.setToolTipsVisible(True)

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
        self.qaFlipImage.setEnabled(pixmapOK)
        #
        self.qaCrop.setEnabled(pixmapOK and (not self.cropActive))
        self.qaResize.setEnabled(pixmapOK and (not self.cropActive))
        self.qaUndoLast.setEnabled(not self.prevPixmap.isNull())
        #
        self.qaToGray.setEnabled(pixmapOK and (not self.isAllGray))
        self.qaToBinary.setEnabled(pixmapOK and self.isAllGray)
        self.qaToContrast.setEnabled(pixmapOK and (not self.isAllGray))
        self.qaToNoise.setEnabled(pixmapOK)
        self.qaToQRcode.setEnabled(pixmapOK)
        
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
        """Open an image or play a video file."""
        if not fName:
            print(f"MainWindow.openFile({fName}) input is empty string")
            return

        file_extension = os.path.splitext(fName)[-1].lower()

        if file_extension in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
            # Open image
            self.removePixmapItem()
            self.pixmap.load(fName)
            if self.pixmap.isNull():
                self.setWindowTitle(f"MainWindow.openFile: error for file {fName}")
            else:
                self.setWindowTitle(f"{self.appFileName} : {fName}")
                self.pixmap2image2np()
            self.setMenuItems()

        elif file_extension in [".avi", ".mp4", ".mov", ".mkv"]:
            # Play video
            self.play_video(fName)

        else:
            print(f"Unsupported file format: {fName}")
   
    def play_video(self, video_path):
        """Play a video inside the QGraphicsView by updating QPixmap."""
        if not os.path.exists(video_path):
            print(f"File not found: {video_path}")
            return

        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print("Error: Could not open video.")
            return

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break  # Stop when video ends

            # Convert frame to QImage
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            bytes_per_line = channel * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # Convert QImage to QPixmap and set it in the scene
            self.pixmap = QPixmap.fromImage(q_img)
            if self.curItem:
                self.scene.removeItem(self.curItem)
            self.curItem = QGraphicsPixmapItem(self.pixmap)
            self.scene.addItem(self.curItem)

            # Process Qt events to update UI
            QApplication.processEvents()

        cap.release()



    #end function openFile
    
    def saveFileDlg(self):
        """Use the Qt save file name dialog to select file to save image into."""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog  # Make dialog appear the same on all systems
        flt = "JPG files (*.jpg);;BMP files (*.bmp);;PNG files (*.png);;All files (*)"
        fName, used_filter = QFileDialog.getSaveFileName(self, "Save image file as", "", flt, options=options)
        
        if fName:
            self.saveFile(fName)
        return

    def saveFile(self, fName):   
        """Save the current image into file given by 'fName'."""
        if not fName:
            print("No file name provided.")
            return

        if self.pixmap is None or self.pixmap.isNull():
            print("Error: No valid image loaded in pixmap.")
            return

        file_format = fName.split(".")[-1].upper()  # Extract format (e.g., JPG, PNG)
        # print(self.pixmap.save(fName, file_format))
        
        if self.pixmap.save(fName):
            print(f"Saved pixmap image into file {fName}")
            self.setWindowTitle(f"{self.appFileName} : {fName}")
        else:
            print(f"Failed to save pixmap image into file {fName}")

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
    
    def flip_image(self):
        """
        Flip the image upside down for the robot purpose.
        """
        flipped_pixmap = self.pixmap.transformed(QTransform().scale(1, -1))
        self.curItem.setPixmap(flipped_pixmap)
        # Flip the NumPy image vertically
        self.npImage = np.flipud(self.npImage)

    
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

# Methods for actions on the Function-menu	
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
        # print( (f"toGray: npImage is an array of {self.npImage.dtype.name}," + 
        #         f" shape {str(self.npImage.shape)}.") )
        return 
    #end function toGray
    
    
        
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
    
    def increaseContrast(self):
        """Increase the contrast of the current image using YUV method."""
        if (len(self.npImage.shape) == 3) and (self.npImage.shape[2] >= 3):
            yuv_image = cv2.cvtColor(self.npImage, cv2.COLOR_BGR2YUV)
            yuv_image[:, :, 0] = cv2.multiply(yuv_image[:, :, 0], 1.5)
            np.clip(yuv_image[:, :, 0], 0, 255, out=yuv_image[:, :, 0])
            contrast_image = cv2.cvtColor(yuv_image, cv2.COLOR_YUV2BGR)
            self.np2image2pixmap(contrast_image, numpyAlso=True)
            self.setWindowTitle(f"{self.appFileName} : contrast increased")
        else:
            print("increaseContrast: Unsupported image format or already grayscale.")
        return
    
    def reduceNoise(self):
        """Reduce noise in the current image using bilateral filter."""
        B = cv2.bilateralFilter(self.npImage, d=9, sigmaColor=75, sigmaSpace=75)
        self.np2image2pixmap(B, numpyAlso=True)
        self.setWindowTitle(f"{self.appFileName} : noise reduced")
        return
    
    def detectQRCodeCenter(self):
        """Try to detect QR code and show its center on the image."""
        decoded_objects = decode(self.npImage)
        centers = []
        if not decoded_objects:
            print("detectQRCodeCenter: No QR code found.")
            return None

        # We assume only one QR code is present for simplicity
        for obj in decoded_objects:
            points = obj.polygon
            if len(points) == 4:
                cx = sum(p.x for p in points) / 4
                cy = sum(p.y for p in points) / 4
                center = (int(cx), int(cy))
                print(f"detectQRCodeCenter: QR center at {center}")
                # Optionally draw
                pts = np.array([(p.x, p.y) for p in points], dtype=np.int32)
                cv2.polylines(self.npImage, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
                cv2.circle(self.npImage, center, radius=5, color=(255, 0, 255), thickness=-1)
                self.np2image2pixmap(self.npImage, numpyAlso=False)
                centers.append(center)
        # print(centers)
        return centers

        
    
    
# Finally, some methods used as slots for common actions
    def resizeEvent(self, arg1):
        """Make the size of the view follow any changes in the size of the main window.
        This method is a 'slot' that is called whenever the size of the main window changes.
        """
        self.view.setGeometry( 0, 20, self.width(), self.height()-50 ) 
        self.status.setGeometry(5, self.height()-29, (self.width()//2)-10, 28) 
        self.posInfo.setGeometry((self.width()//2)+5, self.height()-29, (self.width()//2)-10, 28) 
        return
    


#end class MainWindow
        
if __name__ == '__main__':
    # print( f"{_appFileName}: (version {_version}), path for images is: {myPath}" )
    # print( f"{_appFileName}: Using Qt {QT_VERSION_STR}" )
    print("Launching the app...")
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

