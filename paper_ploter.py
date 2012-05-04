# Jing-Kai Lou (kaeaura@gamil.com)

import os
import sys
sys.path.append('analyzer')
import matplotlib.pylab as plt
from db import LiteDB


def load_data(path, file_dict):
	all_dbs = os.listdir(path)
	assert(set(all_filenames.values()).issubset(set(all_dbs)))
	db = LiteDB()
	all_keynames = {}
	read_keynames = set()
	for read_tracename, read_filename in all_filenames.iteritems():
		db.load(os.path.join(path, read_filename))
		read_keyname = set(db.keys()).difference(read_keynames).pop()
		all_keynames.__setitem__(read_tracename, read_keyname)
		read_keynames.add(read_keyname)
	return(db, all_keynames)

def plot_frac(db, keynames, save_path):
	inFrac_name = 'inFrac_dict'
	outFrac_name = 'outFrac_dict'

	plt.clf()
	plt.figure(figsize = (8, 5))
	x_upperbound = .2

	plt.subplot(2, 2, 1)
	plt.plot(map(lambda x: x / 1000.0, db[keynames['mog']][inFrac_name].keys()), db[keynames['mog']][inFrac_name].values(), 'b-', lw = 5, label = 'fairyland')
	plt.plot(map(lambda x: x / 1000.0, db[keynames['mblg']][inFrac_name].keys()), db[keynames['mblg']][inFrac_name].values(), 'r:', lw = 5, label = 'twitter')
	plt.plot(map(lambda x: x / 1000.0, db[keynames['im']][inFrac_name].keys()), db[keynames['im']][inFrac_name].values(), 'k--', lw = 5, label = 'yahoo')
	plt.xlim(xmax = x_upperbound)
	plt.ylabel('wcc fraction (id)')
	plt.title('interaction')
	plt.grid(True)
	plt.legend(('fairyland', 'twitter', 'yahoo'), loc = 'best', prop = {'size':10})

	plt.subplot(2, 2, 2)
	plt.plot(map(lambda x: x / 1000.0, db[keynames['mogF']][inFrac_name].keys()), db[keynames['mogF']][inFrac_name].values(), 'b-', lw = 5, label = 'fairyland')
	plt.plot(map(lambda x: x / 1000.0, db[keynames['mblgF']][inFrac_name].keys()), db[keynames['mblgF']][inFrac_name].values(), 'r:', lw = 5, label = 'twitter')
	plt.plot(map(lambda x: x / 1000.0, db[keynames['imF']][inFrac_name].keys()), db[keynames['imF']][inFrac_name].values(), 'k--', lw = 5, label = 'yahoo')
	plt.xlim(xmax = x_upperbound)
	plt.title('ally')
	plt.grid(True)
	#plt.legend(('fairyland', 'twitter', 'yahoo'), loc = 'best')

	plt.subplot(2, 2, 3)
	plt.plot(map(lambda x: x / 1000.0, db[keynames['mog']][outFrac_name].keys()), db[keynames['mog']][outFrac_name].values(), 'b-', lw = 5, label = 'fairyland')
	plt.plot(map(lambda x: x / 1000.0, db[keynames['mblg']][outFrac_name].keys()), db[keynames['mblg']][outFrac_name].values(), 'r:', lw = 5, label = 'twitter')
	plt.plot(map(lambda x: x / 1000.0, db[keynames['im']][outFrac_name].keys()), db[keynames['im']][outFrac_name].values(), 'k--', lw = 5, label = 'yahoo')
	plt.xlim(xmax = x_upperbound)
	plt.xlabel('removed fraction by od (%)')
	plt.ylabel('wc fraction (od)')
	plt.grid(True)

	plt.subplot(2, 2, 4)
	plt.plot(map(lambda x: x / 1000.0, db[keynames['mogF']][outFrac_name].keys()), db[keynames['mogF']][outFrac_name].values(), 'b-', lw = 5, label = 'fairyland')
	plt.plot(map(lambda x: x / 1000.0, db[keynames['mblgF']][outFrac_name].keys()), db[keynames['mblgF']][outFrac_name].values(), 'r:', lw = 5, label = 'twitter')
	plt.plot(map(lambda x: x / 1000.0, db[keynames['imF']][outFrac_name].keys()), db[keynames['imF']][outFrac_name].values(), 'k--', lw = 5, label = 'yahoo')
	plt.xlim(xmax = x_upperbound)
	plt.xlabel('removed fraction (%)')
	plt.grid(True)

	plt.savefig(os.path.join(save_dir, save_path))

