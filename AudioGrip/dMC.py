# -*- coding: mbcs -*-
# Created by makepy.py version 0.5.01
# By python version 3.10.2 (tags/v3.10.2:a58ebcc, Jan 17 2022, 14:12:15) [MSC v.1929 64 bit (AMD64)]
# From type library '{E0F7789A-88C0-450B-AD6C-A7EB6D227127}'
# On Mon Jan 31 15:03:29 2022
'dMCScripting 1.0 Type Library'
makepy_version = '0.5.01'
python_version = 0x30a02f0

import win32com.client.CLSIDToClass, pythoncom, pywintypes
import win32com.client.util
from pywintypes import IID
from win32com.client import Dispatch

# The following 3 lines may need tweaking for the particular server
# Candidates are pythoncom.Missing, .Empty and .ArgNotFound
defaultNamedOptArg=pythoncom.Empty
defaultNamedNotOptArg=pythoncom.Empty
defaultUnnamedArg=pythoncom.Empty

CLSID = IID('{E0F7789A-88C0-450B-AD6C-A7EB6D227127}')
MajorVersion = 1
MinorVersion = 0
LibraryFlags = 8
LCID = 0x0

from win32com.client import DispatchBaseClass
class IConverter(DispatchBaseClass):
	'IConverter Interface'
	CLSID = IID('{0AF59AC7-A0A3-4DAD-A040-95A935F1DE04}')
	coclass_clsid = IID('{1C2E0932-61B5-4EAB-A832-06EE6564047D}')

	def AddFromFile(self, newVal=defaultNamedNotOptArg):
		'method AddFromFile'
		return self._oleobj_.InvokeTypes(6, LCID, 1, (24, 0), ((8, 0),),newVal
			)

	def AddFromToFiles(self, FromFile=defaultNamedNotOptArg, ToFile=defaultNamedNotOptArg):
		'method AddFromToFiles'
		return self._oleobj_.InvokeTypes(7, LCID, 1, (24, 0), ((8, 0), (8, 0)),FromFile
			, ToFile)

	# The method AudioProperties is actually a property, but must be used as a method to correctly pass the arguments
	def AudioProperties(self, FileName=defaultNamedNotOptArg):
		'property AudioProperties'
		# Result is a Unicode object
		return self._oleobj_.InvokeTypes(18, LCID, 2, (8, 0), ((8, 0),),FileName
			)

	def Convert(self, FileFrom=defaultNamedNotOptArg, FileTo=defaultNamedNotOptArg, Compression=defaultNamedNotOptArg, CompressionSettings=defaultNamedNotOptArg
			, ErrorFile=defaultNamedNotOptArg):
		'method Convert'
		return self._oleobj_.InvokeTypes(13, LCID, 1, (24, 0), ((8, 0), (8, 0), (8, 0), (8, 0), (8, 0)),FileFrom
			, FileTo, Compression, CompressionSettings, ErrorFile)

	# The method GetCompressions is actually a property, but must be used as a method to correctly pass the arguments
	def GetCompressions(self, Index=defaultNamedNotOptArg):
		'property GetCompressions'
		# Result is a Unicode object
		return self._oleobj_.InvokeTypes(9, LCID, 2, (8, 0), ((3, 0),),Index
			)

	def GetConversionError(self, Index=defaultNamedNotOptArg, pRetError=defaultNamedNotOptArg):
		'method GetConversionError'
		return self._oleobj_.InvokeTypes(12, LCID, 1, (24, 0), ((3, 0), (16392, 0)),Index
			, pRetError)

	def GoConversion(self, ConversionType=defaultNamedNotOptArg, NoOptions=defaultNamedNotOptArg, NoOverwrite=defaultNamedNotOptArg, NoConversionFinished=defaultNamedNotOptArg
			, NoErrorLog=defaultNamedNotOptArg):
		'method GoConversion'
		return self._oleobj_.InvokeTypes(8, LCID, 1, (24, 0), ((8, 0), (3, 0), (3, 0), (3, 0), (3, 0)),ConversionType
			, NoOptions, NoOverwrite, NoConversionFinished, NoErrorLog)

	def ReadIDTag(self, File=defaultNamedNotOptArg, Index=defaultNamedNotOptArg, pRetElement=defaultNamedNotOptArg, pRetValue=defaultNamedNotOptArg):
		'method ReadIDTag'
		return self._oleobj_.InvokeTypes(14, LCID, 1, (24, 0), ((8, 0), (3, 0), (16392, 0), (16392, 0)),File
			, Index, pRetElement, pRetValue)

	# The method ReadIDTagElementValue is actually a property, but must be used as a method to correctly pass the arguments
	def ReadIDTagElementValue(self, File=defaultNamedNotOptArg, Index=defaultNamedNotOptArg):
		'property ReadIDTagElementValue'
		# Result is a Unicode object
		return self._oleobj_.InvokeTypes(19, LCID, 2, (8, 0), ((8, 0), (3, 0)),File
			, Index)

	def SetCommercialLicense(self, License=defaultNamedNotOptArg):
		'method SetCommercialLicense'
		return self._oleobj_.InvokeTypes(17, LCID, 1, (24, 0), ((8, 0),),License
			)

	# The method ShowSettings is actually a property, but must be used as a method to correctly pass the arguments
	def ShowSettings(self, Compression=defaultNamedNotOptArg, InCompSettings=defaultNamedNotOptArg):
		'property ShowSettings'
		# Result is a Unicode object
		return self._oleobj_.InvokeTypes(16, LCID, 2, (8, 0), ((8, 0), (8, 0)),Compression
			, InCompSettings)

	def WriteIDTag(self, File=defaultNamedNotOptArg, Element=defaultNamedNotOptArg, Value=defaultNamedNotOptArg):
		'method WriteIDTag'
		return self._oleobj_.InvokeTypes(15, LCID, 1, (24, 0), ((8, 0), (8, 0), (8, 0)),File
			, Element, Value)

	def abc(self):
		'method abc'
		return self._oleobj_.InvokeTypes(10, LCID, 1, (24, 0), (),)

	_prop_map_get_ = {
		"ConvertToFolder": (4, 2, (3, 0), (), "ConvertToFolder", None),
		"DeleteSourceFiles": (3, 2, (3, 0), (), "DeleteSourceFiles", None),
		"PreserveTags": (2, 2, (3, 0), (), "PreserveTags", None),
		"ToFolder": (5, 2, (8, 0), (), "ToFolder", None),
		"VolumeNormalize": (1, 2, (3, 0), (), "VolumeNormalize", None),
		"WasConvError": (11, 2, (3, 0), (), "WasConvError", None),
	}
	_prop_map_put_ = {
		"ConvertToFolder": ((4, LCID, 4, 0),()),
		"DeleteSourceFiles": ((3, LCID, 4, 0),()),
		"PreserveTags": ((2, LCID, 4, 0),()),
		"ToFolder": ((5, LCID, 4, 0),()),
		"VolumeNormalize": ((1, LCID, 4, 0),()),
	}
	def __iter__(self):
		"Return a Python iterator for this object"
		try:
			ob = self._oleobj_.InvokeTypes(-4,LCID,3,(13, 10),())
		except pythoncom.error:
			raise TypeError("This object does not support enumeration")
		return win32com.client.util.Iterator(ob, None)

