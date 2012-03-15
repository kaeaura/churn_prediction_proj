# Jing-Kai Lou (kaeaura@gamil.com)
# Tue Jan 31 12:35:21 CST 2012
# The characters name and family names have been replaced by cid and fid. Therefore, no need for hash now.
# (smaller logs)

from __future__ import print_function
import re
import os
import sys
import time
import getopt
import cPickle
import datetime
import networkx as nx
import itertools
from collections import defaultdict, Counter

__author__ = "Jing-Kai Lou (kaeaura@gmail.com)"

class GraphSeries():
	def __init__(self, tDict, is_directed, lifespan = 7, step = 1):
		self.timeslots = tDict
		self.isDirected = is_directed
		self.dDay, self.eDay = self.get_date_range()
		self.currentDay = self.dDay
		self.lifespan = lifespan
		self.step = step
	def flush(self):
		"""docstring for flush"""
		self.currentDay = self.dDay
	def get_date_range(self):
		"""return the date range """
		if self.timeslots:
			return(min(self.timeslots.keys()), max(self.timeslots.keys()))
	def shift(self, step = self.step):
		"""docstring for shift"""
		self.currentDay += datetime.timedelta(days = step)
	def forward(self):
		"""docstring for forward"""
		def edgeCounter(edgeSet):
			c = Counter()
			for e in edgeSet:
				c[e] += 1
			return(c)
		totalCount = Counter()
		for sd in itertools.ifilter(lambda x: self.lifespan >= (self.currentDay - x).days >= 0, self.timeslots.keys()):
			totalCount.update(edgeCounter(self.timeslots[sd]))
		d = dict(totalCount)
		subE = [(i, j, d[(i, j)]) for i, j in d.iterkeys()]
		subGName = self.currentDay.__format__('%Y-%m-%d')
		subG = nx.DiGraph(name = subGName) if self.isDirected else nx.Graph(name = subGName)
		subG.add_weighted_edges_from(subE)
		self.shift()
		del totalCount, subE
		return(subG)

def _itemToWeight(item):
	"""docstring for dictToWeights"""
	(i, j), w = item
	return((i, j, w))

def _fileToEdgeAttributes(read_path, as_directed = True, sep = " ", readLineNum = 100000, weight = "freq", enable_verbose = False):
	"""docstring for _fileToEdgeAttributes"""
	assert(os.path.exists(read_path))
	with open(read_path, "r") as F:
		if enable_verbose:
			print ("\t%s" % os.path.basename(read_path))
			print ("\t------------------")
			print ("\tstart reading file")
		lineCount = 0
		#edgeDict = defaultdict(int)
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
				timestamp, sNode, rNode, wFreq, wSum = line.strip().split(sep)
				sNode, rNode = int(sNode), int(rNode)
				t = datetime.datetime.strptime(timestamp, "%Y%m%d")
				#values = int(wFreq) if weight == "freq" else int(wSum)
				if as_directed:
					pairs = (sNode, rNode)
				else:
					pairs = (sNode, rNode) if sNode <= rNode else (rNode, sNode)
				#edgeDict[pairs] += values
				#eTimeDict[pairs].add(_strToDate(t))
				eTimeDict[pairs].add(t)
				tEdgeDict[t].add(pairs)
		if enable_verbose:
			print ("\t\t%d lines already read" % lineCount)
	#return (edgeDict, eTimeDict)
	return (eTimeDict, tEdgeDict)

def fileToStatus(read_path, sep = " ", readLineNum = 100000, enable_verbose = False):
	"""
	return a dictionary of sets that refers the profiles (account, gender, race) of node
	"""
	#0 fairyo08189 0 2
	#1 spadei98388 0 0
	#2 spaden42272 0 0
	assert(os.path.exists(read_path))
	with open(read_path, "r") as F:
		if enable_verbose:
			print ("\tstart reading file")
		lineCount = 0
		accountDict = dict()
		genderDict = dict()
		raceDict = dict()
		while True:
			lines = F.readlines(readLineNum)
			if not lines:
				break
			for line in lines:
				lineCount += 1
				if (lineCount % readLineNum) == 0 and enable_verbose:
					print ("\t\t%d lines already read" % lineCount)
				node, account, gender, race = line.strip().split(sep)
				node, gender, race = int(node), int(gender), int(race)
				accountDict.__setitem__(node, account)
				genderDict.__setitem__(node, gender)
				raceDict.__setitem__(node, race)
		if enable_verbose:
			print ("\t\t%d lines already read" % lineCount)
		return(accountDict, genderDict, raceDict)

