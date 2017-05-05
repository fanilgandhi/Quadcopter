import multi , time
import json , subprocess , select 

filename = "/home/pi/message.txt"

border_values = {
			'throttle' : [1150 , 1850 ],
			'roll'	   : [1000 , 2000 ],
			'pitch'	   : [1000 , 2000 ],
			'yaw'	   : [1000 , 2000 ],
		}

if __name__ == '__main__':
	try :
		open(filename , "w+").close()
		fp = subprocess.Popen(["tail" , "-F" , filename] , stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		new_data = select.poll()
		new_data.register(fp.stdout)
	except:
		print "Error in basic setup"
		exit(0)

	board = multi.Multiwii("/dev/ttyUSB0")
	board.PRINT = True


	while True:
		raw_commands = []
		got_new_data = False
		while new_data.poll(1) : 
			line = fp.stdout.readline().strip().replace("\n" , "")
			if line[0] == '{' : raw_commands.append(line)


		if ( raw_commands != [] ):
			temp_rc = {"roll" : board.roll , "pitch" : board.pitch , "yaw" : board.yaw , "throttle" : board.throttle}
			for each_new_command in raw_commands :
				try : 
					useful_data = json.loads(line) 
					for key in useful_data:
						key = str(key)
						if (key in temp_rc) :
							value = float(useful_data[key])
							if ( border_values[key][0] <= (temp_rc[key] + value) <= border_values[key][1] ) : 
								temp_rc[key] += value
								got_new_data = True
						elif (key == "arm") and (board.ARM_FLAG == 0 ): 
							board.ARM_FLAG = 1
						elif (key == "disarm") and (board.ARM_FLAG == 0 ): 
							board.ARM_FLAG = -1
				except:
					print "fake value " + str(useful_data) 
					
			if got_new_data :
				print "Successful"
				board.buffer.append([temp_rc["roll"] , temp_rc["pitch"] , temp_rc["yaw"] , temp_rc["throttle"] ])
				print temp_rc

'''
## ARM - DISARM function 
while True :
	time.sleep(3)
	board.ARM_FLAG = 1
	time.sleep(3)
	board.ARM_FLAG = -1
'''