class IMp3Settings(DispatchBaseClass):
	'IMp3Settings Interface'
	CLSID = IID('{FB485142-6609-429C-A894-34896DD6C95B}')
	coclass_clsid = IID('{183E63EA-0D05-4CF8-A309-BE6071845CA9}')

	def Set(self, BitRate=defaultNamedNotOptArg, Frequency=defaultNamedNotOptArg, ChannelMode=defaultNamedNotOptArg, VbrMode=defaultNamedNotOptArg):
		'method Set'
		return self._oleobj_.InvokeTypes(1, LCID, 1, (24, 0), ((3, 0), (3, 0), (3, 0), (3, 0)),BitRate
			, Frequency, ChannelMode, VbrMode)

	def SetLame(self, BitRate=defaultNamedNotOptArg, Frequency=defaultNamedNotOptArg, ChannelMode=defaultNamedNotOptArg, Mp3Encoding=defaultNamedNotOptArg
			, Mp3Preset=defaultNamedNotOptArg, VBRMaxBitRate=defaultNamedNotOptArg, VBRQuality=defaultNamedNotOptArg):
		'method SetLame'
		return self._oleobj_.InvokeTypes(2, LCID, 1, (24, 0), ((3, 0), (3, 0), (3, 0), (3, 0), (3, 0), (3, 0), (3, 0)),BitRate
			, Frequency, ChannelMode, Mp3Encoding, Mp3Preset, VBRMaxBitRate
			, VBRQuality)

	_prop_map_get_ = {
	}
	_prop_map_put_ = {
	}
	def __iter__(self):
		"Return a Python iterator for this object"
		try:
			ob = self._oleobj_.InvokeTypes(-4,LCID,3,(13, 10),())
		except pythoncom.error:
			raise TypeError("This object does not support enumeration")
		return win32com.client.util.Iterator(ob, None)