def plot_degreeRate(db, keynames, save_path):
	degRate_x_name = 'degRateDistr_x'
	degRate_y_name = 'degRateDistr_y'

	plt.clf()
	plt.figure(figsize = (8, 5))

	plt.subplot(1, 2, 1)
	plt.plot(db[keynames['mog']][degRate_x_name], db[keynames['mog']][degRate_y_name], 'b-', lw=5, label = 'fairyland')
	plt.plot(db[keynames['mblg']][degRate_x_name], db[keynames['mblg']][degRate_y_name], 'r:', lw=5, label = 'twitter')
	plt.plot(db[keynames['im']][degRate_x_name], db[keynames['im']][degRate_y_name], 'k--', lw=5, label = 'yahoo')
	plt.xscale('log')
	plt.grid(True)
	plt.title('interaction')
	plt.legend(('fairyland', 'twitter', 'yahoo'), loc = 4, prop = {'size': 10})
	plt.xlabel('In-degree to Out-degree Ratio')
	plt.ylabel('CDF')

	plt.subplot(1, 2, 2)
	plt.plot(db[keynames['mogF']][degRate_x_name], db[keynames['mogF']][degRate_y_name], 'b-', lw=5, label = 'fairyland')
	plt.plot(db[keynames['mblgF']][degRate_x_name], db[keynames['mblgF']][degRate_y_name], 'r:', lw=5, label = 'twitter')
	#plt.plot(db[keynames['imF']][degRate_x_name], db[keynames['imF']][degRate_y_name], 'k--', lw=5, label = 'yahoo')
	plt.xscale('log')
	plt.grid(True)
	plt.title('ally')
	plt.xlabel('In-degree to Out-degree Ratio')
	plt.ylabel('CDF')

	plt.savefig(os.path.join(save_dir, save_path))

def plot_degreeOverlap(db, keynames, save_path, attr_name = 'degOverlapRatio'):
	plt.clf()
	plt.figure(figsize = (8, 5))

	x = sorted(db[keynames['mog']][attr_name].keys())
	y = [db[keynames['mog']][attr_name][xx] for xx in x]
	plt.plot(x, y, 'b-', lw = 5, label = 'fairyland interaction')

	x = sorted(db[keynames['mblg']][attr_name].keys())
	y = [db[keynames['mblg']][attr_name][xx] for xx in x]
	plt.plot(x, y, 'r:', lw = 5, label = 'twitter interaction')

	x = sorted(db[keynames['im']][attr_name].keys())
	y = [db[keynames['im']][attr_name][xx] for xx in x]
	plt.plot(x, y, 'k--', lw = 5, label = 'yahoo interaction')

	x = sorted(db[keynames['mogF']][attr_name].keys())
	y = [db[keynames['mogF']][attr_name][xx] for xx in x]
	plt.plot(x, y, 'b.', label = 'fairyland ally')

	x = sorted(db[keynames['mblgF']][attr_name].keys())
	y = [db[keynames['mblgF']][attr_name][xx] for xx in x]
	plt.plot(x, y, 'k*', label = 'twitter ally')

	plt.grid(True)
	plt.title('Overlap')
	plt.xlabel('Fraction of Users ordered by degree (%)')
	plt.ylabel('Overlap (%)')
	plt.legend(('fairyland interaction', 'twitter interaction', 'yahoo interaction', 'fairyland ally', 'twitter ally'), loc = 'best')

	plt.savefig(os.path.join(save_dir, save_path))

