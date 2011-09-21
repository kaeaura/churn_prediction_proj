# Jing-Kai Lou (kaeaura@gamil.com) Tue Sep 13 10:23:27 CST 2011
# This script will load the pickle files and generate the feature table

from collections import defaultdict
from datetime import datetime, timedelta
from mold_saver import Char
import os
import sys
import pickle
import getopt

__author__ = "Jing-Kai Lou (kaeaura@gmail.com)"

secs_in_day = 86400
csv_sep = ','

def add(x, y):
	return(x + y)

def paste(seperator, *args):
	args = map(lambda  x: str(x), args)
	return(seperator.join(args))

#def to_str(int_list, spliter = ","):
#	if type(int_list) is list:
#		return(spliter.join([str(x) for x in int_list]))
#	else:
#		print ("Type Error! Input type is not list")

def main(argv):
	try:
		opts, args = getopt.getopt(argv, "hi:r:o:", ["help", "range"])
	except getopt.GetoptError:
		print ("The given arguments incorrect")
		sys.exit(2)

	enable_show		= True
	picklefile		= None
	show_range		= None
	outfile			= None
	csv_seperator	= ','

	def usage():
		print ("-h : print the usage")
		print ("-i [file-path]: load the features which means the *.pickle file")
		print ("-r [integer]: duration length (unit as day). for extracting the early activity events")
		print ("-o [file-path]: output path. with csv format")

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt in ("-i"):
			picklefile = arg
			if not os.path.exists(picklefile):
				print ("Loading Error! The input file doesn't exist")
				sys.exit(2)
		elif opt in ("-r"):
			try:
				show_range = int(arg)
			except ValueError:
				print ("Arg Error! The range should be an integer")
				sys.exit(2)
		elif opt in ("-o"):
			outfile = arg

	# loading the features (pickle file)
	if enable_show:
		print (" Loading files")
	user_dict = pickle.load(file(picklefile, 'r'))
	if enable_show:
		print (" done")

	# function for extraction
	def early_act(char, delta):
		"""
			char: Char class, user-profile
			delta: unit days
			output the act only in early period as a dictionary
		"""
		return(char.get_events(min(char.subscription) + timedelta(days = delta)))

	def speaks_statistical_data(d):
		"""
			d as the speaks dict in class Char
		"""
		if len(d):
			speak_len_list	= [sum(speak_list) for speak_list in d.values()]
			speak_num_list	= [len(speak_list) for speak_list in d.values()]
			sl_Sum			= sum(speak_len_list)
			sl_Mean			= float(sl_Sum) / len(speak_len_list)
			sl_Max			= max(speak_len_list)
			sl_Min			= min(speak_len_list)
			sl_arr			= [sl_Sum, sl_Mean, sl_Max, sl_Min]
			sn_Sum			= sum(speak_num_list)
			sn_Mean			= float(sn_Sum) / len(speak_num_list)
			sn_Max			= max(speak_num_list)
			sn_Min			= min(speak_num_list)
			sn_arr			= [sn_Sum, sn_Mean, sn_Max, sn_Min]
			return(sl_arr + sn_arr)
		else:
			return([0] * 8)

	# outputing
	outdir = os.path.dirname(outfile)
	if len(outdir) and not os.path.exists(outdir):
		os.makedirs(outdir)

	# clear file
	if os.path.exists(outfile):
		os.remove(outfile)

	if enable_show:
		print ("Outputing ...")

	# outputing
	with open(outfile, 'a') as F:
		predict_part	= "des_len"

		id_part			= paste(csv_sep, "cid", "account", "gender", "race", "level")

		tLValue_part	= paste(csv_sep, "tLSum", "tLMean", "tLMin", "tLMix")
		tNValue_part	= paste(csv_sep, "tNSum", "tNMean", "tNMin", "tNMix")
		tValue_part		= paste(csv_sep, tLValue_part, tNValue_part)

		sLValue_part	= paste(csv_sep, "sLSum", "sLMean", "sLMin", "sLMix")
		sNValue_part	= paste(csv_sep, "sNSum", "sNMean", "sNMin", "sNMix")
		sValue_part		= paste(csv_sep, sLValue_part, sNValue_part)

		pLValue_part	= paste(csv_sep, "pLSum", "pLMean", "pLMin", "pLMix")
		pNValue_part	= paste(csv_sep, "pNSum", "pNMean", "pNMin", "pNMix")
		pValue_part		= paste(csv_sep, pLValue_part, pNValue_part)

		fLValue_part	= paste(csv_sep, "fLSum", "fLMean", "fLMin", "fLMix")
		fNValue_part	= paste(csv_sep, "fNSum", "fNMean", "fNMin", "fNMix")
		fValue_part		= paste(csv_sep, fLValue_part, fNValue_part)

		attr_part		= paste(csv_sep, "dDay", "rDay", tValue_part, sValue_part, pValue_part, fValue_part)

		event_part		= paste(csv_sep, "familyRank", "familyNum", "friendNum")

		outheader		= paste(csv_sep, predict_part, id_part, attr_part, event_part)

		F.write("%s\n" % outheader)

		# character
		for cid, data in user_dict.items():
			if len(data.subscription) :
				# subscription length
				d_date			= min(data.subscription)
				e_date			= max(data.subscription)
				des_len			= (e_date - d_date).total_seconds() / secs_in_day

				# attributes
				account			= data.account
				gender			= data.gender
				race			= data.race
				level			= data.level
				all_attributes	= paste(csv_sep, account, gender, race, level)

				# activities in revealed period
				r_date			= d_date + timedelta(days = show_range)

				values			= data.get_event_summary(d_date, r_date, 'tellspeaks', 'sayspeaks', 'partyspeaks', 'familyspeaks')
				all_values		= reduce(add, map(lambda x: x[1], values))
				all_activities	= csv_sep.join(str(x) for x in all_values)

				# events
				familyRank		= len(filter(lambda x: x != 0, data.rank.values()))
				familyNum		= len(data.familyhistory)
				friendNum		= len(data.addedfriends)
				all_events		= paste(csv_sep, familyRank, familyNum, friendNum)

				outline = paste(csv_sep, str(des_len), cid, all_attributes, all_activities, all_events)
				F.write("%s\n" % outline)
			else:
				continue

