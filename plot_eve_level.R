# Jing-Kai Lou (kaeaura@gamil.com)
# Tue Oct 18 11:38:00 CST 2011

source('plot_eve.R')
# Requirements:
# 	data: data.df, ...
#	package: reshape

# level over realms =================================
# what is the level distribution over different realms?
cat(sprintf('plotting level distribution\n'))

l.list = list()
for (g_month in global_months) {
	sub.df = subset(data.df, substr(ddate, 1, 6) <= g_month)
	if (nrow(sub.df)) {
		l.mdf = melt(sub.df, id = c("label", "level"), measure.var = "sub_len")
		l.cdf = cast(l.mdf, label ~ level, length)
		l.list[[g_month]] = l.cdf
		rm(sub.df, l.mdf)
	} else {
		next
	}
}

fig_name = sprintf('%s/f%d_gender_ratio_all', fig_dir, fig_num)
fig_num = fig_num + 1
plot_num = 1

lv = l.list[[length(l.list)]][,-1]
lv.realm = l.list[[length(l.list)]][,1]

xrange = range(as.integer(names(lv)))
yrange = range(lv / rowSums(lv), 0, 1)
cols = rainbow(length(lv.realm))

my.fig(fig_name)
plot	(
			1,
			type = 'n',
			main = 'Level Distribution',
			xlab = 'level',
			ylab = 'CCDF',
			xlim = xrange,
			ylim = yrange
		)
for (lv.row in 1:nrow(lv)) {
	lv.count = lv[lv.row,]
	lines	(
				x = as.integer(names(lv.count)),
				y = 1 - (cumsum(as.integer(lv.count)) / sum(lv.count)), 
				col = cols[lv.row],
				lwd = 2,
				type = 'l'
			)
}
legend	(
			x = max(xrange),
			y = max(yrange),
			xjust = 1,
			yjust = 1,
			as.character(lv.realm),
			lwd = 4,
			col = cols
		)
my.fig.off()

rm(l.list)
