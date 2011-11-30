# Jing-Kai Lou (kaeaura@gamil.com)
# Tue Oct 18 11:38:00 CST 2011

# gender in race over realms =================================
# Is the gender-in-race ratio is consistency over all realms?
cat(sprintf('fig3: plotting figure about gender-in-race ratio\n'))

rg.list = list()
gr.list = list()

for (g_month in global_months) {
	sub.df = subset(data.df, dmonth <= g_month)
	if (nrow(sub.df)) {
		rg.mdf = melt(sub.df, id = c('label', 'gender', 'race'), measure.var = "sub_len")
		rg.list[[g_month]] = cast(rg.mdf, label + race ~ gender, length)
		gr.list[[g_month]] = cast(rg.mdf, label + gender ~ race, length)
		rm(sub.df, rg.mdf)
	} else {
		next
	}
}

fig_name = sprintf('%s/f3-1_race-in-gender_ratio', fig_dir)
rg.df = subset(rg.list[[length(rg.list)]], select = gender_labels)
rg.label = rg.list[[length(rg.list)]]$label
rg.meta_label = rg.list[[length(rg.list)]]$race
my.fig(fig_name)
par(las = 3)
mp = barplot (
				apply(rg.df, 1, function(x) x / sum(x)),
				space = rep(c(1, 0, 0), length(unique(rg.label))),
				width = rowSums(rg.df) / as.integer(labels_len)[match(rg.label, names(labels_len))],
				# realm size normalization
				main = 'Race in Gender',
				ylab = 'Ratio',
				col = gender_colors,
				legend.text = gender_labels,
				names.arg = paste(rg.label, substr(rg.meta_label, 1, 1), sep = '.')
			)
my.fig.off()

fig_name = sprintf('%s/f3-2_gender-in-race_ratio', fig_dir)
gr.df = subset(gr.list[[length(gr.list)]], select = race_labels)
gr.label = gr.list[[length(gr.list)]]$label
gr.meta_label = gr.list[[length(gr.list)]]$gender
my.fig(fig_name)
par(las = 3)
mp = barplot (
				apply(gr.df, 1, function(x) x / sum(x)),
				space = rep(c(1, 0), length(unique(gr.label))),
				width = rowSums(gr.df) / as.integer(labels_len)[match(gr.label, names(labels_len))],
				# realm size normalization
				main = 'Gender in Race',
				ylab = 'Ratio',
				col = race_colors,
				legend.text = race_labels,
				names.arg = paste(gr.label, substr(gr.meta_label, 1, 1), sep = '.')
			)
my.fig.off()

for (gl in unique(gr.label)) {
	gr.index = grep(gl, lapply(gr.list, function(x) as.character(x$label)))
	sub_gr.list = gr.list[gr.index]

	temp_gr.df = lapply	(
							sub_gr.list, 
							function(x) 
							{
								y = subset(x, label == gl, select = c('gender', race_labels))
								rn = y$gender
								y = subset(y, select = race_labels)
								rownames(y) = rn
								y = y / rowSums(y)
							}
						)
	temp_gr.df = do.call('rbind', temp_gr.df)

	fig_name = sprintf('%s/f3-3_gender_in_race_temporal_%s', fig_dir, gl)
	stopifnot(class(temp_gr.df) == 'matrix' || class(temp_gr.df) == 'data.frame')
	my.fig(fig_name, 1, 2)
	par(las = 3)
	male_temp_gr.df = temp_gr.df[grep('Male', rownames(temp_gr.df)),]
	female_temp_gr.df = temp_gr.df[grep('Female', rownames(temp_gr.df)),]
	mp = barplot	(
						apply(male_temp_gr.df, 1, function(x) x),
						beside = T,
						main = sprintf('Temporal Male Race Ratio (%s)', gl),
						ylab = 'Ratio',
						col = race_colors,
						names.arg = substr(rownames(male_temp_gr.df), 4, 8)
					)
	mp = barplot	(
						apply(female_temp_gr.df, 1, function(x) x),
						beside = T,
						main = sprintf('Temporal Female Race Ratio (%s)', gl),
						ylab = 'Ratio',
						col = race_colors,
						names.arg = substr(rownames(female_temp_gr.df), 4, 8)
					)
	my.fig.off()
}

rm(rg.list, gr.list)
