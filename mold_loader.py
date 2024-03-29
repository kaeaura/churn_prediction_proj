# Jing-Kai Lou (kaeaura@gmail.com) Tue Sep  6 11:52:23 CST 2011
# This script load the cPickle files dumped by mold_saver.py
# And then give a testing or orginized output

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
		opts, args = getopt.getopt(argv, "hi:m:tw:I:", ["help"])
	except getopt.GetoptError:
		print ("The given arguments incorrect")

	loadfile = None
	mergingfiles = list()
	enable_test = False
	enable_write = False
	enable_write_interaction = False

	def usage():
		print ("-h : print the usage")
		print ("-i ...: the loadfile")
		print ("-t: show testing page")
		print ("-m ...: merged file")
		print ("-w ...: write activity table to file")
		print ("-I ...: write interaction table to file")

	def add(x, y):
		return(x + y)

	def paste(seperator, *args):
		args = map(lambda  x: str(x), args)
		return(seperator.join(args))

	def write_interaction(outfile, user_dict, csv_sep = ","):
		def extend(x, y): return(list(x) + list(y))
		with open(outfile, 'w') as F:
			# writing header
			outheader = paste(csv_sep, "sender", "receiver", "interactions")
			F.write("%s\n" % outheader)
			for cid, data in user_dict.items():
				if len(data.talkto.values()) == 0:
					continue
				else:
					all_rids_pool = reduce(extend, data.talkto.values())
					all_rids = list(set(all_rids_pool))
					for rid in all_rids:
						F.write("%s\n" % paste(csv_sep, cid, rid, len(filter(lambda x: x == rid, all_rids_pool))))

	def write_table(outfile, user_dict, csv_sep = ","):
		secs_in_day = 86400
		with open(outfile, 'w') as F:
			# writing header
			predict_part	= "sub_len"
			id_part			= paste(csv_sep, "ddate", "edate", "cid", "account", "gender", "race", "level")
			owl_part		= paste(csv_sep, "ts_stream", "tl_stream", "s_stream", "p_stream", "f_stream")
			event_part		= paste(csv_sep, "familyRank", "familyNum", "friendNum")
			outheader		= paste(csv_sep, predict_part, id_part, owl_part, event_part)
			F.write("%s\n" % outheader)

			# writing data
			for cid, data in user_dict.items():
				# subscription length
				d_date, e_date	= data.get_subscription_range()
				if d_date is not None and e_date is not None:
					des_len			= (e_date - d_date).total_seconds() / secs_in_day
					# attributes
					account			= data.account
					gender			= data.gender
					race			= data.race
					level			= data.level
					all_attributes	= paste(csv_sep, account, gender, race, level)
					# act_hours
					def get_stream(char, channel):
						counts			= char.get_owls(channel).items()
						counts.sort(key = lambda x: x[0])
						return(':'.join(map(lambda x: str(x[1]), counts)))
					ts_stream		= get_stream(data, 'tellspeaks')
					tl_stream		= get_stream(data, 'telllisten')
					s_stream		= get_stream(data, 'sayspeaks')
					p_stream		= get_stream(data, 'partyspeaks')
					f_stream		= get_stream(data, 'familyspeaks')
					streams			= paste(csv_sep, ts_stream, tl_stream, s_stream, p_stream, f_stream)
					# activities in revealed period
					s_int			= min(data.get_subscription())
					r_int			= max(data.get_subscription())
					# events
					familyRank		= len(filter(lambda x: x != 0, data.rank.values()))
					familyNum		= len(data.familyhistory)
					friendNum		= len(data.addedfriends)
					all_events		= paste(csv_sep, familyRank, familyNum, friendNum)
				else:
					continue

				outline = paste(csv_sep, str(des_len), s_int, r_int, cid, all_attributes, streams, all_events)
				F.write("%s\n" % outline)

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
		elif opt in ("-w"):
			enable_write = True
			outfile = arg
		elif opt in ("-I"):
			enable_write_interaction = True
			outfile = arg

	if loadfile is not None and os.path.exists(loadfile):
		print ("Loading file: %s" % loadfile)
		user_dict = cPickle.load(open(loadfile, 'r'))
		print ("done")
	else:
		print ("Initial user_dict")
		user_dict = dict()
		print ("done")

	# merge data
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

	# write table
	if enable_write and len(user_dict):
		print ("Writing file: %s" % outfile)
		write_table(outfile = outfile, user_dict = user_dict)
		print ("done")

	# write interaction table
	if enable_write_interaction and len(user_dict):
		print ("Writing interaction table: %s" % outfile)
		write_interaction(outfile = outfile, user_dict = user_dict)
		print ("done")

	# test print
	if enable_test:
		print ("Dictionary Len: %d" % len(user_dict))
		print ("Dictionary Type: %s" % type(user_dict))
		for user in user_dict.keys():
			print ("++++++++++++++++++++++++++++++++++++")
			print ("ID: %s" % user)
			profile = user_dict[user]
			if profile is None:
				print ("!!! %s" % user)
			else:
				d, e = profile.get_subscription_range()
				print "Act. Period", d, e
				j = min(profile.familyhistory.values()) if len(profile.familyhistory) else 0
				print ("First Guild-joint date: %d" % j)
				f = ';'.join(profile.familyhistory.keys()) if len(profile.familyhistory) else "None"
				print ("Joined Guilds: %s" % f)
				print ("Achieved Guild-Position: %s" % ';'.join(profile.rank.values()))
				c = profile.get_owls()
				print ("Acts in Hours %s" % "::".join([str(v) for v in c.values()]))

if __name__ == "__main__":
	main(sys.argv[1:])

