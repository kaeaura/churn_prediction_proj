# Jing-Kai Lou (kaeaura@gamil.com)
# Tue Mar 13 14:40:49 CST 2012

import os
import re
import sys
import getopt
import cPickle

__author__ = "Jing-Kai Lou (kaeaura@gmail.com)"


class LiteDB(dict):
	def load(self, path, structUpdate = False):
		loadDict = cPickle.load(file(path, 'r'))
		self.attach(loadDict, structUpdate = structUpdate)
	def save(self, path):
		"""docstring for save"""
		cPickle.dump(self, file(path, 'w'))
	def attach(self, loadDict, structUpdate = False):
		"""docstring for attach"""
		if structUpdate:
			aKeys = set(loadDict.keys()).intersection(set(self.keys()))
			bKeys = set(loadDict.keys()).difference(aKeys)
			while len(aKeys):
				a = aKeys.pop()
				self[a].update(loadDict[a])
			while len(bKeys):
				b = bKeys.pop()
				self[b] = loadDict[b]
		else:
			self.update(loadDict)
	def checkkeys(self):
		"""docstring for checkstruc"""
		meta_keys = set.union(*[ set(v.keys()) for v in self.itervalues() ])
		return(all([ meta_keys.__eq__(set(self[k].keys())) for k in self.iterkeys() ]))
	def showkeys(self):
		deepkeys = set.intersection(*[set(self[k].keys()) for k in self.iterkeys()]) if self.__len__() else set()
		return(deepkeys)
	def tolist(self, path, *args):
		#deepkeys = set.intersection(*[set(self[k].keys()) for k in self.iterkeys()])
		deepkeys = self.showkeys()
		legal_args = filter(lambda x: x in deepkeys, list(args))
		legal_args.sort()
		with open(path, 'w') as F:
			F.write("%s,%s\n" % ('dataset', ','.join(legal_args)))
			for k in self.iterkeys():
				def l2str(l, joiner = "/"): return(joiner.join(map(str, l)))
				fields = [l2str(self[k][l]) if hasattr(self[k][l], "__iter__") else self[k][l] for l in legal_args]
				F.write("%s,%s\n" % (k, l2str(fields, joiner = ",")))

def main(argv):
	"""manipulation db via os"""
	inputFile = None
	inputDir = None
	outputFile = None
	asList = False
	showKeys = False
	argList = list()
	
	def usage():
		"""docstring for usage"""
		print ("--")
		print ("manipulate the db") 
		print
		print ("\t-h, --helpL print this usage")
		print ("\t-i: load inputfile")
		print ("\t-I: load inputFolder")
		print ("\t-o: merge the inputfiles and save them to another db")
		print ("\t-s: show the valid attributes")
		print ("\t-w: merge the inputfiles and make them as csv files")
		print ("\t-a: the column names for the csv files (only valid with -w arg)")

	try:
		opts, args = getopt.getopt(argv, "hi:I:o:wa:s", ["help"])
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
		elif opt in ("-I"):
			inputDir = arg
		elif opt in ("-o"):
			outputFile = arg
		elif opt in ("-s"):
			showKeys = True
		elif opt in ("-w"):
			asList = True
		elif opt in ("-a"):
			argList.append(arg)

	db = LiteDB()
	if inputFile is not None and os.path.exists(inputFile):
		db.load(inputFile)
	
	if inputDir is not None and os.path.exists(inputDir):
		pattern = re.compile(r".*\.db$")
		filelist = filter(lambda x: pattern.match(x) is not None, os.listdir(inputDir))
		for f in filelist:
			print (f)
			db.load(os.path.join(inputDir, f))

	if showKeys:
		print ("keys ----")
		print ("\n".join(db.keys()))
		print 
		print ("attribute keys ---")
		print (" ".join(list(db.showkeys())))

	if outputFile is not None:
		if asList:
			db.tolist(outputFile, *argList)
		else:
			db.save(outputFile)

if __name__ == "__main__":
	main(sys.argv[1:])
