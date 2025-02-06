#!/usr/bin/python -tt
# -*- coding: utf-8 -*-  (use format: UTF-8 without BOM)
#
# bf_tools.py   Image Acquisition (ELE610) using python 3.x
#
# This file include some functions for
#  - IDS camera: error_text, cam_info
#  - Image processing: rho_theta_to_x_y, clip_line_to_box
#  - Display image: mpl_plot, cv_plot
#
# TODO:  The functions are still quite unready and "in construction"-shape
#        (but may be helpful for some tasks)
#        Perhaps I should make 'myCameraTools.py' or 'myImageTools.py' based on this file
#
# .../Dropbox/ELE610/py3/bf_tools.py   
# Karl Skretting, UiS, October 2018, June 2022

# Anaconda prompt..> activate py38
# (py38) C:\..\py3> python -i startup.py 
# >>> from bf_tools import mpl_plot
# >>> import bf_tools as bft
# >>> (img, cInfo, sInfo, rectAOI) = bft.cam_info(dev_id=0, verbose=True)  # image as RGB
# >>> bft.mpl_plot(img)              # matplotlib use RGB
# >>> bft.cv_plot(img[:,:,[2,1,0]])  # OpenCV use BGR

import numpy as np
import matplotlib.pyplot as plt
import cv2
# some functions in this module need ueye, but not all (ex: cv_plot, mpl_plot)
try:
	from pyueye import ueye
except ImportError:
	print('Warning: ImportError for pyueye; ueye is not available.')
except:
	print('Warning: Some error when importing pyueye; ueye is not available.')

class NoeGikkFeil(Exception):
	""" Exception used in cam_info() and perhaps other functions (?)
	"""
	def __init__(self, errNo, message):
		self.errNo = errNo
		self.message = message
	
# end class

def error_text(errNo):
	""" get the error text for the given ueye error number
	Error codes are listed in User Manual, uEye Software Development Kit (SDK) ch. 5
	ex:   t = error_text(errNo)
	"""
	if (errNo == ueye.IS_SUCCESS): # 0
		t = "No error."
	elif (errNo == ueye.IS_NO_SUCCESS): # -1
		t = "IS_NO_SUCCESS"
	elif (errNo == ueye.IS_INVALID_CAMERA_HANDLE):  # 1
		t = "IS_INVALID_CAMERA_HANDLE"
	elif (errNo == ueye.IS_IO_REQUEST_FAILED):  # 2
		t = "IS_IO_REQUEST_FAILED"
	elif (errNo == ueye.IS_CANT_OPEN_DEVICE):  # 3
		t = "IS_CANT_OPEN_DEVICE"
	elif (errNo == ueye.IS_TIMED_OUT): # 122
		t = "IS_TIMED_OUT"
	elif (errNo == ueye.IS_CAPTURE_RUNNING): # 140
		t = "IS_CAPTURE_RUNNING"
	elif (errNo == ueye.IS_DEVICE_ALREADY_PAIRED): # 197
		t = "IS_DEVICE_ALREADY_PAIRED"
	else:
		t = "Text not assigned, see IDS uEye User Manual for list"
	#
	return t