def plot_degreeDistr(db, keynames, save_path):
	indeg_x_name = 'inDegDistr_x'
	indeg_y_name = 'inDegDistr_y'
	outdeg_x_name = 'outDegDistr_x'
	outdeg_y_name = 'outDegDistr_y'
	deg_x_name = 'degDistr_x'
	deg_y_name = 'degDistr_y'

	x_upperbound = 10 ** 5
	y_lowerbound = 10 ** -6

	plt.clf()
	plt.figure(figsize = (8, 5))
	plt.subplot(2, 3, 1)
	plt.loglog(db[keynames['mog']][indeg_x_name], db[keynames['mog']][indeg_y_name], 'b-', linewidth=5, label='id')
	plt.loglog(db[keynames['mog']][outdeg_x_name], db[keynames['mog']][outdeg_y_name], 'r--', linewidth=5, label='od')
	#plt.loglog(db[keynames['mogF']][indeg_x_name], db[keynames['mogF']][indeg_y_name], 'r--', linewidth=5, label='ally')
	plt.ylabel('interaction CCDF')
	plt.grid(True)
	plt.xlim(xmax = x_upperbound)
	plt.ylim(ymin = y_lowerbound)
	plt.title('Fairyland Online')
	plt.legend(('id', 'od'), loc = 3, prop = {'size': 7})

	plt.subplot(2, 3, 2)
	plt.loglog(db[keynames['mblg']][indeg_x_name], db[keynames['mblg']][indeg_y_name], 'b-', linewidth=5, label='id')
	plt.loglog(db[keynames['mblg']][outdeg_x_name], db[keynames['mblg']][outdeg_y_name], 'r--', linewidth=5, label='od')
	#plt.loglog(db[keynames['mblgF']][indeg_x_name], db[keynames['mblgF']][indeg_y_name], 'r--', linewidth=5, label='ally')
	plt.grid(True)
	plt.xlim(xmax = x_upperbound)
	plt.ylim(ymin = y_lowerbound)
	plt.title('Twitter')

	plt.subplot(2, 3, 3)
	plt.loglog(db[keynames['im']][indeg_x_name], db[keynames['im']][indeg_y_name], 'b-', linewidth=5, label='id')
	plt.loglog(db[keynames['im']][outdeg_x_name], db[keynames['im']][outdeg_y_name], 'r--', linewidth=5, label='od')
	#plt.loglog(db[keynames['imF']][indeg_x_name], db[keynames['imF']][indeg_y_name], 'r--', linewidth=5, label='ally')
	plt.xlabel('k')
	plt.grid(True)
	plt.xlim(xmax = x_upperbound)
	plt.ylim(ymin = y_lowerbound)
	plt.title('Yahoo! Messenger')

	plt.subplot(2, 3, 4)
	plt.loglog(db[keynames['mogF']][indeg_x_name], db[keynames['mogF']][indeg_y_name], 'b-', linewidth=5, label='id')
	plt.loglog(db[keynames['mogF']][outdeg_x_name], db[keynames['mogF']][outdeg_y_name], 'r--', linewidth=5, label='od')
	#plt.loglog(db[keynames['mogF']][outdeg_x_name], db[keynames['mogF']][outdeg_y_name], 'r--', linewidth=5, label='ally')
	plt.xlabel('k')
	plt.ylabel('ally CCDF')
	plt.grid(True)
	plt.xlim(xmax = x_upperbound)
	plt.ylim(ymin = y_lowerbound)

	plt.subplot(2, 3, 5)
	plt.loglog(db[keynames['mblgF']][indeg_x_name], db[keynames['mblgF']][indeg_y_name], 'b-', linewidth=5, label='id')
	plt.loglog(db[keynames['mblgF']][outdeg_x_name], db[keynames['mblgF']][outdeg_y_name], 'r--', linewidth=5, label='od')
	#plt.loglog(db[keynames['mblgF']][outdeg_x_name], db[keynames['mblgF']][outdeg_y_name], 'r--', linewidth=5, label='ally')
	plt.xlabel('k')
	plt.grid(True)
	plt.xlim(xmax = x_upperbound)
	plt.ylim(ymin = y_lowerbound)

	plt.subplot(2, 3, 6)
	plt.loglog(db[keynames['imF']][deg_x_name], db[keynames['imF']][deg_y_name], 'k-', linewidth=5, label='d')
	#plt.loglog(db[keynames['imF']][indeg_x_name], db[keynames['imF']][indeg_y_name], 'b-', linewidth=5, label='id')
	#plt.loglog(db[keynames['imF']][outdeg_x_name], db[keynames['imF']][outdeg_y_name], 'r--', linewidth=5, label='od')
	#plt.loglog(db[keynames['imF']][outdeg_x_name], db[keynames['imF']][outdeg_y_name], 'r--', linewidth=5, label='ally')
	plt.xlabel('k')
	plt.grid(True)
	plt.xlim(xmax = x_upperbound)
	plt.ylim(ymin = y_lowerbound)
	plt.legend(('d'), loc = 'best', prop = {'size':7})

	plt.savefig(os.path.join(save_dir, save_path))

def plot_reusage(db, keynames, save_path, attr_name = [ 'linkWeightDistr_x', 'linkWeightDistr_y' ]):
	plt.clf()
	plt.figure(figsize = (8, 5))
	plt.loglog(db[keynames['mog']][attr_name[0]], db[keynames['mog']][attr_name[1]], 'b-', lw = 5, label = 'fariyland')
	plt.loglog(db[keynames['mblg']][attr_name[0]], db[keynames['mblg']][attr_name[1]], 'r:', lw = 5, label = 'twitter')
	plt.loglog(db[keynames['im']][attr_name[0]], db[keynames['im']][attr_name[1]], 'k--', lw = 5, label = 'yahoo')
	plt.xlabel('Usage (days)')
	plt.ylabel('CCDF')
	plt.title('Usage of Links')
	plt.grid(True)
	plt.legend(('fairyland', 'twitter', 'yahoo'), loc = 'best')

	plt.savefig(os.path.join(save_dir, save_path))

