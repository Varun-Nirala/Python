import sys
import xml.etree.ElementTree as ET



file_data = open("abc.xml", "r")
str_data = file_data.read()

xml_data = ET.fromstring(str_data)

reelstripdef_list = xml_data.findall("reelstripdef")

for reelstripdef in reelstripdef_list:
	stop_list = reelstripdef.findall("stop")
	print(reelstripdef.get("name"), "NumberOfSymbol = ", len(stop_list))
	for symbol in stop_list:
		print("\t", symbol.get("symbolname"))
