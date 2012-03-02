# Jing-Kai Lou (kaeaura@gamil.com)
# Fri Jan 13 11:49:21 CST 2012

# reading the family channel, and inferring the familyship at time
# Usage: 
# awk -f get_family.awk -v unit="month" $targetFile > $resultFile

function Unique (string) {
	for (i in xArray)
		delete xArray[i]
	for (i in kArray)
		delete kArray[i]
	split(string, xArray, ",")
	for (x in xArray){
		if (xArray[x] != "")
			kArray[xArray[x]]++
	}
	returnString = ""
	for (k in kArray)
		returnString = returnString k ","
	return(returnString)
}

BEGIN{
	if (unit == "")
		unit = "month"
}

length($1) == 14 && NF == 4{

	epochTime = $1
	familyName = $2
	cid = $3

	if (unit == "month") {
		compactedTime = substr(epochTime, 1, 6)
	} else if (unit == "day") {
		compactedTime = substr(epochTime, 1, 8)
	} else if (unit == "hour") {
		compactedTime = substr(epochTime, 1, 10)
	} else {
		errorShow = 1
		errorLineNumber = errorLineNumber $NR ","
		next
	}

	queryKey = cid" "familyName
	appearArray[queryKey] = appearArray[queryKey] compactedTime ","
}

END{
	for (queryKey in appearArray) {
		split(queryKey, qArray, " ")
		appearDates = Unique(appearArray[queryKey])
		split(appearDates, appearDateArray, ",")
		for (aIndex in appearDateArray) {
			if (appearDateArray[aIndex] != "")
				print appearDateArray[aIndex], qArray[1], qArray[2]
		}
	}
}
