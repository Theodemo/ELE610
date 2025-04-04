#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ../ELE610/py3/appCalculator.pyw
# fra https://doc.qt.io/qt-5.10/qtwidgets-widgets-calculator-example.html
# Karl Skretting, UiS, mars 2018

# Example on how to use file:
# (py38) C:\..\py3> pythonw appCalculator.pyw 

import sys
from math import sqrt
from PyQt5.QtWidgets import (QApplication, QWidget, QSizePolicy, QToolButton, QLineEdit,
		QLayout, QGridLayout, QPushButton )
from PyQt5.QtCore import Qt
 
class Button(QPushButton):        #  QToolButton or QPushButton  ??  

	def __init__(self, text = '', parent = None):
		super().__init__(parent)        
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
		self.setText(text)
		return
		
	def sizeHint(self):        # note self is needed in Python but not in C++ (here self is the object itself, class Button)
		# size = QToolButton.sizeHint(QToolButton())  # or
		size = QPushButton().sizeHint()   # but not
		# size = QToolButton.sizeHint()   # or
		# size = QToolButton.sizeHint(self)       # QToolButton is smaller than QPushButton 
		# tested and got:  >>>app = QApplication(sys.argv) >>> tb = QToolButton() >>> tb.sizeHint()  --> PyQt5.QtCore.QSize(23, 22)
		#                                                  >>> pb = QPushButton() >>> pb.sizeHint()  --> PyQt5.QtCore.QSize(32, 23)
		# size.rheight() += 20  # size.rheight() returns a reference to the height (which can not be assigned a value in Python)
		size.setHeight( size.height() + 20 )
		size.setWidth = ( 10 + max(size.width(), size.height()) )
		return size
# end of class Button

