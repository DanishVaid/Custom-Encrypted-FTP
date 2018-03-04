#!/usr/local/bin/python3

from shared import connection
from time import sleep
from client_pkg import command

class Client(object):

	def __init__(self, config_file):
		self.config_file = config_file

		self.client_IP = None
		self.client_port = None

		self.server_IP = None
		self.server_port = None

		self.incoming_stream = None
		self.outgoing_socket = None

	def run(self):
		self.configure()

		self.make_connection()

		user_command = command.Command(self.outgoing_socket)
		user_command.take_command()

		self.close_connection()

	def make_connection(self):
		incoming_socket = connection.create_accept_socket(self.server_IP, self.server_port)
		sleep(5)
		self.outgoing_socket = connection.create_connect_socket(self.client_IP, self.client_port)
		sleep(5)
		self.incoming_stream = connection.open_connection(incoming_socket)

	def close_connection(self):
		connection.close_socket(self.outgoing_socket)

	def configure(self):
		file = open(self.config_file, 'r')
		lines = file.readlines()

		self.server_IP = lines[0].split("=")[1]
		self.server_port = lines[1].split("=")[1]
		self.client_IP = lines[2].split("=")[1]
		self.client_port = lines[3].split("=")[1]

		file.close()

def init(config_file):
	print("Client opened.")

	client = Client()
	client.run()

	print("Client closed.")