class IOggSettings(DispatchBaseClass):
	'IOggSettings Interface'
	CLSID = IID('{773BEA27-E4E4-4032-B29F-150B0F1C7399}')
	coclass_clsid = IID('{A9FF1B87-DC1A-41D5-9AD9-C686AE9DA75A}')

	def Set(self, BitRate=defaultNamedNotOptArg, Frequency=defaultNamedNotOptArg, Channels=defaultNamedNotOptArg, Encoding=defaultNamedNotOptArg):
		'method Set'
		return self._oleobj_.InvokeTypes(1, LCID, 1, (24, 0), ((3, 0), (3, 0), (3, 0), (3, 0)),BitRate
			, Frequency, Channels, Encoding)

	_prop_map_get_ = {
	}
	_prop_map_put_ = {
	}
	def __iter__(self):
		"Return a Python iterator for this object"
		try:
			ob = self._oleobj_.InvokeTypes(-4,LCID,3,(13, 10),())
		except pythoncom.error:
			raise TypeError("This object does not support enumeration")
		return win32com.client.util.Iterator(ob, None)

class IWMASettings(DispatchBaseClass):
	'IWMASettings Interface'
	CLSID = IID('{6A6279A0-ACDE-448E-892A-ADA3B1520397}')
	coclass_clsid = IID('{9E7A0D15-C53E-4564-8D06-93F3300F46AF}')

	def SetWMA(self, Codec=defaultNamedNotOptArg, Setting=defaultNamedNotOptArg, Type=defaultNamedNotOptArg):
		'method SetWMA'
		return self._oleobj_.InvokeTypes(1, LCID, 1, (24, 0), ((8, 0), (8, 0), (3, 0)),Codec
			, Setting, Type)

	_prop_map_get_ = {
	}
	_prop_map_put_ = {
	}
	def __iter__(self):
		"Return a Python iterator for this object"
		try:
			ob = self._oleobj_.InvokeTypes(-4,LCID,3,(13, 10),())
		except pythoncom.error:
			raise TypeError("This object does not support enumeration")
		return win32com.client.util.Iterator(ob, None)

class IWaveSettings(DispatchBaseClass):
	'IWaveSettings Interface'
	CLSID = IID('{40578A1A-59EE-45C6-9D91-1E5FA5BEE302}')
	coclass_clsid = IID('{C1175DFD-4BB0-44EA-8F9D-ECE60F4649E2}')

	def Set(self, Frequency=defaultNamedNotOptArg, Channels=defaultNamedNotOptArg, BitsPerSample=defaultNamedNotOptArg):
		'method Set'
		return self._oleobj_.InvokeTypes(1, LCID, 1, (24, 0), ((3, 0), (3, 0), (3, 0)),Frequency
			, Channels, BitsPerSample)

	_prop_map_get_ = {
	}
	_prop_map_put_ = {
	}
	def __iter__(self):
		"Return a Python iterator for this object"
		try:
			ob = self._oleobj_.InvokeTypes(-4,LCID,3,(13, 10),())
		except pythoncom.error:
			raise TypeError("This object does not support enumeration")
		return win32com.client.util.Iterator(ob, None)

from win32com.client import CoClassBaseClass
# This CoClass is known by the name 'DMCScripting.Converter.1'
class Converter(CoClassBaseClass): # A CoClass
	# Converter Class
	CLSID = IID('{1C2E0932-61B5-4EAB-A832-06EE6564047D}')
	coclass_sources = [
	]
	coclass_interfaces = [
		IConverter,
	]
	default_interface = IConverter

