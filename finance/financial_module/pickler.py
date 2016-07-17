import pickle


# pickle writer
def pickle_write(data, filename):
	print('pickle write :', data)
	with open(filename, 'w+') as fw:
		pickle.dump(data, fw)


# pickle reader
def pickle_read(filename):
	with open(filename, 'r') as fw:
		data = pickle.load(fw)
	return data
