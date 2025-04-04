#!/usr/bin/env python
#
# tatemCom_test.py  --> tatemCom_KS.py  --> tatemCom.py 
#
# Do BLE communication with TATEM tool, read and write through predefined functions, 
# and IP (RWS) communication with Robot only read (from UiS Rudolf).
# cmd2 is used to implement a simple command line interface (CLI).
# 
# Originally made by ABB 2022
# Later adapted to UiS robots by Ali H Jabbour 23 okt 2022, GitHub  ELE610/TATEM/src/python
# Modified and updated for UiS ELE610 course by Karl Skretting from October 2023 
# removed large test in tatemTest.py
# See tatemCom_test.py or tatemCom_KS.py (both on OneDrive ..\ELE610\TATEM) if you want the tests
#
# Use:
# (py11) ..\ELE610\py3> python tatemCom.py

_version = "23.11.08"   #  yy.mm.dd

import os
import sys
import argparse
import json
import cmd2
from time import sleep

import TatemRapidIf
import TatemArduinoIf
try: 
	from showJSON import find_any_json_or_file_with_name, show_parsed_json
	showJSON_OK = True
except:
	showJSON_OK = False 

try:
	jsonFileDir = TatemArduinoIf.jsonFileDir
except:
	jsonFileDir = "C:\\TFS\\TATEM\\datasets"   # as it may be in TatemArduinoIf.py

if not os.path.exists(jsonFileDir):
	# the alternative is current directory
	jsonFileDir = os.getcwd()

# (KS Oct 2023) Remove choices_provider() decorators (complete a word using TAB)
# for how to use them see: https://buildmedia.readthedocs.org/media/pdf/cmd2/latest/cmd2.pdf 

# (KS Oct 2023) Removed run_remote_cmd(..) and get_services()
# as it seemed that they were not used here (except for debug?), 
# The corresponding functions in TatemArduinoIf.py are used now.


