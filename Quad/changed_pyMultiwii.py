#!/usr/bin/env python
import serial, time, struct
class MultiWii:
	"""MultiWii Serial Protocol message ID"""
	RAW_IMU					= 102
	MOTOR					= 104
	RC					= 105
	RAW_GPS					= 106
	COMP_GPS				= 107
	ATTITUDE				= 108
	ALTITUDE				= 109
	PID					= 112
	SET_RAW_RC				= 200
	SET_RAW_GPS				= 201
	SET_PID					= 202
	IS_SERIAL				= 211
	DEBUG					= 254
	PRINT					= True

	"""Class initialization"""
	def __init__(self, serPort):
		self.raw_imu = { 
			'acc_x' : None ,		'acc_y' : None ,		'acc_z' : None ,
			'gyro_x': None ,		'gyro_y': None ,		'gyro_z': None }
		self.motor  = { 
			'motor_1' : None ,	  'motor_2' : None ,
			'motor_3' : None ,	  'motor_4' : None }
		
		self.rc	 = {
			'roll' : None ,		 'pitch' : None , 
			'yaw'  : None ,		 'throttle' : None }
		
		self.raw_gps = { 'raw_gps' : None }
		self.comp_gps = { 'comp_gps' : None }
		
		self.attitude   = { 
			'ang_x' : None ,		'ang_y' : None ,		'heading' : None }
		self.altitude   = { 'altitude' : None }
		self.pid	= { 'pid' : None }
		self.temp = None
		
		self.border_values = {
			'throttle' 	: {1150 , 1850 , 'rc'},
			'roll'	 	: {1000 , 2000 , 'rc'},
			'pitch'		: {1000 , 2000 , 'rc'},
			'yaw'	  	: {1000 , 2000 , 'rc'},
			'arm'	  	: { -1	, 1	, 'control' }
		}

		self.ser = serial.Serial()
		self.ser.port = serPort
		self.ser.baudrate = 115200
		self.ser.bytesize = serial.EIGHTBITS
		self.ser.parity = serial.PARITY_NONE
		self.ser.stopbits = serial.STOPBITS_ONE
		self.ser.timeout = 0
		self.ser.xonxoff = False
		self.ser.rtscts = False
		self.ser.dsrdtr = False
		self.ser.writeTimeout = 2
		"""Time to wait until the board becomes operational"""
		wakeup = 3
		try:
			self.ser.open()
			if self.PRINT: print "Waking up board on "+self.ser.port
			for i in range(wakeup):
				if self.PRINT: print "."
				time.sleep(1)
		except Exception, error:
			print "\n\nError opening " + self.ser.port + " port.\n" + str(error) + "\n\n"
			if self.PRINT : print "Exiting ... "
			exit(1)
	
	def sendCMD(self, data_length, code, data):
		"""Function for sending a command to the board"""   
		checksum = 0
		total_data = ['$', 'M', '<', data_length, code] + data
		for i in struct.pack('<2B%dh' % len(data), *total_data[3:len(total_data)]):
			checksum = checksum ^ ord(i)
		total_data.append(checksum)
		try:
			self.ser.write(struct.pack('<3c2B%dhB' % len(data), *total_data))
		except Exception, error:
			if self.PRINT :
				print "\n\nError in sendCMD."
				print str(error)

	def arm(self):
		"""Function to arm"""
		timer = 0
		start = time.time()
		while timer < 0.5:
			data = [1500,1500,2000,1000]
			self.sendCMD(8,MultiWii.SET_RAW_RC,data)
			time.sleep(0.05)
			timer = timer + (time.time() - start)
			start =  time.time()
	def disarm(self):
		"""Function to disarm"""
		timer = 0
		start = time.time()
		while timer < 0.5:
			data = [1500,1500,1000,1000]
			self.sendCMD(8,MultiWii.SET_RAW_RC,data)
			time.sleep(0.05)
			timer = timer + (time.time() - start)
			start =  time.time()
	
	def getData(self, cmd):
		"""Function to receive a data packet from the board"""
		try:
			start = time.time()
			self.sendCMD(0,cmd,[])
			while True:
				header = self.ser.read()
				if header == '$':
					header = header+self.ser.read(2)
					break
			datalength = struct.unpack('<b', self.ser.read() )[0]
			code = struct.unpack('<b', self.ser.read())
			data = self.ser.read(datalength)
			fmt = '<' + 'h'*(datalength/2)
			data_size = struct.calcsize(fmt)
			try :
				data = data[:data_size]
				temp = struct.unpack(fmt,data)
			except:
				print "Error  in Unpacking \n\t required datalength : {0}\t recv datalength : {3}\t data : {1}\t code : {2}".format(datalength , data , code , len(data) )
				self.ser.flushInput()
				self.ser.flushOutput()		
				return
			self.ser.flushInput()
			self.ser.flushOutput()
			if cmd == MultiWii.RAW_IMU:
				self.raw_imu['acc_x'] = temp[0]
				self.raw_imu['acc_y'] = temp[1]
				self.raw_imu['acc_z'] = temp[2]
				self.raw_imu['gyro_x']  = temp[3]
				self.raw_imu['gyro_y']  = temp[4]
				self.raw_imu['gyro_z']  = temp[5]
			elif cmd == MultiWii.MOTOR:
				self.motor['motor_1']=temp[0]
				self.motor['motor_2']=temp[1]
				self.motor['motor_3']=temp[2]
				self.motor['motor_4']=temp[3]
			elif cmd == MultiWii.RC:
				self.rc['roll']=temp[0]
				self.rc['pitch']=temp[1]
				self.rc['yaw']=temp[2]
				self.rc['throttle']=temp[3]
			elif cmd == MultiWii.RAW_GPS:
				pass
			elif cmd == MultiWii.COMP_GPS :
				pass
			elif cmd == MultiWii.ATTITUDE:
				self.attitude['ang_x'] = temp[0]
				self.attitude['ang_y'] = temp[1]
				self.attitude['heading'] = temp[2]
			elif cmd == MultiWii.ALTITUDE : 
				pass
			elif cmd == MultiWii.PID : 
				pass
			else:
				if self.PRINT : print "Nothing returned from getting " + str(cmd)
		except Exception, error:
			if self.PRINT : print "Error occured in getting data for " + str(cmd)

	def update_all_values(self):
		ans = self.getData(MultiWii.RAW_IMU)
		ans = self.getData(MultiWii.MOTOR)
		ans = self.getData(MultiWii.RC)
#		ans = self.getData(MultiWii.RAW_GPS)
#		ans = self.getData(MultiWii.COMP_GPS)
		ans = self.getData(MultiWii.ALTITUDE)
		ans = self.getData(MultiWii.ATTITUDE)
		ans = self.getData(MultiWii.PID)
		
	def print_data(self):
		z = {}
		z.update(self.raw_imu)
		z.update(self.motor)
		z.update(self.rc)
#		z.update(self.raw_gps)
#		z.update(self.comp_gps)
		z.update(self.attitude)
		z.update(self.altitude)
		z.update(self.pid)
		return z