def rho_theta_to_x_y(rho, theta, width, height):
	"""  Transform a line given by distance, rho [pixels], from origin to point 
	on line closest to origin (x0,y0) and angle, theta [rad], to (x0,y0) clockwise
	from x-axis. That is as a line is given by cv2.HoughLines()
	Origin is upper left point of image, x-axis to the right and y-axis downwards.
	Returns points where line cross image edges (as integers, 0 <= x < width, 0 <= y < height).
	ex:
	(x1,y1,x2,y2) = rho_theta_to_x_y(rho, theta, width, height)
	"""
	epsilon = 0.00001
	(c, s) = (np.cos(theta), np.sin(theta))
	(x0, y0) = (c*rho, s*rho)    # Note that theta is angle of line orthogonal to the given line
	if (abs(c) < epsilon):   # horizontal line,  theta approx 0 (180) degrees
		(x1,y1) = (0,int(y0))
		(x2,y2) = (width-1,int(y0))
	elif (abs(s) < epsilon): # vertical line,  theta approx 90 degrees
		(x1,y1) = (int(x0),0)
		(x2,y2) = (int(x0),height-1)
	else:
		(xA, yA) = (rho/c, rho/s)                  # where line crosses axis
		(xH, yW) = (x0-(s/c)*(height-y0),y0-(c/s)*(width-x0))  # where line crosses image edges
		if ((0.0 < yA) and (yA < height)):         # use yA as P1, where line cross y-axis
			(x1,y1) = (0, int(yA))
			if ((0.0 < xA) and (xA < width)):      # and xA as P2
				(x2,y2) = (int(xA), 0)
			elif ((0.0 < xH) and (xH < width)):    # or xH as P2
				(x2,y2) = (int(xH), height-1)
			elif ((0.0 < yW) and (yW < height)):   # or yW as P2
				(x2,y2) = (width-1, int(yW))
			else:
				print("rho_theta_to_x_y(): only yA=y1=y2 valid")
				(x2,y2) = (x1,y1)
			#end if
		elif ((0.0 < xA) and (xA < width)):        # use  xA as P1
			(x1,y1) = (int(xA), 0)
			if ((0.0 < xH) and (xH < width)):      # and xH as P2
				(x2,y2) = (int(xH), height-1)
			elif ((0.0 < yW) and (yW < height)):   # or yW as P2
				(x2,y2) = (width-1, int(yW))
			else:
				print("rho_theta_to_x_y(): only xA=x1=x2 valid")
				(x2,y2) = (x1,y1)
			#end if
		elif ((0.0 < xH) and (xH < width)):      # use xH as P1
			(x1,y1) = (int(xH), height-1)
			if ((0.0 < yW) and (yW < height)):   # and yW as P2
				(x2,y2) = (width-1, int(yW))
			else:
				print("rho_theta_to_x_y(): only xH=x1=x2 valid")
				(x2,y2) = (x1,y1)
			#end if
		else:
			print("rho_theta_to_x_y(): Perhaps only yW=y1=y2 valid?")
			(x2,y2) = (x1,y1) = (width-1, int(yW))
		#end if
		#print( f" -> xA = {xA:8.3f}, yA = {yA:8.3f}, xH = {xH:8.3f}, yW = {yW:8.3f}" )
	#end if 
	return (x1,y1,x2,y2)
	
