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
p.list = list(); pa.list = list()
v.list = list(); va.list = list()
for (g_month in global_months) {
	list_name = as.character(g_month)
	sub.df = subset(data.df, dmonth <= g_month, select = c('label', 'account'))
	vsub.df = subset(data.df, dmonth <= g_month & emonth >= g_month, select = c('label', 'account'))
	if (nrow(sub.df)) {
		p.mdf = melt(sub.df, id = "label", measure.var = "account")
		p.list[[list_name]] = cast(p.mdf, label ~ variable, length)								#character count
		pa.list[[list_name]] = cast(p.mdf, label ~ variable, function(x) length(unique(x)))		#account count
		rm(sub.df, p.mdf)
	}
	if (nrow(vsub.df)) {
		v.mdf = melt(vsub.df, id = "label", measure.var = "account")
		v.list[[list_name]] = cast(v.mdf, label ~ variable, length)
		va.list[[list_name]] = cast(v.mdf, label ~ variable, function(x) length(unique(x)))
		rm(vsub.df, v.mdf)
	} 
	rm(list_name)
}

# population over time for each realm
cum_char.df = ldply(p.list, data.frame)
cum_acct.df = ldply(pa.list, data.frame)
vis_char.df = ldply(v.list, data.frame)
vis_acct.df = ldply(va.list, data.frame)

#plot figure
fig_name = sprintf('%s/fig%d_population', fig_dir, fig_num)
fig_num = fig_num + 1

my.fig(fig_name, 1, 2)
# visit plot
xaxt = union(cum_char.df$.id, vis_char.df$.id)
xaxt = xaxt[order(as.integer(xaxt))]
xrange = range(1:length(xaxt))
yrange = range(vis_char.df$account, vis_acct.df$account, na.rm = T)
plot	(
			0,
			type = 'n',
			xaxt = 'n',
			xlab = 'time',
			ylab = 'population',
			main = 'Monthly Visit Population',
			xlim = xrange,
			ylim = yrange
		)
axis(1, at = 1:length(xaxt), label = xaxt)

by	(
		vis_char.df,
		vis_char.df$label,
		function(sdf) {
			lines(
					match(sdf$.id, xaxt), 
					sdf$account,
					col = labels_color[which(labels == unique(sdf$label))],
					lty = 1,
					lwd = 2
				)
		}
	)

by	(
		vis_acct.df,
		vis_acct.df$label,
		function(sdf) {
			lines(
					match(sdf$.id, xaxt), 
					sdf$account,
					col = labels_color[which(labels == unique(sdf$label))],
					lty = 3,
					lwd = 2
				)
		}
	)

legend	(
			x = max(xrange),
			y = max(yrange),
			ncol = 2,
			xjust = 1,
			yjust = 1,
			paste(labels, as.character(labels_len), sep = ':'),
			col = labels_color,
			lty = 2,
			lwd = 3,
			cex = 0.6
		)
legend	(
			x = min(xrange),
			y = min(yrange),
			ncol = 2,
			xjust = 0,
			yjust = 0,
			c('character', 'account'),
			lwd = 2,
			lty = c(1, 3),
			cex = 0.6
		)

# population plot
xaxt = union(cum_char.df$.id, cum_char.df$.id)
xaxt = xaxt[order(as.integer(xaxt))]
xrange = range(1:length(xaxt))
yrange = range(cum_char.df$account, cum_acct.df$account, na.rm = T)
plot	(
			0,
			type = 'n',
			xaxt = 'n',
			xlab = 'time',
			ylab = 'population',
			main = 'Cumulative Population',
			xlim = xrange,
			ylim = yrange
		)
axis(1, at = 1:length(xaxt), label = xaxt)

by	(
		cum_char.df,
		cum_char.df$label,
		function(sdf) {
			lines(
					match(sdf$.id, xaxt), 
					sdf$account,
					col = labels_color[which(labels == unique(sdf$label))],
					lty = 1,
					lwd = 2
				)
		}
	)

by	(
		cum_acct.df,
		cum_acct.df$label,
		function(sdf) {
			lines(
					match(sdf$.id, xaxt), 
					sdf$account,
					col = labels_color[which(labels == unique(sdf$label))],
					lty = 3,
					lwd = 2
				)
		}
	)

legend	(
			x = min(xrange),
			y = max(yrange),
			ncol = 2,
			xjust = 0,
			yjust = 1,
			paste(labels, as.character(labels_len), sep = ':'),
			col = labels_color,
			lty = 2,
			lwd = 3,
			cex = 0.6
		)
legend	(
			x = min(xrange),
			y = min(yrange),
			ncol = 2,
			xjust = 0,
			yjust = 0,
			c('character', 'account'),
			lwd = 2,
			lty = c(1, 3),
			cex = 0.6
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
