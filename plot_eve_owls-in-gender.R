# Jing-Kai Lou (kaeaura@gamil.com)
# Wed Oct 19 12:05:37 CST 2011

# gender with owl-coef
# owls in gender =================================
fig_name = sprintf('%s/f6_owls-in-gender', fig_dir)
sample_num = 1000

ks_test_go.by = by	(
					data.df, 
					list(label = data.df$label), 
					function(x) {
						m_ocoefs = x$ocoef[x$gender == 'Male']
						f_ocoefs = x$ocoef[x$gender == 'Female']
						ks_res = ks.test(
										sample(m_ocoefs, sample_num), 
										sample(f_ocoefs, sample_num),
										alternative = 'greater'
								)

						my.fig(paste(fig_name, unique(x$label), sep='-'))

						plot	(
									1, 
									xlim = range(0, 1),
									ylim = range(0, 1),
									type = 'n',
									xlab = 'Owl Coefficient',
									ylab = 'CDF'
								)

						steps = seq(0, 1, .02)
						lines	(
									x = steps,
									y = ecdf(m_ocoefs)(steps),
									lwd = 2,
									col = gender_colors[1]
								)
						lines	(
									x = steps,
									y = ecdf(f_ocoefs)(steps),
									lwd = 2,
									col = gender_colors[2]
								)

						legend	(
									x = 1,
									y = 0,
									xjust = 1,
									yjust = 0,
									gender_labels,
									col = gender_colors,
									lwd = 2
								)

						text	(
									x = 0,
									y = 1,
									adj = c(0, 1),
									sprintf(
										"KS-Test: Male above Female\np-value: %.4f \n D: %.3f",
										ks_res$p.value,
										ks_res$statistic
									)
								)

						my.fig.off()
						
						return(ks_res)
					}
				)

ks_test_log = paste(fig_name, '.txt', sep='')
sink(ks_test_log)
ks_test_go.by
sink()
unlink(ks_test_log)

