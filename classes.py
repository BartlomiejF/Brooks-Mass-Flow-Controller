import os
import serial, time

class MFCPanel():
	'''This is a class representing Brooks Secondary Electronics 0250 series
	device - is path to the file descriptor of Brooks Secondary Electronics (usually '/dev/ttyUSB*')
				note that you must have access to the file descriptor (the easiest way is to write udev rule)
				the /dev/ttyUSB* is actually usb to rs232 converter'''
				
	def __init__(self, device):
		self.meas = serial.Serial(device, timeout=0.5)
		self.address=self.idn()
		self.UnitCode={ '00': 'ml',
							'01': 'mls',
							'02': 'mln',
							'03': 'l',
							'04': 'ls',
							'05': 'ln',
							'06': 'cm^3',
							'07': 'cm^3s',
							'08': 'cm^3n',
							'09': 'm^3',
							'10': 'm^3s',
							'11': 'm^3n',
							'12': 'g',
							'13': 'lb',
							'14': 'kg',
							'15': 'ft^3',
							'16': 'ft^3s',
							'17': 'ft^3n',
							'18': 'scc',
							'19': 'sl',
							'20': 'bar',
							'21': 'mbar',
							'22': 'psi',
							'23': 'kPa',
							'24': 'Torr',
							'25': 'atm',
							'26': 'Volt',
							'27': 'mA',
							'28': 'oC',
							'29': 'oK',
							'30': 'oR',
							'31': 'oF',
							'32': 'g/cc',
							'33': 'sg',
							'34': '%',
							'35': 'lb/in^3',
							'36': 'lb/ft^3',
							'37': 'lb/gal',
							'38': 'kg/m^3',
							'39': 'g/ml',
							'40': 'kg/l',
							'41': 'g/l'}
							
		self.RevUnitCode=dict((v,k) for (k,v) in self.UnitCode.items())
		
		self.RateTimeCode={'0': 'none',
								'1': 'sec',
								'2': 'min',
								'3': 'hrs',
								'4': 'day'}
								
		self.RevRateTimeCode={'none':'00',
								'sec':'01',
								'min':'02',
								'hrs':'03',
								'day':'04'}
 
	def sendCommand(self, command, read=True):
		"""Send commands directly to the panel. If read is set to True this function will allow User to read response from the panel.
		If read is False the purge function will be called to clear all past responses."""
		if isinstance(command, list):
			for com in command:
				self.meas.write(data=com)
				time.sleep(0.5)
				if not read:
					self.purge()
		elif isinstance(command, bytes):
			self.meas.write(data=command)
			time.sleep(0.5)
			if not read:
				self.purge()
 
	def read(self):
		"""Read single line from the panel (response from last command)."""
		out=self.meas.readline()
		print(out)		# ~ for testing purposes:

		return out
	
	def purge(self):
		"""Read all lines from panel output to prevent reading wrong response."""
		_=self.meas.readlines()
		
	def finish(self):
		'''Close the file descriptor'''
		self.meas.close()
		
	def idn(self):
		'''Read identification of the device. It enables reading its own address number.'''
		self.sendCommand(command=b'AZI\r')
		ident=self.read()
		ident=ident.decode(encoding='utf-8').split(',')[1]
		return ident
		
	def setOutput(self, channel, val):
		'''Set gas flow.'''
		com='AZ'+str(self.address)+'.0'+str(channel*2)+'P01='+str(val)+'\r'
		com=bytes(com, encoding='utf-8')
		self.sendCommand(command=com)
		self.read()
		
	def readUnits(self, channel):
		'''Read gas flow units.'''
		com='AZ'+str(self.address)+'.0'+str(channel*2-1)+'P04?\r'
		self.sendCommand(bytes(com, encoding='utf-8'))
		outputUnit_first=self.read()
		outputUnit_first=outputUnit_first.decode(encoding='utf-8').split(',')[4]
		outputUnit_first=str(self.UnitCode[outputUnit_first])
		com='AZ'+str(self.address)+'.0'+str(channel*2-1)+'P10?\r'
		self.sendCommand(bytes(com, encoding='utf-8'))
		outputUnit_second=self.read()
		outputUnit_second=outputUnit_second.decode(encoding='utf-8').split(',')[4]
		outputUnit_second=str(self.RateTimeCode[outputUnit_second])
		outputUnit_whole=outputUnit_first+'/'+outputUnit_second
		return outputUnit_whole
	
	def readOutput(self, channel, unit=False):
		"""Reads output of mfc connected to the channel(1 to 4) if unit argument is set to True the function reads also unit of the output
		returns single output value as float if unit is False
		returns list contatining with output flow value as float(index 0) and its unit as string(index 1)"""
		com='AZ'+str(self.address)+'.0'+str(channel*2)+'P01?\r'
		self.sendCommand(bytes(com, encoding='utf-8'))
		outputFlow=self.read()
		outputFlow=float(outputFlow.decode(encoding='utf-8').split(',')[4])
		if unit:
			flowunit=self.readUnits(channel=channel)
			return [outputFlow, flowunit]
		return outputFlow
		
	def readPVRate(self, channel, unit=False):
		'''Reads PVRate'''
		com='AZ'+str(self.address)+'.0'+str(channel*2-1)+'K\r'
		self.sendCommand(bytes(com, encoding='utf-8'))
		PVRate=self.read()
		PVRate=float(PVRate.decode(encoding='utf-8').split(',')[6])
		if unit:
			flowunit=self.readUnits(channel=channel)
			return [PVRate, flowunit]
		return PVRate
		
	def setUnits(self, channel, VolUnit=None, TimeUnit=None):
		"""Sets flow units of channel given in channel argument, VolUnit should be string of volume unit(eg. 'ml'), TimeUnit should be string of time unit(eg. 'sec')
		The flow units should be set as VolUnit/TimeUnit. Please refer to UnitCode and RateTimeCode attributes(from __init__() function) for appropriate unit names"""
		cmd=list()
		if VolUnit:
			com='AZ'+str(self.address)+'.0'+str(channel*2-1)+'P04='+str(self.RevUnitCode[VolUnit])+'\r'
			com=bytes(com, encoding='utf-8')
			cmd+=[com]
		if TimeUnit:
			com='AZ'+str(self.address)+'.0'+str(channel*2-1)+'P10='+str(self.RevRateTimeCode[TimeUnit])+'\r'
			com=bytes(com, encoding='utf-8')
			cmd+=[com]
		self.sendCommand(cmd)
		for cm in cmd: 		# ~ for testing purposes:
			self.read()
			
	def OpenClose(self, channel):
		'''Set VOR to Closed or Normal'''
		state=self.ReadState(channel=channel)
		if state=='0':
			state=1
		elif state=='1':
			state=0
		else:
			state=0
		cmd='AZ'+str(self.address)+'.0'+str(channel*2)+'P29='+str(state)+'\r'
		cmd=bytes(cmd, encoding='utf-8')
		self.sendCommand([cmd], read=False)
		
	def ReadState(self, channel):
		'''Check what is the state of VOR'''
		cmd='AZ'+str(self.address)+'.0'+str(channel*2)+'P29?\r'
		cmd=bytes(cmd, encoding='utf-8')
		self.sendCommand([cmd])
		state=self.read()
		state=str(state.decode(encoding='utf-8').split(',')[4])
		return state
		
	def ReadFullScale(self, channel): #not sure if it is necessary
		'''Read maximum output'''
		cmd='AZ'+str(self.address)+'.0'+str(channel*2)+'P09?\r'
		cmd=bytes(cmd, encoding='utf-8')
		self.sendCommand([cmd])
		self.read()
	
class MFC():
	'''This class represents single Brooks Mass Flow Controller connected to Brooks Secondary Electronics series 0250.
	panel - an instantion of MFCPanel class
	channel - should be integer (1-4), the number of channel that MFC is connected to '''
	def __init__(self, panel, channel):
		self.panel=panel
		self.channel=channel
		self.PVRate=0
		self.unit=self.panel.readUnits(channel=self.channel)
		self.updatePVRate()
		self.SPRate=0
		
	def OpenCloseValve(self):
		self.panel.OpenClose(channel=self.channel)
		
	def updatePVRate(self):
		pvrate=self.panel.readPVRate(channel=self.channel)
		self.PVRate=str(pvrate)+' '+self.unit
		
	def setSPRate(self, value):
		self.panel.setOutput(channel=self.channel, val=value)
		
