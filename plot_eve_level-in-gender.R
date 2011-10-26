# Jing-Kai Lou (kaeaura@gamil.com)
# Tue Oct 18 11:38:00 CST 2011

source('plot_eve.R')
# Requirements:
# 	data: data.df, ...
#	package: reshape

# level in gender =================================
# which gender works harder for leveling up?
cat(sprintf('plotting figure about gender-in-level ratio\n'))

lg.list = list()
for (g_month in global_months) {
	sub.df = subset(data.df, dmonth <= g_month)
	if (nrow(sub.df)) {
		l.mdf = melt(sub.df, id = c("label", "gender", "level"), measure.var = "sub_len")
		l.cdf = cast(l.mdf, level ~ label + gender, length)
		lg.list[[g_month]] = l.cdf
		rm(sub.df, l.mdf)
	} else {
		next
	}
}

#gl.df = cast(data.df, level ~ label + gender, length, value = 'cid')
gl.level = lg.list[[length(lg.list)]][,1]
gl.df = lg.list[[length(lg.list)]][,-1]
cum_gl.mtx = sweep(cumsum(gl.df), 2, colSums(gl.df), FUN = '/')

# start ploting

fig_name = sprintf('%s/f%d_gender-in-level_ratio', fig_dir, fig_num)
fig_num = fig_num + 1

my.fig(fig_name)
plot	(
			x = 1,
			y = 1,
			xlim = range(gl.level),
			ylim = range(0, 1),
			main = 'Gender-in-Level',
			xlab = 'Level',
			ylab = 'CCDF',
			type = 'n'
		)
marks = strsplit(colnames(cum_gl.mtx), '_')
marks.indices = lapply	(
							marks, 
							function(x) {
								c(which(labels == x[1]), which(gender_labels == x[2]))
							}
						)
for (cum_cindex in 1:ncol(cum_gl.mtx)) {
	marks.index = marks.indices[[cum_cindex]]
	lines	(
				x = gl.level,
				y = 1 - cum_gl.mtx[,cum_cindex],
				col = labels_color[marks.index[1]],
				lty = gender_lty[marks.index[2]],
				type = 'l',
				lwd = 2
			)
}
legend	(
			colnames(gl.df),
			x = max(gl.level),
			y = 1,
			xjust = 1, 
			yjust = 1,
			lwd = 4,
			col = labels_color[sapply(marks.indices, function(x) x[1])],
			lty = gender_lty[sapply(marks.indices, function(x) x[2])]
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
	sub_cum_gl.mtx = cum_gl.mtx[,grep(label, colnames(cum_gl.mtx))]

	# chi-test
	sub_gl.df = gl.df[,grep(label, colnames(gl.df))]
	if (!ncol(sub_gl.df)) {
		next
	} else if (ncol(sub_gl.df) == 2) {
		x_result = chisq.test	(
									sub_gl.df[1:min(nrow(sub_gl.df), max_df),],
									p = matrix(rep(c(.36, .63), nrow(sub_gl.df)), byrow = T, ncol = 2)
								)
	}

	# underlaying
	plot	(
				x = 1,
				y = 1,
				xlim = range(gl.level),
				ylim = range(0, 1),
				main = 'Gender-in-Level',
				xlab = 'Level',
				ylab = 'CDF',
				type = 'n'
			)

	marks = strsplit(colnames(sub_cum_gl.mtx), '_')
	marks.indices = lapply	(
								marks, 
								function(x) {
									c(which(labels == x[1]), which(gender_labels == x[2]))
								}
							)
	for (sub_cum_cindex in 1:ncol(sub_cum_gl.mtx)) {
		marks.index = marks.indices[[sub_cum_cindex]]
		lines	(
					x = gl.level,
					y = sub_cum_gl.mtx[,sub_cum_cindex],
					col = gender_colors[marks.index[2]],
					lty = gender_lty[marks.index[2]],
					lwd = 3,
					type = 'l'
				)
	}

	# legend
	legend	(
				colnames(sub_cum_gl.mtx),
				x = max(gl.level),
				y = 0,
				xjust = 1, 
				yjust = 0,
				col = gender_colors[sapply(marks.indices, function(x) x[2])],
				lty = gender_lty[sapply(marks.indices, function(x) x[2])],
				lwd = 4 # smaller legend
			)

	# text : test result
	if (exists('x_result')) {
		text	(
					x = min(gl.level), 
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

	# for reference
	barplot(apply(sub_gl.df, 1, function(x) x / sum(x)), ylim = range(0, 1), main = 'Gender Ratio in Bin', xlab = 'Level', ylab = 'Gender Ratio', legend.text = colnames(sub_gl.df))

}
my.fig.off()

# ggplot parts
fig_name = sprintf('%s/fig%d_gg-gender-in-level_ratio', fig_dir, fig_num)
fig_num = fig_num + 1
# boxplot over different realms
p <- ggplot	(
				subset(data.df, select = c(label, gender, level)),
				aes(factor(gender), level),
				group = label
			)
p + geom_boxplot(aes(fill = gender)) + facet_grid(. ~ label)
ggsave(file = paste(fig_name, 'pdf', sep = '.')) 
# report anova-test
sdf = subset(data.df, select = c(label, gender, level))
a.results = by	(
				sdf,
				sdf$label,
				function(rdf){
					anova(lm(level ~ gender, data = rdf))
				}
			)
ff = file(sprintf('%s_ANOVA-report.txt', fig_name), open = 'wt')
sink(ff)
sink(ff, type = 'message')
try(a.results)
sink(ff, type = 'message')
sink()
