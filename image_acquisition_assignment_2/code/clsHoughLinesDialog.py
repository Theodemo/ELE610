#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ../ELE610/py3/clsHoughLinesDialog.py 
#
#  The class HoughLinesDialog 
#  and functions: getBestHoughLines, draw_lines 
#
# Karl Skretting, UiS, January-February 2024

# Example on how to use file:
#   (C:\...\Anaconda3) C:\..\py3> activate py11
#   (py11) C:\..\py3> python clsHoughLinesDialog.py
# Example on how to use file in appImageViewer1.py:
#   from clsHoughLinesDialog import HoughLinesDialog, getBestHoughLines, draw_lines

import sys
import numpy as np
import cv2

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QAction, QApplication, QBoxLayout, QButtonGroup, 
			QDialog, QDoubleSpinBox, QFrame, QLabel, QMainWindow, 
			QPushButton, QRadioButton, QSlider, QSpinBox)


def getBestHoughLines(linesFound, B, nofLines, distLines, verbose=True):
	"""Sort and select the 'best' lines from lines as returned by 
	HoughLines or HoughLinesP. Also line representation is changed.
	Angle theta is in radians and shown in degrees.
	
	Use:
	  lines = getBestHoughLines(linesFound, B, nofLines, distLines)
	Input arguments:
	  linesFound : the lines as returned by HoughLines or HoughLinesP
	  B          : the binary image used to find the lines
	               needed to find the 'cover' property of a line
	  nofLines   : maximum number of lines to return
	  distLines  : ignore lines closer to each other than given by distLines
	  verbose    : True (print much) or False (print nothing)
	Output argument:
	  lines      : a numpy array with nofLines rows and 8 columns 
	  lines[row] : each row is a line given by 8 values, two alternative
	    representations and two derived properties
	  (x1,y1) = (line[0],line[1]) first point for line
	  (x2,y2) = (line[2],line[3]) second point for line, x2 >= x1
	  rho = line[4] is distance from line to origin
	  theta = line[5] is angle [radians] from upward in clockwise direction
	  length = line[6] is length from first point to second point
	  cover = line[7] is how many pixels in a thin line from first point 
	    to second point that is non-zero in binary image B     
	"""
	if not (isinstance(linesFound, np.ndarray) and (linesFound.ndim == 3) and \
	        linesFound.size):
		print( "getBestHoughLines(): first argument 'linesFound' not as expected. " )
		print( "Is it from cv2.HoughLines() or cv2.HoughLinesP() ?" )
		return None
	if not (isinstance(B, np.ndarray) and (B.ndim == 2)):
		print( "getBestHoughLines(): second argument 'B' not as expected. " )
		return None
	if (len(linesFound) == 0) or (nofLines < 1) : return None
	#
	L = len(linesFound)
	(w,h) = (B.shape[1], B.shape[0])
	lines = np.zeros((L,8),dtype=np.float64)
	if verbose:
		print( f"\ngetBestHoughLines(..,{nofLines=},{distLines=:6.2f}): started " \
		       f"with {L=} lines in numpy array 'lines'." )
		print( "-- first shows lines in the order they were found by cv2.HoughLines[P] --" )
	# find the two representations and two properties of each line
	for idxLine in range(L):
		line = linesFound[idxLine]
		# HoughLines:  line = array([[rho, theta]], dtype=float32)   # theta in radians
		# HoughLinesP: line = array([[x1,y1,x2,y2]], dtype=int32)
		if (line.ndim == 2) and (line[0].size == 2):  # from HoughLines
			(rho,theta) = line[0]           
			(a,b) = (np.cos(theta), np.sin(theta))
			(x0,y0) = (a*rho, b*rho)   # point on line closest to origin
			(x1,y1) = (int(x0 + 8000*(-b)), int(y0 + 8000*(a)))
			(x2,y2) = (int(x0 - 8000*(-b)), int(y0 - 8000*(a)))
			# input arguments of clipLine should be int, and returned values are int
			(inSide,(x1,y1),(x2,y2)) = cv2.clipLine((0,0,w,h),(x1,y1),(x2,y2))
		elif (line.ndim == 2) and (line[0].size == 4):  # from HoughLinesP
			(x1,y1,x2,y2) = line[0]
		else:
			print( f"ERROR in getBestHoughLines(): {line=}" )
			return None
		# end if
		# use (x1,y1) and (x2,y2) to (re)calculate rho and theta
		length = np.hypot(x2-x1,y2-y1)
		theta = np.arctan2(x2-x1,y1-y2)  # x2-x1 >= 0 ==> 0 <= theta <= pi
		rho = (x2*y1-x1*y2)/length if length else 0.0
		#
		cover = 0
		if (theta < np.pi/4) or (theta > np.pi*3/4):
			# let y go from y1 to y2 and find corresponding x
			for y in range(min(y1,y2),max(y1,y2)+1):
				a = (y-y1)/(y2-y1)
				x = int((1-a)*x1+a*x2)
				if B[y,x]: cover = cover+1
			#
		else:
			# let x go from x1 to x2 and find corresponding y
			for x in range(x1,x2+1):
				a = (x-x1)/(x2-x1)
				y = int((1-a)*y1+a*y2)
				if B[y,x]: cover = cover+1
			#
		#
		if verbose:
			print( f"line {idxLine:4d}: {rho=:8.2f}, theta={theta*180/np.pi:6.1f} [deg] or " +\
			       f"({x1=:4d},{y1=:4d}), ({x2=:4d},{y2=:4d}) ==> {length=:6.1f}, {cover=:4d}." )
		lines[idxLine] = [x1,y1,x2,y2, rho,theta, length,cover]
	# end for
	idx = np.flip(lines[:,7].argsort())
	lines = lines[idx,:].copy()
	if verbose:
		print( "-- lines ordered by 'cover' after copy() --" )
		for idxLine in range(L):
			(x1,y1,x2,y2, rho,theta, length,cover) = lines[idxLine]
			print( f"line {idxLine:4d}: {rho=:8.2f}, theta={theta*180/np.pi:6.2f} [deg] or " +\
			       f"({x1=:7.2f},{y1=:7.2f}), ({x2=:7.2f},{y2=:7.2f}) " + \
			       f"==> {length=:7.2f}, {cover=:7.2f}." )
	#
	# we should still check if some lines are 'overlapping' 
	thetaLim = 5*np.pi/180  # two lines with angle difference larger than this does NOT match
	if verbose:
		print( f"-- check lines for overlap, thetaLim = {{thetaLim*180/np.pi:6.2f}} --" )
		print( f"      Keep line in row    0 as row    0 in 'lines'.")
	okRows = 1   # lines[okRows-1] is the last good row to return
	tryRow = 1   # the next row to try
	while (okRows < min(nofLines, L)) and (tryRow < L):
		tryRowOK = True
		(x1,y1,x2,y2, rho,theta, length,cover) = lines[tryRow]
		(x2x1, y2y1) = (x2-x1, y2-y1)
		# but tryRow need to be different from all okRows
		(closeIdx, closeTh, closeD1, closeD2, closeD) = (0,180,9999,9999,9999)
		for idxRow in range(okRows):   
			# compare lines[tryRow] to lines[idxRow]
			# find d as distance between the two lines, this can be done in several ways
			(x3,y3,x4,y4, rho3,theta3, length3,cover3) = lines[idxRow]
			(tMin,tMax) = (min(theta,theta3),max(theta,theta3))
			thetaDiff = min(tMax-tMin, tMin+np.pi-tMax)
			# We may have that 
