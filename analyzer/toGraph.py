# Jing-Kai Lou (kaeaura@gamil.com)
# Tue Jan 31 12:35:21 CST 2012
# The characters name and family names have been replaced by cid and fid. Therefore, no need for hash now.
# (smaller logs)

from __future__ import print_function
import re
import sys
import time
import getopt
import cPickle
import datetime
import networkx as nx
import itertools
from os import makedirs
from os.path import exists, dirname, basename, join
from collections import defaultdict, Counter

__author__ = "Jing-Kai Lou (kaeaura@gmail.com)"

class EdgeSeries(defaultdict):
	"""
	This class is used to handle a series of edges with time-series, and perform a manipulation on them.
	key: datetime obj, timestamp
	values: iterable obj, edgelists

	is_directed: determine the type of graph when creating graphs. creating directed graphs by default
	lifespan: the length of observation period (i.e. to cumulate the edges). 1 week by default
	"""
	def __init__(self, is_directed = True, lifespan = 7):
		"""set default parameters"""
		self.isDirected = is_directed
		self.lifespan = lifespan
		self.dDay, self.eDay, self.currentDay = None, None, None
	def setup(self):
		"""set up the current date, start date, and the end date"""
		if self.__len__():
			self.dDay, self.eDay = self.get_date_range()
			self.currentDay = self.dDay
	def flush(self):
		"""set the current date as the start date (the minimum timespam key)"""
		if self.currentDay is not None and self.dDay is not None:
			self.currentDay = self.dDay
	def get_date_range(self):
		"""return the date range of keys"""
		if self.__len__():
			return(min(self.keys()), max(self.keys()))
	def next(self, step = 1):
		"""currentday + 1"""
		self.currentDay += datetime.timedelta(days = step)
	def count_value(self, key):
		"""count the edges"""
		c = Counter()
		if self.__contains__(key):
			for e in self[key]:
				c[e] += 1
		return(c)
	def count_values(self, lifespan = None):
		"""docstring for count_values"""
		span = self.lifespan if lifespan is None else lifespan
		totalCount = Counter()
		for key in itertools.ifilter(lambda x: span >= (self.currentDay - x).days >= 0, self.keys()):
			totalCount.update(self.count_value(key))
		return(totalCount)
	def create_graph(self, weighted_ebunch, node_attr = None, edge_attr = None):
		"""create graphs according to the dictionary items"""
		gName = self.currentDay.__format__('%Y-%m-%d')
		g = nx.DiGraph(name = gName) if self.isDirected else nx.Graph(name = gName)
		g.add_weighted_edges_from(weighted_ebunch)
		return(g)
	def attach_node_attr(self, g, node_attr, node_attr_name = "family"):
		"""attach the node attributes to the created graph"""
		# make sure that the node attributes only
		nx.set_node_attributes(g, node_attr_name, {k: node_attr[k] for k in filter(lambda x: node_attr.__contains__(x), g.nodes_iter())})
		return(g)
	def forward(self, step = 1, **kwargs):
		"""
		collect the past <lifespan> days data until currentday and then return a graph object base on these data.
		move the current day 1 day ahead
		"""
		d = dict(self.count_values())
		subE = [(i, j, d[(i, j)]) for i, j in d.iterkeys()]
		g = self.create_graph(weighted_ebunch = subE)
		if kwargs:
			for key in kwargs:
				g = self.attach_node_attr(g, node_attr = kwargs[key], node_attr_name = key)
		self.next(step = step)
		return(g)


