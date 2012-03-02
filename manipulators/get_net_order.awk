
NF >= 2{
	if (!($3 in nodeArray))
		nodeArray[$1] = 1
	if (!($2 in nodeArray))
		nodeArray[$2] = 1
}

END {
	order = 0
	for (nodeIndex in nodeArray) {
		order++
	}
	print FILENAME, order, "vertices"
}
