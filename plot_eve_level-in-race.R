# Jing-Kai Lou (kaeaura@gamil.com)
# Wed Oct 19 11:50:50 CST 2011

# level in gender =================================
# which gender works harder for leveling up?
cat(sprintf('fig4: plotting figure about gender-in-level ratio\n'))

gl.df = cast(data.df, level ~ label + gender, length, value = 'cid')
cum_gl.df = apply(gl.df, 2, function(x) cumsum(x) / sum(x))
distr_gl.list = apply(gl.df[,-1], 2, function(x) rep(gl.df$level, x))
cdf_gl.list = sapply(distr_gl.list, function(x) { ecdf(x) })

# start ploting
fig_name = sprintf('%s/f4_gender-in-level_ratio', fig_dir)

my.fig(fig_name)
plot	(
			x = 1,
			y = 1,
			xlim = range(gl.df$level),
			ylim = range(0, 1),
			main = 'Gender-in-Level',
			xlab = 'Level',
			ylab = 'CDF',
			type = 'n'
		)

for (cgl_col_index in 1:length(cdf_gl.list)) {
	col_index = (cgl_col_index %% length(gender_labels))
	col_index = ifelse(!col_index, length(gender_labels), col_index)
	lines	(
				x = gl.df$level,
				y = cdf_gl.list[[cgl_col_index]](gl.df$level), 
				col = gender_colors[col_index],
				pch = cgl_col_index,
				type = 'p'
			)
}

legend	(
			names(gl.df)[-1],
			x = max(gl.df$level),
			y = 0,
			xjust = 1, 
			yjust = 0,
			col = gender_colors,
			pch = 1:ncol(cum_gl.df),
		)
my.fig.off()

# realm seperately
# gender really affect the leveling? using ks-test
fig_name = paste(fig_name, 'split', sep = '_')
plot_row_num = 3
plot_row_num = ifelse(length(labels) >= 3, 3, 1)

my.fig(fig_name, plot_row_num, ceiling(length(labels) / plot_row_num))
for (label_index in 1:length(labels)) {
	label = labels[label_index]
	sub_gl.df = gl.df[,grep(label, colnames(gl.df))]
	sub_cum_gl.df = cum_gl.df[,grep(label, colnames(cum_gl.df))]
	sub_distr_gl.list = apply(sub_gl.df, 2, function(x) rep(gl.df$level, x))

	if (!ncol(sub_gl.df)) {
		next
	} else if (ncol(sub_gl.df) == 2) {
		x_result = chisq.test(sub_gl.df[1:min(nrow(sub_gl.df), max_df), ])
	}

	sub_cdf_gl.list = sapply(sub_distr_gl.list, function(x) { ecdf(x) })
	
	# underlaying
	plot	(
				x = 1,
				y = 1,
				log = 'x',
				xlim = range(gl.df$level),
				ylim = range(0, 1),
				main = 'Gender-in-Level (log)',
				xlab = 'Level',
				ylab = 'CDF',
				type = 'n'
			)

	for (cgl_col_index in 1:length(sub_cdf_gl.list)) {
		col_index = (cgl_col_index %% length(gender_labels))
		col_index = ifelse(!col_index, length(gender_labels), col_index)

		lines	(
					x = gl.df$level,
					y = sub_cdf_gl.list[[cgl_col_index]](gl.df$level),
					col = gender_colors[col_index],
					pch = gender_pch[cgl_col_index],
					cex = .8,
					type = 'p'
				)
	}

	# legend
	legend	(
				colnames(sub_cum_gl.df),
				x = max(gl.df$level),
				y = 0,
				xjust = 1, 
				yjust = 0,
				col = gender_colors,
				pch = gender_pch[1:ncol(sub_cum_gl.df)],
				cex = 0.8	# smaller legend
			)

	# text : test result
	if (exists('x_result')) {
		text	(
					x = min(gl.df$level), 
					y = 1, 
					adj = c(0, 1),
					cex = 0.75,
					font = 2,
					sprintf(
						'Chisq-test\n p-value: %.4f\n X-squared: %.3f', 
						x_result$p.value,
						x_result$statistic
					)
				)
		rm('x_result')
	}

}
my.fig.off()


# level in race =================================
# which race works harder for leveling up?
cat(sprintf('fig5: plotting figure about race-in-level ratio\n'))

rl.df = cast(data.df, level ~ label + race, length, value = 'cid')
cum_rl.df = apply(rl.df, 2, function(x) cumsum(x) / sum(x))
distr_gl.list = apply(rl.df[,-1], 2, function(x) rep(rl.df$level, x))
cdf_gl.list = sapply(distr_gl.list, function(x) { ecdf(x) })

# start ploting
fig_name = sprintf('%s/f5_race-in-level_ratio', fig_dir)

my.fig(fig_name)
plot	(
			x = 1,
			y = 1,
			xlim = range(rl.df$level),
			ylim = range(0, 1),
			main = 'Gender-in-Level',
			xlab = 'Level',
			ylab = 'CDF',
			type = 'n'
		)

