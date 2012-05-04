# Jing-Kai Lou (kaeaura@gamil.com)

from __future__ import print_function
import os
import re
import sys
import time
import getopt
import cPickle
import networkx as nx
from collections import Counter
from db import LiteDB
from toGraph import read_temporal_edges, EdgeSeries

__author__ = "Jing-Kai Lou (kaeaura@gmail.com)"

uniq_degree = lambda g: sorted(list(set(g.degree().values())))
uniq_in_degree = lambda g: sorted(list(set(g.in_degree().values())))
uniq_out_degree = lambda g: sorted(list(set(g.out_degree().values())))

def descrete_bin_determiner(counter, bin_amount = 100):
	"""docstring for bin_determiner"""
	ks = sorted(counter.keys())
	ks.reverse()
	grid = set([ks[0]])
	while len(ks):
		grab_amount = 0
		while grab_amount < bin_amount and len(ks):
			grab_key = ks.pop()
			grab_amount += counter[grab_key]
		grid.add(grab_key)
	return(sorted(list(grid)))

def bin_counter(counter, bins = None, bin_amount = 100):
	"""
		bin_counter will merge the counter into bins
		Parameters:
		-----------
			counter: Counter
				the original counter (histogram)
			bins: list, default = None
				the bin vessel
			bin_amount:
				the expected number of elements within one bin
		Returns:
		--------
			Counter, the indexed with new bins
	"""
	from collections import Counter
	from numpy import linspace
	from bisect import bisect_left
	if not bins:
		bins = descrete_bin_determiner(counter, bin_amount)
	l = lambda x: bisect_left(bins, x)
	merged_counter = Counter()
	for k, v in counter.items():
		merged_counter[bins[l(k)]] += v
	return(merged_counter)

def degree_count(g):
	dCnt = Counter()
	for dd in g.degree().itervalues(): dCnt[dd] += 1
	return(dCnt)

def in_degree_count(g):
	dCnt = Counter()
	for dd in g.in_degree().itervalues(): dCnt[dd] += 1
	return(dCnt)

def out_degree_count(g):
	dCnt = Counter()
	for dd in g.out_degree().itervalues(): dCnt[dd] += 1
	return(dCnt)

def common_neighbor_num(g, n, m):
	"""
		Count the number of common neighbors of nodes n and m in grah g.
		Note, this function counts the common succeders if g is directed

		Parameters:
		-----------
			g: NetworkX Graph, NetowrkX DiGraph
			n, m: str, or int
				the node index in g
		Return:
		-------
			int, the number of common neighbors
	"""
	n_neighbors = set(g.neighbors(n))
	m_neighbors = set(g.neighbors(m))
	l = len(n_neighbors & m_neighbors)
	return(l)

def all_common_neighbor_num(g):
	"""
		Count the common neighbor number for all pairs in grah g.
		Note this function counts the common succeders if g is directed

		Parameters:
		-----------
			g: Networkx Graph, NetworkX DiGraph
		Returns:
		--------
			iterator, the number of common neighbors of all node pairs in g
	"""
	from collections import Counter
	from itertools import combinations, starmap
	mCnt = Counter()
	nodes = g.nodes()
	pairs = combinations(nodes, 2)
	cNbhrs = lambda x, y: (set(g[x]) & set(g[y])).__len__()
	for m in starmap(cNbhrs, pairs):
		mCnt[m] += 1
	return(mCnt.elements())

def mutual_count(g, samples = None):
	"""
		Count the mutual neighbors number of all pairs in graph g.

		Parameters:
		-----------
			g: NetworkX Graph, NetworkX DiGraph
			samples: int, (default is None)
				the number of sample pairs.
				If samples is None or 0, then do not sample
		Returns:
		--------
			a dictionary of counts, keyed with number of mutual neighbors
	"""
	nodes = g.nodes()
	mCnt = Counter()
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
		pairs = gen_pairs(nodes, samples)
		pair_mutuals = map(lambda x: common_neighbor_num(g, x[0], x[1]), pairs)
		for pm in iter(pair_mutuals):
			mCnt[pm] += 1
	else:
		from itertools import combinations
		#pair_mutuals = map(lambda x: common_neighbor_num(g, x[0], x[1]), combinations(nodes, 2))
		pair_mutuals = all_common_neighbor_num(g)
		for pm in pair_mutuals:
			mCnt[pm] += 1
	return(mCnt)

