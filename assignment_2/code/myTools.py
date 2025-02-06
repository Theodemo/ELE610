#!/usr/bin/python -tt
# -*- coding: utf-8 -*-  (no Byte Order Mark, BOM)
#
# ../ELE610/py3/myTools.py 
#
#  Some basic functions (tools) I use and find helpful in Python
#  Some are made to improve (?) Command Line Interface (CLI), like pwd(), whos()
#  Some are made to locate files on my computers, like DBpath()
#
# Karl Skretting, UiS, January 2017 - February 2019 - August 2020 
#   - January 2022 - June 2022
# January 2022  (KS): removed 'bompenger' (to clsBompenger.py)
# February 2022 (KS): display containers (list,tuple,dict,set) if they are short

# Example on how to use file:
#   from myTools import whos 

"""Some small basic tool functions for python 3.x, which at least I find useful.
 Typically these functions are imported when Python starts in interactive mode,
 i.e. they are included in startup.py when Python is started by:
   (py38) C:\..\py3> python -i startup.py 
"""

_author = "Karl Skretting, UiS" 
_version = "2022-06-27"       # yyyy-mm-dd

import sys
import os
import glob
import re

try:
	import numpy as np
	npExist = True
except ImportError:
	npExist = False

try:
	cv2Exists = True    # or imp.find_module('cv2')
	import cv2
except ImportError:
	cv2Exists = False
	
try: # but does not use it yet
	pathlibExists = True
	from pathlib import Path
except ImportError:
	pathlibExists = False
	
def ls( mask='*', verbose=False, noPath=False ):
	""" Display (if verbose) and return a sorted list of files matching mask.
	Basically this is as: >>> a = sorted(glob.glob( mask ))
	unlike 'dir' in Windows CLI, sorted() is case sensitive, "A" < "Z" < "a" < "z"
	If noPath is True, the file names without path is returned
	ex: f = ls('*')
	"""
	a = sorted(glob.glob( mask ))
	if noPath:
		for idx in range(len(a)):
			a[idx] = os.path.basename( a[idx] )
	#end 
	if verbose:
		print( f"Display files matching mask: '{mask}'" )
		for fn in a:
			print( "  " + fn )
	return a 

def ls_sort_by_yyyymmdd( mask='*', verbose=False, noPath=False ):
	""" Display (if verbose) and return a 'sorted' list of files matching mask.
	Basically this is as: >>> a = sorted(glob.glob( mask ))
	Here we assume some file names has date given by digits yyyymmdd as in '*yyyy*mm*dd*' 
	In this case newest date is returned first, i.e. the files are sorted by the (8 first) digits 
	found in file name, largest first. Also, 'years' from 1900 to 2100 are first. Thus order as below
	2100, 2023, 20220504, 20220430, 2022, 1969, 1900, 99002, 99, 22, 21, 2, 19, 1888, 01, 004, 001
	If noPath is True, the file names without path is returned
	ex: f = ls_sort_by_yyyymmdd('*')
	"""
	def key_fun(fn):
		val = 0.0
		factor = 0.1;
		count = 0
		for ch in os.path.basename(fn): 
			if ch.isdigit():
				val += int(ch)*factor
				factor = 0.1*factor
				count += 1
				if (count > 7): 
					break
		# a special test makes 'non-year' digits fall behind
		if (count < 4) or ((val > 0.2100) or (val < 0.1900)):
			val = 0.1*val
		# The two lines below may be used to test (understand) key function 
		# make a key (number) used for sorting file names based on date (first 8 digits)
		# if verbose and (val > 0.0):
		# 	print( f"  key_fun( '{fn}' ) --> {val:12.9f}" )
		return val 
	# 
	a = sorted(glob.glob( mask ), key=key_fun, reverse=True)
	if noPath:
		for idx in range(len(a)):
			a[idx] = os.path.basename( a[idx] )
	#
	if verbose:
		print( 'Display files matching mask: ' + mask )
		for fn in a:
			print( '  ' + fn )
	return a

