BEGIN {FS = ","; OFS = "," }

{ 
	trace_path = $1 
	split(trace_path, trace_path_patterns, "/") 
	key = trace_path_patterns[5] 
	split(key, q_patterns, "_data") 
	if (length(q_patterns[2]) == 6){
		q_patterns[2] = "20"q_patterns[2]
	}
	#CMD = "python map_realm.py -q -m "q_patterns[1]" -d "q_patterns[2] 
	#CMD | getline realm 
	#close(CMD) 
	#print realm, $1 
	print q_patterns[1], q_patterns[2]
}
