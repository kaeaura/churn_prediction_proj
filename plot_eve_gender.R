# Jing-Kai Lou (kaeaura@gamil.com)
# Tue Oct 18 11:38:00 CST 2011

source('plot_eve.R')
# Requirements:
# 	data: data.df, ...
#	package: reshape

# gender ratio over realms =================================
# Is the gender ratio is consistency over all realms?

cat(sprintf('plotting figure about gender ratio\n'))

g.list = list()
v.list = list()
for (g_month in global_months) {
	list_name = as.character(g_month)
	sub.df = subset(data.df, dmonth <= g_month)
	vsub.df = subset(data.df, dmonth <= g_month & emonth >= g_month) 
	if (nrow(sub.df)) {
		g.mdf = melt(sub.df, id = c("label", "gender"), measure.var = c("ocoef", "sub_len"))
		g.list[[as.character(g_month)]] = cast(g.mdf, label ~ gender, length)
		rm(sub.df, g.mdf)
	} 
	if (nrow(vsub.df)) {
		v.mdf = melt(vsub.df, id = c("label", "gender"), measure.var = c("ocoef", "sub_len"))
		v.list[[as.character(g_month)]] = cast(v.mdf, label ~ gender, length)
		rm(vsub.df, v.mdf)
	}
	rm(list_name)
}

fig_name = sprintf('%s/fig%d_gender_ratio_all', fig_dir, fig_num)
fig_num = fig_num + 1
# last
g.df = subset(g.list[[length(g.list)]], select = gender_labels)
#    Male Female
# 1  3968   3420
# 2 63706  37356
# 3 24888  15568
# 4 12542  11696
# 5 35480  26360
# 6 40576  21630

g.label = g.list[[length(g.list)]]$label
pt = prop.test(g.df$Male, rowSums(g.df))

my.fig(fig_name)
par(bg = 'white')
mp = barplot (
				apply(g.df, 1, function(x) x / sum(x)),
				space = 0.05,
				width = apply(g.df, 1, sum) / as.integer(labels_len)[match(g.label, names(labels_len))],
				# realm size normalization
				main = 'gender ratio',
				ylab = 'ratio',
				col = gender_colors,
				legend.text = gender_labels,
				names.arg = g.label
			)
text	(
			x = mp, 
			y = g.df[,1]/rowSums(g.df) - 0.05, 
			sprintf('%.1f%%', 100 * g.df[,1]/rowSums(g.df)), 
			xpd = t, 
			adj = c(1, 0.5),
			srt = 90,
			col = "white"
		)
legend	(
			x = mp[1],
			y = 0.1,
			xjust = 0,
			yjust = 0,
			sprintf('prop.test: male propotion the in all realms? Xsq = %s, p.value = %s', format(pt$statistic), format(pt$p.value)),
			cex = .7,
		)
my.fig.off()

for (gl in g.label) {
	g.index = grep(gl, lapply(g.list, function(x) as.character(x$label)))
	sub_g.list = g.list[g.index]

	temp_g.df = sapply	(
							sub_g.list, 
							function(x) 
							{
								y = subset(x, label == gl, select = gender_labels),
								y = y / sum(y)
							}
						)

	fig_name = sprintf('%s/f1-1_gender_ratio_temporal_%s', fig_dir, gl)
	stopifnot(class(temp_g.df) == 'matrix')
	my.fig(fig_name)
	par(las = 3)
	mp = barplot	(
						temp_g.df,
						space = 0,
						main = sprintf('Temporal Gender Ratio (%s)', gl),
						ylab = 'Ratio',
						col = gender_colors,
						legend.text = rownames(temp_g.df),
						names.arg = substr(colnames(temp_g.df), 3, 6)
					)
	text	(
				x = mp, 
				y = as.numeric(temp_g.df[1,]) - 0.05, 
				sprintf('%.1f%%', 100 * as.numeric(temp_g.df[1,])), 
				xpd = T, 
				adj = c(1, 0),
				srt = 90,
				cex = .6,
				col = "white"
			)
	my.fig.off()
}

rm(g.list)
