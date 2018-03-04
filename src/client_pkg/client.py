#!/usr/local/bin/python3

from shared import connection
from time import sleep
from client_pkg import command

class Client(object):

	def __init__(self):
		self.incoming_stream = None
		self.outgoing_socket = None

	def run(self):
		self.make_connection()

		user_command = command.Command(self.outgoing_socket)
		user_command.take_command()

		self.close_connection()

	def make_connection(self):
		incoming_socket = connection.create_accept_socket("127.0.0.1", 5001)

		sleep(5)

		self.outgoing_socket = connection.create_connect_socket("127.0.0.1", 5000)

		sleep(5)

		self.incoming_stream = connection.open_connection(incoming_socket)

	def close_connection(self):
		connection.close_socket(self.outgoing_socket)

def init(config_file):
	print("Client opened.")

	client = Client()
	client.run()

	print("Client closed.")