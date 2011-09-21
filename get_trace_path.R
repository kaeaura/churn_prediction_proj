# realm.map.csv is provided by Lager
argv = commandArgs(TRUE)
argc = length(argv)
realm_opt.opt = '-r'
realm_opt.index = grep(realm_opt.opt, argv, fixed = TRUE)

if (argc >= realm_opt.index){
	realm_opt.arg = argv[realm_opt.index + 1]
}else{
	print ('please input the realm')
	q(status = 1)
}

outdir = 'trace_path'
map.df = read.table('realm.map.csv', header=T, sep=' ', row.names=1, as.is=T)

#realms = c('candy')
realms = realm_opt.arg
channels = c('tell', 'family', 'say', 'party')
chat_trace_dir = '/home/kae/trace/fairyland/trace/chat'
chat_logs.list = list()

cat(sprintf('searching the %s realm path and write to folder %s\n', realms, outdir))

for (realm in realms){
	for (channel in channels) {
		cat(sprintf('\tstart collecting trace path of data (realm: %s, channel: %s)\n', realm, channel))

		selected_logs = NULL
		chat_logs = list.files(	
						chat_trace_dir, 
						sprintf('^%s\\.[a-z]+[1-9]*\\.[0-9]+$', channel), 
						full.names=T, 
						recursive=T
					)

		chat_logs.server 	= sapply(strsplit(basename(chat_logs), '.', fixed=T), function(x) x[2])
		chat_logs.date 		= sapply(strsplit(basename(chat_logs), '.', fixed=T), function(x) x[3])
		chat_logs.dateslot 	= findInterval(
								as.numeric(paste('20', chat_logs.date, sep='')), 
								as.numeric(row.names(map.df))
							)

		query.mtx = matrix(c(chat_logs.dateslot, chat_logs.server, chat_logs), nrow = 3, byrow = T)
		valid_indices = (chat_logs.server %in% names(map.df)) & (chat_logs.dateslot %in% 1:nrow(map.df))
		query.mtx = query.mtx[,valid_indices]

		infiles = unlist(
					apply(query.mtx, 2, function(qr) {
						if (map.df[as.numeric(qr[1]), qr[2]] == realm){
							qr[3]
						}
					})
				  )

		if(!file.exists(outdir)) dir.create(outdir)

		write(file = file.path(outdir, sprintf('%s_%s', realm, channel)), infiles, ncolumns = 1)
	}
}

cat ('done\n')
