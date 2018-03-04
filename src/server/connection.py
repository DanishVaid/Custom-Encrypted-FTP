import socket
from time import sleep

### Connection class. Static functions. ###

def open_connection(accept_sock):
	stream, client_address = accept_sock.accept()
	return stream


def close_socket(sock):
	sock.close()


def create_connect_socket(IP, port):
	port = int(port)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	try:
		address = (IP, port)
		sock.connect(address)

	except socket.error as sock_error:
		print(sock_error, IP, port)
		sleep(1)
		create_connect_socket(IP, port)

	return sock
	

def create_accept_socket(IP, port):
	port = int(port)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		address = (IP, port)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind(address)
		sock.listen(10)

	except socket.error as sock_error:
		print(sock_error, IP, port)
		sleep(1)
		create_accept_socket(IP, port)

	return sock