def fileToMembership(read_path, sep = " ", readLineNum = 100000, enable_verbose = False):
	"""
	return a dictionary of sets that refers the families of node
	"""
	assert(os.path.exists(read_path))
	with open(read_path, "r") as F:
		if enable_verbose:
			print ("\tstart reading file")
		lineCount = 0
		memberDict = defaultdict(set)
		while True:
			lines = F.readlines(readLineNum)
			if not lines:
				break
			for line in lines:
				lineCount += 1
				if (lineCount % readLineNum) == 0 and enable_verbose:
					print ("\t\t%d lines already read" % lineCount)
				timestamp, fNode, sNode, wFreq, wSum = line.strip().split(sep)
				sNode, fNode = int(sNode), int(fNode)
				# todo: the timestamp to join a family? (for diffusion issue)
				#t = datetime.datetime.strptime(timestamp, "%Y%m%d")
				memberDict[sNode].add(fNode)
		if enable_verbose:
			print ("\t\t%d lines already read" % lineCount)
		return(memberDict)

def _fileToFriendship(read_path, as_directed = True, sep = " ", readLineNum = 100000, enable_verbose = False):
	"""docstring for fileToF"""
	assert(os.path.exists(read_path))
	with open(read_path, "r") as F:
		if enable_verbose:
			print ("\tstart reading file")
		lineCount = 0
		friendSet = set()
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
				if as_directed:
					friendSet.add((fNode, sNode))
				else:
					if int(fNode) <= int(sNode):
						friendSet.add((fNode, sNode))
					else:
						friendSet.add((sNode, fNode))
		if enable_verbose:
			print ("\t\t%d lines already read" % lineCount)
		return(list(friendSet))

def _toGraph(eTimeDict, as_directed = True, as_simple = True, weight = "weight"):
	if as_simple:
		G = nx.DiGraph() if as_directed else nx.Graph()
	else:
		G = nx.MultiDiGraph() if as_directed else nx.MultiGraph()
	if len(eTimeDict.keys()):
		#G.add_edges_from(map(lambda x: (x[0][0], x[0][1], {weight: x[1]}), edgeDict.items()))
		#G.add_edges_from(map(lambda x: (x[0][0], x[0][1], {weight: x[1]}), eTimeDict.items()))
		G.add_weighted_edges_from(map(lambda x: _itemToWeight(x), eTimeDict.items()))
		G.remove_edges_from(G.selfloop_edges())
	return(G)

