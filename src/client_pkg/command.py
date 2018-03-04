from client_pkg import preferences

class Command(object):

	def __init__(self, server_socket):
		self.server_socket = server_socket

		self.file_directory = None # Default to cwd

	def take_command(self):
		in_session = True
		while in_session:
			self.list_commands()

			console_input = input("Command (enter 'exit' to quit):")
			console_input = console_input.split()

			if len(console_input) == 0:
				print("No input detected.")
				continue

			command = console_input[0]

			args = []
			if len(console_input) > 1:
				args = console_input[1:]

			if command == "exit":
				in_session = False

			elif command == "pref":
				user_preferences = preferences.Preferences()
				user_preferences.set_preferences()

			elif command == "ls":
				pass

			elif command == "cd":
				pass

			elif command == "upload":
				pass

			elif command == "download":
				pass

			else:
				print("Command not recognized.")

			self.server_socket.sendall((command).encode())


	def list_commands(self):
		print("Commands")
		print("--------")

		print("Set Preferences: pref")

		print("List Current Directory: ls")
		print("Change Directory: cd <directory name>")

		print("Upload File: upload <filename>")
		print("Download File: download <filename>")