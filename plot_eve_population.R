# Jing-Kai Lou (kaeaura@gamil.com)
# Wed Oct 19 10:04:55 CST 2011

source('plot_eve.R')
# Requirements:
# 	data: data.df, ...
#	package: reshape

# population over realms =================================
# does the population getting grow or decay over time?

cat(sprintf('fig: plotting figure about population\n'))


# population over time
p.list = list()
v.list = list()
for (g_month in global_months) {
	list_name = as.character(g_month)
	sub.df = subset(data.df, dmonth <= g_month, select = c('label', 'sub_len'))
	vsub.df = subset(data.df, dmonth <= g_month & emonth >= g_month, select = c('label', 'sub_len'))
	if (nrow(sub.df)) {
		p.mdf = melt(sub.df, id = "label", measure.var = "sub_len")
		p.list[[list_name]] = cast(p.mdf, label ~ variable, length)
		rm(sub.df, p.mdf)
	}
	if (nrow(vsub.df)) {
		v.mdf = melt(vsub.df, id = "label", measure.var = "sub_len")
		v.list[[list_name]] = cast(v.mdf, label ~ variable, length)
		rm(vsub.df, v.mdf)
	} 
	rm(list_name)
}

# population over time for each realm
realm.list = lapply	(
						labels, 
						function(l) {
							sapply(p.list, function(d)  ifelse(length(grep(l, d$label)), d$sub_len[grep(l, d$label)], NA))
						}
					)
names(realm.list) = labels

# visit pop. for each realm
visit.list = lapply (
						labels, 
						function(l) {
							sapply(v.list, function(d)  ifelse(length(grep(l, d$label)), d$sub_len[grep(l, d$label)], NA))
						}
					)
names(visit.list) = labels

#plot figure
fig_name = sprintf('%s/fig%d_population', fig_dir, fig_num)
fig_num = fig_num + 1

my.fig(fig_name, 2, 1)
# visit plot
xrange = range(1, length(v.list))
yrange = range(visit.list, na.rm = T)
plot	(
			0,
			log = 'y',
			xaxt = 'n',
			type = 'n',
			xlab = 'time',
			ylab = 'population',
			main = 'Monthly Visit Population',
			xlim = xrange,
			ylim = yrange
		)
axis(1, 1:length(v.list), names(v.list))
for (v.index in 1:length(visit.list)) {
	label = names(visit.list)[v.index]
	lines	(
				x = 1:length(visit.list[[v.index]]),
				y = visit.list[[v.index]],
				col = labels_color[which(labels == label)],
				lty = 2,
				lwd = 2
			)
}
legend	(
			x = min(xrange),
			y = min(yrange),
			ncol = 2,
			xjust = 0,
			yjust = 0,
			paste(labels, as.character(labels_len), sep = ':'),
			col = labels_color,
			lty = 2,
			lwd = 3,
			cex = 0.6
		)
# population plot
xrange = range(1, length(p.list))
yrange = range(realm.list, na.rm = T)
plot	(
			0,
			log = 'y',
			xaxt = 'n',
			type = 'n',
			xlab = 'time',
			ylab = 'population',
			main = 'Cumulative Population',
			xlim = xrange,
			ylim = yrange
		)
axis(1, 1:length(p.list), names(p.list))
for (r.index in 1:length(realm.list)) {
	label = names(realm.list)[r.index]
	lines	(
				x = 1:length(realm.list[[r.index]]),
				y = realm.list[[r.index]],
				col = labels_color[which(labels == label)],
				pch = 19,
				lwd = 2,
			)
}
legend	(
			x = min(xrange),
			y = min(yrange),
			ncol = 2,
			xjust = 0,
			yjust = 0,
			paste(labels, as.character(labels_len), sep = ':'),
			col = labels_color,
			lwd = 3,
			pch = 19,
			cex = .6
		)
my.fig.off()

#plot population cdf
fig_name = sprintf('%s/fig%d_population-cdf', fig_dir, fig_num)
fig_num = fig_num + 1

my.fig(fig_name)
xrange = range(1, length(p.list))
yrange = range(0, 1)
plot	(
			0,
			type = 'n',
			xlab = 'living time (month)',
			ylab = 'population',
			main = 'Cumulative Population Ratio',
			xlim = xrange,
			ylim = yrange
		)

for (r.index in 1:length(realm.list)) {
	label = names(realm.list)[r.index]
	values = realm.list[[r.index]]
	values = values[!is.na(values)]
	values = values / values[length(values)]
	lines	(
				x = 1:length(values),
				y = values,
				col = labels_color[which(labels == label)],
				pch = 19,
				lwd = 2,
			)
}
legend	(
			x = max(xrange),
			y = min(yrange),
			ncol = 2,
			xjust = 1,
			yjust = 0,
			paste(labels, as.character(labels_len), sep = ':'),
			col = labels_color,
			lwd = 3,
			pch = 19,
			cex = .6
		)
my.fig.off()

rm(p.list, realm.list, visit.list)
