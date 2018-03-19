import socket
import sys
import time

from shared import files
from shared import packets
from shared import directory

class ConnectionHandler(object):

	def __init__(self, outgoing_socket, enc_obj, client_id):
		self.outgoing_socket = outgoing_socket

		self.directory = directory.Directory("server")
		self.in_session = True

		self.file_obj = None
		self.file_uid = None
		
		self.enc_obj = enc_obj
		self.client_id = client_id
		self.file_uid = 0

	def consume_packet(self, packet):
		if packet._type == 'c':
			self.process_command(packet)
			print("Processed command :", packet.data)
		elif packet._type == 'm':
			self.process_metadata(packet) # Save file information into object
		elif packet._type == 'd':
			self.download(packet)
		elif packet._type == 'e':
			self.process_end_of_data(packet)
		else:
			print("[ERROR] Packet type not detected. Packet dropped.")
			print("[DEBUG] Packet data:", packet.data)

	def process_command(self, packet):
		packet_data_list = packet.data.split(' ')
		if packet_data_list[0] == 'ls':
			directory_files = self.directory.get_current_directory_files()
			res = 'ls [REMOTE] Current directory files are:\n ' + ' '.join(directory_files)

			packet = packets.ResponsePacket(res)
			self.outgoing_socket.sendall(packet.serialize(self.enc_obj))

		elif packet_data_list[0] == 'cd':
			print('[DEBUG] Changing directory to:', packet_data_list[1])
			self.directory.set_current_directory(packet_data_list[1])

			res = 'cd [REMOTE] CWD: ' + self.directory.get_current_directory()
			packet = packets.ResponsePacket(res)
			self.outgoing_socket.sendall(packet.serialize(self.enc_obj))
		
		elif packet_data_list[0] == 'pwd':
			direc = self.directory.get_current_directory()

			packet = packets.ResponsePacket('pwd [REMOTE] CWD: ' + direc)
			self.outgoing_socket.sendall(packet.serialize(self.enc_obj))

		elif packet_data_list[0] == 'download':
			self.upload(packet_data_list[1])

		elif packet_data_list[0] == 'upload':
			ack_packet = packets.ResponsePacket('upload ACK')
			self.outgoing_socket.sendall(ack_packet.serialize(self.enc_obj))

		elif packet_data_list[0] == 'exit':
			from server_pkg.message_queue import closeServer
			ack_packet = packets.ResponsePacket('exit ACK')
			self.outgoing_socket.sendall(ack_packet.serialize(self.enc_obj))
			print("--- EXIT REVEICED ---")
			raise closeServer()

	def process_metadata(self, packet):
		file_path = self.directory.get_current_directory() + '/' + packet.file_name + '.' + packet.file_type
		self.file_obj = files.Files(file_path, 'ab')
		self.file_uid = packet.file_uid
		self.client_id = packet.client_id

	def process_end_of_data(self, packet):
		self.file_obj.close()
		self.file_obj = None
		self.file_uid = None
		self.client_id = None
		ack_packet = packets.ResponsePacket('upload ACK')
		self.outgoing_socket.sendall(ack_packet.serialize(self.enc_obj))

	def upload(self, filename):
		packet_size = 4095
		self.file_uid += 1

		ack_packet = packets.ResponsePacket('download ACK')
		self.outgoing_socket.sendall(ack_packet.serialize(self.enc_obj))

		filepath = self.directory.get_current_directory() + '/' + filename
		curr_file = files.Files(filepath, 'rb', packet_size - packets.DataPacket._overhead)

		# Network delay
		time.sleep(0.001)

		# Build and send 'metadata' packet
		filename = filename.split('.')
		metadata_packet = packets.MetadataPacket(self.file_uid, filename[0], filename[1], self.client_id)
		self.outgoing_socket.sendall(metadata_packet.serialize(self.enc_obj))
		
		curr_pack = None
		seq_num = 0
		while True:
			seq_num += 1
			data = curr_file.read_file_slice()

			if len(data) == 0:
				# Create an 'end' packet to send
				curr_pack = packets.EndOfDataPacket(self.file_uid)
				self.outgoing_socket.sendall(curr_pack.serialize(self.enc_obj))
				break
			else:
				curr_pack = packets.DataPacket(self.file_uid, seq_num, data)

			# print("SENDING PACK", curr_pack)
			self.outgoing_socket.sendall(curr_pack.serialize(self.enc_obj))

			# Sleeps are in there to simulate network delay
			time.sleep(0.001)
		curr_file.close()
		print("Successfully uploaded:", filename)

	def download(self, packet):
		if packet.file_uid != self.file_uid:
			print("[ERROR] File uid is not matching. Exiting...")
			from server_pkg.message_queue import closeServer
			raise closeServer

		self.file_obj.write_file_by_append(packet.data)