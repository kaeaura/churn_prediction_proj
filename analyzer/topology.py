# Jing-Kai Lou (kaeaura@gamil.com)
# Sun Feb 26 15:17:41 CST 2012

import matplotlib as mpl
mpl.use('Agg')
# for server rendering plots without X server
import os
import sys
import time
import getopt
import networkx as nx
import evolution as ev
from pylab import *
from scipy import average
from scipy.optimize import leastsq
from collections import Counter, defaultdict

__author__ = "Jing-Kai Lou (kaeaura@gmail.com)"

powerlaw = lambda x, amp, index: amp * (x**index)

def average_degree(g):
	"""docstring for average_degree"""
	d = g.degree()
	return(float(sum(d.values())) / g.order())

def norm_cc(g):
	"""docstring for norm_cc"""
	c = nx.average_clustering(g)
	rc = float(g.size() * 2) / (g.order() * (g.order() - 1))
	return(c / rc if rc > 0 else 0)

def reinforce(g, weight = 'weight'):
	w = nx.get_edge_attributes(g, weight)
	return(filter(lambda x: x > 1, w.values()).__len__() / float(w.__len__()))

def reciprocity(g, normalized = True):
	"""docstring for reciprocity"""
	assert(g.is_directed())
	L = set(g.edges()).difference(set(g.selfloop_edges()))
	Lb = set()
	for e in L:
		Lb.add(frozenset(e))
	n = g.order()
	r = float(len(Lb)) / len(L)
	a = float(len(L)) / (n * (n - 1))
	rho = ((r - a) / (1 - a)) if len(Lb) else (-a / (1 - a))
	if normalized:
		return(rho)
	else:
		return(r)

def powerlaw_fit(xdata, ydata, err = 0.1):
	yerr = err * ydata
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

	return(amp, index, indexErr)

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


def plot_degree_distribution(g, fig_name, title_text = "degree distribution", y_max = 1, is_plot = False):
	c = Counter()
	for d in g.degree().itervalues():
		c[d] += 1
	d = dict(c)
	if d.__contains__(0):
		d.__delitem__(0)
	xdata = array(d.keys())
	ydata = array(map(lambda x: float(x) / sum(d.values()), d.itervalues()))
	if is_plot:
		plot_fig(xdata, ydata, fig_name = fig_name, title_text = title_text, xlab = 'degree k', ylab = 'P(k)')
	return(xdata, ydata)

def plot_cluster_distribution(g, fig_name, title_text = "clustering distribution", is_plot = False):
	if g.is_directed():
		print ("function plot_cluster_distribution works only for undirected graphs")
		return(None)
	k = nx.clustering(g)
	d = g.degree()
	ck = defaultdict(list)
	for n in g.nodes_iter():
		ck[d[n]].append(k[n])
	xdata, ydata = list(), list()
	for x, y in ck.iteritems():
		if x > 1 and average(y) > 0:
			xdata.append(x)
			ydata.append(average(y))

	xdata = array(xdata)
	ydata = array(ydata)
	if is_plot:
		plot_fig(xdata, ydata, fig_name, title_text, xlab = 'degree k', ylab = 'clustering C(k)')
	return(xdata, ydata)

def plot_degree_correlation(g, fig_name, title_text = "degree correlation", is_plot = False):
	"""docstring for plot_degree_correlation"""
	k = nx.average_neighbor_degree(g)
	d = g.degree()
	ck = defaultdict(list)
	for n in g.nodes_iter():
		ck[d[n]].append(k[n])
	xdata, ydata = list(), list()
	for x, y in ck.iteritems():
		if x > 0 and average(y) > 0:
			xdata.append(x)
			ydata.append(average(y))

	xdata = array(xdata)
	ydata = array(ydata)
	if is_plot:
		plot_fig(xdata, ydata, fig_name, title_text = title_text, xlab = "degree k", ylab = "Knn(k)")
	return(xdata, ydata)

