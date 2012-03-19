require(ggplot2)
require(reshape)
figDir = sprintf('../../fig/fig_%s', strptime(Sys.time(), '%Y-%m-%d'))
if (!file.exists(figDir)) dir.create(figDir)

fn = 'temp.csv'
df = read.csv(fn, header = T, as.is = T)
df$realm = sapply (strsplit(df$dataset, "_"), function(x) x[1])
df$width = sapply (strsplit(df$dataset, "_"), function(x) sub("shift", "", x[3]))
df$degcor = as.numeric(sapply (strsplit(df$degcor, "/"), function(x) x[1]))
df$d.power.index = as.numeric(sapply (strsplit(df$degDistr_fit, "/"), function(x) x[2]))
df$i.power.index = as.numeric(sapply (strsplit(df$inDegDistr_fit, "/"), function(x) x[2]))
df$o.power.index = as.numeric(sapply (strsplit(df$outDegDistr_fit, "/"), function(x) x[2]))

m = melt(df, id = c('realm', 'meta', 'order', 'size'), measure.vars = c('d.power.index', 'i.power.index', 'o.power.index'))
sm = subset(m, realm == 'anderson' | realm == 'plurk' | realm == 'cit-HepTh')
g = ggplot(data = sm, aes(x = size/order, y = value, shape = factor(variable), color = realm))
g + geom_point() + scale_x_log10() + stat_smooth(method = 'lm', se = T, formula = y ~ log(x))
ggsave(file.path(figDir, 'powerIndex_direction.pdf'))

# ---------------------------------------------------------------
fn = 'xx.csv'
fn = 'dir.csv'
fn = 'temp1.csv'
stopifnot(file.exists(fn))
df = read.csv(fn, header = T, as.is = T)
df$realm = sapply (strsplit(df$dataset, "_"), function(x) x[1])
df$width = sapply (strsplit(df$dataset, "_"), function(x) sub("shift", "", x[3]))
df$degcor = as.numeric(sapply (strsplit(df$degcor, "/"), function(x) x[1]))
df$power.index = as.numeric(sapply (strsplit(df$degDistr_fit, "/"), function(x) x[2]))
df$d.power.index = as.numeric(sapply (strsplit(df$degDistr_fit, "/"), function(x) x[2]))
df$i.power.index = as.numeric(sapply (strsplit(df$inDegDistr_fit, "/"), function(x) x[2]))
df$o.power.index = as.numeric(sapply (strsplit(df$outDegDistr_fit, "/"), function(x) x[2]))
ddf = subset(df, meta == 'mmo' | meta == 'msg' | meta == 'cit' & width != 'd')

# --
# directed graphs
# users contact others more easily in MMO
g = ggplot(data = subset(df, type == 'static'), aes(x = order, y = size, label = realm))
f = g + geom_point(aes(color = meta)) + geom_text(hjust = 0, vjust = 0, color = 'black', size = 2.5) + scale_x_log10() + scale_y_log10()
f + stat_smooth(method = 'lm', se = T)
ggsave(file.path(figDir, 'density_global.pdf'))

g = ggplot(data = subset(df, type == 'dynamic'), aes(x = order, y = size, label = paste(realm, width, sep='-'), color = meta))
f = g + geom_point(aes(shape = meta)) + geom_text(hjust = 1, vjust = 1, color = 'black', size = 2.5, angle = -35) + scale_x_log10() + scale_y_log10() 
f + stat_smooth(method = 'lm', se = T, formula = y ~ x) 
ggsave(file.path(figDir, 'density_tmp.pdf'))

g = ggplot(data = subset(df, type == 'static'), aes(x = factor(meta), y = d.power.index, fill = factor(meta)))
f = g + geom_boxplot()
ggsave(file = file.path(figDir, 'power.index_box_global.pdf'), power.index_box_global)

g = ggplot(data = subset(ddf, type == 'dynamic' & meta == 'mmo'), aes(x = order, y = size, label = width, color = realm))
f = g + geom_point() + scale_x_log10() + scale_y_log10()
f + stat_smooth(method = 'lm', se = T, formula = y ~ x, fullrange = T) + facet_wrap(~ realm)
ggsave(file.path(figDir, 'density_mmo.pdf'))