#	An angle difference larger than 5 degrees, or rho difference larger
#	than 'distLines' means that the lines are regarded as unique lines.
#	Perhaps also thetaLim (here 5*pi/180) should be an input argument.
			#if verbose and (thetaDiff < 2*thetaLim):
			#	print( f"line {tryRow=:4d} and line {idxRow=:4d} " + \
			#		   f"(angles: {theta*180/np.pi:6.2f} and {theta3*180/np.pi:6.2f}) " + \
			#		   f"has angle difference of {thetaDiff*180/np.pi:6.2f}." )
			#	print( f"{tryRow=:4d} {lines[tryRow,5]*180/np.pi:6.2f} [deg], " + \
			#	       f"{idxRow=:4d} {lines[idxRow,5]*180/np.pi:6.2f} [deg]." )
			#
			#if (thetaDiff > thetaLim) or (abs(rho3-rho) > distLines): continue  
			#
			# distance between end points of each line
			d1 = ( min(np.hypot(x3-x1,y3-y1), np.hypot(x3-x2,y3-y2)) + \
			       min(np.hypot(x4-x1,y4-y1), np.hypot(x4-x2,y4-y2)) )/2
			# or distance of end points projected onto the other line
			d2 = ( abs(x2x1*(y3-y1)-(x3-x1)*y2y1) + \
			       abs(x2x1*(y4-y1)-(x4-x1)*y2y1) )/(2*length)
			# or a combination
			d = (d1+d2)/2
			#
			if (d < closeD):
				(closeIdx, closeTh, closeD1, closeD2, closeD) = (idxRow,thetaDiff,d1,d2,d)
			#if verbose and (d < 2*distLines): 
			#	print( f"line {tryRow=:4d} and line {idxRow=:4d}, " + \
			#	       f"angle difference {thetaDiff*180/np.pi:6.2f}, " + \
			#	       f"end points distances {d2=:6.1f}, {d=:6.1f}, {d1=:6.1f}." )
			#
			if (d < distLines): # to small distance
				tryRowOK = False
				break   # for loop
			#
		#end for (all idxRow)
		if verbose:
			print( f"line {tryRow:4d} has 'closest' line {closeIdx:4d}, " + \
			       f"angle difference is {closeTh*180/np.pi:6.2f} [deg], " + \
			       f"end points distances d2={closeD2:6.1f}, " + \
			       f"d={closeD:6.1f}, d1={closeD1:6.1f}." )
		#
		if tryRowOK:
			if verbose:
				print( f"  ==> Keep line in row {tryRow=:4d} as row {okRows=:4d} in 'lines'.")
			if (okRows < tryRow): lines[okRows] = lines[tryRow]  
			okRows = okRows + 1
		elif verbose: 
			print( f"  ==> Discard line in row {tryRow=:4d}.")
		#
		tryRow = tryRow + 1
	# end while
	if verbose:
		print( f"-- getBestHoughLines() returns {okRows} lines in numpy array --\n" )
	#
	return lines[:okRows]

