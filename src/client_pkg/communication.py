import sys
import socket

from shared import files
from shared import packets
from shared import directory

class Communication(object):

	def __init__(self, incoming_stream, outgoing_socket):
		self.incoming_stream = incoming_stream
		self.outgoing_socket = outgoing_socket

		self.directory = directory.Directory("client")
		self.in_session = True

		self.key = None
		self.client_id = None

	def establish_secure_key(self):
		init_pack = packets.InitializerPacket()
		self.key = init_pack.sym_key
		self.outgoing_socket.sendall(init_pack.serialize(True))
		
		while(True):
			self.incoming_stream.settimeout(1)
			try:
				data = self.incoming_stream.recv(4096)
				packet = packets.deserialize_init_packet(data, False, self.key)

				if packet.sym_key != self.key:
					print("[ERROR] Failed to establish same key")
					sys.exit(1)

				self.client_id = packet.client_id
				return
			except socket.timeout:
				pass

	def take_command(self):
		commands = {
			"exit": self.exit,
			"lls": self.lls,
			"lcd": self.lcd,
			"lpwd": self.lpwd,
			"ls": self.ls,
			"cd": self.cd,
			"pwd": self.pwd,
			"upload": self.upload,
			"download": self.download
		}

		zero_arg_commands = ["exit", "lls", "lpwd", "ls", "pwd"]
		one_arg_commands = ["lcd", "cd", "upload", "download"]
		commands_need_response = ["ls", "cd", "pwd"]

		self.list_commands()
		while self.in_session:
			command, args = self.take_input()

			if command in zero_arg_commands:
				commands[command]()
			elif command in one_arg_commands:
				commands[command](args[0])
			else:
				print("Command not recognized.")

			if command in commands_need_response:
				self.receive_messages()

	def take_input(self):
		console_input = input("\nCommand (enter 'exit' to quit): ")
		console_input = console_input.split()

		if len(console_input) == 0:
			print("No input detected.")
			return

		command = console_input[0]
		args = []

		if len(console_input) > 1:
			args = console_input[1:]

		return command, args

	def list_commands(self):
		print("Commands")
		print("--------")

		print("List Local Current Directory: lls")
		print("Change Local Directory: lcd <directory name>")
		print("Print Local Working Directory: lpwd")

		print("List Remote Current Directory: ls")
		print("Change Remote Directory: cd <directory name>")
		print("Print Remote Working Directory: pwd")

		print("Upload File: upload <filename>")
		print("Download File: download <filename>")

	def exit(self):
		packet = packets.CommandPacket("exit")
		self.outgoing_socket.sendall(packet.serialize())
		if not self.receive_ack('exit'):
			print("[ERROR] Exit ACK not received")
			sys.exit(1)
		self.in_session = False

	def lls(self):
		print(self.directory.get_current_directory_files())

	def lcd(self, directory):
		print(self.directory.set_current_directory(directory))

	def lpwd(self):
		print(self.directory.get_current_directory())

	def ls(self):
		packet = packets.CommandPacket("ls")
		self.outgoing_socket.sendall(packet.serialize())
		print("[REMOTE] Current directory files are:")

	def cd(self, directory):
		packet = packets.CommandPacket('cd ' + directory)
		self.outgoing_socket.sendall(packet.serialize())

	def pwd(self):
		packet = packets.CommandPacket("pwd")
		self.outgoing_socket.sendall(packet.serialize())

	def upload(self, filename):
		packet_size = 4096	# TODO: If we have time, avoid hard coding
		file_uid = 1 # TODO: Set file_uid 
		client_id = 1 # TODO: Set client_id

		filepath = self.directory.get_current_directory() + '/' + filename
		curr_file = files.Files(filepath, 'rb', packet_size - packets.DataPacket._overhead)

		command_packet = packets.CommandPacket("upload")
		self.outgoing_socket.sendall(command_packet.serialize())

		# Receive and ensure its a correct 'ACK' (checking keys)
		if not self.receive_ack('upload'):
			return

		# Build and send 'metadata' packet
		filename = filename.split('.')
		metadata_packet = packets.MetadataPacket(file_uid, filename[0], filename[1], client_id)
		self.outgoing_socket.sendall(metadata_packet.serialize())
		
		curr_pack = None
		seq_num = 0
		while True:
			seq_num += 1
			data = curr_file.read_file_slice()

			if len(data) == 0:
				# Create an 'end' packet to send
				curr_pack = packets.EndOfDataPacket(file_uid)
				self.outgoing_socket.sendall(curr_pack.serialize())
				print('End of data packet Sent')
				self.receive_ack('upload')
				return
			else:
				curr_pack = packets.DataPacket(file_uid, seq_num, data)

			self.outgoing_socket.sendall(curr_pack.serialize())
		curr_file.close()
		print("Successfully uploaded:", filename)

	def download(self, filename):
		# TODO: Figure out protocol
		packet = packets.CommandPacket("download " + filename)
		self.outgoing_socket.sendall(packet.serialize())
		if not self.receive_ack('download'):
			return
		self.receive_download()

	def receive_messages(self):
		response_to_function = {
			"ls": self.print_response,
			"cd": self.print_response,
			"pwd": self.print_response,
		}

		waiting = True
		while(waiting):
			self.incoming_stream.settimeout(1)

			try:
				data = self.incoming_stream.recv(4096)
				# TODO: Decrypt with sym key when we add encyrption
				packet = packets.deserialize_packet(data)

				if packet._type != 'r':
					print("[ERROR] Received following instead of a Response packet:\n\ttype = {}, data = {}".format(packet._type, packet.data))
					sys.exit(1)

				response = packet.data.split(' ')
				response_to_function[response[0]](response[1:])
				break

			except socket.timeout:
				pass


	def print_response(self, content):
		# content = content.split('|')
		content = ' '.join(content)
		print(content)
		
	def receive_download(self):
		# TODO: Incorporate file_uid
		# TODO: Double check correct information
		file_uid, file_name, file_type, client_id = self.receive_metadata()
		new_file_path = self.directory.get_current_directory() + '/' + file_name + '.' + file_type
		new_file = files.Files(new_file_path, 'ab')

		while(True):
			seq_num = 0
			try:
				self.incoming_stream.settimeout(1)
				data = self.incoming_stream.recv(4096)
				# TODO: Decrypt with sym key when we add encryption
				packet = packets.deserialize_packet(data)
				seq_num += 1

				if packet._type == 'e':
					new_file.close()
					return

				if packet._type != 'd':
					print("[ERROR] Received following instead of data/end packet:\n\ttype = {}, data = {}".format(packet._type, packet.data))
					sys.exit(1)
				elif seq_num != packet.seq_num:
					print("[ERROR] Sequence Number does not match:\n\ttype = {}, data = {}".format(packet._type, packet.data))
					sys.exit(1)

				new_file.write_file_by_append(packet.data)
				
			except socket.timeout:
				pass


	def receive_metadata(self):
		while(True):
			try:
				self.incoming_stream.settimeout(1)
				data = self.incoming_stream.recv(4096)
				# TODO: Decrypt with sym key when we add encryption
				packet = packets.deserialize_packet(data)

				if packet._type != 'm':
					print("[ERROR] Received following instead of metadata packet:\n\ttype = {}, data = {}".format(packet._type, packet.data))
					sys.exit(1)

				return packet.file_uid, packet.file_name, packet.file_type, packet.client_id

			except socket.timeout:
				pass

	def receive_ack(self, func):
		while(True):
			self.incoming_stream.settimeout(1)

			try:
				data = self.incoming_stream.recv(4096)
				# TODO: Decrypt with sym key when we add encyrption
				packet = packets.deserialize_packet(data)

				if packet._type != 'r' or packet.data != "{} ACK".format(func):
					print("[ERROR] Received following instead of a correct ACK:\n\ttype = {}, data = {}".format(packet._type, packet.data))
					return False
				
				return True

			except socket.timeout:
				pass