# knn via degree bin ####
def plot_KnnDistr(db, keynames, save_path):
	knnMean_x_name = 'knnDistr_avg_x'
	knnMean_y_name = 'knnDistr_avg_y'
	knnMedian_x_name = 'knnDistr_median_x'
	knnMedian_y_name = 'knnDistr_median_y'

	inKnnMean_x_name = 'inKnnDistr_avg_x'
	inKnnMean_y_name = 'inKnnDistr_avg_y'
	inKnnMedian_x_name = 'inKnnDistr_median_x'
	inKnnMedian_y_name = 'inKnnDistr_median_y'

	outKnnMean_x_name = 'outKnnDistr_avg_x'
	outKnnMean_y_name = 'outKnnDistr_avg_y'
	outKnnMedian_x_name = 'outKnnDistr_median_x'
	outKnnMedian_y_name = 'outKnnDistr_median_y'

	x_upperbound = 10 ** 5
	x_lowerbound = 10 ** 0
	y_upperbound = 10 ** 4
	y_lowerbound = 10 ** -1

	plt.clf()
	plt.figure(figsize = (8, 8))

	plt.subplot(2, 2, 1)
	plt.loglog(db[keynames['mog']][inKnnMean_x_name], db[keynames['mog']][inKnnMean_y_name], 'b.', mec='b', ms=5, label='fairyland')
	plt.loglog(db[keynames['mblg']][inKnnMean_x_name], db[keynames['mblg']][inKnnMean_y_name], 'r+', mec='r', mfc='None', ms=5, label='twitter')
	plt.loglog(db[keynames['im']][inKnnMean_x_name], db[keynames['im']][inKnnMean_y_name], 'k>', mec='k', mfc='None', ms=5, label='yahoo')
	plt.xlim((x_lowerbound, x_upperbound))
	plt.ylim((y_lowerbound, y_upperbound))
	plt.title('interaction')
	plt.ylabel('$<k_{nn}>^{in}$')
	plt.grid(True)
	plt.legend(('fairyland', 'twitter', 'yahoo'), loc = 'best', prop = {'size': 10})

	plt.subplot(2, 2, 2)
	plt.loglog(db[keynames['mogF']][inKnnMean_x_name], db[keynames['mogF']][inKnnMean_y_name], 'b.', mec='b', ms=5, label='fairyland')
	plt.loglog(db[keynames['mblgF']][inKnnMean_x_name], db[keynames['mblgF']][inKnnMean_y_name], 'r+', mec='r', mfc='None', ms=5, label='twitter')
	plt.loglog(db[keynames['imF']][knnMean_x_name], db[keynames['imF']][knnMean_y_name], 'k>', mec='k', mfc='None', ms=5, label='yahoo')
	plt.xlim((x_lowerbound, x_upperbound))
	plt.ylim((y_lowerbound, y_upperbound))
	plt.title('ally')
	plt.grid(True)

	plt.subplot(2, 2, 3)
	plt.loglog(db[keynames['mog']][outKnnMean_x_name], db[keynames['mog']][outKnnMean_y_name], 'b.', mec='b', ms=5, label='fairyland')
	plt.loglog(db[keynames['mblg']][outKnnMean_x_name], db[keynames['mblg']][outKnnMean_y_name], 'r+', mec='r', mfc='None', ms=5, label='twitter')
	plt.loglog(db[keynames['im']][outKnnMean_x_name], db[keynames['im']][outKnnMean_y_name], 'k>', mec='k', mfc='None', ms=5, label='yahoo')
	plt.xlim((x_lowerbound, x_upperbound))
	plt.ylim((y_lowerbound, y_upperbound))
	plt.title('interaction')
	plt.xlabel('$k$')
	plt.ylabel('$<k_{nn}>^{out}$')
	plt.grid(True)

	plt.subplot(2, 2, 4)
	plt.loglog(db[keynames['mogF']][outKnnMean_x_name], db[keynames['mogF']][outKnnMean_y_name], 'b.', mec='b', ms=5, label='fairyland')
	#plt.loglog(db[keynames['mogF']][outKnnMedian_x_name], db[keynames['mogF']][outKnnMedian_y_name], 'g--', label='fairyland-median')
	plt.loglog(db[keynames['mblgF']][outKnnMean_x_name], db[keynames['mblgF']][outKnnMean_y_name], 'r+', mec='r', mfc='None', ms=5, label='twitter')
	#plt.loglog(db[keynames['mblgF']][outKnnMedian_x_name], db[keynames['mblgF']][outKnnMedian_y_name], 'y--', label='twitter-median')
	plt.loglog(db[keynames['imF']][knnMean_x_name], db[keynames['imF']][knnMean_y_name], 'k>', mec='k', mfc='None', ms=5, label='yahoo')
	#plt.loglog(db[keynames['imF']][knnMedian_x_name], db[keynames['imF']][knnMedian_y_name], 'c--', ms=5, label='yahoo')
	plt.xlim((x_lowerbound, x_upperbound))
	plt.ylim((y_lowerbound, y_upperbound))
	plt.title('ally')
	plt.xlabel('$k$')
	plt.grid(True)
	plt.savefig(os.path.join(save_dir, save_path))

