#!/bin/bash
# Jing-Kai Lou (kaeaura@gmail.com) Sun Sep  4 13:27:53 CST 2011
# This script extracts the user-id and family-name with earliest time-stamp
# from logs of family channel

# family.parsed format: timestamp family-name user-id len(content)
if [ $# -eq 1 -a -e $1 ]; then
	gawk '
		NF == 4 {
			key = $2" "$3
			if (!(key in family_join) || $1 < family_join[key])
				family_join[key] = $1
		}
		END {
			for (key in family_join)
				print key, family_join[key]
		}
	' $1
fi
