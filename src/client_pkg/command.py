from client_pkg import preferences
from shared import files
from shared.packets import Command_Packet

class Command(object):

	def __init__(self, server_socket):
		self.server_socket = server_socket

		self.file_directory = None # Default to cwd

	def take_command(self):
		in_session = True
		while in_session:
			self.list_commands()

			console_input = input("Command (enter 'exit' to quit): ")
			console_input = console_input.split()

			if len(console_input) == 0:
				print("No input detected.")
				continue
			command = console_input[0]
			args = []

			built_pack = None

			if len(console_input) > 1:
				args = console_input[1:]

			if command == "exit":
				in_session = False

			elif command == "pref":
				user_preferences = preferences.Preferences()
				user_preferences.set_preferences()

			elif command == "ls":
				built_pack = Command_Packet('ls')

			elif command == "cd":
				pass

			elif command == "upload":
				packet_size = 4096
				file = files.Files("client_pkg/test.txt", packet_size)

				seek_point = 0
				while True:
					data = file.read_file(seek_point)

					if len(data) == 0:
						break

					self.server_socket.sendall(data)
					seek_point = seek_point + packet_size

				print("[DEBUG] Done sending.")

			elif command == "download":
				pass

			else:
				print("Command not recognized.")

			self.server_socket.sendall(built_pack.serialize())


	def list_commands(self):
		print("Commands")
		print("--------")

		print("Set Preferences: pref")

		print("List Current Directory: ls")
		print("Change Directory: cd <directory name>")

		print("Upload File: upload <filename>")
		print("Download File: download <filename>")