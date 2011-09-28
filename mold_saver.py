# Jing-Kai Lou (kaeaura@gmail.com) Tue Sep  6 12:09:54 CST 2011 
# This script helps to make summary of parsed tell channel logs

from __future__ import print_function # We require Python 2.6 or later
from collections import defaultdict
from datetime import datetime
import os
import sys
import time
import getopt
import cPickle

__author__ = "Jing-Kai Lou (kaeaura@gmail.com)"


def str_to_idate(date_str):
	try:
		if len(date_str) >= 10:
			return(int(date_str[:10]))
		elif len(date_str) == 8:
			return(int(date_str + '00'))
		else:
			return(None)
	except ValueError:
		return(None)

class Char():
	"""
		Char information
	"""
	def __init__(self, cid):
		# static
		self.__name__			= "Char"
		self.cid				= cid
		self.account			= None
		self.race				= None
		self.gender				= None
		self.level				= None
		# event
		self.rank				= dict()
		self.addedfriends		= set()
		self.familyhistory		= dict()
		# activity
		self.talkto				= defaultdict(set)
		self.listento			= defaultdict(set)
		self.familyspeaks		= defaultdict(list)
		self.partyspeaks		= defaultdict(list)
		self.sayspeaks			= defaultdict(list)
		self.tellspeaks			= defaultdict(list)
		self.telllisten			= defaultdict(list)
		self.sellto				= defaultdict(set)
		self.buyfrom			= defaultdict(set)

	def update(self, C):
		if C.__name__ == "Char":
			self.rank.update(C.rank)
			self.addedfriends.update(C.addedfriends)
			self.familyhistory.update(C.familyhistory)
			self.talkto.update(C.talkto)
			self.listento.update(C.listento)
			self.familyspeaks.update(C.familyspeaks)
			self.partyspeaks.update(C.partyspeaks)
			self.sayspeaks.update(C.sayspeaks)
			self.tellspeaks.update(C.tellspeaks)
			self.telllisten.update(C.telllisten)
			self.sellto.update(C.sellto)
			self.buyfrom.update(C.buyfrom)
		else:
			print ("!!!")

	def set_account(self, account):
		self.account = account

	def set_race(self, race):
		self.race = race

	def set_gender(self, gender):
		self.gender = gender

	def set_rank(self, family, rank):
		if family not in self.rank.keys():
			self.rank[family] = rank
		else:
			self.rank[family] = max(rank, self.rank[family])

	def set_level(self, level):
		if self.level is None or self.level < level:
			self.level = level

	def add_friends(self, friends):
		if type(friends) in (set, list):
			self.addedfriends.update(friends)
		else:
			try:
				self.addedfriends.add(friends)
			except:
				print ('Friend list should be iteratiable')

	def join_family(self, family, time):
		if type(time) is not int:
			time = str_to_idate(time)
		if family not in self.familyhistory.keys() or self.familyhistory[family] > time:
			self.familyhistory[family] = time

	def join_families(self, families, times):
		for family, time in zip(families, times):
			self.join_family(family, time)

	def talk_to_one(self, rid, time):
		self.talkto[time].add(rid)

	def talk_to_them(self, rids, times):
		for rid, time in zip(rids, times):
			self.talk_to_one(rid, time)

	def listen_to_one(self, sid, time):
		self.listento[time].add(sid)

	def listen_to_them(self, sids, times):
		for sid, time in zip(sids, times):
			self.listen_to_one(sid, time)

	def speak_in_family(self, con, time):
		self.familyspeaks[time].append(con)

	def speak_in_party(self, con, time):
		self.partyspeaks[time].append(con)

	def speak_in_say(self, con, time):
		self.sayspeaks[time].append(con)

	def speak_in_tell(self, con, time):
		self.tellspeaks[time].append(con)

	def listen_in_tell(self, con, time):
		self.telllisten[time].append(con)

	def int_to_date(self, date_int):
		if date_int >= 10000000:
			date_str 	= str(date_int)
			s_year		= int(date_str[:4])
			s_month		= int(date_str[4:6])
			s_day		= int(date_str[6:8])
			s_hour		= int(date_str[8:10])
			return (datetime(year = s_year, month = s_month, day = s_day, hour = s_hour))
		else:
			print ("func:str_to_date:: length of time string is not long enough (10-digit)")
			return (None)

	def get_subscription(self):
		subscription = set()
		subscription.update(self.familyspeaks.keys())
		subscription.update(self.partyspeaks.keys())
		subscription.update(self.sayspeaks.keys())
		subscription.update(self.tellspeaks.keys())
		subscription.update(self.telllisten.keys())
		subscription.update(self.sellto.keys())
		subscription.update(self.buyfrom.keys())
		return(subscription)

	def get_owls(self, *args):
		"""
			for night-owl detection
		"""
		bins = map(lambda x: "%02d" % x, range(24))
		counts = dict().fromkeys(bins, 0)
		def get_hour(x): return(str(x)[-2:] if len(str(x)) == 10 else '123')

		items = list()
		if ('familyspeaks' in args):
			items.extend(self.familyspeaks.items())
		if ('partyspeaks' in args):
			items.extend(self.partyspeaks.items())
		if ('sayspeaks' in args):
			items.extend(self.sayspeaks.items())
		if ('tellspeaks' in args):
			items.extend(self.tellspeaks.items())
		if ('telllisten' in args):
			items.extend(self.telllisten.items())
		if ('sellto' in args):
			items.extend(self.sellto.items())
		if ('buyfrom' in args):
			items.extend(self.buyfrom.items())

		# loop through 
		for item in items:
			k, v = item
			if get_hour(k) in bins and type(v) is list:
				counts[get_hour(k)] += len(v)
		return(counts)

	def get_subscription_range(self):
		subscriptions = self.get_subscription()
		if len(subscriptions):
			return([self.int_to_date(min(subscriptions)), self.int_to_date(max(subscriptions))])
		else:
			return(None, None)

	def speaks_statistical_data(self, d):
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

	def get_events(self, start, end):
		pins		= [pin for pin in self.get_subscription() if end >= pin >= start]
		talkto		= dict(filter(lambda i: i[0] in pins, self.talkto.items()))
		listento	= dict(filter(lambda i: i[0] in pins, self.listento.items()))
		familyspeaks= dict(filter(lambda i: i[0] in pins, self.familyspeaks.items()))
		partyspeaks	= dict(filter(lambda i: i[0] in pins, self.partyspeaks.items()))
		sayspeaks	= dict(filter(lambda i: i[0] in pins, self.sayspeaks.items()))
		tellspeaks	= dict(filter(lambda i: i[0] in pins, self.tellspeaks.items()))
		telllisten	= dict(filter(lambda i: i[0] in pins, self.telllisten.items()))
		sellto		= dict(filter(lambda i: i[0] in pins, self.sellto.items()))
		buyfrom		= dict(filter(lambda i: i[0] in pins, self.buyfrom.items()))

		return(
			{
				'talkto': talkto,
				'listen': listento,
				'familyspeaks': familyspeaks,
				'partyspeaks': partyspeaks,
				'sayspeaks': sayspeaks,
				'tellspeaks': tellspeaks,
				'telllisten': telllisten,
				'sellto': sellto,
				'buyfrom': buyfrom
			}
		)

	def get_event_summary(self, start, end, *args):
		events = self.get_events(start, end)
		summary = list()
		for arg in args:
			if arg in events.keys():
				summary.append((arg, self.speaks_statistical_data(events[arg])))
		return(summary)

