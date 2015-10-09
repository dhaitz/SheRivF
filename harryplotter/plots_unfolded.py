#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Artus.HarryPlotter.harry as harry
from Excalibur.Plotting.utility.toolsZJet import PlottingJob
import Excalibur.Plotting.utility.colors as colors
import parsertools

import numpy as np
import common


def unfold(args=None):
	"""Unfold Z(->ee) distributions and save as root. All combinations of n jet categories, rapidity bins, MC samples and quantities (y, mass, pT) are plotted."""

	known_args, args = parsertools.parser_list_tool(args, ['ybins', 'mcs', 'quantities', 'iterations'])

	# some variables
	path = common.bkgr_path
	max_iterations = 4

	plots = []
	for ybin, ybinsuffix in zip(*parsertools.get_list_slice([
				["1"] + common.ybin_weights,
				["inclusive"] + common.ybin_labels,
	], known_args.no_ybins)):
		for mc_label, mc in zip(*parsertools.get_list_slice([
			['Madgraph', 'Powheg'],
			['mc_ee.root', 'mc_ee_powheg.root']
		], known_args.no_mcs)):
			for quantity in parsertools.get_list_slice([common.data_quantities], known_args.no_quantities)[0]:
				for iteration in parsertools.get_list_slice([range(1, 1+max_iterations)], known_args.no_iterations)[0]:
					for variation in common.variations + common.unfolding_variations:
						if variation == '_unfdown':
							unfolding_variation = -1
							input_var = ""
						elif variation == '_unfup':
							unfolding_variation = 1
							input_var = ""
						else:
							unfolding_variation = 0
							input_var = variation
						d = {
							'x_expressions': ['data']+[common.root_quantity(quantity).replace("z", "genz"), common.root_quantity(quantity), common.root_quantity(quantity).replace("z", "genz")],
							'y_expressions': [None, common.root_quantity(quantity), None, None],
							'files': ["1_background-subtracted/" + quantity + "_" + ybinsuffix + input_var + ".root"]+[path + "/work/" + mc]*3,
							'nicks': [
								'data_reco',
								'responsematrix',
								'mc_reco',
								'mc_gen',
							],
							'lumis': [common.lumi],
							'folders': ['']+['zcuts_ak5PFJetsCHSL1L2L3/ntuple']*3,
							'weights': "weight*({}&&hlt)".format(ybin),
							'x_bins': [common.bins[quantity]],
							'y_bins': [None, common.bins[quantity], None, None],
							# analysis
							'analysis_modules': ['Unfolding'],
							'unfolding': ['data_reco', 'mc_reco'],
							'unfolding_responsematrix': 'responsematrix',
							'unfolding_mc_gen': 'mc_gen',
							'unfolding_mc_reco': 'mc_reco',
							'unfolding_new_nicks': ['data_unfolded', 'mc_unfolded'],
							'unfolding_iterations': iteration,
							'unfolding_variation': unfolding_variation,
							'libRooUnfold': '~/home/RooUnfold/libRooUnfold.so',
							#output
							'plot_modules': ['ExportRoot'],
							'filename': "_".join([quantity, mc_label.lower(), ybinsuffix]) + variation + "_" + str(iteration),
							'output_dir': common.unfold_path,
							'export_json': False,
						}
						plots.append(d)
	return [PlottingJob(plots, args)]


def different_iterations(args=None):
	"""compare different unfolding iterations"""
	plots = []
	ybin = 'inclusive'
	max_iteration = 4
	for quantity in common.data_quantities:
		basename = common.unfold_path + '/' + '_'.join([quantity, 'madgraph', ybin, '{}']) + '.root'
		d = {
			# input
			'files': [basename.format(str(1))]*2 + [basename.format(str(1+n)) for n in range(max_iteration)],
			'folders': [''],
			'nicks': ['data', 'mc'] + [str(item) for item in range(max_iteration)],
			'labels': ['Data', 'MC Gen'] + ["Unfolded ({} iter.)".format(str(item+1)) for item in range(max_iteration)],
			'x_expressions': ['data_reco', 'mc_gen']+['data_unfolded']*max_iteration,
			# formatting
			'markers': ['o', 'fill'] + ['.']*(max_iteration*2+1),
			'line_styles': ['None']*2 + ['-']*(max_iteration)+['None']*(max_iteration+1),
			'step': [True],
			'marker_colors': ['black', 'red', 'blue', 'green', 'purple']*2,
			'x_label': quantity,
			'legend': 'upper right',
			# output
			'filename': 'iterations_' + quantity,
			'www_title': 'Unfolding: different iterations',
			'www_text': r"Different iterations for d\'Agostini unfolding",
		}
		if quantity == 'zpt':
			d['y_log'] = True
		# ratio to MC gen
		d.update({
			'analysis_modules': ['Ratio'],
			'ratio_numerator_nicks': [str(item) for item in ([0]+range(max_iteration))],
			'ratio_denominator_nicks': ['mc'],
			'y_subplot_label': 'Ratio to MC Gen',
			'y_subplot_lims': [0, 2],
		})
		plots.append(d)
	return [PlottingJob(plots, args)]

