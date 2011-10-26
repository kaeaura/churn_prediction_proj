# Jing-Kai Lou (kaeaura@gamil.com)
# Tue Oct 18 11:38:00 CST 2011

source('plot_eve.R')
# Requirements:
# 	data: data.df, ...
#	package: reshape
# race ratio over realms =================================
# Is the race ratio is consistency over all realms?
cat(sprintf('fig2: plotting figure about race ratio\n'))

r.list = list()
for (g_month in global_months) {
	sub.df = subset(data.df, substr(ddate, 1, 6) <= g_month)
	if (nrow(sub.df)) {
		r.mdf = melt(sub.df, id = c("label", "race"), measure.var = "sub_len")
		r.cdf = cast(r.mdf, label ~ race, length)
		r.list[[g_month]] = r.cdf
		rm(sub.df, r.mdf, r.cdf)
	} else {
		next
	}
}

#pt = prop.test(r.df$Human, rowSums(r.df))

fig_name = sprintf('%s/f2-1_race_ratio_all', fig_dir)
r.df = subset(r.list[[length(r.list)]], select = race_labels)
r.label = r.list[[length(r.list)]]$label
my.fig(fig_name)
mp = barplot (
				apply(r.df, 1, function(x) x / sum(x)),
				space = 0.05,
				width = apply(r.df, 1, sum) / as.integer(labels_len)[match(r.label, names(labels_len))],
				# realm size normalization
				main = 'Race Ratio',
				ylab = 'Ratio',
				col = race_colors,
				#legend.text = race_labels,
				names.arg = r.label
			)
text	(
			x = mp, 
			y = r.df[,1]/rowSums(r.df) - 0.05, 
			sprintf('%.1f%%', 100 * r.df[,1]/rowSums(r.df)), 
			xpd = T, 
			adj = c(1, 0.5),
			srt = 90,
			col = "white"
		)
text	(
			x = mp, 
			y = (r.df[,1] + r.df[,2])/rowSums(r.df) - 0.05, 
			sprintf('%.1f%%', 100 * r.df[,2]/rowSums(r.df)), 
			xpd = T, 
			adj = c(1, 0.5),
			srt = 90,
			col = "darkred"
		)
text	(
			x = mp, 
			y = (r.df[,1] + r.df[,2] + r.df[,3])/rowSums(r.df) - 0.05, 
			sprintf('%.1f%%', 100 * r.df[,3]/rowSums(r.df)), 
			xpd = T, 
			adj = c(1, 0.5),
			srt = 90,
			col = "darkblue"
		)
my.fig.off()

for (gl in r.label) {
	r.index = grep(gl, lapply(r.list, function(x) as.character(x$label)))
	sub_r.list = r.list[r.index]

	temp_r.df = sapply	(
							sub_r.list, 
							function(x) 
							{
								y = subset(x, label == gl, select = race_labels)
								y = y / sum(y)
							}
						)

	fig_name = sprintf('%s/f2-1_race_ratio_temporal_%s', fig_dir, gl)
	stopifnot(class(temp_r.df) == 'matrix')
	my.fig(fig_name)
	par(las = 3)
	mp = barplot	(
						temp_r.df,
						space = 0,
						main = sprintf('Temporal Race Ratio (%s)', gl),
						ylab = 'Ratio',
						col = race_colors,
						#legend.text = rownames(temp_r.df),
						names.arg = substr(colnames(temp_r.df), 3, 6)
					)
	text	(
				x = mp, 
				y = as.numeric(temp_r.df[1,]) - 0.05, 
				sprintf('%.1f%%', 100 * as.numeric(temp_r.df[1,])), 
				xpd = T, 
				adj = c(1, 0),
				srt = 90,
				cex = .6,
				col = "white"
			)
	text	(
				x = mp, 
				y = as.numeric(temp_r.df[1,]) + as.numeric(temp_r.df[2,]) - 0.05, 
				sprintf('%.1f%%', 100 * as.numeric(temp_r.df[2,])), 
				xpd = T, 
				adj = c(1, 0),
				srt = 90,
				cex = .6,
				col = "darkred"
			)
	text	(
				x = mp, 
				y = as.numeric(temp_r.df[1,]) + as.numeric(temp_r.df[2,]) + as.numeric(temp_r.df[3,]) - 0.05, 
				sprintf('%.1f%%', 100 * as.numeric(temp_r.df[3,])), 
				xpd = T, 
				adj = c(1, 0),
				srt = 90,
				cex = .6,
				col = "darkblue"
			)
	my.fig.off()
}

rm(r.list)
