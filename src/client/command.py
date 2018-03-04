def take_command(server_socket):
	in_session = True
	while in_session:
		list_commands()

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

		server_socket.sendall((command).encode())


def list_commands():
	print("List of commands:")

	print("List Current Directory: ls")
	print("Change Directory: cd <directory name>")
	print("Upload File: upload <filename>")
	print("Download File: download <filename>")