def response_matrix(args=None):
	""" plot response matrix"""
	plots = []
	ybin = 'inclusive'
	for log in [True, False]:
		for quantity in common.data_quantities:
			lims = common.lims(quantity)
			d = {
				# input
				'files': [common.unfold_path + '/' + '_'.join([quantity, 'madgraph', ybin, '1']) + '.root'],
				'folders': [''],
				'x_expressions': ['responsematrix'],
				# formatting
				'y_lims': lims,
				'x_lims': lims,
				'x_label': 'gen' + quantity,
				'y_label': 'reco' + quantity,
				'energies': [8],
				'z_log': log,
				# output
				'filename': 'responsematrix_' + quantity + ("_log" if log else ""),
				'www_title': 'Response Matrices',
				'www_text': r"Unfolding response matrices from d\'Agostini Unfolding for Z y,mass,pT with log and scalar z-axis",
			}
			plots.append(d)
	return [PlottingJob(plots, args)]


def unfolding_comparison(args=None):
	"""Comparison between reco,gen,unfolded for Data and MC"""
	plots = []

	ybin = 'inclusive'
	labels = ['Data Reco', 'MC Reco', 'MC Gen', 'Data Unfolded', 'MC Unfolded']
	expressions = [label.lower().replace(" ", "_") for label in labels]

	for iterations in range(1, 5):
		for quantity in common.data_quantities:
			filename = common.unfold_path + '/' + '_'.join([quantity, 'madgraph', ybin, str(iterations)]) + '.root'
			d = {
				# input
				'files': [filename],
				'folders': [''],
				'x_expressions': expressions,
				'nicks': expressions,
				# formatting
				'labels': labels,
				'markers': ['o']*2+['fill']+['.']*2+['o']*2+['.']*2,
				'line_styles': [None]*3 + ['-']*2+[None]*2+['-']*2,
				'step': [True],
				'marker_colors': ['black', 'red'],
				'zorder': [10,10,2,10,10],
				'energies': [8],
				'legend': 'upper right',
				'y_subplot_lims': [0.9, 1.1],
				#'lumis': [common.lumi],
				'x_label': quantity,
				#'title': str(iterations) + " iteration" + ("s" if iterations != 1 else ""),
				# output
				'filename': "_".join(['unfolded', quantity, str(iterations)]),
				'www_title': 'Unfolding',
				'www_text': 'Comparison of Data and MC at reco-, gen- and unfolded-level for different unfolding iterations',
			}
			if quantity == 'zpt':
				d['y_log'] = True
				d['x_log'] = common.zpt_xlog
				d['y_lims'] = [1, 1e7]
				d['x_ticks'] = common.zpt_ticks
			# ratio to MC gen
			d.update({
				'analysis_modules': ['Ratio'],
				'ratio_numerator_nicks': [e for e in expressions if "unfolded" in e],
				'ratio_denominator_nicks': [e for e in expressions if "reco" in e],
				'y_subplot_label': 'Unfolded/Reco',
			})
			plots.append(d)
	return [PlottingJob(plots, args)]


def unfolded_to_hera(args=None):
	""" take unfolded data and convert it into herafitter format"""
	plots = []
	d = {
		'files': ['2_unfolded/zpt_madgraph_inclusive_{}.root'.format(iterations_to_use)],
		'folders': [''],
		'x_expressions': ['data_unfolded'],
		# output
		'plot_modules': 'ExportHerafitter',
		'header_file': '/usr/users/dhaitz/home/qcd/sherivf/herafitter/herafitter_header.txt',
		'filename': 'CMS_Zee_HFinput',
		'output_dir': 'herafitter/',
	}
	plots.append(d)
	return [PlottingJob(plots, args)]


if __name__ == '__main__':
	zee_unfolded()