def read_temporal_edges(read_path, as_directed = True, sep = " ", timestamp_format = "%Y%m%d", readLineNum = 100000, enable_verbose = False, collapse = False, weightCol = None):
	"""
		Read the temporal edgelist with line format (time, node1, node2) 

		Parameters:
		-----------
			read_path: str, 
				input file path
			as_directed: bool, optional, (default = True)
				If True, treat the logs as directed edges
			sep: str, optional (default = " ")
				field seperator
			timestamp_format: str, optional (default = '%Y%m%d')
			readLineNum: int, optional, (default = 100000)
				number of lines to read each time
			enable_verbose: bool, optiona, (default = False)
				If True, show the verbose in command line
			collapse: bool, optional (defualt = False)
				If True, the time information of edges are removed. That means the this function reutnrs edge dict instead of eTimeDict.
			weightCol: int, optional, (default = None)
				the index of weight value, the 0 present the 1st column.
		Returns:
		--------
			eTimeDict, a dictionary of timestamps keyed with edges / edgeDict, a dictionary of weights keyed with edges
			tEdgeDict, a dictionary of edges keyed with timestamps
	""" 
	with open(read_path, "r") as F:
		if enable_verbose:
			print ("\t%s" % basename(read_path))
			print ("\t------------------")
			print ("\tstart reading file")
		lineCount = 0
		if collapse:
			from collections import Counter
			eTimeDict = Counter()
		else:
			eTimeDict = defaultdict(set)
		tEdgeDict = defaultdict(set)
		# read file
		while True:
			lines = F.readlines(readLineNum)
			if not lines:
				break
			for line in lines:
				lineCount += 1
				if (lineCount % readLineNum) == 0 and enable_verbose:
					print ("\t\t%d lines already read" % lineCount)
				readIn_variables = line.strip().split(sep)
				if len(readIn_variables) >= 3:
					timestamp, sNode, rNode = readIn_variables[:3]
					sNode, rNode = int(sNode), int(rNode)
					t = datetime.datetime.strptime(timestamp, timestamp_format)
					pairs = (sNode, rNode)
					if not as_directed: 
						pairs = tuple(sorted(list(pairs)))
					weight = int(readIn_variables[weightCol]) if type(weightCol) is int else 1
					tEdgeDict[t].add(pairs)
					if collapse:
						eTimeDict[pairs] += weight
					else:
						eTimeDict[pairs].add(t)
		if enable_verbose:
			print ("\t\t%d lines already read" % lineCount)
	return (eTimeDict, tEdgeDict)

def read_temporal_cum_edges(read_path, as_directed = True, sep = " ", timestamp_format = "%Y%m%d", readLineNum = 100000, enable_verbose = False, weightCol = None):
	"""
		Read the temporal edgelis, but treat them as a snapshot (timestamp, node1, node2, ...)

		Parameters:
		-----------
			read_path: str, 
				input file path
			as_directed: bool, optional, (default = True)
				If True, treat the logs as directed edges
			sep: str, optional (default = " ")
				field seperator
			timestamp_format: str, optional (default = '%Y%m%d')
			readLineNum: int, optional, (default = 100000)
				number of lines to read each time
			enable_verbose: bool, optiona, (default = False)
				If True, show the verbose in command line
			weightCol: int, optional, (default = Node)
				the index of weight value, the 0 present the 1st column.
		Returns:
		--------
			edgeWeight, a dictionary of weighted values keyed with edges
	"""
	from collections import Counter
	with open(read_path, "r") as F:
		if enable_verbose:
			print ("\tstart reading file")
		lineCount = 0
		edgeWeight = Counter()
		durationSet = set()
		while True:
			lines = F.readlines(readLineNum)
			if not lines:
				break
			for line in lines:
				lineCount += 1
				if (lineCount % readLineNum) == 0 and enable_verbose:
					print ("\t\t%d lines already read" % lineCount)
				readIn_variables = line.strip().split(sep)
				if len(readIn_variables) >= 3:
					timestamp, sNode, rNode = readIn_variables[:3]
					sNode, rNode = int(sNode), int(rNode)
					durationSet.add(datetime.datetime.strptime(timestamp, timestamp_format))
					pairs = (sNode, rNode)
					if not as_directed:
						pairs = tuple(sorted(list(pairs)))
				weight = int(readIn_variables[weightCol]) if weightCol and type(weightCol) is int else 1
				edgeWeight[pairs] += weight
		if enable_verbose:
			print ("\t\t%d lines already read" % lineCount)
		return(dict(edgeWeight), { min(durationSet) : 0, max(durationSet) : 0 })

