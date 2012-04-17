# Jing-Kai Lou (kaeaura@gamil.com)
# Sun Feb 26 15:17:41 CST 2012

import os
import re
import sys
import time
import getopt
import cPickle
import networkx as nx
from db import LiteDB
from scipy import average, median, array, log10, sqrt
from scipy.optimize import leastsq
from collections import Counter, defaultdict
from itertools import ifilter

__author__ = "Jing-Kai Lou (kaeaura@gmail.com)"

powerlaw = lambda x, amp, index: amp * (x**index)

def strength_centrality(G, weight, k = None, mode = 'out'):
	'''
		Return the degree centrality according to the weight on the edges.

		Arguments:
		--
		* weight: str. the name of the edge attribute using for the weight values
		* k: the node list. would be G.nodes() if k is ignored
		* mode: str. should be "in", "out" or "all", which stands for the in_degree, out_degree, and degree respectively
	'''
	if k == None:
		k = G.nodes()
	n_weight_dict = dict()
	for node in k:
		if mode == 'out':
			n_weight_dict[node] = sum(map(lambda x: x[2][weight], G.out_edges(node, data = True)))
		elif mode == 'in':
			n_weight_dict[node] = sum(map(lambda x: x[2][weight], G.in_edges(node, data = True)))
		else:
			n_weight_dict[node] = sum(map(lambda x: x[2][weight], G.out_edges(node, data = True) + G.in_edges(node, data = True)))
	return(n_weight_dict)

def average_degree(g):
	if g.order():
		d = g.degree().values()
		return(float(sum(d)) / g.order())
	else:
		return(0)

def average_in_degree(g):
	if g.order():
		d = g.in_degree().values()
		return(float(sum(d)) / g.order())
	else:
		return(0)

def average_out_degree(g):
	if g.order():
		d = g.out_degree().values()
		return(float(sum(d)) / g.order())
	else:
		return(0)

def degcor(g):
	"""
		Calculating the pearson correlation between in-degree and out-degree of nodes
		in the given Graph g.

		Parameters:
		-----------
			g: NetworkX DiGraph
		Returns:
		-------
		degree correlation, float
	"""
	assert(g.is_directed())
	from scipy.stats import pearsonr
	x, y = list(), list()
	for n in g.nodes_iter():
		x.append(g.out_degree(n))
		y.append(g.in_degree(n))
	return(pearsonr(x, y))

def to_undirected(g, is_bi = False):
	"""
		Remove the selfloops and make it as undirected for a given graph.

		Parameters:
		-----------
			g: NetworkX Graph, NetworkX DiGraph
			is_bi: bool, (default = False)
				If is_bi is true, then only bi-directional tie left. 
				That means all single directional arc between nodes are removed

		Returns:
		-------
			NetworkXGraph
	"""
	g.remove_edges_from(g.selfloop_edges())

	return(nx.Graph(g))

def mean_clustering(g, normalized = False):
	"""
		Calculating the clustering coefficient for a graph. If given graph is directed, 
		the graph is converted to undirected automatically that means any arc will be an edge.

		Parameters:
		-----------
			g: NetworkX Graph, NetworkX DiGraph
			normalized: bool, optional, (default = False)
		Returns:
		-------
			float, (normalized) clustering coefficient
	"""
	# first, remove the self edges
	g = to_undirected(g)
	c = nx.average_clustering(g)
	rc = float(g.size() * 2) / (g.order() * (g.order() - 1))
	if normalized:
		return(c / rc if rc > 0 else 0)
	else:
		return(c)

def randomly_clustering(g, tries = 10):
	"""
		Comparing the average clustering coefficient of g with other graphs h
		which share identical degree sequence. This function returns the comparison ratio.

		Parameters:
		-----------
			g: NetworkX Graph, NetworkX DiGraph
			tries: int, optional, (default = 10)
				number of tries (compared graphs)
		See also:
		---------
			mean_clustering
		Returns:
		--------
			float, the ratio of avg clustering coefficient, avg_cc(g) / mean(avg_cc(h))
	"""
	from scipy import average
	g = to_undirected(g)
	d = g.degree().values()
	c = mean_clustering(g, normalized = False)
	p = list()
	for t in xrange(tries):
		ng = nx.configuration_model(d, create_using = nx.Graph())
		p.append(mean_clustering(ng))
		del ng
	return(c / average(p))
		
