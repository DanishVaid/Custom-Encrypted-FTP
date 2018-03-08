import socket
import subprocess

from shared import files
from shared.packets import deserialize_packet

class Communication(object):

	def __init__(self, incoming_stream, outgoing_socket):
		self.incoming_stream = incoming_stream
		self.outgoing_socket = outgoing_socket

	def receive_messages(self):
		print("Receiving Messages.")

		in_session = True
		while(in_session):
			incoming_stream.settimeout(1)

			try:
				data = incoming_stream.recv(4096)
				packet = deserialize_packet(data)
				
				if packet._type == 'c':
					# TODO: Figure how to send to close connection message
					process_command(packet)

				elif packet._type == 'm':
					process_metadata(packet)

				elif packet._type == 'd':
					process_data(packet)

			except socket.timeout:
				pass

	def process_command(self):
		if pack.data == 'ls':
			# TODO: send string to client
			print('\nFiles in current directory:\n', subprocess.getoutput('ls'))

	def process_metadata(self):
		pass

	def process_data(self):
		pass