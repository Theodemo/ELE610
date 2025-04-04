from pyueye import ueye
import numpy as np
import cv2
import ctypes

def capture_photo():
    # Initialize the camera
    hCam = ueye.HIDS(0)  # Assuming the first camera (index 0)
    ret = ueye.is_InitCamera(hCam, None)
    
    if ret != ueye.IS_SUCCESS:
        print("Failed to initialize the camera!")
        return

    # Set image properties (width, height, bit depth)
    width = 640
    height = 480
    bitDepth = 24  # BGR format

    # Allocate memory for the image
    pMem = ctypes.POINTER(ctypes.c_char)()  # Pointer to hold the memory address
    memId = ctypes.c_int(0)  # Initialize the memory ID variable

    ret = ueye.is_AllocImageMem(hCam, width, height, bitDepth, ctypes.byref(pMem), ctypes.byref(memId))
    
    if ret != ueye.IS_SUCCESS:
        print(f"Failed to allocate memory. Error code: {ret}")
        return

    # Set the allocated memory to be used for capturing images
    ret = ueye.is_SetImageMem(hCam, pMem, memId)
    if ret != ueye.IS_SUCCESS:
        print("Failed to set the image memory!")
        return

    # Capture a single frame
    ret = ueye.is_FreezeVideo(hCam)
    if ret != ueye.IS_SUCCESS:
        print("Failed to capture image!")
        return

    # Access the image data from the memory pointer
    # You would typically copy the data from `pMem` here into a numpy array or other format

    # For example, we can save the image or process it here

    # Free the allocated memory
    ueye.is_FreeImageMem(hCam, pMem, memId)

    # Close the camera and release resources
    ueye.is_ExitCamera(hCam)

# Call the function to capture the photo
capture_photo()