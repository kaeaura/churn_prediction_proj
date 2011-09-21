# Jing-Kai Lou (kaeaura@gamil.com) Wed Sep  7 10:39:09 CST 2011
# This script helps finding the emotion text candidates

import os
import sys
import codecs
import getopt

__author__ = "Jing-Kai Lou (kaeaura@gmail.com)"

def get_prefix(str1, str2):
	if type(str1) is str and type(str2) is str:
		prefix = list()
		for x, y in zip(str1, str2):
			if x == y:
				prefix.append(x)
			else:
				break
		return("".join(prefix))
	else:
		print ("The given arguments incorrect. Should be string type")

def main(argv):
	try:
		opts, args = getopt.getopt(argv, "hi:", ["help"])
	except getopt.GetoptError:
		print ("The given arguments incorrect")
		sys.exit(2)

	is_shown = False
	infile = None

	def usage():
		print ("-h : print the usage")
		print ("-i ...: the infile")

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt in ("-i"):
			infile = arg
			if not os.path.exists(arg):
				print ("The input file does not exist")
				sys.exit(2)

	# reading the ids
	id_set = set()
	with open(infile, 'r') as F:
		for line in F:
			readId = line.strip()
			id_set.add(readId)
	id_list = list(id_set)
	del id_set

	# comparing each two id
	emotion_candidates = set()
	for id1_index, id1 in enumerate(id_list):
		for id2 in id_list[(id1_index + 1):]:
			common_str = get_prefix(id1, id2)
			common_str_len = len(common_str)
			if is_shown:
				print ("::".join([id1, id2]))
				print (common_str)
			if common_str_len > 2:
				emotion_candidates.update([id1[common_str_len:], id2[common_str_len:]])
			else:
				continue

	# output
	for emotion_candidate in emotion_candidates:
		print (emotion_candidate)

if __name__ == "__main__":
	main(sys.argv[1:])