def main(argv):
	try:
		opts, args = getopt.getopt(argv, "hP:t:f:s:p:S:l:xg:", ["help", "save=", "load=", "exclusive"])
	except getopt.GetoptError:
		print ("The given arguments incorrect")
		sys.exit(2)

	known_sep = " "
	profile_file = None
	tell_log_file = None
	family_log_file = None
	say_log_file = None
	party_log_file = None
	savefile = None
	loadfile = None
	enable_exclusive = False
	group_size = 0

	def usage():
		print ("-h [--help] : print the usage")
		print ("-P ...: mold the user-profile")
		print ("-t ...: mold the tell log")
		print ("-f ...: mold the family log")
		print ("-s ...: mold the say log")
		print ("-p ...: mold the party log")
		print ("-S [--save] ...: file to save the user-profiles")
		print ("-l [--load] ...: load existing cPickle-file")
		print ("-x [--exclusive]: exclusive mode; char without profiles will not be saved")
		print ("-g ...: user number, split the saved files")

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt in ("-P"):
			profile_file = arg
		elif opt in ("-t"):
			tell_log_file = arg
		elif opt in ("-f"):
			family_log_file = arg
		elif opt in ("-s"):
			say_log_file = arg
		elif opt in ("-p"):
			party_log_file = arg
		elif opt in ("-S", "--save"):
			nf = arg.split('.')
			if nf[-1] != "cPickle":
				savefile = arg + ".cPickle"
			else:
				savefile = arg
		elif opt in ("-l", "--load"):
			loadfile = arg
		elif opt in ("-x"):
			enable_exclusive = True
		elif opt in ("-g"):
			try:
				group_size = int(arg)
			except ValueError:
				print ("Arg Error: The group size error!")
				sys.exit(2)


	# get features from chat logs (tell, family, say, party)
	if loadfile is not None and os.path.exists(loadfile):
		print ("Loading the user dictionary")
		user_dict = cPickle.load(file(loadfile, "r"))
	else:
		print ("Creating the user dictionary")
		user_dict	= dict()

	if profile_file is not None and os.path.exists(profile_file):
		read_line_number = 0
		print ("Analyzing file: %s" % profile_file)
		with open(profile_file, 'r') as F:
			for line in F:
				read_line_number += 1
				print ("%d\r" % read_line_number, end = "")
				sys.stdout.flush()
				record = line.strip().split(',')

				if len(record) != 11:
					print ("Warning. Type tell should contain 11 items in a line")
					continue
				else:
					filename= record[1]
					stamp	= '20' + filename.split('/')[4].split('_data')[1]
					account = record[3]
					cid		= record[4]
					gender	= record[5]
					race	= record[6]
					level	= record[7]
					family	= record[8]
					fRank	= record[9]
					friends = record[10]	# list, sep = ';'

					try:
						stamp	= stamp if len(stamp) == 8 else None
						gender	= int(gender)
						race	= int(race)
						level	= int(level)
						if stamp is None:
							print ("Wrong stamp")
							continue
					except ValueError:
						print ("Warning. Type profile: gender, race, or level shall be integer")
						continue

					if cid not in user_dict.keys():
						user_dict[cid] = Char(cid)
					user_dict[cid].set_account(account)
					user_dict[cid].set_gender(gender)
					user_dict[cid].set_race(race)
					user_dict[cid].set_level(level)
					user_dict[cid].add_friends(friends.split(';'))
					if family != '0':
						user_dict[cid].join_family(family, stamp)
						user_dict[cid].set_rank(family, fRank)

	if tell_log_file is not None and os.path.exists(tell_log_file):
		read_line_number = 0
		print ("Analyzing file: %s" % tell_log_file)
		with open(tell_log_file, 'r') as F:
			for line in F:
				read_line_number += 1
				print ("%d\r" % read_line_number, end = "")
				sys.stdout.flush()
				record = line.strip().split(known_sep)

				if len(record) != 4:
					print ("Warning. Type tell should contain 4 items in a line")
					continue
				else:
					tstamp, tsender, treceiver, tlen = record
					try:
						tstamp = str_to_idate(tstamp)
						tlen = int(tlen)
						if tstamp is None:
							print ("Wrong stamp")
							continue
					except ValueError:
						print ("Warning. Type tell: timestamp or content length shall be integer")
						continue

				if tsender not in user_dict.keys() and not enable_exclusive:
					user_dict[tsender] = Char(tsender)
				if tsender in user_dict.keys():
					user_dict[tsender].talk_to_one(treceiver, tstamp)
					user_dict[tsender].speak_in_tell(tlen, tstamp)

				if treceiver not in user_dict.keys() and not enable_exclusive:
					user_dict[treceiver] = Char(treceiver)
				if treceiver in user_dict.keys():
					user_dict[treceiver].listen_to_one(tsender, tstamp)
					user_dict[treceiver].listen_in_tell(tlen, tstamp)

	if family_log_file is not None and os.path.exists(family_log_file):
		read_line_number = 0
		print ("Analyzing file: %s" % family_log_file)
		with open(family_log_file, 'r') as F:
			for line in F:
				read_line_number += 1
				print ("%d\r" % read_line_number, end = "")
				sys.stdout.flush()
				record = line.strip().split(known_sep)

				if len(record) != 4:
					print ("Warning. Type family should contain 4 items in a line")
					continue
				else:
					fstamp, fname, fsender, flen = record
					try:
						fstamp = str_to_idate(fstamp)
						flen = int(flen)
						if fstamp is None:
							print ("Wrong stamp")
							continue
					except ValueError:
						print ("Warning. Type family: timestamp or content length shall be integer")
						continue

				if fsender not in user_dict.keys() and not enable_exclusive:
					user_dict[fsender] = Char(fsender)
				if fsender in user_dict.keys():
					user_dict[fsender].speak_in_family(flen, fstamp)
					user_dict[fsender].join_family(fname, fstamp)

	if say_log_file is not None and os.path.exists(say_log_file):
		read_line_number = 0
		print ("Analyzing file: %s" % say_log_file)
		with open(say_log_file, 'r') as F:
			for line in F:
				read_line_number += 1
				print ("%d\r" % read_line_number, end = "")
				sys.stdout.flush()
				record = line.strip().split(known_sep)

				if len(record) != 3:
					print ("Warning. Type say should contain 3 items in a line")
					continue
				else:
					sstamp, ssender, slen = record
					try:
						sstamp = str_to_idate(sstamp)
						slen = int(slen)
						if sstamp is None:
							print ("Wrong stamp")
							continue
					except ValueError:
						print ("Warning. Type say: timestamp or content length shall be integer")
						continue

				if ssender not in user_dict.keys() and not enable_exclusive:
					user_dict[ssender] = Char(ssender)
				if ssender in user_dict.keys():
					user_dict[ssender].speak_in_say(slen, sstamp)

	if party_log_file is not None and os.path.exists(party_log_file):
		read_line_number = 0
		print ("Analyzing file: %s" % party_log_file)
		with open(party_log_file, 'r') as F:
			for line in F:
				read_line_number += 1
				print ("%d\r" % read_line_number, end = "")
				sys.stdout.flush()
				record = line.strip().split(known_sep)

				if len(record) != 3:
					print ("Warning. Type party should contain 3 items in a line")
					continue
				else:
					pstamp, psender, plen = record
					try:
						pstamp = str_to_idate(pstamp)
						plen = int(plen)
						if pstamp is None:
							print ("Wrong stamp")
							continue
					except ValueError:
						print ("Warning. Type party: timestamp or content length shall be integer")
						continue
				if psender not in user_dict.keys() and not enable_exclusive:
					user_dict[psender] = Char(psender)
				if psender in user_dict.keys():
					user_dict[psender].speak_in_party(plen, pstamp)

	if savefile is not None:
		print ("Saving file: %s" % savefile)
		if group_size:
			all_dict = user_dict.copy()	# replace user-dict by all_dict
			user_dict = dict()
			par_index = 1
			while len(all_dict):
				k, v = all_dict.popitem()
				user_dict[k] = v
				if len(user_dict) == group_size:
					par_savefile = '.'.join(savefile.split('.')[:-1]) + '_part' + str(par_index) + '.cPickle'
					par_index += 1
					with open(par_savefile, 'w') as F:
						cPickle.dump(user_dict, F)
					print ("Saveing to %s" % par_savefile)
					user_dict.clear()
			par_savefile = '.'.join(savefile.split('.')[:-1]) + '_part' + str(par_index) + '.cPickle'
			with open(par_savefile, 'w') as F:
				cPickle.dump(user_dict, F)
			print ("Saveing to %s" % par_savefile)
		else:
			with open(savefile, 'w') as F:
				cPickle.dump(user_dict, F)
			print ("Saving to %s" % savefile)

	return(0)

if __name__ == "__main__":
	main(sys.argv[1:])

