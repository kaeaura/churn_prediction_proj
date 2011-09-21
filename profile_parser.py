# Jing-Kai Lou (kaeaura@gmail.com) Thu Aug 25 11:34:51 CST 2011
import os
import re
import sys
import codecs
import getopt

def main(argv):
	input_file = ""
	is_shown = True
	is_written = False
	log_file = "profile_parser.log"

	try:
		opts, args = getopt.getopt(argv, "hqi:o:", ["help"])
	except getopt.GetoptError:
		print "The given arguments incorrect"
		sys.exist(2)

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print ("----------------------")
			print ("Usage: python profile_parser.py")
			print ("")
			print ("\t-h, --help: show the usage")
			print ("\t-q: quiet mode")
			print ("\t-i ...: input profile")
			print ("\t-o ...: output profile")
			print ("----------------------")
			sys.exit()
		elif opt in ("-i"):
			input_file = arg
		elif opt in ("-o"):
			output_file = arg
			is_written = True
		elif opt in ("-q"):
			is_shown = False
		else:
			print "The given arguments incorrect"
			sys.exit(2)

	if not os.path.exists(input_file):
		print ("The input-file: %s doesn't exist" % input_file)

	# parsing the profile
	try:
		with codecs.open(input_file, "r", "big5") as F:
			header = F.readline().strip()
			if header != "#/obj/user.c":
				if is_shown:
					print ("(header error) The input format incorrect")
					print ("header: %s" % header)
				with open(log_file, "a") as W:
					W.write("%s header_incorrect\n" % input_file)
					sys.exit(2)

			for line in F:
				line_tokens = line.strip().split(" ")
				if line_tokens[0] == "idata":
					# check if the number of line tokens is 2
					if len(line_tokens) != 2:
						merged_line_tokens = " ".join(line_tokens[1:])
						q_patterns = '\"[^\"]*\"'
						q_replacing_token = "KAEQTOKEN"
						replaced_tokens = re.findall(q_patterns, merged_line_tokens)
						data_field = re.sub(q_patterns, q_replacing_token, " ".join(line_tokens[1:]))
					else:
						data_field = line_tokens[1]

					if is_shown:
						print ("idata data-field: %s" % data_field)

					b_patterns = '\(\{[^\)\}]*\}\)'
					b_replacing_token = "KAEBTOKEN"
					q_patterns = '\"[^\"]*\"'
					q_replacing_token = "KAEQTOKEN"
					data_field = re.sub('^\(\{', '', data_field)
					data_field = re.sub('\}\)$', '', data_field)
					merged_data_field = re.sub(b_patterns, b_replacing_token, data_field)
					q_replaced_tokens = re.findall(q_patterns, merged_data_field)
					merged_data_field = re.sub(q_patterns, q_replacing_token, merged_data_field)
					data_tokens = merged_data_field.split(',')

					if is_shown:
						print ("")
						print ("q_replaced_tokens")
						print (",".join(q_replaced_tokens))
						print ("")
						print ("idata data-tokens:\n%s" % merged_data_field)
						print ("idata data-token number: %d" % len(data_tokens))

					def qtoken_recovery(index):
						qIndex = len(filter(lambda x: x == q_replacing_token, data_tokens[:index]))
						try:
							return (q_replaced_tokens[qIndex])
						except IndexError:
							with open(log_file, "a") as W:
								W.write("%s qRecovery_incorrect" % input_file)

					data_token_number = 62
					if len(data_tokens) == data_token_number:
						# fetching the profile info.
						char_id = data_tokens[0]
						if char_id == q_replacing_token:
							char_id = qtoken_recovery(0)
						char_level = data_tokens[5]
						char_race = data_tokens[33]
						char_gender = data_tokens[34]
						char_account = data_tokens[41]
						if char_account == q_replacing_token:
							char_account = qtoken_recovery(41)
						char_profession = data_tokens[48]
						char_class = data_tokens[49]
						char_file = data_tokens[57]
						if char_file == q_replacing_token:
							char_file = qtoken_recovery(57)
						char_family = data_tokens[60]
						if char_family == q_replacing_token:
							char_family = qtoken_recovery(60)

						try:
							int(char_race)
							int(char_level)
							int(char_gender)
						except ValueError:
							with open(log_file, "a") as W:
								W.write("%s race_level_or_gender_may_not_be_number\n" % input_file)

						if is_shown:
							print ("id: %s" % char_id)
							print ("level: %s" % char_level)
							print ("race: %s" % char_race)
							print ("gender: %s" % char_gender)
							print ("account: %s" % char_account)
							print ("profession: %s" % char_profession)
							print ("class: %s" % char_class)
							print ("file: %s" % char_file)
							print ("family: %s" % char_family)
					else:
						if is_shown:
							print ("Warning! The format may incorrect.")
							print ("idata-token number shall be %d instead of %d" % (data_token_number, len(data_tokens)))
						with open(log_file, "a") as W:
							W.write("%s parsed_items_number_is_not_62\n" % input_file)

				elif line_tokens[0] == "dbase":
					data_field = " ".join(line_tokens[1:])
					char_fRank_field = re.findall('\"f_rank\":[^,]*', data_field)
					char_fRank = map(lambda x: x.split(':')[1], char_fRank_field) if len(char_fRank_field) else ['0']
					char_fRank = ';'.join(char_fRank)
					if is_shown:
						print ("rank: %s" % char_fRank)

					char_friend_field = re.findall('(?<=\"friend\":\(\[)[^\]\)]*\]\)', data_field)
					char_friend_token = re.sub('\]\)', '', char_friend_field[0]) if len(char_friend_field) else ""
					if char_friend_token == "":
						char_friends = ""
					else:
						char_friend_token_list = filter(lambda x: x != "", char_friend_token.split(','))
						char_friends = ';'.join(map(lambda x: x.split(':')[0], char_friend_token_list))
					if is_shown:
						print (char_friends)

				else:
					continue

		# format the output
		try:
			idata_oput = [char_file, char_account, char_id, char_gender, char_race, char_level, char_family]
			dbase_oput = [char_fRank, char_friends]
			format_output = map(lambda x: re.sub('\"', '', x), [input_file]+idata_oput+dbase_oput)
		except NameError:
			with open(log_file, "a") as W:
				W.write("%s some_parsed_items_are_lost\n" % input_file)
				W.write("%s some_parsed_items_are_lost" % input_file)

		# writing the prased result
		if is_written:
			output_dir = os.path.dirname(output_file) if os.path.dirname(output_file) != "" else "."
			if not os.path.exists(output_dir):
				os.makedirs(output_dir)
			with codecs.open(output_file, 'a', 'utf-8') as F:
				F.write("%s\n" % ",".join(format_output))
		else:
			print("%s" % ",".join(format_output))

	except UnicodeError:
		with open(log_file, "a") as W:
			W.write("%s unicodeerror_incorrect\n" % input_file)

if __name__ == "__main__":
	main(sys.argv[1:])

