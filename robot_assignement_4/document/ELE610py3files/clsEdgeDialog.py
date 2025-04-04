#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ../ELE610/py3/clsEdgeDialog.py 
#
#  The class EdgeDialog
#
# Karl Skretting, UiS, February 2019, June 2022

# Example on how to use file:
#   (C:\...\Anaconda3) C:\..\py3> activate py38
#   (py38) C:\..\py3> python clsEdgeDialog.py
# Example on how to use file in appImageViewer1.py:
#   from clsEdgeDialog import EdgeDialog

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QDialog, QLabel, 
			QRadioButton, QPushButton, QButtonGroup, QFormLayout, QBoxLayout)

class EdgeDialog(QDialog):
	""" A dialog widget for giving parameters to use in a function like
	toEdges() in appImageViewer1.py, or a similar function
	example of use: 
		d = EdgeDialog(parent=self)   # create object (but does not run it)
		(valK,valS) = d.getValues()   # display dialog and return values
		if d.result():   # 1 if accepted (OK), 0 if rejected (Cancel)
			pass   # or something appropriate
	The parent (p) should be a descendant of a QMainWindow (and QWidget), 
	and parent (p) must have defined the following function
		p.tryEdges(..)   as used in tryClicked() below (used even if no button for it!)
	"""
	def __init__(self, parent):
		super().__init__(parent)
		self.title = 'Edge dialog for making edge image'
		self.setWindowTitle(self.title)
		self.setGeometry(parent.x()+20, parent.y()+120, 320, 130)
		# contents
		labelK = QLabel('Select k-size to use in Sobel filters.') 
		qrbK3 = QRadioButton('k=3')
		qrbK5 = QRadioButton('k=5')
		qrbK7 = QRadioButton('k=7')
		qrbK9 = QRadioButton('k=9')
		qrbK3.setChecked(True)
		self.qbgK = QButtonGroup()
		self.qbgK.addButton(qrbK3, 3)
		self.qbgK.addButton(qrbK5, 5)
		self.qbgK.addButton(qrbK7, 7)
		self.qbgK.addButton(qrbK9, 9)
		self.qbgK.buttonClicked.connect(self.tryClicked)
		#
		labelS = QLabel('Select size of separable smoothing filter.') 
		qrbS1 = QRadioButton('none')
		qrbS3 = QRadioButton('3x3')
		qrbS5 = QRadioButton('5x5')
		qrbS7 = QRadioButton('7x7')
		qrbS9 = QRadioButton('9x9')
		qrbS5.setChecked(True)
		self.qbgS = QButtonGroup()
		self.qbgS.addButton(qrbS1, 1)
		self.qbgS.addButton(qrbS3, 3)
		self.qbgS.addButton(qrbS5, 5)
		self.qbgS.addButton(qrbS7, 7)
		self.qbgS.addButton(qrbS9, 9)
		self.qbgS.buttonClicked.connect(self.tryClicked)
		#
		tryButton = QPushButton('Try it')
		tryButton.clicked.connect(self.tryClicked)
		okButton = QPushButton('OK')
		okButton.clicked.connect(self.okClicked)
		cancelButton = QPushButton('Cancel')
		cancelButton.clicked.connect(self.cancelClicked)
		#
		layout = QFormLayout()
		layout.addRow(labelK)
		kLine = QBoxLayout(0)
		kLine.addWidget(qrbK3)
		kLine.addWidget(qrbK5)
		kLine.addWidget(qrbK7)
		kLine.addWidget(qrbK9)
		kLine.addStretch()
		layout.addRow(kLine)
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
		#btnLine.addWidget(tryButton)
		layout.addRow(btnLine)
		self.setLayout(layout)
		return
		
	def getKandS(self):
		valK = self.qbgK.checkedId()
		valS = self.qbgS.checkedId()
		return (valK,valS)
		
	def okClicked(self):
		self.accept()
		return 
		
	def cancelClicked(self):
		self.reject()
		return 
	
	def tryClicked(self,ignored=None):
		p = self.parent()
		(valK,valS) = self.getKandS()
		p.tryEdges(valK,valS)
		return 
		
	def getValues(self):
		self.exec()
		return self.getKandS()
	#end class EdgeDialog
	
#for testing the dialog
class MainWindow(QMainWindow):
	def __init__(self, fName="", parent=None):
		super().__init__(parent)
		self.setWindowTitle("Simple test of EdgeDialog")
		self.setGeometry(150, 50, 800, 600)  # initial window position and size
		#
		qaShowDialog = QAction('showDialog', self)
		qaShowDialog.setShortcut('Ctrl+D')
		qaShowDialog.setToolTip('Show the edge dialog')
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
		d = EdgeDialog(parent=self)   # create object (but does not run it)
		(valK,valS) = d.getValues()   # display dialog and return values
		print( f"EdgeDialog getValues(): valK = {valK},  valS = {valS}, d.result() is {d.result()}" )
		return
	#end function showDialog
	
	def tryEdges(self, valK, valS):
		print( f"tryEdges(): now called using valK = {valK},  valS = {valS}" )
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
	