def read_node_attrs(read_path, fields = list(), sep = " ", readLineNum = 100000, enable_verbose = False, enable_header = False):
	"""
	Read the node attributes with line format (node, *fields)

	Parameters:
	-----------
		read_path: str,
			input file path
		fields: list of str, optional, (default = [])
			the fields to read
		sep: str, optional (default = " ")
			field seperator
		readLineNum: int, optional, (default = 100000)
			number of lines to read each time
		enable_verbose: bool, optiona, (default = False)
			if True, show the verbose in command line
		enable_header: bool, optional, (default = False)
			if True, then take the first line as parameter fields
	Returns:
	--------
		node_attr, a dictionary of node attribute dictionaries keyed with attribute names (i.e. fields)
	Example:
	--------
		file: Alice_Node_Attr.txt
		#0 fairyo08189 0 2
		#1 spadei98388 0 0
		#2 spaden42272 0 0

		node_attr = read_node_attrs(read_path = 'Alice_Node_Attr', fields = ['account', 'gender', 'race'])
		node_attr['race'] = {0: '2', 1: '0', 2: '0'}
		node_attr['account'].values() = ['fairyo08189', 'spadei98388', 'spaden42272'] 
	"""
	with open(read_path, "r") as F:
		if enable_verbose:
			print ("\tstart reading file")
		lineCount = 0
		node_attr = defaultdict(dict)
		while True:
			lines = F.readlines(readLineNum)
			if not lines:
				break
			for line in lines:
				lineCount += 1
				if (lineCount % readLineNum) == 0 and enable_verbose:
					print ("\t\t%d lines already read" % lineCount)
				readIn_variables = line.strip().split(sep)
				if enable_header and lineCount == 1:
					fields = list(readIn_variables[1:])
					next
				if readIn_variables: node = int(readIn_variables.pop(0))
				for field in fields:
					node_attr[field].__setitem__(node, readIn_variables.pop(0))
		if enable_verbose:
			print ("\t\t%d lines already read" % lineCount)
		return(node_attr)

def read_node_attrSet(read_path, node_col, attr_col, sep = " ", readLineNum = 100000, enable_verbose = False):
	"""
	Read the node attributes as sets. Therefore, the node attributes are handled as elements.

	Parameters:
	-----------
		read_path: str,
			input file path
		node_col: int, 
			the columen index to read as node 
		attr_col: int,
			the columen index to read as node_attr element
		readLineNum: int, optional, (default = 100000)
			number of lines to read each time
		enable_verbose: bool, optiona, (default = False)
			if True, show the verbose in command line
	Returns:
	--------
		node_attrSet, a dictionary of set keyed with node
	"""
	with open(read_path, "r") as F:
		if enable_verbose:
			print ("\tstart reading file")
		lineCount = 0
		node_attrSet = defaultdict(set)
		while True:
			lines = F.readlines(readLineNum)
			if not lines:
				break
			for line in lines:
				lineCount += 1
				if (lineCount % readLineNum) == 0 and enable_verbose:
					print ("\t\t%d lines already read" % lineCount)
				readIn_variables = line.strip().split(sep)
				if len(readIn_variables):
					sNode = readIn_variables[node_col - 1]
					sElt = readIn_variables[attr_col - 1]
					node_attrSet[int(sNode)].add(sElt)
		if enable_verbose:
			print ("\t\t%d lines already read" % lineCount)
		return(node_attrSet)

def read_edges(read_path, as_directed = True, sep = " ", readLineNum = 100000, enable_verbose = False):
	"""
		Read the edgelist with line format (node1, node2)

		Parameters:
		-----------
			read_path: str,
				input file path
			as_directed: bool, optional, (default = True)
				If True, treat the logs as directed edges
			sep: str, optional (default = " ")
				field seperator
			readLineNum: int, optional, (default = 100000)
				number of lines to read each time
			enable_verbose: bool, optiona, (default = False)
				If True, show the verbose in command line
		Returns:
		--------
			edges, a list of edges
	"""
	with open(read_path, "r") as F:
		if enable_verbose:
			print ("\tstart reading file")
		lineCount = 0
		edges = set()
		while True:
			lines = F.readlines(readLineNum)
			if not lines:
				break
			for line in lines:
				lineCount += 1
				if (lineCount % readLineNum) == 0 and enable_verbose:
					print ("\t\t%d lines already read" % lineCount)
				try:
					fNode, sNode = line.strip().split(sep)
					sNode, fNode = int(sNode), int(fNode)
				except ValueError:
					next
				pairs = (fNode, sNode)
				if not as_directed: 
					pairs = tuple(sorted(list(pairs)))
				edges.add(pairs)
		if enable_verbose:
			print ("\t\t%d lines already read" % lineCount)
		return(list(edges))

