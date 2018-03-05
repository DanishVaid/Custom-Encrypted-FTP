import socket
from shared import files

def process_command(message):
	pass

def receive_message(incoming_stream):
	print("Mapper is receiving messages.")

	in_session = True
	while(in_session):
		incoming_stream.settimeout(1)

		try:
			data = incoming_stream.recv(4096)

			if len(data) > 0:
				if data == "exit":
					in_session = False

				print("Message is:", data)

				file = files.Files("server_pkg/test_received.txt", 4096)
				file.write_file_by_append(data)

				# Replace with process_command(data)

				# if data[-1] == "%":
				# 	data = data[:-1]

				# data = data.split("%")
				# print(data)

				# for message in data:
				# 	if message == "close":
				# 		in_session = False
					
				# 	fileName = message.split(" ")[0]
				# 	offset = int(message.split(" ")[1])
				# 	size = int(message.split(" ")[2])

				# 	self.map(fileName, offset, size)

		except socket.timeout:
			pass