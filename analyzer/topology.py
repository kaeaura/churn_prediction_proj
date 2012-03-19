# Jing-Kai Lou (kaeaura@gamil.com)
# Sun Feb 26 15:17:41 CST 2012

import os
import re
import sys
import time
import getopt
import networkx as nx
import cPickle
from db import LiteDB
from scipy import average, array, log10, sqrt
from scipy.optimize import leastsq
from collections import Counter, defaultdict

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
	"""docstring for average_degree"""
	if g.order():
		d = g.degree()
		return(float(sum(d.values())) / g.order())
	else:
		return(0)

def degcor(g):
	"""docstring for degcor"""
	assert(g.is_directed())
	from scipy.stats import pearsonr
	x, y = list(), list()
	for n in g.nodes():
		x.append(g.out_degree(n))
		y.append(g.in_degree(n))
	return(pearsonr(x, y))

def norm_cc(g):
	"""docstring for norm_cc"""
	c = nx.average_clustering(g)
	rc = float(g.size() * 2) / (g.order() * (g.order() - 1))
	return(c / rc if rc > 0 else 0)

def reinforce(g, weight = 'weight', isSet = False):
	w = nx.get_edge_attributes(g, weight)
	if len(w):
		return(filter(lambda x: x.__len__() > 1 if hasattr(x, '__iter__') else x > 1, w.values()).__len__() / float(w.__len__()))
	else:
		return(0)

def reciprocity(g, normalized = True):
	"""docstring for reciprocity"""
	assert(g.is_directed())
	L = set(g.edges()).difference(set(g.selfloop_edges()))
	Lb = set()
	for e in L:
		Lb.add(frozenset(e))
	n = g.order()
	r = 2 * (len(L) - float(len(Lb))) / len(L)
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

def get_degree_distribution(g, mode = 'both'):
	""" return 2-tuple of array (degree k, degree probability P(k))"""
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
	for k in xdata:
		ylist.append(sum([d[kk] for kk in xdata[xdata >= k]]))
	ydata = array(map(lambda x: float(x) / dSum, ylist))
	return(xdata, ydata)

def get_cluster_distribution(g):
	""" return 2-tuple of array (clustering coefficient cc, clustering coefficient probability P(cc))"""
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
	return(xdata, ydata)

def get_degree_correlation(g):
	""" return 2-tuple of array (degree k, Knn_k) """
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
	return(xdata, ydata)

