import json

from shared import connection
from time import sleep
from client_pkg import command

class Client(object):

	def __init__(self):
		self.client_IP = None
		self.client_port = None

		self.server_IP = None
		self.server_port = None

		self.incoming_stream = None
		self.outgoing_socket = None

	def run(self, config):
		self.configure(config)

		self.make_connection()

		user_command = command.Command(self.outgoing_socket)
		user_command.take_command()

		self.close_connection()

	def make_connection(self):
		incoming_socket = connection.create_accept_socket(self.client_IP, self.client_port)
		sleep(5)
		self.outgoing_socket = connection.create_connect_socket(self.server_IP, self.server_port)
		sleep(5)
		self.incoming_stream = connection.open_connection(incoming_socket)

	def close_connection(self):
		connection.close_socket(self.outgoing_socket)

	def configure(self, config):
		self.client_IP = config['client_ip']
		self.client_port = config['client_port']
		self.server_IP = config['server_ip']
		self.server_port = config['server_port']


def init(config_file):
	if config_file is None:
		config_file = 'client_pkg/config.json'
	with open(config_file, 'r') as c_file:
		config = json.load(c_file)

	print("Client starting . . .")

	client = Client()
	client.run(config)

	print("Client closed.")