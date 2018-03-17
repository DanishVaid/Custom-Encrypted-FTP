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
			self.incoming_stream.settimeout(1)

			try:
				data = self.incoming_stream.recv(4096)
				print(data)
				packet = deserialize_packet(data)

				# TODO: Current hardcoded for one connection.
				self.connection_handlers[0].consume_packet(packet)

				# TODO: Figure out how to safely close server.

			except socket.timeout:
				pass

	def add_handler(self, connection_handler):
		self.connection_handlers.append(connection_handler)