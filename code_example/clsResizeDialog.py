#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ../ELE610/py3/clsResizeDialog.py 
#
#  The class ResizeDialog
#
# Karl Skretting, UiS, November 2021, June 2022

# Example on how to use file:
#   (C:\...\Anaconda3) C:\..\py3> activate py38
#   (py38) C:\..\py3> python clsResizeDialog.py
# Example on how to use file in appImageViewer1.py:
#   from clsResizeDialog import ResizeDialog

import sys
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, 
			QDialog, QLabel, QSpinBox, QSlider, 
			QRadioButton, QPushButton, QButtonGroup, QFormLayout, QBoxLayout)

class ResizeDialog(QDialog):
	""" A dialog widget for giving parameters to use in a function like
	resizeImage() in appImageViewer1.py, or a similar function
	example of use: 
		d = ResizeDialog(parent=self)   # create object (but does not run it)
		(newWidth, newHight) = d.getValues()   # display dialog and return values, 
		if d.result():   # 1 if accepted (OK), 0 if rejected (Cancel)
			pass   # or something appropriate
	The parent (p) should be a descendant of a QMainWindow (and QWidget)
	and have an element p.npImage
	"""
	def __init__(self, parent):
		super().__init__(parent)
		self.title = 'Resize dialog for resizing current image'
		self.setWindowTitle(self.title)
		self.setGeometry(parent.x()+20, parent.y()+120, 400, 250)
		(self.wIm, self.hIm) = self.getImSize()
		# contents
		a = self.qsbPercent = QSpinBox()
		a.setRange(10, 400)
		a.setValue(100)
		a.valueChanged.connect(self.percentChanged)
		#
		a = self.qsbWidth = QSpinBox()
		a.setRange(self.wIm//10, self.wIm*4)
		a.setValue(self.wIm)
		a.valueChanged.connect(self.widthChanged)
		#
		a = self.qsbHight = QSpinBox()
		a.setRange(self.hIm//10, self.hIm*4)
		a.setValue(self.hIm)
		a.valueChanged.connect(self.hightChanged)
		#
		# a slider for percent change
		a = self.slider = QSlider(Qt.Horizontal)
		a.setMinimum(10)
		a.setMaximum(400)
		# a.setTracking(False)
		a.setSliderPosition(100)
		a.sliderMoved.connect(self.sliderMoved)
		#
		okButton = QPushButton('OK')
		okButton.clicked.connect(self.okClicked)
		cancelButton = QPushButton('Cancel')
		cancelButton.clicked.connect(self.cancelClicked)
		btnLine = QBoxLayout(1)
		btnLine.addWidget(okButton)
		btnLine.addWidget(cancelButton)
		btnLine.addStretch()
		#
		layout = QFormLayout()
		layout.addRow(QLabel( "Resize image and keep aspect ratio." ))
		layout.addRow(QLabel( f"Current size (w x h): ({self.wIm} x {self.hIm})" ))
		layout.addRow(self.slider)
		layout.addRow( "Scale in percent: ", self.qsbPercent)
		layout.addRow(QLabel( "The values below are returned, changing these do not keep aspect ratio." ))
		layout.addRow('New width: ', self.qsbWidth)
		layout.addRow('New hight: ', self.qsbHight)
		layout.addRow(btnLine)
		self.setLayout(layout)
		return
		
	def getImSize(self):
		try:
			(wIm,hIm) = (self.parent().npImage.shape[1], self.parent().npImage.shape[0])
		except AttributeError as e:
			print('Error in clsResizeDialog: no npImage attribute for parent()')
			(wIm,hIm) = (0,0)
		return (wIm,hIm)
		
	def okClicked(self):
		self.accept()
		return 
		
	def cancelClicked(self):
		self.reject()
		return 
	
	# avoid update everything 
	def sliderMoved(self,val):
		self.qsbPercent.setValue(val)
		return
		
	def percentChanged(self,val):
		self.slider.setSliderPosition(val)
		(new_w, new_h) = ((self.wIm*val)//100, (self.hIm*val)//100)
		self.qsbWidth.setValue(new_w)
		self.qsbHight.setValue(new_h)
		return
	
	def widthChanged(self,new_w):
		# do not update any other fields!
		return
	
	def hightChanged(self,new_h):
		# do not update any other fields!
		return
	
	def getValues(self):
		self.exec()
		new_w = self.qsbWidth.value()
		new_h = self.qsbHight.value()
		return (new_w, new_h)
	#end class ResizeDialog
	
#for testing the dialog, a simple minimal MainWindow
class MainWindow(QMainWindow):
	def __init__(self, fName="", parent=None):
		super().__init__(parent)
		self.setWindowTitle("Simple test of ResizeDialog")
		self.setGeometry(150, 50, 1400, 800)  # initial window position and size
		self.npImage = np.ones((40,60),dtype=np.uint8)
		#
		qaShowDialog = QAction('showDialog', self)
		qaShowDialog.setShortcut('Ctrl+D')
		qaShowDialog.setToolTip('Show the resize dialog')
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
		(w,h) = (self.npImage.shape[1], self.npImage.shape[0])
		d = ResizeDialog(self)   # create object (but does not run it)
		(newWidth, newHight) = d.getValues()   # display dialog and return values
		print( f"Current size (w x h): ({w} x {h})" )
		print( (f"ResizeDialog getValues(): newWidth = {newWidth}," +
		        f" newHight = {newHight}, d.result() is {d.result()}") )
		return
	#end function showDialog
	
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
	