# This CoClass is known by the name 'DMCScripting.Mp3Settings.1'
class Mp3Settings(CoClassBaseClass): # A CoClass
	# Mp3Settings Class
	CLSID = IID('{183E63EA-0D05-4CF8-A309-BE6071845CA9}')
	coclass_sources = [
	]
	coclass_interfaces = [
		IMp3Settings,
	]
	default_interface = IMp3Settings

# This CoClass is known by the name 'DMCScripting.OggSettings.1'
class OggSettings(CoClassBaseClass): # A CoClass
	# OggSettings Class
	CLSID = IID('{A9FF1B87-DC1A-41D5-9AD9-C686AE9DA75A}')
	coclass_sources = [
	]
	coclass_interfaces = [
		IOggSettings,
	]
	default_interface = IOggSettings

# This CoClass is known by the name 'DMCScripting.WMASettings.1'
class WMASettings(CoClassBaseClass): # A CoClass
	# WMASettings Class
	CLSID = IID('{9E7A0D15-C53E-4564-8D06-93F3300F46AF}')
	coclass_sources = [
	]
	coclass_interfaces = [
		IWMASettings,
	]
	default_interface = IWMASettings

# This CoClass is known by the name 'DMCScripting.WaveSettings.1'
class WaveSettings(CoClassBaseClass): # A CoClass
	# WaveSettings Class
	CLSID = IID('{C1175DFD-4BB0-44EA-8F9D-ECE60F4649E2}')
	coclass_sources = [
	]
	coclass_interfaces = [
		IWaveSettings,
	]
	default_interface = IWaveSettings