def identifying_new_edges(g, h, loop_removed = True):
	"""
		Suppose h is an evoloved graph of graph g.
		This function identify the new generated edges in h that not existed in g

		Parameters:
		-----------
			g, h: NetworkX graph, NetowrkX DiGraph
			loop_removed: bool, (default is True)
				If True, then the new generated loop will be removed
		Returns:
		--------
			the new generated edges
	"""
	new_edges = filter(lambda e: not g.has_edge(*e), h.edges())
	if loop_removed:
		new_edges = filter(lambda x: x[0] != x[1], new_edges)
	return(new_edges)

def identifying_closure(g, h):
	"""
		Suppose h is a an evoloved graph of graph g
		A closure (edge) is an edge that connected in h with two nodes that already exists in g.
		Therefore, the clouser edge will enclose (form) a circuit.

		Parameter:
		----------
			g: NetworkX Graph, NetowrkX DiGraph

		Returns:
		--------
			a list of clousre edges (closure)
	"""
	new_edges = identifying_new_edges(g, h, loop_removed = True)
	existing_nodes = set(g.nodes())
	closure_edges = filter(lambda x: set(x).issubset(existing_nodes), new_edges)
	return(closure_edges)

def identifying_attachment(g, h):
	"""
		Suppose h is an evolved graph of graph g. 
		An attachment (edge) is a connection between two nodes that one in g and another in h.
		The attachments somewaht show how attractive are the elder nodes in g.

		Parameter:
		----------
			g: NetworkX Graph, NetowrkX DiGraph

		Returns:
		--------
			a list of attaching edges (attachment)
	"""
	existing_nodes = set(g.nodes())
	new_edges = identifying_new_edges(g, h)
	attaching_edges = filter(lambda x: g.has_node(x[0]) ^ g.has_node(x[1]), new_edges)
	return(attaching_edges)

def identifying_attachment_degree_histogram(g, h):
	"""
		Suppose h is an evolved graph of graph g. 
		Count the the number of attached nodes with degree k, for possible k in g.

		Parameters:
		----------
			g, h: NetworkX Graph, NetworkX DiGraph
		Returns:
		--------
			a dictionary of count of attached nodes, keyed with the degree of attached nodes
	"""
	isDirected = g.is_directed()
	hist = Counter()
	existing_nodes = set(g.nodes())
	attachments = identifying_attachment(g, h)
	print ("attachments %d" % len(attachments))
	for attaching_edge in iter(attachments):
		attached_node = filter(lambda x: existing_nodes.__contains__(x), attaching_edge)[0]
		attached_node_degree = nx.in_degree(g, attached_node) if isDirected else nx.degree(g, attached_node)
		hist[attached_node_degree] += 1
	return(hist)

def preferential_attachment_relative_prob(g, later_g, enable_bins = False):
	"""
		Suppose h (in time t+1) is an evolved graph of graph g (in time t). 
		Calculate the relative preferential attachmebt probability, R_k
			P_k(t) = R_k(t) * n_k(t) / N(t),
		where P_k(t) is the probability of attachment (calculated by identifying_attachment_degree_histogram),
		n_k(t) is the number of nodes with degree k in g, and N(t) is the number of nodes in g.

		Parameters:
		-----------
			g, later_g: NetworkX Graph, NetworkX DiGraph

		Returns:
		--------
			The dictionary of R_k, keyed with the degree k

		Reference:
		----------
			[1]	M. E. J. Newman, "Clustering and preferential attachment in growing networks," 
			arXiv.org, vol. cond-mat.stat-mech. 12-Apr.-2001.

		See Also:
		---------
			identifying_attachment_degree_histogram
	"""
	N = float(g.order())
	dCnt = degree_count(g)
	attachedCnt = identifying_attachment_degree_histogram(g, later_g)
	print (dCnt)
	print (attachedCnt)
	if enable_bins:
		binned_dCnt = bin_counter(dCnt, bin_amount = 100)
		binned_attachedCnt = bin_counter(attachedCnt.iteritems, bins = binned_dCnt)
	prefDict = dict()
	for d, v in attachedCnt.iteritems():
		prefDict[d] = v * N / dCnt[d]
	return(prefDict)

def identifying_closure_mutual_neighbors_histogram(g, h):
	"""
		Suppose h is an evolved graph of graph g.
		Count the number of enclosed node pairs that share m neighbors in g.

		Parameters:
		-----------
			g, h: NetworkX Graph, NetworkX DiGraph

		Returns:
		--------
			a dictionary of count of enclosed nodes, keyed with the number of mutual neighbors, m.
	"""
	hist = Counter()
	pair_mutuals = map(lambda x: common_neighbor_num(g, x[0], x[1]), iter(identifying_closure(g, h)))
	for pm in iter(pair_mutuals):
		hist[pm] += 1
	return(hist)