#		# character
#		for cid, data in user_dict.items():
#			if len(data.subscription) :
#				# subscription length
#				d_iDate			= min(data.subscription)
#				d_date			= to_date(d_iDate)
#				e_iDate			= max(data.subscription)
#				e_date			= to_date(e_iDate)
#				if type(d_date) is date and type(e_date) is date:
#					des_len	= (e_date - d_date).days + 1
#					if des_len < 10:
#						continue
#				else:
#					des_len = None
#					continue
#
#				# attributes
#				account			= data.account
#				gender			= data.gender
#				race			= data.race
#				level			= data.level
#				all_attributes	= to_str([account, gender, race, level])
#
#				# activities in revealed period
#				r_iDate			= intDate_addition(d_iDate, show_range)
#				if r_iDate == 1:	#input error
#					print ("%s :: %d" % (cid, d_iDate))
#					continue
#				acts_dict		= early_act(data, show_range)
#				tValues			= to_str(speaks_statistical_data(acts_dict['tellspeaks']))
#				sValues			= to_str(speaks_statistical_data(acts_dict['sayspeaks']))
#				pValuse			= to_str(speaks_statistical_data(acts_dict['partyspeaks']))
#				fValues			= to_str(speaks_statistical_data(acts_dict['familyspeaks']))
#				all_activities	= to_str([d_iDate, r_iDate, tValues, sValues, pValuse, fValues])
#
#				# events
#				familyRank		= len(filter(lambda x: x != 0, data.rank.values()))
#				familyNum		= len(data.familyhistory)
#				friendNum		= len(data.addedfriends)
#				all_events		= to_str([familyRank, familyNum, friendNum])
#
#				outline = to_str([str(des_len), cid, all_attributes, all_activities, all_events])
#				F.write("%s\n" % outline)
#			else:
#				continue


	if enable_show:
		print ("done")

if __name__ == "__main__":
	main(sys.argv[1:])
