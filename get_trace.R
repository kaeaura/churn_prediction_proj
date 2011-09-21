# Jing-Kai Lou (kaeaura@gmail.com) Tue Aug 30 13:46:20 CST 2011 
argv = commandArgs(TRUE)
argc = length(argv)

stopifnot(file.exists(argv[1]) && argc == 2)
tfile = argv[1]
cdir = argv[2]

trace_paths = scan(tfile, what = character())
trace_paths = trace_paths[file.exists(trace_paths)]

# path operation
if (!file.exists(cdir)) dir.create(cdir)
outfile = file.path(cdir, basename(tfile))
if (file.exists(outfile)) file.remove(outfile)

for (trace_path in trace_paths){
	file.append(outfile, trace_path)
}