IConverter_vtables_dispatch_ = 1
IConverter_vtables_ = [
	(( 'VolumeNormalize' , 'pVal' , ), 1, (1, (), [ (16387, 10, None, None) , ], 1 , 2 , 4 , 0 , 56 , (3, 0, None, None) , 0 , )),
	(( 'VolumeNormalize' , 'pVal' , ), 1, (1, (), [ (3, 1, None, None) , ], 1 , 4 , 4 , 0 , 64 , (3, 0, None, None) , 0 , )),
	(( 'PreserveTags' , 'pVal' , ), 2, (2, (), [ (16387, 10, None, None) , ], 1 , 2 , 4 , 0 , 72 , (3, 0, None, None) , 0 , )),
	(( 'PreserveTags' , 'pVal' , ), 2, (2, (), [ (3, 1, None, None) , ], 1 , 4 , 4 , 0 , 80 , (3, 0, None, None) , 0 , )),
	(( 'DeleteSourceFiles' , 'pVal' , ), 3, (3, (), [ (16387, 10, None, None) , ], 1 , 2 , 4 , 0 , 88 , (3, 0, None, None) , 0 , )),
	(( 'DeleteSourceFiles' , 'pVal' , ), 3, (3, (), [ (3, 1, None, None) , ], 1 , 4 , 4 , 0 , 96 , (3, 0, None, None) , 0 , )),
	(( 'ConvertToFolder' , 'pVal' , ), 4, (4, (), [ (16387, 10, None, None) , ], 1 , 2 , 4 , 0 , 104 , (3, 0, None, None) , 0 , )),
	(( 'ConvertToFolder' , 'pVal' , ), 4, (4, (), [ (3, 1, None, None) , ], 1 , 4 , 4 , 0 , 112 , (3, 0, None, None) , 0 , )),
	(( 'ToFolder' , 'pVal' , ), 5, (5, (), [ (16392, 10, None, None) , ], 1 , 2 , 4 , 0 , 120 , (3, 0, None, None) , 0 , )),
	(( 'ToFolder' , 'pVal' , ), 5, (5, (), [ (8, 1, None, None) , ], 1 , 4 , 4 , 0 , 128 , (3, 0, None, None) , 0 , )),
	(( 'AddFromFile' , 'newVal' , ), 6, (6, (), [ (8, 0, None, None) , ], 1 , 1 , 4 , 0 , 136 , (3, 0, None, None) , 0 , )),
	(( 'AddFromToFiles' , 'FromFile' , 'ToFile' , ), 7, (7, (), [ (8, 0, None, None) , 
			 (8, 0, None, None) , ], 1 , 1 , 4 , 0 , 144 , (3, 0, None, None) , 0 , )),
	(( 'GoConversion' , 'ConversionType' , 'NoOptions' , 'NoOverwrite' , 'NoConversionFinished' , 
			 'NoErrorLog' , ), 8, (8, (), [ (8, 0, None, None) , (3, 0, None, None) , (3, 0, None, None) , 
			 (3, 0, None, None) , (3, 0, None, None) , ], 1 , 1 , 4 , 0 , 152 , (3, 0, None, None) , 0 , )),
	(( 'GetCompressions' , 'Index' , 'pVal' , ), 9, (9, (), [ (3, 0, None, None) , 
			 (16392, 10, None, None) , ], 1 , 2 , 4 , 0 , 160 , (3, 0, None, None) , 0 , )),
	(( 'abc' , ), 10, (10, (), [ ], 1 , 1 , 4 , 0 , 168 , (3, 0, None, None) , 0 , )),
	(( 'WasConvError' , 'pVal' , ), 11, (11, (), [ (16387, 10, None, None) , ], 1 , 2 , 4 , 0 , 176 , (3, 0, None, None) , 0 , )),
	(( 'GetConversionError' , 'Index' , 'pRetError' , ), 12, (12, (), [ (3, 0, None, None) , 
			 (16392, 0, None, None) , ], 1 , 1 , 4 , 0 , 184 , (3, 0, None, None) , 0 , )),
	(( 'Convert' , 'FileFrom' , 'FileTo' , 'Compression' , 'CompressionSettings' , 
			 'ErrorFile' , ), 13, (13, (), [ (8, 0, None, None) , (8, 0, None, None) , (8, 0, None, None) , 
			 (8, 0, None, None) , (8, 0, None, None) , ], 1 , 1 , 4 , 0 , 192 , (3, 0, None, None) , 0 , )),
	(( 'ReadIDTag' , 'File' , 'Index' , 'pRetElement' , 'pRetValue' , 
			 ), 14, (14, (), [ (8, 0, None, None) , (3, 0, None, None) , (16392, 0, None, None) , (16392, 0, None, None) , ], 1 , 1 , 4 , 0 , 200 , (3, 0, None, None) , 0 , )),
	(( 'WriteIDTag' , 'File' , 'Element' , 'Value' , ), 15, (15, (), [ 
			 (8, 0, None, None) , (8, 0, None, None) , (8, 0, None, None) , ], 1 , 1 , 4 , 0 , 208 , (3, 0, None, None) , 0 , )),
	(( 'ShowSettings' , 'Compression' , 'InCompSettings' , 'pVal' , ), 16, (16, (), [ 
			 (8, 0, None, None) , (8, 0, None, None) , (16392, 10, None, None) , ], 1 , 2 , 4 , 0 , 216 , (3, 0, None, None) , 0 , )),
	(( 'SetCommercialLicense' , 'License' , ), 17, (17, (), [ (8, 0, None, None) , ], 1 , 1 , 4 , 0 , 224 , (3, 0, None, None) , 0 , )),
	(( 'AudioProperties' , 'FileName' , 'pVal' , ), 18, (18, (), [ (8, 0, None, None) , 
			 (16392, 10, None, None) , ], 1 , 2 , 4 , 0 , 232 , (3, 0, None, None) , 0 , )),
	(( 'ReadIDTagElementValue' , 'File' , 'Index' , 'pVal' , ), 19, (19, (), [ 
			 (8, 0, None, None) , (3, 0, None, None) , (16392, 10, None, None) , ], 1 , 2 , 4 , 0 , 240 , (3, 0, None, None) , 0 , )),
]

