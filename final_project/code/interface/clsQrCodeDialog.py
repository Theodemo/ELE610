#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QDialog, 
			QPushButton, QFormLayout, QBoxLayout,QSpinBox,QSlider)

class QrCodeDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.title = 'QRcode Dialog'
        self.setWindowTitle(self.title)
        self.setGeometry(parent.x()+20, parent.y()+120, 320, 130) 
             
        self.qsbDiameter = QSpinBox()
        self.qsbDiameter.setRange(0, 255)
        self.qsbDiameter.setValue(10)
        
        self.qsbSigmaColor = QSpinBox()
        self.qsbSigmaColor.setRange(0, 255)
        self.qsbSigmaColor.setValue(20)

        
        self.qsbSigmaSpace = QSpinBox()
        self.qsbSigmaSpace.setRange(0, 255)
        self.qsbSigmaSpace.setValue(20)


        tryButton = QPushButton('Try it')
        tryButton.clicked.connect(self.tryClicked)
        okButton = QPushButton('OK')
        okButton.clicked.connect(self.okClicked)
        cancelButton = QPushButton('Cancel')
        cancelButton.clicked.connect(self.cancelClicked)
        
        layout = QFormLayout()
        layout.addRow('Diameter of the pixel neighborhood: ', self.qsbDiameter)
        layout.addRow('Filter sigma in the color space: ', self.qsbSigmaColor)
        layout.addRow('Filter sigma in the coordinate space: ', self.qsbSigmaSpace)

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
        values = (self.qsbDiameter.value(), self.qsbSigmaColor.value(), self.qsbSigmaSpace.value())
        p.tryQrCode(*values)
        return
    
         
    def getValues(self):
        self.exec()
        valDiameter = self.qsbDiameter.value()
        valSigmaColor = self.qsbSigmaColor.value()
        valSigmaSpace = self.qsbSigmaSpace.value()
        
        return valDiameter, valSigmaColor, valSigmaSpace
	
#for testing the dialog
class MainWindow(QMainWindow):
    def __init__(self, fName="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Simple test of QRCodeDialog")
        self.setGeometry(150, 50, 800, 600)
        #
        qaShowDialog = QAction('showDialog', self)
        qaShowDialog.setShortcut('Ctrl+D')
        qaShowDialog.setToolTip('Show the QrCode dialog')
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
    
    def showDialog(self):   
        d = QrCodeDialog(self)   # create object (but does not run it)
        t = d.getValues()   # display dialog and return values
        print( f"QrCodeDialog getValues(): t = {t}, d.result() is {d.result()}" )
        return

    def tryQrCode(self, valDiameter=0, valSigmaColor=0, valSigmaSpace=0):
        print(f"tryQrCode(): diameter = {valDiameter}, sigmaColor = {valSigmaColor}, sigmaSpace = {valSigmaSpace}")  

    def closeWin(self):
        print( "Close the main window and quit program" )
        self.close()
        return
		
if __name__ == '__main__':
	mainApp = QApplication(sys.argv)
	mainWin = MainWindow()
	mainWin.show()
	sys.exit(mainApp.exec_())
	