def main(argv):
	"""readling the logs, and save it in pickle format"""
	try:
		opts, args = getopt.getopt(argv, "hi:m:f:S:o:s:ud:v:", ["help"])
	except getopt.GetoptError:
		print ("The given argv incorrect")

	enableVerbose = False
	inputChatFile = ""
	inputMemberFile = ""
	inputStatusFile = ""
	inputFriendshipFile = ""
	outputGPickleFile = ""
	outputGSeriesPickleFile = ""
	asDirected = True
	asSimple = True
	isMerged = False
	shiftSapnList = list()

	def usage():
		print ("turn the logs into graphs (format: pickle)")
		print ("-h, --help: print this usage")
		print ("-i ...: input path")
		print ("-m ...: membership path")
		print ("-f ...: friendship path")
		print ("-S ...: status path")
		print ("-o ...: output path (underlay graph)")
		print ("-s ...: output path (list of temporal series graphs)")
		print ("-u : read as undirected")
		print ("-d 7,14,1000: length of lifespan in days. handle multiple inputs seprated by ,")
		print ("-v: enable verbose")

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt in ("-i"):
			inputChatFile = arg
		elif opt in ("-m"):
			inputMemberFile = arg
		elif opt in ("-f"):
			inputFriendshipFile = arg
		elif opt in ("-o"):
			outputGPickleFile = arg
		elif opt in ("-s"):
			outputGSeriesPickleFile = arg
		elif opt in ("-u"):
			asDirected = False
		elif opt in ("-S"):
			inputStatusFile = arg
		elif opt in ("-M"):
			isMerged = True
		elif opt in ("-d"):
			shiftSapnList = [int(ss) for ss in arg.split(',')]
		elif opt in ("-v"):
			enableVerbose = True

	if enableVerbose:
		print ("inputChatFile: %s" % inputChatFile)
		print ("inputMemberFile: %s" % inputMemberFile)
		print ("inputFriendshipFile: %s" % inputMemberFile)
	timeTotalStart = time.time()

	timeLoadStart = time.time()
	# readFile: node-list, edge-list
	eDict, tDict = _fileToEdgeAttributes(read_path = inputChatFile, as_directed = asDirected, enable_verbose = enableVerbose)
	# readFile: status
	aDict, gDict, rDict = None, None, None
	if os.path.exists(inputStatusFile):
		aDict, gDict, rDict = fileToStatus(read_path = inputStatusFile, enable_verbose = enableVerbose)
	# readFile: membership
	mDict = None
	if os.path.exists(inputMemberFile):
		if enableVerbose:
			print ('\t\tadditional membership node attributes are added')
		mDict = fileToMembership(read_path = inputMemberFile, enable_verbose = enableVerbose)
	# readFile: friendship
	fList = None
	if os.path.exists(inputFriendshipFile):
		if enableVerbose:
			print ('\t\tadditional friendship edge attributes are added')
		fList = _fileToFriendship(read_path = inputFriendshipFile, enable_verbose = enableVerbose)
	else:
		print ("\t%s does not exist" % inputFriendshipFile)
	timeLoadEnd = time.time()
	print ("\t[LoadTime] %.2f sec" % (timeLoadEnd - timeLoadStart))

	# buildGraph
	timeBuildStart = time.time()
	G = _toGraph(eDict, as_directed = asDirected, as_simple = asSimple)
	hMDict = None
	if mDict is not None:
		hMDict = defaultdict(set)
		for k in set(mDict.keys()) & set(G.nodes()):
			hMDict[k] = mDict.pop(k)
		nx.set_node_attributes(G, 'family', hMDict)
	hADict, hGDict, hRDict = None, None, None
	if aDict is not None and gDict is not None and rDict is not None:
		hADict = dict()
		hGDict = dict()
		hRDict = dict()
		for k in set(aDict.keys()) & set(G.nodes()):
			hADict.__setitem__(k, aDict.pop(k))
			hGDict.__setitem__(k, gDict.pop(k))
			hRDict.__setitem__(k, rDict.pop(k))
		nx.set_node_attributes(G, 'account', hADict)
		nx.set_node_attributes(G, 'gender', hGDict)
		nx.set_node_attributes(G, 'race', hRDict)
	if fList is not None:
		timeFilterStart = time.time()
		nodeSet = set(G.nodes())
		inducedFList = filter(lambda x: set(x).issubset(nodeSet), fList)
		inducedFList = list(set(inducedFList))
		timeFilterEnd = time.time()
		#print ("\t\t[FilterTime] %.2f sec" % (timeFilterEnd - timeFilterStart))

		timeAddingStart = time.time()
		#G.add_edges_from(map(lambda x: (x[0], x[1], {'friend': 1}), inducedFList))
		G.add_weighted_edges_from(map(lambda x: _itemToWeight(x), zip(inducedFList, [1] * len(inducedFList))), weight = 'friend')
		timeAddingEnd = time.time()
		#print ("\t\t[AddingEdgesTime] %.2f sec" % (timeAddingEnd - timeAddingStart))
		del inducedFList
	del fList
	timeBuildEnd = time.time()
	print ("\t[BuildTime] %.2f sec" % (timeBuildEnd - timeBuildStart))

	# saveFile directory
	gSaveDir = os.path.dirname(outputGPickleFile)
	if len(gSaveDir) and not os.path.exists(gSaveDir):
		os.makedirs(gSaveDir)
	gSeriesSaveDir = os.path.dirname(outputGSeriesPickleFile)
	if len(gSeriesSaveDir) and not os.path.exists(gSeriesSaveDir):
		os.makedirs(gSeriesSaveDir)

	# saveFile [ Underlay Graph ]
	timeSaveStart = time.time()
	nx.write_gpickle(G, outputGPickleFile)
	timeSaveEnd = time.time()
	print ("\t[SaveTime] %.2f sec" % (timeSaveEnd - timeSaveStart))
	print ("\t[FileSaved] graph is saved")

	# saveSeriesFile [spanlife]
	temporalSizeLimitation = 3000000
	for shiftSpan in shiftSapnList:
		print ("\t[Process-%d-Series]" % shiftSpan)
		timeShiftStart = time.time()
		partIndex = 1
		seriesBasename = "%ddays_%s" % (shiftSpan, os.path.basename(outputGSeriesPickleFile))
		seriesFilename = os.path.join(os.path.dirname(outputGSeriesPickleFile), seriesBasename)
		seriesFilenameParts = list()
		temporalGraphs = dict()
		temporalSize = 0
		gSeries = GraphSeries(tDict, is_directed =  asDirected, lifespan = shiftSpan, step = 1)
		while gSeries.currentDay <= gSeries.eDay:
			print ("\t\t[%s | %s]\r" % (gSeries.currentDay.strftime("%d/%m,%y"), gSeries.eDay.strftime("%d/%m,%y")), end = "")
			sys.stdout.flush()
			tG = gSeries.forward()
			if hMDict:
				nx.set_node_attributes(tG, 'family', {k: hMDict[k] for k in filter(lambda x: hMDict.__contains__(x), tG.nodes_iter())})
			if hGDict:
				nx.set_node_attributes(tG, 'gender', {k: hGDict[k] for k in filter(lambda x: hGDict.__contains__(x), tG.nodes_iter())})
			if hRDict:
				nx.set_node_attributes(tG, 'race', {k: hRDict[k] for k in filter(lambda x: hRDict.__contains__(x), tG.nodes_iter())})
			temporalGraphs[gSeries.currentDay] = tG
			temporalSize += tG.size()
			del tG
			if (temporalSize > temporalSizeLimitation):
				print ("\n\t\t reach the limitation of edges (%d); so split out; part - %d" % (temporalSizeLimitation, partIndex))
				seriesFilenamePart = "%s_part%d.cpickle" % (re.sub("\.[cCgG][pP]ickle$", "", seriesFilename), partIndex)
				seriesFilenameParts.append(seriesFilenamePart)
				cPickle.dump(temporalGraphs, open(seriesFilenamePart, "wb"))
				partIndex += 1
				del temporalGraphs
				temporalGraphs = dict()
				temporalSize = 0
		if temporalGraphs:
			if partIndex == 1:
				cPickle.dump(temporalGraphs, open(seriesFilename, "wb"))
			else:
				cPickle.dump(temporalGraphs, open("%s_part%d.cpickle" % (re.sub("\.[cCgG][pP]ickle$", "", seriesFilename), partIndex), "wb"))
		if isMerged and seriesFilenameParts:
			print ("\n\t\tmerging parts...")
			for sfile in seriesFilenameParts:
				if os.path.exists(sfile):
					temporalGraphs.update(cPickle.load(open(sfile, "r")))
				else:
					print ("\t\tfile %s does not exist\n", sfile)
			cPickle.dump(temporalGraphs, open(seriesFilename, "wb"))
			print ("\t\tmerge completed")
		del temporalGraphs, gSeries, seriesFilenameParts
		timeShiftEnd = time.time()
		print ("\n\t[FileSaved] %dd graph series saved" % shiftSpan)
		print ("\t[%d-day ShiftTime] %.2f sec\n" % (shiftSpan, timeShiftEnd - timeShiftStart))

	timeTotalEnd = time.time()
	del mDict, aDict, gDict, rDict, eDict, tDict
	print ("\t--")
	print ("\t[TotalTime] %.2f mins\n" % ((timeTotalEnd - timeTotalStart) / 60))

if __name__ == "__main__":
	main(sys.argv[1:])
