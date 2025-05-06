#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ../ELE610/py3/clsThresholdDialog.py 
#
#  The class ThresholdDialog
#
# Karl Skretting, UiS, February 2019, June 2022

# Example on how to use file:
#   (C:\...\Anaconda3) C:\..\py3> activate py38
#   (py38) C:\..\py3> python clsThresholdDialog.py
# Example on how to use file in appImageViewer1.py:
#   from clsThresholdDialog import ThresholdDialog

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, 
			QDialog, QLabel, QSpinBox, QSlider, 
			QRadioButton, QPushButton, QButtonGroup, QFormLayout, QBoxLayout)

class ThresholdDialog(QDialog):
	""" A dialog widget for giving parameters to use in a function like
	toBinary() in appImageViewer1.py, or a similar function
	example of use: 
		d = ThresholdDialog(parent=self)   # create object (but does not run it)
		t = d.getValues()   # display dialog and return values
		if d.result():   # 1 if accepted (OK), 0 if rejected (Cancel)
			pass   # or something appropriate
	The parent (p) should be a descendant of a QMainWindow (and QWidget), 
	and parent (p) must have defined the following function
		p.tryBinary(..)   as used in tryClicked() below
	"""
	def __init__(self, parent):
		super().__init__(parent)
		self.title = 'Thresholding dialog for making binary image'
		self.setWindowTitle(self.title)
		self.setGeometry(parent.x()+20, parent.y()+120, 400, 150)
		# contents
		self.rbVal = QRadioButton('Use &value below as threshold')
		self.qsbThreshold = QSpinBox()
		self.qsbThreshold.setRange(0, 255)
		self.qsbThreshold.setValue(127)
		slider = QSlider(Qt.Horizontal)
		slider.setMinimum(0)
		slider.setMaximum(255)
		slider.setTracking(False)
		slider.setSliderPosition(127)
		slider.sliderMoved.connect(self.sliderMoved)
		self.rbOtsu = QRadioButton('Use value from &Otsu method as threshold')
		self.rbOtsu.setChecked(True)
		tryButton = QPushButton('Try it')
		tryButton.clicked.connect(self.tryClicked)
		okButton = QPushButton('OK')
		okButton.clicked.connect(self.okClicked)
		cancelButton = QPushButton('Cancel')
		cancelButton.clicked.connect(self.cancelClicked)
		#
		layout = QFormLayout()
		layout.addRow(self.rbVal)
		layout.addRow('Threshold value: ', self.qsbThreshold)
		layout.addRow(slider)
		layout.addRow(self.rbOtsu)
		btnLine = QBoxLayout(1)
		btnLine.addWidget(okButton)
		btnLine.addWidget(cancelButton)
		btnLine.addStretch()
		btnLine.addWidget(tryButton)
		layout.addRow(btnLine)
		self.setLayout(layout)
		return
		
	def okClicked(self):
		self.accept()
		return 
		
	def cancelClicked(self):
		self.reject()
		return 
	
	def tryClicked(self):
		p = self.parent()
		if self.rbVal.isChecked():
			val = self.qsbThreshold.value()
		else: 
			val = 0
		p.tryBinary(t=val)
		return 
		
	def sliderMoved(self,val):
		self.qsbThreshold.setValue(val)
		self.rbVal.setChecked(True)
		self.parent().tryBinary(t=val)
		return
		
	def getValues(self):
		self.exec()
		if self.rbVal.isChecked():
			val = self.qsbThreshold.value()
		else: 
			val = 0
		return val
	#end class ThresholdDialog
	
#for testing the dialog
class MainWindow(QMainWindow):
	def __init__(self, fName="", parent=None):
		super().__init__(parent)
		self.setWindowTitle("Simple test of ThresholdDialog")
		self.setGeometry(150, 50, 1400, 800)  # initial window position and size
		#
		qaShowDialog = QAction('showDialog', self)
		qaShowDialog.setShortcut('Ctrl+D')
		qaShowDialog.setToolTip('Show the threshold dialog')
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
		d = ThresholdDialog(self)   # create object (but does not run it)
		t = d.getValues()   # display dialog and return values
		print( f"ThresholdDialog getValues(): t = {t}, d.result() is {d.result()}" )
		return
	#end function showDialog
	
	def tryBinary(self, t=0):  
		print( f"tryBinary(): now called using t = {t}" )
		return
	
	def closeWin(self):
		print( "Close the main window and quit program" )
		self.close()
		return
		
#end class MainWindow
	
if __name__ == '__main__':
	mainApp = QApplication(sys.argv)
	mainWin = MainWindow()
	mainWin.show()
	sys.exit(mainApp.exec_())
	
