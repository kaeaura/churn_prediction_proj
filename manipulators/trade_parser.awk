BEGIN{
	FS = " : "
	OFS = "\t"
	keyWord = "trade"
	cnt = 0
	moneyFlow = 0
}

$0 ~ /trade \[$/ {
	cnt++

	timeStamp = $1
	header = $2
	split(header, headerArray, keyWord)
	senderID = headerArray[1]
	sub("^ +", "", senderID)
	sub(" +$", "", senderID)
	
	sCount = -1
	sMoney = 0
	do 
	{
		if ((getline nextLine) > 0) {
			if (nextLine ~ /^gold [0-9]+$/) {
				split(nextLine, moneyArray, " ")
				moneyFlow = moneyFlow + moneyArray[2]
				sMoney = sMoney + moneyArray[2]
			} else {
				sCount++
			}
		} else {
			break
		}
	}
	while(nextLine !~ /\] with.*/)

	#sub(".*] with", "", nextLine)
	split(nextLine, receiverPatternArry, "] with ")
	split(receiverPatternArry[2], nextArray, " ")
	receiverID = nextArray[1]
	sub("^ +", "", receiverID)
	sub(" +$", "", receiverID)

	rCount = -1
	rMoney = 0
	do 
	{
		if ((getline nextLine) > 0) {
			if (nextLine ~ /^gold [0-9]+$/) {
				split(nextLine, moneyArray, " ")
				moneyFlow = moneyFlow + moneyArray[2]
				rMoney = rMoney + moneyArray[2]
			} else {
				rCount++
			}
		} else {
			break
		}
	}
	while(nextLine !~ /^\]$/)

	print timeStamp, senderID, receiverID, sCount, sMoney, rCount, rMoney
}

END{
	#print "--"
	#print "Total Trade Reocrds:", cnt
	#print "Total Trade Money Flow:", moneyFlow
}
