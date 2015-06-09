import string
import random
import os
import sys

files_name = []

def generate_line(size):
	return''.join(random.choice(string.hexdigits) for i in range(size))

def generate_file(size):
	s = ""
	for i in range (size/100):
		s += generate_line(99)
		s += "\n"
	s += generate_line(size % 100)
	return s


if __name__ =="__main__":
	if len(sys.argv) != 3:
		print 'Usage is : random_gen <number of files><size in bytes>'
		sys.exit(1)
	else:
		if not os.path.exists("./dataset"):
			os.makedirs("./dataset")
		
		for i in range(int(sys.argv[1])):
			files_name.append(''.join(random.choice(string.hexdigits) for i in range(10)));

		for file_name in files_name:
			f = open(os.path.join('./dataset', file_name), 'w')
			f.write(generate_file(int(sys.argv[2])))

