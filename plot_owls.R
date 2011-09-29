# Jing-Kai Lou (kaeaura@gmail.com)
# Wed Sep 28 15:51:39 CST 2011
source('included.R')
if (file.exists('my.fig.R')) source('my.fig.R')

argv = commandArgs(TRUE)
argc = length(argv)

fig_dir = '../fig'
top_number = 1:9

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
			fig_name = paste('stream', basename(arg), sep = '_')
			if (!file.exists(fig_dir)) dir.create(fig_dir)

			if (exists('my.fig')) {
				fig_name = file.path(fig_dir, replace_extention(fig_name, ''))
				my.fig(fig_name, 3, ceiling(length(top_number)/3))
			} else {
				fig_name = file.path(fig_dir, replace_extention(fig_name, '.eps'))
				postscript (fig_name, width = 800, height = 600)
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

			cat(sprintf('fig: %s is done\n', fig_name))

		} else {
			cat(sprintf("No %s column", col_name))
		}
	} else {
		next
	}
}
