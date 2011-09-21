#!/bin/bash
# Jing-Kai Lou (kaeaura@gmail.com) Thu Sep  1 14:36:24 CST 2011 
# usage sh map_profile [parsed_profile_file]
# add an additioanl column "realm" which is decided according to the file realm.map.csv

if [ $# -eq 1 -a -e $1 ]; then
	# extract the date and machine
	gawk '
	BEGIN {FS = ","; OFS = "," }
	{ 
		trace_path = $1 
		split(trace_path, trace_path_patterns, "/") 
		key = trace_path_patterns[5] 
		split(key, q_patterns, "_data") 
		if (length(q_patterns[2]) == 6){
			q_patterns[2] = "20"q_patterns[2]
		}
		print q_patterns[1], q_patterns[2]
	}' $1 > $1.qterms

	# get the result
	python /home/kae/trace/fairyland/src/map_realm.py -f $1.qterms > $1.qresults

	# merge the result
	paste -d "," $1.qresults $1 > $1.addRealm

	# clean the temporal files
	rm -f $1.qterms $1.qresults
else
	echo "aaa"
	#echo "Usage sh map_profile [parsed_profile_file]"
fi