def reinforce(g, weight = 'weight'):
	w = nx.get_edge_attributes(g, weight)
	if len(w):
		return(filter(lambda x: x.__len__() > 1 if hasattr(x, '__iter__') else x > 1, w.values()).__len__() / float(w.__len__()))
	else:
		return(0)

def reciprocity(g, return_cor = True):
	"""
		Calculate the reciprocity for a directed graphs. If return_cor is False, 
		then it provides a traditional way of quantifying reciprocity r as the ratio of 
		the number of links pointing in both directions L_r to the total number of links L.

		Nevertheless, reciprocity r must be compared with the value r_rand expected 
		in a random graph with exactly same size and order, or it has only a relative meaning
		and does not carry complete information by itself. In order to avoid the aforementioned
		problems, this also proposes a new definition of reciprocity rho as the correlation 
		between the entries of the adjacency matrix of a directed graph.

		Parameters: 
		-----------
			g: NetworkX DiGraph
			return_cor: bool, optional, (default = True)
				If true, return the return_cor reciprocity rho (correlation) 
		Returns:
		-------
			reciprocity: float
		References:
		-----------
		[1] D. Garlaschelli and M. I. Loffredo, 
		'Patterns of link reciprocity in directed networks,' 
		arXiv.org, vol. cond-mat.dis-nn. 22-Apr.-2004.
	"""
	if g:
		assert(g.is_directed())
		# first, remove the self loops and duplicated edges
		# in matrix aspect, remove the diagonal elements and make the element are no greater than 1
		n = g.order()
		L = set(g.edges()).difference(set(g.selfloop_edges()))
		# sort the directional edges as undirectional edges
		L_unorder = map(lambda x: '-'.join(map(str, list(set(x)))), L)
		L_cnt = Counter()
		for l in iter(L_unorder):
			L_cnt[l] += 1
		L_r = filter(lambda x: L_cnt[x] > 1, L_cnt.iterkeys())
		r = 2 * float(len(L_r)) / len(L_unorder)
		a = float(len(L)) / (n * (n - 1))
		rho = ((r - a) / (1 - a))
		return(rho if return_cor else r)
	else:
		return(None)

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

def get_degree_distribution(g, mode = 'both', is_CDF = True):
	""" 
		The discrete degree distribution. Similar to the histogram shows the possible degrees k,
		and ratio of nodes with degree greater than k in graph g.

		Parameters:
		-----------
			g: NetworkX Graph
			mode: str ('in', 'out', 'both'), (default = 'both')
			is_CDF: bool, (default = True)
				if True, return the ratio values as CDF, else return the ratio values as PDF
		Returns:
		--------
			xdata, ydata, a 2-tuple of array, (degree k, P(k))
	"""
	if mode == 'both':
		dg = g.degree().values()
	elif mode == 'in':
		dg = g.in_degree().values()
	elif mode == 'out':
		dg = g.out_degree().values()
	else:
		return(0)

	c = Counter()
	for d in iter(dg):
		c[d] += 1
	d = dict(c)
	if d.__contains__(0):
		d.__delitem__(0)
	dSum = sum(d.values())
	dKeys = d.keys()
	dKeys.sort()
	xdata = array(dKeys)
	ylist = list()
	if is_CDF:
		for k in xdata: ylist.append(sum([d[kk] for kk in xdata[xdata >= k]]))
	else:
		for k in xdata: ylist.append(sum([d[kk] for kk in xdata[xdata == k]]))

	ydata = array(map(lambda x: float(x) / dSum, ylist))
	return(xdata, ydata)

