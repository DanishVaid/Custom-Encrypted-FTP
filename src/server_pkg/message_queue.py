import socket

from shared.packets import InitializerPacket, deserialize_packet, deserialize_init_packet
from . import connection_handler

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

	def establish_secure_key(self, outgoing_socket):
		while(True):
			self.incoming_stream.settimeout(1)

			try:
				init_data = self.incoming_stream.recv(4096)
				packet = deserialize_init_packet(init_data, True)
				print(packet)

				client_id = len(self.connection_handlers)
				conn_handler = connection_handler.ConnectionHandler(outgoing_socket, packet.sym_key, client_id)
				self.add_handler(conn_handler)

				ret_pack = InitializerPacket(conn_handler.key, conn_handler.client_id)
				outgoing_socket.sendall(ret_pack.serialize(False))
				return
			except socket.timeout:
				pass