# clustering ####
def plot_clustDistr(db, keynames, save_path):
	cluMean_x_name = 'ccDistr_avg_x'
	cluMean_y_name = 'ccDistr_avg_y'
	cluMedian_x_name = 'ccDistr_median_x'
	cluMedian_y_name = 'ccDistr_median_y'

	x_upperbound = 10 ** 4
	y_upperbound = .4
	y_lowerbound = 10 ** -5

	plt.clf()
	plt.figure(figsize = (8, 5))

	plt.subplot(1, 2, 1)
	plt.loglog(db[keynames['mog']][cluMean_x_name], db[keynames['mog']][cluMean_y_name], 'b.', mec='b', ms=5, label='fairyland')
	plt.loglog(db[keynames['mblg']][cluMean_x_name], db[keynames['mblg']][cluMean_y_name], 'r+', mec='r', mfc='None', ms=5, label='twitter')
	plt.loglog(db[keynames['im']][cluMean_x_name], db[keynames['im']][cluMean_y_name], 'k>', mec='k', mfc='None', ms=5, label='yahoo')
	plt.title('interaction')
	plt.xlabel('$k$')
	plt.ylabel('cc')
	plt.grid(True)
	plt.legend(('fairyland', 'twitter', 'yahoo'), loc = 'best', prop = {'size': 10})
	plt.xlim(xmax = x_upperbound)
	plt.ylim(ymax = y_upperbound, ymin = y_lowerbound)

	plt.subplot(1, 2, 2)
	plt.loglog(db[keynames['mogF']][cluMean_x_name], db[keynames['mogF']][cluMean_y_name], 'b.', mec='b', ms=5, label='fairyland')
	plt.loglog(db[keynames['mblgF']][cluMean_x_name], db[keynames['mblgF']][cluMean_y_name], 'r+', mec='r', mfc='None', ms=5, label='twitter')
	plt.loglog(db[keynames['imF']][cluMean_x_name], db[keynames['imF']][cluMean_y_name], 'k>', mec='k', mfc='None', ms=5, label='yahoo')
	plt.title('ally')
	plt.xlabel('$k$')
	plt.grid(True)
	plt.xlim(xmax = x_upperbound)
	plt.ylim(ymax = y_upperbound, ymin = y_lowerbound)

	plt.savefig(os.path.join(save_dir, save_path))

def plot_dist(db, keynames, save_path):
	"""plot the sample path distance (in number of hops)"""
	diam_name = 'diameter'
	dist_name = 'hop_counts'

	plt.clf()
	plt.figure(figsize = (8, 5))

	plt.subplot(1, 2, 1)
	x = db[keynames['mog']][dist_name].keys()
	y = db[keynames['mog']][dist_name].values()
	ySum = float(sum(y))
	y = map(lambda z: z / ySum, y)
	plt.plot(x, y, 'b-', lw = 3, label = 'fairyland')

	x = db[keynames['mblg']][dist_name].keys()
	y = db[keynames['mblg']][dist_name].values()
	ySum = float(sum(y))
	y = map(lambda z: z / ySum, y)
	plt.plot(x, y, 'r:', lw = 3, label = 'twitter')

	x = db[keynames['im']][dist_name].keys()
	y = db[keynames['im']][dist_name].values()
	ySum = float(sum(y))
	y = map(lambda z: z / ySum, y)
	plt.plot(x, y, 'k--', lw = 3, label = 'yahoo')

	plt.title('interaction')
	plt.grid(True)
	plt.xlabel('hop number')
	plt.ylabel('probability')
	plt.legend(('fairyland', 'twitter', 'yahoo'), loc = 'best')
	plt.xlim((0, 15))
	plt.ylim((0, .7))

	plt.subplot(1, 2, 2)

	x = db[keynames['mogF']][dist_name].keys()
	y = db[keynames['mogF']][dist_name].values()
	ySum = float(sum(y))
	y = map(lambda z: z / ySum, y)
	plt.plot(x, y, 'b-', lw = 3, label = 'fairyland')

	plt.title('ally')
	plt.grid(True)
	plt.xlabel('hop number')
	plt.legend(('fairyland', 'twitter', 'yahoo'), loc = 'best')
	plt.xlim((0, 15))
	plt.ylim((0, .7))

	plt.savefig(os.path.join(save_dir, save_path))

