# Jing-Kai Lou (kaeaura@gamil.com)
# test the power-law the degree sequence
# write back the result into doc/interactions_over_platforms/tables
import plfit
import numpy as np
import networkx as nx
from collections import OrderedDict
from pylab import *
import os
import re

def scan(filename):
	import csv
	dataReader = csv.reader(open(filename, 'r'))
	data = [map(int, l) for l in dataReader]
	return([item for sublist in data for item in sublist])

def write_table(filename, dds):
	import csv
	dds_fields = dds[0].keys()
	with open(filename, 'wb') as F:
		dr = csv.DictWriter(F, fieldnames = dds_fields)
		dr.writeheader()
		for d in dds:
			dr.writerow(d)

source_dir = 'doc/interactions_over_platforms/tables/deg_seq'
figure_dir = 'doc/interactions_over_platforms/figures/deg_seq_fitness'
if not os.path.exists(figure_dir):
	os.makedirs(figure_dir)
degSeq_files = os.listdir(source_dir)
degFits = list()

for degSeq_file in degSeq_files:
	if not os.path.isdir(degSeq_file):
		readFile = os.path.join(source_dir, degSeq_file)
		dataset, trace_type, direction = re.sub(r'\.csv$', '', degSeq_file).split('_')
		d = scan(readFile)
		dd = np.array(filter(lambda x: x > 0, d))
		p = plfit.plfit(np.array(dd, dtype = 'float64'), usefortran = False, discrete = True)
		# tested values collected
		pdata = OrderedDict()
		pdata['dataset'] = dataset
		pdata['type'] = trace_type
		pdata['dir'] = direction
		pdata['xmin'] = p._xmin
		pdata['alpha'] = p._alpha
		pdata['D'] = p._ks
		#pdata['ksP'] = p._ks_prob
		degFits.append(pdata)
		# diagnosis plots
		clf()
		p.xminvsks()
		savefig(os.path.join(figure_dir, "%s_%s_%s_kstest.pdf" % (dataset, trace_type, direction)))
		clf()
		p.plotcdf()
		savefig(os.path.join(figure_dir, "%s_%s_%s_cdf.pdf" % (dataset, trace_type, direction)))

write_table('doc/interactions_over_platforms/tables/degFitness.csv', degFits)
