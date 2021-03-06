#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
	DOCUMENTATION
	script to check the statistical precision of fastNLO tables
	originally be gsieber
	
	Example:
		$ python fnlostatana.py -i $PWD/sherpa_output/ --nlo '^zpt_[0-9]+.tab$' --max 5  --work $PWD
	find all tables in sherpa_output/ matching '^zpt_[0-9]+.tab$', print mean,
	StdDev, all tables where |xsec-median|> 5 sigma and create plots for all
	bins in a folder in the current dir
	Add --filter to move critical tables into subfolder.
"""

import argparse
import glob
import math
import multiprocessing
import numpy as np
import os
import re
import sys
import shutil

import matplotlib.pyplot as plt
import matplotlib

import fastnlo
fastnlo.SetGlobalVerbosity(fastnlo.WARNING)

import logging
log = logging.getLogger(__name__)
# additional log handler to write log file
filelog = logging.FileHandler(os.path.splitext(os.path.basename(__file__))[0]+'.log')
filelog.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
log.addHandler(filelog)


def main():

	parser = argparse.ArgumentParser(description='Statistical analysis of fastNLO tables')

	parser.add_argument('-i', '--input-folder', help='Folder containing the fastNLO files.', required=True)
	parser.add_argument('--work-dir', help='Workdir.')
	parser.add_argument('--pdfset', default='CT10nlo', help='PDF set to evaluate fastNLO tables.')
	parser.add_argument('-r', '--regex', default='^.*nlo.*$', help='Regex matching tables in input folder.')
	parser.add_argument('-m', '--max-processes', type=int, default=8, help='Max number of parallel processes')
	parser.add_argument('--filter', action='store_true', default=False, help='Filter invalid tables.')
	parser.add_argument('-s', '--stds', type=float, default=100., help='number of standard deviations a \
	                   table is allowed to deviate from the median to not be considered critical')
	parser.add_argument("--log-level", default="info", help="Log level.")

	# Parse arguments.
	args = vars(parser.parse_args())
	if args['work_dir'] is None:
		args['work_dir'] = args['input_folder']

	# Setup logger and log level
	log_level = getattr(logging, args['log_level'].upper(), None)
	if not isinstance(log_level, int):
		raise ValueError('Invalid log level: %s' % loglevel)
	logging.basicConfig(format='%(message)s', level=log_level)

	log.info('Globbing all .tab files in input directory.')
	log.debug('Regex for NLO tables is \'{0}\'.'.format(args['regex']))

	# Find all fastNLO tables in input folder
	fnlo_tables = glob.glob(os.path.join(args['input_folder'], '*.tab'))
	tables_files = [table for table in fnlo_tables if re.match(args['regex'], os.path.basename(table))]
	log.info('Found {0} tables in input directory.'.format(len(tables_files)))
	if len(tables_files) < 1:
		log.error("no tables!")
		sys.exit(1)

	# Read one table to get number of bins
	_fnlo = fastnlo.fastNLOLHAPDF(tables_files[0], args['pdfset'])
	n_bins = _fnlo.GetNObsBin()
	log.info('Tables contain {0} observable bins.'.format(n_bins))

	# get cross section values
	n_procs = min([args['max_processes'], len(tables_files)])
	log.info("Get cross section from fastNLO tables using {} processes".format(n_procs))
	pool = multiprocessing.Pool(processes=n_procs)
	results = pool.map_async(gettab, [(tab, args['pdfset']) for tab in tables_files])
	xs_nlo = np.array(results.get(9999999)) # 9999999 is needed for KeyboardInterrupt to work: http://stackoverflow.com/questions/1408356/keyboard-interrupts-with-pythons-multiprocessing-pool

	# calculate statistical estimators
	mean = np.mean(xs_nlo, axis=0)
	std = np.std(xs_nlo, axis=0)
	mean_error = std/math.sqrt(float(len(tables_files)))
	mean_error_rel = mean_error/mean
	mean_error_rel_percent = mean_error_rel*100.
	median = np.median(xs_nlo, axis=0)
	tmean = trimmed_mean(xs_nlo, axis=0, percentile=0.1)
	tstd = trimmed_std(xs_nlo, axis=0, percentile=0.1)

	# print results
	for values in ['mean', 'tmean', 'std', 'mean_error', 'mean_error_rel', 'mean_error_rel_percent', 'tstd', 'median', 'std/mean', 'tstd/mean', 'mean/median']:
		log.info(values)
		values = eval(values)
		magn = min([int(math.log10(x)) for x in values])
		log.info(np.array([round(value, max([0, 2-magn])) for value in values]))

	#plot
	plot_distribution(xs_nlo, plot_dir='nlo_plots', **args)

	# Find all tables where any bin is > x std off from the mean
	invalid_nlo_tables = np.array(tables_files)[np.any(xs_nlo-median > args['stds'] * xs_nlo.std(axis=0), axis=1)]
	if invalid_nlo_tables.size != 0:
		log.warning('There are tables with potential problems (any bin with xsec {} sigma away from median):'.format(args['stds']))
		log.info('\n'.join(invalid_nlo_tables))
		if args['filter']:
			directory = os.path.join(args['work_dir'],'invalid_nlo_tables')
			log.info('The tables will be moved into the directory {0}.'.format(directory))
			if not os.path.exists(directory):
				os.makedirs(directory)
			for filename in invalid_nlo_tables:
				shutil.move(filename, directory)

	#TODO
	# merge tables


def trimmed_mean(data, axis=None, percentile=0.05):
	""" Return trimmed mean while trimming percentile data."""
	data_sorted = np.sort(data)
	percentile = percentile / 2.
	low, high = int(percentile * len(data)), int((1. - percentile) * len(data))
	return data[low:high,...].mean(axis=axis)

def trimmed_std(data, axis=None, percentile=0.05):
	""" Return trimmed std while trimming percentile data."""
	data_sorted = np.sort(data)
	percentile = percentile / 2.
	low = int(percentile * len(data))
	high = int((1. - percentile) * len(data))
	return data[low:high,...].std(ddof=0, axis=axis)



def plot_distribution(xs, **kwargs):
	"""
	   Calculates cross section for each bin, fills a histogram and 
	   plots the pull to the mean of all predictions.
	"""
	xs = xs.transpose()
	directory = os.path.join(kwargs['work_dir'],kwargs.get('plot_dir', 'plots'))
	log.info("Create plots in "+directory)
	if not os.path.exists(directory):
		os.makedirs(directory)

	# Fill distribution for each bin
	for i, bin_arr in enumerate(xs):
		mean = np.median(bin_arr)
		std = np.std(bin_arr)
		hist, bin_edges = np.histogram(bin_arr/mean, bins=np.arange(0.05, 1.95, 0.01))
		fig = plt.figure()
		fig.suptitle('Normalized width observable bin: {0}'.format(i))
		ax = fig.add_subplot(1, 1, 1)
		bin_width=(bin_edges[1:]-bin_edges[:-1])
		ax.bar(bin_edges[:-1], hist,bottom=1., width=bin_width)
		ax.set_xlim(min(bin_edges), max(bin_edges))

		ax.set_xlabel(r'$\sigma / \langle \sigma \rangle $')
		ax.set_ylabel('count')

		ax.text(0.98, 0.98, 'mean={0:.2g}\nstd={1:.2f}%\n$\Delta$mean={4:.2f}%\nmin={2:.2g}\nmax={3:.2g}'.format(
					 mean, 
					 (std/mean)*100.,
					 np.min(bin_arr),
					 np.max(bin_arr), 
					 ((std/np.sqrt(bin_arr.size))/mean)*100.),
				ha='right', va='top', 
				transform=ax.transAxes)

		fig.savefig(os.path.join(directory, 'bin_{0}.png'.format(i)), bbox_inches='tight')
		plt.close()


def gettab(arg):
	return np.array(fastnlo.fastNLOLHAPDF(*arg).GetCrossSection())



def merge_fnlo_tables(fnlo_tables, output_path):
	"""Merges fastNLO tables. Basically a copy of fnlo-tk-merge tool."""
	if not fnlo_tables:
		raise ValueError("Input list is empty or not a valid list.")

	res_table = None
	for fnlo_table_path in fnlo_tables:
		# Check if path exists
		if not os.path.exists(fnlo_table_path):
			raise Exception("The path {0} is not a valid.".format(fnlo_table_path))

		table = fastnlo.fastNLOTable(fnlo_table_path)
		# If results is None (first table), create one

		if res_table is None:
			res_table = table
		else:
			# Check if table is 
			if res_table.IsCompatible(table):
				log.debug("Adding table {0}.".format(fnlo_table_path))
				res_table.AddTable(fastnlo.fastNLOTable(table))
			else:
				raise Exception('fastNLOTables not compatible')

	res_table.SetFilename(output_path)
	res_table.WriteTable()


if __name__ == '__main__':
	main()