def get_cluster_distribution(g, method = 'average'):
	""" 
		The clustering coefficient distribution grouped by degree. Similar to the histogram shows the possible degree k,
		and average/median clustering coefficient of nodes with degree k in graph g.

		Parameters:
		-----------
			g: NetworkX Graph
			method: str, ('average', 'median'), (default = 'average')
		Returns:
		--------
			xdata, ydata, a 2-tuple of array, (k, avg_cc(V_k)), where V_k are the nodes with degree k
	"""
	g = to_undirected(g)
	k = nx.clustering(g)
	d = g.degree()
	ck = defaultdict(list)
	for n in g.nodes_iter():
		ck[d[n]].append(k[n])
	xdata, ydata = list(), list()
	
	if method == 'average':
		for x, y in ifilter(lambda x: x[0] > 1 and average(x[1]) > 0, ck.iteritems()):
			xdata.append(x)
			ydata.append(average(y))
	elif method == 'median':
		for x, y in ifilter(lambda x: x[0] > 1 and median(x[1]) > 0, ck.iteritems()):
			xdata.append(x)
			ydata.append(median(y))
	else:
		raise NameError("method should be 'average' or 'mean'")
	xdata = array(xdata)
	ydata = array(ydata)
	return(xdata, ydata)

def get_degree_correlation(g, method = 'average', mode = 'both'):
	""" 
		The average neighbor degree/in-degree/out-degree distribution grouped by degree. Similar to the histogram shows the possible degree k,
		and average/median clustering coefficient of nodes with degree k in graph g.

		Parameters:
		-----------
			g: NetworkX Graph
			mode: str, ('in', 'out', 'both'), (default = 'both')
			method: str, ('average', 'median'), (default = 'average')
		Returns:
		--------
			xdata, ydata, a 2-tuple of array, (k, <Knn>(k)), where <Knn>(k) denotes as the average/median degree
	"""
	if mode == 'both':
		d = g.degree()
		k = nx.average_neighbor_degree(g)
	elif mode == 'in':
		d = g.in_degree()
		k = nx.average_neighbor_degree(g, source = 'in', target = 'in')
	elif mode == 'out':
		d = g.out_degree()
		k = nx.average_neighbor_degree(g, source = 'out', target = 'out')
	else:
		raise NameError("mode must be 'in', 'out', or 'both'")
	ck = defaultdict(list)
	#group the nodes by degree
	for n in g.nodes_iter():
		ck[d[n]].append(k[n])
	xdata, ydata = list(), list()
	if method == 'average':
		for x, y in ifilter(lambda x: x[0] > 0 and average(x[1]) > 0, ck.iteritems()):
			xdata.append(x)
			ydata.append(average(y))
	elif method == 'median':
		for x, y in ifilter(lambda x: x[0] > 0 and median(x[1]) > 0, ck.iteritems()):
			xdata.append(x)
			ydata.append(median(y))
	else:
		raise NameError("method must be 'average' or 'median'")
	xdata = array(xdata)
	ydata = array(ydata)
	return(xdata, ydata)

def effect_diameter(graph):
	"""
		Get the diamter of the largest (weakly) connected component

		Parameters:
		-----------
			graph: Networkx Graph, Networkx DiGraph,
		Returns:
		--------
			int, the diameter of the largested connected component
	"""
	if graph.is_directed():
		graph = to_undirected(graph)
	return(nx.diameter(nx.connected_component_subgraphs(graph)[0]))

