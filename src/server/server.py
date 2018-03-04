#!/usr/local/bin/python3

import process_message
import connection
from time import sleep

class Server(object):

	def __init__(self):
		self.incoming_stream = None
		self.outgoing_socket = None

		file_directory = None

	def run(self):
		self.make_connection()
		process_message.receive_message(self.incoming_stream)
		self.close_connection()

	def make_connection(self):
		incoming_socket = connection.create_accept_socket("127.0.0.1", 5000)

		sleep(5)

		self.outgoing_socket = connection.create_connect_socket("127.0.0.1", 5001)

		sleep(5)

		self.incoming_stream = connection.open_connection(incoming_socket)

	def close_connection(self):
		connection.close_socket(self.outgoing_socket)

def main():
	print("Running Server")

	server = Server()
	server.run()

if __name__ == "__main__":
	main()