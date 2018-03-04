import socket

def process_command(message):
	pass

def receive_message(incoming_stream):
	print("Mapper is receiving messages.")

	in_session = True
	while(in_session):
		incoming_stream.settimeout(1)

		try:
			data = incoming_stream.recv(4096).decode()

			if len(data) > 0:
				if data == "exit":
					in_session = False

				print("Message is:", data)
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