def pwd( ):
	""" Display and returns current (present) work directory. 
	ex: p = pwd()   # same as: p = os.getcwd()
	"""
	a = os.getcwd()
	# print( 'Current catalog: ' + a )
	return a

def visKeyValue( name, v, show_hidden=False, mask_name='' ):
	""" Display (print) a variable name, type and part of its value.
	name   should be a string, the name of the variable
	v      should be the contents of the variable, i.e. the value (the actual variable)
	"""
	tLen = 20
	tLen2 = 60
	if len(name) and (show_hidden or (name[0] != '_')) and (not len(mask_name) or re.match(mask_name, name)):
		if isinstance(v, bool):
			print( name.ljust(tLen), 'bool :', v )
		elif isinstance(v, int):
			print( name.ljust(tLen), 'int  :', v )
		elif isinstance(v, float):
			print( name.ljust(tLen), 'float:', v )
		elif isinstance(v, complex):
			print( name.ljust(tLen), 'complex :', v )
		elif isinstance(v, str):
			i1 = v.find('\n')
			if (i1 >= 0): 
				v1 = v[:min(i1,tLen2)]
			else:
				v1 = v[:min(len(v),tLen2)]
			try: 
				print( f"{name.ljust(tLen)} str, len={len(v)} : {v1}" )
			except UnicodeEncodeError:
				print( 'UnicodeEncodeError:  Perhaps string contains unprintable character.' )
			# if (len(v) < (tLen2+1)):
			#     print( name.ljust(tLen), 'str  :', v )
			# else:    
			#    print( name.ljust(tLen), 'str  :', v[:tLen2], '...' )
		elif isinstance(v, (list,dict,tuple,set)):
			if isinstance(v, list):
				print( name.ljust(tLen) + ' list : ', end='' )
			elif isinstance(v, dict):
				print( name.ljust(tLen) + ' dict : ', end='' )
			elif isinstance(v, tuple):
				print( name.ljust(tLen) + ' tuple: ', end='' )
			elif isinstance(v, set):
				print( name.ljust(tLen) + ' set  : ', end='' )
			#
			if len(v) < 20:  # short container
				v_string = str(v)
			else:
				v_string = ''
			#
			if (len(v) < 20) and (len(v_string) < 40):
				print(v_string)
			else:
				print( f"{len(v)} elements" )
		#
		elif npExist and isinstance(v, np.ndarray):
			print( name.ljust(tLen) + ' ndarray of ' + v.dtype.name + ', shape: ' + str(v.shape) )
		elif isinstance(v, bytes):
			v1 = str(v)
			i1 = i1 = min(tLen2,len(v1))
			print( f"{name.ljust(tLen)} bytes, len={len(v)} : {v1[:i1]}" )
		elif isinstance(v, bytearray):
			print( f"{name.ljust(tLen)} bytearray : {len(v)} elements" )
		else:
			stv = str(type(v))   # typically: <class 'type name'>
			if (len(stv) > 10):
				stv = stv[8:-2]   # display only type name
			# sv = str(v).strip()   # the string with leading and trailing whitespace removed.
			sv = " ".join(str(v).split())  # also remove spaces between words
			if (sv.find('\n')>=0):
				sv = sv[:sv.find('\n')] + ',..'  # only first line
			if (len(sv) > (100 - tLen - len(stv))):  
				sv = sv[:(100 - tLen - len(stv))] + '...'
			#
			try:
				i = len(v)   # not all classes has a length, may cause error
				print( name.ljust(tLen), stv + f", len={len(v)} : {sv}" )
			except:
				print( f"{name.ljust(tLen)} {stv} : {sv}" ) 
	else:
		pass
	return
	