def pack(graph, **kwargs):
	"""docstring for to_pack"""
	t = dict()
	# add meta labels
	for k in kwargs:
		t.__setitem__(k, kwargs[k])
	# resolve the features
	t.__setitem__('order', graph.order())
	t.__setitem__('size', graph.size())
	t.__setitem__('degree', average_degree(graph))
	t.__setitem__('asr', nx.degree_assortativity_coefficient(graph))
	xdata, ydata = get_degree_distribution(graph)
	t.__setitem__('degDistr_x', xdata)
	t.__setitem__('degDistr_y', ydata)
	t.__setitem__('degDistr_fit', powerlaw_fit(xdata, ydata))
	xdata, ydata = get_degree_correlation(graph)
	t.__setitem__('knnDistr_x', xdata)
	t.__setitem__('knnDistr_y', ydata)
	t.__setitem__('knnDistr_fit', powerlaw_fit(xdata, ydata))
	if graph.is_directed():
		t.__setitem__('recp', reciprocity(graph))
		t.__setitem__('reinf', reinforce(graph))
		t.__setitem__('degcor', degcor(graph))
		xdata, ydata = get_degree_distribution(graph, mode = 'in')
		t.__setitem__('inDegDistr_x', xdata)
		t.__setitem__('inDegDistr_y', ydata)
		t.__setitem__('inDegDistr_fit', powerlaw_fit(xdata, ydata))
		xdata, ydata = get_degree_distribution(graph, mode = 'out')
		t.__setitem__('outDegDistr_x', xdata)
		t.__setitem__('outDegDistr_y', ydata)
		t.__setitem__('outDegDistr_fit', powerlaw_fit(xdata, ydata))
	else:
		t.__setitem__('cc', nx.average_clustering(graph))
		t.__setitem__('norm_cc', norm_cc(graph))
		xdata, ydata = get_cluster_distribution(graph)
		t.__setitem__('ccDistr_x', xdata)
		t.__setitem__('ccDistr_y', ydata)
		t.__setitem__('ccDistr_fit', powerlaw_fit(xdata, ydata))
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
	inputIsPickle = True
	outputFile = None
	dataName = None
	enableVerbose = False
	IsHete = False
	heteNames = None
	heteNameSep = ","
	enablePlot = False
	show_fit = False
	metalabels = dict()
	forceSave = False
	asDirected = False
	enable_appendant = False
	ofs = ","

	def usage():
		"""docstring for usage"""
		print ("--")
		print ("read the gpickles to analyze")
		print
		print ("\t-h, --help: print this usage")
		print ("\t-i: inputFile (gpickle)")
		print ("\t-I: inputDir (directory)")
		print ("\t-e: inputFile type = edgelist")
		print ("\t-o: outputFile")
		print ("\t-r: dataName")
		print ("\t-v: verbose")
		print ("\t-M: Is Hete. data")
		print ("\t-N: Hete. names")
		print ("\t-c: meta data for graph")
		print ("\t-a: append previous result")
		print ("\t-f: force save")
		print ("\t-d: as directed (only valid while reading edgelist)")

	try:
		opts, args = getopt.getopt(argv, "hi:I:eo:r:vMN:c:afd", ["help"])
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
			inputIsPickle = False
		elif opt in ("-o"):
			outputFile = arg
		elif opt in ("-r"):
			dataName = arg
		elif opt in ("-v"):
			enableVerbose = True
		elif opt in ("-M"):
			IsHete = True
		elif opt in ("-N"):
			heteNames = arg.split(heteNameSep)
		elif opt in ("-c"):
			k, v = arg.split("=")
			metalabels.__setitem__(k, v)
		elif opt in ("-a"):
			enable_appendant = True
		elif opt in ("-f"):
			forceSave = True
		elif opt in ("-d"):
			asDirected = True

	if enableVerbose:
		print ("inputFile: %s" % inputFile)
		print ("outputFile: %s" % outputFile)
		print ("dataName: %s" % dataName)
		print ("enableVerbose: %s" % enableVerbose)
		print ("IsHete: %s" % IsHete)
		print ("heteNames: %s" % heteNames)
		print ("asDirected: %s" % asDirected)

	if inputDir is not None:
		assert(os.path.exists(inputDir))
		pattern = re.compile(r".*\.gpickle$") if inputIsPickle else re.compile(r".*.txt$")
		filelist = filter(lambda x: pattern.match(x) is not None, os.listdir(inputDir))
		inputFile.extend([os.path.join(inputDir, f) for f in filelist])
		print inputFile
		
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

		if inputIsPickle:
			g = nx.read_gpickle(file(f, "r"))
		else:
			if asDirected:
				g = nx.read_edgelist(f, nodetype = int, create_using = nx.DiGraph())
			else:
				g = nx.read_edgelist(f, nodetype = int, create_using = nx.Graph())

		graphs = list()
		if IsHete:
			net = DiNet(g) if g.is_directed() else Net(g)
			graphs.extend(net.extract_multiple_edges(*heteNames))
		else:
			graphs.append(g)

		for graph in iter(graphs):
			autoName = re.sub(".gpickle", "", os.path.basename(f)) if inputIsPickle else re.sub(".txt", "", os.path.basename(f))
			fillinName = autoName if dataName is None else dataName
			graph_key = "_".join([fillinName, str(graph), 'd' if graph.is_directed() else 'u'])
			if db.__contains__(graph_key) and not forceSave:
				print ("warnning! lite database already exist such data (%s)" % graph_key)
				print ("skip")
				next
			else:
				db.__setitem__(graph_key, pack(graph, **metalabels))
			
	db.save(outputFile)

if __name__ == "__main__":
	main(sys.argv[1:])
