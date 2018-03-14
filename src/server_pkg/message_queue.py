import socket

from shared.packets import deserialize_packet

class MessageQueue(object):

	def __init__(self, incoming_stream):
		self.incoming_stream = incoming_stream

		self.message_queue = []
		self.connection_handlers = []

	def receive_messages(self):
		print("Receiving Messages.")

		in_session = True
		while(in_session):
			incoming_stream.settimeout(1)

			try:
				data = incoming_stream.recv(4096)
				packet = deserialize_packet(data)

				# TODO: Figure out how to safely close server.

			except socket.timeout:
				pass