def identifying_closure_distance_histogram(g, h):
	"""
		Suppose h is an evolved graph of graph g.
		Count the number of d-steps enclosed node pairs.
		A d-steps enclosed pairs (u, v) is a pair of nodes that one is d steps distant from another 
		in graph g, and then a link (u, v) appears later (i.e., in graph h).

		Parameters:
		-----------
			g, h: NetworkX Graph, NetworkX DiGraph

		Returns:
		--------
			a dictionary of count of enclosed nodes, keyed with the distance between the pair, d.
	"""
	hist = Counter()
	existing_nodes = set(g.nodes())
	for closure_edge in iter(identifying_closure(g, h)):
		try:
			closed_distance_length = nx.bidirectional_dijkstra(g, closure_edge[0], closure_edge[1])[0]
			hist[closed_distance_length] += 1
		except nx.NetworkXNoPath:
			next
	return(hist)

def clustering_relative_prob(g, later_g):
	"""
		Get the relative prob of linking between two nodes by the closure edges, i.e. 
		the ratio between the actural prob. of their links and the porb of their linking 
		in a network in which presence of mutual acquaintances makes no difference.

		Reference:
		----------
			[1]	M. E. J. Newman, "Clustering and preferential attachment in growing networks," 
			arXiv.org, vol. cond-mat.stat-mech. 12-Apr.-2001.

	"""
	N = float(g.order())
	M = N * (N - 1) / 2
	mc = mutual_count(g, samples = None)
	mutualCnt = identifying_closure_mutual_neighbors_histogram(g, later_g)
	clustDict = dict()
	for m, v in mutualCnt.iteritems():
		if mc[m] == 0:
			print (m, v)
			break
		clustDict[m] = v * M / mc[m]
	return(clustDict)

def longitude_pack(g, later_g, **kwargs):
	"""
		Packing the longititude properties of a given graph
		This pack includes: clustering relative probability, 
		preferential attachment relative probability, and
		closure distance count.

		Parameters:
		-----------
			g: NetworkX Graph, Networkx DiGraph
				The original graph 
			later_g: NetworkX Graph, Networkx DiGraph
				The graph grow later. Technically, g is a subgraph of later_g
		Returns:
		--------
			a dictionary of longitude properties, keyed with property names
	"""
	t = dict()
	for k in kwargs:
		t.__setitem__(k, kwargs[k])

	print ('processing cluster_prob')
	cr = clustering_relative_prob(g, later_g)
	t.__setitem__('cluster_prob', cr)

	print ('processing pref_attach')
	pa = preferential_attachment_relative_prob(g, later_g)
	t.__setitem__('pref_attach', pa)

	print ('processing closure_dist')
	cd = identifying_closure_distance_histogram(g, later_g)
	t.__setitem__('closure_dist', cd)
	return(t)

def pref_pack(g, later_g, **kwargs):
	"""
		Packing the longititude properties of a given graph
		This pack includes: preferential attachment relative probability. 
		Parameters:
		-----------
			g: NetworkX Graph, Networkx DiGraph
				The original graph 
			later_g: NetworkX Graph, Networkx DiGraph
				The graph grow later. Technically, g is a subgraph of later_g
		Returns:
		--------
			a dictionary of longitude properties, keyed with property names
	"""
	t = dict()
	for k in kwargs:
		t.__setitem__(k, kwargs[k])

	print ('processing pref_attach')
	pa = preferential_attachment_relative_prob(g, later_g)
	t.__setitem__('pref_attach', pa)
	return(t)

def clust_pack(g, later_g, **kwargs):
	"""
		Packing the longititude properties of a given graph
		This pack includes: clustering relative probability.

		Parameters:
		-----------
			g: NetworkX Graph, Networkx DiGraph
				The original graph 
			later_g: NetworkX Graph, Networkx DiGraph
				The graph grow later. Technically, g is a subgraph of later_g
		Returns:
		--------
			a dictionary of longitude properties, keyed with property names
	"""
	t = dict()
	for k in kwargs:
		t.__setitem__(k, kwargs[k])
	print ('processing cluster_prob')
	cr = clustering_relative_prob(g, later_g)
	t.__setitem__('cluster_prob', cr)
	return(t)

def closure_pack(g, later_g, **kwargs):
	"""
		Packing the longititude properties of a given graph
		This pack includes: closure distance count.

		Parameters:
		-----------
			g: NetworkX Graph, Networkx DiGraph
				The original graph 
			later_g: NetworkX Graph, Networkx DiGraph
				The graph grow later. Technically, g is a subgraph of later_g
		Returns:
		--------
			a dictionary of longitude properties, keyed with property names
	"""
	t = dict()
	for k in kwargs:
		t.__setitem__(k, kwargs[k])
	print ('processing closure_dist')
	cd = identifying_closure_distance_histogram(g, later_g)
	t.__setitem__('closure_dist', cd)
	return(t)

