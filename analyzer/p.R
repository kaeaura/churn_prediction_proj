require(ggplot2)
figDir = sprintf('../../fig/fig_%s', strptime(Sys.time(), '%Y-%m-%d'))
if (!file.exists(figDir)) dir.create(figDir)

f = 'xx.csv'
stopifnot(file.exists(f))
df = read.csv(f, header = T, as.is = T)
df$realm = sapply (strsplit(df$dataset, "_"), function(x) x[1])
df$width = sapply (strsplit(df$dataset, "_"), function(x) sub("shift", "", x[3]))
df$degcor = as.numeric(sapply (strsplit(df$degcor, "/"), function(x) x[1]))
df$powerIndex = as.numeric(sapply (strsplit(df$degDistr_fit, "/"), function(x) x[2]))
ddf = subset(df, meta == 'mmo' | meta == 'msg' | meta == 'cit' & width != 'd')

# --
# directed graphs
# users contact others more easily in MMO
g = ggplot(data = subset(df, order >= 1000), aes(x = order, y = size, label = meta))
g + geom_point(aes(color = meta)) + scale_x_log10() + scale_y_log10()
ggsave(file.path(figDir, 'density_global.pdf'))
g = ggplot(data = subset(ddf, realm != 'alice'), aes(x = order, y = size, label = width, color = meta))
g + geom_point() + geom_text(size = 1.5, hjust = 1, vjust = 1) + stat_smooth(method = 'lm', se = T, formula = y ~ x, fullrange = T) + scale_x_log10() + scale_y_log10()
ggsave(file.path(figDir, 'density_growth.pdf'))

# reciprocity
g = ggplot(data = df, aes(x = size, y = recp, label = meta, shape = meta))
g + geom_point(aes(color = meta)) + geom_text(hjust = 1, vjust = 1, angle = 45, size = 1.5)
ggsave(file.path(figDir, 'reciprocity_global.pdf'))
g = ggplot(data = ddf, aes(x = size, y = recp, label = width, shape = meta))
g + geom_point(aes(color = realm)) + geom_text(hjust = 1, vjust = 1, angle = 45, size = 1.5)
ggsave(file.path(figDir, 'reciprocity_growth.pdf'))

# degcor
g = ggplot(data = df, aes(x = size / order, y = degcor, label = meta, shape = meta))
g + geom_point(aes(color = meta)) + geom_text(hjust = 1, vjust = 1, angle = 45, size = 1.5)
ggsave(file.path(figDir, 'degreeCor_global.pdf'))
g = ggplot(data = ddf, aes(x = size, y = degcor, label = width, shape = meta))
g + geom_point(aes(color = realm)) + geom_text(hjust = 1, vjust = 1, angle = 45, size = 1.5)
ggsave(file.path(figDir, 'degreeCor_growth.pdf'))

# assortativity
g = ggplot(data = df, aes(x = size, y = asr, label = meta, shape = meta))
g + geom_point(aes(color = meta)) + geom_text(hjust = 1, vjust = 1, angle = 45, size = 1.5)
ggsave(file.path(figDir, 'assortativity_global.pdf'))
g = ggplot(data = ddf, aes(x = size, y = asr, label = width, shape = meta))
g + geom_point(aes(color = realm)) + geom_text(hjust = 1, vjust = 1, angle = 45, size = 1.5)
ggsave(file.path(figDir, 'assortativity_growth.pdf'))

# powerIndex
g = ggplot(data = df, aes(x = size, y = powerIndex, label = meta, shape = meta))
g + geom_point(aes(color = meta)) + geom_text(hjust = 1, vjust = 1, angle = 45, size = 1.5)
ggsave(file.path(figDir, 'powerIndex_global.pdf'))
g = ggplot(data = ddf, aes(x = size, y = powerIndex, color = meta, label = width, shape = meta))
g + geom_point() + geom_text(hjust = 1, vjust = 1, angle = 45, size = 1.5) + stat_smooth(method = 'lm', se = T, formula = y ~ log(x))
ggsave(file.path(figDir, 'powerIndex_growth.pdf'))
g = ggplot(data = subset(ddf, realm == 'anderson' | realm == 'plurk'), aes(x = size, y = powerIndex, color = meta, label = width, shape = meta))
g + geom_point() + geom_text(hjust = 1, vjust = 1, angle = 45, size = 1.5) + stat_smooth(method = 'lm', se = T, formula = y ~ log(x))
ggsave(file.path(figDir, 'powerIndex_growth.pdf'))


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
g = ggplot(data = df, aes(factor(paste(meta, type)), degDistr_fit))
powerIndex_box_global = g + geom_boxplot(aes(fill = factor(paste(meta, type))))
ggsave(file = 'powerIndex_box_global.pdf', powerIndex_box_global)

# vs order (scatter view)
g = ggplot(data = subset(df, type == 'envolop'), aes(x = order, y = degDistr_fit, label = dataset))
powerIndex_Order_scatter_global = g + geom_point(aes(color = factor(meta)), size = 6) + geom_text(vjust = 0, hjust = 0, angle = 40, size = 3) + scale_x_log10() + ylab('power index') + xlab('order')
ggsave(file = 'powerIndex_Order_scatter_global.pdf', powerIndex_Order_scatter_global)

# vs size (scatter view)
g = ggplot(data = subset(df, type == 'envolop'), aes(x = size, y = degDistr_fit, label = dataset))
powerIndex_Size_scatter_global = g + geom_point(aes(color = factor(meta)), size = 6) + geom_text(vjust = 0, hjust = 0, angle = 40, size = 3) + scale_x_log10() + ylab('power index') + xlab('size')
ggsave(file = 'powerIndex_Size_scatter_global.pdf', powerIndex_Size_scatter_global)

## vs density (scatter view)
g = ggplot(data = subset(df, type == 'envolop'), aes(x = size / (order ** 2), y = degDistr_fit, label = dataset))
powerIndex_Density_scatter_global = g + geom_point(aes(color = factor(meta)), size = 6) + geom_text(vjust = 0, hjust = 0, angle = 40, size = 3) + scale_x_log10() + ylab('power index') + xlab('density')
ggsave(file = 'powerIndex_Density_scatter_global.pdf', powerIndex_Density_scatter_global)


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