dy.df = subset(df, type == 'dynamic')
dy.df = ddply(dy.df, .(realm), transform, dpl_coef = coef(lm(log(size) ~ log(order)))[2], dpl_rsquared = summary(lm(log(size) ~ log(order)))$r.squared)
m = melt(dy.df, id = c('meta', 'realm'), measure.vars = c('dpl_coef','dpl_rsquared'))
mc = cast(m, meta + realm ~ variable, unique)
g = ggplot(mc, aes(x = realm, y = dpl_coef, fill = meta, label = sprintf("coef: %s R2: %s", format(dpl_coef, digits = 3), format(dpl_rsquared, digits = 2))))
f = g + geom_bar(position = 'dodge', stat = 'identity') + ylab('densification power index') + geom_text(hjust = 1, size = 3.5) + coord_flip()
ggsave(file.path(figDir, 'densityGrowthIndex_tmp.pdf'))

# reciprocity
g = ggplot(data = df, aes(x = size, y = recp, label = realm, shape = type))
g + geom_point(aes(color = meta)) + geom_text(hjust = 0, vjust = 1, angle = 33, size = 2)
ggsave(file.path(figDir, 'reciprocity_global.pdf'))
g = ggplot(data = subset(ddf, type == 'dynamic'), aes(x = size, y = recp, label = width, shape = meta))
g + geom_point(aes(color = realm)) + geom_line(aes(color = realm)) + scale_x_log10()
ggsave(file.path(figDir, 'reciprocity_tmp.pdf'))
g = ggplot(data = subset(ddf, meta == 'mmo'), aes(x = size, y = recp, label = width))
g + geom_line(aes(color = realm)) + geom_point(aes(color = realm))
ggsave(file.path(figDir, 'reciprocity_mmo.pdf'))

# degcor
g = ggplot(data = df, aes(x = size, y = degcor, label = meta, shape = meta))
g + geom_point(aes(color = meta)) + geom_text(hjust = 1, vjust = 1, angle = 45, size = 1.5) + scale_x_log10()
ggsave(file.path(figDir, 'degreeCor_global.pdf'))
g = ggplot(data = ddf, aes(x = size, y = degcor, label = width, shape = meta))
g + geom_point(aes(color = realm)) + geom_text(hjust = 1, vjust = 1, angle = 45, size = 1.5) + scale_x_log10()
ggsave(file.path(figDir, 'degreeCor_tmp.pdf'))

# assortativity
g = ggplot(data = df, aes(x = size, y = asr, label = meta, shape = meta))
g + geom_point(aes(color = meta)) + geom_text(hjust = 1, vjust = 1, angle = 45, size = 1.5)
ggsave(file.path(figDir, 'assortativity_global.pdf'))
g = ggplot(data = ddf, aes(x = size, y = asr, label = width, shape = meta))
g + geom_point(aes(color = realm)) + geom_text(hjust = 1, vjust = 1, angle = 45, size = 1.5)
ggsave(file.path(figDir, 'assortativity_tmp.pdf'))

# power.index
g = ggplot(data = df, aes(x = size, y = power.index, label = meta, shape = meta))
g + geom_point(aes(color = meta)) + scale_x_log10()
ggsave(file.path(figDir, 'power.index_global.pdf'))
g = ggplot(data = subset(ddf, realm == 'cit-HepTh' | realm == 'anderson' | realm == 'plurk'), aes(x = size / order, y = power.index, color = meta, label = width, shape = meta))
g + geom_point() + geom_text(hjust = 0, vjust = 0, size = 1.5, color = 'black') + stat_smooth(method = 'lm', se = T, formula = y ~ x) + scale_x_log10()
ggsave(file.path(figDir, 'power.index_tmp.pdf'))

# ------------------------------------------
# undirected
# older 
f = 'aa.csv'

df = read.csv(f, header = T, as.is = T)
df$dname = paste(df$dataset, df$type, sep = '_')
idx = which(df$meta == 'mmo' & df$type == 'envolop')
sdf = df[-idx,]

# section order and size
# mmo comparison : friend network vs weight network
g = ggplot(data = subset(df, type != 'envolop' & meta == 'mmo'), aes(x = order, y = size, label = dname))
density_scatter_mmo = g + geom_point(aes(color = dataset), size = 6) + geom_text(vjust = 0, hjust = 0, angle = 90, size = 3) + facet_wrap(~ type) + stat_smooth(method = 'lm', formula = y ~ poly(x, 1), se = T) + scale_x_log10() + scale_y_log10()
ggsave(file = "density_scatter_mmo.pdf", density_scatter_mmo)

# global comparison network size and order:
g = ggplot(data = subset(df, type == 'envolop'), aes(x = order, y = size, label = dataset))
density_scatter_global = g + geom_point(aes(color = factor(meta)), size = 6) + geom_text(vjust = 0, hjust = 0, angle = 0, size = 3) + scale_x_log10() + scale_y_log10() + stat_smooth(method = 'lm', se = T)
ggsave(file = 'density_scatter_global.pdf', density_scatter_global)