def clip_line_to_box(x1,y1,x2,y2,xW,xE,yN,yS):
	"""  Clip line to box or image. If the line is crossing the box borders
	only the part of the line inside box is kept, else (part of) the line is kept.
	The line is given by two points (x1,y1) and (x2,y2)
	The box is given by x-values for West (left) and East (right) edge: xW, xE
	and y-values for North (top) and South (bottom): yN, yS
	We should have: (xW < xE) and (yN < yS).
	The algorithm is implemented to be fast as possible, using out codes.
	Outputs may be float (even if all inputs are int)
	Outputs may be on border, i.e. equal to upper limit; x == xE, y == yS 
	
	ex: 
	(x1,y1,x2,y2) = clip_line_to_box(x1,y1,x2,y2, xW,xE,yN,yS)
	(x1,y1,x2,y2) = clip_line_to_box(x1,y1,x2,y2, 0,width,0,height)
	"""
	if not ((xW < xE) and (yN < yS)):
		print("clip_line_to_box:  box edges (or image size) not as supposed.")
		return(x1,y1,x2,y2)
	#
	"""   # included if we want to return integer values
	If any of the input arguments is float, the outputs are float.
	If all the  input arguments are int, the outputs are int.
	Note: After clipping and rounding a point may have (xW <= x <= xE)
	or (yN <= y <= yS)  Note the last "<="
	#
	if ( isinstance(x1, int) and isinstance(x2, int) and 
	     isinstance(y1, int) and isinstance(y2, int) and
	     isinstance(xW, int) and isinstance(xE, int) and 
	     isinstance(yN, int) and isinstance(yS, int) ):
		all_are_int = True
	else:
		all_are_int = False
	#
	# and just before return:
	# Below round, but should perhaps (?) have xW <= x1,x2 < xE, and yN <= y1,y2 < yS 
	if all_are_int:    (int() alone round towards zero, and may be more what is wanted)
		(x1,y1,x2,y2) = ( int(round(x1)), int(round(y1)),
		                  int(round(x2)), int(round(y2)) )
	"""
	#
	# find the Outside Codes 
	oc1 = ((x1 < xW) + ((x1 > xE) << 1) + ((y1 < yN) << 2) + ((y1 > yS) << 3))
	oc2 = ((x2 < xW) + ((x2 > xE) << 1) + ((y2 < yN) << 2) + ((y2 > yS) << 3))
	done = False
	while (not done):
		if ((oc1 == 0) and (oc2 == 0)):  # both points inside
			done = True
		elif (oc1 & oc2):  # both points outside and on same side 
			# may include or omit next line, anyway done = True, no (more) clipping
			# (x1,y1,x2,y2) = (xW-1,yN-1,xW-1,yN-1)   # a new point outside (-1,-1) 
			done = True
		else:  # one point inside and one point outside, or (!) both outside on different sides
			if oc1:
				oc0 = oc1
			else:
				oc0 = oc2
			#end if oc1
			if (oc0 & 1):  # move point to west
				(x0, y0) = (xW, y1 + (y2 - y1)*(xW - x1)/(x2 - x1))
			elif (oc0 & 2):	# move point to east
				(x0, y0) = (xE, y1 + (y2 - y1)*(xE - x1)/(x2 - x1))
			elif (oc0 & 4):	# move point to north
				(x0, y0) = (x1 + (x2 - x1)*(yN - y1)/(y2 - y1), yN)
			else:  # i.e. (oc0 & 8)  move point to south
				(x0, y0) = (x1 + (x2 - x1)*(yS - y1)/(y2 - y1), yS)
			#end if (oc0 & 1)
			if (oc0 == oc1):
				(x1, y1) = (x0, y0)
				oc1 = ((x1 < xW) + ((x1 > xE) << 1) + ((y1 < yN) << 2) + ((y1 > yS) << 3))
			else:
				(x2, y2) = (x0, y0)
				oc2 = ((x2 < xW) + ((x2 > xE) << 1) + ((y2 < yN) << 2) + ((y2 > yS) << 3))
			#end if (oc0 == oc1)
		#end if ((oc1 == 0) and (oc2 == 0))
	#end while
	return (x1,y1,x2,y2)
	
def im_info(A):
	if isinstance(A, np.ndarray):
		print( 'argument: dtype=', A.dtype, ', size=', A.size, 
		       ', ndim=', A.ndim, ', shape=', A.shape,
		       ', np.min()=', np.min(A), ', np.max()=', np.max(A) )
	else:
		print( 'Argument A is not ndarray, i.e. not an image.' )
	return

def cv_plot(img, title=''):
	""" plot image (using OpenCV) 
	use:  cv_plot(img, title='')
	"""
	if not isinstance(img, np.ndarray):
		print( 'Arg 1 is not ndarray, i.e. not an image.' )
		return
	#end if
	#
	# this and cv2.namedWindow(..) gives error Aug 2020
	cv2.imshow(title,img)
	print( 'Press a key to continue.' )
	cv2.waitKey()  # wait until a key is pressed
	# k = cv2.waitKey(0) & 0xFF    # returned value k is NoneType ??
	# print( f"key number {k} ({ord(k)}) was pressed." )
	cv2.destroyAllWindows()
	return 

