# Jing-Kai Lou (kaeaura@gamil.com)
# Fri Feb  3 17:45:07 CST 2012
BEGIN{
	if (hashTable == "")
		exit
	hashValue = 0
	while ((getline line < hashTable) > 0) {
		hashArray[hashValue] = line
		hashValue++
	}
}

{
	if ($(maskCol) in hashArray) {
		outputString = ""
		for (nf = 1; nf <= NF; nf++) {
			if (nf == maskCol)
				outputString = outputString" "hashArray[$(maskCol)]
			else
				outputString = outputString" "$nf
		}
		sub("^ ", "", outputString)
		print outputString
	} 
}

