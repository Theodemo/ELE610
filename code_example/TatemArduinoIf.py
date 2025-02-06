#!/usr/bin/env python
#
# Originally made by ABB 2022
# Some updates for UiS ELE610 course by Karl Skretting October 2023 ...

from datetime import datetime
from http import client
import threading
import asyncio
import sys
import time
import json
import os

from bleak import BleakScanner, BleakClient, BleakError
# from bleak.backends.scanner import AdvertisementData
# from bleak.backends.device import BLEDevice

jsonFileDir = "C:\\TFS\\TATEM\\datasets"   


def discover():
	"""List available bluetooth devices by use of BleakScanner.discover"""
	print( "List available BLE-devices by use of BleakScanner.discover" )
	devs = asyncio.run( BleakScanner.discover() )
	#
	if devs:
		print( "Unnamed devices:" )
		for dev in devs:
			if not dev.name:
				print( f"* {dev.address = }" )
		print( "Named devices:" )
		for dev in devs:
			if dev.name:
				print( f"* {dev.address = }, {dev.name=}" )
	#
	if not devs:
		print( f"No bluetooth-low-energy (BLE) devices were found" )
	#
	return


# All necessary bluetooth communication with the Arduino is handled from here. 
class TatemArduinoIf(threading.Thread):
	# Creating the BLE-object representing the Arduino
	def __init__(self, ip):
		self.ip = ip
		self.tA = "10"
		self.tO = "10"
		self.tR = "10"
		self.client = None
		self.keepConnection = True
		self.UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
		self.UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
		self.UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
		#
		threading.Thread.__init__(self)
		self.start()

	# Setting up the BLE-connection with the Arduino. 
	# Will be up and running until it is prompted to disconnect using the "Disconnect"-function.
	async def ConnectingBLE(self, ble_address: str):
		device = await BleakScanner.find_device_by_address(ble_address, timeout=20.0)
		if not device:
			raise BleakError(f"A device with address {ble_address} could not be found.")
		async with BleakClient(device) as self.client:
			print("Connection successful")
			while self.keepConnection:
				await asyncio.sleep(1)
			# Do we need to add something here to make sure the connection is broken
	
	# Starts up a BLE-connection with the Arduino. This function overrides the "run"-function in the thread class. 
	def run(self):
		asyncio.run(self.ConnectingBLE(self.ip))

	# Disconnecting the BLE-connection with the Arduino
	def Disconnect(self):
		self.keepConnection = False
	
	# Checking if the BLE-connection with the Arduino is present
	def IsConnected(self):
		if self.client != None:
			status = self.client.is_connected
		else:
			status = False
		return status
	
	# Handling the BLE-communication with the Arduino
	async def run_remote_cmd(self, cmd: str, doPrint=True) -> str:
		print( f"Start of run_remote_cmd() {cmd=}")
		dataReceived=bytearray()
		cmdReceivedEvent = asyncio.Event()

		def handle_rx(_: int, data: bytearray):
			if doPrint: print("received:", data)
			dataReceived.extend(data)
			# Maybe have a time-out here - if it takes more than maybe 20 s, then we are timing out
			if dataReceived[-2:] == b'$0' or  dataReceived[-2:] == b'$1': 
				# This is to signal that we are done collecting the data
				if doPrint: print("End of data set")
				cmdReceivedEvent.set()

		tgetData = time.time()
		# Think this is notifying what to do when the data from the Arduino starts coming in
		if doPrint: print("1: Notify Arduino")
		await self.client.start_notify(self.UART_TX_CHAR_UUID, handle_rx) 
		# Send command
		# May be the "getreport"-message to the Arduino, which will make it send the report. 
		if doPrint: print(f"2: Send command '{cmd}'")
		data = bytes(cmd+'\r\n',"utf8")
		# Once it has sent everything, it will end with a "$0", which indicates that it is done
		if doPrint: print("3: Execute command until '$0'")
		await self.client.write_gatt_char(self.UART_RX_CHAR_UUID, data) 
		# think this is waiting until all the data has been collected. 
		# When it has been collected, the .set()-function is started and 
		# that will trigger the next part - the stop notifying part
		if doPrint: print("4: Wait until data has been collected")
		await cmdReceivedEvent.wait() 
		#
		if doPrint: print("5: Stop")
		await self.client.stop_notify(self.UART_TX_CHAR_UUID)
		#
		if doPrint: print(f'6: Time getting data: {time.time()-tgetData:6.3f} [s]')
		if doPrint: print("7: Decode")
		datadecoded = dataReceived.decode()
		if doPrint: print(  "8: Return from 'BLE-communication with the Arduino'-function" )
		print( f"   Decoded data has length {len(datadecoded)}" )
		return datadecoded   

	# Converting the collected Arduino data to a json-file
	def writeFile(self, data, filedir):
		e = datetime.now()
		filename = e.strftime("%Y-%m-%d_%H-%M-%S")+'.json'
		isDir = os.path.exists(filedir)
		if not isDir: os.makedirs(filedir)
		dfn = os.path.join(filedir, filename)
		with open(dfn, 'a', encoding='utf-8') as f:
			json.dump(data, f, indent=1, separators=(',', ': '))
			f.close()
		ok = os.path.exists(dfn)
		if ok: print( f"TatemArduinoIf.writeFile(..): Written {os.path.getsize(dfn)} bytes to {dfn}" )
		return dfn if ok else ""

	# Collecting the data from the connected Arduino
	def GetReport(self):
		dfn = ""
		if self.IsConnected():
			# Sending the "getreport"-command to the Arduino, 
			# which will instruct it to start sending the stored data
			print( f"TatemArduinoIf.GetReport(): Get report from connected TATEM tool" )
			report = asyncio.run( self.run_remote_cmd( 'getreport' ) ) 
			if report[-2:]=='$0':
				print( f"Loads json report into Python dict 'repDict'" )
				repDict = json.loads(report[:-2])
				print( f"Write Python dict 'repDict' to file in {jsonFileDir=}" )
				dfn = self.writeFile(repDict, jsonFileDir)
			else:
				print( "TatemArduinoIf.GetReport(): Not able to convert report from json to dict" )
				print( f"{report = }" )
		else:
			print("There is no Arduino connected")
		print("done with GetReport() function!")
		return dfn

	# Resetting the connected Arduino
	def Reset(self):
		message = "reset"
		if self.IsConnected():
			print('resetting the Arduino...')
			resetDone = asyncio.run( self.run_remote_cmd( message ) )
			if resetDone[-2:]=='$0':
				print("reset has been successful")
			else:
				print( "TatemArduinoIf.Reset(): Something went wrong" )
		else:
			print( "TatemArduinoIf.Reset(): There is no Arduino connected" )

	# Setting the tA value on the Arduino to the tA-value in the rapid code,
	# KS assume unit is us, and that default value is 100000 us = 100 ms = 0.1 s 
	# this should perhaps be verified by inspecting the Arduino code
	def SetTa(self, tA_new: str):
		message = "SetTa " + tA_new
		if self.IsConnected():
			print( f"setting Ta-value on Arduino,  {message=}" )
			tA = asyncio.run( self.run_remote_cmd( message, doPrint=False ) )
			if tA[-2:]=='$0':
				self.tA =tA[:-2]
				print( f"tA value has been set to: {self.tA} [us]" )
			else:
				print( "TatemArduinoIf.SetTa(): Something went wrong" )
		else:
			print( "TatemArduinoIf.SetTa(): There is no Arduino connected" )
	
	
	# Setting the tO value on the Arduino to the tO-value in the rapid code, 
	# KS assume unit is us, and that default value is 300000 us = 300 ms = 0.3 s 
	# this should perhaps be verified by inspecting the Arduino code
	def SetTo(self, tO_new: str):
		message = "SetTo " + tO_new
		if self.IsConnected():
			print( f"setting To-value on Arduino,  {message=}" )
			tO = asyncio.run( self.run_remote_cmd( message, doPrint=False ) )
			if tO[-2:]=='$0':
				self.tO = tO[:-2]
				print( f"tO value has been set to: {self.tO} [us]" )
			else:
				print( "TatemArduinoIf.SetTo(): Something went wrong" )
		else:
			print( "TatemArduinoIf.SetTo(): There is no Arduino connected" )
	
	# Setting the tR value on the Arduino to the tR-value in the rapid code,
	# KS assume unit is us, and that default value is 100000 us = 100 ms = 0.1 s
	# this should perhaps be verified by inspecting the Arduino code
	def SetTr(self, tR_new: str):
		message = "SetTr " + tR_new
		if self.IsConnected():
			print( f"setting Tr-value on Arduino,  {message=}" )
			tR = asyncio.run( self.run_remote_cmd( message, doPrint=False ) )
			if tR[-2:]=='$0':
				self.tR = tR[:-2]
				print( f"tR value has been set to: {self.tR} [us]" )
			else:
				print( "TatemArduinoIf.SetTr(): Something went wrong" )
		else:
			print( "TatemArduinoIf.SetTr(): There is no Arduino connected" )

def main():
	print("Test of 'TatemArduinoIf.py' should probably be started from 'tatemCom*.py")
	# tatemArduinoIf = TatemArduinoIf('10.47.89.50')       # on ABB tool ?
	tatemArduinoIf = TatemArduinoIf("A1:F8:14:CE:BA:AC")   # UiS Arduino

if __name__ == "__main__":
	main()
	
