#!/usr/bin/env python

"""test-send.py: Test script to send RC commands to a MultiWii Board."""



from pyMultiwii import MultiWii
import time

if __name__ == "__main__":

    #board = MultiWii("/dev/ttyUSB0")
    board=MultiWii("COM5")
    #board = MultiWii("/dev/tty.SLAB_USBtoUART")

    if True:
        board.arm()
        print  ( "Board is armed now! \n In 3 seconds it will disarm..." )
        time.sleep(3)
        board.disarm()
        print ("Disarmed.")
        time.sleep(3)

    