def main(argv):
	"""
		load the temporal series, and calculat the 
			- preferential attachment porb.
			- new communication distance
	"""
	inputFile = None
	asDirected = False
	outputFile = None
	dataName = None
	packType = "all"
	timestampformat = "%Y%m%d"
	outputTimeFormat = "%Y-%m-%d"
	base_duration = 60
	extended_duration = 60
	ofs = ","

	def usage():
		"""print the usage"""
		print ("----------------------------------------")
		print ("read the temporal edge list, output the longitude properties")
		print
		print ("-h, --help: print this usage")
		print ("-i ...: path, read temporal edgelist")
		print ("-b ...: int, the length of the base period")
		print ("-e ...: int, the length of the extended period")
		print ("-T [all|pa|cr|cd]: the type of pack, default = all")
		print ("\tall = pa + cr + cd")
		print ("\tpa = preferential attachment")
		print ("\tcr = clustering relative prob.")
		print ("\tcd = closure distance")
		print ("-o ...: path, output .db file")
		print ("----------------------------------------")

	try:
		opts, args = getopt.getopt(argv, "hi:b:e:T:o:", ["help"])
	except getopt.GetoptError:
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
		elif opt in ("-b"):
			base_duration = int(arg)
		elif opt in ("-e"):
			extended_duration = int(arg)
		elif opt in ("-T"):
			packType = arg
		elif opt in ("-o"):
			outputFile = arg

	timeLoadStart = time.time()
	eDict, tDict = read_temporal_edges(read_path = inputFile, as_directed = False, enable_verbose = False)
	timeLoadEnd = time.time()
	print ("[Load Time] %.2f sec" % (timeLoadEnd - timeLoadStart))

	# set large lifespan to make it always be cumulative
	gSeries = EdgeSeries(is_directed = False, lifespan = 1000)	
	gSeries.update(tDict)
	gSeries.setup()

	gSeries.next(step = base_duration)
	g = gSeries.forward()
	gSeries.next(step = extended_duration)
	later_g = gSeries.forward()

	print ("[GraphOrder] g: %d / later_g: %d" % (g.order(), later_g.order()))
	print ("[GraphSize] g: %d / later_g: %d" % (g.size(), later_g.size()))

	db = LiteDB()
	fillinName = re.sub(".[^\.]+$", "", os.path.basename(inputFile)) if dataName is None else dataName
	timeinfo = "--".join([ min(tDict.keys()).strftime("%Y-%m-%d"), max(tDict.keys()).strftime("%Y-%m-%d") ])
	graph_key = "_".join([fillinName, timeinfo, 'd'])

	timePackStart = time.time()

	if db.__contains__(graph_key):
		if packType == "all":
			print ('updating in longitude mode')
			db[graph_key].update(longitude_pack(g, later_g, base_len = base_duration, extended_len = extended_duration))
		elif packType == "pa":
			print ('updating in pa mode')
			db[graph_key].update(pref_pack(g, later_g, base_len = base_duration, extended_len = extended_duration))
		elif packType == "cr":
			print ('updating in cr mode')
			db[graph_key].update(clust_pack(g, later_g, base_len = base_duration, extended_len = extended_duration))
		elif packType == "cd":
			print ('updating in cd mode')
			db[graph_key].update(closure_pack(g, later_g, base_len = base_duration, extended_len = extended_duration))
		else:
			print ('do nothing')
	else:
		if packType == "all":
			print ('writing in longitude mode')
			db[graph_key] = longitude_pack(g, later_g, base_len = base_duration, extended_len = extended_duration)
		elif packType == "pa":
			print ('writing in pa mode')
			db[graph_key] = pref_pack(g, later_g, base_len = base_duration, extended_len = extended_duration)
		elif packType == "cr":
			print ('writing in cr mode')
			db[graph_key] = clust_pack(g, later_g, base_len = base_duration, extended_len = extended_duration)
		elif packType == "cd":
			print ('writing in cd mode')
			db[graph_key] = closure_pack(g, later_g, base_len = base_duration, extended_len = extended_duration)

	timePackEnd = time.time()
	print ("[Pack Time] %.2f sec" % (timePackEnd - timePackStart))

	db.save(outputFile)

if __name__ == "__main__":
	main(sys.argv[1:])
