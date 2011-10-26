# Jing-Kai Lou (kaeaura@gamil.com)
source('plot_eve.R')

# gender issue ============================
# mean level?
gender.level.test.by = 
	by(
		data.df, 
		list(label = data.df$label), 
		function(x) {
			wilcox.test(
				x$level[x$gender == 'Male'], 
				x$level[x$gender == 'Female'], 
				alternative = 'g'
			)
		}
	)

# mean sub_len
gender.sublen.test.by = 
	by(
		data.df, 
		list(label = data.df$label), 
		function(x) {
			wilcox.test(
				x$sub_len[x$gender == 'Male'], 
				x$sub_len[x$gender == 'Female'], 
				alternative = 'l'
			)
		}
	)

# mean ocoef
gender.ocoef.test.by = 
	by(
		data.df, 
		list(label = data.df$label), 
		function(x) {
			wilcox.test(
				x$ocoef[x$gender == 'Male'], 
				x$ocoef[x$gender == 'Female'], 
				alternative = 'l'
			)
		}
	)


# race issue ============================
# mean level?
race.level.test.by = 
	by(
		data.df, 
		list(label = data.df$label), 
		function(x) {
			wilcox.test(
				x$level[x$race == race_labels[1]], 
				x$level[x$race == race_labels[3]], 
				alternative = 'l'
			)
		}
	)

# mean sub_len
race.sublen.test.by = 
	by(
		data.df, 
		list(label = data.df$label), 
		function(x) {
			wilcox.test(
				x$sub_len[x$race == race_labels[1]], 
				x$sub_len[x$race == race_labels[2]], 
				alternative = 'l'
			)
		}
	)

# mean ocoef
race.ocoef.test.by = 
	by(
		data.df, 
		list(label = data.df$label), 
		function(x) {
			wilcox.test(
				x$ocoef[x$race == race_labels[1]], 
				x$ocoef[x$race == race_labels[2]], 
				alternative = 'l'
			)
		}
	)


zz <- file('test.result', open = 'wt')
sink(zz)
sink(zz, type = 'message')
gender.level.test.by
gender.sublen.test.by
gender.ocoef.test.by
race.level.test.by
race.sublen.test.by
race.ocoef.test.by
sink(zz, type = 'message')
sink()
