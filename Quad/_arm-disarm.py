#!/usr/bin/env python

from changed_pyMultiwii import MultiWii
import time
	

if __name__ == "__main__":
	
	#board = MultiWii("COM5")
	board = MultiWii("/dev/ttyUSB0")
	board.PRINT = True

	for i in range(3):
		print "Arming Board \n"
		board.arm()
		time.sleep(2)
		print "Disarming Board \n"
		board.disarm()
		time.sleep(2)

