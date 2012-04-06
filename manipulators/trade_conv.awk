# Jing-Kai Lou (kaeaura@gamil.com)
BEGIN{
	FS = "\t"
	monthAbbrArray["Jan"] = "01"
	monthAbbrArray["Feb"] = "02"
	monthAbbrArray["Mar"] = "03"
	monthAbbrArray["Apr"] = "04"
	monthAbbrArray["May"] = "05"
	monthAbbrArray["Jun"] = "06"
	monthAbbrArray["Jul"] = "07"
	monthAbbrArray["Aug"] = "08"
	monthAbbrArray["Sep"] = "09"
	monthAbbrArray["Oct"] = "10"
	monthAbbrArray["Nov"] = "11"
	monthAbbrArray["Dec"] = "12"
}

{
	timeStamp = $1
	senderID = $2
	receiverID = $3
	senderItemNum = $4
	senderMoney = $5
	receiverItemNum = $6
	receiverMoney = $7

	split(timeStamp, stampArray, " ")
	if (length(stampArray) != 5) 
		next
	year = stampArray[5]
	month = monthAbbrArray[stampArray[2]]
	day = stampArray[3]
	timeTuple = stampArray[4]
	split(timeTuple, tupleArray, ":")
	if (length(tupleArray) != 3) 
		next
	hour = tupleArray[1]
	min = tupleArray[2]
	sec = tupleArray[3]

	newTimeStamp = sprintf("%4d%02d%02d%02d%02d%02d", year, month, day, hour, min, sec)

	if (senderMoney > 0)
		print newTimeStamp, senderID, receiverID, senderMoney
	if (receiverMoney > 0)
		print newTimeStamp, receiverID, senderID, receiverMoney
}
