#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ../ELE610/py3/clsHoughCirclesDialog.py 
#
#  The class HoughCirclesDialog
# 
# Karl Skretting, UiS, November 2020, June 2022

# Example on how to use file:
#   (C:\...\Anaconda3) C:\..\py3> activate py38
#   (py38) C:\..\py3> python clsHoughCirclesDialog.py
# Example on how to use file in appImageViewer3.py:
#   from clsHoughCirclesDialog import HoughCirclesDialog

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QFrame, QPushButton, 
			QDialog, QLabel, QSlider, QSpinBox, QDoubleSpinBox, QBoxLayout)
		# QRadioButton, QButtonGroup, , QGridLayout, QFormLayout

class HoughCirclesDialog(QDialog):
	"""A dialog widget for giving parameters to use in the OpenCV HoughCircles method
	
	From the calling program it should be possible to try the parameters, 
	visualize the results by drawing the circles on image, 
	and then continue trying other values.
	example of use: 
		d = HoughCirclesDialog(parent=self)   # create object (but does not run it)
		t = d.getValues()   # display dialog and return 7 values
		if d.result():   # 1 if accepted (OK), 0 if rejected (Cancel)
			pass   # or something appropriate
	The parent (p) should be a descendant of a QMainWindow (and QWidget), 
	and parent (p) must have defined the following function
		p.tryHoughCircles(..)   as used in tryClicked() below
	"""
	def __init__(self, parent, title="", default=(2.0,40.0,100.0,60.0,20,60,20)):
		"""Initialize the HoughCirclesDialog 
		A title, type str, and 
		a tuple or list with 6-7 initial (default) values may be given, 
		i.e. default = (dp, minDist, param1, param2, minRadius, maxRadius, nofCircles)
		the 6 first are parameters for HoughCircles and the last is max number of circles 
		to show (in appImageViewer3)
		"""
		super().__init__(parent)
		if (isinstance(title, str) and len(title)):
			self.title = title
		else:
			self.title = 'Dialog widget to change parameters used in OpenCV HoughCircles() method'
		#
		if not (isinstance(default, (tuple,list)) and ((len(default)==6) or (len(default)==7))):
			default=(2.0, 40.0, 100.0, 60.0, 20, 60, 20)
		elif (len(default)==6):
			default = tuple(default) + (20,)
		#
		self.setWindowTitle(self.title)
		self.setGeometry(parent.x()+20, parent.y()+120, 420, 400)
		headFont = QFont("Arial",11,weight=75)
		labelWidth = 60
		spinBoxWidth = 80
		sliderWidth = 250
		# contents
		horizontalLine1 = QFrame()
		horizontalLine1.resize(self.width(), 4)
		horizontalLine1.setFrameShape(QFrame.HLine)
		horizontalLine2 = QFrame()
		horizontalLine2.resize(self.width(), 4)
		horizontalLine2.setFrameShape(QFrame.HLine)
		#
		headText = QLabel('Parameters in cv2.HoughCircles(..)')
		headText.setFont(headFont)
		# text from https://docs.opencv.org/3.4/ ...
		# An array of 7 strings (each 1 to more lines)
		text = ["Inverse ratio of the accumulator resolution to the image resolution.\n" + 
				"For example, if dp=1, the accumulator has the same resolution as the input image.\n" + 
				"If dp=2 , the accumulator has half as big width and height.", 
				"Minimum distance between the centers of the detected circles.\n" +
				"If the parameter is too small, multiple neighbor circles may be\n" + 
				"falsely detected in addition to a true one. If it is too large,\n" + 
				"some circles may be missed.", 
				"First method-specific parameter. In case of HOUGH_GRADIENT,\n" + 
				"it is the higher threshold of the two passed to the Canny edge\n" + 
				"detector (the lower one is twice smaller).", 
				"Second method-specific parameter. In case of HOUGH_GRADIENT,\n" + 
				"it is the accumulator threshold for the circle centers at the detection stage.\n" + 
				"The smaller it is, the more false circles may be detected.\n" + 
				"Circles, corresponding to the larger accumulator values, will be returned first.",
				"Minimum circle radius.", 
				"Maximum circle radius. If <= 0, uses the maximum image dimension.\n" + 
				"If < 0, returns centers without finding the radius.",
				"Maximum number of circles to display (in parent())" ]
		# 7 labels, 7 spinBoxes and 7 sliders:
		labels = [QLabel("dp: "), QLabel("minDist: "), QLabel("param1: "), 
		          QLabel("param2: "), QLabel("minRadius: "), 
		          QLabel("maxRadius: "), QLabel("maxCircles: ")]
		for i in range(len(labels)):
			labels[i].setAlignment(Qt.AlignRight)
			labels[i].setFixedWidth(labelWidth)
		#
		self.spinBoxes = [QDoubleSpinBox(), QDoubleSpinBox(), QDoubleSpinBox(), 
		                  QDoubleSpinBox(), QSpinBox(), 
		                  QSpinBox(), QSpinBox()]
		self.spinBoxes[0].setRange(0.5, 5.0)     # dp
		self.spinBoxes[0].setSingleStep(0.1)     
		self.spinBoxes[1].setRange(5.0, 400.0)   # minDist
		self.spinBoxes[1].setSingleStep(5.0)     
		self.spinBoxes[2].setRange(5.0, 400.0)   # param1
		self.spinBoxes[2].setSingleStep(5.0)     
		self.spinBoxes[3].setRange(1.0, 400.0)   # param2
		self.spinBoxes[3].setSingleStep(5.0)     
		self.spinBoxes[4].setRange(5, 200)       # minRadius
		self.spinBoxes[4].setSingleStep(5)     
		self.spinBoxes[5].setRange(-1, 400)      # maxRadius
		self.spinBoxes[5].setSingleStep(5)     
		self.spinBoxes[6].setRange(1, 200)       # maxCircles
		for i in range(len(self.spinBoxes)):
			self.spinBoxes[i].setValue(default[i])
			self.spinBoxes[i].setFixedWidth(spinBoxWidth)
			if (i<4):
				self.spinBoxes[i].setDecimals(1)
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
		btnLine = QBoxLayout(1)
		btnLine.addWidget(okButton)
		btnLine.addWidget(cancelButton)
		btnLine.addStretch()
		btnLine.addWidget(tryButton)
		#
		layout = QBoxLayout(QBoxLayout.TopToBottom)
		layout.addWidget(headText)
		for i in range(len(lines)):
			if (i == (len(lines)-1)):  # before last line; lines[6]
				layout.addWidget(horizontalLine1)
			layout.addWidget(QLabel(text[i]))
			layout.addLayout(lines[i])
		#
		layout.addWidget(horizontalLine2)
		layout.addLayout(btnLine)
		#
		self.setLayout(layout)
		return
		
	def sliderValueChanged(self,relVal,boxNo,doTry):
		val = self.spinBoxes[boxNo].minimum() + (relVal/200)*(self.spinBoxes[boxNo].maximum() - self.spinBoxes[boxNo].minimum())
		if (boxNo >= 4):
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
		self.sliderValueChanged(val,5,True)
		return
		
	def slider_6_Changed(self,val):
		self.sliderValueChanged(val,6,True)
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
		"""A slot for the [Try it] button in the dialog window, starts parent().tryHoughCircles(t)"""
		dp = self.spinBoxes[0].value()
		minDist = self.spinBoxes[1].value()
		param1 = self.spinBoxes[2].value()
		param2 = self.spinBoxes[3].value()
		minRadius = self.spinBoxes[4].value()
		maxRadius = self.spinBoxes[5].value()
		maxCircles = self.spinBoxes[6].value()
		t = (dp, minDist, param1, param2, minRadius, maxRadius, maxCircles)
		self.parent().tryHoughCircles(t)
		return 
		
	def getValues(self):
		"""Execute the dialog widget and return the 7 values."""
		self.exec()
		dp = self.spinBoxes[0].value()
		minDist = self.spinBoxes[1].value()
		param1 = self.spinBoxes[2].value()
		param2 = self.spinBoxes[3].value()
		minRadius = self.spinBoxes[4].value()
		maxRadius = self.spinBoxes[5].value()
		maxCircles = self.spinBoxes[6].value()
		t = (dp, minDist, param1, param2, minRadius, maxRadius, maxCircles)
		return t
	#end class HoughCirclesDialog
	
