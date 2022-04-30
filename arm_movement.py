import time
import os
import logging
import threading
from dynamixel_sdk import *
import sys, tty, termios

def getch():
	fd = sys.stdin.fileno()
	old_settings = termios.tcgetattr(fd)
	try:
		tty.setraw(sys.stdin.fileno())
		ch = sys.stdin.read(1)
	finally:
		termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
	return ch

def dynamixel_setup():
##############################################################################
# DYNAMIXEL SETUP
##############################################################################

	#********* DYNAMIXEL Model definition *********
	#***** (Use only one definition at a time) *****
	MY_DXL = 'X_SERIES'       # X330 (5.0 V recommended), X430, X540, 2X430
	# MY_DXL = 'MX_SERIES'    # MX series with 2.0 firmware update.
	# MY_DXL = 'PRO_SERIES'   # H54, H42, M54, M42, L54, L42
	# MY_DXL = 'PRO_A_SERIES' # PRO series with (A) firmware update.
	# MY_DXL = 'P_SERIES'     # PH54, PH42, PM54
	# MY_DXL = 'XL320'        # [WARNING] Operating Voltage : 7.4V


	# Control table address
	ADDR_TORQUE_ENABLE          = 64
	ADDR_GOAL_POSITION          = 116
	ADDR_PRESENT_POSITION       = 132
	DXL_MINIMUM_PITCH_VALUE     = 0         # Refer to the Minimum Position Limit of product eManual
	DXL_MAXIMUM_PITCH_VALUE     = 2020      # Refer to the Maximum Position Limit of product eManual
	DXL_MINIMUM_AMP_VALUE	    = 3700
	DXL_MAXIMUM_AMP_VALUE	    = 4095
	ADDR_MIN_POS		    = 52
	ADDR_MAX_POS		    = 48
	BAUDRATE                    = 57600
	ADDR_PGAIN		    = 84
	ADDR_IGAIN		    = 82
	ADDR_DGAIN		    = 80

	# DYNAMIXEL Protocol Version (1.0 / 2.0)
	# https://emanual.robotis.com/docs/en/dxl/protocol2/

	PROTOCOL_VERSION            = 2.0

	# Factory default ID of all DYNAMIXEL is 1
	DXL_PITCH_ID                      = 1
	DXL_AMP_ID                        = 2

	# Use the actual port assigned to the U2D2.
	# ex) Windows: "COM*", Linux: "/dev/ttyUSB*", Mac: "/dev/tty.usbserial-*"
	DEVICENAME                  = '/dev/ttyUSB0'

	TORQUE_ENABLE               = 1     # Value for enabling the torque
	TORQUE_DISABLE              = 0     # Value for disabling the torque
	DXL_MOVING_STATUS_THRESHOLD = 20    # Dynamixel moving status threshold

	# Initial stable PID tuning
	PGAIN			    = 1000
	IGAIN			    = 1
	DGAIN			    = 500

	# Initialize PortHandler instance
	# Set the port path
	# Get methods and members of PortHandlerLinux or PortHandlerWindows
	portHandler = PortHandler(DEVICENAME)

	# Initialize PacketHandler instance
	# Set the protocol version
	# Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
	packetHandler = PacketHandler(PROTOCOL_VERSION)

	# Open port
	if portHandler.openPort():
		print("Succeeded to open the port")
	else:
		print("Failed to open the port")
		print("Press any key to terminate...")
		getch()
		quit()


	# Set port baudrate
	if portHandler.setBaudRate(BAUDRATE):
		print("Succeeded to change the baudrate")
	else:
		print("Failed to change the baudrate")
		print("Press any key to terminate...")
		getch()
		quit()

	# Set min/max position limits
	dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_PITCH_ID, ADDR_MIN_POS, DXL_MINIMUM_PITCH_VALUE)
	if dxl_comm_result != COMM_SUCCESS:
		print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
	elif dxl_error != 0:
		print("%s" % packetHandler.getRxPacketError(dxl_error))

	dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_PITCH_ID, ADDR_MAX_POS, DXL_MAXIMUM_PITCH_VALUE)
	if dxl_comm_result != COMM_SUCCESS:
		print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
	elif dxl_error != 0:
		print("%s" % packetHandler.getRxPacketError(dxl_error))

	dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_AMP_ID, ADDR_MIN_POS, DXL_MINIMUM_AMP_VALUE)
	if dxl_comm_result != COMM_SUCCESS:
		print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
	elif dxl_error != 0:
		print("%s" % packetHandler.getRxPacketError(dxl_error))

	dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_AMP_ID, ADDR_MAX_POS, DXL_MAXIMUM_AMP_VALUE)
	if dxl_comm_result != COMM_SUCCESS:
		print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
	elif dxl_error != 0:
		print("%s" % packetHandler.getRxPacketError(dxl_error))

	else:
		print("Dynamixel position limits successfully set")


	# Set PID gains
	dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, DXL_PITCH_ID, ADDR_PGAIN, PGAIN)
	if dxl_comm_result != COMM_SUCCESS:
		print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
	elif dxl_error != 0:
		print("%s" % packetHandler.getRxPacketError(dxl_error))

	dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, DXL_PITCH_ID, ADDR_IGAIN, IGAIN)
	if dxl_comm_result != COMM_SUCCESS:
		print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
	elif dxl_error != 0:
		print("%s" % packetHandler.getRxPacketError(dxl_error))

	dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, DXL_PITCH_ID, ADDR_DGAIN, DGAIN)
	if dxl_comm_result != COMM_SUCCESS:
		print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
	elif dxl_error != 0:
		print("%s" % packetHandler.getRxPacketError(dxl_error))
	else:
    		print("Dynamixel PID successfully set")

	# Enable Dynamixel Torque
	dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_PITCH_ID, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
	if dxl_comm_result != COMM_SUCCESS:
		print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
	elif dxl_error != 0:
		print("%s" % packetHandler.getRxPacketError(dxl_error))
	else:
		print("Pitch Dynamixel has been successfully connected")

	dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_AMP_ID, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
	if dxl_comm_result != COMM_SUCCESS:
		print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
	elif dxl_error != 0:
		print("%s" % packetHandler.getRxPacketError(dxl_error))
	else:
		print("Amplitude Dynamixel has been successfully connected")


	return portHandler, packetHandler, DXL_PITCH_ID, DXL_AMP_ID, ADDR_GOAL_POSITION, ADDR_PRESENT_POSITION, ADDR_TORQUE_ENABLE, TORQUE_DISABLE, DXL_MOVING_STATUS_THRESHOLD, ADDR_PGAIN, ADDR_IGAIN, ADDR_DGAIN



