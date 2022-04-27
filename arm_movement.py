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
#	if os.name == 'nt':
#		import msvcrt
#		def getch():
#	    		return msvcrt.getch().decode()
#	else:
#		fd = sys.stdin.fileno()
#		old_settings = termios.tcgetattr(fd)
#		def getch():
#	    		try:
#	        		tty.setraw(sys.stdin.fileno())
#	        		ch = sys.stdin.read(1)
#	    		finally:
#	        		termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
#	    		return ch


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
	DXL_MAXIMUM_AMP_VALUE	    = 4000
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
	PGAIN			    = 100
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


	return portHandler, packetHandler, DXL_PITCH_ID, DXL_AMP_ID, ADDR_GOAL_POSITION, ADDR_PRESENT_POSITION, ADDR_TORQUE_ENABLE, TORQUE_DISABLE, DXL_MOVING_STATUS_THRESHOLD;

######################################################################################
# SET GOAL POSITIONS
######################################################################################
def set_positions():
	index = 0
	dxl_goal_position = [1300, 1600, 1800, 2020, 1400, 2023, 1023]
	dxl_volumes = [3700, 3700, 4000, 3900, 3900, 3700, 3000]

	print("Positions set.........", dxl_goal_position)
	print("Volumes set..........", dxl_volumes)

	return index, dxl_goal_position, dxl_volumes


######################################################################################
# MOVE THROUGH POSITIONS
######################################################################################
def move_to(index, dxl_goal_position, dxl_volumes, portHandler, packetHandler, DXL_PITCH_ID, DXL_AMP_ID, ADDR_GOAL_POSITION, ADDR_PRESENT_POSITION, DXL_MOVING_STATUS_THRESHOLD):
	if len(dxl_goal_position) != len(dxl_volumes):
		print("Error: Make sure note and volume arrays are the same length")
		return
	try:
		while 1:
			# Write goal pitch position
			dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_PITCH_ID, ADDR_GOAL_POSITION, dxl_goal_position[index])
			
			if dxl_comm_result != COMM_SUCCESS:
				print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
			elif dxl_error != 0:
				print("%s" % packetHandler.getRxPacketError(dxl_error))

			# Write goal pitch position
                        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_AMP_ID, ADDR_GOAL_POSITION, dxl_volumes[index])

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

				print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL_PITCH_ID, dxl_goal_position[index], dxl_present_position))

				if not abs(dxl_goal_position[index] - dxl_present_position) > DXL_MOVING_STATUS_THRESHOLD:
					break

				dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, DXL_AMP_ID, ADDR_PRESENT_POSITION)

                                if dxl_comm_result != COMM_SUCCESS:
                                        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                                elif dxl_error != 0:
                                        print("%s" % packetHandler.getRxPacketError(dxl_error))

                                print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL_AMP_ID, dxl_volumes[index], dxl_present_position))

                                if not abs(dxl_volumes[index] - dxl_present_position) > DXL_MOVING_STATUS_THRESHOLD:
                                        break

			time.sleep(2) #pause

			# Change goal position
			index = index + 1
			if index == len(dxl_goal_position):
				index = 0
				break


	except KeyboardInterrupt:
		pass

def dynamixel_shutdown(portHandler, packetHandler, DXL_PITCH_ID, DXL_AMP_ID, ADDR_TORQUE_ENABLE, TORQUE_DISABLE):
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

#######################################################################################
# MAIN
#######################################################################################
#if __name__ == "__main__":
	# connect to dynamixels
#	portHandler, packetHandler, DXL_PITCH_ID, DXL_AMP_ID, ADDR_GOAL_POSITION, ADDR_PRESENT_POSITION, ADDR_TORQUE_ENABLE, TORQUE_DISABLE, DXL_MOVING_STATUS_THRESHOLD  = dynamixel_setup()

	# get goal positions
#	index, dxl_goal_position, dxl_volumes = set_positions()

	# wait to proceed
#	while 1:
#		print("Press SPACE to start")
#		if getch() == chr(0x20):
#			break

	# move through positions
#	move_to(index, dxl_goal_position, dxl_volumes, portHandler, packetHandler, DXL_PITCH_ID, DXL_AMP_ID, ADDR_GOAL_POSITION, ADDR_PRESENT_POSITION, DXL_MOVING_STATUS_THRESHOLD)

	# finish
#	print("Shutting down")
#	dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_PITCH_ID, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
#	if dxl_comm_result != COMM_SUCCESS:
#		print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
#	elif dxl_error != 0:
#		print("%s" % packetHandler.getRxPacketError(dxl_error))
#
#	dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_AMP_ID, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
#       if dxl_comm_result != COMM_SUCCESS:
#               print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
#       elif dxl_error != 0:
#               print("%s" % packetHandler.getRxPacketError(dxl_error))
#
#	portHandler.closePort()
