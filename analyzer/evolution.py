# Jing-Kai Lou (kaeaura@gamil.com)
# Wed Feb 15 14:30:08 CST 2012
# analyze the files in temporal folder

import re
import os
import sys
import getopt
import cPickle
import datetime
import networkx as nx
from scipy import average

__author__ = "Jing-Kai Lou (kaeaura@gmail.com)"

def reinforce(g, weight = "weight"):
	w = nx.get_edge_attributes(g, weight)
	if w.__len__():
		return(filter(lambda x: x > 1, w.values()).__len__() / float(w.__len__()))
	else:
		print("no such edge weight '%s'" % weight)
		return(None)

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

class GraphSeriesCollection:
	"""
		handler for the files that contains GraphSeries 
	"""
	def __init__(self, realm, lifespan, is_directed):
		"""docstring for __init__"""
		self.realm = realm
		self.lifespan = lifespan
		self.is_directed = is_directed
		self.table = dict()
	def _filenameMatch(self, s, pattern):
		"""docstring for _file"""
		p = re.compile(pattern)
		return(False if p.match(s) is None else True)
	def scan_file(self, path):
		"""docstring for scan_file"""
		gType = "d" if self.is_directed else "u"
		pattern = "^%ddays_%s_%s(_part\d+)?\.cpickle$" % (self.lifespan, self.realm, gType)
		matchedFiles = filter(lambda x: self._filenameMatch(x, pattern), map(lambda x: os.path.basename(x), os.listdir(path)))
		return(matchedFiles)
	def load_file(self, infile):
		"""docstring for load_file"""
		return(cPickle.load(file(infile, 'r')))
	def get_topology_dict(self, series):
		#for d, g in series.items():
		while len(series):
			g = series.pop()
			d = datetime.datetime.strptime(g.__str__(), "%Y-%m-%d")
			self.table[d] = {'size': g.size(), 'order': g.order()}
			g_order = self.table[d]['order']
			self.table[d].__setitem__('degree', average(g.degree().values()))
			sg = g.subgraph(nx.get_node_attributes(g, 'family').keys())

			if sg.__len__():
				self.table[d].__setitem__('f_size', sg.size())
				self.table[d].__setitem__('f_order', sg.order())
				self.table[d].__setitem__('f_degree', sum(sg.degree().values()) / float(sg.order()))
				sg_order = self.table[d]['f_order']
			else:
				sg_order = 0

			gDict = nx.get_node_attributes(g, 'gender')
			if gDict.__len__():
				self.table[d].__setitem__('gender_order', filter(lambda x: gDict.__contains__(x) and gDict[x] == 0, g.nodes_iter()).__len__())
				self.table[d].__setitem__('f_gender_order', filter(lambda x: gDict.__contains__(x) and gDict[x] == 0, sg.nodes_iter()).__len__())

			if self.is_directed:
				if sg_order:
					self.table[d].__setitem__('f_rep', reciprocity(sg))
					self.table[d].__setitem__('f_rei', reinforce(sg))
					self.table[d].__setitem__('f_asr', nx.degree_assortativity_coefficient(sg, weight = "weight"))
					self.table[d].__setitem__('f_asr_gender', nx.attribute_assortativity_coefficient(sg, "gender"))
					self.table[d].__setitem__('f_asr_race', nx.attribute_assortativity_coefficient(sg, "race"))

				if g_order:
					self.table[d].__setitem__('rep', reciprocity(g))
					self.table[d].__setitem__('rei', reinforce(g))
					self.table[d].__setitem__('asr', nx.degree_assortativity_coefficient(g, weight = "weight"))
					if nx.get_node_attributes(g, 'gender'):
						self.table[d].__setitem__('asr_gender', nx.attribute_assortativity_coefficient(g, "gender"))
					if nx.get_node_attributes(g, 'race'):
						self.table[d].__setitem__('asr_race', nx.attribute_assortativity_coefficient(g, "race"))
					scc = nx.strongly_connected_component_subgraphs(g)[0]
					self.table[d].__setitem__('scc_order', scc.order())
					self.table[d].__setitem__('scc_size', scc.size())
					del scc
					wcc = nx.weakly_connected_component_subgraphs(g)[0]
					self.table[d].__setitem__('wcc_order', wcc.order())
					self.table[d].__setitem__('wcc_size', wcc.size())
					del wcc
				else:
					self.table[d].__setitem__('rep', 0)
					self.table[d].__setitem__('scc_order', 0)
					self.table[d].__setitem__('scc_size', 0)
					self.table[d].__setitem__('wcc_order', 0)
					self.table[d].__setitem__('wcc_size', 0)
			else:
				if sg_order:
					self.table[d].__setitem__('fcc', nx.average_clustering(sg))

				if g_order:
					self.table[d].__setitem__('cc', nx.average_clustering(g))
					gcc = nx.connected_component_subgraphs(g)[0] if g_order else nx.Graph()
					self.table[d].__setitem__('gcc_order', gcc.order())
					self.table[d].__setitem__('gcc_size', gcc.size())
					#self.table[d].__setitem__('gcc_apl', nx.average_shortest_path_length(gcc))
					del gcc
				else:
					self.table[d].__setitem__('cc', 0)
					self.table[d].__setitem__('gcc_order', 0)
					self.table[d].__setitem__('gcc_size', 0)
					#self.table[d].__setitem__('gcc_apl', 0)
	def tofile(self, outfile, *args):
		"""docstring for tofile"""
		seperator = ','
		with open(outfile, "w") as F:
			if args:
				F.write("%s\n" % ("date" + seperator + seperator.join(args)))
			else:
				F.write("date\n")
			ks = self.table.keys()
			ks.sort()
			for k in ks:
				v = self.table[k]
				rowFields = k.strftime("%Y/%m/%d")
				contentFields = seperator.join([str(v[arg]) if v.__contains__(arg) else "-" for arg in args])
				F.write("%s\n" % seperator.join([rowFields, contentFields]))

	def toPickle(self, outfile, enable_update = True):
		"""docstring for topickle"""
		direction = 'd' if self.isDirected else 'u'
		if enable_update and os.path.exists(outfile):
			topoFeatureDict = cPickle.load(file(outfile, 'r'))
		else:
			topoFeatureDict = dict()

		if not topoFeatureDict.__contains__(realm):
			topoFeatureDict[realm] = dict()

		if not topoFeatureDict[realm].__contains__(direction):
			topoFeatureDict[realm][direction] = dict()

		if topoFeatureDict.__contains__(realm) and topoFeatureDict[realm].__contains__(direction):
			topoFeatureDict[realm][direction].update(self.table)
		cPickle.dump(topoFeatureDict, open(outfile, 'wb'))

