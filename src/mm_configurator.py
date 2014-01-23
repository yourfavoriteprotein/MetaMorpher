#!/usr/bin/python

import os

def main():
	mm = MMConfigurator()
	mm.write_config()
	#mm.interactive()

class MMConfigurator(object):
	def __init__(self, config_filename=None):
		filepath = os.path.dirname(os.path.abspath(__file__))
		if config_filename:
			self.config = config_filename
		else:
			self.config = filepath + "/mm_config.txt"

		self.option = None # to be set by read_in_config
		self.defaults = {"default" : "runall",
						"readsim" : "true",
						"insert"  : "300",
						"error"   : "0",
						"reads"   : "100",
						"readsize": "100",
						"read1"   : "file1.fasta",
						"read2"   : "file2.fasta",
						"multiple": "false",

						"misassembly": "false",
						"mismatch" : "false",
						"reference": "none",
						"align"  : "none",
						"query"  : "none",

						"quast"  : "false",
						"assembler" : "velvet",
						"assemblerpath" : "none",
						"blat"   : "blat",
						"quastpath" : "quast.py",
						"block"  : "block",
						
						"kmer"	: '21'} # or, whatever, MUST BE A STRING HERE

	def argify(self):
		'''return 'args' object for use in MetaMorpher'''

		# convert strings to bools or None
		for foo in self.defaults:
			if self.defaults[foo] == 'true':
				self.defaults[foo] = True
			if self.defaults[foo] == 'false':
				self.defaults[foo] = False
			if self.defaults[foo] == 'none':
				self.defaults[foo] = None

		# because I forgot "self." and don't want to change every line
		default = self.defaults

		# argify and return args :)
		args = Argifier()
		switch = self.option

		args.multiple = default['multiple']
		args.target = default['reference']
		args.misassembly = default['misassembly']
		args.mismatch = default['mismatch']
		args.assembler = default['assembler']
		args.quast = default['quast']
		args.kmer = int(default['kmer'])
		
		args.assemblerpath = default['assemblerpath']
		args.blatpath = default['blat']
		args.quastpath = default['quastpath']
		args.block = default['block']
		args.insert = int(default['insert'])

		if switch == 'noread':
			args.reads = default['read1']
			args.paired = default['read2']
		elif switch == 'runall' or switch == "readsonly":
			args.error = int(default['error'])
			args.reads = int(default['reads']) # number_reads
			args.readsize = int(default['readsize'])
			args.file1 = default['read1']
			args.file2 = default['read2']
		elif switch == 'reportonly':
			args.align = default['align']
			args.query = default['query']

		return args

	def read_in_config(self):
		if not os.path.isfile(self.config):
			res = raw_input("Configuration file does not exist. Create one? ")
			res = res.strip().lower()
			if res == 'y' or res == 'yes' or res == 'true':
				self.interactive()
				self.write_config()
				print "config written to", self.config
			exit(0)

		# read in configuration	
		with open(self.config, 'r') as config:
			for line in config:
				line = line.strip()
				if not line or line[0] == '#' or line[0] == '!':
					continue
				line = line.split()
				if line[0] == 'default':
					self.defaults['default'] = line[1]
				elif line[0] == 'multiple':
					self.defaults['multiple'] = line[1]
				elif line[0] == 'reference':
					self.defaults['reference'] = line[1]
				elif line[0] == 'readsim':
					self.defaults['readsim'] = line[1]
				elif line[0] == 'insert':
					self.defaults['insert'] = line[1]
				elif line[0] == 'error':
					self.defaults['error'] = line[1]
				elif line[0] == 'reads':
					self.defaults['reads'] = line[1]
				elif line[0] == 'readsize':
					self.defaults['readsize'] = line[1]
				elif line[0] == 'read1':
					self.defaults['read1'] = line[1]
				elif line[0] == 'read2':
					self.defaults['read2'] = line[1]
				elif line[0] == 'misassembly':
					self.defaults['misassembly'] = line[1]
				elif line[0] == 'mismatch':
					self.defaults['mismatch'] = line[1]
				elif line[0] == 'align':
					self.defaults['align'] = line[1]
				elif line[0] == 'query':
					self.defaults['query'] = line[1]
				elif line[0] == 'quast':
					self.defaults['quast'] = line[1]
				elif line[0] == 'assembler':
					self.defaults['assembler'] = line[1]
				elif line[0] == 'assemblerpath':
					self.defaults['assemblerpath'] = line[1]
				elif line[0] == 'quastpath':
					self.defaults['quastpath'] = line[1]
				elif line[0] == 'kmer':
					self.defaults['kmer'] = line[1]
				elif line[0] == 'block':
					self.defaults['block'] = line[1]

		self.option = self.defaults['default']

	def interactive(self):
		print "running SETUP to generate MetaMorpher configuration file"
		print "\t-to skip field and use default value, press 'enter' at prompt"
		print "\t\t-[REQUIRED] indicates that you must enter a value"
		print "\t-at any time, type EXIT to quit without creating configuration\n"

		print "Which option to run by default?\n\tnoread -- run assembler, " \
			"run blat, and generate report\n\trunall -- noread + generating " \
			"simulated reads\n\treadsonly -- only generate simulated reads\n\t" \
			"reportonly -- only generate report\n"
		# res = raw_input("noread, runall, readsonly, reportonly ")
		res = raw_input("option:\t")
		prog = res.strip().lower()
		self.defaults['default'] = prog
		if prog not in "noread runall readsonly reportonly".split():
			print "invalid option"
			exit(0)

		res = raw_input("[REQUIRED] file path to referenece genome:\n\t").strip()
		if res:
			self.defaults['reference'] = res
		res = raw_input("multiple chromosomes? 'true' or 'false':\n\t").strip()
		if res:
			self.defaults['multiple'] = res.strip()

		if prog == "runall" or prog == "readsonly":
			res = raw_input("insert size:\n\t").strip()
			if res:
				self.defaults['insertsize'] = res
			res = raw_input("error rate (out of 100):\n\t").strip()
			if res:
				self.defaults['error'] = res
			res = raw_input("number of reads:\n\t").strip()
			if res:
				self.defaults['reads'] = res
			res = raw_input("size of reads in bp:\n\t").strip()
			if res:
				self.defaults['readsize'] = res
			res = raw_input("filename for simulated reads:\n\t").strip()
			if res:
				self.defaults['read1'] = res
			res = raw_input("filename for simulated paired ends:\n\t").strip()
			if res:
				self.defaults['read2'] = res

			if prog == "readsonly":
				return
		else:
			self.defaults['readsim'] = 'false'

		res = raw_input("Include misassemblies in %Coverage? 'true' or 'false':\n\t").strip()
		if res:
			self.defaults['misassembly'] = res.lower()
			res = raw_input("Minimum length of contig in bp to indicate a  " \
				"misassembly? Default is 500:\n\t").strip()
			if res:
				self.defaults['block'] = res
		res = raw_input("Include mismatched bp in %Coverage? 'true' or 'false':\n\t").strip()
		if res:
			self.defaults['mismatch'] = res.lower()

		if prog == 'reportonly':
			# need .psl, contigs
			res = raw_input("[REQUIRED] PSL file:\n\t").strip()
			if res:
				self.defaults['align'] = res
			res = raw_input("[REQUIRED] path to contigs file:\n\t").strip()
			if res:
				self.defaults['query'] = res
			return

		if prog == 'noread':
			# need reads, paired if any
			res = raw_input("path to file for reads:\n\t").strip()
			if res:
				self.defaults['read1'] = res
			res = raw_input("path to file for paired ends, or 'none':\n\t").strip()
			if res:
				self.defaults['read2'] = res

		res = raw_input("Include Quast in report? 'true' or 'false':\n\t").strip()
		if res:
			self.defaults['quast'] = res.lower()
		res = raw_input("Assembler to be used? Velvet, Ray, Spades, SOAPDenovo, or IDBA?:\n\t").strip()
		if res:
			self.defaults['assembler'] = res.lower()
		res = raw_input("Path to blat? Or just 'blat' if $PATH set:\n\t").strip()
		if res:
			self.defaults['blat'] = res
		res = raw_input("Path to assembler? Or 'none' if $PATH set:\n\t").strip()
		if res:
			self.defaults['assemblerpath'] = res
		res = raw_input("Path to Quast? Or 'none' if $PATH set:\n\t").strip()
		if res:
			self.defaults['quastpath'] = res
		res = raw_input("kmer length?:\n\t").strip()
		if res:
			self.defaults['kmer'] = res


	def write_config(self):
		filelist = []
		filelist.append("# MetaMorpher Configuration file\n\n")
		filelist.append("#########################")
		filelist.append("#\tDefault Operation\t#")
		filelist.append("#########################")
		filelist.append("!default\n")
		filelist.append("# which option runs with RUN command?")
		filelist.append("# choose from {noread, runall, readsonly, reportonly}")
		filelist.append("# or run SETUP to create config file")
		filelist.append("default " + self.defaults['default'] +"\n")
		filelist.append("# options not specific to any command\n")
		filelist.append("# create reads from multiple chromosomes?")
		filelist.append("multiple " + self.defaults['multiple'] + "\n")
		filelist.append("# reference genome, the target")
		filelist.append("reference " + self.defaults['reference'] + "\n\n")
		filelist.append("#########################")
		filelist.append("#\tRead Simulation \t#")
		filelist.append("#########################")
		filelist.append("!readbuilder\n")
		filelist.append("# simulate reads?")
		filelist.append("readsim " + self.defaults['readsim'] + "\n")
		filelist.append("# insert size")
		filelist.append("insert " + self.defaults['insert'] + "\n")
		filelist.append("# error rate")
		filelist.append("error " + self.defaults['error'] + "\n")
		filelist.append("# number of reads")
		filelist.append("reads " + self.defaults['reads'] + "\n")
		filelist.append("# size of reads in bp")
		filelist.append("readsize " + self.defaults['readsize'] + "\n")
		filelist.append("# default filename for read")
		filelist.append("read1 " + self.defaults['read1'] + "\n")
		filelist.append("# default filename for paired ends")
		filelist.append("read2 " + self.defaults['read2'] + "\n")
		filelist.append("#########################")
		filelist.append("#\tCoverage Report \t#")
		filelist.append("#########################")
		filelist.append("!pslcoverage\n")
		filelist.append("# include misassemblies in % coverage?")
		filelist.append("misassembly " + self.defaults['misassembly'] + "\n")
		filelist.append("# minimum contig length in bp to indicate misassembly")
		filelist.append("block " + self.default['block'] + "\n")
		filelist.append("# include mismatched base pairs in % coverage?")
		filelist.append("mismatch " + self.defaults['mismatch'] + "\n")
		filelist.append("# alignment file, must be in psl format")
		filelist.append("align " + self.defaults['align'] + "\n")
		filelist.append("# query file, the contigs generated by an assembler")
		filelist.append("query " + self.defaults['query'] + "\n\n")
		filelist.append("#########################")
		filelist.append("#\tAdditional Options\t#")
		filelist.append("#########################")
		filelist.append("!other\n")
		filelist.append("# include Quast in report?")
		filelist.append("quast " + self.defaults['quast'] + "\n")
		filelist.append("# assembler to be used")
		filelist.append("# supported assemblers: velvet, ray, spades")
		filelist.append("assembler " + self.defaults['assembler'] + "\n")
		filelist.append("# kmer length")
		filelist.append("kmer " + self.defaults['kmer'])

		filelist.append("# path to assembler or 'none' if $PATH set")
		filelist.append("assemblerpath " + self.defaults['assemblerpath'] + "\n")

		filelist.append("# path to blat? Or just 'blat' if $PATH set")
		filelist.append("blat " + self.defaults['blat'] + "\n")
		filelist.append("# path to quast? Or 'none' if $PATH set")
		filelist.append("quastpath " + self.defaults['quastpath'] + "\n")
		filelist.append("# assembler specific commands, to be done")

		with open(self.config, 'w') as config:
			for line in filelist:
				config.write("%s\n" % line)


class Argifier(object):
	'''container to fake getting arguments from argparse'''
	def __init__(self):
		self.target = None # reference genome
		self.reads = None # read1 or number_reads
		self.paired = None # read2
		self.assembler = None # assembler
		self.multiple = None # multiple
		self.misassembly = None # misassembly
		self.block = None # min contig length to be a misassembly
		self.mismatch = None # mismatch
		self.quast = None # quast
		self.kmer = None # kmer

		self.insert = None # insert
		self.error = None
		self.readsize = None
		self.file1 = None # read1 again
		self.file2 = None # read2 again
		# self.seed = None ##### not here, only when ReadBuilder run on own

		self.align = None # psl
		self.query = None # contigs

		# because MetaMorpher asks for this, maybe could add support in the future
		self.seed = False

		self.assemblerpath = None
		self.quastpath = None
		self.blatpath = None

if __name__ == "__main__":
	main()
