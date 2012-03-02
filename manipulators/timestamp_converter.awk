# Jing-Kai Lou (kaeaura@gamil.com)
# replace the standard timestamp format by a 14-digits number string
#Tue Nov  4 15:09:01 2003 : 哈娜亞 tell 冷漠無情 : 安
#Tue Nov  4 15:09:16 2003 : 哈娜亞 tell 冷漠無情 : 怎又是這個名子
BEGIN{
	FS = " : "
	monthAbbrArray["Jan"] = 1
	monthAbbrArray["Feb"] = 2
	monthAbbrArray["Mar"] = 3
	monthAbbrArray["Apr"] = 4
	monthAbbrArray["May"] = 5
	monthAbbrArray["Jun"] = 6
	monthAbbrArray["Jul"] = 7
	monthAbbrArray["Aug"] = 8
	monthAbbrArray["Sep"] = 9
	monthAbbrArray["Oct"] = 10
	monthAbbrArray["Nov"] = 11
	monthAbbrArray["Dec"] = 12
}

NF > 1{
	standardTimeStamp = $1
	split(standardTimeStamp, timeArray, " ")
	if (length(timeArray) == 5) {
		month_str = timeArray[2]
		if (month_str in monthAbbrArray)
			month_int = monthAbbrArray[month_str]
		else
			next
		day_int = timeArray[3]
		year_int = timeArray[5]

		split(timeArray[4], daytimeArray, ":")
		if (length(daytimeArray) == 3) {
			hour_int = daytimeArray[1]
			min_int = daytimeArray[2]
			sec_int = daytimeArray[3]
		} else {
			next
		}
		timestamp = sprintf("%4d%02d%02d%02d%02d%02d", year_int, month_int, day_int, hour_int, min_int, sec_int)
		#print timestamp
		restComps = timestamp
		for (nf = 2; nf <= NF; nf++) {
			restComps = restComps""FS""$nf
		}
		print restComps
	}
}
