import json
from time import sleep

from server_pkg import message_queue
from server_pkg import connection_handler
from shared import connection

class Server(object):

	def __init__(self, config):
		self.config = config

		self.server_IP = None
		self.server_port = None

		# TODO: Temporary, to be removed when we add multi-threading/client
		self.client_IP = None
		self.client_port = None

		self.incoming_stream = None
		self.outgoing_socket = None

	def run(self):
		self.configure()
		self.make_connection()
		msg_queue = message_queue.MessageQueue(self.incoming_stream)
		conn_handler = connection_handler.ConnectionHandler(self.outgoing_socket)
		msg_queue.add_handler(conn_handler)

		msg_queue.receive_messages()
		self.close_connection()

	def make_connection(self):
		# TODO: To be changed to allow for multi-client
		incoming_socket = connection.create_accept_socket(self.server_IP, self.server_port)
		sleep(5)
		self.outgoing_socket = connection.create_connect_socket(self.client_IP, self.client_port)
		sleep(5)
		self.incoming_stream = connection.open_connection(incoming_socket)

	# TODO: To be changed to allow for multi-client
	def close_connection(self):
		connection.close_socket(self.outgoing_socket)

	def configure(self):
		self.server_IP = self.config['server_ip']
		self.server_port = self.config['server_port']

		# TODO: Temporary, to be removed when we add multi-threading/client
		self.client_IP = self.config['client_ip']
		self.client_port = self.config['client_port']

def init(config_file):
	if config_file is None:
		config_file = 'server_pkg/config.json'
		
	with open(config_file, 'r') as c_file:
		config = json.load(c_file)
		
	print("Starting server . . .")

	server = Server(config)
	server.run()

	print("-- Server closed --")