import socket
from server_pkg.process_command import process_command
from shared import files
from shared.packets import deserialize_packet

def receive_message(incoming_stream):
	print("Receiving Messages.")

	in_session = True
	while(in_session):
		incoming_stream.settimeout(1)

		try:
			msg = incoming_stream.recv(4096)
			pack = deserialize_packet(msg)
			
			if pack._type == 'c':
				process_command(pack)

		except socket.timeout:
			pass