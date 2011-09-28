# Jing-Kai Lou (kaeaura@gmail.com)
if (file.exists('my.fig.R')) source('my.fig.R')

argv = commandArgs(TRUE)
argc = length(argv)

thread = 300
top_number = 1:9

find_extension <- function(filename) {
	if (class(filename) == "character" && length(filename) == 1) {
		split_filename = strsplit(filename, '.', fixed = T)[[1]]
		if (length(split_filename) > 1) {
			return(split_filename[length(split_filename)])
		}else{
			cat("contains no exe")
			return(NULL)
		}
	}
}

replace_extention <- function(filename, replacing) {
	original_extension = find_extension(filename)
	if (!is.null(original_extension)) {
		return(sub(sprintf('%s$', original_extension), replacing, filename))
	} else {
		return(1)
	}
}

stream_sum <- function(string, s_sep = ":") {
	# 1:2:3 --> 1 + 2 + 3 = 6
	stopifnot (class(string) == "character" && length(string) == 1) 
	return (sapply(strsplit(string, s_sep), function(x) sum(as.integer(x))))
}

to_stream <- function(string, s_sep = ":") {
	# 1:2:3 --> c(1, 2, 3)
	stopifnot (class(string) == "character" && length(string) == 1) 
	return (sapply(strsplit(string, s_sep), function(x) as.integer(x)))
}

stream_sum <- function(string, s_sep = ":") {
	return(sum(to_stream(string, s_sep)))
}

col_names = c('t_stream', 's_stream', 'p_stream', 'f_stream')
col_colors = c('pink', 'white', 'blue', 'green')

for (arg in argv) {
	if (file.exists(arg) && find_extension(arg) == 'csv') {
		df = read.csv(arg, header = T, as.is = T, encoding = 'iso-8859-1')

		if (all(c('account', col_names) %in% names(df))) {
			stream.df = subset(df, select = c('account', col_names))
			stream.df$tc = apply(stream.df, 1, function(x) { sum(sapply(x[-1], stream_sum)) })

			# only fetch the top_number records
			show.df = stream.df[order(stream.df$tc, decreasing = T)[top_number], ]

			# plotting
			if (exists('my.fig')) {
				my.fig(replace_extention(paste('stream', basename(arg), sep='_'), ''), 3, ceiling(length(top_number)/3))
			} else {
				postscript (replace_extention(paste('stream', basename(arg), sep='_'), 'eps'), width = 800, height = 600)
				par(mfrow = c(3, ceiling(length(top_number)/3)))
			}

			for (i in top_number) {
				s.df = subset(show.df[i,], select = setdiff(names(show.df), c('account', 'tc')))
				streams = as.character(s.df)
				streams.mtx = sapply(streams, to_stream)

				if (i == 1) {
					ltext = names(s.df)
				} else {
					ltext = NULL
				}

				barplot(t(streams.mtx), 
						col = col_colors,
						main = sprintf('id: %s; act-freq: top %d', show.df$account[i], i),
						xlab = 'hours in a day',
						ylab = 'act counts',
						names.arg = 0:(nrow(streams.mtx)-1),
						legend.text = ltext,
						density = 24,
						angle = c(45, -45, 45, -45),
						cex.name = 0.6
				)
			}

			if (exists('my.fig')) {
				dev.off()
			} else {
				my.fig.off()
			}

		} else {
			cat(sprintf("No %s column", col_name))
		}
	} else {
		next
	}
}
