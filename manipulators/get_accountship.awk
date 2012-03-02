# Jing-Kai Lou (kaeaura@gamil.com)
# Tue Feb 14 11:25:06 CST 2012

BEGIN{
	FS = ","
	for (x in accountArray)
		delete accountArray[x]
}

NF == 11 {
	is_deleted = 0
	path = $2
	account = $4
	cid = $5
	char_gender = $6
	char_race = $7

	# test if this character deleted
	split(path, pathArray, "/")
	for (i = 1; i <= length(pathArray); i++) {
		if (pathArray[i] ~ "deleted") {
			is_deleted = 1
			break
		}
	}

	if (!(cid in accountArray))
		accountArray[cid] = sprintf("%s %s %s", account, char_gender, char_race)
}

END{
	for (cid in accountArray)
		print cid, accountArray[cid]
}