class MORPGraph():
	def __init__(self, g):
		"""docstring for __init__"""
		self.hete = g
	def _itemToTuple(self, item):
		"""docstring for _itemToTuple"""
		(i, j), y = item
		y = len(y) if dir(y).__contains__('__len__') else y
		return((i, j, y))
	def extract_edges(self, edge_attr):
		"""docstring for extract"""
		subED = nx.get_edge_attributes(self.hete, edge_attr)
		subE = map(lambda x: self._itemToTuple(x), subED.items())
		sg = nx.DiGraph() if self.hete.is_directed() else nx.Graph()
		if subE:
			sg.add_weighted_edges_from(subE, weight = edge_attr)
		return(sg)
	def extract_nodes(self, node_attr):
		subND = nx.get_node_attributes(self.hete, node_attr)
		sg = self.hete.subgraph(subND.keys())
		return(sg)
	def overlap(self, edge_attrA = 'weight', edge_attrB = 'friend'):
		"""docstring for overlap"""
		setA = set(nx.get_edge_attributes(self.hete, edge_attrA).keys())
		setB = set(nx.get_edge_attributes(self.hete, edge_attrB).keys())
		return(setA.intersection(setB))
	def utility(self, edge_attrA = 'weight', edge_attrB = 'friend'):
		w = nx.get_edge_attributes(self.hete, edge_attrA)
		totalW = sum(map(lambda x: x.__len__(), w.itervalues()))
		ut = float(0)
		for interEdge in self.overlap():
			ut += w[interEdge].__len__()
		return(ut / totalW)
	def envolop(self):
		act = nx.get_node_attributes(self.hete, 'account')
		uniq_act = list(set(act.values()))

