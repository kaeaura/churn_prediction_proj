# This script helps to chopp the logs into peices according to the date-information
# Jing-Kai Lou (kaeaura@gmail.com) Thu Sep 22 10:36:25 CST 2011
# Usage gawk -f log_chopper.awk -v unit=[year|month|day] -v c=[date_column] [file]

# original date format: yyyymmddHHMMSS
BEGIN{
	print "unit:", unit, "c", c
}

{
	date = $c

	if (date ~ /^[0-9]{8,}$/){	# numberic string with length more than 8

		year	= substr(date, 1, 4)
		month	= substr(date, 5, 2)
		day		= substr(date, 7, 2)

		if (unit == "year") {
			outfile = FILENAME"_"year
		} else if (unit == "month") {
			outfile = FILENAME"_"year"-"month
		} else if (unit == "day") {
			outfile = FILENAME"_"year"-"month"-"day
		} else {
			print "Var: unit error"
			next
		}	

		print $0 > outfile

	} else {
		print "date format error", "::", $c
	}
}
