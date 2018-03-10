import os

class Directory(object):

	def __init__(self, user_type):
		self.home_directory_prefixes = self.get_home_directory_prefixes(user_type)
		self.current_directory_prefixes = self.home_directory_prefixes

	# Equivalent to cd
	def set_current_directory(self, directory):
		if directory == "..":
			self.current_directory_prefixes = self.current_directory_prefixes[:-1]
		else:
			directory_files = self.get_current_directory_files()

			possible_directories = []
			for file in directory_files:
				possible_directory = self.get_current_directory() + file
				if os.path.isdir(possible_directory):	#TODO: This does not work, learn functionality or find alternative
					possible_directories.append(file)

			if directory in possible_directories:
				self.current_directory_prefixes.append(directory)
				return self.build_directory_path_string(self.current_directory_prefixes)
			else:
				return "Directory does not exist."

	# Equivalent to pwd
	def get_current_directory(self):
		return self.build_directory_path_string(self.current_directory_prefixes)

	# Equivalent to ls
	def get_current_directory_files(self):
		files = os.listdir(self.build_directory_path_string(self.current_directory_prefixes))
		return files

	def build_directory_path_string(self, directory_prefixes):
		directory_path = ""
		for i in range(0, len(directory_prefixes)):
			directory_path += "/" + directory_prefixes[i]

		return directory_path

	def get_home_directory_prefixes(self, user_type):
		shared_src_directory = os.getcwd()

		prefixes = shared_src_directory.split('/')
		prefixes = prefixes[1:-1]	# TODO: Test that cwd is src
		prefixes.append(user_type + "_home")

		return prefixes