def mpl_plot(img, title='', fsize=(8,6)):
	""" plot image (using matplotlib.pyplot)
	title may be given, fsize (w,h) is given in inches, each inch 100 pixel
	ex:  mpl_plot(img[:,:,[2,1,0]], title='')    # display BGR image
	"""
	if not isinstance(img, np.ndarray):
		print( 'Arg 1 is not ndarray, i.e. not an image.' )
		return
	#end if
	#
	(fig, ax) = plt.subplots(num=1, figsize=fsize, dpi=100, facecolor='w', edgecolor='k')
	ax.axis('off')
	if (img.ndim == 3):   # assume RGB 
		ax.imshow( img )
		if not len(title):
			title = f"RGB-image of {str(img.dtype)}, height x width is {img.shape[0]}x{img.shape[1]}" 
	if (img.ndim == 2): 
		if (img.dtype == 'uint8'):
			ax.imshow( img, plt.cm.gray )
		if (img.dtype == 'int16'):
			ax.imshow( img, plt.cm.bwr )
		if not len(title):
			title = f"Grayscale image of {str(img.dtype)}, height x width is {img.shape[0]}x{img.shape[1]}"
	#endif 
	plt.title( title )
	plt.show(block = True)     
	return

def cam_info(dev_id=0, verbose=True):
	""" initialize camera, get and display camera information, capture an image,
	and then close the camera again. This is perhaps simpler, i.e. easier to 
	understand, than the code in pyueye_example_main.py as Qt and OpenCV
	is not used here. 
	This function is not appropriate to use within a loop.
	Example:
	  (img, cInfo, sInfo, rectAOI) = cam_info(dev_id=1, verbose=True):
	"""
	#Variables
	hCam = ueye.HIDS(dev_id)     # ueye.HIDS()        blir objekt   ueye.c_uint 
	cInfo = ueye.CAMINFO()
	sInfo = ueye.SENSORINFO()    # tomt objekt
	pcImageMemory = ueye.c_mem_p()
	MemID = ueye.INT()           # ueye.int() og ueye.INT() blir begge objekt  ueye.c_int
	rectAOI = ueye.IS_RECT()
	pitch = ueye.INT()
	nBitsPerPixel = ueye.INT(24)    # 24: bits per pixel for color mode; take 8 bits per pixel for monochrome
	nColorMode = ueye.INT(0)        # Y8/RGB16/RGB24/REG32
	channels = 3                    #3: channels for color mode(RGB); take 1 channel for monochrome
	bytes_per_pixel = int( (nBitsPerPixel.value + 7)/8 )   # runder av nedover 
	isInitialised = False
	isMemoryAssigned = False
	img = -1
	#-----------------------------------------------------------------------
	try:
		# Starts the driver and establishes the connection to the camera
		nRet = ueye.is_InitCamera(hCam, None)
		if nRet != ueye.IS_SUCCESS:
			raise NoeGikkFeil(nRet, 'ERROR in ueye.is_InitCamera()')
		#
		isInitialised = True

		# Reads out the data hard-coded in the non-volatile camera memory 
		# and writes it to the data structure that cInfo points to
		nRet = ueye.is_GetCameraInfo(hCam, cInfo)
		if nRet != ueye.IS_SUCCESS:
			raise NoeGikkFeil(nRet, 'ERROR in ueye.is_GetCameraInfo()')
		#
		if verbose:
			print(" CameraInfo: ")   # cInfo er 64 byte, se kap 2.3 User Manual uEye
			print(f"   Camera serial no.:    {cInfo.SerNo.decode('utf-8')}" ) # 12 byte
			print(f"   Camera ID:            {cInfo.ID.decode('utf-8')}" ) # 20 byte
			print(f"   Camera Version:       {cInfo.Version.decode('utf-8')}" ) # 10 byte
			print(f"   Camera Date:          {cInfo.Date.decode('utf-8')}" ) # 12 byte
			print(f"   Camera Select byte:   {cInfo.Select.value}" ) # 1 byte
			print(f"   Camera Type byte:     {cInfo.Type.value}" ) # 1 byte
			# 8 site byte er ubrukt

		# You can query additional information about the sensor type used in the camera
		nRet = ueye.is_GetSensorInfo(hCam, sInfo)
		if nRet != ueye.IS_SUCCESS:
			raise NoeGikkFeil(nRet, "ERROR in ueye.is_GetSensorInfo()")
		#
		if verbose:
			print(" SensorInfo: ")   # sInfo, see ch. 4.50 User Manual uEye
			print(f"   Sensor SensorID:      {sInfo.SensorID.value}" ) # WORD (ushort) (2 byte)
			print(f"   Sensor strSensorName: {sInfo.strSensorName.decode('utf-8')}" ) # 32 byte
			print(f"   Sensor nColorMode:    {int.from_bytes(sInfo.nColorMode.value, byteorder='big')}" )
			print(f"   Sensor nMaxWidth:     {sInfo.nMaxWidth.value}" ) # DWORD (uint) (4 byte)
			print(f"   Sensor nMaxHeight:    {sInfo.nMaxHeight.value}" ) # DWORD (uint) (4 byte)
			print(f"   Sensor bMasterGain:   {str(bool(sInfo.bMasterGain.value))}" )
			print(f"   Sensor bRGain:        {str(bool(sInfo.bRGain.value))}" )
			print(f"   Sensor bGGain:        {str(bool(sInfo.bGGain.value))}" )
			print(f"   Sensor bBGain:        {str(bool(sInfo.bBGain.value))}" )
			print(f"   Sensor bGlobShutter:  {str(bool(sInfo.bGlobShutter.value))}" )
	
		nRet = ueye.is_ResetToDefault( hCam	)
		if nRet != ueye.IS_SUCCESS:
			raise NoeGikkFeil(nRet, "ERROR in ueye.is_ResetToDefault()")
		#
		if verbose:
			print(" is_ResetToDefault(..) ok") 

		# Set display mode to DIB
		nRet = ueye.is_SetDisplayMode(hCam, ueye.IS_SET_DM_DIB)
		if nRet != ueye.IS_SUCCESS:
			raise NoeGikkFeil(nRet, 'ERROR in ueye.is_SetDisplayMode()')
		#	
		if verbose:
			print(" is_SetDisplayMode(..) ok") 
	
		# Set the right color mode
		col_mode = int.from_bytes(sInfo.nColorMode.value, byteorder='big')  # ordinary Python int
		if col_mode == ueye.IS_COLORMODE_BAYER:  
			nRet = ueye.is_GetColorDepth(hCam, nBitsPerPixel, nColorMode)
			if nRet != ueye.IS_SUCCESS:
				raise NoeGikkFeil(nRet, 'ERROR in ueye.is_GetColorDepth()')
			#	
			bytes_per_pixel = int( (nBitsPerPixel.value + 7)/8 )   # runder av nedover 
			if verbose:
				print( (f" IS_COLORMODE_BAYER: nColorMode = {nColorMode}," + 
				        f" nBitsPerPixel = {nBitsPerPixel}," + 
				        f" bytes_per_pixel = {bytes_per_pixel}") )
		elif col_mode == ueye.IS_COLORMODE_CBYCRY:
			# for color camera models use RGB32 mode
			nColorMode = ueye.INT( ueye.IS_CM_BGRA8_PACKED )
			nBitsPerPixel = ueye.INT(32)
			bytes_per_pixel = int( (nBitsPerPixel.value + 7)/8 )   # runder av nedover 
			if verbose:
				print( (f" IS_COLORMODE_CBYCRY: nColorMode = {nColorMode}," + 
				        f" nBitsPerPixel = {nBitsPerPixel}," + 
				        f" bytes_per_pixel = {bytes_per_pixel}") )
		elif col_mode == ueye.IS_COLORMODE_MONOCHROME:
			nColorMode = ueye.INT( ueye.IS_CM_MONO8 )
			nBitsPerPixel = ueye.INT(8)
			bytes_per_pixel = int( (nBitsPerPixel.value + 7)/8 )   # runder av nedover 
			if verbose:
				print( (f" IS_COLORMODE_MONOCHROME: nColorMode = {nColorMode}," + 
				        f" nBitsPerPixel = {nBitsPerPixel}," + 
				        f" bytes_per_pixel = {bytes_per_pixel}") )
		else: 		# for monochrome camera models use Y8 mode
			nColorMode = ueye.INT( ueye.IS_CM_MONO8 )
			nBitsPerPixel = ueye.INT(8)
			bytes_per_pixel = int( (nBitsPerPixel.value + 7)/8 )   # runder av nedover 
			if verbose:
				print( (f" else: nColorMode = {nColorMode}," + 
				        f" nBitsPerPixel = {nBitsPerPixel}," + 
				        f" bytes_per_pixel = {bytes_per_pixel}") )
		#end if
	
		# Can be used to set the size and position of an "area of interest"(AOI) within an image
		nRet = ueye.is_AOI(hCam, ueye.IS_AOI_IMAGE_GET_AOI, rectAOI, ueye.sizeof(rectAOI))
		if nRet != ueye.IS_SUCCESS:
			raise NoeGikkFeil(nRet, 'ERROR in ueye.is_AOI()')
		#
		width = rectAOI.s32Width   # c_int
		height = rectAOI.s32Height # c_int
		if verbose:
			print( f" AOI: max size (width x height) = {width.value} x {height.value}" ) 
	
		# Allocates an image memory for an image having its dimensions 
		# defined by width and height and its color depth defined by nBitsPerPixel
		nRet = ueye.is_AllocImageMem(hCam, width, height, nBitsPerPixel, pcImageMemory, MemID)
		if nRet != ueye.IS_SUCCESS:
			raise NoeGikkFeil(nRet, "ERROR in ueye.is_AllocImageMem()" )
		#
		isMemoryAssigned = True
		if verbose:
			print( " is_AllocImageMem ok." ) 
		#
		# Makes the specified image memory the active memory
		nRet = ueye.is_SetImageMem(hCam, pcImageMemory, MemID)
		if nRet != ueye.IS_SUCCESS:
			raise NoeGikkFeil(nRet, "ERROR in ueye.is_SetImageMem()" )
		#
		# Set the desired color mode
		nRet = ueye.is_SetColorMode(hCam, nColorMode)
		if nRet != ueye.IS_SUCCESS:
			raise NoeGikkFeil(nRet, "ERROR in ueye.is_SetColorMode()" )
		#
		# alt (?) ok så langt
		
		# Activates the camera's live video mode (free run mode) 
		# nRet = ueye.is_CaptureVideo(hCam, ueye.IS_DONT_WAIT)  # gir sort bilde
		# nRet = ueye.is_CaptureVideo(hCam, 10)  # wait 0.1 s
		nRet = ueye.is_CaptureVideo(hCam, ueye.IS_WAIT)  # works well
		if nRet != ueye.IS_SUCCESS:
			raise NoeGikkFeil(nRet, 'ERROR in ueye.is_CaptureVideo()')
		#
		# When (if ever) do we need Freeze?  if there is no wait-time?
		# nRet = ueye.is_FreezeVideo(hCam, 10)  # wait 0.1 s
		# if nRet != ueye.IS_SUCCESS:
		# 	raise NoeGikkFeil(nRet, 'ERROR in ueye.is_FreezeVideo()')
		#
		# Enables the queue mode for existing image memory sequences
		nRet = ueye.is_InquireImageMem(hCam, pcImageMemory, MemID, width, height, nBitsPerPixel, pitch)
		if nRet != ueye.IS_SUCCESS:
			raise NoeGikkFeil(nRet, 'ERROR in ueye.is_InquireImageMem()')
		#
		if verbose:
			print( (f" InquireImageMem: size (width x height) = {width.value} x {height.value}," +
			        f" bits per pixel {nBitsPerPixel.value}, line increment {pitch.value}" + 
			        f" = {width.value * int((nBitsPerPixel.value + 7)/8)}") ) 
		#
		if verbose:
			print( " Capture the image from camera memory and store it as numpy array" )
		# ...extract the data of our image memory (undocumented?) function
		array = ueye.get_data(pcImageMemory, width, height, nBitsPerPixel, pitch, copy=True)
		if verbose:
			print( (f" numpy array has size {array.size} and ndim {array.ndim}," + 
			        f" shape = {array.shape}") )
		# ...reshape it in an numpy array...
		img = np.reshape(array, (height.value, width.value, bytes_per_pixel) )
		if verbose:
			print( (f" img as captured has size {img.size} and ndim {img.ndim}," + 
			        f" shape = {img.shape}") )
		#-----------------------------------------------------
		# may do some image processing. Ex: resize the image by a half
		#   img = cv2.resize(img, (0,0), fx=0.5, fy=0.5)
		#-----------------------------------------------------
		#
		img = img[:,:,[2,1,0]]   # # BGRx --> RGB
		if verbose:
			print( (f" img as returned has size {img.size} and ndim {img.ndim}," + 
			        f" shape = {img.shape}") )
		#
	except NoeGikkFeil as e:
		print( f" ** {e.message}, errNo = {e.errNo} ({error_text(e.errNo)})" )
		#
	except Exception as e:
		print(" ** An ordinary error occurred.")
		print(" **", e )
	except:
		print(" ** Another error occurred.")
	else:
		print(" Function returns with no errors.")
	finally:
		# free memory and stop camera
		if isMemoryAssigned:
			# cv2.destroyAllWindows()  
			ueye.is_FreeImageMem(hCam, pcImageMemory, MemID)
			isMemoryAssigned = False
		if isInitialised:
			ueye.is_ExitCamera(hCam)
			isInitialised = False
	#end try
	return (img, cInfo, sInfo, rectAOI)
