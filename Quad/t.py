#!/usr/bin/env python
import time ,os , json
import subprocess ,select

from socketIO_client import SocketIO, LoggingNamespace
from changed_pyMultiwii import MultiWii

filename = "../message.txt"

def fetch_data(line):
	line = json.loads(line)
	key = line.keys()[0]
	value = line[key]
	if key in border_values.keys():
		border_value = border_values[key]
		if (border_value[0] <= value <= border_value[1]) :
			return [key , value , border_value[2]]
	return None
	
if __name__ == "__main__":
	if 1: #try :
		open(filename , "w+").close()
		fp = subprocess.Popen(['tail' , '-F' , filename], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		new_data = select.poll()
		new_data.register(fp.stdout)
		client = SocketIO('localhost', 80, LoggingNamespace)
	else: #except:
		print "Error in basic setup "
		exit(0)
			
	board = MultiWii("/dev/ttyUSB0")
	board.PRINT = True
	border_values = board.border_values

	if 1: #try :
		while True:			
			data = {}
			while new_data.poll(1):
				line = fp.stdout.readline()
				if line[0] == '{' : 
					line = fetch_data(line.strip())
					if line != None:
						if not data.has_key(line[2]) : data[ line[2] ] = {}
						data[line[2]][line[0]] = line[1]

			if ( data != {} ) :
				if data.has_key("rc") :
					temp_rc = board.rc
					temp_rc.update(data["rc"])
					board.sendCMD(8, MultiWii.SET_RAW_RC, temp_rc)	
				
			## Send New Data ##	
			board.getData(105)
			temp = board.rc
			client.emit('read_message', temp , lambda:None)
			time.sleep(0.1)
			print temp
	else:	#except :
		board.disarm()
		exit(0)

