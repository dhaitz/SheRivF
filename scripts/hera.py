#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
	create a workdir and all files, start herafitter in parallel with GC including all uncertainties
"""

import time, sys, os, glob, argparse, subprocess
import sherivftools
import copy_herafitter_steering


class Hera(object):

	def __init__(self):
		self.mode = 'hera2'
		self.default_value = None
		self.config = "herafitter.conf"
		self.files_to_copy = [self.config, 'minuit.in.txt', 'herapdf_par.conf', 'ewparam.txt','run-herafitter.sh']
		self.default_storage_path = get_env('HERA_STORAGE_PATH')
		self.get_arguments()


	def get_arguments(self):
		parser = argparse.ArgumentParser(
			description="%(prog)s is the main analysis program.", epilog="Have fun.")

		parser.add_argument('-v', '--value', type=str, default=self.default_value, help="Value", choices=copy_herafitter_steering.values.keys())
		parser.add_argument('-o', '--output-dir', type=str, default=None, help="")
		
		self.args = parser.parse_args()
		if self.args.output_dir is None:
			self.args.output_dir = (self.mode + ('_' + self.args.value if self.args.value else '') + "_" + time.strftime("%Y-%m-%d_%H-%M"))
		self.args.output_dir = self.default_storage_path + "/" + self.args.output_dir


	def run(self):
		# create gc-dir and copy necessary files
		print "Output directory:", self.args.output_dir
		os.makedirs(self.args.output_dir + "/work." + self.config.replace(".conf", ""))
		os.makedirs(self.args.output_dir + "/output")
		
		self.list_of_gc_files = [sherivftools.get_env('SHERIVFDIR') + '/hera-gc/' + f for f in self.files_to_copy]
		for gcfile in self.list_of_gc_files:
			sherivftools.copyfile(gcfile, self.args.output_dir+'/'+os.path.basename(gcfile),{
				'@OUTDIR@': self.args.output_dir+'/output',
			})
		copy_herafitter_steering.copy_herafile(self.mode, self.args.value, True, self.args.output_dir)

		# run GC
		self.gctime = time.time()
		gc_success = sherivftools.run_gc(self.args.output_dir + "/" + self.config, self.args.output_dir)
		self.gctime = time.time() - self.gctime
		if gc_success:
			sherivftools.create_result_linkdir(self.args.output_dir+"/output/", self.mode + ('_' + self.args.value if self.args.value else ''))



if __name__ == "__main__":
	start_time = time.time()
	hera = Hera()
	hera.run()
	if hasattr(hera, "gctime"):
		print "---        Hera took {}  ---".format(sherivftools.format_time(time.time() - start_time))
		print "--- GridControl took {}  ---".format(sherivftools.format_time(hera.gctime))