def hop_counts(graph, cutoff = None, samples = 100000):
	"""
		Calculating the length (in number of hops) with nodes  using dijkstra algorithm. 
		The input graph will be automaically turned into an undirected simple graph without loops.
		Note the function only focus on the largest connected component if graph is disconnected.

		To reduce the computation complexity, sampling method is used by default. Can use the argument
		'samples' to control the number of samples.

		Parameters:
		-----------
			graph: Networkx Graph, NetworkX DiGraph,
			cutoff: integer or float, optional
				Depth to stop search. Only paths of length <= cutoff are counted
			samples: int
				The number of sampling node pairs in order 
				If samples equals to 0, then all pairs of nodes will be included.
		Returns:
		--------
			a dictionary, keyed by hop count, of number of paths with specific hops
	"""
	graph = to_undirected(graph)
	from collections import Counter
	cnt = Counter()
	if samples > 0:
		def gen_pairs(p, n):
			"""
				generting the sampling node pairs.
				duplicated pairs is possible, but self loop is impossible
			"""
			import random
			random.seed()
			pairs = [ random.sample(p, 2) for s in xrange(n) ]
			return(pairs)
		pairs = gen_pairs(nx.connected_components(graph)[0], samples)
		pair_lens = map(lambda x: nx.bidirectional_dijkstra(graph, x[0], x[1], weight = None)[0], pairs)
		if cutoff: pair_lens = filter(lambda x: x <= cutoff, pair_lens)
		for pl in iter(pair_lens):
			cnt[pl] += 1
	else:
		plDict = nx.all_pairs_dijkstra_path_length(graph, cutoff = cutoff)
		for p in plDict.itervalues():
			for d in p.itervalues():
				cnt[d] += 1
	return(dict(cnt))

def dist_pack(graph, **kwargs):
	"""
		Packing the distant measurement properties of given graph

		Parameters:
		-----------
			graph: Networkx Graph, NetworkX Digraph,
			arbitary args: **kwargs,
		Returns:
		--------
			a dictionary, keyed by property names, of property values.
	"""
	t = dict()
	for k in kwargs:
		t.__setitem__(k, kwargs[k])
	t.__setitem__('diameter', effect_diameter(graph))
	t.__setitem__('hop_counts', hop_counts(graph, samples = 50000, cutoff = 10))
	return(t)

def easy_pack(graph, **kwargs):
	"""
		Packing the topological properties of a given graph.

		Parameters:
		-----------
			graph: NetworkX Graph, NetworkX DiGraph,
			arbitary args: **kwargs,
				set prop_name = prop_value
		Returns:
		--------
			a dictionary of topological property, keyed with property names
	"""
	t = dict()
	for k in kwargs:
		t.__setitem__(k, kwargs[k])
	# resolve the features
	t.__setitem__('order', graph.order())
	t.__setitem__('size', graph.size())
#	t.__setitem__('degree', average_degree(graph))
#	t.__setitem__('asr', nx.degree_assortativity_coefficient(graph))
	t.__setitem__('recp', reciprocity(graph, return_cor = False))
	t.__setitem__('rho', reciprocity(graph, return_cor = True))
	t.__setitem__('reinf', reinforce(graph))
#	if graph.is_directed():
#		t.__setitem__('degcor', degcor(graph))
#		# in_degree
#		xdata, ydata = get_degree_distribution(graph, mode = 'in')
#		t.__setitem__('inDegDistr_x', xdata)
#		t.__setitem__('inDegDistr_y', ydata)
#		t.__setitem__('inDegDistr_fit', powerlaw_fit(xdata, ydata))
#
#		# out_degree
#		xdata, ydata = get_degree_distribution(graph, mode = 'out')
#		t.__setitem__('outDegDistr_x', xdata)
#		t.__setitem__('outDegDistr_y', ydata)
#		t.__setitem__('outDegDistr_fit', powerlaw_fit(xdata, ydata))
	return(t)