# global comparison network size and order with multiple lm
g = ggplot(data = subset(sdf, meta %in% c('mmo', 'p2p', 'ca', 'purchasing')), aes(x = order, y = size, label = dataset, color = factor(paste(meta, type))))
density_scatter_global = g + geom_point(size = 6) + geom_text(vjust = 0, hjust = 0, angle = 0, size = 3) + scale_x_log10() + scale_y_log10() + stat_smooth(method = 'lm', se = T, fullrange = F)
ggsave(file = 'density_scatter_global_multiLM.pdf', density_scatter_global)

## power-law index
# (boxplot view)

# vs order (scatter view)
g = ggplot(data = subset(df, type == 'envolop'), aes(x = order, y = degDistr_fit, label = dataset))
power.index_Order_scatter_global = g + geom_point(aes(color = factor(meta)), size = 6) + geom_text(vjust = 0, hjust = 0, angle = 40, size = 3) + scale_x_log10() + ylab('power index') + xlab('order')
ggsave(file = 'power.index_Order_scatter_global.pdf', power.index_Order_scatter_global)

# vs size (scatter view)
g = ggplot(data = subset(df, type == 'envolop'), aes(x = size, y = degDistr_fit, label = dataset))
power.index_Size_scatter_global = g + geom_point(aes(color = factor(meta)), size = 6) + geom_text(vjust = 0, hjust = 0, angle = 40, size = 3) + scale_x_log10() + ylab('power index') + xlab('size')
ggsave(file = 'power.index_Size_scatter_global.pdf', power.index_Size_scatter_global)

## vs density (scatter view)
g = ggplot(data = subset(df, type == 'envolop'), aes(x = size / (order ** 2), y = degDistr_fit, label = dataset))
power.index_Density_scatter_global = g + geom_point(aes(color = factor(meta)), size = 6) + geom_text(vjust = 0, hjust = 0, angle = 40, size = 3) + scale_x_log10() + ylab('power index') + xlab('density')
ggsave(file = 'power.index_Density_scatter_global.pdf', power.index_Density_scatter_global)


## asr
g = ggplot(data = sdf, aes(x = size, y = asr, label = dataset))
assort_Size_scatter_global = g + geom_point(aes(color = paste(meta, type), shape = factor(type)), size = 6) + geom_text(vjst = 0, hjust = 0, size = 2) + scale_x_log10() + ylab('assortativity') + xlab('size')
ggsave(file = 'assort_Size_scatter_global.pdf', assort_Size_scatter_global)

## vs size (scatter view)
#g = ggplot(data = subset(df, type == 'envolop'), aes(x = size, y = asr, label = dataset))
#assort_Size_scatter_global = g + geom_point(aes(color = factor(meta)), size = 6) + geom_text(vjust = 0, hjust = 0, angle = 40, size = 3) + scale_x_log10() + yl#ab('assortativity') + xlab('Size')
#ggsave(file = 'assort_Size_scatter_global.pdf', assort_Size_scatter_global)

## vs size (scatter view)
#g = ggplot(data = subset(df, type == 'envolop'), aes(x = size, y = asr, label = dataset))
#assort_Size_scatter_global = g + geom_point(aes(color = factor(meta)), size = 6) + geom_text(vjust = 0, hjust = 0, angle = 40, size = 3) + scale_x_log10() + ylab('assortativity') + xlab('size')
#ggsave(file = 'assort_Size_scatter_global.pdf', assort_Size_scatter_global)

# index vs asr
g = ggplot(data = sdf, aes(x = degDistr_fit, y = asr, label = dataset))
assort_Index_scatter_global = g + geom_point(aes(color = paste(meta, type), shape = factor(type)), size = 6) + geom_text(vjst = 0, hjust = 0, size = 2) + ylab('assortativity') + xlab('power index') + stat_smooth(method = 'lm', formula = y ~ poly(x, 2), se = T)
ggsave(file = 'assort_Index_scatter_global.pdf', assort_Index_scatter_global)

g = ggplot(data = subset(sdf, meta == 'mmo'), aes(x = degDistr_fit, y = asr, label = dataset))
assort_Index_scatter_mmo = g + geom_point(aes(color = paste(meta, type), shape = factor(type)), size = 6) + geom_text(vjst = 0, hjust = 0, size = 2) + ylab('assortativity') + xlab('power index') + stat_smooth(method = 'lm', formula = y ~ poly(x, 2), se = T)
ggsave(file = 'assort_Index_scatter_mmo.pdf', assort_Index_scatter_mmo)
