#!/bin/bash
# Usage: sh sort_profile.sh alice_user.csv > alice_user_sorted.csv

awk -F "," '{
	path = $2
	split(path, pathArry, "/")
	split(pathArry[5], patternArray, "_data")
	if (length(patternArray) == 2)
		date = patternArray[2]
	print date, $0
}' $1 | sort | awk '{
	line = ""
	for (nf = 2; nf <= NF; nf++)
		line = line","$(nf)
	sub(",", "", line)
	print line
}'
