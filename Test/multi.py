#!/usr/bin/env python
import time , struct , serial
import threading , collections
from socketIO_client import SocketIO , LoggingNamespace

###############################
# Multiwii Serial Protocol
# Hex value for MSP request
##############################
BASIC="\x24\x4d\x3c\x00"		# MSG Send Header (to MultiWii)

MSP_RAW_IMU	=BASIC+"\x66\x66"	# MSG ID: 102
MSP_MOTOR	=BASIC+"\x68\x68"	# MSG ID: 104
MSP_RC 		=BASIC+"\x69\x69"	# MSG ID: 105
MSP_ATTITUDE=BASIC+"\x6C\x6C"	# MSG ID: 108
MSP_ALTITUDE=BASIC+"\x6D\x6D"	# MSG ID: 109

MSP_SET_RC	=BASIC+"\xC8\xC8"  	# MSG ID: 200

class Multiwii: 
	ARM_FLAG = 0  ## disarm = -1 , none = 0 , arm = 1
	PRINT = False

	def __init__(self , port):
		self.started = True
		
		self.looptime = 1 / 7 ## 7 times in 1 second
		self.armed    = "disarmed"
 
		self.ser = serial.Serial()
		self.ser.port = port
		self.ser.baudrate = 115200
		self.ser.bytesize=serial.EIGHTBITS
		self.ser.parity=serial.PARITY_NONE
		self.ser.stopbits=serial.STOPBITS_ONE
		self.ser.timeout=0
		self.ser.xonxoff=False
		self.ser.rtscts=False
		self.ser.dsrdtr=False
		self.ser.writeTimeout=2

		self.timeMSP=0.02
		self.client = SocketIO('localhost', 80, LoggingNamespace)

		try : 
			self.ser.open()
		except Exception , error :
			print "Error while open serial port : " + str(error)
			exit(1)

		###############################
		# Initialize Global Variables
		###############################
		self.acc_x 	=	0.0
		self.acc_y 	=	0.0
		self.acc_z 	=	0.0
		self.gyro_x =	0.0
		self.gyro_y =	0.0
		self.gyro_z =	0.0
		self.mag_x 	=	0.0
		self.mag_y 	=	0.0
		self.mag_z 	=	0.0
		
		self.motor1	=	0.0
		self.motor2	= 	0.0		
		self.motor3	= 	0.0
		self.motor4	= 	0.0
		
		self.roll 	=	0.0
		self.pitch 	=	0.0
		self.yaw 	= 	0.0
		self.throttle	= 	0.0
		self.buffer 	= 	collections.deque()
		
		self.angx 	=	0.0
		self.angy	=	0.0
		self.heading =	0.0
		
		self.altitude 	=	0.0
				
		self.loopThread = threading.Thread(target= self.loop)
		if self.ser.isOpen():
			print("Wait 5 sec for calibrate Multiwii")
			time.sleep(5)
			self.loopThread.start()

	def stop(self):
		self.started = False


	#############################################################
	# littleEndian(value)  : hex ==> integer 
	#############################################################
	def littleEndian(self, value):
		length = len(value)
		actual = ""
		for x in range(0, length/2 ):
			actual += value[length-2-(2*x):length-(2*x)]
			x += 1
		intVal = self.twosComp(actual)
		return intVal				

	###################################################################
	# twosComp(hexValue) :  hex ==> swaps & decimal 
	###################################################################
	def twosComp(self, hexValue):
		firstVal = int(hexValue[:1], 16)
		if firstVal >= 8:	
			bValue = bin(int(hexValue, 16))
			bValue = bValue[2:]	
			newBinary = []
			length = len(bValue)
			index = bValue.rfind('1')	
			for x in range(0, index+1):	
				if x == index: 
					newBinary.append(bValue[index:])
				elif bValue[x:x+1] == '1':
					newBinary.append('0')
				elif bValue[x:x+1] == '0':
					newBinary.append('1')
				x += 1
			newBinary = ''.join(newBinary) 
			finalVal = -int(newBinary, 2)	
			return finalVal
				
		else:		
			return int(hexValue, 16)

	
	def sendData(self, data_length, code, data):
		checksum = 0
		total_data = ['$', 'M', '<', data_length, code] + data
		for i in struct.pack('<2B%dh' % len(data), *total_data[3:len(total_data)]):
			checksum = checksum ^ ord(i)
		total_data.append(checksum)
		try:
			b = self.ser.write(struct.pack('<3c2B%dhB' % len(data), *total_data))
		except Exception, ex:
			print 'send data error for ' + str(code)
			print(ex)
		return b

	

	#############################################################
	# askIMU() : Do everything to ask the MW for data and save it on globals 
	#############################################################
	def askIMU(self):
		self.ser.flushInput()
		self.ser.flushOutput()
		self.ser.write(MSP_RAW_IMU)
		time.sleep(self.timeMSP)
		response = self.ser.readline()
		if str(response) == "": return
		else:
			msp_hex = response.encode("hex")
	
			if msp_hex[10:14] == "": print("acc_x unavailable")
			else: self.acc_x = float(self.littleEndian(msp_hex[10:14]))
	
			if msp_hex[14:18] == "": print("acc_y unavailable")
			else: self.acc_y = float(self.littleEndian(msp_hex[14:18]))
	
			if msp_hex[18:22] == "": print("acc_z unavailable")
			else: self.acc_z = float(self.littleEndian(msp_hex[18:22]))

			if msp_hex[22:26] == "": print("gyro_x unavailable")
			else: self.gyro_x = float(self.littleEndian(msp_hex[22:26]))
	
			if msp_hex[26:30] == "": print("gyro_y unavailable")
			else: self.gyro_y = float(self.littleEndian(msp_hex[26:30]))
	
			if msp_hex[30:34] == "": print("gyro_z unavailable")
			else: self.gyro_z = float(self.littleEndian(msp_hex[30:34]))
	
			if msp_hex[34:38] == "": print("mag_x unavailable")
			else: self.mag_x = float(self.littleEndian(msp_hex[34:38]))
	
			if msp_hex[38:42] == "": print("mag_y unavailable")
			else: self.mag_y = float(self.littleEndian(msp_hex[38:42]))
	
			if msp_hex[42:46] == "": print("mag_z unavailable")
			else: self.mag_z = float(self.littleEndian(msp_hex[42:46]))


	#############################################################
	# askATT() : Do everything to ask the MW for data and save it on globals 
	#############################################################
	def askATT(self):
		self.ser.flushInput()
		self.ser.flushOutput()
		self.ser.write(MSP_ATTITUDE)
		time.sleep(self.timeMSP)
		response = self.ser.readline()
		if str(response) == "": return
		else:
			msp_hex = response.encode("hex")
	
			if msp_hex[10:14] == "": print("angx unavailable")
			else: self.angx = float(self.littleEndian(msp_hex[10:14]))
	
			if msp_hex[14:18] == "": print("angy unavailable")
			else: self.angy = float(self.littleEndian(msp_hex[14:18]))
	
			if msp_hex[18:22] == "": 
				if self.PRINT : print("heading unavailable")
			else: self.heading = float(self.littleEndian(msp_hex[18:22]))
			

	#############################################################
	# askALT() : Do everything to ask the MW for data and save it on globals 
	#############################################################
	def askALT(self):
		self.ser.flushInput()
		self.ser.flushOutput()
		self.ser.write(MSP_ALTITUDE)
		time.sleep(self.timeMSP)
		response = self.ser.readline()
		if str(response) == "": return
		else:
			msp_hex = response.encode("hex")
	
			if msp_hex[10:14] == "": print("altitude unavailable")
			else: self.altitude = float(self.littleEndian(msp_hex[10:14]))

	#############################################################
	# askRC() : Do everything to ask the MW for data and save it on globals 
	#############################################################
	def askRC(self):
		self.ser.flushInput()
		self.ser.flushOutput()
		self.ser.write(MSP_RC)
		time.sleep(self.timeMSP)
		response = self.ser.readline()
		if str(response) == "": return
		else:
			msp_hex = response.encode("hex")
	
			if msp_hex[10:14] == "": print("roll unavailable")
			else: self.roll = float(self.littleEndian(msp_hex[10:14]))
	
			if msp_hex[14:18] == "": print("pitch unavailable")
			else: self.pitch = float(self.littleEndian(msp_hex[14:18]))
	
			if msp_hex[18:22] == "": print("yaw unavailable")
			else: self.yaw = float(self.littleEndian(msp_hex[18:22]))
	
			if msp_hex[22:26] == "": print("throttle unavailable")
			else: self.throttle = float(self.littleEndian(msp_hex[22:26]))


	def askMOTOR(self):
		self.ser.flushInput()
		self.ser.flushOutput()
		self.ser.write(MSP_MOTOR)
		time.sleep(self.timeMSP)
		response = self.ser.readline()
		if str(response) == "": return
		else:
			msp_hex = response.encode("hex")
	
			if msp_hex[10:14] == "": print("motor1 unavailable")
			else: self.motor1 = float(self.littleEndian(msp_hex[10:14]))
	
			if msp_hex[14:18] == "": print("motor2 unavailable")
			else: self.motor2 = float(self.littleEndian(msp_hex[14:18]))
	
			if msp_hex[18:22] == "": print("motor3 unavailable")
			else: self.motor3 = float(self.littleEndian(msp_hex[18:22]))
	
			if msp_hex[22:26] == "": print("motor4 unavailable")
			else: self.motor4 = float(self.littleEndian(msp_hex[22:26]))


	def setRC(self , rcData): ## format roll , pitch ,yaw , throttle 
		if ((type(rcData) == list ) and (len(rcData) == 4)):
			self.sendData(8, 200, rcData)    ### SET_RAW_RC : 200 
			time.sleep(self.timeMSP)
		else:
			if self.PRINT : print "Inappropriate values to setRC " + str(rcData)


	def arm(self):
		timer = 0 
		start = time.time()
		while (time.time() - start) < 0.5:
			data = [1500,1500,2000,1000]
			self.setRC(data)
			time.sleep(0.05)
		self.armed = "armed"

	def disarm(self):
		timer = 0 
		start = time.time()
		while (time.time() - start) < 0.5:
			data = [1500,1500,1000,1000]
			self.setRC(data)
			time.sleep(0.05)
		self.armed = "disarmed"


	def loop(self):
		print "Success \n starting data stream "
		try:
			while self.started:
				if (self.ARM_FLAG != 0 ) :
					if self.ARM_FLAG > 0 : self.arm()
					else : self.disarm()
					self.ARM_FLAG = 0 

				while len(self.buffer) > 0 :
					rcData = self.buffer.popleft()
					self.setRC(rcData)					

				self.askIMU()
				self.askMOTOR()
				self.askRC()				
				self.askATT()
				self.askALT()
				
				message  = ' {'
				message += ' "status" : "{0}", '.format(self.armed)
				message += ' "ax" 	: {0}, "ay" 	: {1}, "az" 	: {2}, '.format(self.acc_x , self.acc_y , self.acc_z)
				message += ' "gx" 	: {0}, "gy" 	: {1}, "gz" 	: {2}, '.format(self.gyro_x , self.gyro_y, self.gyro_z)
				message += ' "mag_x": {0}, "mag_y" 	: {1}, "mag_z" 	: {2}, '.format(self.mag_x , self.mag_y, self.mag_z)
				message += ' "motor_1":{0},"motor_2": {1}, "motor_3": {2}, "motor_4":{3},'.format(self.motor1 , self.motor2 , self.motor3, self.motor4)
				message += ' "roll" : {0}, "pitch" 	: {1}, "yaw" 	: {2}, "throttle": {3}, '.format( self.roll, self.pitch, self.yaw, self.throttle)					
				message += ' "angx" : {0}, "angy" 	: {1}, "heading": {2}, '.format(self.angx , self.angy , self.heading)
				message += ' "altitude" : {0} '.format(self.altitude)
				message += ' }'	
				
				self.client.emit('read_message' , message , lambda:None)	
				message = " roll : {0} , pitch : {1} , yaw : {2} , throttle : {3} , arm : {4} ".format(self.roll , self.pitch , self.yaw , self.throttle , self.ARM_FLAG)
				self.client.emit("log" , message , lambda:None	)			
				time.sleep(self.looptime)

			self.ser.close()
			file.close()
		
		except Exception,e1:	# Catches any errors in the serial communication
			print("Error on main: " + str(e1) )

