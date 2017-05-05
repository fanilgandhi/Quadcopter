#!/usr/bin/env python

from changed_pyMultiwii import MultiWii
import time
	
if __name__ == "__main__":
	
	#board = MultiWii("COM5")
	board = MultiWii("/dev/ttyUSB0")
	board.PRINT = False
	while True:
		board.update_all_values()		
		#print board.print_data()
		time.sleep(0.05)

	
