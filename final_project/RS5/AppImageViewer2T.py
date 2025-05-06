_appFileName = "ImageViewer"
_author = "Théo de Morais" 
_version = "2025.02.6"

import sys
import os.path
import numpy as np
import cv2
import random
import time

try:
    from PyQt5.QtGui import QImage, QPixmap
    from PyQt5.QtWidgets import (QApplication, QAction,QGraphicsPixmapItem, QDialog)
except ImportError:
    raise ImportError( f"{_appFileName}: Requires PyQt5." )

try:
    from pyueye import ueye
    from utils.pyueye_example_camera import Camera
    from utils.pyueye_example_utils import ImageData, ImageBuffer
    ueyeOK = True
except ImportError:
    ueye_error = f"{_appFileName}: Requires IDS pyueye example files (and IDS camera)." 
    ueyeOK = False  

from AppImageViewer1 import myPath, MainWindow as inheritedMainWindow 
from utils.myImageTools import np2qimage
from utils.camLuminosityDialog import LuminosityDialog
from utils.camPropertiesDialog import CamPropertiesDialog

class MainWindow(inheritedMainWindow):  
    """MainWindow class for this image viewer is inherited from another image viewer."""
       
    def __init__(self, fName="", parent=None):
        super().__init__(fName, parent)
        self.appFileName = _appFileName 
        if self.pixmap.isNull(): 
            self.setWindowTitle(self.appFileName)
            self.npImage = np.array([]) 
        else:
            self.setWindowTitle( f"{self.appFileName} : {fName}" ) 
            self.pixmap2image2np()
         
        self.cam = None
        self.camOn = False
        
        self.initMenu2()
        self.setMenuItems2()
        self.fps = 20
        self.exposure_time = 1.5 #ms
        self.width_c = 1280
        self.height_c = 960
        
        
    
    def initMenu2(self):
        a = self.qaCameraOn = QAction('Camera on', self)
        a.triggered.connect(self.cameraOn)
        a = self.qaCameraInfo = QAction('Print camera info', self)
        a.triggered.connect(self.printCameraInfo)
        a = self.qaGetOneImage = QAction('Get one image', self)
        a.setShortcut('Ctrl+N')
        a.triggered.connect(self.getOneImage)
        a  =self.qaFindFocus = QAction('Find Focus', self)
        a.triggered.connect(self.find_focus)
        a = self.qaChangeLum = QAction('Change luminosity', self)
        a.triggered.connect(self.change_lum)
        a = self.qaCamProperties = QAction('Properties', self)
        a.triggered.connect(self.properties_func)
        a = self.qaCameraOff = QAction('Camera off', self)
        a.triggered.connect(self.cameraOff)
        a = self.qaRecordVideo = QAction('Record video', self)
        a.triggered.connect(self.record_video2)

        camMenu = self.mainMenu.addMenu('&Camera')
        camMenu.addAction(self.qaCameraOn)
        camMenu.addAction(self.qaCameraInfo)
        camMenu.addAction(self.qaGetOneImage)
        camMenu.addAction(self.qaFindFocus)
        camMenu.addAction(self.qaChangeLum)
        camMenu.addAction(self.qaCamProperties)
        camMenu.addAction(self.qaRecordVideo)
        camMenu.addAction(self.qaCameraOff)
        return

    def setMenuItems2(self):

        setM = getattr(super(), "setMenuItems", None)
        if callable(setM):
            setM()
        self.qaCameraOn.setEnabled(ueyeOK and (not self.camOn))
        self.qaCameraInfo.setEnabled(ueyeOK and self.camOn)
        self.qaGetOneImage.setEnabled(ueyeOK and self.camOn)
        self.qaCameraOff.setEnabled(ueyeOK and self.camOn)
        self.qaFindFocus.setEnabled(ueyeOK and self.camOn)
        self.qaCamProperties.setEnabled(ueyeOK and self.camOn)
        self.qaRecordVideo.setEnabled(ueyeOK and self.camOn)
        self.qaChangeLum.setEnabled(ueyeOK and self.camOn)
        return
    
    def copy_image(self, image_data):
        tempBilde = image_data.as_1d_image()
        if np.min(tempBilde) != np.max(tempBilde):
            self.npImage = np.copy(tempBilde[:,:,[0,1,2]])
            print( ("copy_image(): 'self.npImage' is an ndarray" + 
                    f" of {self.npImage.dtype.name}, shape {str(self.npImage.shape)}.") )
        else: 
            self.npImage = np.array([])
        image_data.unlock()
        return 
        
    def cameraOn(self):
        if ueyeOK and (not self.camOn):
            self.cam = Camera()
            self.cam.init()
            self.cam.set_colormode(ueye.IS_CM_BGR8_PACKED)
            self.cam.set_aoi(0, 0, 1280, 960)
            self.cam.alloc(3)
            self.camOn = True
            self.setMenuItems2()
            print( f"{self.appFileName}: cameraOn() Camera started ok" )
        #
        return
           
    def printCameraInfo(self):
        if not self.camOn:
            print("Camera is not turned on.")
            return

        d = ueye.double()
        ui1 = ueye.uint()

        retVal = ueye.is_SetFrameRate(self.cam.handle(), ueye.IS_GET_FRAMERATE, d)
        if retVal == ueye.IS_SUCCESS:
            print(f"  Current frame rate: {float(d):8.3f} fps")

        retVal = ueye.is_Exposure(self.cam.handle(), ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, d, 8)
        if retVal == ueye.IS_SUCCESS:
            print(f"  Current exposure time (before change): {float(d):8.3f} ms")

        time.sleep(0.5)

        retVal = ueye.is_Exposure(self.cam.handle(), ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, d, 8)
        if retVal == ueye.IS_SUCCESS:
            print(f"  Current exposure time (after change): {float(d):8.3f} ms")

        retVal = ueye.is_Exposure(self.cam.handle(), ueye.IS_EXPOSURE_CMD_GET_EXPOSURE_RANGE_MIN, d, 8)
        if retVal == ueye.IS_SUCCESS:
            print(f"  Minimum exposure time: {float(d):8.3f} ms")

        retVal = ueye.is_Exposure(self.cam.handle(), ueye.IS_EXPOSURE_CMD_GET_EXPOSURE_RANGE_MAX, d, 8)
        if retVal == ueye.IS_SUCCESS:
            print(f"  Maximum exposure time: {float(d):8.3f} ms")

        return
        
    def find_focus(self):
        if ueyeOK and self.camOn:
            num_images = random.randint(15, 25)
            print(f" Capturing {num_images} images to find focus.")
   
        for i in range(num_images):
            print(f" Capturing image {i + 1} / {num_images}...")
            self.getOneImage()
   
        print(f"{self.appFileName}: FindFocus() - Focus found.")
        return
    
    

    def getOneImage(self):
        if ueyeOK and self.camOn:
            self.view.setMouseTracking(False)
            imBuf = ImageBuffer()
            self.cam.freeze_video(True)
            retVal = ueye.is_WaitForNextImage(self.cam.handle(), 1000, imBuf.mem_ptr, imBuf.mem_id)
            if retVal == ueye.IS_SUCCESS:
                self.copy_image( ImageData(self.cam.handle(), imBuf) )
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
                else:
                    self.image = QImage()
                    self.pixmap = QPixmap()
                    print( "  no image in buffer " + str(imBuf) )
                
            else: 
                self.setWindowTitle( "{self.appFileName}: getOneImage() error retVal = {retVal}" )
            self.setIsAllGray()
            self.setMenuItems2()
        return
    
    
    
    
    def change_lum(self):
        if not ueyeOK or not self.camOn:
            print("Camera is not available or not turned on.")
            return
        
        dialog = LuminosityDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            luminosity_value = dialog.get_luminosity()
            luminosity_value = max(0, min(100, luminosity_value))
            
            retVal = ueye.is_SetHardwareGain(self.cam.handle(), luminosity_value, ueye.IS_IGNORE_PARAMETER, 
                                             ueye.IS_IGNORE_PARAMETER, ueye.IS_IGNORE_PARAMETER)
            if retVal == ueye.IS_SUCCESS:
                print(f"Luminosity set to {luminosity_value}")
            else:
                print("Failed to set luminosity.")
        return
    
    
    def change_expo_time(self):
        if not self.camOn:
            print("Camera is not turned on.")
            return
        
        auto_exposure = ueye.double(0)
        ret = ueye.is_SetAutoParameter(self.cam.handle(), ueye.IS_SET_ENABLE_AUTO_SHUTTER, auto_exposure, None)
        if ret != ueye.IS_SUCCESS:
            print("Warning: Failed to disable auto-exposure. Manual exposure might not work.")

        # Set exposure time
        exp_time = ueye.c_double(self.exposure_time)
        ret = ueye.is_Exposure(self.cam.handle(), ueye.IS_EXPOSURE_CMD_SET_EXPOSURE, exp_time, 8)

        if ret == ueye.IS_SUCCESS:
            print(f"Exposure time successfully set to {exp_time.value} ms")
            time.sleep(0.1)  # Small delay to let the setting take effect

            # Verify the change by reading the exposure time back
            new_exposure = ueye.double()
            ret = ueye.is_Exposure(self.cam.handle(), ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, new_exposure, 8)
            if ret == ueye.IS_SUCCESS:
                print(f"Verified exposure time: {new_exposure.value:.3f} ms")
            else:
                print("Failed to verify the updated exposure time.")
        else:
            print("Failed to set exposure time.")

            
            
    def change_framerate(self):
        """Change the frame rate of the camera."""
        
        new_fps = ueye.c_double(self.fps)
        ret = ueye.is_SetFrameRate(self.cam.handle(), new_fps, new_fps)

        if ret == ueye.IS_SUCCESS:
            print(f"Frame rate set to {new_fps.value} FPS")
        else:
            print("Failed to set frame rate.")
            
            
    def properties_func(self):
        """Opens a dialog to change camera properties (exposure time & frame rate) without closing the main window."""
        
        app = QApplication.instance()
        if app is None:  # Ensure we don't create a new one if it's already running
            app = QApplication([])


        dialog = CamPropertiesDialog(parent=self, current_exposure=self.exposure_time, current_fps=self.fps)
        
        if dialog.exec_():  # Runs modal dialog and waits for user input
            self.exposure_time, self.fps = dialog.get_values()
            print(self.fps, self.exposure_time)
            self.change_expo_time()
            self.change_framerate()
        
    

    def record_video2(self):
        """Record video from the IDS camera and save it as both video and images."""
        if not (ueyeOK and self.camOn):
            print("Camera is not available or not turned on.")
            return
        
        duration = 2  # Video duration in seconds
        save_folder = r"C:\Raph Stockage\Courses\Applied Robot Technology\Assignment_IA\Video"

        # Ensure the save folder exists
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        # Video file path
        video_path = os.path.join(save_folder, "output.mp4")

        # Video writer setup
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec
        out = cv2.VideoWriter(video_path, fourcc, self.fps, (self.width_c, self.height_c))

        print(f"Recording video: {video_path}")

        self.cam.alloc(3)  # Allocate memory for the image buffer
        
        frame_count = 0
        expected_frames = int(self.fps * duration)

        start_time = time.time()

        while frame_count < expected_frames:
            imBuf = ImageBuffer()
            self.cam.freeze_video(True)
            retVal = ueye.is_WaitForNextImage(self.cam.handle(), 1000, imBuf.mem_ptr, imBuf.mem_id)

            if retVal == ueye.IS_SUCCESS:
                self.copy_image(ImageData(self.cam.handle(), imBuf))
                
                if self.npImage.size > 0:
                    frame = self.npImage
                    
                    # Convert to BGR format if needed
                    # frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) if frame.shape[-1] == 3 else frame
                    
                    # Save frame as an image
                    img_filename = os.path.join(save_folder, f"frame_{frame_count:04d}.png")
                    cv2.imwrite(img_filename, frame)

                    # Write frame to video
                    out.write(frame)
                    frame_count += 1
                else:
                    print("Warning: Empty frame captured.")
            else:
                print("Failed to capture frame.")
                break

            # Ensure correct frame pacing
            elapsed_time = time.time() - start_time
            expected_time = frame_count / self.fps
            if elapsed_time < expected_time:
                time.sleep(expected_time - elapsed_time)

        out.release()
        print(f"Video recording finished. Saved to {video_path}")
        print(f"Recorded {frame_count} frames at {self.fps} FPS.")

            
        
        
        


        
    def cameraOff(self):
        """Turn IDS camera off and print some information."""
        if ueyeOK and self.camOn:
            self.cam.exit()
            self.camOn = False
            self.setMenuItems2()
            print( f"{self.appFileName}: cameraOff() Camera stopped ok" )
        return
# endregion
    

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
        mainWin = MainWindow(fName=fn)
    else:
        mainWin = MainWindow()
    mainWin.show()
    sys.exit(mainApp.exec_())  # single_trailing_underscore_ is used for avoiding conflict with Python keywords