def pack(graph, **kwargs):
	"""
		Packing the topological properties of given graph.

		Parameters:
		-----------
			graph: NetworkX Graph, NetworkX DiGraph,
			arbitary args: **kwargs,
				set prop_name = prop_value
		Returns:
		--------
			a dictionary of topological property values keyed with property names
	"""

	t = dict()
	# add meta labels
	for k in kwargs:
		t.__setitem__(k, kwargs[k])
	# resolve the features
	t.__setitem__('order', graph.order())
	t.__setitem__('size', graph.size())
	t.__setitem__('degree', average_degree(graph))
	t.__setitem__('asr', nx.degree_assortativity_coefficient(graph))
	t.__setitem__('recp', reciprocity(graph, return_cor = False))
	t.__setitem__('rho', reciprocity(graph, return_cor = True))
	t.__setitem__('reinf', reinforce(graph))
	if graph.is_directed():
		t.__setitem__('degcor', degcor(graph))
		# in_degree
		xdata, ydata = get_degree_distribution(graph, mode = 'in')
		t.__setitem__('inDegDistr_x', xdata)
		t.__setitem__('inDegDistr_y', ydata)
		t.__setitem__('inDegDistr_fit', powerlaw_fit(xdata, ydata))

		# out_degree
		xdata, ydata = get_degree_distribution(graph, mode = 'out')
		t.__setitem__('outDegDistr_x', xdata)
		t.__setitem__('outDegDistr_y', ydata)
		t.__setitem__('outDegDistr_fit', powerlaw_fit(xdata, ydata))

		# in_knn
		xdata, ydata = get_degree_correlation(graph, method = 'average', mode = 'in')
		t.__setitem__('inKnnDistr_avg_x', xdata)
		t.__setitem__('inKnnDistr_avg_y', ydata)
		t.__setitem__('inKnnDistr_avg_fit', powerlaw_fit(xdata, ydata))

		xdata, ydata = get_degree_correlation(graph, method = 'median', mode = 'in')
		t.__setitem__('inKnnDistr_median_x', xdata)
		t.__setitem__('inKnnDistr_median_y', ydata)
		t.__setitem__('inKnnDistr_median_fit', powerlaw_fit(xdata, ydata))

		# out_knn
		xdata, ydata = get_degree_correlation(graph, method = 'average', mode = 'out')
		t.__setitem__('outKnnDistr_avg_x', xdata)
		t.__setitem__('outKnnDistr_avg_y', ydata)
		t.__setitem__('outKnnDistr_avg_fit', powerlaw_fit(xdata, ydata))

		xdata, ydata = get_degree_correlation(graph, method = 'median', mode = 'out')
		t.__setitem__('outKnnDistr_median_x', xdata)
		t.__setitem__('outKnnDistr_median_y', ydata)
		t.__setitem__('outKnnDistr_median_fit', powerlaw_fit(xdata, ydata))

	# degree
	xdata, ydata = get_degree_distribution(graph)
	t.__setitem__('degDistr_x', xdata)
	t.__setitem__('degDistr_y', ydata)
	t.__setitem__('degDistr_fit', powerlaw_fit(xdata, ydata))

	# clustering
	t.__setitem__('clustering', mean_clustering(graph, normalized = False))
	t.__setitem__('clustering_over_random', mean_clustering(graph, normalized = True))
	t.__setitem__('clustering_over_config', randomly_clustering(graph, tries = 100))

	xdata, ydata = get_cluster_distribution(graph, method = 'average')
	t.__setitem__('ccDistr_avg_x', xdata)
	t.__setitem__('ccDistr_avg_y', ydata)
	t.__setitem__('ccDistr_avg_fit', powerlaw_fit(xdata, ydata))

	xdata, ydata = get_cluster_distribution(graph, method = 'median')
	t.__setitem__('ccDistr_median_x', xdata)
	t.__setitem__('ccDistr_median_y', ydata)
	t.__setitem__('ccDistr_median_fit', powerlaw_fit(xdata, ydata))

	# knn
	xdata, ydata = get_degree_correlation(graph, method = 'average')
	t.__setitem__('knnDistr_avg_x', xdata)
	t.__setitem__('knnDistr_avg_y', ydata)
	t.__setitem__('knnDistr_avg_fit', powerlaw_fit(xdata, ydata))

	xdata, ydata = get_degree_correlation(graph, method = 'median')
	t.__setitem__('knnDistr_median_x', xdata)
	t.__setitem__('knnDistr_median_y', ydata)
	t.__setitem__('knnDistr_median_fit', powerlaw_fit(xdata, ydata))
	return(t)
		