def plot_prefAttach(db, keynames, save_path):
	"""docstring for plot_pref"""
	pa_name = 'pref_attach'
	import numpy as np
	from scipy.optimize import leastsq
	degree = 2
	observation_length = 200
	fit_length = 200

	plt.clf()
	plt.figure(figsize = (9, 7))
	y_upperbound = 4 * 10 ** 6
	y_lowerbound = 0
	x_upperbound = observation_length
	mSize = 5
	
	x = sorted(db[keynames['mog']][pa_name].keys())
	y = []
	for k in x:
		y.append(db[keynames['mog']][pa_name][k])
	if len(x) >= observation_length:
		x = x[:observation_length]
		y = y[:observation_length]
	A = np.vander(x[:fit_length], degree + 1)
	coef, residual, rank, sing_vals = np.linalg.lstsq(A, y[:fit_length])
	f = np.poly1d(coef)
	y_est = f(x)
	plt.plot(x, y, 'b.', label = 'fairyland', ms = mSize)
	plt.plot(x, y_est, 'b-', lw = 2, label = 'fairyland-fitness')

	x = sorted(db[keynames['mblg']][pa_name].keys())
	y = []
	for k in x:
		y.append(db[keynames['mblg']][pa_name][k])
	if len(x) >= observation_length:
		x = x[:observation_length]
		y = y[:observation_length]
	A = np.vander(x[:fit_length], degree + 1)
	coef, residual, rank, sing_vals = np.linalg.lstsq(A, y[:fit_length])
	f = np.poly1d(coef)
	y_est = f(x)
	plt.plot(x, y, 'r+', label = 'twitter', ms = mSize)
	plt.plot(x, y_est, 'r-', lw = 2, label = 'twitter-fitness')

	x = sorted(db[keynames['im']][pa_name].keys())
	y = []
	for k in x:
		y.append(db[keynames['im']][pa_name][k])
	if len(x) >= observation_length:
		x = x[:observation_length]
		y = y[:observation_length]
	A = np.vander(x[:fit_length], degree + 1)
	coef, residual, rank, sing_vals = np.linalg.lstsq(A, y[:fit_length])
	f = np.poly1d(coef)
	y_est = f(x)
	plt.plot(x, y, 'k>', mfc='None', mec='k', label = 'yahoo', ms = mSize)
	plt.plot(x, y_est, 'k--', lw = 2, label = 'yahoo-fitness')

	plt.xlim(xmax = x_upperbound)
	plt.ylim(ymax = y_upperbound, ymin = y_lowerbound)
	#plt.grid(True)
	plt.xlabel('k')
	plt.ylabel('$R_k$')
	plt.legend(('fairyland', 'fairyland-fitness', 'twitter', 'twitter-fitness', 'yahoo', 'yahoo-fitness'), loc = 2, ncol = 2, prop = {'size': 12})

	plt.savefig(os.path.join(save_dir, save_path))

def plot_clustProb(db, keynames, save_path, attr_name = 'cluster_prob'):
	"""docstring for plot_pref"""
	import numpy as np
	degree = 2
	observation_length = 200
	fit_length = 200

	plt.clf()
	plt.figure(figsize = (9, 7))
	y_upperbound = 4 * 10 ** 8
	y_lowerbound = 0
	x_upperbound = observation_length
	mSize = 5
	
	x = sorted(db[keynames['mog']][attr_name].keys())
	y = []
	for k in x:
		y.append(db[keynames['mog']][attr_name][k])
	if len(x) >= observation_length:
		x = x[:observation_length]
		y = y[:observation_length]
	A = np.vander(x[:fit_length], degree + 1)
	coef, residual, rank, sing_vals = np.linalg.lstsq(A, y[:fit_length])
	f = np.poly1d(coef)
	y_est = f(x)
	plt.plot(x, y, 'b.', label = 'fairyland', ms = mSize)
	plt.plot(x, y_est, 'b-', lw = 2, label = 'fairyland-fitness')

	x = sorted(db[keynames['mblg']][attr_name].keys())
	y = []
	for k in x:
		y.append(db[keynames['mblg']][attr_name][k])
	if len(x) >= observation_length:
		x = x[:observation_length]
		y = y[:observation_length]
	A = np.vander(x[:fit_length], degree + 1)
	coef, residual, rank, sing_vals = np.linalg.lstsq(A, y[:fit_length])
	f = np.poly1d(coef)
	y_est = f(x)
	plt.plot(x, y, 'r+', label = 'twitter', ms = mSize)
	plt.plot(x, y_est, 'r-', lw = 2, label = 'twitter-fitness')

	x = sorted(db[keynames['im']][attr_name].keys())
	y = []
	for k in x:
		y.append(db[keynames['im']][attr_name][k])
	if len(x) >= observation_length:
		x = x[:observation_length]
		y = y[:observation_length]
	A = np.vander(x[:fit_length], degree + 1)
	coef, residual, rank, sing_vals = np.linalg.lstsq(A, y[:fit_length])
	f = np.poly1d(coef)
	y_est = f(x)
	plt.plot(x, y, 'k>', mfc='None', mec='k', label = 'yahoo', ms = mSize)
	plt.plot(x, y_est, 'k--', lw = 2, label = 'yahoo-fitness')

	plt.xlim(xmax = x_upperbound)
	plt.ylim(ymax = y_upperbound, ymin = y_lowerbound)
	#plt.grid(True)
	plt.xlabel('k')
	plt.ylabel('$R_k$')
	plt.legend(('fairyland', 'fairyland-fitness', 'twitter', 'twitter-fitness', 'yahoo', 'yahoo-fitness'), loc = 1, ncol = 2, prop = {'size': 12})

	plt.savefig(os.path.join(save_dir, save_path))

