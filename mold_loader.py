# Jing-Kai Lou (kaeaura@gmail.com) Tue Sep  6 11:52:23 CST 2011
# This script load the cPickle files dumped by mold_saver.py

from collections import defaultdict
from datetime import datetime, timedelta
from mold_saver import Char
import os
import sys
import getopt
import cPickle

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

	return(cPickle.load(open(loadfile, 'r')))

if __name__ == "__main__":
	profiles = main(sys.argv[1:])

	# testing print
	print ("Dictionary Len: %d" % len(profiles))
	print ("Dictionary Type: %s" % type(profiles))
	for user in profiles.keys():
		print ("===")
		print ("ID: %s" % user)
		d, e = profiles[user].get_subscription_range()
		print "Act. Period", d, e
		j = min(profiles[user].familyhistory.values()) if len(profiles[user].familyhistory) else 0
		print ("First Guild-joint date: %d" % j)
		f = ';'.join(profiles[user].familyhistory.keys()) if len(profiles[user].familyhistory) else "None"
		print ("Joined Guilds: %s" % f)
		print ("Achieved Guild-Position: %s" % ';'.join(profiles[user].rank.values()))