#for testing the dialog
class MainWindow(QMainWindow):
	def __init__(self, fName="", parent=None):
		super().__init__(parent)
		self.setWindowTitle("Simple test of HoughCirclesDialog")
		self.setGeometry(150, 50, 1400, 800)  # initial window position and size
		#
		qaShowDialog = QAction('showDialog', self)
		qaShowDialog.setShortcut('Ctrl+D')
		qaShowDialog.setToolTip('Show the HoughCircles dialog')
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
		d = HoughCirclesDialog(self)   # create object (but does not run it)
		t = d.getValues()   # display dialog and return values
		(dp, minDist, param1, param2, minRadius, maxRadius, maxCircles) = t
		print(f"HoughCirclesDialog getValues(): d.result() is {d.result()}")
		print( (f"t = (dp={dp}, minDist={minDist}, param1={param1}, param2={param2}, " + 
				f"minRadius={minRadius}, maxRadius={maxRadius}, maxCircles={maxCircles})") )
		return
	#end function showDialog
	
	def tryHoughCircles(self, t):
		"""Simply display the parameters given in tuple 't'."""
		(dp, minDist, param1, param2, minRadius, maxRadius, maxCircles) = t
		print("tryHoughCircles(): now called using:")
		print( (f"t = (dp={dp}, minDist={minDist}, param1={param1}, param2={param2}, " + 
				f"minRadius={minRadius}, maxRadius={maxRadius}, maxCircles={maxCircles})") )
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
	