def whos( a=None, show_hidden=False, mask_name='', var_type='mbfv' ):
	""" Print the content of input argument (dictionary or list) in a more 
	reader friendly format than the simple: print( a )
	Thus, it is actually a reformat function: whos( a ).
	When the input dictionary is the locals (local variables), i.e. locals() or vars(),
	this function is, as intended, almost like the 'whos'-function in Matlab.
	Input:
	  a             a dictionary or a list (or a tuple)
	  show_hidden   a boolean to indicate if hidden names, i.e. start with '_', should be included
	  mask_name     a regular expression (re) that may be given to match the name
	  var_type      a string indicating which variable to include when 'a' is a dictionary: 
	                'm' (module), 'b' (builtin...), 'f' (function), 'v' (other variables), 
	                's' (string), 'l' (list), 'd' (dict) and 'n' (numpy array)
	Examples:
	>>> whos( theDict )
	>>> whos( theList )
	>>> whos( vars() )         # content in workspace
	>>> whos( vars(os) )       # contens of 'os'
	>>> whos( vars(), mask_name='[ac]' )         # content in workspace, that starts with 'a' or 'c'
	>>> whos( vars(), var_type='v' )             # only variables (not 'mbf')
	"""
	if (str(type(a)) == "<class 'NoneType'>"): # or (a == None):  # some objects give error here
		print( "whos(): use 1 argument, ex: >>> whos( vars() )" )
	else:
		if isinstance(a, dict):
			if ('m' in var_type) or ('b' in var_type) or ('f' in var_type):   
				print( ' ' )
			if ('m' in var_type):   
				for k in sorted( a.keys() ):
					if isinstance( a[k], type(os) ):    # module
						visKeyValue( k, a[k], show_hidden, mask_name )
			if ('b' in var_type):   
				for k in sorted( a.keys() ):        
					if isinstance( a[k], type(os.chdir) ):   # builtin function  
						visKeyValue( k, a[k], show_hidden, mask_name )
			if ('f' in var_type):   
				for k in sorted( a.keys() ):        
					if isinstance( a[k], type(pwd) ):   # function  
						visKeyValue( k, a[k], show_hidden, mask_name )
			# now list the other elements
			if ('v' in var_type) or ('s' in var_type) or ('l' in var_type) or ('d' in var_type) or ('n' in var_type):  
				print(' ')
				for k in sorted( a.keys() ):
					if (not isinstance( a[k], (type(os),type(os.chdir),type(pwd)) ) 
					    and (    ('v' in var_type) 
						      or (('s' in var_type) and isinstance(a[k], str))
						      or (('l' in var_type) and isinstance(a[k], list))
						      or (('d' in var_type) and isinstance(a[k], dict))
						      or (('n' in var_type) and npExist and isinstance(a[k], np.ndarray))  )  ): 
						visKeyValue( k, a[k], show_hidden, mask_name )
		elif isinstance(a, (list,tuple)):
			stv = str(type(a))   # typically: <class 'type name'>
			if (len(stv) > 10):
				stv = stv[8:-2]   # display only type name
			if (len(a) > 20):
				print( f"Display the 5 first and 5 last elements in input of type {stv}" )
				for k in range(5):
					visKeyValue( f"element {k:4d}", a[k], show_hidden, mask_name )
				print(' ... ')
				for k in [len(a)-5,len(a)-4,len(a)-3,len(a)-2,len(a)-1]:
					visKeyValue( f"element {k:6d}", a[k], show_hidden, mask_name )
			else:
				print( f"Display the {len(a)} elements in input of type {stv}:" )
				for k in range(len(a)):
					visKeyValue( f"element {k:2d}", a[k], show_hidden, mask_name )
		else:
			print( "whos(): use argument type 'list' or 'dict', ex: >>> whos( vars() )" )
			visKeyValue( 'anyway, arg is', a, show_hidden, mask_name )
	# return dir()  # sorted(vars().keys())
	
