from rtpmidi import RtpMidi
from pymidi import server
from arm_movement import *

portHandler = None
packetHandler = None
DXL_PITCH_ID = None
DXL_AMP_ID = None
ADDR_GOAL_POSITION = None
ADDR_TORQUE_ENABLE = None
TORQUE_DISABLE = None
DXL_MOVING_STATUS_THRESHOLD = None
ADDR_PGAIN = None
ADDR_IGAIN = None
ADDR_DGAIN = None
ignore_noteoff = None

class MyHandler(server.Handler):
    ignore_noteoff = False

    def on_peer_connected(self, peer):
        # Handler for peer connected
        print('Peer connected: {}'.format(peer))

    def on_peer_disconnected(self, peer):
        # Handler for peer disconnected
        print('Peer disconnected: {}'.format(peer))

    def on_midi_commands(self, peer, command_list):
        # Handler for midi msgs
        print(DXL_PITCH_ID)
        print(self.ignore_noteoff)
        for command in command_list:
            if command.command == 'note_on':
                key = command.params.key
                velocity = command.params.velocity
                print('ON:     key {} with velocity {}'.format(key, velocity))
                # EMG midi flags
                if key == "D2": #frown
                    set_legato(portHandler, packetHandler, DXL_PITCH_ID, ADDR_PGAIN)
                    self.ignore_noteoff = True
                    print(ignore_noteoff)
                elif key == "D3": #smile
                    set_staccato(portHandler, packetHandler, DXL_PITCH_ID, ADDR_PGAIN)
                    self.ignore_noteoff = False
                else:
                     move_to(portHandler, packetHandler, DXL_PITCH_ID, DXL_AMP_ID, ADDR_GOAL_POSITION, ADDR_PRESENT_POSITION, DXL_MOVING_STATUS_THRESHOLD, key, velocity)

            elif command.command == 'note_off' and self.ignore_noteoff == False:
                key = command.params.key
                velocity = 0
                print('OFF:     key {} with velocity {}'.format(key, velocity))
                move_to(portHandler, packetHandler, DXL_PITCH_ID, DXL_AMP_ID, ADDR_GOAL_POSITION, ADDR_PRESENT_POSITION, DXL_MOVING_STATUS_THRESHOLD, key, velocity)

            else:
                pass

if __name__ == "__main__":
    # Connect to dynamixels
    portHandler, packetHandler, DXL_PITCH_ID, DXL_AMP_ID, ADDR_GOAL_POSITION, ADDR_PRESENT_POSITION, ADDR_TORQUE_ENABLE, TORQUE_DISABLE, DXL_MOVING_STATUS_THRESHOLD, ADDR_PGAIN, ADDR_IGAIN, ADDR_DGAIN  = dynamixel_setup()


    # Start listening for midi
    ROBOT = "ThereminBot"
    PORT = 5004
    rtp_midi = RtpMidi(ROBOT, MyHandler(), PORT)
    rtp_midi.run()

    # Finish
    dynamixel_shutdown(portHandler, packetHandler, DXL_PITCH_ID, DXL_AMP_ID, ADDR_TORQUE_ENABLE, TORQUE_DISABLE, ADDR_GOAL_POSITION, ADDR_PRESENT_POSITION, DXL_MOVING_STATUS_THRESHOLD)