class TatemCLI(cmd2.Cmd):
	"""cmd2 application."""
	
	def __init__(self, devid):
		super().__init__()
		self.arduinoIP = None    # actually mac address
		self.robotIP = None      # default addresses in connect-functions below
		self.Arduino = None
		self.Robot = None
		self.TestCycle = None
		self.prompt = 'tatem>'
		#  
		self.intro = cmd2.style( f"Welcome to the TATEM application for ELE610, ver.{_version}", 
				fg=cmd2.Fg.RED, bg=cmd2.Bg.WHITE, bold=True)
		return
	
	
	def do_discover(self, args):
		"""List available TATEM tools by use of BleakScanner.discover
		simply call the discover function in TatemArduinoIf.py """
		# ignore any args here
		TatemArduinoIf.discover()  
		return
	
	
	tatem_parser = cmd2.Cmd2ArgumentParser()
	tatem_parser.add_argument('address', type=str, nargs='?', 
			help='the arduino TATEM address' )
	@cmd2.with_argparser(tatem_parser)
	def do_connectArduino(self, args):
		"""Connecting the TATEM tool (Arduino). The MAC-address may be given as an argument,
		or if no argument is given, the default MAC-address (for UiS TATEM tool) is used."""
		self.arduinoIP = args.address if args.address else "A1:F8:14:CE:BA:AC"  
		self.poutput("Use TATEM tool address " + self.arduinoIP)
		# Will start the bluetooth connection
		self.Arduino = TatemArduinoIf.TatemArduinoIf(self.arduinoIP) 
		maxtime = 0
		# 
		while not self.Arduino.IsConnected() and maxtime < 40: 
			if (maxtime%2 == 0): print("Connecting to the Arduino...")
			sleep(1)
			maxtime = maxtime + 1
		#
		if maxtime == 40:
			self.Arduino.Disconnect()
			self.pwarning("Timeout error: The TATEM tool is not connected.")
			self.Arduino = None
			self.arduinoIP = None
		else:
			self.poutput(f"Connected to TATEM tool with mac: {self.arduinoIP}")
		#
		return
	
	
	tatem_parser = cmd2.Cmd2ArgumentParser()
	tatem_parser.add_argument('address', type=str, nargs='?', 
			help='the robot address' )
	@cmd2.with_argparser(tatem_parser)
	def do_connectRobot(self, args):
		"""Connecting the Robot. The IP-address may be given as an argument,
		or if no argument is given, the IP-address of UiS Rudolf is used."""
		self.robotIP = args.address if args.address else "152.94.0.39"  # (Rudolf IP)
		self.poutput("Use robot address " + self.robotIP)
		self.Robot = TatemRapidIf.TatemRapidIf(self.robotIP)
		# connecting
		self.Robot.Connect() 
		if self.Robot.CheckConnection():
			self.poutput(f"Connected to Robot with IP: {self.robotIP}")
		else:
			self.pwarning("Something went wrong with the connection. No robot is connected.")
			self.Robot = None
			self.robotIP = None
		#
		return
	
	
	def do_checkArduinoConnection(self, args):
		"""Check the connection to the TATEM tool (Arduino)"""
		if self.Arduino == None:
			self.poutput( "No Arduino is connected" )
		elif self.Arduino.IsConnected():
			self.poutput( f"Connected to Arduino with IP: {self.arduinoIP}" )
		else:
			self.poutput( f"An Arduino object with IP {self.arduinoIP} has been created, " +\
					"but it is not connected" )
		#
		return
	
	
	def do_checkRobotConnection(self, args):
		"""Check the connection to the robot"""
		if self.Robot == None:
			self.poutput("No robot is connected")
		elif self.Robot.CheckConnection():
			self.poutput(f"Connected to robot with IP: {self.robotIP}")
		else:
			self.poutput(f"A robot object with IP {self.robotIP} has been created, but is not connected")
		#
		return
	
	
	def do_resetArduino(self, args):
		"""Reset the TATEM tool (Arduino) by calling self.Arduino.Reset()
		Then set the default time-values: tA=100, tO=300, tR=100 [us]"""
		if self.Arduino == None:
			self.pwarning("No Arduino is connected")
		else:
			self.Arduino.Reset()
			# may also set times
			# self.Arduino.SetTa( "100000" )   # set is done with unit us
			# self.Arduino.SetTo( "300000" )
			# self.Arduino.SetTr( "100000" )
		#
		return
	
	
	def do_disconnectArduino(self, args):
		"""Disconnect the TATEM tool (Arduino)"""
		if self.Arduino != None:
			self.poutput("Disconnecting Arduino...")
			self.Arduino.Disconnect()
			while self.Arduino.IsConnected():
				self.poutput("Disconnecting Arduino...")
				sleep(1)
			self.poutput("Arduino is disconnected")
		#
		self.Arduino = None
		self.arduinoIP = None
		return
	
	
	def do_disconnectRobot(self, args):
		"""Disconnect the connected robot"""
		if self.Robot != None:
			self.Robot.Disconnect()
		#
		self.Robot = None
		self.robotIP = None
		return
	
	
	def do_getReport(self, args):
		"""Get the report from the TATEM tool (Arduino) by calling self.Arduino.GetReport()
		The report is saved as a file on catalog 'jsonFileDir' and shown on output"""
		if self.Arduino == None:
			self.pwarning("No Arduino is connected")
		else:
			# call: self.Arduio.GetReport(..) and it calls writeFile(..) in TatemArduinoIf.py
			dfn = self.Arduino.GetReport()
			if dfn:
				self.poutput( f"do_getReport():  report stored in {dfn}" )
				self.do_load( dfn )
			else:
				self.poutput( f"do_getReport():  Hmmm, no file to show" )
			#
		#
		return
	
	
	name_parser = cmd2.Cmd2ArgumentParser()
	name_parser.add_argument('logfile', type=str, nargs='?', 
			help='the logfile from the TATEM tool to load and show' )
	@cmd2.with_argparser(name_parser)
	def do_load(self, args):
		"""Load a json-file and display it, assuming it is a logfile from the TATEM tool.
		Without any logfile given it will try to find a json-file on the computer."""
		fn = args.logfile
		if showJSON_OK: # try to find json-file in several locations
			fn = find_any_json_or_file_with_name(fn)
		# 
		if fn and os.path.exists(fn):
			self.poutput( f"do_load(..):  Load {fn} and show content" )
			#
			data = []
			with open( fn, 'r') as f: 
				data = json.load( f )
			#
			self.poutput( f"This file has {len(data)} events" )
			if showJSON_OK:
				show_parsed_json(data)
			elif data:
				for idx, evt  in enumerate(data):
					# assume correct content of file
					self.poutput( f"event {idx} start: {evt['eventStart']} " +\
						f"end: {evt['eventEnd']} doOff: {evt['doOff']} tA: {evt['tA']} " +\
						f"tO: {evt['tO']} tR: {evt['tR']}, eventResult: {evt['eventResult']}" )
			else:
				self.pwarning( f"Hmmm, {data = }" )
			#
		#
		return
	
	
	def do_getTvalues(self, args):
		"""Read the time-values from RAPID program on robot and display them
		but does not write them to TATEM tool (Arduino).
		"""
		if self.Robot == None:
			self.pwarning("No robot is connected")
		else:
			self.poutput("The t-values from RAPID program on robot are:")
			tA_s = self.Robot.GettA()  # suffix '_s' indicate seconds, and is here a string
			tO_s = self.Robot.GettO()
			tR_s = self.Robot.GettR()
			self.poutput( "Current t-values are:" +\
			              f"\ntA = {1000*tA_s:6.1f} [ms]" +\
			              f"\ntO = {1000*tO_s:6.1f} [ms]" +\
			              f"\ntR = {1000*tR_s:6.1f} [ms]" )
		return
	
	
	def do_setTvalues(self, args):
		"""Read the time-values from RAPID program on robot 
		or use default values for times (tA=100 ms, tO=300 ms and tR=100 ms)
		and then write them to the TATEM tool (Arduino) and display them.
		"""
		if self.Arduino == None:
			self.pwarning("No TATEM tool (Arduino) is connected")
			return
		#
		if self.Robot and self.Robot.RobotState() != "stopped":
			self.poutput("Test on robot is in progress. Do nothing.")
			return
		#
		if self.Robot:
			tA_s = float(self.Robot.GettA())   # suffix '_s' indicate seconds (not string)
			tO_s = float(self.Robot.GettO())
			tR_s = float(self.Robot.GettR())
		else:
			self.pwarning("No robot is connected, set default times.")
			tA_s = 0.1    
			tO_s = 0.3 
			tR_s = 0.1 
		#
		tA_us = str(tA_s*1000000)
		tO_us = str(tO_s*1000000)
		tR_us = str(tR_s*1000000)
		self.Arduino.SetTa(tA_us)   # set is done with unit us
		self.Arduino.SetTo(tO_us)
		self.Arduino.SetTr(tR_us)
		self.poutput( "Current t-values are:" +\
					  f"\ntA = {1000*tA_s:6.1f} [ms]" +\
					  f"\ntO = {1000*tO_s:6.1f} [ms]" +\
					  f"\ntR = {1000*tR_s:6.1f} [ms]" )
		#
		return
	
	
	tA_parser = cmd2.Cmd2ArgumentParser()
	tA_parser.add_argument('tA', type=float, help='tA value in milliseconds' )
	@cmd2.with_argparser(tA_parser)
	def do_set_tA(self, args):
		"""Write supplied tA, in ms, to the connected TATEM tool (Arduino)."""
		tA_ms = float(args.tA) 
		self.poutput( f"We want to set tA to {tA_ms:7.1f} [ms]" ) 
		if self.Arduino == None:
			self.pwarning("No TATEM tool (Arduino) is connected")
		else:
			self.Arduino.SetTa( str(1000*tA_ms) )   # set is done with unit us
		#
		return
	
	
	tO_parser = cmd2.Cmd2ArgumentParser()
	tO_parser.add_argument('tO', type=float, help='tO value in milliseconds' )
	@cmd2.with_argparser(tO_parser)
	def do_set_tO(self, args):
		"""Write supplied tO, in ms, to the connected TATEM tool (Arduino)."""
		tO_ms = float(args.tO)   # suffix '_s' indicate seconds (not string)
		self.poutput( f"We want to set tO to {tO_ms:7.1f} [ms]" ) 
		if self.Arduino == None:
			self.pwarning("No TATEM tool (Arduino) is connected")
		else:
			self.Arduino.SetTo( str(1000*tO_ms) )   # set is done with unit us
		#
		return
	
	
	tR_parser = cmd2.Cmd2ArgumentParser()
	tR_parser.add_argument('tR', type=float, help='tR value in milliseconds' )
	@cmd2.with_argparser(tR_parser)
	def do_set_tR(self, args):
		"""Write supplied tR, in ms, to the connected TATEM tool (Arduino)."""
		tR_ms = float(args.tR) 
		self.poutput( f"We want to set tR to {tR_ms:7.1f} [ms]" ) 
		if self.Arduino == None:
			self.pwarning("No TATEM tool (Arduino) is connected")
		else:
			self.Arduino.SetTr( str(1000*tR_ms) )   # set is done with unit us
		#
		return
	
	
	def do_info(self, args):
		"""May display some relevant information"""
		self.poutput(f"Info on TATEM application for ELE610, ver.{_version}:")
		self.poutput("tatemCom program for BLE communication with UiS TATEM tool, ") 
		self.poutput("read and write access through predefined functions.") 
		self.poutput("Can reset TATEM tool, wait until weld simulation is done,") 
		self.poutput("then get and display report from the TATEM tool.") 
		self.poutput("Also IP (RWS) communication with Robot UiS Rudolf")
		self.poutput("is available but only read of time-values; tA, tO and tR")
		self.poutput("See help for functions and help on functions.")
		return
	
	
	def do_quit(self, args):   # redefining quit, an alternative is to remove quit: del cmd2.Cmd.do_quit
		"""Disconnect any connected TATEM tool (Arduino) and quit"""
		return self.do_exit(args)
	
	
	def do_exit(self, args):
		"""Disconnect any connected TATEM tool (Arduino) and exit"""
		self.do_disconnectArduino(args)
		self.do_disconnectRobot(args)
		self.poutput('exit')
		return True
	
	
def main():
	# selection of robot
	arg_parser = argparse.ArgumentParser(description='Process commandline arguments...') 
	arg_parser.add_argument('--devid', type=str,default='192.168.126.150' )
	
	startupargs = arg_parser.parse_args()
	
	c = TatemCLI( startupargs.devid )
	sys.exit( c.cmdloop() )  # exit python (with response from c) without returning to __main__
	
	
if __name__ == "__main__":
	sys.exit( main() )         # or just main()
