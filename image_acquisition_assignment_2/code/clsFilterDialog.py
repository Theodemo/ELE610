#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ../ELE610/py3/clsFilterDialog.py 
#
#  The class FilterDialog
#
# Karl Skretting, UiS, February 2019, June 2022

# Example on how to use file:
#   (C:\...\Anaconda3) C:\..\py3> activate py38
#   (py38) C:\..\py3> python clsFilterDialog.py
# Example on how to use file in appImageViewer1.py:
#   from clsFilterDialog import FilterDialog

import sys
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, 
			QDialog, QLabel, QSpinBox, QComboBox, 
			QRadioButton, QPushButton, QButtonGroup, QFormLayout, QBoxLayout)
import numpy as np

class FilterDialog(QDialog):
	""" A dialog widget for giving parameters to use in a function like
	filterImage() in appImageViewer1.py, or a similar function
	example of use: 
		d = FilterDialog(parent=self)   # create object (but does not run it)
		(h,valS) = d.getValues()   # display dialog and return values
		if d.result():   # 1 if accepted (OK), 0 if rejected (Cancel)
			pass   # or something appropriate
	The parent (p) should be a descendant of a QMainWindow (and QWidget), 
	and parent (p) must have defined the following function
		p.tryFilter(..)   as used in tryClicked() below
	"""
	def __init__(self, parent):
		super().__init__(parent)
		self.title = 'Filter dialog'
		self.setWindowTitle(self.title)
		self.setGeometry(parent.x()+20, parent.y()+120, 400, 200)
		# contents
		useFontSize = 10
		self.vTab = [1.0,0.75,0.5,0.25,0.0,-0.25,-0.5,-0.75,-1.0]
		#
		a = labelFiltSize = QLabel('Size of first filter k x k, k =') 
		a.setFont(QFont("Arial",useFontSize))
		#
		a = self.qsbFiltSize = QSpinBox()
		a.setFont(QFont("Arial",useFontSize))
		a.setRange(1,25)
		a.setValue(11)
		a.setSingleStep(2)
		a.setMinimumWidth(60)
		a.valueChanged.connect(self.tryClicked)
		#
		a = labelFiltValues = QLabel( "Values for blocks in first filter" ) 
		a.setFont(QFont("Arial",useFontSize))
		a = self.qcbUpperLeftValue = QComboBox()
		a.setFont(QFont("Arial",useFontSize))
		for v in self.vTab:
			a.addItem( f"Upper Left = {v:4.2f}" )
		a.setCurrentIndex(0)
		a.setMinimumWidth(60)
		# a.currentIndexChanged.connect(self.tryClicked)
		a = self.qcbUpperRightValue = QComboBox()
		a.setFont(QFont("Arial",useFontSize))
		for v in self.vTab:
			a.addItem( f"Upper Right = {v:4.2f}" )
		a.setCurrentIndex(0)
		a.setMinimumWidth(60)
		# a.currentIndexChanged.connect(self.tryClicked)
		a = self.qcbLowerLeftValue = QComboBox()
		a.setFont(QFont("Arial",useFontSize))
		for v in self.vTab:
			a.addItem( f"Lower Left = {v:4.2f}" )
		a.setCurrentIndex(len(self.vTab)-1)
		a.setMinimumWidth(60)
		# a.currentIndexChanged.connect(self.tryClicked)
		a = self.qcbLowerRightValue = QComboBox()
		a.setFont(QFont("Arial",useFontSize))
		for v in self.vTab:
			a.addItem( f"Lower Right = {v:4.2f}" )
		a.setCurrentIndex(len(self.vTab)-1)
		a.setMinimumWidth(60)
		# a.currentIndexChanged.connect(self.tryClicked)
		#
		labelS = QLabel( "Size of separable smoothing filter" ) 
		labelS.setFont(QFont("Arial",useFontSize))
		qrbS1 = QRadioButton("none")
		qrbS3 = QRadioButton("3x3")
		qrbS5 = QRadioButton("5x5")
		qrbS7 = QRadioButton("7x7")
		qrbS9 = QRadioButton("9x9")
		qrbS5.setChecked(True)
		self.qbgS = QButtonGroup()
		self.qbgS.addButton(qrbS1, 1)
		self.qbgS.addButton(qrbS3, 3)
		self.qbgS.addButton(qrbS5, 5)
		self.qbgS.addButton(qrbS7, 7)
		self.qbgS.addButton(qrbS9, 9)
		self.qbgS.buttonClicked.connect(self.tryClicked)
		#
		tryButton = QPushButton("Try it")
		tryButton.clicked.connect(self.tryClicked)
		okButton = QPushButton("OK")
		okButton.clicked.connect(self.okClicked)
		cancelButton = QPushButton("Cancel")
		cancelButton.clicked.connect(self.cancelClicked)
		# 
		layout = QFormLayout()
		line1 = QBoxLayout(0)
		line1.addWidget(labelFiltSize)
		# line1.addStretch()
		line1.addWidget(self.qsbFiltSize)
		layout.addWidget(  QLabel("A sketch for a filter options dialog, it should be improved sometime.") )
		layout.addRow(line1)
		layout.addRow(labelFiltValues)
		line2 = QBoxLayout(0)
		line2.addStretch()
		line2.addWidget(self.qcbUpperLeftValue)
		line2.addWidget(self.qcbUpperRightValue)
		line2.addStretch()
		layout.addRow(line2)
		line3 = QBoxLayout(0)
		line3.addStretch()
		line3.addWidget(self.qcbLowerLeftValue)
		line3.addWidget(self.qcbLowerRightValue)
		line3.addStretch()
		layout.addRow(line3)
		#
		layout.addRow(labelS)
		sLine = QBoxLayout(0)
		sLine.addWidget(qrbS1)
		sLine.addWidget(qrbS3)
		sLine.addWidget(qrbS5)
		sLine.addWidget(qrbS7)
		sLine.addWidget(qrbS9)
		sLine.addStretch()
		layout.addRow(sLine)
		btnLine = QBoxLayout(1)
		btnLine.addWidget(okButton)
		btnLine.addWidget(cancelButton)
		btnLine.addStretch()
		btnLine.addWidget(tryButton)
		layout.addRow(btnLine)
		self.setLayout(layout)
		return
		
	def getFilters(self):
		v = self.qsbFiltSize.value()
		if (v < 3):
			H = np.zeros(1)
		else:
			H = np.zeros((v,v))
			H[:(v//2),:(v//2)] = self.vTab[self.qcbUpperLeftValue.currentIndex()]
			H[:(v//2),(v//2+1):] = self.vTab[self.qcbUpperRightValue.currentIndex()]
			H[(v//2+1):,:(v//2)] = self.vTab[self.qcbLowerLeftValue.currentIndex()]
			H[(v//2+1):,(v//2+1):] = self.vTab[self.qcbLowerRightValue.currentIndex()]
		valS = self.qbgS.checkedId()
		return (H,valS)
		
	def okClicked(self):
		self.accept()
		return 
		
	def cancelClicked(self):
		self.reject()
		return 
	
	def tryClicked(self,ignored=None):  # or other thing change that should try (do) the filtering
		p = self.parent()
		(filterKernel,valS) = self.getFilters()
		p.tryFilter(filterKernel,valS)
		return 
		
	def getValues(self):
		self.exec()
		return self.getFilters()
	#end class FilterDialog
	
#for testing the dialog
class MainWindow(QMainWindow):
	def __init__(self, fName="", parent=None):
		super().__init__(parent)
		self.setWindowTitle("Simple test of FilterDialog")
		self.setGeometry(150, 50, 1400, 800)  # initial window position and size
		#
		qaShowDialog = QAction('showDialog', self)
		qaShowDialog.setShortcut('Ctrl+D')
		qaShowDialog.setToolTip('Show the filter dialog')
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
		d = FilterDialog(parent=self)   # create object (but does not run it)
		(h,valS) = d.getValues()   # display dialog and return values
		print( (f"FilterDialog getValues(): h.shape = {str(h.shape)}, " + 
		        f"valS = {valS}, d.result() is {d.result()}") )
		return
	#end function showDialog
	
	def tryFilter(self, h, valS):
		print( f"tryFilter(): now called using h.shape = {str(h.shape)},  valS = {valS}" )
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
	
