#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ../ELE610/TATEM/showJSON.py 
#  Print and sum up results of a JSON file created by the ABB TATEM-tool on UiS robot Rudolf. 
#
# Made for UiS ELE610 course by Karl Skretting October 2023

# Example on how to use file:
#   (C:\...\Anaconda3) C:\..\py3> activate py39
#   (py39) C:\..\ELE610\TATEM> python showJSON.py path_and_filename
#   (py39) C:\..\ELE610\TATEM> python showJSON.py C:\TFS\TATEM\datasets\2023-09-06_14-43-55.json
#   (py39) C:\..\ELE610\TATEM> python showJSON.py datasets\2023-09-06_14-43-55.json
#   (py39) C:\..\ELE610\TATEM> python showJSON.py datasets\2023-09-06_14-49-55.json
# or from within python, 'showJSON.py' in current catalog ('startup.py' in a sibling catalog)
#   (py38) C:\..\ELE610\TATEM> python -i ..\py3\startup.py
# 'startup.py' import some useful functions, and os and sys
#    >>> sys.path.append( os.getcwd() )
#    >>> import showJSON
#    >>> showJSON.main()

import sys
import os
import json

try:
	from TatemArduinoIf import jsonFileDir
except:
	jsonFileDir = "C:\\TFS\\TATEM\\datasets"   # as it may be in TatemArduinoIf.py

if not os.path.exists(jsonFileDir):
	# the alternative is current directory
	jsonFileDir = os.getcwd()

def get_directory_list():
	# return a list of directories where (json-) files may be
	cwd = os.getcwd()
	return [cwd, jsonFileDir, "C:\\TFS\\TATEM\\datasets", cwd+"\\datasets", 
			cwd+"\\TATEM\\datasets", "..\\datasets", "..\\TATEM\\datasets"]


def find_directory_with_json_files():
	for directory in get_directory_list():
		if os.path.exists(directory):
			# Get a list of all JSON files in the directory
			json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
			if json_files: return directory  # Found a directory with JSON files
	return None  # No directory with JSON files found

def find_any_json_or_file_with_name(fn=""):
	# and if fn is not found as given, add path from default directory list
	# and perhaps also suffix '.json', and if still not found look for 
	# newest json-file in the first found directory containing json-files
	if fn:
		if os.path.exists(fn): return fn
		# first look for fn in directory_list
		for d in get_directory_list():
			dfn = os.path.join(d, fn)
			if os.path.exists(dfn): return dfn
		# then add suffix and again look for fn in directory_list
		if not fn.endswith('.json'): fn = fn + '.json'
		for d in get_directory_list():
			dfn = os.path.join(d, fn)
			if os.path.exists(dfn): return dfn
	#
	json_directory = find_directory_with_json_files()
	if json_directory:
		json_files = [f for f in os.listdir(json_directory) if f.endswith('.json')]
		json_files.sort(key=lambda x: os.path.getmtime(os.path.join(json_directory, x)), reverse=True)
		newest_json_file = json_files[0]
		return os.path.join(json_directory, newest_json_file)
	#
	return None
	
def show_parsed_json(parsed_json):
	# this file is more robust than it initially was, but still not ready to display
	# any json-file without errors, it should be a json-file from the UiS TATEM tool.
	num = -1
	numTaError = 0
	numSuccess = 0
	numNotDefined = 0
	numOther = 0
	if not parsed_json:
		print( "The report is empty, no events reported." )
	else:
		time0 = parsed_json[0]['eventStart']
		for e in parsed_json:
			num = num + 1
			if isinstance(e, dict):
				time1 = (e['eventStart'] - time0)/1e6 if 'eventStart' in e else -1.0  # [s]
				tA = e['tA']/1e3 if 'tA' in e else -1.0 # ms
				tO = e['tO']/1e3 if 'tO' in e else -1.0 # ms
				tR = e['tR']/1e3 if 'tR' in e else -1.0 # ms
				print( f"Event {num:3d} is {e['eventResult']:10s} {tA=:6.1f}  " +\
					   f" {tO=:6.1f}  {tR=:6.1f} [ms]  " +\
					   f"(time since first event is {time1:8.4f} [s])" )
				#
				if (e['eventResult']=="Success"):
					numSuccess = numSuccess + 1
					tA2 = (e['operationStart'] - e['eventStart'])/1e3   # [ms]
					DOon = (e['doOff'] - e['eventStart'])/1e3   # [ms]
					L1on = (e['eventEnd'] - e['eventStart'])/1e3   # [ms]
					tR2 = L1on - DOon
					print( f"  More times           {tA2=:6.1f} {DOon=:6.1f} {tR2=:6.1f} " +\
						   f"{L1on=:6.1f} [ms]" )
				elif (e['eventResult']=="TaError"):
					numTaError = numTaError + 1
				elif (e['eventResult']=="NotDefined"):
					numNotDefined = numNotDefined + 1
				else:
					numOther = numOther + 1
				#
				if isinstance( e['details'], list ):
					for ed in e['details']:
						timeStarted = (ed['time'] - e['eventStart'])/1e3 if 'time' in ed else -1.0 # [ms]
						print( f"  Detail {ed['no'] if 'no' in ed else -1:3d}, " +\
							   f"error: {ed['ERROR'] if 'ERROR' in ed else ''}, " +\
							   f"DO: {ed['DO'] if 'DO' in ed else ''},  " +\
							   f"L1: {ed['L1'] if 'L1' in ed else ''}, " +\
							   f"L2: {ed['L2'] if 'L2' in ed else ''}, " +\
							   f"S1: {ed['S1'] if 'S1' in ed else ''}, " +\
							   f"S2: {ed['S2'] if 'S2' in ed else ''}, " +\
							   f" time {timeStarted:7.1f} [ms], " +\
							   f"state: {ed['STATE'] if 'STATE' in ed else ''}" )
	#
	print( f"Summary: {numSuccess} Success, {numTaError} TaError, " +\
		   f"{numNotDefined} NotDefined, {numOther} Other." )
	return

def main(fn=""):
	fn = find_any_json_or_file_with_name(fn)
	# 
	if fn and os.path.exists(fn):
		print( f"Try to parse file {fn}" )
		with open(fn) as user_file: 
			parsed_json = json.load(user_file)
	else:
		print( f"File {fn} does not exists" )
		parsed_json = None
	#
	if parsed_json:  # isinstance(parsed_json, list) and len(parsed_json):
		print( f"File {fn} contains a list of {len(parsed_json)} elements." )
		show_parsed_json(parsed_json)
	else:
		print( f"File {fn} does not exists or does not contain a json-list, hmmm." )
	#
	return

if __name__ == "__main__":
	if len(sys.argv) > 1:
		main(sys.argv[1])   
	else: # no supplied filename
		main()
