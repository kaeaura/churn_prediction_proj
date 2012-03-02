# Jing-Kai Lou (kaeaura@gamil.com)
require(ggplot2)
fig.dir = "../../fig"
date.format = "%Y/%m/%d"
dsecs = 86400
w.order = c("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

argv = commandArgs(TRUE)
argc = length(argv)

if (argc == 2) {
	readFolder = argv[1]
	readRealm = argv[2]
}


Generate.Temporal.Data <- function(readFolder, readRealm, line.size = 1.2, is.plot = F) {
	
	fl = list.files(readFolder, sprintf("^%s_[a-z]+_[0-9]+d\\.csv$", readRealm), full.names = T)

	u.df = d.df = data.frame()
	for (fn in fl) {
		cat(sprintf("reading file: %s ... ", basename(fn)))
		fFeatures = unlist(strsplit(sub(".csv", "", basename(fn), fixed = T), '_'))
		if (length(fFeatures) == 3 && fFeatures[1] == readRealm) {
			is.directed = ifelse(fFeatures[2] == "directed", T, F)
			lifespan = fFeatures[3]
			t.df = read.csv(fn, header = T)
			t.df = transform(	t.df, 
								w.date = strftime(strptime(t.df$date, date.format), "%a"), 
								epoch.date = as.numeric(strptime(t.df$date, date.format))
					)
			t.df = transform(	t.df, 
								i.date = 1 + ((epoch.date - min(epoch.date)) / dsecs),
								is.directed = is.directed,
								lifespan = lifespan
					)
			if (is.directed) {
				cat(sprintf("as directed graph\n"))
				d.df = rbind(d.df, t.df)
			} else {
				cat(sprintf("as undirected graph\n"))
				u.df = rbind(u.df, t.df)
			}
		} else {
			next
		}
	}

	if (nrow(u.df)) u.df$w.date = factor(as.character(u.df$w.date), label = w.order)
	if (nrow(d.df)) {
		d.df$w.date = factor(as.character(d.df$w.date), label = w.order)
		if ('rei' %in% names(d.df))
			d.df$rei = as.numeric(as.character(d.df$rei))
	}

	if (is.plot) {
		current.time = strftime(Sys.time(), "%Y-%m-%d")
		fig.path = file.path(fig.dir, sprintf("fig_%s", current.time))
		if (!file.exists(fig.path) || !file.info(fig.path)$isdir) dir.create(fig.path, recursive = T)
		
		# for directed
		if (nrow(u.df)) {
			fn.header = sprintf("%s_u", readRealm)

			# temporal order
			g = ggplot(data = u.df, aes(x = i.date, y = cc))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Clustering coefficient")
			ggsave(q, filename = file.path(fig.path, sprintf("clustering_%s.pdf", fn.header)))
		}

		if (nrow(d.df)) {
			fn.header = sprintf("%s_d", readRealm)

			# temporal order
			g = ggplot(data = d.df, aes(x = i.date, y = order))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Number of users")
			ggsave(q, filename = file.path(fig.path, sprintf("order_%s.pdf", fn.header)))

			# temporal order
			g = ggplot(data = d.df, aes(x = i.date, y = gender_order / order))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Male users ratio")
			ggsave(q, filename = file.path(fig.path, sprintf("gender_ratio_%s.pdf", fn.header)))

			# temporal family order
			g = ggplot(data = d.df, aes(x = i.date, y = f_order/order))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Ratio of family members")
			ggsave(q, filename = file.path(fig.path, sprintf("f_orderRatio_%s.pdf", fn.header)))

			# temporal order
			g = ggplot(data = d.df, aes(x = i.date, y = f_gender_order / f_order))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Family male users ratio")
			ggsave(q, filename = file.path(fig.path, sprintf("gender_ratio_%s.pdf", fn.header)))

			# temporal degree
			g = ggplot(data = d.df, aes(x = i.date, y = degree))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Average number of acquaintances")
			ggsave(q, filename = file.path(fig.path, sprintf("degree_%s.pdf", fn.header)))

			# temporal family degree
			g = ggplot(data = d.df, aes(x = i.date, y = f_degree / degree))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Average number of acquaintances ratio")
			ggsave(q, filename = file.path(fig.path, sprintf("f_degreeRatio_%s.pdf", fn.header)))

			# temporal reciprocity
			g = ggplot(data = d.df, aes(x = i.date, y = rep))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Degree reciprocity")
			ggsave(q, filename = file.path(fig.path, sprintf("reciprocity_%s.pdf", fn.header)))

			# temporal reciprocity
			g = ggplot(data = d.df, aes(x = i.date, y = f_rep))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Family degree reciprocity")
			ggsave(q, filename = file.path(fig.path, sprintf("f_reciprocity_%s.pdf", fn.header)))

			# temporal reinforcement
			g = ggplot(data = d.df, aes(x = i.date, y = as.numeric(as.character(rei))))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Reinforcement")
			ggsave(q, filename = file.path(fig.path, sprintf("reinforcement_%s.pdf", fn.header)))

			# temporal reinforcement
			g = ggplot(data = d.df, aes(x = i.date, y = as.numeric(as.character(f_rei))))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Family Reinforcement")
			ggsave(q, filename = file.path(fig.path, sprintf("f_reinforcement_%s.pdf", fn.header)))

			# temporal assortativity
			g = ggplot(data = d.df, aes(x = i.date, y = asr))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Degree assortativity")
			ggsave(q, filename = file.path(fig.path, sprintf("assortativity_%s.pdf", fn.header)))

			g = ggplot(data = d.df, aes(x = i.date, y = f_asr))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Family degree assortativity")
			ggsave(q, filename = file.path(fig.path, sprintf("f_assortativity_%s.pdf", fn.header)))

			g = ggplot(data = d.df, aes(x = i.date, y = asr_gender))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Gender assortativity")
			ggsave(q, filename = file.path(fig.path, sprintf("gender_assortativity_%s.pdf", fn.header)))

			g = ggplot(data = d.df, aes(x = i.date, y = f_asr_gender))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Family Gender assortativity")
			ggsave(q, filename = file.path(fig.path, sprintf("gender_assortativity_%s.pdf", fn.header)))
			# --
	#		g = ggplot(data = d.df, aes(x = w.date, y = rep))
	#		g + geom_point(position = 'jitter') + facet_wrap(~lifespan)
	#
	#		g = ggplot(data = subset(d.df, i.date > 150 & i.date <= 200), aes(x = i.date, y = order))
	#		g + geom_point(aes(colour = factor(lifespan)))
	#
	#		g = ggplot(data = subset(d.df, i.date > 150 & i.date <= 200), aes(factor(w.date), degree))
	#		g + geom_boxplot() + facet_wrap( ~ lifespan)
	#
	#		g = ggplot(data = , aes(factor(w.date), degree))
	#		g + geom_boxplot() + facet_wrap( ~ lifespan)
		}
	}

	return(list(d = d.df, u = u.df))
}


Generate.Temporal.Datas <- function(readFolder, readRealms, line.size = 1, is.plot = F) {
	g.list = list()
	for (r in readRealms) {
		g.list[[r]] = Generate.Temporal.Data(readFolder, r, line.size = line.size, is.plot = F)
	}
	d.df = ldply(lapply(g.list, function(x) x$d))
	u.df = ldply(lapply(g.list, function(x) x$u))
	z = list(d = d.df, u = u.df)

	if (is.plot) {
		current.time = strftime(Sys.time(), "%Y-%m-%d")
		fig.path = file.path(fig.dir, sprintf("fig_%s", current.time))
		if (!file.exists(fig.path) || !file.info(fig.path)$isdir) dir.create(fig.path, recursive = T)

		if (nrow(z$u)) {
			# TODO danger!! modify it
			z$u$order = z$d$order

			print ("uuuu")
			fn.header = "all_u"
			u.m = melt(z$u, id = ".id", measure.vars = "i.date")
			u.c = cast(u.m, variable ~ .id, max)
			i.date.upper = min(subset(u.c, select = -variable))

			# temporal clustering
			g = ggplot(data = subset(z$u, i.date <= i.date.upper), aes(x = i.date, y = cc))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Clustering coefficient") + facet_wrap(~.id)
			ggsave(q, filename = file.path(fig.path, sprintf("clustering_%s.pdf", fn.header)))

			# temporal normalized clustering
			g = ggplot(data = subset(z$u, i.date <= i.date.upper), aes(x = i.date, y = cc * (order * (order - 1)) / (2 *size)))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Normalized clustering coefficient") + facet_wrap(~.id)
			ggsave(q, filename = file.path(fig.path, sprintf("NormClustering_%s.pdf", fn.header)))

			# temporal gcc_ratio
			g = ggplot(data = subset(z$u, i.date <= i.date.upper), aes(x = i.date, y = gcc_order / order))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Giant component ratio") + facet_wrap(~.id)
			ggsave(q, filename = file.path(fig.path, sprintf("gccRatio_%s.pdf", fn.header)))
		}

		if (nrow(z$d)) {
			print ("dddd")
			fn.header = "all_d"
			d.m = melt(z$u, id = ".id", measure.vars = "i.date")
			d.c = cast(d.m, variable ~ .id, max)
			i.date.upper = min(subset(d.c, select = -variable))

			# temporal order
			g = ggplot(data = subset(z$d, i.date <= i.date.upper), aes(x = i.date, y = order))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Number of users") + facet_wrap(~.id)
			ggsave(q, filename = file.path(fig.path, sprintf("order_%s.pdf", fn.header)))

			# temporal male order
			g = ggplot(data = subset(z$d, i.date <= i.date.upper), aes(x = i.date, y = gender_order / order))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Male users ratio") + facet_wrap(~.id)
			ggsave(q, filename = file.path(fig.path, sprintf("gender_ratio_%s.pdf", fn.header)))

			# family order
			g = ggplot(data = ,subset(z$d, i.date <= i.date.upper), aes(x = i.date, y = f_order/order))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Ratio of family members") + facet_wrap(~.id)
			ggsave(q, filename = file.path(fig.path, sprintf("f_orderRatio_%s.pdf", fn.header)))

			# temporal degree
			g = ggplot(data = subset(z$d, i.date <= i.date.upper), aes(x = i.date, y = degree))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Average number of acquaintances") + facet_wrap(~.id)
			ggsave(q, filename = file.path(fig.path, sprintf("degree_%s.pdf", fn.header)))

			# temporal reciprocity
			g = ggplot(data = subset(z$d, i.date <= i.date.upper), aes(x = i.date, y = rep))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Reciprocity") + facet_wrap(~.id)
			ggsave(q, filename = file.path(fig.path, sprintf("reciprocity_%s.pdf", fn.header)))

			# temporal reinforcement
			g = ggplot(data = subset(z$d, i.date <= i.date.upper), aes(x = i.date, y = as.numeric(rei)))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Reinforcement") + facet_wrap(~.id)
			ggsave(q, filename = file.path(fig.path, sprintf("reinforcement_%s.pdf", fn.header)))

			# assortativity
			g = ggplot(data = subset(z$d, i.date <= i.date.upper), aes(x = i.date, y = asr))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Degree assortativity") + facet_wrap(~.id)
			ggsave(q, filename = file.path(fig.path, sprintf("assortativity_%s.pdf", fn.header)))

			g = ggplot(data = subset(z$d, i.date <= i.date.upper), aes(x = i.date, y = asr_gender))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Gender assortativity") + facet_wrap(~.id)
			ggsave(q, filename = file.path(fig.path, sprintf("gender_assortativity_%s.pdf", fn.header)))

			g = ggplot(data = subset(z$d, i.date <= i.date.upper), aes(x = i.date, y = f_asr))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Family degree assortativity") + facet_wrap(~.id)
			ggsave(q, filename = file.path(fig.path, sprintf("f_assortativity_%s.pdf", fn.header)))

			g = ggplot(data = subset(z$d, i.date <= i.date.upper), aes(x = i.date, y = f_asr_gender))
			q = g + geom_line(aes(colour = lifespan, linetype = lifespan), size = line.size) + xlab("Days") + ylab("Family Gender assortativity") + facet_wrap(~.id)
			ggsave(q, filename = file.path(fig.path, sprintf("f_gender_assortativity_%s.pdf", fn.header)))
		}
	}

	return(z)
}

if (argc)
	Generate.Temporal.Datas(readFolder, readRealm, is.plot=T)
