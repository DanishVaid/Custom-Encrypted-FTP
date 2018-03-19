import socket

from Crypto.Cipher import AES

from shared.packets import InitializerPacket, deserialize_packet, deserialize_init_packet
from . import connection_handler

# Handles receiving data stream, packetization, and distributing to respective handler
class MessageQueue(object):

	def __init__(self, incoming_stream):
		self.incoming_stream = incoming_stream

		self.message_queue = []
		self.connection_handlers = []

	# Always open to receive messages until end of session
	def receive_messages(self):
		print("Receiving Messages.")

		in_session = True
		while(in_session):
			self.incoming_stream.settimeout(1)

			try:
				data = self.incoming_stream.recv(4096)
				enc_obj = self.connection_handlers[0].enc_obj
				packet = deserialize_packet(data, enc_obj)

				# Send packet to connection handler
				self.connection_handlers[0].consume_packet(packet)

			except socket.timeout:
				pass
			except closeServer:
				print("Closing server . . .")
				return

	def add_handler(self, connection_handler):
		self.connection_handlers.append(connection_handler)

	# Initial handshake process
	def establish_secure_key(self, outgoing_socket):
		while(True):
			self.incoming_stream.settimeout(1)

			try:
				init_data = self.incoming_stream.recv(4096)
				packet = deserialize_init_packet(init_data, True)
				print(packet)

				client_id = len(self.connection_handlers) + 1
				enc_obj = AES.new(packet.sym_key, AES.MODE_ECB)
				conn_handler = connection_handler.ConnectionHandler(outgoing_socket, enc_obj, client_id)
				self.add_handler(conn_handler)

				ret_pack = InitializerPacket(packet.sym_key, conn_handler.client_id)
				print("RET_PACK IS:", ret_pack)
				outgoing_socket.sendall(ret_pack.serialize(False))
				return
			except socket.timeout:
				pass

class closeServer(Exception):
	pass