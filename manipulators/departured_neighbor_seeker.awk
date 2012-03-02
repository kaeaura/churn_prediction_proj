# Jing-Kai Lou (kaeaura@gamil.com)
# read the life table 
# targeting the leader node n who leave at time t 
# judge the neighbors of a node in its last period (d = 30 days)
# check if the neighbors also left month later than time t = 40 days

function UniqueLength (string) {
	for (i in xArray)
		delete xArray[i]
	for (i in kArray)
		delete kArray[i]
	split(string, xArray, ",")
	for (x in xArray){
		if (xArray[x] != "")
			kArray[xArray[x]]++
	}
	return(length(kArray))
}

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

function ToEpoch (string) {
	if (length(string) == 8)
		cusString = sprintf("%s %s %s 0 0 0", substr(string, 1, 4), substr(string, 5, 2), substr(string, 7, 2))
	else
		print "Error in ToEpoch function, the length of input string should be 8"
	return(mktime(cusString))
}

BEGIN{
	isDetaild = 0
	kDayTime = 86400
	lastPeriodLength = kDayTime * 30
	dampPeriodLength = kDayTime * 40

	while((getline line < life_file) > 0) {
		split(line, lifeArray, " ")
		key = lifeArray[1]
		firstArray[key] = lifeArray[3]
		lastArray[key] = lifeArray[4]
		if (lifeArray[6] == "True") {
			leaderArray[key] = 1
		}
	}
	#print "== start of test =="
	#T = "a,a,b,c,a"
	#print T
	#print Unique(T)
	#print UniqueLength(T)
	#print "== end of test =="
	if (!isDetaild)
		print "coreNode", "lastCount", "departCount", "quitterCount", "leaderCount", "departLeaderCount"
}

{
	time = $1

	for (id_index = 2; id_index <= 3; id_index++) {
		id = $(id_index)
		if (id_index == 2)
			rid = $(id_index + 1)
		else
			rid = $(id_index - 1)

		# search for the neighbors who contact to the leader in the last period
		# 	1. id is leader, 
		#	2. the contact time is in the last month of leader's leave; 
		timeDiff = ToEpoch(lastArray[id]) - ToEpoch(time)
		if (id in leaderArray && timeDiff <= lastPeriodLength ) {
			lastNeiArray[id] = lastNeiArray[id] rid ","
		}
	}
}

END {
	for (coreNode in lastNeiArray) {
		uniqNeisString = Unique(lastNeiArray[coreNode])
		split(uniqNeisString, uniqNeisArray, ",")

		# for short
		#	the number of last neighbors, 
		#	number of departed neighbors, 
		#	number of quitter neighbors, 
		#	and number of leader neighbors

		# for detailed
		if (isDetaild) {
			print "---------------------------------"
			print coreNode":"uniqNeisString
			print coreNode, "(", firstArray[coreNode], lastArray[coreNode], ")"
			print "+++"
		}

		lastCount = 0
		departCount = 0
		quitterCount = 0
		leaderCount = 0
		departLeaderCount = 0

		for (uNeiIndex in uniqNeisArray){
			uNeiID = uniqNeisArray[uNeiIndex]

			if (uNeiID != ""){
				lastCount++
				neiLastEpoch = ToEpoch(lastArray[uNeiID])
				coreLastEpoch = ToEpoch(lastArray[coreNode])

				if (neiLastEpoch < coreLastEpoch)
					quitterCount++
				if (leaderArray[uNeiID])
					leaderCount++

				if (neiLastEpoch >= coreLastEpoch && neiLastEpoch - coreLastEpoch <= dampPeriodLength) {
					isDeparted = "True"
					departCount++
					if (leaderArray[uNeiID])
						departLeaderCount++
				} else {
					isDeparted = "False"
				}

				if (isDetaild)
					print uNeiID, "("firstArray[uNeiID]"--"lastArray[uNeiID]")", isDeparted
			}
		}

		if (isDetaild) {
			print "+++"
			print "lastCount:", lastCount, "departCount:", departCount, "quitterCount:", quitterCount, "leaderCount:", leaderCount, "departLeaderCount:", departLeaderCount
		} else {
			print coreNode, lastCount, departCount, quitterCount, leaderCount, departLeaderCount
		}
	}
}
