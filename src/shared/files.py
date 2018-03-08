

class Files(object):

	def __init__(self, filename, packet_size):
		self.filename = filename
		self.packet_size = packet_size

		self.seek_point = 0

	def read_file(self, seek_point):
		data = ""
		with open(self.filename, 'rb+') as file:
			file.seek(seek_point)
			data = file.read(self.packet_size)

		return data

	def write_file(self, write_point):
		pass

	def write_file_by_append(self, data):
		with open(self.filename, 'ab') as file:
			file.write(data)