#end cam_info(..)

def test_clip():
	(xW,xE,yN,yS) = (0,11, 0,7)   # west, east, north, south edges of box
	(x1,y1,x2,y2) = (-2,-1, 7,8)
	print( f"    (x1,y1) = ({x1:8.1f}, {y1:8.1f}),   (x2,y2) = ({x2:8.1f}, {y2:8.1f})" )
	(x1,y1,x2,y2) = clip_line_to_box(x1,y1,x2,y2, xW,xE,yN,yS)
	print( f"--> (x1,y1) = ({x1:8.1f}, {y1:8.1f}),   (x2,y2) = ({x2:8.1f}, {y2:8.1f})" )
	(x1,y1,x2,y2) = (8.5,1.5, 11.5,4.5)
	# (x1,y1,x2,y2) = (5.0,4.5, -1.0,10.5)
	print( f"    (x1,y1) = ({x1:8.1f}, {y1:8.1f}),   (x2,y2) = ({x2:8.1f}, {y2:8.1f})" )
	(x1,y1,x2,y2) = clip_line_to_box(x1,y1,x2,y2, xW,xE,yN,yS)
	print( f"--> (x1,y1) = ({x1:8.1f}, {y1:8.1f}),   (x2,y2) = ({x2:8.1f}, {y2:8.1f})" )
	return
	
