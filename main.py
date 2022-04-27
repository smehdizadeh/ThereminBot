from rtpmidi import RtpMidi
from pymidi import server

class MyHandler(server.Handler):
    def on_peer_connected(self, peer):
        # Handler for peer connected
        print('Peer connected: {}'.format(peer))

    def on_peer_disconnected(self, peer):
        # Handler for peer disconnected
        print('Peer disconnected: {}'.format(peer))

    def on_midi_commands(self, peer, command_list):
        # Handler for midi msgs
        for command in command_list:
            if command.command == 'note_on':
                key = command.params.key
                velocity = command.params.velocity
                print('key {} with velocity {}'.format(key, velocity))



if __name__ == "__main__":
    ROBOT = "Your Robot"
    PORT = 5004
    rtp_midi = RtpMidi(ROBOT, MyHandler(), PORT)
    rtp_midi.run()
