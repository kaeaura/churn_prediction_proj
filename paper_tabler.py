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

powerlaw = lambda x, amp, index: amp * (x**index)

def insert_ks_table(db, keynames, save_path):
	"""docstring for insert_ks_table"""
	indeg_x_name = 'inDegDistr_x'
	indeg_y_name = 'inDegDistr_y'
	indeg_fit = 'inDegDistr_fit'
	outdeg_x_name = 'outDegDistr_x'
	outdeg_y_name = 'outDegDistr_y'
	outdeg_fit = 'outDegDistr_fit'

