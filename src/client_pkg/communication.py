from shared import files
from shared import packets
from shared import directory

class Communication(object):

	def __init__(self, incoming_stream, outgoing_socket):
		self.incoming_stream = incoming_stream
		self.outgoing_socket = outgoing_socket

		self.directory = directory.Directory("client")t
		self.in_session = True

	def take_command(self):
		commands = {
			"exit": exit,
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
		commands_need_response = ["ls", "cd", "pwd", "upload", "download"]

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
		packet = packets.CommandPacket("exit")
		self.outgoing_socket.sendall(packet)
		self.in_session = False

	def lls(self):
		print(self.directory.get_current_directory_files())

	def lcd(self, directory):
		print(self.directory.set_current_directory(directory))

	def lpwd(self):
		print(self.directory.get_current_directory())

	def ls(self):
		packet = packets.CommandPacket("ls")
		self.outgoing_socket.sendall(packet)

	def cd(self, directory):
		packet = packets.CommandPacket("cd")
		self.outgoing_socket.sendall(packet)

	def pwd(self):
		packet = packets.CommandPacket("pwd")
		self.outgoing_socket.sendall(packet)

	def upload(self, filename):
		packet_size = 4096	# TODO: Set in command line, make global

		filepath = self.directory.get_current_directory() + filename
		file = files.Files(filepath, packet_size)

		# TODO: send metadata
		while True:
			data = file.read_file_slice()

			if len(data) == 0:
				break

			self.outgoing_socket.sendall(data)

		print("[DEBUG] Done sending.")

	def download(self, filename):
		packet = packets.CommandPacket("download_" + filename)
		self.outgoing_socket.sendall(packet)

	def receive_messages(self):
		# TODO: Add blocking/timeout
		# TODO: Do function, can take structure from server code
		pass
