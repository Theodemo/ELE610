#!/usr/bin/python -tt
# -*- coding: utf-8 -*-  (without BOM)
#
# .../Dropbox/ELE610/py3/startup.py    
# available at:  http://www.ux.uis.no/~karlsk/ELE610/startup.py
# This file is Python 3.x startup file for Karl Skretting at UiS.
# It can be used on my UiS Windows 10 computer, on my home Ubuntu (Unix) computer,
# on my Samsung laptop PC, and on the TekNat Unix system, preferable gorina3.
# A similar file (for Python 2.7) is on .../Dropbox/ELE610/python/startup.py
# Karl Skretting, UiS, 2017 - 2020 - 2022

# Anaconda prompt..> activate py38  (or py3[.bat], or something else)
# (py38) C:\..\py3> python -i startup.py 
#
# Unix system at UiS or Ubuntu at home:  
#   ssh karlsk@gorina2   # gorina2.ux.uis.no
#   (login pw)
#   cd ~/python
#   python3 -i startup.py 

print( "** Startup-file for Python 3.x, import some packages and functions." )

import sys
print( "Package   sys ver. " + sys.version )

import os

from math import sqrt, pi, cos, sin, tan, log, floor, ceil  # from math import *

from myTools import DBpath, ls, whos, pwd 

try:
	from importlib import reload
except ImportError:
	print( "Error importing reload from importlib; reload is not available." )

try:
	import numpy as np
	print( "Package numpy ver. " + np.__version__ )
except ImportError:
	print( "ImportError for numpy; np is not available." )
except:
	print( "Error importing numpy; np is perhaps not available." )

try:
	import matplotlib.pyplot as plt   # or import matplotlib as mpl
except ImportError:
	print( "ImportError for matplotlib.pyplot; plt is not available." )
except:
	print( "Error importing matplotlib.pyplot; plt is perhaps not available." )

try:
	import cv2
	print( "Package   cv2 ver. " + cv2.__version__ )
except ImportError:
	print( "ImportError for OpenCV; cv2 is not available." )
except:
	print( "Error importing OpenCV; cv2 is perhaps not available.")
	print( "  In some cases I found that it was private variables that were unavailable.")

print( "** Assign values to some variables." )
pm = DBpath('m610');
print( "Define path for Matlab files in ELE610: pm = " + pm )
f = ls( pm + os.path.sep + "*.jpg" )
if (len(f) > 0):
	i = len(f) - 1
	print( f"and jpg-files there in list f:  f[{i}] = {f[i]}." )

print( "** List defined variables and Python is ready to use.\n" )
whos(vars())

""" Kunne lest img
# print( 'Pakke   mpl ver. ' + mpl._version + ' (i.e. matplotlib)' )

if cv2Exists:
	img = cv2.imread( f[i] )      # blir ndarray
	print( "Leser bilde med:  'img = cv2.imread( f[i] )',  img blir ndarray" )
	print( 'img.dtype = ', img.dtype, ', img.size = ', img.size, ', img.ndim = ', img.ndim, ', img.shape = ', img.shape )
	# fig, ax = plt.subplots(num=1, figsize=(12, 6), dpi=100, facecolor='w', edgecolor='k')
	# ax.axis('off')
	# ax.imshow( img[...,::-1] )   # lager bilde med pyplot og samtidig BGR --> RGB 
	# plt.title("Bilde "+f[i])
	# plt.show(block = False)       # og viser det
	# fig.set_size_inches(11,6)
elif PilExists:  # noe det ikke gjor i py35
	# img = Image.open(f[i])       # eller
	img = Image.open(f[i]).convert("L")
	print( "Leser bilde med:  'img = Image.open(f[i])'" )
	print( f[i], img.format, f"{img.size}x{img.mode}" )
else:
	pass
"""


'''  noe eksempelkode som kan brukes her og der
def meny(): 
	print """Enkel meny (bør ikke brukes?):
	1. vis bilde (med plt eller PIL.Image)
	2. vis funksjon-plott. (plt)
	3. vis bilde med cv2.imshow( .. )
	"""
	inn = raw_input('Valg: ') 
	if  (inn == '1'):
		if cv2Exists:    
			plt.imshow( img[...,::-1] )   # lager bilde med pyplot og samtidig BGR --> RGB 
			plt.show()      # og viser det 
			# fortsetter ikke her før bilde-vinduet er lukket
			# plt.show( False )  # viser bilde i vindu og fortsetter med vindu oppe
			# alternativ er cv2.imshow( ... )
		elif PilExists:
			img.show()  # calls the xv utility to display the image (?). 
			# If you don’t have xv installed, it won’t even work. 
		else:
			pass
	elif (inn == '2'):
		a = np.linspace(0,5,100)
		b = np.exp(-a)
		plt.plot(a,b)
		plt.show()  
	elif (inn == '3'):
		print 'Viser bilde'
		cv2.namedWindow( 'Bilde', cv2.WINDOW_NORMAL)
		cv2.imshow( 'Bilde', img )   # RGB vises som det skal
		print 'Trykk en tast for å fortsette..'
		a = cv2.waitKey( 0 )
'''