for (cgl_col_index in 1:length(cdf_gl.list)) {
	col_index = (cgl_col_index %% length(race_labels))
	col_index = ifelse(!col_index, length(race_labels), col_index)
	lines	(
				x = rl.df$level,
				y = cdf_gl.list[[cgl_col_index]](rl.df$level), 
				col = race_colors[col_index],
				pch = cgl_col_index,
				type = 'p'
			)
}

legend	(
			names(rl.df)[-1],
			x = max(rl.df$level),
			y = 0,
			xjust = 1, 
			yjust = 0,
			col = race_colors,
			pch = 1:ncol(cum_rl.df),
		)
my.fig.off()

# realm seperately
# race really affect the leveling? using wilcox-test
# mean-level in xx race is greate than mean-level in yy race?
fig_name = paste(fig_name, 'split', sep = '_')
plot_row_num = 3
plot_row_num = ifelse(length(labels) >= 3, 3, 1)

my.fig(fig_name, plot_row_num, ceiling(length(labels) / plot_row_num))
for (label_index in 1:length(labels)) {
	label = labels[label_index]
	sub_rl.df = rl.df[,grep(label, colnames(rl.df))]
	sub_cum_rl.df = cum_rl.df[,grep(label, colnames(cum_rl.df))]
	sub_distr_gl.list = apply(sub_rl.df, 2, function(x) rep(rl.df$level, x))

	if (!ncol(sub_rl.df)) {
		next
	} else if (ncol(sub_rl.df) == 3) {
		x_result = chisq.test(sub_rl.df[1:min(nrow(sub_rl.df), max_df), ])
	}

	sub_cdf_gl.list = sapply(sub_distr_gl.list, function(x) { ecdf(x) })
	
	# underlaying
	plot	(
				x = 1,
				y = 1,
				log = 'x',
				xlim = range(rl.df$level),
				ylim = range(0, 1),
				main = 'Race-in-Level (log)',
				xlab = 'Level',
				ylab = 'CDF',
				type = 'n'
			)

	for (cgl_col_index in 1:length(sub_cdf_gl.list)) {
		col_index = (cgl_col_index %% length(race_labels))
		col_index = ifelse(!col_index, length(race_labels), col_index)

		lines	(
					x = rl.df$level,
					y = sub_cdf_gl.list[[cgl_col_index]](rl.df$level),
					col = race_colors[col_index],
					pch = race_pch[cgl_col_index],
					cex = .8,
					type = 'p'
				)
	}

	# legend
	legend	(
				colnames(sub_cum_rl.df),
				x = max(rl.df$level),
				y = 0,
				xjust = 1, 
				yjust = 0,
				col = race_colors,
				pch = race_pch[1:ncol(sub_cum_rl.df)],
				cex = 0.8	# smaller legend
			)

	# text : test result
	if (exists('x_result')) {
		text	(
					x = min(rl.df$level), 
					y = 1, 
					adj = c(0, 1),
					cex = 0.75,
					font = 2,
					sprintf(
						'Chisq-test\n p-value: %.4f\n X-squared: %.3f', 
						x_result$p.value,
						x_result$statistic
					)
				)
		rm('x_result')
	}

}
my.fig.off()

# ggplot parts ============================================================================================
fig_name = sprintf('%s/fig%d_gg-race-in-level_ratio', fig_dir, fig_num)
fig_num = fig_num + 1
# boxplot over different realms
p <- ggplot	(
				subset(data.df, select = c(label, race, level)),
				aes(factor(race), level),
				group = label
			)
p + geom_boxplot(aes(fill = race)) + facet_grid(. ~ label)
ggsave(file = paste(fig_name, 'pdf', sep = '.')) 
# report anova-test
sdf = subset(data.df, select = c(label, race, level))
a.results = by	(
				sdf,
				sdf$label,
				function(rdf){
					anova(lm(level ~ race, data = rdf))
				}
			)
ff = file(sprintf('%s_ANOVA-report.txt', fig_name), open = 'wt')
sink(ff)
sink(ff, type = 'message')
try(a.results)
sink(ff, type = 'message')
sink()
# ggplot parts ============================================================================================
fig_name = sprintf('%s/fig%d_gg-gender-race-in-level_ratio', fig_dir, fig_num)
fig_num = fig_num + 1
# boxplot over different realms
p <- ggplot	(
				subset(data.df, select = c(label, gender, race, level)),
				aes(factor(gender), level),
				group = label
			)
p + geom_boxplot(aes(fill = gender)) + facet_grid(race ~ label)
ggsave(file = paste(fig_name, 'pdf', sep = '.')) 
# report anova-test
sdf = subset(data.df, select = c(label, gender, race, level))
a.results = by	(
				sdf,
				sdf$label,
				function(rdf){
					anova(lm(level ~ gender + race, data = rdf))
				}
			)
ff = file(sprintf('%s_ANOVA-report.txt', fig_name), open = 'wt')
sink(ff)
sink(ff, type = 'message')
try(a.results)
sink(ff, type = 'message')
sink()
