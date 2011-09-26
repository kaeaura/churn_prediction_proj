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
		opts, args = getopt.getopt(argv, "hi:m:t", ["help"])
	except getopt.GetoptError:
		print ("The given arguments incorrect")

	loadfile = None
	mergingfiles = list()
	enable_test = False

	def usage():
		print ("-h : print the usage")
		print ("-i ...: the loadfile")
		print ("-t: show testing page")
		print ("-m ...: merged files")

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
		elif opt in ("-t"):
			enable_test = True
		elif opt in ("-m"):
			mergingfiles.append(arg)

	print ("Loading file: %s" % loadfile)
	user_dict = cPickle.load(open(loadfile, 'r'))
	print ("done")

	for mfile in mergingfiles:
		if os.path.exists(mfile):
			print ("Loading to-merge file: %s" % mfile)
			addon_dict = cPickle.load(open(mfile, 'r'))

			print ("Merging ...")
			# update items in addon_dict not in user_dict
			mdiff_keys = list(set(addon_dict.keys()) - set(user_dict.keys()))
			for mdiff_key in mdiff_keys:
				user_dict[mdiff_key] = addon_dict[mdiff_key]

			# update items in addon_dict and in user_dict
			minter_keys = list(set(addon_dict.keys()) - set(mdiff_keys))
			for minter_key in minter_keys:
				user_dict[minter_key].update(addon_dict[minter_key])

			addon_dict.clear()
			print ("done")
		else:
			print ("file : %s does not exist! so skipped." % mfile)

	# testing print
	if enable_test:
		print ("Dictionary Len: %d" % len(user_dict))
		print ("Dictionary Type: %s" % type(user_dict))
		for user in user_dict.keys():
			print ("===")
			print ("ID: %s" % user)
			if user_dict[user] is None:
				print ("!!! %s" % user)
			else:
				d, e = user_dict[user].get_subscription_range()
				print "Act. Period", d, e
				j = min(user_dict[user].familyhistory.values()) if len(user_dict[user].familyhistory) else 0
				print ("First Guild-joint date: %d" % j)
				f = ';'.join(user_dict[user].familyhistory.keys()) if len(user_dict[user].familyhistory) else "None"
				print ("Joined Guilds: %s" % f)
				print ("Achieved Guild-Position: %s" % ';'.join(user_dict[user].rank.values()))

if __name__ == "__main__":
	main(sys.argv[1:])