def plot_Knn(db, keynames, save_path, attr_names = ('knn', 'weighted_knn')):
	plt.clf()
	plt.figure(figsize = (8, 5))
	mSize = 7

	x_upperbound = 10 ** 4
	y_upperbound = 10 ** 4
	y_lowerbound = 10 ** 0

	plt.subplot(1, 2, 1)
	x = sorted(db[keynames['mog']][attr_names[0]].keys())
	y = [db[keynames['mog']][attr_names[0]][k] for k in x]
	plt.loglog(x, y, 'b.', mec = 'b', label = 'fairyland', ms = mSize)

	x = sorted(db[keynames['mblg']][attr_names[0]].keys())
	y = [db[keynames['mblg']][attr_names[0]][k] for k in x]
	plt.loglog(x, y, 'r+', label = 'twitter', ms = mSize)

	x = sorted(db[keynames['im']][attr_names[0]].keys())
	y = [db[keynames['im']][attr_names[0]][k] for k in x]
	plt.loglog(x, y, 'k>', mfc='None', label = 'yahoo', ms = mSize)
	#plt.yscale('log')
	plt.legend(('fairyland', 'twitter', 'yahoo'), loc = 'best')

	plt.title('interaction')
	plt.xlabel('$k$')
	plt.ylabel('$K_{nn}$')
	plt.xlim(xmax = x_upperbound)
	plt.ylim(ymax = y_upperbound, ymin = y_lowerbound)
	plt.grid(True)

	plt.subplot(1, 2, 2)
	x = sorted(db[keynames['mogF']][attr_names[0]].keys())
	y = [db[keynames['mogF']][attr_names[0]][k] for k in x]
	plt.loglog(x, y, 'b.', mec = 'b', label = 'fairyland', ms = mSize)

	x = sorted(db[keynames['mblgF']][attr_names[0]].keys())
	y = [db[keynames['mblgF']][attr_names[0]][k] for k in x]
	plt.loglog(x, y, 'r+', label = 'twitter', ms = mSize)

	x = sorted(db[keynames['imF']][attr_names[0]].keys())
	y = [db[keynames['imF']][attr_names[0]][k] for k in x]
	plt.loglog(x, y, 'k>', mfc='None', label = 'yahoo', ms = mSize)

	plt.title('ally')
	#plt.yscale('log')
	plt.xlabel('$k$')
	plt.xlim(xmax = x_upperbound)
	plt.ylim(ymax = y_upperbound, ymin = y_lowerbound)
	plt.grid(True)

	plt.savefig(os.path.join(save_dir, save_path))

def plot_closureProb(db, keynames, save_path, attr_name):
	plt.clf()
	plt.figure(figsize = (9, 7))
	mSize = 7
	
	x = sorted(db[keynames['mog']][attr_name].keys())
	y = []
	for k in x:
		y.append(db[keynames['mog']][attr_name][k])
	ySum = float(sum(y))
	y = map(lambda z: z / ySum, y)
	plt.plot(x, y, 'bo-', label = 'fairyland', ms = mSize)

	x = sorted(db[keynames['mblg']][attr_name].keys())
	y = []
	for k in x:
		y.append(db[keynames['mblg']][attr_name][k])
	ySum = float(sum(y))
	y = map(lambda z: z / ySum, y)
	plt.plot(x, y, 'r+:', label = 'twitter', ms = mSize)

	x = sorted(db[keynames['im']][attr_name].keys())
	y = []
	for k in x:
		y.append(db[keynames['im']][attr_name][k])
	ySum = float(sum(y))
	y = map(lambda z: z / ySum, y)
	plt.plot(x, y, 'k>--', mfc='None', mec='k', label = 'yahoo', ms = mSize)

	plt.grid(True)
	plt.xlim(xmax = 15)
	plt.xlabel('hop count $d$')
	plt.ylabel('$P(d)$')
	plt.legend(('fairyland', 'twitter', 'yahoo'), loc = 1)

	plt.savefig(os.path.join(save_dir, save_path))

