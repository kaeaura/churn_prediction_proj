# Jing-Kai Lou (kaeaura@gamil.com)
# Wed Sep 28 15:50:40 CST 2011

# contents =============================================================================
# script for analyzing and plotting figures
#
# associated files
# plot_eve.R:
# |	-- library
# |	-- read input
# |	-- plot par. settings
# |
# |	(section 1) terms: population, gender, race, level, family, observation_lenght
# |- plot_eve_population.R : population
# |- plot_eve_gender.R : gender
# |- plot_eve_race.R : race
# |- plot_eve_gender-in-race: gender + race
# |- plot_eve_level.R : level
# |- plot_eve_level-in-gender: level + gender
# |- plot_eve_level-in-race: level + race
# |- ... (to be extanded)
# |
# |	(section 2) owl, addiction (test if mean significatn differencet)
# |- plot_eve_owls : gender + owl
# |- plot_eve_gender-in-owls : gender + owl
# |- plot_eve_gender-in-owls : gender + owl
# |- ... (to be extanded)
#
# contents
# - library
# - functions
# - pre parameter settings
# - argv for input files
# - post parameter settings
# ==========================================================================================

# library settings =============================================================================
cat('--loading-library\n')
require('ggplot2')
require('reshape')
source('my.fig.R')
source('included.R')

# functions =============================================================================
cat('load-funcs\n')
# get owl-coefficient
get_owl_coef <- function(x, sep = ':') {
	night_period = c(1:5, 23:24)
	sapply	(
				strsplit(x, sep), 
				function(x) {
					nx = as.integer(x)
					if (length(nx) >= 24) {
						return(ifelse(sum(nx), sum(nx[night_period]) / sum(nx), 0))
					}
				}
	)
}

# pre-parameter settings =============================================================================
cat('pre-par\n')
fig_dir = '../fig'
if (!file.exists(fig_dir)) dir.create(fig_dir)
enable_post_process = F
default_infile = '../exp/temp.txt'

options(digits = 4)

max_df = 60 - 1
fig_num = 1

gender_labels = c('Male', 'Female')
gender_colors = c('royalblue', 'lightpink')
gender_lty = c(2, 1)
gender_pch = c(18, 4)

race_labels = c('Human', 'Elf', 'Dwarf')
race_colors = c('royalblue', 'lightgreen', 'darkgoldenrod1')
race_lty = c(1, 2, 4)
race_pch = c(18, 4, 2)

# argv for input files =============================================================================
# testing argv: ../exp/alice_activity.csv
# Usage: Rscript --vanilla plot_eve.R alice_activity.csv
cat('--parsing-argv\n')
argv = commandArgs(TRUE)
argc = length(argv)

if (argc) {
	infiles = argv[file.exists(argv)]
	infiles = infiles[order(file.info(infiles)$size)]
} else if (!argc && file.exists(default_infile)) {
	infiles = default_infile
} else {
	cat('no proper input')
	exist()
}

data.df = data.frame()
labels = NULL

for (infile_index in 1:length(infiles)) {
	infile = infiles[infile_index]
	read.df = read.csv(infile, header = T, encoding = 'iso-8859-1')

	if ('label' %in% names(read.df)) {
		label = unique(as.character(read.df$label))
	} else {
		label = toupper(substring(basename(infile), 1, 3))
		read.df$label = label
	}

	labels = c(labels, label)

	if ( infile_index == 1 ) {
		data.df = read.df
	} else {
		data.df = rbind(data.df, read.df)
	}
}

# NOTE: only the subscription length greater than 10 days
data.df = subset(data.df, sub_len > 10)

# post-process
if (enable_post_process) {
	print ('post-processing')
	data.df <- within(
			data.df, {
				gender = factor(data.df$gender, labels = c('Male', 'Female'))
				race = factor(data.df$race, labels = c('Human', 'Elf', 'Dwarf'))
				label = as.factor(data.df$label)
				ocoef = apply	(
									subset(data.df, select=c(t_stream, s_stream, p_stream, f_stream)), 
									1, 
									function(x) {
										sum(sapply(x, get_owl_coef)) / 4
									}
								)
				dmonth = substr(data.df$ddate, 1, 6)
				emonth = substr(data.df$edate, 1, 6)
				rm(cid, ddate, edate, t_stream, s_stream, p_stream, f_stream)
			}
		)
	print ('done')
	write.csv(data.df, file = '../exp/temp.txt', row.names = F, quote = F)
}

# post-parameter settings =============================================================================
cat('--post-par\n')
labels = unique(as.character(data.df$label))
labels_color = rainbow(length(labels))
labels_pch = 1:length(labels)

labels_len = by	(
					data.df, 
					data.df$label, 
					function(x) {
						uniq_months = unique(union(x$dmonth, x$emonth))
						return(length(uniq_months))
					}
				)

#global_months = sort(unique(substr(c(data.df$ddate, data.df$edate), 1, 6)))
global_months = sort(unique(c(data.df$dmonth, data.df$emonth)))