######################################################################################
# MOVE THROUGH POSITIONS
######################################################################################
def move_to(portHandler, packetHandler, DXL_PITCH_ID, DXL_AMP_ID, ADDR_GOAL_POSITION, ADDR_PRESENT_POSITION, DXL_MOVING_STATUS_THRESHOLD, key_value, vel_value):
	try:


		note_dict = 	{"E5": 1662,
				"F5": 1823,
				"Fs5": 1879,
				"G5": 1928,
				"Gs5": 1956,
				"A5": 1971,
				"As5": 1984,
				"B5": 1996,
				"C6": 2006,
				"Cs6": 2015}

		# Write goal pitch position
		dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_PITCH_ID, ADDR_GOAL_POSITION, note_dict[key_value])

		if dxl_comm_result != COMM_SUCCESS:
			print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
		elif dxl_error != 0:
			print("%s" % packetHandler.getRxPacketError(dxl_error))

		amp_pos = round(4095.0 - (3.11*vel_value))

		# Write goal amplitude position
		dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_AMP_ID, ADDR_GOAL_POSITION, amp_pos)

		if dxl_comm_result != COMM_SUCCESS:
			print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
		elif dxl_error != 0:
			print("%s" % packetHandler.getRxPacketError(dxl_error))

		while 1:
			# Read present position
			dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, DXL_PITCH_ID, ADDR_PRESENT_POSITION)

			if dxl_comm_result != COMM_SUCCESS:
				print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
			elif dxl_error != 0:
				print("%s" % packetHandler.getRxPacketError(dxl_error))

			#print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL_PITCH_ID, note_dict[key_value], dxl_present_position))

			if not abs(note_dict[key_value] - dxl_present_position) > DXL_MOVING_STATUS_THRESHOLD:
				break

			dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, DXL_AMP_ID, ADDR_PRESENT_POSITION)

			if dxl_comm_result != COMM_SUCCESS:
				print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
			elif dxl_error != 0:
				print("%s" % packetHandler.getRxPacketError(dxl_error))

			#print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL_AMP_ID, amp_pos, dxl_present_position))

			if not abs(amp_pos - dxl_present_position) > DXL_MOVING_STATUS_THRESHOLD:
				break


	except KeyboardInterrupt:
		pass

###################################################################################################
# DYNAMIXEL SHUTDOWN SEQUENCE
####################################################################################################
def dynamixel_shutdown(portHandler, packetHandler, DXL_PITCH_ID, DXL_AMP_ID, ADDR_TORQUE_ENABLE, TORQUE_DISABLE, ADDR_GOAL_POSITION, ADDR_PRESENT_POSITION, DXL_MOVING_STATUS_THRESHOLD):
	move_to(portHandler, packetHandler, DXL_PITCH_ID, DXL_AMP_ID, ADDR_GOAL_POSITION, ADDR_PRESENT_POSITION, DXL_MOVING_STATUS_THRESHOLD, "C6", 127)

	time.sleep(1)

	print("Shutting down")
	dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_PITCH_ID, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
	if dxl_comm_result != COMM_SUCCESS:
		print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
	elif dxl_error != 0:
		print("%s" % packetHandler.getRxPacketError(dxl_error))

	dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_AMP_ID, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
	if dxl_comm_result != COMM_SUCCESS:
		print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
	elif dxl_error != 0:
		print("%s" % packetHandler.getRxPacketError(dxl_error))

	portHandler.closePort()



def set_staccato(portHandler, packetHandler, DXL_PITCH_ID, ADDR_PGAIN):
	print("staccato")
	dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, DXL_PITCH_ID, ADDR_PGAIN, 1000)
	if dxl_comm_result != COMM_SUCCESS:
		print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
	elif dxl_error != 0:
		print("%s" % packetHandler.getRxPacketError(dxl_error))

def set_legato(portHandler, packetHandler, DXL_PITCH_ID, ADDR_PGAIN):
	print("legato")
	dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, DXL_PITCH_ID, ADDR_PGAIN, 500)
	if dxl_comm_result != COMM_SUCCESS:
		print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
	elif dxl_error != 0:
		print("%s" % packetHandler.getRxPacketError(dxl_error))

