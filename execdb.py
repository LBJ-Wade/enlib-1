class ExecDB:
	"""ExecDB is a flexible way of mapping from dataset ids to
	the files needed for analysing that dataset. It is based on two
	inputs:
	
	1. The database file containes python code that should define
	variables containing the information necessary to load and interpret
	the dataset files. The variables available to the code in this
	file is setup by a second file - the vars setup file.
	2. The vars setup is a file containing python code that will be
	called with the variable "id" defined. Its job is to define variables
	that can be used in the data file. The idea is that this file is
	needs to chance much less often than the other one.

	For example, if vars is 'a = len(id)' and db is
	'if a[0] > 2: moo = id
	 else: moo = id[::-1]'
	then a query with id = "hello" will result in
	{'moo': 'hello', 'id'='hello', 'a': 4}"""
	def __init__(self, db_file=None, vars_file=None, db_data=None, vars_data=None):
		db_data    = read_data(db_file,    db_data)
		vars_data = read_data(vars_file, vars_data, "")
		if db_data is None: raise ValueError("No database specified in ExecDB")
		self.source = vars_data + "\n" + db_data
		self.code   = compile(self.source, "<exec_db,source>", "exec")
	def query(self, id):
		locs = {"id":id}
		exec(self.code, {}, locs)
		locs = recursive_format(locs, locs.copy())
		return locs
	def dump(self):
		return self.source

def read_data(file_or_fname=None, data=None, default=None):
	"""Helper function for ExecDB. Gets a string of data
	from either a file or the provided data argument"""
	if data is not None: return data
	if file_or_fname is None: return default
	if isinstance(file_or_fname, file):
		return file.read()
	else:
		with open(file_or_fname) as f:
			return f.read()

def recursive_format(data, formats):
	"""Expand all strings contained in dicts, lists or tuples in data
	using string.format with the given formats dict"""
	if isinstance(data, dict):
		data = {key: recursive_format(data[key], formats) for key in data}
	elif isinstance(data, list):
		data = [recursive_format(val, formats) for val in data]
	elif isinstance(data, tuple):
		data = tuple([recursive_format(val, formats) for val in data])
	elif isinstance(data, basestring):
		return data.format(**formats)
	return data