# DBpath : a function useful for myself, 
# as Dropbox is in different locations on disks on different PCs I frequently use 
def DBpath( navn='m610' ):
	""" A special function that returns a path on my personal Dropbox catalog. 
	The path depends on where Dropbox is mounted for the different 
	computers that I may use. Examples:
	  p = DBpath( 'Matlab/ele610' )   or   p = DBpath( 'Matlab\\ele610' ) 
	I have defined some 'short names'; 
	'm610' (Matlab-files for ELE610)
	'm620' (Matlab-files for ELE620)
	'l610' or 'ele610' (LaTeX-files for ELE610), and more
	"""
	sti = '.'
	if navn.lower() == 'turkart':
		navn = 'TurKart'
	if navn.lower() == 'm610':
		navn = 'Matlab' + os.path.sep + 'ele610'
	if navn.lower() == 'm620':
		navn = 'Matlab' + os.path.sep + 'ele620'
	if (navn.lower() == 'l610') or (navn.lower() == 'ele610'):
		navn = 'ELE610' + os.path.sep + '2022'
	# chech if location is ../Dropbox/..  
	fullsti = os.path.abspath( '.' )
	pos = fullsti.find('Dropbox')
	if (pos >= 0):
		if (navn[0] != os.path.sep):
			navn = os.path.sep + navn
		# does catalog exist
		sti = fullsti[:pos] + 'Dropbox' + navn 
		if not os.path.isdir( sti ):
			print( 'DBpath(): ' + sti + ' not found as a catalog in my Dropbox.' )
			sti = fullsti[:pos] + 'Dropbox' 
	else:
		print( "DBpath(): Can't locate Dropbox catalog, try Documents " )
		pos = fullsti.find('Documents')
		if (pos >= 0):
			if (navn[0] != os.path.sep):
				navn = os.path.sep + navn
			# does catalog exist
			sti = fullsti[:pos] + 'Documents' + navn 
			if not os.path.isdir( sti ):
				print( 'DBpath(): ' + sti + ' not found as a catalog in Documents.' )
				sti = fullsti[:pos] + 'Documents' 
		else:
			print( "DBpath(): Can't locate Dropbox or Documents, returns " + sti )
	return sti

def which(program):
	""" Mimics behavior of UNIX which command.
	may also locate (first occurrence of) file if argument contains '.',  ex: which('temp.txt')
	"""
	# Add .exe program extension for windows support
	if (program.find('.') < 0) and os.name == "nt" and not program.endswith(".exe"):
		program += ".exe"
	#
	envdir_list = [os.curdir] + os.environ["PATH"].split(os.pathsep)
	#
	for envdir in envdir_list:
		program_path = os.path.join(envdir, program)
		if os.path.isfile(program_path) and os.access(program_path, os.X_OK):
			return program_path
	# if not found return nothing
	return
	
# *********************** TEST functions ************************* #

def test01(arg):
	print( "\ntest01(): arguments passed to test function, and print of 'å'" )
	name = 'Karl'
	print( 'Hei og hopp', name )
	for name in arg[1:]:
		print( 'Hei også til', name )
	return
		
def test02():
	print( "\ntest02(): test of ls() and ls_sort_by_yyyymmdd()" )
	mask = '*.py'
	# mask = '../../TurKart/*.gpx'
	L = 10    # number of files to print from each list
	#
	a = ls(mask, noPath=True)
	print( f"The first {min(L, len(a))} of {len(a)} files as returned by ls( '{mask}', noPath=True )" ) 
	for fn in a[:min(L, len(a))]:
		print('  ', fn)
	#
	b = ls_sort_by_yyyymmdd( mask, noPath=True )
	print( (f"The first {min(L, len(b))} of {len(b)} files" + 
	        f" as returned by ls_sort_by_yyyymmdd( '{mask}', noPath=True )") )
	for fn in b[:min(L, len(b))]:
		print('  ', fn)
	return

# This is used for test functions
# Start from an OS command window as  C:\..\py3> python myTools.py 
if __name__ == '__main__':
	# test01(sys.argv)
	test02()
	pass
	
	