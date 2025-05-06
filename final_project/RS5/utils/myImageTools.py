#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ../ELE610/py3/myImageTools.py 
#
#  Some tools (functions) for image processing. The functions are:
#  qimage2np() and np2qimage2np() convert image from Qt to numpy (and back)
#    as used for appImageViewer*.py, the work is done by the qimage2ndarray 
#    package if it is available, else simple (and slow) file write and read is used.
#  smoothFilter()  returns a simple low-pass filter
#
# Karl Skretting, UiS, February 2019, November 2020 (need Python 3.6 ->), June 2022
#      minor updates January 2024

# Example on how to use file:
#   >>> from myImageTools import smoothFilter, qimage2np, np2qimage
#   >>> import myImageTools
#   (py38) C:\..\py3> python myImageTools.py   # test

import sys
import os.path
from PyQt5.QtGui import QImage
import numpy as np
try:
	import cv2
	cv2_ok = True
except:
	print( "Error importing cv2, functions from myImageTools have cv2 options disabled." )
	cv2_ok = False
#

try:
	import qimage2ndarray as q2n
	q2n_ok = True
except ImportError:
	# functions below should work even without qimage2ndarray package
	# raise ImportError( f"myImageTools: Requires qimage2ndarray." ) 
	print( f"myImageTools: Import error for qimage2ndarray. Continue without it." )
	q2n_ok = False
#end try, import qimage2ndarray

empty_ndarray = np.array([], dtype=np.uint8)
tempFile = 'temp.png'

def smoothFilter(len=3):
	"""Generate and returns a small simple low-pass FIR filter with given length (3,5,7 or 9)."""
	if (len == 3):
		a = np.array([1,2,1])/4
	elif (len == 5):
		a = np.array([1,4,6,4,1])/16
	elif (len == 7):
		a = np.array([1,4,6,6,6,4,1])/28
	elif (len == 9):
		a = np.array([1,4,6,8,8,8,6,4,1])/46
	else:			
		a = np.array([1,2,1])/4
	#
	return a 

# could these functions be simplified if we include isAllGray?
def qimage2np(qImage):
	"""Converts a QImage object into a numpy array 2D or 3D (for color).

	The best (fastest) way to do this is to use a function that extract the 
	bytes inside the QImage memory representation. Here we try to use the
	qimage2ndarray package, but if import of this is unsuccessful an alternative
	is used; the image is saved in a file and then read by OpenCV function imread.
	ex.: B = qimage2np(qImage)
	
	Parameters
	----------
	qImage: QImage

	Returns
	-------
	B: numpy.ndarray (of uint8) 
	"""
	if q2n_ok:
		if (not qImage.isNull()):
			B = q2n.byte_view(qImage)   # B may be 2D or 3D (RGBA/BRGA)
		else:
			B = empty_ndarray
	else: 
		print("qimage2np: qimage2ndarray (q2n) is not imported, make image B (numpy array) by writing and reading a file.")
		if qImage.save(tempFile,quality=100):   #  True if successfully saved
			B = cv2.imread(tempFile)
		else:
			B = empty_ndarray
		#
	#
	return B
#end function qimage2np

def np2qimage(B):
	"""Converts a numpy array to QImage object.

	This is done by gray2qimage() method in qimage2ndarray package but only
	for gray scale images. For color image, i.e. 3D array B, the image is saved 
	in a file by OpenCV imwrite() function and then read by when QImage object
	is created. If B is not an array representing an image, an empty QImage
	object is returned.
	ex.: qImage = qimage2np(B)
	
	Parameters
	----------
	B: numpy.ndarray (of uint8) 
	
	Returns
	-------
	qImage: QImage
	"""
	if not isinstance(B, np.ndarray):
		print("np2qimage: Ignore illegal argument B (not numpy array), return empty QImage.")
		return QImage()  
	#
	if q2n_ok and ((len(B.shape) == 2) or ((len(B.shape) == 3) and (B.shape[2] == 1))):
		qImage = q2n.gray2qimage(B)   # must be gray for this, and qImage.format = 3 (indexed)
	elif cv2_ok and (len(B.shape) == 2) or (len(B.shape) == 3):   # must be 2D or 3D array 
		# print( f"np2qimage: write image B (numpy array) to file {tempFile}" )
		cv2.imwrite(tempFile, B)
		# print( f"np2qimage: and read it from file {tempFile} into qImage" )
		qImage = QImage(tempFile)   # read from file
	else:   # B = empty_ndarray ends here
		qImage = QImage()   # and returns empty QImage
	# 
	return qImage
#end function np2qimage

def testAll():
	"""Simple function for testing the three functions in this file."""
	print("myImageTools.py: testAll()  # test the three functions in this file")
	print("Test smoothFilter()")
	b = smoothFilter(5)
	if isinstance(b, np.ndarray):
		print( f"  smoothFilter(5) return b as np.ndarray of {b.dtype.name}, shape {str(b.shape)}" ) 
		print( "  returned values are: (" + " ".join([f"{x:.4f}" for x in b]) + ")" )
	# old string format: "  returned values are: (" + len(b)*" %.4f " % tuple(b) + ")"
	# new string format: "  returned values are: (" + " ".join([f"{x:.4f}" for x in b]) + ")"
	# or the simple way: f"  returned values are: {str(tuple(b))}"
	#
	ok = True
	if not os.path.exists(tempFile):
		print( f"The file {tempFile} does not exist" )
		ok = False
	#
	if ok:
		print( "Read image B from file using OpenCV imread" ) 
		try:
			B = cv2.imread(tempFile)
		except:
			print("  error when using cv2.imread()") 
			B = []
		#
		if isinstance(B, np.ndarray):
			print(f"  B is np.ndarray of {B.dtype.name}, shape {B.shape}.") 
		else:
			print("  B is NOT np.ndarray") 
			ok = False
		#
	if ok:
		print("Make qImage from B using np2qimage")
		qImage = np2qimage(B)
		if isinstance(qImage, QImage) and (not qImage.isNull()):
			print( (f"  the returned qImage has format {qImage.format()}," + 
			        f" height {qImage.height()} and width {qImage.width()}") ) 
		else:
			print( "  but it did NOT return a non-empty qImage" )
			ok = False
		#
	if ok:
		print( "Make numpy.ndarray C from qImage using qimage2np" )
		C = qimage2np(qImage)
		if isinstance(C, np.ndarray):
			print( f"  C is np.ndarray of {C.dtype.name}, shape {C.shape}." ) 
		else:
			ok = False
		# 
	if ok:
		if (isinstance(B, np.ndarray) and (len(B.shape)==3) and (B.shape[2]==3) and
			isinstance(C, np.ndarray) and (len(C.shape)==3) and (C.shape[2]==4) ):
			xy = (x,y) = (243,421)  # xy: tuple, x,y: int
			if ((0 <= x) and (x < B.shape[0]) and (x < C.shape[0]) and
				(0 <= y) and (y < B.shape[1]) and (y < C.shape[1]) ):
				print( (f"  B[{x},{y}] = [{B[x,y,0]},{B[x,y,1]},{B[x,y,2]}]," +
				        f"  C[{x},{y}] = [{C[x,y,0]},{C[x,y,1]},{C[x,y,2]},{C[x,y,3]}]") )
			#
		#
	#end if
	#
	return

# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
	testAll()

