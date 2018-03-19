import sys
import socket
import time

from Crypto.Cipher import AES

from shared import files
from shared import packets
from shared import directory

class Communication(object):

	def __init__(self, incoming_stream, outgoing_socket):
		self.incoming_stream = incoming_stream		# Used to receive messages
		self.outgoing_socket = outgoing_socket		# Used to send messages

		self.directory = directory.Directory("client")	# Used to navigate through files
		self.in_session = True

		self.enc_obj = None								# Used for encryption
		self.client_id = None
		self.file_uid = 0

	# Handshake process to establish symmetric key and client ID
	def establish_secure_key(self):
		init_pack = packets.InitializerPacket()
		self.outgoing_socket.sendall(init_pack.serialize(True))
		
		while(True):
			self.incoming_stream.settimeout(1)
			try:
				data = self.incoming_stream.recv(4096)
				packet = packets.deserialize_init_packet(data, False, init_pack.sym_key)

				if packet.sym_key != init_pack.sym_key:
					print("[ERROR] Failed to establish same key")
					sys.exit(1)

				self.enc_obj = AES.new(init_pack.sym_key, AES.MODE_ECB)
				self.client_id = packet.client_id
				return
			except socket.timeout:
				pass

	# Start taking in commands from the user in the command line
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

			# Some commands expect responses from the server
			if command in commands_need_response:
				self.receive_messages()

	# Grab user input from the command line
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

	# Show user the list of possible commands
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

	# Ends session on the client side and also tells server to close respective connection
	def exit(self):
		packet = packets.CommandPacket("exit")
		self.outgoing_socket.sendall(packet.serialize(self.enc_obj))
		if not self.receive_ack('exit'):
			print("[ERROR] Exit ACK not received")
			sys.exit(1)
		self.in_session = False

	# 'ls' on local directory
	def lls(self):
		files = ' '.join(self.directory.get_current_directory_files())
		print("[CLIENT] Current working directory files:\n", files)

	# 'cd' on local directory
	def lcd(self, directory):
		cwd = self.directory.set_current_directory(directory)
		print("[CLIENT] CWD now is:", cwd)

	# 'pwd' on local directory
	def lpwd(self):
		cwd = self.directory.get_current_directory()
		print("[CLIENT] CWD is:", cwd)

	# 'ls' on remote directory
	def ls(self):
		packet = packets.CommandPacket("ls")
		self.outgoing_socket.sendall(packet.serialize(self.enc_obj))

	# 'cd' on remote directory
	def cd(self, directory):
		packet = packets.CommandPacket('cd ' + directory)
		self.outgoing_socket.sendall(packet.serialize(self.enc_obj))

	# 'pwd' on remote directory
	def pwd(self):
		packet = packets.CommandPacket("pwd")
		self.outgoing_socket.sendall(packet.serialize(self.enc_obj))

	# Upload specified file
	def upload(self, filename):
		packet_size = 4095
		self.file_uid += 1

		# Prepare filepath and object for sending data
		filepath = self.directory.get_current_directory() + '/' + filename
		curr_file = files.Files(filepath, 'rb', packet_size - packets.DataPacket._overhead)

		# Simulate network delay
		time.sleep(0.001)

		# Tell server that the client wants to upload a file
		command_packet = packets.CommandPacket("upload")
		self.outgoing_socket.sendall(command_packet.serialize(self.enc_obj))

		# Receive and ensure its a correct 'ACK' (checking keys)
		if not self.receive_ack('upload'):
			return

		# Build and send 'metadata' packet
		filename = filename.split('.')
		metadata_packet = packets.MetadataPacket(self.file_uid, filename[0], filename[1], self.client_id)
		self.outgoing_socket.sendall(metadata_packet.serialize(self.enc_obj))
		
		# Start sending to the server the contents of the file in chunks
		curr_pack = None
		seq_num = 0
		while True:
			seq_num += 1
			data = curr_file.read_file_slice()

			if len(data) == 0:
				# Create an 'end' packet to send
				curr_pack = packets.EndOfDataPacket(self.file_uid)
				self.outgoing_socket.sendall(curr_pack.serialize(self.enc_obj))
				print('End of data packet Sent')
				self.receive_ack('upload')
				return
			else:
				curr_pack = packets.DataPacket(self.file_uid, seq_num, data)

			# print("SENDING:", curr_pack)
			# print("LENGTH IS:", len(curr_pack.serialize(self.enc_obj)))
			self.outgoing_socket.sendall(curr_pack.serialize(self.enc_obj))

			# Simulate network delay
			time.sleep(0.001)
		curr_file.close()
		print("Successfully uploaded:", filename)

	# Download specified file
	def download(self, filename):
		# Tell server that the client wants to download a file
		packet = packets.CommandPacket("download " + filename)
		self.outgoing_socket.sendall(packet.serialize(self.enc_obj))
		if not self.receive_ack('download'):
			return
		self.receive_download()

	# Start receiving responses from the server sequentially
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
				packet = packets.deserialize_packet(data, self.enc_obj)

				if packet._type != 'r':
					print("[ERROR] Received following instead of a Response packet:\n\ttype = {}, data = {}".format(packet._type, packet.data))
					sys.exit(1)

				response = packet.data.split(' ')
				response_to_function[response[0]](response[1:])
				break

			except socket.timeout:
				pass

	# Print response to command from the server
	def print_response(self, content):
		# content = content.split('|')
		content = ' '.join(content)
		print(content)
	
	# Start receiving file information
	def receive_download(self):
		# Set file metadata
		file_uid, file_name, file_type, client_id = self.receive_metadata()

		if self.client_id != client_id:
			print("[ERROR] Incorrect client_id. Exiting...")
			sys.exit(1)

		self.file_uid = file_uid

		new_file_path = self.directory.get_current_directory() + '/' + file_name + '.' + file_type
		new_file = files.Files(new_file_path, 'ab')

		seq_num = 0
		while(True):
			try:
				self.incoming_stream.settimeout(1)
				data = self.incoming_stream.recv(4096)
				packet = packets.deserialize_packet(data, self.enc_obj)
				seq_num += 1

				if packet.file_uid != self.file_uid:
					print("[ERROR] Packet dumped, incorrect file uid. Exiting...")
					sys.exit(1)

				if packet._type == 'e':
					new_file.close()
					return

				if packet._type != 'd':
					print("[ERROR] Received following instead of data/end packet:\n\ttype = {}, data = {}".format(packet._type, packet.data))
					sys.exit(1)
				elif seq_num != packet.seq_num:
					print("[ERROR] Sequence Number does not match (Client at:", seq_num, ")\nPacket:", packet)
					sys.exit(1)

				new_file.write_file_by_append(packet.data)
				
			except socket.timeout:
				pass

	# Expect a metadata packet
	def receive_metadata(self):
		while(True):
			try:
				self.incoming_stream.settimeout(1)
				data = self.incoming_stream.recv(4096)
				packet = packets.deserialize_packet(data, self.enc_obj)

				if packet._type != 'm':
					print("[ERROR] Received following instead of metadata packet:\n\ttype = {}, data = {}".format(packet._type, packet.data))
					sys.exit(1)

				return packet.file_uid, packet.file_name, packet.file_type, packet.client_id

			except socket.timeout:
				pass

	# Expect an ACK
	def receive_ack(self, func):
		while(True):
			self.incoming_stream.settimeout(1)

			try:
				data = self.incoming_stream.recv(4096)
				packet = packets.deserialize_packet(data, self.enc_obj)

				if packet._type != 'r' or packet.data != "{} ACK".format(func):
					print("[ERROR] Received following instead of a correct ACK:\n\ttype = {}, data = {}".format(packet._type, packet.data))
					return False
				
				return True

			except socket.timeout:
				pass