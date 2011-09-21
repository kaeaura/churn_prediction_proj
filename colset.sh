# Jing-Kai Lou (kaeaura@gmail.com) Mon Sep  5 11:15:12 CST 2011
#!/bin/bash
# This script get the set of i-th column
USAGE="Usage: colset.sh [col_num] file"

if [ $# -eq 2 ]; then
	COLNUM=$1
	FILE=$2
	if [ $COLNUM ]; then
		if [ ! $(echo "$COLNUM" | grep -E "^[0-9]+$") ]; then
			echo $COLNUM is not a valid integer.
			exit 1
		else
			if ! [ $COLNUM -ge 0 ] || ! [ $COLNUM -le 100 ]; then
				echo $COLNUM is an invalid value. Range is [0-100]
				exit 1
			fi
		fi
	fi
	test -e $FILE && gawk -v c=${COLNUM} '{ print $c }' ${FILE} | sort | uniq || echo "file doesnt exist"
else
	echo "$USAGE"
	exit 1
fi
