#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse, os

from Excalibur.Plotting.utility.toolsZJet import PlottingJob

import plots_electron
import plots_fastnlo
import plots_pdf_reweighted
import plots_pdf
import plots_pdf_correlation
import plots_sherpa
import plots_bkgrs
import plots_zee_divide
import plots_uncertainties
import plots_unfolded
import plots_pdf_uncertainties


def allplots(args=None):
	"""make allplots"""
	plotting_jobs = []

	parser = argparse.ArgumentParser()
	parser.add_argument('--www-dir', type=str, default="zee", help="www dir")
	parser.add_argument('--start', type=int, default=0, help="start")
	parser.add_argument('--end', type=int, default=999, help="end")
	known_args, args = parser.parse_known_args(**({'args':args} if args is not None else {}))

	plot_min = known_args.start
	plot_max = known_args.end

	functions = [
		plots_pdf.pdfs_thesis,  # 0
		plots_pdf_correlation.pdf_correlations,
		plots_electron.electron_id,
		plots_electron.electron_corr,
		plots_electron.electron_trigger_sf,
		plots_bkgrs.zee_bkgrs,  # 5
		plots_bkgrs.emu,
		plots_unfolded.different_iterations,
		plots_unfolded.response_matrix,
		plots_unfolded.unfolding_comparison,
		plots_sherpa.sherpa,  # 10
		plots_sherpa.sherpa_mc,
		plots_fastnlo.fastnlo_pdfsets,
		plots_fastnlo.fastnlo_pdfmember,
		plots_fastnlo.sherpa_fastnlo,
		plots_pdf_reweighted.nnpdf,  # 15
		plots_uncertainties.scale_uncertainties,
		plots_fastnlo.k_factors,
		plots_uncertainties.plot_uncertainties,
		plots_zee_divide.divided_ptspectrum,
		plots_pdf_uncertainties.plot_pdf_uncs_hera,  # 20
		plots_pdf_uncertainties.plot_pdf_uncs_heraZ,
		plots_pdf_uncertainties.plot_pdf_uncs_heraZ_bins,
		plots_pdf_uncertainties.plot_pdf_unc_comparison,
		plots_bkgrs.signal_background_ratio,
		plots_electron.electron_scale_unc,  # 25
		plots_pdf_uncertainties.plot_pdf_uncs_heraZ_pt,
	][plot_min:plot_max]
	
	wwwdirs = [
		"pdfs",
		"correlations",
		"electron_id",
		"electron_momentum_corrections",
		"electron_sf",
		"backgrounds",
		"emu",
		"unfolding_iteration",
		"unfolding_reponsematrices",
		"unfolding_comparisons",
		"sherpa",
		"sherpa_mc",
		"fastnlo_pdfsets",
		"fastnlo_pdfmember",
		"fastnlo_sherpa",
		"nnpdf",
		"scale_uncertainty",
		"k_factors",
		"uncertainties",
		"spectra_in_ybins",
		"pdf_uncertainties_hera",
		"pdf_uncertainties_heraZ",
		"pdf_uncertainties_heraZ_bins",
		"pdf_uncertainties_comparison",
		"backgrounds_signal_ratio",
		"electron_scale_uncertainty",
		"pdf_uncertainties_heraZ_pt",
	][plot_min:plot_max]

	for function, wwwdir in zip(functions, wwwdirs):
		if function == plots_bkgrs.zee_bkgrs:
			plots = function(args + ["--no-njets", "--no-ybins", "--no-mcs"])
		elif function == plots_bkgrs.signal_background_ratio:
			plots = function(args + ["--no-njets", "--no-ybins"])
		else:
			plots = function(args)
		for plot in plots[0].plots:
			plot['www'] = os.path.join(known_args.www_dir, wwwdir)
		plotting_jobs += plots

	return plotting_jobs

