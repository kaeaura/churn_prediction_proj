# Jing-Kai Lou (kaeaura@gamil.com)
# Tue Mar  6 16:13:33 CST 2012

import matplotlib as mpl
mpl.use("Agg")
import os
import re
import cPickle
import networkx as nx
import numpy as np
import matplotlib.pylab as plt
#from pylab import *
from topology import LiteDB
from scipy import average, array, log10, sqrt


def plot_fig(xdata, ydata, fig_name, title_text = "", xlab = "", ylab = "", **kwargs):
	"""docstring for plot_fig"""
	yerr = 0.1 * ydata
	logx = log10(xdata)
	logy = log10(ydata)
	logyerr = yerr / ydata
	fitfunc = lambda p, x: p[0] + p[1] * x
	errfunc = lambda p, x, y, err: (y - fitfunc(p, x)) / err
	pinit = [2.0, -2.0]
	out = leastsq(errfunc, pinit, args = (logx, logy, logyerr), full_output = 1)
	pfinal = out[0]
	covar = out[1]
	index = pfinal[1]
	amp = 10 ** pfinal[0]
	indexErr = sqrt(covar[0][0])

	clf()
	text(min(xdata) * 2, min(ydata), "Index = %5.2f +/- %5.2f" % (index, indexErr), ha = 'left', va = 'bottom')
	loglog(xdata, ydata, ls = "None", marker = '.')
	loglog(xdata, powerlaw(xdata, amp, index), color = 'r')
	if title_text:
		title(title_text)
	else:
		title('degree distribution')
	if xlab:
		xlabel(xlab)
	if ylab:
		ylabel(ylab)
	grid(True)
	if "ymax" in kwargs:
		ylim(ymax = kwargs["ymax"])
	savefig(fig_name)



def prob_plot_range(data, prop = 'degDistr'):
	xProp = "_".join([prop, 'x'])
	yProp = "_".join([prop, 'y'])
	xValues = set.union(*[set(data[k][xProp]) for k in data.keys() if data.__contains__(k)])
	xmin, xmax = min(*xValues), max(*xValues)
	yValues = set.union(*[set(data[k][yProp]) for k in data.keys() if data.__contains__(k)])
	ymin, ymax = min(*yValues), max(*yValues)
	return(xmin, xmax, ymin, ymax)


def display_mmo(data, realms, fig_name, subs = ['envolop', 'weight', 'friend'], compare = None, prop = 'degDistr', main = 'Degree Distribution', style = 'l', fig_size = (9, 9)):
	keys = []
	for realm in realms:
		keys.extend([ "_".join([ realm, sub, "u" ]) for sub in subs ])
	if compare is not None:
		keys.append(compare)
	subdata = { k: data[k] for k in keys }
	xmin, xmax, ymin, ymax = prob_plot_range(subdata, prop)
	r = realms.__len__()
	c = subs.__len__()
	f, axarr = plt.subplots(nrows = r, ncols = c, figsize = fig_size, sharex = True, sharey = True)
	for realm in realms:
		for sub in subs:
			k = "_".join([realm, sub, "u"])
			if data.__contains__(k):
				xdata = data[k]['_'.join([prop, 'x'])]
				ydata = data[k]['_'.join([prop, 'y'])]
				data_order = [np.argsort(xdata)]
				ri = realms.index(realm)
				ci = subs.index(sub)
				if style == 'l':
					axarr[ri, ci].loglog(xdata[data_order], ydata[data_order])
				else:
					axarr[ri, ci].loglog(xdata[data_order], ydata[data_order], ls = "None", marker = '.')
				axarr[ri, ci].set_title(k, size = 'small')
				axarr[ri, ci].grid(True)
				axarr[ri, ci].set_xlim(xmin, xmax)
				axarr[ri, ci].set_ylim(ymin, ymax)
				if ri == (r - 1): axarr[ri, ci].set_xlabel('k')
				if ci == 0: axarr[ri, ci].set_ylabel(re.sub('Distr', '', prop))
				if compare is not None and data.__contains__(compare):
					if r == 0 and c == 0: 
						axarr[ri, ci].text(xmax, ymax, compare, ha = 'right', va = 'top', size = 'small')
					xdata = data[compare]['_'.join([prop, 'x'])]
					ydata = data[compare]['_'.join([prop, 'y'])]
					plt.axis(size = 'x-small')
					data_order = [np.argsort(xdata)]
					if style == 'l':
						axarr[ri, ci].loglog(xdata[data_order], ydata[data_order], c = 'r')
					else:
						axarr[ri, ci].loglog(xdata[data_order], ydata[data_order], c = 'r', ls = "None", marker = '+')
				f.subplots_adjust(wspace = .1)
	plt.savefig(fig_name)

if __name__ == "__main__":

	path = "../../exp/db"
	pattern = re.compile(r"\w+_DB(_[^_]+)*\.cpickle$")
	fl = filter(lambda x: pattern.match(x) is not None, os.listdir(path))

	d = LiteDB()
	for f in fl:
		d.load(os.path.join(path, f))

	metas = list(set([d[k]['meta'] for k in d.iterkeys()]))

	mmo_keys = [k for k in d.iterkeys() if d[k]['meta'] == 'mmo']
	realms = list(set(map(lambda x: x.split('_')[0], mmo_keys)))
	realms.sort()

	other_testers = list(set(d.keys()).difference(set(mmo_keys)))
	props = ['degDistr', 'ccDistr', 'knnDistr']

	print len(other_testers)
	ot1 = other_testers[:7]
	ot2 = other_testers[7:14]
	ot3 = other_testers[14:]

	if 1:
		for comp in iter(ot3):
			comp_name = comp.split('_')[0]
			meta_name = comp_name.split('-')[0]
			print "--"
			for p in props:
				print (comp, p)
				fig_save_path = os.path.join(p, meta_name)
				if not os.path.exists(fig_save_path):
					os.makedirs(fig_save_path)
				if p == 'degDistr':
					display_mmo(d, realms, fig_name = "%s/Vs__%s.pdf" % (fig_save_path, comp_name), compare = comp, prop = p) 
				else:
					display_mmo(d, realms, fig_name = "%s/Vs__%s.pdf" % (fig_save_path, comp_name), compare = comp, prop = p, style = "+")