#  ..\ELE610\py3\bf1.py  contains the first version of this function
def draw_lines(lines, img, color=(0,255,0), thickness=3, verbose=True):
	"""Draw lines, as returned by HoughLines or HoughLinesP or getBestHoughLines into 
	img, a BGR image of the same size as the binary image used when the lines were found.
	The image has origin in upper left corner, 
	x-axis is to the right (width) and y-axis downwards (height).
	rho is distance from line to origin, 
	and rho is negative if closest point, (x0,y0) in code, has negative y-value.
	theta is angle [radians] from upward in clockwise direction
	Note that color and thickness is as used in cv2.line function,
	color should be a BGR tuple and thickness is not exactly width in pixels.
	see: https://stackoverflow.com/questions/24682797/python-opencv-drawing-line-width
	"""
	if verbose:
		print( f"draw_lines(..): started, {lines.shape=}, {img.shape=}" )
	(w,h) = (img.shape[1], img.shape[0])
	for line in lines:
		# print( f"lines[{no}] = {line = }" )
		# HoughLines:  line = array([[rho, theta]], dtype=float32)   # theta in radians
		# HoughLinesP: line = array([[x1,y1,x2,y2]], dtype=int32)
		if (line.ndim == 2) and (line[0].size == 2):  # lines are from HoughLines
			(rho,theta) = line[0]           
			(a,b) = (np.cos(theta), np.sin(theta))
			(x0,y0) = (a*rho, b*rho)   # point on line closest to origin
			(x1,y1) = (int(x0 + 3000*(-b)), int(y0 + 3000*(a)))
			(x2,y2) = (int(x0 - 3000*(-b)), int(y0 - 3000*(a)))
			# input arguments of clipLine should be int, and returned values are int
			(inSide,(x1,y1),(x2,y2)) = cv2.clipLine((0,0,w,h),(x1,y1),(x2,y2))
			length = np.hypot(x1-x2,y1-y2)
			if verbose:
				print( f"  HL line: {rho=:8.2f}, theta={theta*180/np.pi:6.1f} [deg] " +\
				       f"gives ({x1=:4d},{y1=:4d}), ({x2=:4d},{y2=:4d}), {length=:6.1f}" )
		elif (line.ndim == 2) and (line[0].size == 4):  # lines are from HoughLinesP
			(x1,y1,x2,y2) = line[0]
			length = np.hypot(x1-x2,y1-y2)
			if verbose:
				print( f"  HLP line: ({x1=:4d},{y1=:4d}), ({x2=:4d},{y2=:4d}), {length=:6.1f}" )
		elif (line.ndim == 1) and (line.size == 8):  # lines are from getBestHoughLines
			(x1,y1,x2,y2) = (int(line[0]),int(line[1]),int(line[2]),int(line[3]))
			(rho,theta,length,cover) = (line[4],line[5],line[6],int(line[7]))
			if verbose:
				print( f"  BHL line: ({x1=:4d},{y1=:4d}), ({x2=:4d},{y2=:4d}), " + \
			           f"theta={theta*180.0/np.pi:6.1f} [deg], {length=:6.1f}, {cover=}" )
		else:
			print( f"ERROR in draw_lines(): line not as expected. \n{line=}" )
			return
		# 
		# x2 >= x1
		cv2.line(img,(x1,y1),(x2,y2),color,thickness)
	return

