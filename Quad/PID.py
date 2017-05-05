from changed_pyMultiwii import MultiWii

board = MultiWii("COM5")

def print_PID():
	for i in range(10):
		print board.getData(112)

def set_PID(length , data):
	for i in range(10):
		board.sendCMD(length , 112 , data)

print_PID()

x = [100 , 100 ,100 ]
set_PID(6 , x)

print_PID()
