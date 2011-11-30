# Jing-Kai Lou (kaeaura@gamil.com)
# Wed Sep 28 15:50:40 CST 2011

# contents =============================================================================
# script for generation the table describing the fairyland dataset 
#
# associated files
# plot_eve.R:
# |	-- library
# |	-- read input
# |	-- plot par. settings
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
#source('my.fig.R')
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
member_infile = '../exp/members.csv'

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
	exit()
}

data.df = data.frame()
labels = NULL

for (infile_index in 1:length(infiles)) {
	infile = infiles[infile_index]
	read.df = read.csv(infile, header = T, as.is = T, encoding = 'iso-8859-1')

	if ('label' %in% names(read.df)) {
		label = unique(as.character(read.df$label))
	} else {
		label = toupper(substring(basename(infile), 1, 3))
		read.df$label = label
	}

	labels = c(labels, label)

	if (infile_index == 1) {
		data.df = read.df
	} else {
		data.df = rbind(data.df, read.df)
	}
}

# post-process
if (enable_post_process) {
	print ('post-processing')
	stream_to_value <- function(s) {
		sapply(strsplit(s, ':'), function(x) sum(as.integer(x)))
	}

	if (file.exists(member_infile)) {
		member.df = read.csv(member_infile)
		pg = as.character(member.df$p_gender)
		member.df$p_gender = factor(pg, level = c('男', '女'), labels = c('Male', 'Female'))
	} else {
		cat(sprintf('file: %s does not exist!\n', member_infile))
	}

	data.df <- within(
			data.df, {
				gender = factor(data.df$gender, labels = c('Male', 'Female'))
				race = factor(data.df$race, labels = c('Human', 'Elf', 'Dwarf'))
				label = as.factor(data.df$label)
				family_joined = data.df$familyNum > 0
				ocoef = apply	(
									subset(data.df, select=c(ts_stream, tl_stream, s_stream, p_stream, f_stream)), 
									1, 
									function(x) {
										sum(sapply(x, get_owl_coef)) / 4
									}
								)
				t_sum = stream_to_value(data.df$ts_stream)
				l_sum = stream_to_value(data.df$tl_stream)
				s_sum = stream_to_value(data.df$s_stream)
				p_sum = stream_to_value(data.df$p_stream)
				f_sum = stream_to_value(data.df$f_stream)
				dmonth = substr(data.df$ddate, 1, 6)
				emonth = substr(data.df$edate, 1, 6)
				rm(ts_stream, tl_stream, s_stream, p_stream, f_stream)
			}
		)

	# rename colnames
	data.df = rename(data.df, c(cid = "c_id", friendNum = "friend_num", familyRank = "family_pos", familyNum = "family_num"))


	# newly add features
	data.df = transform	(
							data.df, 
							all_sum = t_sum + l_sum + s_sum + p_sum + f_sum, 
							level_speed = level / sub_len, 
							recip = l_sum / (t_sum + l_sum)
						)

	# merge the member data.frame
	data.df = merge(data.df, member.df, by = 'account')

	# noise filter
	data.df = subset(data.df, sub_len > 3 & t_sum + l_sum + s_sum + p_sum + f_sum > 10)

	# unique cid
	data.df = ddply	(data.df, 
						.(paste(account, c_id, sep = ':')), 
						function(x) { 
							if(nrow(x) > 1) {
								x[which.max(x$all_sum),]
							}else{
								x
							}
						}
					)

	# insert the realm information
	data.df = ddply(data.df, .(label), transform, realm_population = length(label), realm_dmonth = min(dmonth), realm_emonth = max(emonth))

	# first avatar
	first.avatar = ddply(data.df, .(account), function(x) x$c_id[which.min(x$ddate)])
	first.avatar = rename(first.avatar, c(V1 = 'c_id'))
	data.df$is_first_avatar = paste(data.df$account, data.df$c_id) %in% paste(first.avatar$account, first.avatar$c_id)
	rm(first.avatar)

	# first account
	first.account = ddply(data.df, .(m_id), function(x) x$account[which.min(x$ddate)])
	first.account = rename(first.account, c(V1 = 'account'))
	data.df$is_first.account = paste(data.df$account, data.df$account) %in% paste(first.account$account, first.account$account)
	rm(first.account)

	# type of account
	data.df = ddply	(
						data.df, 
						.(account), 
						function(x) { 
										if (all(x$gender == x$p_gender)) { 
											transform(x, a_type = 'order')
										} else if (all(x$gender != x$p_gender)) {
											transform(x, a_type = 'disorder')
										} else {
											transform(x, a_type = 'hybrid')
										}
									}
					)

	# type of member
	data.df = ddply	(
						data.df, 
						.(m_id), 
						function(x) { 
										if (all(x$gender == x$p_gender)) { 
											transform(x, m_type = 'order')
										} else if (all(x$gender != x$p_gender)) {
											transform(x, m_type = 'disorder')
										} else {
											transform(x, m_type = 'hybrid')
										}
									}
					)

	write.csv(data.df, file = '../exp/temp.txt', row.names = F, quote = F)
	print ('done')
}

if (any(names(data.df) == 'gender') && !is.factor(data.df$gender)) data.df$gender = as.factor(data.df$gender)
if (any(names(data.df) == 'race') && !is.factor(data.df$race)) data.df$race = as.factor(data.df$race)
if (any(names(data.df) == 'family_pos') && !is.factor(data.df$family_pos)) data.df$family_pos = as.factor(data.df$family_pos)

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

global_months = sort(unique(c(data.df$dmonth, data.df$emonth)))

