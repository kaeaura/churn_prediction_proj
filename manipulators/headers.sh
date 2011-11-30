#!/bin/bash
# Jing-Kai Lou (kaeaura@gmail.com)
# Thu Aug 25 10:29:23 CST 2011
# get the headers of all *.o files in the specific directory
# Usage: sh headers.sh [directory] [output-file-path]

if [ $# -eq 2 ]; then
	if [ -d $1 ]; then
		echo "extracting headers of files in $1"
		find $1 -name "*.o" | xargs head -1 > $2.tmp
		awk '$1 == "==>" && 3 == NF{
			getline fh;
			print $2, fh;
		}' $2.tmp > $2
		rm $2.tmp
	else
		echo "$1 is not a directory"
	fi
else
	echo "need exactly two args"
	echo "usage: sh headers.sh [directory] [output-file-path]"
fi
