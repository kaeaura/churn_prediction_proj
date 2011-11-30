#!/bin/bash
# Jing-Kai Lou (kaeaura@gmail.com) Thu Aug 25 16:30:36 CST 2011
# Usage: sh profile_parser_batch.sh

trace_path="/home/kae/trace/fairyland/"
infile=$trace_path"/data/$1"
outfile=$trace_path"/data/parsed_$1"
parser=$trace_path"/src/profile_parser.py"

if [ -f $infile -a -e $parser ]; then
	gawk -v p=$parser -v o=$outfile -v h=$trace_path '2 == NF{
		#sub("../", "", $1);
		path = h""$1;
		CMD = "python "p" -q -i "$1" -o "o
		print CMD;
		system(CMD); 
	}' $infile 
else
	echo "Usage: sh profile_parser_batch.sh"
	echo "$infile or $parser does not exist"
fi
