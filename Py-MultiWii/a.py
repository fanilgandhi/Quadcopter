### common modules
import time

## MultiWii setup
from pyMultiwii import MultiWii
board = MultiWii("/dev/ttyUSB0")
#board = MultiWii("COM5")

## Socket Setup
from socketIO_client import SocketIO, LoggingNamespace

def lol(): pass

client = SocketIO('localhost', 80, LoggingNamespace)

while True:
	board.getData(MultiWii.ATTITUDE)
	client.emit('message', {'attitude': str(board.attitude)}, lol)
	time.sleep(0.1)
	#client.wait(seconds=0.05)
	#socketIO.wait_for_callbacks(seconds=1)
