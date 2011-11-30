# Jing-Kai Lou (kaeaura@gamil.com)
# Wed Oct 19 17:15:23 CST 2011

source('plot_eve.R')

# owls over realms 
# what is the owls distribution over different realms?

m.df = melt(data.df, id = c('label', 'dmonth', 'gender', 'race' ), measure.vars = 'ocoef')
var_in_g.list = cast(m.df, dmonth ~ gender | label + variable, mean, trim = 0.1)
var_in_r.list = cast(m.df, dmonth ~ race | label + variable, mean, trim = 0.1)
var_in_gr.list = cast(m.df, dmonth ~ gender + race | label + variable, mean, trim = 0.1)

# plot figure
fig_name = sprintf('%s/fig%d_owl_all', fig_dir, fig_num)
fig_num = fig_num + 1

my.fig(fig_name, 2, 1)
# owl plot
xrange = range(1, length(global_months))
yrange = range(owl.list, na.rm = T)
plot	(
			0,
			xaxt = 'n',
			type = 'n',
			xlab = 'time',
			ylab = 'owl coefficient',
			main = 'Average Owl Coefficient',
			xlim = xrange,
			ylim = yrange
		)
axis(1, 1:length(o.list), names(o.list))
for (r.index in 1:length(owl.list)) {
	label = names(owl.list)[r.index]
	lines	(
				x = 1:length(owl.list[[r.index]]),
				y = owl.list[[r.index]],
				col = labels_color[which(labels == label)],
				type = 'b',
				lwd = 2,
				lty = 1,
				pch = 19
			)
}
legend	(
			x = max(xrange),
			y = max(yrange),
			ncol = 3,
			xjust = 1,
			yjust = 1,
			paste(labels, as.character(labels_len), sep = ':'),
			col = labels_color,
			lwd = 3,
			cex = .6,
			pch = 19,
		)
# sub_len plot
xrange = range(1, length(o.list))
yrange = range(sublen.list, na.rm = T)
plot	(
			0,
			xaxt = 'n',
			type = 'n',
			xlab = 'time',
			ylab = 'subscription length',
			main = 'Average Subscription',
			xlim = xrange,
			ylim = yrange
		)
axis(1, 1:length(o.list), names(o.list))
for (r.index in 1:length(sublen.list)) {
	label = names(sublen.list)[r.index]
	lines	(
				x = 1:length(sublen.list[[r.index]]),
				y = sublen.list[[r.index]],
				col = labels_color[which(labels == label)],
				lwd = 2,
				lty = 1,
				pch = 19,
			)
}
legend	(
			x = min(xrange),
			y = min(yrange),
			ncol = 3,
			xjust = 0,
			yjust = 0,
			paste(labels, as.character(labels_len), sep = ':'),
			col = labels_color,
			lwd = 3,
			cex = .6,
			pch = 19,
		)
my.fig.off()

# ggplot parts ============================================================================================
sdf = subset(data.df, select = c(label, gender, race, level, sub_len, ocoef))
sdf$ocoef.level = factor(findInterval(sdf$ocoef, seq(0, 1, .25), rightmost.closed = T), labels = c('not owl', 'maybe owl', 'owl', 'big owl'))
sdf$level.level = factor(findInterval(sdf$level, seq(0, 100, 25), rightmost.closed = T), labels = c('noob', 'advanced', 'great', 'master'))

# owl.level vs level.level ============
m = melt(sdf, id = c('label', 'ocoef.level', 'level.level'), measure.var = 'sub_len')
z = cast(m, label ~ ocoef.level ~ level.level, length)

# in gender ============
fig_name = sprintf('%s/fig%d_gg-gender-in-owl', fig_dir, fig_num)
fig_num = fig_num + 1
# boxplot over different realms
p <- ggplot	(sdf, aes(factor(gender), ocoef), group = label)
p + geom_boxplot(aes(fill = gender)) + facet_grid(. ~ label)
ggsave(file = paste(fig_name, 'pdf', sep = '.')) 
# report anova-test
a.results = by	(
				sdf,
				sdf$label,
				function(rdf){
					anova(lm(ocoef ~ gender, data = rdf))
				}
			)
ff = file(sprintf('%s_ANOVA-report.txt', fig_name), open = 'wt')
sink(ff)
sink(ff, type = 'message')
try(a.results)
sink(ff, type = 'message')
sink()
# in race ============
fig_name = sprintf('%s/fig%d_gg-race-in-owl', fig_dir, fig_num)
fig_num = fig_num + 1
# boxplot over different realms
p <- ggplot	(sdf, aes(factor(race), ocoef), group = label)
p + geom_boxplot(aes(fill = race)) + facet_grid(. ~ label)
ggsave(file = paste(fig_name, 'pdf', sep = '.')) 
# report anova-test
a.results = by	(
				sdf,
				sdf$label,
				function(rdf){
					anova(lm(ocoef ~ race, data = rdf))
				}
			)
ff = file(sprintf('%s_ANOVA-report.txt', fig_name), open = 'wt')
sink(ff)
sink(ff, type = 'message')
try(a.results)
sink(ff, type = 'message')
sink()

# in gender + race ============
fig_name = sprintf('%s/fig%d_gg-gender-race-in-owl', fig_dir, fig_num)
fig_num = fig_num + 1
# boxplot over different realms
p <- ggplot	(sdf, aes(factor(gender), ocoef), group = label)
p + geom_boxplot(aes(fill = gender)) + facet_grid(race ~ label)
ggsave(file = paste(fig_name, 'pdf', sep = '.')) 
# report anova-test
a.results = by	(
				sdf,
				sdf$label,
				function(rdf){
					anova(lm(ocoef ~ gender + race, data = rdf))
				}
			)
ff = file(sprintf('%s_ANOVA-report.txt', fig_name), open = 'wt')
sink(ff)
sink(ff, type = 'message')
try(a.results)
sink(ff, type = 'message')
sink()

# level in owl level ============
fig_name = sprintf('%s/fig%d_gg-owl-in-level_ratio', fig_dir, fig_num)
fig_num = fig_num + 1
# boxplot over different realms
p <- ggplot	(
				sdf,
				aes(factor(ocoef.level), level),
				group = label
			)
p + geom_boxplot(aes(fill = ocoef.level)) + coord_flip() + facet_grid(label ~ gender)
ggsave(file = paste(fig_name, 'pdf', sep = '.')) 

# level in owl level ============
fig_name = sprintf('%s/fig%d_gg-level-in-owl', fig_dir, fig_num)
fig_num = fig_num + 1
# boxplot over different realms
p <- ggplot	(
				sdf,
				aes(factor(level.level), ocoef),
				group = label
			)
p + geom_boxplot(aes(fill = level.level)) + coord_flip() + facet_grid(label ~ gender)
ggsave(file = paste(fig_name, 'pdf', sep = '.')) 

# correlation with sub_len ============
fig_name = sprintf('%s/fig%d_sublen-in-owl', fig_dir, fig_num)
fig_num = fig_num + 1

d <- qplot(ocoef, sub_len, data = sdf, colour = level)
d + facet_wrap(label ~ race) + scale_colour_gradient(limits = c(30, 70), low = 'blue', high = 'red')
ggsave(file = paste(fig_name, 'pdf', sep = '.')) 
