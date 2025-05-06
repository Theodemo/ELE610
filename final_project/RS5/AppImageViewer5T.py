# My own image viewer app - Inherited from AppImageViewer2T
# For actions on dice

_appFileName = "ImageViewer"
_author = "Théo and Jesus" 
_version = "2025.02.6"

# region Libraries

import sys
import os.path
import numpy as np
from time import sleep
import cv2
import random

import time
from rwsuis import RWS

from utils.variables import T_500, T_250, T_500_bis

norbert_ip = "http://152.94.160.198"
robot = RWS.RWS(norbert_ip)



try:
    from PyQt5.QtCore import Qt, QPoint, QRectF, QT_VERSION_STR
    from PyQt5.QtGui import QImage, QPixmap, QTransform
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QFileDialog, QLabel, 
            QGraphicsScene, QGraphicsPixmapItem, QDialog)
except ImportError:
    raise ImportError( f"{_appFileName}: Requires PyQt5." )
#end try, import PyQt5 classes

try:
    from pyueye import ueye
    from utils.pyueye_example_camera import Camera
    from utils.pyueye_example_utils import ImageData, ImageBuffer  # FrameThread, 
    ueyeOK = True
except ImportError:
    ueye_error = f"{_appFileName}: Requires IDS pyueye example files (and IDS camera)." 
    # raise ImportError(ueye_error)
    ueyeOK = False   # --> may run program even without pyueye
#end try, import pyueye

from AppImageViewer2T import myPath, MainWindow as inheritedMainWindow


# endregion

class MainWindow(inheritedMainWindow):  
    """MainWindow class for this image viewer is inherited from another image viewer."""
    
