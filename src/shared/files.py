

class Files(object):

	def __init__(self, filename, data_size):
		self.filename = filename
		self.data_size = data_size

		self.seek_point = 0

	def read_file_slice(self):
		data = ""
		# TODO: File object handles current read point
		with open(self.filename, 'rb') as this_file:
			this_file.seek(self.seek_point)
			data = this_file.read(self.data_size)
			self.seek_point += self.data_size

		return data

	def write_file_by_append(self, data):
		with open(self.filename, 'ab') as this_file:
			this_file.write(data)

	# TODO: Destructor