def _itemToWeight(item):
	(i, j), w = item
	return((i, j, w))

def _toGraph(eTimeDict, as_directed = True, weight = "weight", name = None):
	G = nx.DiGraph(name = name) if as_directed else nx.Graph(name = name)
	if len(eTimeDict.keys()):
		G.add_weighted_edges_from(map(lambda x: _itemToWeight(x), eTimeDict.items()))
		G.remove_edges_from(G.selfloop_edges())
	return(G)

def main(argv):
	"""readling the logs, and save it in pickle format"""
	try:
		#opts, args = getopt.getopt(argv, "hi:m:f:S:o:s:xN:d:vw:", ["help"])
		opts, args = getopt.getopt(argv, "hi:uF:o:as:xd:w:S:m:f:N:v", ["help"])
	except getopt.GetoptError:
		print ("The given argv incorrect")

	enableVerbose = False
	inputChatFile = None
	timestampFormat = "%Y%m%d"
	importMember = False
	inputMemberFile = None
	importStatus = False
	inputStatusFile = None
	inputFriendshipFile = None
	outputGPickleFile = None
	asStatic = False
	outputGSeriesPickleFile = None
	asDirected = True
	isMerged = False
	shiftSpanList = list()
	movingStep = 1
	enableCompact = True
	node_status_attrs = [ 'account', 'gender', 'race' ] 
	temporalSizeLimitation = 3000000

	def usage():
		print
		print ("----------------------------------------")
		print ("read the logs and output pickles describing graphs")
		print
		print ("-h, --help: print this usage")
		print ("-i ...: input path (format: timestamp(%Y%m%d) sid rid")
		print ("-u : [ optional ], read files as undirected")
		print ("-F ...: [ optional ] timestamp format, default = '%Y%m%d'")
		print ("-o ...: output path for graph")
		print ("-a : output as static graph")
		print ("-s ...: output path for temporal graph series")
		print ("\t-x : [ optional, only works if -s given ], disable compact save format for list of temporal series graphs")
		print ("\t-d 7,14,1000: [ requiered if -s given ], length of lifespan (in days) of temporal graph series. can handle multiple inputs seprated by ','")
		print ("\t-w: [ optional, only works if -s given ], step width of tempral graph series, 1 day by default")
		print ("-S ...: [ optional ], applying node attributes, status path")
		print ("-m ...: [ optional ], applying node attributes (as sets), membership path")
		print ("-f ...: [ optional ], applying hete. edges, friendship path")
		print ("-N ... : [ optional ], the size of compact temporal sereis graphs, 3000000 (edges) by default")
		print ("-v : [ optional ], enable verbose mode")
		print ("----------------------------------------")

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt in ("-i"):
			inputChatFile = arg
		elif opt in ("-m"):
			inputMemberFile = arg
		elif opt in ("-S"):
			inputStatusFile = arg
		elif opt in ("-f"):
			inputFriendshipFile = arg
		elif opt in ("-o"):
			outputGPickleFile = arg
		elif opt in ("-a"):
			asStatic = True
		elif opt in ("-s"):
			outputGSeriesPickleFile = arg
		elif opt in ("-x"):
			enableCompact = False
		elif opt in ("-N"):
			temporalSizeLimitation = int(arg)
		elif opt in ("-u"):
			asDirected = False
		elif opt in ("-M"):
			isMerged = True
		elif opt in ("-d"):
			shiftSpanList = [int(ss) for ss in arg.split(',')]
		elif opt in ("-w"):
			movingStep = int(arg)
		elif opt in ("-v"):
			enableVerbose = True
		elif opt in ("-F"):
			timestampFormat = arg

	if enableVerbose:
		print ("inputChatFile: %s" % inputChatFile)
		print ("inputMemberFile: %s" % inputMemberFile)
		print ("inputFriendshipFile: %s" % inputMemberFile)

	# checking the arguments
	if not outputGPickleFile and not outputGSeriesPickleFile:
		print ("\tWarnning! Neither given graph output path nor given temporal graph series output path, so skip")
		print ("\targument -o or -s needed")
		exit()
	if not shiftSpanList and outputGSeriesPickleFile:
		print ("\tWarnning! Given temporal graph series output path but without life span length, so skip")
		print ("\targument -d needed")
		exit()

	timeTotalStart = time.time()
	timeLoadStart = time.time()

	# readFile
