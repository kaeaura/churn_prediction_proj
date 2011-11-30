# This script helps to chopp the logs into peices according to the $c-information
# Jing-Kai Lou (kaeaura@gmail.com) Thu Sep 22 10:36:25 CST 2011
# Usage gawk -f log_chopper.awk -v unit=[year|month|day] -v c=[$c_column] [file]

# original $c format: yyyymmddHHMMSS
BEGIN{
	print "unit:", unit, "c", c
}

# numberic string with length more than 8
$c ~ /^[0-9]+$/ {

	if (length($c) >= 4)
		year	= substr($c, 1, 4)
	if (length($c) >= 6)
		month	= substr($c, 5, 2)
	if (length($c) >= 8)
		day		= substr($c, 7, 2)
		
	if (unit == "year" && year != "") {
		outfile = FILENAME"_"year
	} else if (unit == "month" && month != "") {
		outfile = FILENAME"_"year"-"month
	} else if (unit == "day" && day != "") {
		outfile = FILENAME"_"year"-"month"-"day
	} else {
		print "Var: unit error"
		next
	}	

	print $0 > outfile

}
