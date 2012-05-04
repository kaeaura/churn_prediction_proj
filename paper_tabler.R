# Jing-Kai Lou (kaeaura@gamil.com)
source('../../my_lib/my.fig.R')
source('../../my_lib/plfit.r')
require(plyr)
tbls = 2

extract <- function(x) as.numeric(unlist(strsplit(x, '/')))
powerlaw <- function(x, amp, index) amp * (x ** index)

if ( 1 %in% tbls) {
	df = read.csv('doc/interactions_over_platforms/tables/degFit.csv', header = T, as.is = T)
	d1.df <- ddply (df, .(dataset),
			function(x) {
				fit <- extract(x$outDegDistr_fit)
				y.hat <- powerlaw(x = extract(x$outDegDistr_x), amp = fit[1], index = fit[2])
				y <- extract(x$outDegDistr_y)
				out.D <- ks.test(y, y.hat)$statistic
				fit <- extract(x$inDegDistr_fit)
				y.hat <- powerlaw(x = extract(x$inDegDistr_x), amp = fit[1], index = fit[2])
				y <- extract(x$inDegDistr_y)
				in.D <- ks.test(y, y.hat)$statistic
				d <- c(out.D, in.D)
				names(d) <- c('outdegree.D', 'indegree.D')
				return(d)
			}
	)

	df = read.csv('doc/interactions_over_platforms/tables/degFit_yf.csv', header = T, as.is = T)
	d2.df <- ddply (df, .(dataset),
			function(x) {
				fit <- extract(x$degDistr_fit)
				y.hat <- powerlaw(x = extract(x$degDistr_x), amp = fit[1], index = fit[2])
				y <- extract(x$degDistr_y)
				d <- ks.test(y, y.hat)$statistic
				d <- rep(d, 2)
				names(d) <- c('outdegree.D', 'indegree.D') 
				return(d)
			}
	)
	d.df <- rbind(d1.df, d2.df)

	write.csv(d.df, file = 'doc/interactions_over_platforms/tables/degFit_D.csv', quote = F, row.names=F)
}

if (2 %in% tbls){
	# read data
	source.dir <- 'doc/interactions_over_platforms/tables'
	plfit.df = read.csv(file.path(source.dir, 'degFit.csv'), header = T, as.is = T)
	datasets <- plfit.df$dataset

	require(MASS)
	require(VGAM)
	
	D.df = list()
	for (db in datasets){
		seq.file <- file.path(source.dir, 'deg_seq', sprintf('%s_indegree.csv', db))
		if (file.exists(seq.file)) {
			d = scan(seq.file)
			d = d[d > 0]
			r = range(d)
			lnorm.est <- fitdistr(d, 'lognormal')$estimate
			gamma.est <- fitdistr(d, 'gamma', list(shape = 1, rate = 1))$estimate
			plfit.est <- plfit(d, 'limit', 100)

			# distance
			lnorm.D <- ks.test(d, 'plnorm', lnorm.est[1], lnorm.est[2])$statistic
			gamma.D <- ks.test(d, 'pgamma', gamma.est[1], gamma.est[2])$statistic
			pl.D <- ks.test(d, 'ppareto', plfit.est$xmin, plfit.est$alpha)$statistic
			#pl.D = plfit.est$D
			Ds <- c(lnorm.D, gamma.D, pl.D)
			D.df[[db]] = 

			# plot
			r.seq = seq(r[1], r[2], 1)
			d.ecdf = ecdf(d)
			my.fig(sprintf("doc/interactions_over_platforms/figures/fitness/%s", db), 1, 1)
			cols <- c('red','blue','orange')
			lw <- 2
			legend.names <- paste(c('log-normal', 'gamma', 'power-law'), c(lnorm.D, gamma.D, pl.D), sep=':')
			plot(r.seq, 1 - d.ecdf(r.seq), log = 'xy', pch = 19, cex = .6, main = db, xlab = 'degree', ylab = 'CCDF')
			curve(1 - plnorm(x, lnorm.est[1], lnorm.est[2]), from = r[1], to = r[2], add = T, col = cols[1], lwd = lw)
			curve(1 - pgamma(x, gamma.est[1], gamma.est[2]), from = r[1], to = r[2], add = T, col = cols[2], lwd = lw)
			curve(1 - ppareto(x, plfit.est$xmin, plfit.est$alpha), from = r[1], to = r[2], add = T, col = cols[3], lwd = lw)
			legend('bottomleft', legend.names, col = cols, lwd = lw)
			my.fig.off()
		} else {
			cat(sprintf("%s doesn't exist\n", seq.file))
		}
	}
}
