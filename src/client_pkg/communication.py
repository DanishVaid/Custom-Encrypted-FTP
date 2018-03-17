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
		commands_need_response = ["ls", "cd", "pwd", "upload"]

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
			elif command == 'download':
				self.receive_download()

	def take_input(self):
		# self.list_commands()

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
		self.in_session = False
		print("Exiting session.")

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
		packet = packets.CommandPacket("cd")
		self.outgoing_socket.sendall(packet.serialize())

	def pwd(self):
		packet = packets.CommandPacket("pwd")
		self.outgoing_socket.sendall(packet.serialize())

	def upload(self, filename):
		packet_size = 4096	# TODO: If we have time, avoid hard coding
		file_uid = 1 # TODO: Set file_uid 
		client_id = 1 # TODO: Set client_id

		filepath = self.directory.get_current_directory() + filename
		file = files.Files(filepath, packet_size - packets.DataPacket._overhead)

		command_packet = packets.CommandPacket("upload")
		self.outgoing_socket.sendall(command_packet.serialize())

		# Receive and ensure its a correct 'ACK'
		self.receive_ack()

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
			else:
				curr_pack = packets.DataPacket(file_uid, seq_num, data)

			self.outgoing_socket.sendall(curr_pack.serialize())

		print("Successfully uploaded:", filename)

	def download(self, filename):
		# TODO: Figure out protocol
		packet = packets.CommandPacket("download " + filename)
		self.outgoing_socket.sendall(packet.serialize())

	def receive_messages(self):
		waiting = True
		while(waiting):
			self.incoming_stream.settimeout(1)

			try:
				data = self.incoming_stream.recv(4096)
				# TODO: Decrypt with sym key when we add encyrption
				packet = packets.deserialize_packet(data)

				if packet._type != 'r':
					print("(ERROR) Received following instead of a correct ACK:\n\ttype = {}, data = {}".format(packet._type, packet.data))
					sys.exit(1)
				
				# TODO: Do we want to print the response only?
				print(packet.data)
				break

			except socket.timeout:
				pass
		
	def receive_download(self):
		# TODO: Incorporate file_uid
		self.receive_ack()
		waiting = True
		while(waiting):
			self.incoming_stream.settimeout(1)

			try:
				data = self.incoming_stream.recv(4096)
				# TODO: Decrypt with sym key when we add encyrption
				packet = packets.deserialize_packet(data)

				if packet._type != 'm':
					print("(ERROR) Received following instead of metadata:\n\ttype = {}, data = {}".format(packet._type, packet.data))
					sys.exit(1)

				new_file = packet.file_name + '.' + packet.file_type
				with open(new_file, 'wb') as f:
					seq_num = 0
					while packet._type != 'e':
						try:
							self.incoming_stream.settimeout(1)
							data = self.incoming_stream.recv(4096)
							# TODO: Decrypt with sym key when we add encyrption
							packet = packets.deserialize_packet(data)
							seq_num += 1

							if packet._type == 'e':
								return

							if packet._type != 'd':
								print("(ERROR) Received following instead of data/end packet:\n\ttype = {}, data = {}".format(packet._type, packet.data))
								sys.exit(1)
							elif seq_num != packet.seq_num:
								print("(ERROR) Sequence Number does not match:\n\ttype = {}, data = {}".format(packet._type, packet.data))
								sys.exit(1)

							print("PACKET DATA RECEIVED IS:")
							print(packet.data)
							f.write(packet.data)
							
						except socket.timeout:
							pass
				break

			except socket.timeout:
				pass

	def receive_ack(self):
		waiting = True
		while(waiting):
			self.incoming_stream.settimeout(1)

			try:
				data = self.incoming_stream.recv(4096)
				# TODO: Decrypt with sym key when we add encyrption
				packet = packets.deserialize_packet(data)

				if packet._type != 'r' or packet.data != 'ACK':
					print("(ERROR) Received following instead of a correct ACK:\n\ttype = {}, data = {}".format(packet._type, packet.data))
					sys.exit(1)
				break

			except socket.timeout:
				pass