# loading and plot ##########
flag = [1]
save_dir = 'doc/interactions_over_platforms/figures'
print (flag)

if 1 in flag:
	db_path = '../exp/db/degree'
	all_filenames = {'mog':'anderson_chat_degree.db', 'mogF': 'anderson_friend_degree.db', 'mblg':'twitter_cut_degree.db', 'mblgF':'twitter_follower_degree.db', 'im': 'yahoo_chat_degree.db', 'imF':'yahoo_friend_degree.db'}
	db, all_keynames = load_data(db_path, all_filenames)
	plot_degreeRate(db, all_keynames, 'degree_rate_distribution.pdf')
	plot_degreeOverlap(db, all_keynames, 'degree_overlap.pdf')
	plot_reusage(db, all_keynames, save_path = 'link_reusage.pdf')
	plot_degreeDistr(db, all_keynames, 'degree_distribution.pdf')

if 2 in flag:
	db_path = '../exp/db/focus'
	all_filenames = {'mog':'anderson_chat.db', 'mogF': 'anderson_friend.db', 'mblg':'twitter_cut.db', 'mblgF':'twitter_follower.db', 'im': 'yahoo_chat.db', 'imF':'yahoo_friend.db'}
	db, all_keynames = load_data(db_path, all_filenames)
	#plot_degreeDistr(db, all_keynames, 'degree_distribution.pdf')
	#plot_KnnDistr(db, all_keynames, 'knn_distribution.pdf')
	plot_clustDistr(db, all_keynames, 'clust_distribution.pdf')

if 3 in flag:
	db_path = '../exp/db/knn'
	all_filenames = {'mog':'anderson_chat_knn.db', 'mogF': 'anderson_friend_knn.db', 'mblg':'twitter_cut_knn.db', 'mblgF':'twitter_follower_knn.db', 'im': 'yahoo_chat_knn.db', 'imF':'yahoo_friend_knn.db'}
	db, all_keynames = load_data(db_path, all_filenames)
	plot_Knn(db, all_keynames, save_path = 'knn_distribution.pdf')

if 4 in flag:
	db_path = '../exp/db/frac'
	all_filenames = {'mog':'anderson_chat_frac.db', 'mogF': 'anderson_friend_frac.db', 'mblg':'twitter_cut_frac.db', 'mblgF':'twitter_follower_frac.db', 'im': 'yahoo_chat_frac.db', 'imF': 'yahoo_friend_frac.db'}
	db, all_keynames = load_data(db_path, all_filenames)
	plot_frac(db, all_keynames, 'frac.pdf')

if 5 in flag:
	db_path = '../exp/db/dist'
	all_filenames = {'mog':'anderson_chat_dist.db', 'mogF': 'anderson_friend_dist.db', 'mblg':'twitter_cut_dist.db', 'im': 'yahoo_chat_dist.db'}
	db, all_keynames = load_data(db_path, all_filenames)
	plot_dist(db, all_keynames, 'dist.pdf')

if 6 in flag:
	db_path = '../exp/db/pa'
	all_filenames = {'mog': 'anderson_chat_pa.db', 'mblg':'twitter_chat_pa.db', 'im': 'yahoo_chat_pa.db'}
	db, all_keynames = load_data(db_path, all_filenames)
	plot_prefAttach(db, all_keynames, 'pref_attachment_rp.pdf')

	db_path = '../exp/db/cr'
	all_filenames = {'mog': 'anderson_chat_cr.db', 'mblg':'twitter_chat_cr.db', 'im': 'yahoo_chat_cr.db'}
	db, all_keynames = load_data(db_path, all_filenames)
	plot_clustProb(db, all_keynames, 'clust_rp.pdf') 

	db_path = '../exp/db/cd'
	all_filenames = {'mog': 'anderson_chat_cd.db', 'mblg':'twitter_chat_cd.db', 'im': 'yahoo_chat_cd.db'}
	db, all_keynames = load_data(db_path, all_filenames)
	plot_closureProb(db, all_keynames, 'closure_dist.pdf', attr_name = 'closure_dist') 

