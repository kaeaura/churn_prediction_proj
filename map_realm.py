# Jing-Kai Lou (kaeaura@gmail.com) Wed Aug 31 14:40:17 CST 2011 import os
import os
import sys
import csv
import getopt

realm_map_filename = "/home/kae/trace/fairyland/src/realm.map.csv"

def main(argv):
	is_shown = True
	q_date = None
	q_machine = None
	infile = None
	spliter = ","

	try:
		opts, args = getopt.getopt(argv, "hqd:m:f:F:", ["help"])
	except getopt.GetoptError:
		print "The given arguments incorrect"
		sys.exit(2)

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print ("----------------------")
			print ("Usage: python map_realm.py -d [date] -m [machine_name]")
			print ("")
			print ("\t-h, --help: show the usage")
			print ("\t-q: quiet mode")
			print ("\t-d ...: log date")
			print ("\t-m ...: log machine")
			print ("\t-f ...: read-file mode; lines in file = 'machine date'")
			print ("\t-F ...: change the spliter in read-file mode. default is ','")
			print ("----------------------")
			sys.exit()
		elif opt in ("-d"):
			q_date = arg
		elif opt in ("-m"):
			q_machine = arg
		elif opt in ("-q"):
			is_shown = False
		elif opt in ("-f"):
			infile = arg
		elif opt in ("-F"):
			spliter = arg
		else:
			print "The given arguments incorrect"
			sys.exit(2)

	if not os.path.exists(realm_map_filename):
		print ("The mapping table doesn't exists")
		print ("Make sure that maping table is in %s" % realm_map_filename)
		sys.exit(2)

	mapReader = csv.reader(open(realm_map_filename, 'rb'), delimiter=' ')

	# build dictionary
	line_num = 0
	q_dict = dict()
	for line in mapReader:
		line_num += 1
		if line_num == 1:
			machines = line
		else:
			date = line[0]
			realms = line[1:]
			q_dict[date] = dict(zip(machines, realms))

	def shift_qDate(q_date):
		# shift q_date
		q_dates = q_dict.keys()
		q_dates.sort()
		if q_date not in q_dates:
			try:
				mq_date = q_dates[len(filter(lambda x : int(q_date) >= int(x), q_dates)) - 1]
			except IndexError:
				print 'queried date is out of range'
				sys.exit(2)
		else:
			mq_date = q_date
		return(mq_date)

	# output
	if infile is not None:
		try:
			qReader = csv.reader( open(infile, 'rb'), delimiter = spliter)
			for query in qReader:
				if len(query) == 2:
					q_machine, q_date = query
					mq_date = shift_qDate(q_date)
					print (q_dict[mq_date][q_machine])
				else:
					continue
		except IOError:
			print ("Input file does not exist")
			sys.exit(2)
	elif q_date is not None and q_machinea is not None:
		if is_shown:
			print (q_date)
			print (q_dates)
			print (mq_date)
			print (q_dict[date])
			print (q_machine)
		print (q_dict[mq_date][q_machine])
	else:
		print ("Need for arguments")
		sys.exit(2)

if __name__ == "__main__":
	main(sys.argv[1:])
