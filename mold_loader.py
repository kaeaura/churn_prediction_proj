# Jing-Kai Lou (kaeaura@gmail.com) Tue Sep  6 11:52:23 CST 2011
# This script load the pickle files dumped by mold_saver.py

from collection import defaultdict
from datetime import datetime, timedelta
from mold_saver import Char
import os
import sys
import getopt
import pickle

__author__ = "Jing-Kai Lou (kaeaura@gmail.com)"

def main(argv):
	try:
		opts, args = getopt.getopt(argv, "hi:", ["help"])
	except getopt.GetoptError:
		print ("The given arguments incorrect")

	loadfile = None
	mergingfile = None

	def usage():
		print ("-h : print the usage")
		print ("-i ...: the loadfile")

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt in ("-i"):
			loadfile = arg
			if not os.path.exists(loadfile):
				print ("The load-file does not exist!")
				usage()
				sys.exit(2)

if __name__ == "__main__":
	profiles = main(sys.argv[1:])

	# testing print
	for user in profiles.keys():
		print "==="
		print "ID: ", user
		#print "subscription range: %s %s" % "-".join(map(lambda x: str(x), profiles[user].deslen))
		#print "tell con count: %d" % len(profiles[user].t_con_len)
