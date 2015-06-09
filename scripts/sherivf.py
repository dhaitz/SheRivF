#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This is the GC wrapper"""

import sys, os, glob, shutil, time, subprocess, argparse, socket


class Sherivf(object):

	def __init__(self):
		self.fastnlo_outputs = ['fnlo_yZ.txt', 'fnlo_pTZ.txt', 'fnlo_mZ.txt']

		if 'naf' in socket.gethostname().lower():
			self.default_config = 'naf'
			self.default_storage_path = '/afs/desy.de/user/d/dhaitz/nfs/sherivf/'
		elif 'ekp' in socket.gethostname().lower():
			self.default_config = 'ekpcluster'
			self.default_storage_path = '/storage/a/dhaitz/sherivf/'
		self.get_arguments()

	def run(self):
		"""Main function.
			1. Get configs.
			2. Check if a new workdir has to be created.
			3. Delete, resume or start new (default) run
		"""

		# config dir: new or existing one?
		if self.args.delete or self.args.resume:
			paths = glob.glob("{0}/{1}*".format(self.args.output_dir, self.args.config))
			paths.sort()
			try:
				self.args.output_dir = paths[-1]
				self.args.configfile = filter(lambda x: "work.sherpa-rivet" in x, glob.glob(paths[-1] + "/*"))[0].split("work.")[-1] + ".conf"
			except IndexError:
				sys.exit("No output directories exist!")
		else:
			self.args.output_dir += (self.args.config + "_" + time.strftime("%Y-%m-%d_%H-%M"))

		# delete, normal run or warmup?
		if self.args.delete:
			self.delete_latest_output_dir()
		else:
			if not self.args.resume:
				self.create_output_dir()
				self.copy_gc_configs()
			run_gc(self.args.output_dir + "/" + self.args.configfile)
			if not self.args.warmup:
				outputs = self.merge_outputs()
				print "\nOutputs:\n", outputs
			else:
				self.merge_warmup_files()


	def delete_latest_output_dir(self):
		try:
			subprocess.call(['go.py', self.args.output_dir + "/" + self.args.configfile, "-d all"])
		except:
			print "could not delete currently running jobs"
			exit(1)
		try:
			shutil.rmtree(self.args.output_dir)
			print "Directory {0} deleted.".format(self.args.output_dir)
		except:
			print "Could not delete output directory {0}".format(self.args.output_dir)


	def get_arguments(self):
		parser = argparse.ArgumentParser(
			description="%(prog)s is the main analysis program.", epilog="Have fun.")

		parser.add_argument('-c', '--config', type=str, default=self.default_config,
			help="config to run. will be set automatically for naf")
		parser.add_argument('-d', '--delete', action='store_true',
			help="delete the latest output and jobs still running")
		parser.add_argument('-r', '--resume', action='store_true',
			help="resume the grid-control run.")
		parser.add_argument('--rivet-only', action='store_true',
			help="only recover rivet outputs, not fastNLO.")

		parser.add_argument('-n', '--n-events', type=str, default='1',
			help="n events")
		parser.add_argument('-j', '--n-jobs', type=str, default='1',
			help="n jobs")

		parser.add_argument('--output-dir', type=str, help="output directory",
			default=self.default_storage_path)

		parser.add_argument('-w', '--warmup', action='store_true', default=False,
			help="if set, do warmup run")

		self.args = parser.parse_args()

		# define configs to use
		self.args.configfile = 'sherpa-rivet_{0}.conf'.format(self.args.config)
		self.args.list_of_gc_cfgs = [
			get_env('SHERIVFDIR') + '/' + 'sherpa-gc/sherpa-rivet_base.conf',
			get_env('SHERIVFDIR') + '/' + 'sherpa-gc/run-sherpa.sh',
			get_env('SHERIVFDIR') + '/' + 'sherpa-gc/sherpa-rivet_{0}.conf'.format(self.args.config)
		]
		if 'ekp' in socket.gethostname().lower():
			self.args.list_of_gc_cfgs.append(get_env('SHERIVFDIR') + '/' + 'sherpa-gc/sherpa-rivet_ekp-base.conf')
		if self.args.config == 'ekpcloud':
			self.args.output_dir = self.args.output_dir.replace("/a/", "/ekpcloud_local/")


	def create_output_dir(self):
		"""
			ensure that the output path exists and delete old outputs optionally)
			to save your outputs simply rename them without timestamp
		"""
		print "Output directory:", self.args.output_dir
		os.makedirs(self.args.output_dir + "/work." + self.args.configfile.replace(".conf", ""))
		os.makedirs(self.args.output_dir + "/output")


	def copy_gc_configs(self):
		if self.args.rivet_only:
			output = (' '.join(self.fastnlo_outputs) if self.args.warmup else "Rivet.yoda")
		else:
			output = (' '.join(self.fastnlo_outputs) if self.args.warmup else "Rivet.yoda " + ' '.join(self.fastnlo_outputs))

		for gcfile in self.args.list_of_gc_cfgs:
			copyfile(gcfile, self.args.output_dir+'/'+os.path.basename(gcfile),{
				'@NEVENTS@': self.args.n_events,
				'@NJOBS@': self.args.n_jobs,
				'@OUTDIR@': self.args.output_dir+'/output',
				'@WARMUP@': ("rm *warmup*.txt"if self.args.warmup else ""),
				'@OUTPUT@': output,
			})


	def merge_outputs(self):
		outputs = []
		try:
			commands = ['yodamerge']+ glob.glob(self.args.output_dir+'/output/'+'*.yoda') +['-o', self.args.output_dir+'/Rivet.yoda']
			print_and_call(commands)
			outputs.append(self.args.output_dir+'/Rivet.yoda')
		except:
			print "Could not merge Rivet outputs!"

		if self.args.rivet_only:
			return outputs

		try:
			for quantity in [item.split("_")[1].replace("Z.txt", "") for item in self.fastnlo_outputs]:
				commands = ['fnlo-tk-append'] + glob.glob(self.args.output_dir+'/output/'+'fnlo_{}Z*.txt'.format(quantity)) + [output_dir+'/fnlo_{}Z.txt'.format(quantity)]
				print_and_call(commands)
				outputs.append(self.args.output_dir+'/fnlo_{}Z.txt'.format(quantity))
		except:
			print "Could not merge fastNLO outputs!"

		return outputs


	def merge_warmup_files(self):
		for scenario in [item.replace("Z.txt", "") for item in self.fastnlo_outputs]:
			commands = [
				"/usr/users/dhaitz/home/qcd/fastnlo_toolkit_fredpatches/fastNLO/trunk/tools/fnlo-add-warmup.pl",
				"-w",
				self.args.output_dir+"/output/",
				scenario
			]
			print_and_call(commands)

def run_gc(config):
	commands = ['go.py', config]
	try:
		print_and_call(commands)
	except KeyboardInterrupt:
		exit(0)
	except:
		print "grid-control run failed"
		exit(1)


def print_and_call(commands):
	print " ".join(commands)
	subprocess.call(commands)


def copyfile(source, target, replace={}):
	# copy file with replace dict
	with open(source) as f:
		text = f.read()
	for a, b in replace.items():
		text = text.replace(a, b)
	with open(target, 'wb') as f:
		f.write(text)
	return text


def get_env(variable):
	try:
		return os.environ[variable]
	except:
		print variable, "is not in shell variables:", os.environ.keys()
		print "Please source scripts/ini.sh!"
		sys.exit(1)


if __name__ == "__main__":
	sherivf = Sherivf()
	sherivf.run()