def test_rho():
	(width, height) = (10, 6)
	(rho, theta) = (5, 0.6435)  # cos(theta) > 0.8    sin(theta) < 0.6
	print( f"rho = {rho:8.2f}, theta = {theta:8.5f},  width = {width:8.1f}, height = {height:8.1f}" )
	(x1,y1,x2,y2) = rho_theta_to_x_y(rho, theta, width, height)	
	print( f"--> (x1,y1) = ({x1:8.1f}, {y1:8.1f}),   (x2,y2) = ({x2:8.1f}, {y2:8.1f})" )
	#
	(rho, theta) = (2.5, 2.2143)  
	print( f"rho = {rho:8.2f}, theta = {theta:8.5f},  width = {width:8.1f}, height = {height:8.1f}" )
	(x1,y1,x2,y2) = rho_theta_to_x_y(rho, theta, width, height)	
	print( f"--> (x1,y1) = ({x1:8.1f}, {y1:8.1f}),   (x2,y2) = ({x2:8.1f}, {y2:8.1f})" )
	#
	(rho, theta) = (-2.5, 2.2143)  
	print( f"rho = {rho:8.2f}, theta = {theta:8.5f},  width = {width:8.1f}, height = {height:8.1f}" )
	(x1,y1,x2,y2) = rho_theta_to_x_y(rho, theta, width, height)	
	print( f"--> (x1,y1) = ({x1:8.1f}, {y1:8.1f}),   (x2,y2) = ({x2:8.1f}, {y2:8.1f})" )
	return

if __name__ == '__main__':
	# (img, cInfo, sInfo, rectAOI) = cam_info(dev_id=0, verbose=True)
	test_rho()
