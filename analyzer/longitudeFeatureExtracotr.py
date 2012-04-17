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
	n_neighbors = g.neighbors(n)
	m_neighbors = g.neighbors(m)
	return(len(set(n_neighbors).intersection(set(m_neighbors))))

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
		pairs = gen_pairs(g.nodes(), samples)
		pair_mutuals = map(lambda x: common_neighbor_num(g, x[0], x[1]), pairs)
	else:
		from itertools import combinations
		pair_mutuals = map(lambda x: common_neighbor_num(g, x[0], x[1]), combinations(g.nodes(), 2))
	mCnt = Counter()
	for pm in iter(pair_mutuals):
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
	#attaching_edges = filter(lambda x: set(x).intersection(existing_nodes).__len__() == 1, new_edges)
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
	for attaching_edge in iter(identifying_attachment(g, h)):
		attached_node = filter(lambda x: existing_nodes.__contains__(x), attaching_edge)[0]
		attached_node_degree = nx.in_degree(g, attached_node) if isDirected else nx.degree(g, attached_node)
		hist[attached_node_degree] += 1
	return(hist)

def preferential_attachment_relative_prob(g, later_g):
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
	dc = degree_count(g)
	attachedCnt = identifying_attachment_degree_histogram(g, later_g)
	prefDict = dict()
	for d, v in attachedCnt.iteritems():
		prefDict[d] = v * N / dc[d]
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
		Count the number of enclosed node pairs that have d steps distance in g.

		Parameters:
		-----------
			g, h: NetworkX Graph, NetworkX DiGraph

		Returns:
		--------
			a dictionary of count of enclosed nodes, keyed with the distance between the pair, d.
	"""
		#identifying the distance between the nodes that later connected by the closure edges.
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
	t.__setitem__('cluster_prob', clustering_relative_prob(g, later_g))
	print ('processing pref_attach')
	t.__setitem__('pref_attach', preferential_attachment_relative_prob(g, later_g))
	print ('processing closure_dist')
	t.__setitem__('closure_dist', identifying_closure_distance_histogram(g, later_g))
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
	timestampformat = "%Y%m%d"
	outputTimeFormat = "%Y-%m-%d"
	ofs = ","

	def usage():
		"""print the usage"""
		print ("----------------------------------------")
		print ("read the temporal edge list")
		print
		print ("-h, --help: print this usage")
		print ("-r ...: read edgelist")
		print ("-i ...: read pickle")
		print ("-o ...: outputfile")
		print ("----------------------------------------")

	try:
		opts, args = getopt.getopt(argv, "hi:o:", ["help"])
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
		elif opt in ("-o"):
			outputFile = arg

	eDict, tDict = read_temporal_edges(read_path = inputFile, as_directed = False, enable_verbose = True)

	gSeries = EdgeSeries(is_directed = False, lifespan = 1000)	# set large lifespan to make it always be cumulative
	gSeries.update(tDict)
	gSeries.setup()

	gSeries.next(step = 60)
	g = gSeries.forward()
	gSeries.next(step = 60)
	later_g = gSeries.forward()

	db = LiteDB()
	fillinName = re.sub(".[^\.]+$", "", os.path.basename(inputFile)) if dataName is None else dataName
	timeinfo = "--".join([ min(tDict.keys()).strftime("%Y-%m-%d"), max(tDict.keys()).strftime("%Y-%m-%d") ])
	graph_key = "_".join([fillinName, timeinfo, 'd'])

	if db.__contains__(graph_key) and not forceSave:
		print ('updating in longitude mode')
		db[graph_key].update(longitude_pack(g, later_g))
	else:
		print ('writing in longitude mode')
		db.__setitem__(graph_key, longitude_pack(g, later_g))

	db.save(outputFile)

if __name__ == "__main__":
	main(sys.argv[1:])