class HoughLinesDialog(QDialog):
	""" A dialog widget for giving parameters to use in 
	showDialog() and tryHoughLines() in class MainWindow or
	toHoughLines() and and tryHoughLines() in appImageViewer1.py
	example of use: 
		d = HoughLinesDialog(parent=self)   # create object (but does not run it)
		t = d.getValues()   # display dialog and return values in tuple t
		(rho, theta, threshold, minLineLength, maxLineGap) = t
		if d.result():   # 1 if accepted (OK), 0 if rejected (Cancel)
			pass   # or something appropriate
	The parent (p) should be a descendant of a QMainWindow (and QWidget), 
	and parent (p) must have defined the following function
		p.tryHoughLines(..)   as used in tryClicked() below (used even if no button for it!)
	"""
	def __init__(self, parent, title="", default=(2.0, 1.0, 500, 25.0, 25.0, 10, 10.0)):
		super().__init__(parent)
		if (isinstance(title, str) and len(title)):
			self.title = title
		else:
			self.title = "Dialog for finding lines in binary image"
		self.setWindowTitle(self.title)
		self.setGeometry(parent.x()+20, parent.y()+120, 500, 650)
		if not (isinstance(default, (tuple,list)) and (len(default)==7)):
			default=(2.0, 1.0, 500, 25.0, 25.0, 10, 10.0)
		headFont = QFont("Arial",11,weight=75)
		labelWidth = 80
		spinBoxWidth = 80
		sliderWidth = 250
		#
		# some general information first 
		labelInfo = QLabel( "Finds lines in a binary image using OpenCV (cv2)." + \
				"Either the standard Hough transform HoughLines(), " + \
				"or the probabilistic Hough transform HoughLinesP(). " + \
				"The input image should be 8-bit, single-channel binary image. " + \
				"The output depends of the function and is explained in " + \
				"the OpenCV documentation. Angle is here given and shown in degrees, " + \
				"but used in radians in the OpenCV functions. " + \
				"Origin is upper left corner, x-axis to the right and y-axis downward. " + \
				"0 or 180 degrees is for vertical lines, " + \
				"45 degrees for lines from lower-left to upper-right, " + \
				"90 degrees for horizontal lines, " + \
				"and 135 degrees for lines from upper-left to lower-right. \n" + \
				"[Try it] button will show all lines found by HoughLines " + \
				"but after [OK] button is clicked appImageViewer may discard " + \
				"some of these lines as given by the bottom two values." )
		labelInfo.setWordWrap(True)
		#
		horizontalLines = []
		for i in range(5):
			a = QFrame()
			a.resize(self.width()-6, 4)
			a.setFrameShape(QFrame.HLine)
			horizontalLines.append(a)
		#
		# qbgHLorHLP, 2 radio buttons 
		self.qrbUseHL = QRadioButton('Use HoughLines() function.')
		self.qrbUseHL.setFont(headFont)
		self.qrbUseHL.setChecked(True)
		self.qrbUseHLP = QRadioButton('Use HoughLinesP() function.')
		self.qrbUseHLP.setFont(headFont)
		self.qbgHLorHLP = QButtonGroup()
		self.qbgHLorHLP.addButton(self.qrbUseHL, 0)
		self.qbgHLorHLP.addButton(self.qrbUseHLP, 1)
		self.qbgHLorHLP.setExclusive(True)
		#
		# An array of strings explaining the 7 values the dialog can adjust
		text = ["Distance resolution of the accumulator in pixels.", 
				"Angle resolution of the accumulator in degrees.", 
				"Accumulator threshold parameter.", 
				"Minimum line length.",
				"Maximum line gap.", 
				"Maximum number of lines to keep and show.", 
				"Discard lines closer to each other than given distance." ]
		# The explanation is followed by labels, spinBoxes and sliders for
		# (rho, theta, threshold, minLineLength, maxLineGap)
		labels = [QLabel("rho: "), QLabel("theta: "), QLabel("threshold: "), 
		          QLabel("minLineLength: "), QLabel("maxLineGap: "),
		          QLabel("nofLines: "), QLabel("distLines: ")]
		for i in range(len(labels)):
			labels[i].setAlignment(Qt.AlignRight)
			labels[i].setFixedWidth(labelWidth)
		#
		self.spinBoxes = [QDoubleSpinBox(), QDoubleSpinBox(), QSpinBox(), 
		                  QDoubleSpinBox(), QDoubleSpinBox(),
		                  QSpinBox(), QDoubleSpinBox()]
		self.spinBoxes[0].setRange(0.0, 50.0)    # rho
		self.spinBoxes[0].setSingleStep(1.0)     
		self.spinBoxes[1].setRange(0.0, 45.0)    # theta
		self.spinBoxes[1].setSingleStep(0.5)     
		self.spinBoxes[2].setRange(0, 4000)      # threshold
		self.spinBoxes[2].setSingleStep(100)     
		self.spinBoxes[3].setRange(0, 200)       # minLineLength
		self.spinBoxes[3].setSingleStep(25.0)     
		self.spinBoxes[4].setRange(0, 200)       # maxLineGap
		self.spinBoxes[4].setSingleStep(25.0)     
		self.spinBoxes[5].setRange(0, 200)       # nofLines
		self.spinBoxes[5].setSingleStep(5)     
		self.spinBoxes[6].setRange(0.0, 100.0)   # distLines
		self.spinBoxes[6].setSingleStep(5.0)     
		for i in range(len(self.spinBoxes)):
			self.spinBoxes[i].setValue(default[i])
			self.spinBoxes[i].setFixedWidth(spinBoxWidth)
			if not ((i == 2) or (i == 5)): self.spinBoxes[i].setDecimals(2)
		#
		sliders = [ QSlider(Qt.Horizontal), QSlider(Qt.Horizontal), 
		            QSlider(Qt.Horizontal), QSlider(Qt.Horizontal), 
		            QSlider(Qt.Horizontal), QSlider(Qt.Horizontal), 
		            QSlider(Qt.Horizontal) ]   
		for i in range(len(sliders)):
			sliders[i].setFixedWidth(sliderWidth)
			sliders[i].setMinimum(0)
			sliders[i].setMaximum(200)
			sliders[i].setTracking(False)  # valueChanged() only when mouse button is released
			relVal = ((self.spinBoxes[i].value()   - self.spinBoxes[i].minimum()) / 
					  (self.spinBoxes[i].maximum() - self.spinBoxes[i].minimum()))
			sliders[i].setSliderPosition( int(200*relVal) )
		# 
		sliders[0].valueChanged.connect(self.slider_0_Changed)
		sliders[1].valueChanged.connect(self.slider_1_Changed)
		sliders[2].valueChanged.connect(self.slider_2_Changed)
		sliders[3].valueChanged.connect(self.slider_3_Changed)
		sliders[4].valueChanged.connect(self.slider_4_Changed)
		sliders[5].valueChanged.connect(self.slider_5_Changed)
		sliders[6].valueChanged.connect(self.slider_6_Changed)
		sliders[0].sliderMoved.connect(self.slider_0_Moved)
		sliders[1].sliderMoved.connect(self.slider_1_Moved)
		sliders[2].sliderMoved.connect(self.slider_2_Moved)
		sliders[3].sliderMoved.connect(self.slider_3_Moved)
		sliders[4].sliderMoved.connect(self.slider_4_Moved)
		sliders[5].sliderMoved.connect(self.slider_5_Moved)
		sliders[6].sliderMoved.connect(self.slider_6_Moved)
		#
		lines = [QBoxLayout(QBoxLayout.LeftToRight), QBoxLayout(QBoxLayout.LeftToRight),
				QBoxLayout(QBoxLayout.LeftToRight), QBoxLayout(QBoxLayout.LeftToRight), 
				QBoxLayout(QBoxLayout.LeftToRight), QBoxLayout(QBoxLayout.LeftToRight), 
				QBoxLayout(QBoxLayout.LeftToRight) ]
		for i in range(len(lines)):
			lines[i].addWidget(labels[i])
			lines[i].addWidget(self.spinBoxes[i])
			lines[i].addWidget(sliders[i])
		#
		tryButton = QPushButton('Try it')
		tryButton.clicked.connect(self.tryClicked)
		okButton = QPushButton('OK')
		okButton.clicked.connect(self.okClicked)
		cancelButton = QPushButton('Cancel')
		cancelButton.clicked.connect(self.cancelClicked)
		#
		layout = QBoxLayout(QBoxLayout.TopToBottom)
		layout.addWidget(labelInfo)
		layout.addWidget(horizontalLines[0])
		#
		layout.addWidget(self.qrbUseHL)
		layout.addWidget(self.qrbUseHLP)
		layout.addWidget(horizontalLines[1])
		#
		# Common arguments
		layout.addWidget(QLabel( "Common arguments for HoughLines() and HoughLinesP():" ))
		for i in range(3):
			layout.addWidget(QLabel(text[i]))
			layout.addLayout(lines[i])
		layout.addWidget(horizontalLines[2])
		# Arguments for HLP
		layout.addWidget(QLabel( "Additional arguments only for HoughLinesP():" ))
		for i in range(3,5):
			layout.addWidget(QLabel(text[i]))
			layout.addLayout(lines[i])
		layout.addWidget(horizontalLines[3])
		# Arguments for selecting lines to show
		for i in range(5,7):
			layout.addWidget(QLabel(text[i]))
			layout.addLayout(lines[i])
		layout.addWidget(horizontalLines[4])
		#
		btnLine = QBoxLayout(QBoxLayout.RightToLeft)
		btnLine.addWidget(okButton)
		btnLine.addWidget(cancelButton)
		btnLine.addStretch()
		btnLine.addWidget(tryButton)
		layout.addLayout(btnLine)
		self.setLayout(layout)
		return
		
	def sliderValueChanged(self,relVal,boxNo,doTry):
		# move slider value into spinBox value
		val = self.spinBoxes[boxNo].minimum() \
		    + (relVal/200)*(self.spinBoxes[boxNo].maximum() - self.spinBoxes[boxNo].minimum())
		if (boxNo == 2) or (boxNo == 5):
			val = int(val)
		self.spinBoxes[boxNo].setValue(val)
		if doTry:
			self.tryClicked()
		return
		
	def slider_0_Changed(self,val):
		self.sliderValueChanged(val,0,True)
		return
		
	def slider_1_Changed(self,val):
		self.sliderValueChanged(val,1,True)
		return
		
	def slider_2_Changed(self,val):
		self.sliderValueChanged(val,2,True)
		return
		
	def slider_3_Changed(self,val):
		self.sliderValueChanged(val,3,True)
		return
		
	def slider_4_Changed(self,val):
		self.sliderValueChanged(val,4,True)
		return
		
	def slider_5_Changed(self,val):
		self.sliderValueChanged(val,5,False)
		return
		
	def slider_6_Changed(self,val):
		self.sliderValueChanged(val,6,False)
		return
		
	def slider_0_Moved(self,val):
		self.sliderValueChanged(val,0,False)
		return
		
	def slider_1_Moved(self,val):
		self.sliderValueChanged(val,1,False)
		return
		
	def slider_2_Moved(self,val):
		self.sliderValueChanged(val,2,False)
		return
		
	def slider_3_Moved(self,val):
		self.sliderValueChanged(val,3,False)
		return
		
	def slider_4_Moved(self,val):
		self.sliderValueChanged(val,4,False)
		return
		
	def slider_5_Moved(self,val):
		self.sliderValueChanged(val,5,False)
		return
		
	def slider_6_Moved(self,val):
		self.sliderValueChanged(val,6,False)
		return
		
	def okClicked(self):
		self.accept()
		return 
		
	def cancelClicked(self):
		self.reject()
		return 
	
	def tryClicked(self):
		"""A slot for the [Try it] button in the dialog window, 
		starts parent().tryHougheLines(t). The tuple t has 5 elements
		for HoughLines checked and 7 elements for HoughLinesP checked.
		As for now, this function is also called when a slider value is changed! 
		"""
		rho = self.spinBoxes[0].value()
		theta = self.spinBoxes[1].value()
		threshold = self.spinBoxes[2].value()
		nofLines = self.spinBoxes[5].value()
		distLines = self.spinBoxes[6].value()
		if self.qrbUseHL.isChecked(): 
			t = (rho, theta, threshold, nofLines, distLines)
		else: 
			minLineLength = self.spinBoxes[3].value()
			maxLineGap = self.spinBoxes[4].value()
			t = (rho, theta, threshold, minLineLength, maxLineGap, nofLines, distLines)
		#
		if getattr(self.parent(), 'tryHoughLines', False):
			self.parent().tryHoughLines(t)
		else:
			print( "The parent() of HoughLinesDialog object has no function 'tryHoughLines'." )
		#
		return 
		
	def getValues(self):
		"""Execute the dialog widget and return the 5 or 7 values."""
		self.exec()
		rho = self.spinBoxes[0].value()
		theta = self.spinBoxes[1].value()
		threshold = self.spinBoxes[2].value()
		nofLines = self.spinBoxes[5].value()
		distLines = self.spinBoxes[6].value()
		if self.qrbUseHL.isChecked(): 
			t = (rho, theta, threshold, nofLines, distLines)
		else: 
			minLineLength = self.spinBoxes[3].value()
			maxLineGap = self.spinBoxes[4].value()
			t = (rho, theta, threshold, minLineLength, maxLineGap, nofLines, distLines)
		#
		return t
	
	#end class HoughLinesDialog
	
