import socket

from shared import files
from shared import packets
from shared import directory

class ConnectionHandler(object):

	def __init__(self, outgoing_socket):
		self.outgoing_socket = outgoing_socket

		self.directory = directory.Directory("server")
		self.in_session = True

		# self.commands = {
		# 	"exit": exit,
		# 	"lls": lls,
		# 	"lcd": lcd,
		# 	"lpwd": lpwd,
		# 	"ls": ls,
		# 	"cd": cd,
		# 	"pwd": pwd,
		# 	"upload": upload,
		# 	"download": download
		# }

	def consume_packet(self, packet):
		if packet._type == 'c':
			# TODO: Figure how to send to close connection message
			self.process_command(packet)
			print("Processed command :", packet.data)
		elif packet._type == 'm':
			self.process_metadata(packet)
		elif packet._type == 'd':
			self.process_data(packet)
		else:
			print("[ERROR] Packet type not detected. Packet dropped.")
			print("[DEBUG] Packet data:", packet.data)

	def process_command(self, packet):
		# TODO: Finish these
		packet_data_list = packet.data.split(' ')
		if packet_data_list[0] == 'ls':
			# TODO: send string to client
			directory_files = self.directory.get_current_directory_files()
			directory_files = ' '.join(directory_files)

			packet = packets.ResponsePacket(directory_files)
			self.outgoing_socket.sendall(packet.serialize())

		elif packet_data_list[0] == 'download':
			print("HERE IT IS:", packet_data_list)
			self.upload(packet_data_list[1])

	def process_metadata(self):
		pass

	def process_data(self):
		pass

	def upload(self, filename):
		packet_size = 4096	# TODO: If we have time, avoid hard coding
		file_uid = 1 # TODO: Set file_uid 
		client_id = 1 # TODO: Set client_id

		ack_packet = packets.ResponsePacket('ACK')
		self.outgoing_socket.sendall(ack_packet.serialize())

		filepath = self.directory.get_current_directory() + '/' + filename
		file = files.Files(filepath, packet_size - packets.DataPacket._overhead)

		# TODO: Get rid of this and solve packets arriving at the same time
		import time
		time.sleep(1)

		# Build and send 'metadata' packet
		filename = filename.split('.')
		metadata_packet = packets.MetadataPacket(file_uid, filename[0], filename[1], client_id)
		self.outgoing_socket.sendall(metadata_packet.serialize())
		
		curr_pack = None
		seq_num = 0
		while True:
			seq_num += 1
			data = file.read_file_slice()

			if len(data) == 0:
				# Create an 'end' packet to send
				curr_pack = packets.EndOfDataPacket(file_uid)
				self.outgoing_socket.sendall(curr_pack.serialize())
				break
			else:
				curr_pack = packets.DataPacket(file_uid, seq_num, data)

			self.outgoing_socket.sendall(curr_pack.serialize())

			# TODO: Get rid of this and solve packets arriving at the same time
			time.sleep(1)

		print("Successfully uploaded:", filename)