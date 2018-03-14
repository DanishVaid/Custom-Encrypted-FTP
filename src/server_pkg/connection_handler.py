import socket

from shared import files
from shared import packet
from shared import directory

class ConnectionHandler(object):

	def __init__(self, outgoing_socket):
		self.outgoing_socket = outgoing_socket

		self.directory = directory.Directory("server")
		self.in_session = True

		self.commands = {
			"exit": exit,
			"lls": lls,
			"lcd": lcd,
			"lpwd": lpwd,
			"ls": ls,
			"cd": cd,
			"pwd": pwd,
			"upload": upload,
			"download": download
		}

	def consume_packet(self, packet):
		if packet._type == 'c':
			# TODO: Figure how to send to close connection message
			process_command(packet)
		elif packet._type == 'm':
			process_metadata(packet)
		elif packet._type == 'd':
			process_data(packet)
		else:
			print("[ERROR] Packet type not detected. Packet dropped.")
			print("[DEBUG] Packet data:", data)

	def process_command(self, packet):
		if pack.data == 'ls':
			# TODO: send string to client
			print('\nFiles in current directory:\n', subprocess.getoutput('ls'))

	def process_metadata(self):
		pass

	def process_data(self):
		pass