#for testing the dialog
class MainWindow(QMainWindow):
	def __init__(self, fName="", parent=None):
		super().__init__(parent)
		self.setWindowTitle("Simple test of HoughLinesDialog")
		self.setGeometry(150, 50, 800, 800)  # initial window position and size
		#
		qaShowDialog = QAction('showDialog', self)
		qaShowDialog.setShortcut('Ctrl+D')
		qaShowDialog.setToolTip('Show the HoughLines dialog')
		qaShowDialog.triggered.connect(self.showDialog)
		#
		qaCloseWin = QAction('closeWin', self)
		qaCloseWin.setShortcut('Ctrl+Q')
		qaCloseWin.setToolTip('Close and quit program')
		qaCloseWin.triggered.connect(self.closeWin)
		#
		mainMenu = self.menuBar()
		fileMenu = mainMenu.addMenu('&File')
		fileMenu.addAction(qaShowDialog)
		fileMenu.addAction(qaCloseWin)
		fileMenu.setToolTipsVisible(True)
		#
		return
	#end function __init__
	
	def showDialog(self):   
		"""Simply run the dialog, and display the returned parameters given in tuple 't'."""
		d = HoughLinesDialog(self)   # create object (but does not run it)
		t = d.getValues()   # display dialog and return values
		print( f"HoughLinesDialog.getValues(): {d.result()=}" )
		if (len(t) == 5):
			(rho, theta, threshold, nofLines, distLines) = t
			print( f"Should do HoughLines({rho=:.2f}, {theta=:.2f}*pi/180, {threshold=})" )
			print( f"and show max {nofLines} lines with difference larger than {distLines}." )
		elif (len(t) == 7):
			(rho, theta, threshold, minLineLength, maxLineGap, nofLines, distLines) = t
			print( f"Should do HoughLinesP({rho=:.2f}, {theta=:.2f}*pi/180, {threshold=}, " + \
			       f"{minLineLength=:.2f}, {maxLineGap=:.2f})" )
			print( f"and show max {nofLines} lines with difference larger than {distLines}." )
		else: 
			print( "showDialog: dialog response 't'  has not expected length." )
		#
		return
	#end function showDialog
	
	def tryHoughLines(self, t):
		"""Simply display the parameters given in tuple 't'."""
		print("tryHoughLines(): now called using:")
		if (len(t) == 5):
			(rho, theta, threshold, nofLines, distLines) = t
			print( f"argument t = ({rho=:.2f}, {theta=:.2f}*pi/180, {threshold=}, " + \
			       f"{nofLines=}, {distLines=:.2f}" )
		elif (len(t) == 7):
			(rho, theta, threshold, minLineLength, maxLineGap, nofLines, distLines) = t
			print( f"argument t = ({rho=:.2f}, {theta=:.2f}*pi/180, {threshold=}, " + \
			       f"{minLineLength=:.2f}, {maxLineGap=:.2f}, " + \
			       f"{nofLines=}, {distLines=:.2f}" )
		else: 
			print( "tryHoughLines: dialog response 't'  has not expected length." )
		#
		return
	
	def closeWin(self):
		print("Close the main window and quit program.")
		self.close()
		return
		
#end class MainWindow
	
if __name__ == '__main__':
	mainApp = QApplication(sys.argv)
	mainWin = MainWindow()
	mainWin.show()
	sys.exit(mainApp.exec_())
	
