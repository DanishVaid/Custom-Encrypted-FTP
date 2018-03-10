
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
			"exit": exit,
			"lls": lls,
			"lcd": lcd,
			"lpwd": lpwd,
			"ls": ls,
			"cd": cd,
			"pwd": pwd,
			"upload": upload,
			"download": download
		}

		zero_arg_commands = ["exit", "lls", "lpwd", "ls", "pwd"]
		one_arg_commands = ["lcd", "cd", "upload", "download"]

		while self.in_session:
			command, args = self.take_input()

			if command in zero_arg_commands:
				commands[command]()
			elif command in one_arg_commands:
				commands[command](args[0])
			else:
				print("Command not recognized.")

			if command == "exit":
				in_session = False
				continue

			elif command == "ls":
				packet = packets.CommandPacket("ls")
				self.outgoing_socket.sendall(packet)

			elif command == "cd":
				packet = packets.CommandPacket("cd")
				self.outgoing_socket.sendall(packet)

			elif command == "upload":
				# TODO: move this functionality somewhere else, replace with command packet 'upload'
				# TODO: and/or send metadata

			elif command == "download":
				# TODO: include filename
				file_name = args[0]
				packet = packets.CommandPacket("download")
				self.outgoing_socket.sendall(packet)

			else:
				print("Command not recognized.")

			self.receive_messages()

	def take_input(self):
		self.list_commands()

		console_input = input("Command (enter 'exit' to quit):")
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
		pass

	def lls(self):
		pass

	def lcd(self, directory):
		pass

	def lpwd(self):
		pass

	def ls(self):
		pass

	def cd(self, directory):
		pass

	def pwd(self):
		pass

	def upload(self, filename):
		pass

	def download(self, filename):
		pass

	def receive_messages(self):
		# TODO: Add blocking/timeout
		# TODO: Do function, can take structure from server code
		pass

	# NOTE: This is called after handshake, when ack received from server
	def send_file_data(self):
		pass
		# packet_size = 4096	# TODO: Set in command line, make global

		# file_name = args[0]
		# file_path = self.directory.get_current_directory() + file_name
		# file = files.Files(file_path, packet_size)

		# seek_point = 0
		# while True:
		# 	data = file.read_file(seek_point)

		# 	if len(data) == 0:
		# 		break

		# 	self.outgoing_socket.sendall(data)
		# 	seek_point = seek_point + packet_size

		# print("[DEBUG] Done sending.")