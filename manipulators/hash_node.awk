# Jing-Kai Lou (kaeaura@gamil.com)
# Wed Feb  1 16:36:04 CST 2012
# Hash the cid string to int

BEGIN{
	hashIndex = 0
}

NF == 1{
	if (!($1 in hashArray)) {
		if (prefix == "")
			hashArray[$1] = hashIndex
		else
			hashArray[$1] = prefix""hashIndex
		hashIndex = hashIndex + 1
	}
}

END {
	for (hashKey in hashArray) 
		print hashArray[hashKey], hashKey
}