# Two initialization methods used when an object is created
    def __init__(self, fName="", parent=None):
        # print( f"File {_appFileName}: (debug) first line in __init__()" )
        super().__init__(fName, parent) # use inherited __init__ with extension as follows
        #
        # set appFileName as it should be, name not inherited from super()...
        self.appFileName = _appFileName 
        if (not self.pixmap.isNull()): 
            self.setWindowTitle( f"{self.appFileName} : {fName}" )
        else:
            self.setWindowTitle(self.appFileName)
        # 
        # self.view.rubberBandRectGiven.connect(self.meanColorEnd)  
        # signal is already connected to cropEnd (appImageViewer1), now connected to two slots!
        self.meanColorActive = False
        self.mastership = False  
        self.center = None
        self.t_center = []
        
        self.better = False
        self.temp_center = None
        self.block = False
        #
        self.initMenu3()
        self.setMenuItems3()
        # print( f"File {_appFileName}: (debug) last line in __init__()" )
        return
    #end function __init__
    
    
    def initMenu3(self):
        """Initialize Robot menu."""
        a = self.qaMastership = QAction('Request mastership', self)
        a.triggered.connect(self.requestMastership)
        a = self.qaStartRAPID = QAction('Start RAPID code', self)
        a.triggered.connect(self.start_rapid)

        a = self.qaTask01 = QAction('Launch Task01', self)
        a.triggered.connect(self.Task01)
        a = self.qaDetectPuck = QAction('Detect puck', self)
        a.triggered.connect(self.detect_pucks)

        a = self.qaCollectPucks = QAction('Collect all detected pucks', self)
        a.triggered.connect(self.collect_pucks)
        
        a = self.qaCollectPuck = QAction('Collect one detected puck', self)
        a.triggered.connect(self.collect_puck)
        
        #
        robotMenu = self.mainMenu.addMenu('&Robot')
        robotMenu.addAction(self.qaMastership)
        robotMenu.addAction(self.qaStartRAPID)
        robotMenu.addAction(self.qaTask01)
        robotMenu.addAction(self.qaDetectPuck)
        robotMenu.addAction(self.qaCollectPuck)
        robotMenu.addAction(self.qaCollectPucks)
        
        
        return
    
    def setMenuItems3(self):
        """Enable/disable menu items as appropriate."""
        # should the 'inherited' function be used, first check if it exists 
        setM = getattr(super(), "setMenuItems", None)  # both 'self' and 'super()' seems to work as intended here
        if callable(setM):
            # print("setMenuItems2(): The 'setMenuItems' function is inherited.")
            setM()  # and run it
            
        pixmapOK = ((not self.pixmap.isNull()) and isinstance(self.curItem, QGraphicsPixmapItem))
        self.qaTask01.setEnabled(self.mastership)
        self.qaDetectPuck.setEnabled(self.mastership)
        self.qaCollectPuck.setEnabled(self.mastership)
        self.qaCollectPucks.setEnabled(self.mastership)
        self.qaStartRAPID.setEnabled(False)
        return
    
    # ------------------- Help methods -------------------
    
    def wait_for_rapid_variable(var_name, expected_value, poll_interval=0.2, timeout=30):
        """
        Wait for a RAPID variable to equal a specific value.
        
        Parameters:
        - var_name (str): The name of the RAPID variable to check.
        - expected_value (Any): The value we're waiting for.
        - poll_interval (float): Seconds to wait between polls.
        - timeout (float): Max time in seconds to wait before giving up.
        
        Returns:
        - True if the expected value was found, False if timeout occurred.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            current_value = robot.get_rapid_variable(var_name)
            if current_value == expected_value:
                return True
            time.sleep(poll_interval)
        print(f"Timeout while waiting for {var_name} to become {expected_value}.")
        return False

    
    # ------------------- Robot methods -------------------
    def requestMastership(self):
        """
        Request the mastership on the flex pendant.
        """
        robot.request_rmmp()  # GRANT must be confirmed on FlexPendant
        self.mastership = True
        self.setMenuItems3()
        print("Mastership granted")
        
        
    def start_rapid(self):
        """
        Launch the RAPID code. But need to be in automatic mode.
        """
        robot.start_RAPID()
        
        
    def get_center(self):
        """
        Return the center of the QR codes find in the images.
        """
        self.reduceNoise()
        self.increaseContrast()
        self.toGray()
        self.tryBinary(t=132)
        self.center = self.detectQRCodeCenter()
        
        # small coding blocks to redo if self.center is None
        if self.center:
            return
        else:
            self.get_center()
        
        
    def detect_pucks(self):
        """
        Take a picture and return the table coordinates for each puck.
        Then gives to RAPID the number of puck detected.
        """
        self.t_center = []
        self.getOneImage()
        self.flip_image()
        self.get_center()   # return a list of tuples [(541,325), (10,20), ...]

        
        height = int(robot.get_gripper_height())
        
        if len(self.center) > 0:
        
            for center in self.center:
                    
                if center and 490 <= height <= 510:
                    t_coors = T_500_bis @ np.array([center[0], center[1], 1]).reshape(-1,1)
                    new_rt = [int(x) for x in t_coors.flatten()[:2]]
                    new_rt.append(0)
                    self.t_center.append(new_rt)
                
                elif center and 240 <= height <= 260 and (not self.better):
                    t_coors = T_250 @ np.array([center[0], center[1], 1]).reshape(-1,1)
                    new_rt = [int(x) for x in t_coors.flatten()[:2]]
                    new_rt.append(0)
                    self.t_center.append(new_rt)
                    
                elif center and 240 <= height <= 260 and self.better:
                    # Here is the process to have a better accuracy for the picking of pucks 
                    # (take a photo and compute the offset needed for an accurate pick of the puck)
                    expected_center = np.array([658, 291, 1])   # maybe need to change ot the images is the wrong upside-down direction(need to flip it)
                    actual_center = self.center
                    
                    expected_table = T_250 @ expected_center
                    actual_table = T_250 @ actual_center
                    
                    offset = expected_table - actual_table
                    
                    new_center = original_coor + offset  # think I'm wrong here: need to define original_coor: how to remember it ?
        
            robot.set_rapid_variable("nPuck", len(self.t_center))
            print(f"nPuck set to {len(self.t_center)}.")
        
        
        
        
    def Task01(self):
        """
        Launch Task01 of the RAPID code
        """
        robot.set_rapid_variable("WPW", 1)
        print("Sent WPW = 1 (Task01)")
        
            
   
    def collect_pucks(self):
        """
        Launch Task04 of the RAPID code
        """
        self.detect_pucks()     # detect all the pucks on the table and gives the coordinates to the robot
        
        for i in range(len(self.t_center)):
        
            robot.set_robtarget_translation(f"Task04_{i}", self.t_center[i])
            
            #if self.block:
            #    break
            
        print("Detecte pucks moved to the reference position.")
            
            
        robot.set_rapid_variable("WPW", 4)

        print("Sent WPW = 4 (Task04)")
        
        
    def collect_puck(self):
        """
        Collect a single puck and place it in a reference position.
        """
        self.block = True
        self.collect_pucks()
        
        
    # ------------------- Better robot methods -------------------
    
    def Task03(self):
        """
        Launch Task05 of the RAPID code wich is the same as Task04 but better.
        It waits for RAPID to go on.
        """
        self.detect_pucks()     # detect all the pucks on the table and gives the coordinates to the robot
        
        for i in range(len(self.t_center)):
            robot.set_robtarget_translation(f"Task02_{i}", self.t_center[i])
            
        
        # new part to take images at 250 mm to have a better accuracy on puck's position
        self.better = True
        num = robot.get_rapid_variable("nPuck")
        for i in range(num):    
            success = wait_for_rapid_variable("WRD", 0)
            self.temp_center = self._center[i]
            if success:
                self.detect_pucks()
                robot.set_robtarget_translation(f"puckPos", self.t_center[0])
                robot.set_rapid_variable("temp", 1)
            else:
                print("Timeout waiting for RAPID.")
        
            
            
        


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