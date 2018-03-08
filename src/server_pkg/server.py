import json

from server_pkg import message
from shared import connection
from time import sleep

class Server(object):

	def __init__(self):
		self.incoming_stream = None
		self.outgoing_socket = None

		self.file_directory = None

	def run(self, config):
		self.make_connection(config)
		message.receive_message(self.incoming_stream)
		self.close_connection()

	def make_connection(self, config):
		incoming_socket = connection.create_accept_socket(config['incoming_ip'], config['incoming_port'])

		sleep(5)

		self.outgoing_socket = connection.create_connect_socket(config['outgoing_ip'], config['outgoing_port'])

		sleep(5)

		self.incoming_stream = connection.open_connection(incoming_socket)

	def close_connection(self):
		connection.close_socket(self.outgoing_socket)

def init(config_file):
	if config_file is None:
		config_file = 'server_pkg/config.json'
	with open(config_file, 'r') as c_file:
		config = json.load(c_file)
		
	print("Starting server . . .")

	server = Server()
	server.run(config)

	print("-- Server closed --")