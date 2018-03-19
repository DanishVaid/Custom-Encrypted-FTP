
# Object for keep state of accessing each file
class Files(object):

	def __init__(self, filename, usetype, data_size=None):
		self.filename = filename
		self.data_size = data_size
		self.usetype = usetype
		self.file_obj = open(filename, usetype)

	def read_file_slice(self):
		assert self.usetype == 'rb'

		data = ""
		data = self.file_obj.read(self.data_size)
		return data

	def write_file_by_append(self, data):
		assert self.usetype == 'ab'

		self.file_obj.write(data)

	def close(self):
		self.file_obj.close()