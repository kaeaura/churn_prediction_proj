# Jing-Kai Lou (kaeaura@gamil.com)
# This script helps to compact the parsed tell logs

#original tell log
#20030701000000 ．∵╭☆∴． 苑名零 3
#compact tell log
#2003041605 小可兒 網路過客 2-3-2-3-2-2-4-5-5-2-14-9-4-2-2-1-2-2-8-3-2-2-7-5-7-12-7-2-2-3-7-2-8-2

#original say or party log
BEGIN{
	if (unit == "")
		unit = "month"
}

length($1) == 14{

	epoch_time = $1

	if (unit == "month")
		timekey = substr(epoch_time, 1, 6)
	else if (unit == "hour")
		timekey = substr(epoch_time, 1, 10)
	else if
		error_show = 1
		next

	if (NF == 4) {
		con_len = $4
		key = timekey" "$2" "$3
	} else if (NF == 3) {
		con_len = $3
		key = timekey" "$2
	}else{
		next
	}

	if (key in hash)
		hash[key] = hash[key]"-"con_len 
	else
		hash[key] = con_len
}

END {
	if error_show == 1
		print "Var: unit incorrect"
	for (key in hash) {
		print key, hash[key]
	}
}
