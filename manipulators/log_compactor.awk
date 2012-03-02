# Jing-Kai Lou (kaeaura@gamil.com)
# This script helps to compact the parsed tell logs

#original tell log
#20030701000000 ．∵╭☆∴． 苑名零 3
#compact tell log
#2003041605 小可兒 網路過客 2-3-2-3-2-2-4-5-5-2-14-9-4-2-2-1-2-2-8-3-2-2-7-5-7-12-7-2-2-3-7-2-8-2

function CountWeight (weightString) {
	for (wIndex in weightArray)
		delete weightArray[wIndex]
	split(weightString, weightArray, "-")
	return length(weightArray)
}

function SumWeight (weightString) {
	for (wIndex in weightArray)
		delete weightArray[wIndex]
	split(weightString, weightArray, "-")
	weightSum = 0
	for (wIndex in weightArray) {
		weightSum = weightSum + weightArray[wIndex]
	}
	return weightSum
}

#original say or party log
BEGIN{
	if (unit == "")
		unit = "month"
}

length($1) == 14{

	epochTime = $1

	if (unit == "month") {
		timekey = substr(epochTime, 1, 6)
	} else if (unit == "day") {
		timekey = substr(epochTime, 1, 8)
	} else if (unit == "hour") {
		timekey = substr(epochTime, 1, 10)
	} else {
		error_show = 1
		errorLineArray[NR] = 1
		next
	}

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
	if (error_show == 1 && length(errorLineArray) > 0) {
		print "Var: unit incorrect"
		for (errorLineNumber in errorLineArray)
			print "Error cuased by line:", errorLineNumber
	}
	for (key in hash) {
		print key, CountWeight(hash[key]), SumWeight(hash[key])
	}
}