class Calculator(QWidget):

	def __init__(self, parent = None):
		super().__init__(parent)
		#
		# much initialization below (done once for each new object)
		self.sumInMemory = 0.0
		self.sumSoFar = 0.0
		self.factorSoFar = 0.0
		self.waitingForOperand = True
		self.pendingAdditiveOperator = ''
		self.pendingMultiplicativeOperator = ''

		self.display = QLineEdit("0")
		self.display.setReadOnly(True)
		self.display.setAlignment(Qt.AlignRight)
		self.display.setMaxLength(15)
		font = self.display.font()
		font.setPointSize(font.pointSize() + 8)
		self.display.setFont(font);

		self.digitButtons = []
		# slik det ikke ville virke (men som jeg ikke forstår hvorfor er feil)
		# lambda eksempel: https://www.tutorialspoint.com/pyqt/pyqt_qradiobutton_widget.htm
	#	for d in "0123456789":
	#		button = self.createButton(d, lambda:self.digitClicked(d))
	#		self.digitButtons.append( button )
		# en annen mulighet er å ha sender() som i widTest01.pyw
		
		# slik jeg måtte gjøre det
		self.digitButtons.append( self.createButton("0", self.digit0Clicked ) )
		self.digitButtons.append( self.createButton("1", self.digit1Clicked ) )
		self.digitButtons.append( self.createButton("2", self.digit2Clicked ) )
		self.digitButtons.append( self.createButton("3", self.digit3Clicked ) )
		self.digitButtons.append( self.createButton("4", self.digit4Clicked ) )
		self.digitButtons.append( self.createButton("5", self.digit5Clicked ) )
		self.digitButtons.append( self.createButton("6", self.digit6Clicked ) )
		self.digitButtons.append( self.createButton("7", self.digit7Clicked ) )
		self.digitButtons.append( self.createButton("8", self.digit8Clicked ) )
		self.digitButtons.append( self.createButton("9", self.digit9Clicked ) )
		
		# the others buttons
		self.pointButton = self.createButton( ".", self.pointClicked )
		self.changeSignButton = self.createButton("\261", self.changeSignClicked )
		self.backspaceButton = self.createButton("Backspace", self.backspaceClicked )
		self.clearButton = self.createButton("Clear", self.clear )
		self.clearAllButton = self.createButton("Clear All", self.clearAll )

		self.clearMemoryButton = self.createButton("MC", self.clearMemory )
		self.readMemoryButton = self.createButton("MR", self.readMemory )
		self.setMemoryButton = self.createButton("MS", self.setMemory )
		self.addToMemoryButton = self.createButton("M+", self.addToMemory )

		self.divisionButton = self.createButton("/", self.divClicked )
		self.timesButton = self.createButton("*", self.multClicked )
		self.minusButton = self.createButton("-", self.minusClicked )
		self.plusButton = self.createButton("+", self.plusClicked )

		self.squareRootButton = self.createButton("Sqrt", self.squareRootClicked )
		self.powerButton = self.createButton("x\262", self.powerClicked )
		self.reciprocalButton = self.createButton("1/x", self.reciprocalClicked )
		self.equalButton = self.createButton("=", self.equalClicked )

		mainLayout = QGridLayout()
		mainLayout.setSizeConstraint(QLayout.SetFixedSize)
		mainLayout.addWidget(self.display, 0, 0, 1, 6)
		mainLayout.addWidget(self.backspaceButton, 1, 0, 1, 2)
		mainLayout.addWidget(self.clearButton, 1, 2, 1, 2)
		mainLayout.addWidget(self.clearAllButton, 1, 4, 1, 2)

		mainLayout.addWidget(self.clearMemoryButton, 2, 0)
		mainLayout.addWidget(self.readMemoryButton, 3, 0)
		mainLayout.addWidget(self.setMemoryButton, 4, 0)
		mainLayout.addWidget(self.addToMemoryButton, 5, 0)

		for i in range(1,len(self.digitButtons)):
			row = ((9 - i) // 3) + 2
			column = ((i - 1) % 3) + 1
			mainLayout.addWidget(self.digitButtons[i], row, column)

		mainLayout.addWidget(self.digitButtons[0], 5, 1)
		mainLayout.addWidget(self.pointButton, 5, 2)
		mainLayout.addWidget(self.changeSignButton, 5, 3)

		mainLayout.addWidget(self.divisionButton, 2, 4)
		mainLayout.addWidget(self.timesButton, 3, 4)
		mainLayout.addWidget(self.minusButton, 4, 4)
		mainLayout.addWidget(self.plusButton, 5, 4)

		mainLayout.addWidget(self.squareRootButton, 2, 5)
		mainLayout.addWidget(self.powerButton, 3, 5)
		mainLayout.addWidget(self.reciprocalButton, 4, 5)
		mainLayout.addWidget(self.equalButton, 5, 5)
		self.setLayout(mainLayout)
		self.setWindowTitle("Calculator")
		
		return

	def createButton(self, text, funClicked):
		button = Button(text)
		button.clicked.connect(funClicked)
		return button

	# write these simple functions compactly
	def digit0Clicked(self): self.digitClicked("0")
	def digit1Clicked(self): self.digitClicked("1")
	def digit2Clicked(self): self.digitClicked("2")
	def digit3Clicked(self): self.digitClicked("3")
	def digit4Clicked(self): self.digitClicked("4")
	def digit5Clicked(self): self.digitClicked("5")
	def digit6Clicked(self): self.digitClicked("6")
	def digit7Clicked(self): self.digitClicked("7")
	def digit8Clicked(self): self.digitClicked("8")
	def digit9Clicked(self): self.digitClicked("9")
		
	def digitClicked(self, strValue):
		if not ((self.display.text() == "0") and (strValue == "0")):
			if (self.waitingForOperand):
				self.display.clear()
				self.waitingForOperand = False
			self.display.setText(self.display.text() + strValue)
		return
		
	def squareRootClicked(self): self.unaryOperatorClicked("Sqrt")
	def powerClicked(self): self.unaryOperatorClicked("x2")
	def reciprocalClicked(self): self.unaryOperatorClicked("1/x")

	def unaryOperatorClicked(self, clickedOperator):
		operand = float(self.display.text())
		result = 0.0
		if (clickedOperator == "Sqrt"):
			if (operand < 0.0):
				self.abortOperation()
				return
			result = sqrt(operand)
		elif (clickedOperator == "x2"):
			result = operand*operand
		elif (clickedOperator == "1/x"):
			if (operand == 0.0):
				self.abortOperation()
				return
			result = 1.0 / operand
		# end if
		self.display.setText(str(result))
		self.waitingForOperand = True
		return
		
	def plusClicked(self): self.additiveOperatorClicked("+")
	def minusClicked(self): self.additiveOperatorClicked("-")
	
	def additiveOperatorClicked(self, clickedOperator):
		operand = float(self.display.text())
		if (len(self.pendingMultiplicativeOperator) > 0):
			if (not self.calculate(operand, self.pendingMultiplicativeOperator)):
				self.abortOperation()
				return
			self.display.setText(str(self.factorSoFar))
			operand = self.factorSoFar
			factorSoFar = 0.0
			pendingMultiplicativeOperator = ''
		if (len(self.pendingAdditiveOperator) > 0):
			if (not self.calculate(operand, self.pendingAdditiveOperator)):
				self.abortOperation()
				return
			self.display.setText(str(self.sumSoFar))
		else:
			self.sumSoFar = operand
		#end if
		self.pendingAdditiveOperator = clickedOperator
		self.waitingForOperand = True
		return
		
	def multClicked(self): self.multiplicativeOperatorClicked("*")
	def divClicked(self): self.multiplicativeOperatorClicked("/") 
	
	def multiplicativeOperatorClicked(self, clickedOperator):
		operand = float(self.display.text())
		if (len(self.pendingMultiplicativeOperator) > 0):
			if (not self.calculate(operand, self.pendingMultiplicativeOperator)):
				self.abortOperation()
				return
			self.display.setText(str(self.factorSoFar))
		else:
			self.factorSoFar = operand;
		#end if
		self.pendingMultiplicativeOperator = clickedOperator
		self.waitingForOperand = True
		return
		
	def calculate(self, rightOperand, pendingOperator):
		if (pendingOperator == "+"):
			self.sumSoFar = self.sumSoFar + rightOperand
		elif (pendingOperator == "-"):
			self.sumSoFar = self.sumSoFar - rightOperand
		elif (pendingOperator == "*"):
			self.factorSoFar = self.factorSoFar * rightOperand
		elif (pendingOperator == "/"): 
			if (rightOperand == 0.0):
				return False
			self.factorSoFar = self.factorSoFar / rightOperand
		else:
			return False
		#end if
		return True
		
	def equalClicked(self):
		operand = float(self.display.text())
		if (len(self.pendingMultiplicativeOperator) > 0):
			if (not self.calculate(operand, self.pendingMultiplicativeOperator)):
				abortOperation()
				return
			operand = self.factorSoFar
			factorSoFar = 0.0
			self.pendingMultiplicativeOperator = ''
		#
		if (len(self.pendingAdditiveOperator) > 0):
			if (not self.calculate(operand, self.pendingAdditiveOperator)):
				abortOperation()
				return
			self.pendingAdditiveOperator = ''
		else:
			self.sumSoFar = operand
		#end if
		self.display.setText(str(self.sumSoFar))
		self.sumSoFar = 0.0
		self.waitingForOperand = True
		return
		
	def pointClicked(self):
		if self.waitingForOperand:
			self.display.setText("0")
		if not ('.' in self.display.text()):
			self.display.setText(self.display.text() + ".")
		self.waitingForOperand = False
		return
		
	def changeSignClicked(self):
		value = -1.0*float(self.display.text())
		self.display.setText(str(value))
		return
		
	def backspaceClicked(self):
		if not self.waitingForOperand:
			text = self.display.text()
			text = text[:-1]
			if (len(text) == 0) or (text == "-"):
				text = "0"
				self.waitingForOperand = True
			self.display.setText(text)
		return
		
	def clear(self):
		# if not self.waitingForOperand:
		self.display.setText("0")
		self.waitingForOperand = True
		return
		
	def clearAll(self):
		self.sumSoFar = 0.0
		self.factorSoFar = 0.0
		self.pendingAdditiveOperator = ''
		self.pendingMultiplicativeOperator = ''
		self.display.setText("0");
		self.waitingForOperand = True
		return
		
	def clearMemory(self):
		self.sumInMemory = 0.0
		return
		
	def readMemory(self):
		self.display.setText(str(self.sumInMemory));
		self.waitingForOperand = True
		return
		
	def setMemory(self):
		self.equalClicked()
		self.sumInMemory = float(self.display.text())
		return
		
	def addToMemory(self):
		self.equalClicked()
		self.sumInMemory = self.sumInMemory + float(self.display.text())
		return
		
	def abortOperation(self):
		self.clearAll();
		self.display.setText("####")
		return

# end of class Calculator
		
if __name__ == '__main__':
	app = QApplication(sys.argv)
	calculator = Calculator()
	calculator.show()
	sys.exit(app.exec())