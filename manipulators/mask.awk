# Jing-Kai Lou (kaeaura@gamil.com)
# Wed Feb  1 17:13:43 CST 2012
BEGIN{
	if (hashTable == "")
		exit
	hashValue = 0
	while ((getline line < hashTable) > 0) {
		hashArray[line] = hashValue
		hashValue++
	}
	if (length(hashArray) == 0) {
		print "No input from hashTable"
		exit
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