class DiNet(nx.DiGraph):
	def __init__(self, graph, name = 'envolop'):
		"""docstring for __init__"""
		nx.DiGraph.__init__(self, data = graph, name = name)

	def _itemToTuple(self, item):
		"""docstring for _itemToTuple"""
		(i, j), y = item
		y = len(y) if dir(y).__contains__('__len__') else y
		return((i, j, y))
	def extract_edges(self, edge_attr):
		"""docstring for extract"""
		exEdges = nx.get_edge_attributes(self, edge_attr)
		sg = nx.DiGraph(data = exEdges.keys(), name = edge_attr) 
		if len(exEdges):
			nx.set_edge_attributes(sg, edge_attr, exEdges)
		return(sg)
	def extract_multiple_edges(self, *edge_attrs):
		sgs = []
		for edge_attr in edge_attrs:
			sgs.append(self.extract_edges(edge_attr))
		return(sgs)
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

class Net(nx.Graph):
	def __init__(self, graph, name = 'envolop'):
		"""docstring for __init__"""
		nx.Graph.__init__(self, data = graph, name = name)

	def _itemToTuple(self, item):
		"""docstring for _itemToTuple"""
		(i, j), y = item
		y = len(y) if dir(y).__contains__('__len__') else y
		return((i, j, y))
	def extract_edges(self, edge_attr):
		"""docstring for extract"""
		exEdges = nx.get_edge_attributes(self, edge_attr)
		sg = nx.Graph(data = exEdges.keys(), name = edge_attr) 
		if len(exEdges):
			nx.set_edge_attributes(sg, edge_attr, exEdges)
		return(sg)
	def extract_multiple_edges(self, *edge_attrs):
		sgs = []
		for edge_attr in edge_attrs:
			sgs.append(self.extract_edges(edge_attr))
		return(sgs)
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