def main(argv):
	"""docstring for main"""
	inputFile = ""
	inputIsPickle = True
	outputFile = ""
	realm = ""
	enableVerbose = False
	enableMMOG = False
	enablePlot = False
	show_fit = False
	ofs = ","

	def usage():
		"""docstring for usage"""
		print ("--")
		print ("read the gpickles to analyze")
		print
		print ("\t-h, --help: print this usage")
		print ("\t-i: inputFile (gpickle)")
		print ("\t-e: inputFile type = edgelist")
		print ("\t-o: outputFile")
		print ("\t-r: realm")
		print ("\t-v: verbose")
		print ("\t-M: MMOG trace format")
		print ("\t-D: plot degree distribution")

	try:
		opts, args = getopt.getopt(argv, "hi:eo:r:vMD", ["help"])
	except getopt.GetoptError, err:
		print ("The given argv incorrect")
		usage()
		print (err)
		sys.exit(2)

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt in ("-i"):
			inputFile = arg
		elif opt in ("-e"):
			inputIsPickle = False
		elif opt in ("-o"):
			outputFile = arg
		elif opt in ("-r"):
			realm = arg
		elif opt in ("-v"):
			enableVerbose = True
		elif opt in ("-M"):
			enableMMOG = True
		elif opt in ("-D"):
			enablePlot = True

	if enableVerbose:
		print ("inputFile: %s" % inputFile)
		print ("outputFile: %s" % outputFile)
		print ("realm: %s" % realm)
		print ("enableVerbose: %s" % enableVerbose)
		print ("enableMMOG: %s" % enableMMOG)

	if realm == "":
		realm = os.path.basename(inputFile)

	assert(os.path.exists(inputFile))
	if inputIsPickle:
		g = nx.read_gpickle(file(inputFile, "r"))
	else:
		g = nx.read_edgelist(inputFile, nodetype = int)

	if enableMMOG:
		m = MORPGraph(g)
		f = m.extract_edges('friend')
		w = m.extract_edges('weight')
		test_graph_names = [realm + "_all", realm + "_friend", realm + "_chat"]
		test_graphs = [g, f, w]
	else:
		test_graph_names = [realm]
		test_graphs = [g]

	if outputFile:
		tDict = dict()
		tDict.__setitem__('order', map(lambda x: x.order(), test_graphs))
		tDict.__setitem__('size', map(lambda x: x.size(), test_graphs))
		tDict.__setitem__('degree', map(lambda x: average_degree(x), test_graphs))
		tDict.__setitem__('asr', map(lambda x: nx.degree_assortativity_coefficient(x), test_graphs))
		if g.is_directed():
			tDict.__setitem__('rep', map(lambda x: reciprocity(x), test_graphs))
			#tDict.__setitem__('rei', map(lambda x: reinforce(x), test_graphs))
		else:
			tDict.__setitem__('cc', map(lambda x: nx.average_clustering(x), test_graphs))
			tDict.__setitem__('norm_cc', map(lambda x: norm_cc(x), test_graphs))

		outputDir = os.path.dirname(outputFile)
		if outputDir and not (os.path.exists(outputDir)):
			os.makedirs(outputDir)

		with open(outputFile, "w") as F:
			if tDict.__len__():
				ks = tDict.keys()
				F.write("%s\n" % ("graph" + ofs + ofs.join(ks)))
				for tIndex in xrange(test_graphs.__len__()):
					rownameFields = test_graph_names[tIndex]
					contentFields = ofs.join(map(lambda x: str(x[tIndex]), tDict.itervalues()))
					F.write("%s\n" % ofs.join([rownameFields, contentFields]))

	if enablePlot:
		if enableMMOG:
			# degree distribution -- 
			chat_dd_x, chat_dd_y = plot_degree_distribution(w, 'xx')
			chat_dd_amp, chat_dd_index, chat_dd_indexErr = powerlaw_fit(chat_dd_x, chat_dd_y)
			fd_dd_x, fd_dd_y = plot_degree_distribution(f, 'xx')
			fd_dd_amp, fd_dd_index, fd_dd_indexErr = powerlaw_fit(fd_dd_x, fd_dd_y)

			clf()
			loglog(chat_dd_x, chat_dd_y, linestyle = "None", marker = '.', color = 'r', label = 'Chat')
			loglog(fd_dd_x, fd_dd_y, linestyle = "None", marker = '+', color = 'b', label = 'Friend')
			if show_fit:
				loglog(chat_dd_x, powerlaw(chat_dd_x, chat_dd_amp, chat_dd_index), color = 'k', label = 'Chat fit')
				loglog(fd_dd_x, powerlaw(fd_dd_x, fd_dd_amp, fd_dd_index), color = 'k', label = 'Friend fit')
			legend(["Chat %.2f +/- %.2f" % (chat_dd_index, chat_dd_indexErr), "Friend %.2f +/- %.2f" % (fd_dd_index, fd_dd_indexErr)])
			title('degree distribution')
			xlabel('degree k')
			ylabel('P(k)')
			savefig('%s_fd_chat_degDistr.png' % realm)

			# clustering coefficient -- 
			chat_cc_x, chat_cc_y = plot_cluster_distribution(w, 'xx')
			chat_cc_amp, chat_cc_index, chat_cc_indexErr = powerlaw_fit(chat_cc_x, chat_cc_y)
			fd_cc_x, fd_cc_y = plot_cluster_distribution(f, 'xx')
			fd_cc_amp, fd_cc_index, fd_cc_indexErr = powerlaw_fit(fd_cc_x, fd_cc_y)

			clf()
			loglog(chat_cc_x, chat_cc_y, linestyle = "None", marker = '.', color = 'r', label = 'Chat')
			loglog(fd_cc_x, fd_cc_y, linestyle = "None", marker = '+', color = 'b', label = 'Friend')
			if show_fit:
				loglog(chat_cc_x, powerlaw(chat_cc_x, chat_cc_amp, chat_cc_index), color = 'k', label = 'Chat fit')
				loglog(fd_cc_x, powerlaw(fd_cc_x, fd_cc_amp, fd_cc_index), color = 'k', label = 'Friend fit')
			legend(["Chat %.2f +/- %.2f" % (chat_cc_index, chat_cc_indexErr), "Friend %.2f +/- %.2f" % (fd_cc_index, fd_cc_indexErr)])
			title('clustering distribution')
			xlabel('degree k')
			ylabel('C(k)')
			savefig('%s_fd_chat_ccDistr.png' % realm)

			# degree correlation -- 
			chat_dc_x, chat_dc_y = plot_degree_correlation(w, 'xx')
			chat_dc_amp, chat_dc_index, chat_dc_indexErr = powerlaw_fit(chat_dc_x, chat_dc_y)
			fd_dc_x, fd_dc_y = plot_degree_correlation(f, 'xx')
			fd_dc_amp, fd_dc_index, fd_dc_indexErr = powerlaw_fit(fd_dc_x, fd_dc_y)

			clf()
			loglog(chat_dc_x, chat_dc_y, linestyle = "None", marker = '.', color = 'r', label = 'Chat')
			loglog(fd_dc_x, fd_dc_y, linestyle = "None", marker = '+', color = 'b', label = 'Friend')
			if show_fit:
				loglog(chat_dc_x, powerlaw(chat_dc_x, chat_dc_amp, chat_dc_index), color = 'k', label = 'Chat fit')
				loglog(fd_dc_x, powerlaw(fd_dc_x, fd_dc_amp, fd_dc_index), color = 'k', label = 'Friend fit')
			legend(["Chat %.2f +/- %.2f" % (chat_dc_index, chat_dc_indexErr), "Friend %.2f +/- %.2f" % (fd_dc_index, fd_dc_indexErr)])
			title('degree correlation')
			xlabel('degree k')
			ylabel('Knn(k)')
			savefig('%s_fd_chat_dcDistr.png' % realm)
		else:
			# degree distribution -- 
			dd_x, dd_y = plot_degree_distribution(g, 'xx')
			dd_amp, dd_index, dd_indexErr = powerlaw_fit(dd_x, dd_y)

			clf()
			loglog(dd_x, dd_y, linestyle = "None", marker = '.', color = 'r', label = realm)
			if show_fit:
				loglog(dd_x, powerlaw(dd_x, dd_amp, dd_index), color = 'k', label = '%s fit' % realm)
			legend(["%s %.2f +/- %.2f" % (realm, dd_index, dd_indexErr)])
			title('degree distribution')
			xlabel('degree k')
			ylabel('P(k)')
			savefig('%s_degDistr.png' % realm)

			# cluster distribution -- 
			cc_x, cc_y = plot_cluster_distribution(g, 'xx')
			cc_amp, cc_index, cc_indexErr = powerlaw_fit(cc_x, cc_y)

			clf()
			loglog(cc_x, cc_y, linestyle = "None", marker = '.', color = 'r', label = realm)
			if show_fit:
				loglog(cc_x, powerlaw(cc_x, cc_amp, cc_index), color = 'k', label = '%s fit' % realm)
			legend(["%s %.2f +/- %.2f" % (realm, cc_index, cc_indexErr)])
			title('clustering distribution')
			xlabel('degree k')
			ylabel('C(k)')
			savefig('%s_ccDistr.png' % realm)

			# degree correlation -- 
			dc_x, dc_y = plot_degree_correlation(g, 'xx')
			dc_amp, dc_index, dc_indexErr = powerlaw_fit(dc_x, dc_y)

			clf()
			loglog(dc_x, dc_y, linestyle = "None", marker = '.', color = 'r', label = realm)
			if show_fit:
				loglog(dc_x, powerlaw(dc_x, dc_amp, dc_index), color = 'k', label = '%s fit' % realm)
			legend(["%s %.2f +/- %.2f" % (realm, dc_index, dc_indexErr)])
			title('degree correlation')
			xlabel('degree k')
			ylabel('Knn(k)')
			savefig('%s_dcDistr.png' % realm)

if __name__ == "__main__":
	main(sys.argv[1:])
