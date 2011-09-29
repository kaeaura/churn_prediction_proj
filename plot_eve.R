# Jing-Kai Lou (kaeaura@gamil.com)
# Wed Sep 28 15:50:40 CST 2011
# This script analyze the attributes in gender
requre('ggplot2')
if (file.exists('my.fig.R')) source('my.fig.R')
source('included.R')

# testing argv: ../exp/alice_activity.csv
# example: Rscript --vanilla plot_eve.R alice_activity.csv

argv = commandArgs(TRUE)
argc = length(argv)

fig_dir = '../fig'

gender_labels = c('Male', 'Female')
gender_colors = c('blue', 'red')
gender_pch = c(18, 4)

race_labels = c('Human', 'Elf', 'Dwarf')
race_colors = c('blue', 'green', 'gold')
race_pch = c(18, 4, 2)

for (arg in argv) {
	if (file.exists(arg) && find_extension(arg) == 'csv') {
		cat(sprintf('reading file: %s', arg))
		df = read.csv(arg, header = T, as.is = T, encoding = 'iso-8859-1')
		cat(sprintf('\tdone\n'))

		# in gender
		if ('gender' %in% names(df)) {
			# race in gender ==============================================================
			fig_name = replace_extention(basename(arg), '')
			fig_name = file.path(fig_dir, paste('race_in_gender', fig_name, sep = '_'))
			cat(sprintf('plotting figure: %s', fig_name))

			my.fig(fig_name, 1, 1)
			race_in_gender = by(df, df$gender, function(g.df) { g.df$race })
			race.gender.mtx = sapply(race_in_gender, function(x) table(x))
			barplot(race.gender.mtx, 
					beside = T,
					names.arg = gender_labels,
					legend.text = race_labels,
					main = sprintf('Race in Gender (data: %s)', basename(arg)),
					angle = c(45, -45, 45),
					col = race_colors
			)
			my.fig.off()
			cat('\tdone\n')

			# level in gender ==============================================================
			fig_name = replace_extention(basename(arg), '')
			fig_name = file.path(fig_dir, paste('level_in_gender', fig_name, sep = '_'))
			cat(sprintf('plotting figure: %s', fig_name))

			my.fig(fig_name, 1, 1)
			level_in_gender = by(df, df$gender, function(g.df) { g.df$level })
			level.gender.list = sapply(level_in_gender, function(x) table(x))
			max_level = max(as.integer(unlist(sapply(level.gender.list, names))))
			max_ratio = max(unlist(level.gender.list))

			plot(	0, 
					type = 'n', 
					xlab = 'achevied level',
					ylab = 'character ratio',
					xlim = range(0, max_level, 100), 
					ylim = range(0, max_ratio), 
					main = sprintf('Level in Gender (data: %s)', basename(arg))
			)

			for (lg_index in 1:length(level.gender.list)) {
				lines(	level.gender.list[[lg_index]], 
						type = 'p', 
						col = gender_colors[lg_index],
						pch = gender_pch[lg_index],
						cex = 1.2
				)
			}

			legend( x = max(max_level, 100), 
					y = max_ratio, 
					xjust = 1,
					yjust = 1,
					gender_labels, 
					col = gender_colors, 
					pch = gender_pch
			)

			my.fig.off()
			cat('\tdone\n')

			# ploting subscription length ==============================================================
			# 	figure name
			fig_name = replace_extention(basename(arg), '')
			fig_name = file.path(fig_dir, paste('subscription_in_gender', fig_name, sep = '_'))
			cat(sprintf('plotting figure: %s', fig_name))

			# 	plotting
			my.fig(fig_name, 1, 1)
			sl_in_gender = by(df, df$gender, function(g.df) { ceiling(g.df$sub_len) })
			sl.gender = sapply(sl_in_gender, function(x) table(x) )
			if (class(sl.gender) == 'list') {
				max_sl = max(as.integer(unlist(sapply(sl.gender, names))), na.rm = T)
				max_ratio = max(unlist(sl.gender))
			} else if (class(sl.gender) == 'matrix') {
				max_sl = max(as.integer(row.names(sl.gender)))
				max_ratio = max(sl.gender)
			}

			plot(	1, 
					type = 'n', 
					xlab = 'subscription length (day)',
					ylab = 'character number',
					xlim = range(1, max_sl), 
					ylim = range(1, max_ratio), 
					main = sprintf('Subscription in Gender (data: %s)', basename(arg)),
					log = 'xy'
			)

			#	lines
			if (class(sl.gender) == 'list') {
				for (sl_index in 1:length(sl.gender)) {
					lines(	sl.gender[[sl_index]],
							type = 'p',
							col = gender_colors[sl_index],
							pch = gender_pch[sl_index],
							cex = 1.2
					)
				}
			} else {
				for (sl_index in 1:ncol(sl.gender)) {
					lines(	sl.gender[,sl_index],
							type = 'p',
							col = gender_colors[sl_index],
							pch = gender_pch[sl_index],
							cex = 1.2
					)
				}
			}

			#	legend
			legend( x = max_sl, 
					y = max_ratio, 
					xjust = 1,
					yjust = 1,
					gender_labels, 
					col = gender_colors, 
					pch = gender_pch
			)
			my.fig.off()
			cat('\tdone\n')

			# guild joined ==============================================================
			# world phase: population, observation  ==============================================================
		}

		if ('race' %in% names(df)) {
			# level in race ==============================================================
			#	figure name
			fig_name = replace_extention(basename(arg), '')
			fig_name = file.path(fig_dir, paste('level_in_race', fig_name, sep = '_'))
			cat(sprintf('plotting figure: %s', fig_name))

			#	plotting
			my.fig(fig_name, 1, 1)
			level_in_race = by(df, df$race, function(g.df) { g.df$level })
			level.race.list = sapply(level_in_race, function(x) table(x))
			max_level = max(as.integer(unlist(sapply(level.race.list, names))))
			max_ratio = max(unlist(level.race.list))
			plot(	0, 
					type = 'n', 
					xlab = 'achevied level',
					ylab = 'character ratio',
					xlim = range(0, max_level, 100), 
					ylim = range(0, max_ratio), 
					main = sprintf('Level in Gender (data: %s)', basename(arg)),
			)

			#	lines
			for (lr_index in 1:length(level.race.list)){
				lines(	level.race.list[[lr_index]], 
						type = 'p',
						col = race_colors[lr_index],
						pch = race_pch[lr_index],
						cex = 1.2
				)
			}

			#	legend
			legend( x = max(max_level, 100), 
					y = max_ratio, 
					xjust = 1,
					yjust = 1,
					race_labels, 
					col = race_colors, 
					pch = race_pch
			)
			my.fig.off()
			cat('\tdone\n')

			# subscription in race ==============================================================
			# 	figure name
			fig_name = replace_extention(basename(arg), '')
			fig_name = file.path(fig_dir, paste('subscription_in_race', fig_name, sep = '_'))
			cat(sprintf('plotting figure: %s', fig_name))

			# 	plotting
			my.fig(fig_name, 1, 1)
			sl_in_race = by(df, df$race, function(g.df) { ceiling(g.df$sub_len) })
			sl.race = sapply(sl_in_race, function(x) table(x) )
			if (class(sl.race) == 'list') {
				max_sl = max(as.integer(unlist(sapply(sl.race, names))), na.rm = T)
				max_ratio = max(unlist(sl.race))
			} else if (class(sl.race) == 'matrix') {
				max_sl = max(as.integer(row.names(sl.race)))
				max_ratio = max(sl.race)
			}

			plot(	1, 
					type = 'n', 
					xlab = 'subscription length (day)',
					ylab = 'character number',
					xlim = range(1, max_sl), 
					ylim = range(1, max_ratio), 
					main = sprintf('Subscription in Race (data: %s)', basename(arg)),
					log = 'xy'
			)

			#	lines
			if (class(sl.race) == 'list') {
				for (sl_index in 1:length(sl.race)) {
					lines(	sl.race[[sl_index]],
							type = 'p',
							col = race_colors[sl_index],
							pch = race_pch[sl_index],
							cex = 1.2
					)
				}
			} else {
				for (sl_index in 1:ncol(sl.race)) {
					lines(	sl.race[,sl_index],
							type = 'p',
							col = race_colors[sl_index],
							pch = race_pch[sl_index],
							cex = 1.2
					)
				}
			}

			#	legend
			legend( x = max_sl, 
					y = max_ratio, 
					xjust = 1,
					yjust = 1,
					race_labels, 
					col = race_colors, 
					pch = race_pch
			)
			my.fig.off()
			cat('\tdone\n')

		}

	} else {
		cat(sprintf("file: %s does not exist\n", arg))
	}
}