IMp3Settings_vtables_dispatch_ = 1
IMp3Settings_vtables_ = [
	(( 'Set' , 'BitRate' , 'Frequency' , 'ChannelMode' , 'VbrMode' , 
			 ), 1, (1, (), [ (3, 0, None, None) , (3, 0, None, None) , (3, 0, None, None) , (3, 0, None, None) , ], 1 , 1 , 4 , 0 , 56 , (3, 0, None, None) , 0 , )),
	(( 'SetLame' , 'BitRate' , 'Frequency' , 'ChannelMode' , 'Mp3Encoding' , 
			 'Mp3Preset' , 'VBRMaxBitRate' , 'VBRQuality' , ), 2, (2, (), [ (3, 0, None, None) , 
			 (3, 0, None, None) , (3, 0, None, None) , (3, 0, None, None) , (3, 0, None, None) , (3, 0, None, None) , 
			 (3, 0, None, None) , ], 1 , 1 , 4 , 0 , 64 , (3, 0, None, None) , 0 , )),
]

IOggSettings_vtables_dispatch_ = 1
IOggSettings_vtables_ = [
	(( 'Set' , 'BitRate' , 'Frequency' , 'Channels' , 'Encoding' , 
			 ), 1, (1, (), [ (3, 0, None, None) , (3, 0, None, None) , (3, 0, None, None) , (3, 0, None, None) , ], 1 , 1 , 4 , 0 , 56 , (3, 0, None, None) , 0 , )),
]

IWMASettings_vtables_dispatch_ = 1
IWMASettings_vtables_ = [
	(( 'SetWMA' , 'Codec' , 'Setting' , 'Type' , ), 1, (1, (), [ 
			 (8, 0, None, None) , (8, 0, None, None) , (3, 0, None, None) , ], 1 , 1 , 4 , 0 , 56 , (3, 0, None, None) , 0 , )),
]

IWaveSettings_vtables_dispatch_ = 1
IWaveSettings_vtables_ = [
	(( 'Set' , 'Frequency' , 'Channels' , 'BitsPerSample' , ), 1, (1, (), [ 
			 (3, 0, None, None) , (3, 0, None, None) , (3, 0, None, None) , ], 1 , 1 , 4 , 0 , 56 , (3, 0, None, None) , 0 , )),
]

RecordMap = {
}

CLSIDToClassMap = {
	'{0AF59AC7-A0A3-4DAD-A040-95A935F1DE04}' : IConverter,
	'{1C2E0932-61B5-4EAB-A832-06EE6564047D}' : Converter,
	'{40578A1A-59EE-45C6-9D91-1E5FA5BEE302}' : IWaveSettings,
	'{C1175DFD-4BB0-44EA-8F9D-ECE60F4649E2}' : WaveSettings,
	'{FB485142-6609-429C-A894-34896DD6C95B}' : IMp3Settings,
	'{183E63EA-0D05-4CF8-A309-BE6071845CA9}' : Mp3Settings,
	'{773BEA27-E4E4-4032-B29F-150B0F1C7399}' : IOggSettings,
	'{A9FF1B87-DC1A-41D5-9AD9-C686AE9DA75A}' : OggSettings,
	'{6A6279A0-ACDE-448E-892A-ADA3B1520397}' : IWMASettings,
	'{9E7A0D15-C53E-4564-8D06-93F3300F46AF}' : WMASettings,
}
CLSIDToPackageMap = {}
win32com.client.CLSIDToClass.RegisterCLSIDsFromDict( CLSIDToClassMap )
VTablesToPackageMap = {}
VTablesToClassMap = {
	'{0AF59AC7-A0A3-4DAD-A040-95A935F1DE04}' : 'IConverter',
	'{40578A1A-59EE-45C6-9D91-1E5FA5BEE302}' : 'IWaveSettings',
	'{FB485142-6609-429C-A894-34896DD6C95B}' : 'IMp3Settings',
	'{773BEA27-E4E4-4032-B29F-150B0F1C7399}' : 'IOggSettings',
	'{6A6279A0-ACDE-448E-892A-ADA3B1520397}' : 'IWMASettings',
}


NamesToIIDMap = {
	'IConverter' : '{0AF59AC7-A0A3-4DAD-A040-95A935F1DE04}',
	'IWaveSettings' : '{40578A1A-59EE-45C6-9D91-1E5FA5BEE302}',
	'IMp3Settings' : '{FB485142-6609-429C-A894-34896DD6C95B}',
	'IOggSettings' : '{773BEA27-E4E4-4032-B29F-150B0F1C7399}',
	'IWMASettings' : '{6A6279A0-ACDE-448E-892A-ADA3B1520397}',
}