#	if asStatic:
#		eDict, tDict = read_temporal_cum_edges(read_path = inputChatFile, as_directed = asDirected, enable_verbose = enableVerbose, weightCol = 4)
#	else:
#		eDict, tDict = read_temporal_edges(read_path = inputChatFile, timestamp_format = timestampFormat, as_directed = asDirected, enable_verbose = enableVerbose)

	eDict, tDict = read_temporal_edges(read_path = inputChatFile, timestamp_format = timestampFormat, as_directed = asDirected, enable_verbose = enableVerbose, collapse = asStatic, weightCol = 4)

	# readFile: status
	attrsDict = None
	if inputStatusFile and exists(inputStatusFile):
		importStatus = True
		if enableVerbose: print ('\t\tadditional status node attributes are added')
		attrsDict = read_node_attrs(read_path = inputStatusFile, fields = ['account', 'gender', 'race'], enable_verbose = enableVerbose)

	# readFile: membership
	mDict = None
	if inputMemberFile and exists(inputMemberFile):
		importMember = True
		if enableVerbose: print ('\t\tadditional membership node attributes are added')
		mDict = read_node_attrSet(read_path = inputMemberFile, node_col = 3, attr_col = 2, enable_verbose = enableVerbose)

	# readFile: friendship
	fList = None
	if inputFriendshipFile is not None and exists(inputFriendshipFile):
		if enableVerbose: print ('\t\tadditional friendship edge attributes are added')
		fList = read_edges(read_path = inputFriendshipFile, as_directed = asDirected, enable_verbose = enableVerbose)

	timeLoadEnd = time.time()
	print ("\t[LoadTime] %.2f sec" % (timeLoadEnd - timeLoadStart))

	# buildGraph
	timeBuildStart = time.time()
	G = _toGraph(eDict, as_directed = asDirected, name = '--'.join([ min(tDict.keys()).strftime('%Y-%m-%d'), max(tDict.keys()).strftime('%Y-%m-%d') ]))
	nodes = set(G.nodes())

	# attach node attributes: family, account, gender, ...
	nodeAttrs = defaultdict(dict)

	if mDict: 
		#for k in set(mDict.keys()) & set(G.nodes()):
		for k in itertools.ifilter(lambda x: nodes.__contains__(x), mDict.iterkeys()):
			nodeAttrs['family'].__setitem__(k, mDict[k])
		del mDict

	if attrsDict:
		for attr in attrsDict.iterkeys():
			for k in itertools.ifilter(lambda x: nodes.__contains__(x), attrsDict[attr].iterkeys()):
				nodeAttrs[attr].__setitem__(k, attrsDict[attr][k])

	for nodeAttr in nodeAttrs.iterkeys():
		nx.set_node_attributes(G, nodeAttr, nodeAttrs[nodeAttr])

	# attach new (hete-) links
	if fList: 
		inducedFList = filter(lambda x: set(x).issubset(nodes), fList)
		G.add_weighted_edges_from(map(lambda x: _itemToWeight(x), zip(inducedFList, [1] * len(inducedFList))), weight = 'friend')
		del inducedFList
	del fList

	timeBuildEnd = time.time()
	print ("\t[BuildTime] %.2f sec" % (timeBuildEnd - timeBuildStart))

	# saveFile [ Underlay Graph ] =============
	if outputGPickleFile is not None:
		gSaveDir = dirname(outputGPickleFile)
		if len(gSaveDir) and not exists(gSaveDir):
			makedirs(gSaveDir)

		timeSaveStart = time.time()
		nx.write_gpickle(G, outputGPickleFile)
		timeSaveEnd = time.time()
		print ("\t[SaveTime] %.2f sec" % (timeSaveEnd - timeSaveStart))
		print ("\t[FileSaved] graph is saved")
		print ("\t[Destination] %s" % outputGPickleFile)
		print 

	# saveSeriesFile [ Temporal Graph Series] =============
	if outputGSeriesPickleFile:
		gSeriesSaveDir = dirname(outputGSeriesPickleFile)
		if gSeriesSaveDir and not exists(gSeriesSaveDir):
			makedirs(gSeriesSaveDir)

		for shiftSpan in shiftSpanList:
			print ("\t[Process-%d-Series]" % shiftSpan)
			timeShiftStart = time.time()

			gSeries = EdgeSeries(is_directed = asDirected, lifespan = shiftSpan)
			gSeries.update(tDict)
			gSeries.setup()

			if enableCompact:
				seriesFilename = outputGSeriesPickleFile
				partIndex = 1

				while gSeries.currentDay <= gSeries.eDay:
					temporalGraphs = list()
					temporalSize = temporalGraphs.__len__()
					while temporalSize <= temporalSizeLimitation and gSeries.currentDay <= gSeries.eDay:
						print ("\t\t[%s | %s]\r" % (gSeries.currentDay.strftime("%d/%m,%y"), gSeries.eDay.strftime("%d/%m,%y")), end = "")
						sys.stdout.flush()
						tG = gSeries.forward(step = movingStep, **nodeAttrs)
						temporalGraphs.append(tG)
						temporalSize += tG.size()

					if gSeries.currentDay > gSeries.eDay:
						break
					else:
						print ("\n\t\t reach the limitation of edges (%d); so split out; part - %d" % (temporalSizeLimitation, partIndex))
						seriesBasename = "c%d-s%d-l%d_%s" % (shiftSpan, movingStep, len(temporalGraphs), basename(outputGSeriesPickleFile))
						seriesFilename = join(gSeriesSaveDir, seriesBasename)
						seriesFilenamePart = "%s_part%d.cpickle" % (re.sub("\.[cCgG][pP]ickle$", "", seriesFilename), partIndex)
						cPickle.dump(temporalGraphs, open(seriesFilenamePart, "wb"))
						partIndex += 1

				if temporalGraphs:
					seriesBasename = "c%d-s%d-l%d_%s" % (shiftSpan, movingStep, len(temporalGraphs), basename(outputGSeriesPickleFile))
					seriesFilename = join(gSeriesSaveDir, seriesBasename)
					if partIndex == 1:
						cPickle.dump(temporalGraphs, open(seriesFilename, "wb"))
					else:
						seriesFilenamePart = "%s_part%d.cpickle" % (re.sub("\.[cCgG][pP]ickle$", "", seriesFilename), partIndex)
						cPickle.dump(temporalGraphs, open(seriesFilenamePart, "wb"))

				del temporalGraphs, gSeries 

			else:
				seriesFilename = outputGSeriesPickleFile
				partIndex = movingStep

				while gSeries.currentDay <= gSeries.eDay:
					print ("\t\t[%s | %s]\r" % (gSeries.currentDay.strftime("%d/%m,%y"), gSeries.eDay.strftime("%d/%m,%y")), end = "")
					sys.stdout.flush()
					tG = gSeries.forward(step = movingStep, **nodeAttrs)

					seriesFilenamePart = "%s_c%d-s%d-l%d.gpickle" % (re.sub("\.[cCgG][pP]ickle$", "", seriesFilename), shiftSpan, movingStep, partIndex)
					cPickle.dump(tG, open(seriesFilenamePart, "wb"))
					partIndex += movingStep

				del tG

			timeShiftEnd = time.time()
			print ("\n\t[FileSaved] %dd graph series saved" % shiftSpan)
			print ("\t[Destination] %s" % (gSeriesSaveDir if gSeriesSaveDir else "."))
			print ("\t[%d-day ShiftTime] %.2f sec\n" % (shiftSpan, timeShiftEnd - timeShiftStart))

	timeTotalEnd = time.time()
	del eDict, tDict
	print ("\t--")
	print ("\t[TotalTime] %.2f mins\n" % ((timeTotalEnd - timeTotalStart) / 60))

if __name__ == "__main__":
	main(sys.argv[1:])
