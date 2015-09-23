#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Excalibur.Plotting.utility.toolsZJet import PlottingJob


def herafile(args=None, additional_dictionary=None, pdflabel=""):
	"""make herafile"""
	quantity = "abs(zy)"
	d = {
		# input
		"x_expressions": ['nick0'],
		"files": ['3_divided/{}_madgraph_inclusive_1.root'.format(quantity)],
		"folders": [""],
		# output
		"plot_modules": ['ExportHerafitter'],
		"header_file": "herafitter/herafitter_header.txt",
		"hera_sys": 10,
		"hera_quantity": quantity.replace("(","").replace(")",""),
		"filename": 'CMS_Zee_HFinput',
		"output_dir": "/usr/users/dhaitz/home/qcd/sherivf/herafitter",
		# output
		"export_json": False,
	}
	if additional_dictionary is not None:
		d.update(additional_dictionary)
	return [PlottingJob([d], args)]


if __name__ == '__main__':
	herafile()
