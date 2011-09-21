# Jing-Kai Lou (kaeaura@gmail.com) Tue Sep  6 11:52:23 CST 2011
# This script load the pickle files dumped by mold_saver.py

import os
import sys
import getopt
import pickle
from mold_saver import Char

__author__ = "Jing-Kai Lou (kaeaura@gmail.com)"

def migration(mfrom, mto):
	if mfrom.__name__ == "Char" and mto.__name__ == "Char":
		if mfrom.cid == mto.cid:
			mto.add_onei_iter(mfrom.onei.keys(), mfrom.onei.values())
			mto.add_inei_iter(mfrom.inei.keys(), mfrom.inei.values())
			mto.add_family_iter(mfrom.family.keys(), mfrom.family.values())
			mto.extend_tcon(mfrom.t_con_len)
			mto.extend_fcon(mfrom.f_con_len)
			mto.extend_scon(mfrom.s_con_len)
			mto.extend_pcon(mfrom.p_con_len)
			mto.refresh_description(mfrom.deslen)
			return(mto)
		else:
			print ("Error! Two inputs should share the identical cid")
			return(None)
	else:
		print ("Incorrect input class")
		return(None)


def main(argv):
	try:
		opts, args = getopt.getopt(argv, "hi:m:", ["help"])
	except getopt.GetoptError:
		print ("The given arguments incorrect")

	loadfile = None
	mergingfile = None

	def usage():
		print ("-h : print the usage")
		print ("-i ...: the loadfile")
		print ("-m ...: the file to merge")

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
		elif opt in ("-m"):
			mergingfile = arg
			if not os.path.exists(mergingfile):
				print ("The merging-file does not exist!")
				usage()
				sys.exit(2)

	if mergingfile is None:
		return (pickle.load(file(loadfile, 'r')))
	else:
		ld = pickle.load(file(loadfile, 'r'))
		md = pickle.load(file(mergingfile, 'r'))
		to_merge_ids = list(set(ld.keys()) & set(md.keys()))

		# migrating the information from md dictionary to ld dictionary
		for md_id in md.keys():
			if md_id in to_merge_ids:
				x = migration(md[md_id], ld[md_id])
				if x is not None:
					ld[md_id] = x
			else:
				ld[md_id] = md[md_id]
		return (ld)

if __name__ == "__main__":
	profiles = main(sys.argv[1:])

	# testing print
	for user in profiles.keys():
		print "==="
		print "ID: ", user
		print "subscription length: %s" % "-".join(map(lambda x: str(x), profiles[user].deslen))
		print "tell con count: %d" % len(profiles[user].t_con_len)
		print "family:"
		for f, t in profiles[user].family.items():
			print "\t", f, t