def main(argv):
	"""docstring for main"""
	inputFile = list()
	inputDir = None
	inputFileType = 'gpickle'
	outputFile = None
	dataName = None
	enableVerbose = False
	heteNames = None
	heteNameSep = ","
	enablePlot = False
	show_fit = False
	metalabels = dict()
	forceSave = False
	asDirected = False
	enable_appendant = False
	enable_easyPack = False
	packType = 'normal'
	ofs = ","

	def usage():
		print ("----------------------------------------")
		print ("read the graphs (in gpickle, edgelist, or cpickle format) and ")
		print ("extract the graph topological features, and then pack features as a .db file")
		print
		print ("-h, --help: print this usage")
		print ("-i ...: read inputFile (as a gpickle file)")
		print ("-I ...: read inputDir (directory)")
		print ("control file type:")
		print ("\t(default: searching gpickle files)")
		print ("\t-e: set inputFile type as edgelist")
		print ("\t-p: set inputFile type as cpickle (for the temporal series file)")
		print ("-d: forced the input graph as directed (only valid while reading edgelist files)")
		print ("-o: outputFile (default *.db file)")
		print ("-r: dataName (saved as the db key)")
		print ("-v: enable verbose")
		print ("-N [typeName1,typeName2,...]: If input graph contains different edge type, split them into subgraphs")
		print ("-c [attribute]=[value]: dynamically add additioanl attribute to the output db file")
		print ("-a: if output file already existed, then append previous result. If detecting identical keys, then update the values")
		print ("  : The update means: older attributes will be update, new attributes will be create")
		print ("-f: if output file already existed, then replace previous result")
		print ("-T: pack type [easy, noraml, dist] ")
		print ("----------------------------------------")

	try:
		opts, args = getopt.getopt(argv, "hi:I:epo:r:vMN:c:afT:d", ["help"])
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
			inputFile.append(arg)
		elif opt in ("-I"):
			inputDir = arg
		elif opt in ("-e"):
			inputFileType = 'edgelist'
		elif opt in ("-p"):
			inputFileType = 'cpickle'
		elif opt in ("-o"):
			outputFile = arg
		elif opt in ("-r"):
			dataName = arg
		elif opt in ("-v"):
			enableVerbose = True
		elif opt in ("-N"):
			heteNames = arg.split(heteNameSep)
		elif opt in ("-c"):
			k, v = arg.split("=")
			metalabels.__setitem__(k, v)
		elif opt in ("-a"):
			enable_appendant = True
		elif opt in ("-f"):
			forceSave = True
		elif opt in ("-T"):
			packType = arg
		elif opt in ("-d"):
			asDirected = True

	inputFileTypeDict = { "gpickle": ".*\.gpickle$", "edgelist": ".*\.txt$", "cpickle": ".*\.cpickle$" }

	if inputDir:
		assert(os.path.exists(inputDir))
		pattern = re.compile(inputFileTypeDict[inputFileType]) 
		filelist = filter(lambda x: pattern.match(x) is not None, os.listdir(inputDir))
		inputFile.extend([os.path.join(inputDir, f) for f in filelist])
		print inputFile

	if enableVerbose:
		print ("inputFile: %s" % inputFile)
		print ("outputFile: %s" % outputFile)
		print ("dataName: %s" % dataName)
		print ("enableVerbose: %s" % enableVerbose)
		print ("heteNames: %s" % heteNames)
		print ("asDirected: %s" % asDirected)

	if outputFile is not None:
		outputDir = os.path.dirname(outputFile)
		if outputDir and not (os.path.exists(outputDir)):
			os.makedirs(outputDir)
	else:
		print ("There is no output")

	db = LiteDB()
	if os.path.exists(outputFile) and enable_appendant:
		db.load(outputFile)
	
	for f in inputFile: 
		print ("processing %s" % f)
		if not os.path.exists(f): next

		if inputFileType == 'gpickle':		# a graph
			g = nx.read_gpickle(file(f, "r"))
		elif inputFileType == 'edgelist':	# edgelist
			g = nx.read_edgelist(f, nodetype = int, create_using = nx.DiGraph()) if asDirected else nx.read_edgelist(f, nodetype = int, create_using = nx.Graph())
		elif inputFileType == 'cpickle':	# a list of graphs
			g = cPickle.load(file(f, "r"))

		graphs = list()

		if heteNames:
			for gg in g:
				net = DiNet(gg) if g.is_directed() else Net(gg)
				graphs.extend(net.extract_multiple_edges(*heteNames))
		else:
			if inputFileType in ('gpickle', 'edgelist'):
				graphs.append(g)
			elif inputFileType in ('cpickle'):
				graphs.extend(g)
			else:
				print ('empty file')
				sys.exit()

		for graph in iter(graphs):
			autoName = re.sub(".%s" % inputFileType, "", os.path.basename(f)) 
			fillinName = autoName if dataName is None else dataName
			graph_key = "_".join([fillinName, str(graph), 'd' if graph.is_directed() else 'u'])
			if db.__contains__(graph_key) and not forceSave:
				if packType == 'easy':
					print ('updating in easy-pack mode')
					db[graph_key].update(easy_pack(graph, **metalabels))
				elif packType == 'dist':
					print ('updating in dist-pack mode')
					db[graph_key].update(dist_pack(graph, **metalabels))
				else:
					print ('updating in normal-pack mode')
					db[graph_key].update(pack(graph, **metalabels))
			else:
				if packType == 'easy':
					print ("writing in easy-pack mode")
					db.__setitem__(graph_key, easy_pack(graph, **metalabels))
				elif packType == 'dist':
					print ("writing in dist-pack mode")
					db.__setitem__(graph_key, dist_pack(graph, **metalabels))
				else:
					print ("writing in normal-pack mode")
					db.__setitem__(graph_key, pack(graph, **metalabels))
			
	db.save(outputFile)

if __name__ == "__main__":
	main(sys.argv[1:])