def main(argv):
	"""docstring for main"""
	inFolder = None
	inFolder = "../../distillation/act_collections/graphs/temporal" #by default
	outfile = None
	realm = None
	isDirected = True
	lifespan = None
	enableVerbose = False

	def usage():
		"""docstring for usage"""
		print ("--")
		print ("read the temporal pickles to build data table")
		print
		print ("h, help: print this usage")
		print ("I: inFolder")
		print ("r: realm")
		print ("o: outfile")
		print ("u: set isDirected = False (True by default)")
		print ("d: value of lifespan")
		print

	try:
		opts, args = getopt.getopt(argv, "hI:o:r:ud:", ["help"])
	except getopt.GetoptError, err:
		print ("The given argv incorrect")
		usage()
		print (err)
		sys.exit(2)

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt in ("-I"):
			inFolder = arg
		elif opt in ("-r"):
			realm = arg
		elif opt in ("-u"):
			isDirected = False
		elif opt in ("-d"):
			lifespan = int(arg)
		elif opt in ("-o"):
			outfile = arg
		elif opt in ("-v"):
			enableVerbose = True
		else:
			assert False, "unhandle option"

	assert(type(realm) is str and type(lifespan) is int and os.path.exists(inFolder))
	t = GraphSeriesCollection(realm, lifespan, isDirected)
	infiles = t.scan_file(inFolder)

	while len(infiles):
		readFile = os.path.join(inFolder, infiles.pop())
		print (readFile)
		graphSeriesDict = t.load_file(readFile)
		t.get_topology_dict(graphSeriesDict)
		del(graphSeriesDict)

	if isDirected:
		t.tofile(outfile, 'order', 'size', 'gender_order', 'f_gender_order', 'degree', 'rep', 'rei', 'asr', 'asr_gender', 'asr_race', 'scc_order', 'scc_size', 'wcc_order', 'wcc_size', 'f_order', 'f_size', 'f_degree', 'f_rep', 'f_rei', 'f_asr', 'f_asr_gender', 'f_asr_race')
	else:
		t.tofile(outfile, 'order', 'size', 'degree', 'cc', 'f_size', 'f_cc', 'gcc_order', 'asr', 'gcc_size')

if __name__ == "__main__":
	main(sys.argv[1:])
