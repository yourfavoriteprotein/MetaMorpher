#!/usr/bin/python -tt

import argparse
import sys
import subprocess
import os
import time

import src.metaMorpher_utils as mu
import src.PSLCoverage as pslc
import src.ReadBuilder as rbdr

def main():
	args = None
	parser = mu.get_MetaMorpher_parser()
	args = parser.parse_args()

	mu.run_Meta_Morpher(args)

	'''
	# move all this stuff to utilities -- pretty ugly in main
	switch = args.commands
	call = {"option" : switch}
	if switch == "SETUP": # set up config file
		print "setup not yet implemented"
		exit(0)

	elif switch == "RUN": # run from config file
		# should be able to run ANY of these cases
		print "RUN not yet implemented"
		exit(0)

	elif switch == "noread": # user provides reads, still run assembler, blat, etc.
		print "noread"

		call['reference'] = args.target
		call['query'] = None # create query by running assembler
		call['read1'] = args.reads
		call['read2'] = args.paired
		if args.assembler:
			call['assembler'] = args.assembler
		call['multiple'] = args.multiple
		#call['outfile'] = args.outfile # not a parser option
		call['misassembly'] = args.misassembly
		call['mismatch'] = args.mismatch
		call['quast'] = args.quast
		call['kmer'] = args.kmer

		# MetaMorpher object drives control flow from here on.
		mmobj = MetaMorpher(**call)

	elif switch == "runall": # run everything
		# create reads
		kwargs = {"target" : args.target, "insert_size" : args.insert, 
			"error_rate" : args.error, "number_reads" : args.reads, 
			"read_size" : args.readsize, "file1" : args.file1, "file2" : args.file2,
			"seed" : args.seed, "mc" : args.multiple}
		rb = rbdr.ReadBuilder(**kwargs)
		rb.make_reads()

		# MetaMorpher object will call assembler, blat, and coverage
		call['reference'] = args.target
		call['query'] = None # created by running assembler
		call['read1'] = rb._file1 # ReadBuilder object has file names
		call['read2'] = rb._file2
		if args.assembler:
			call['assembler'] = args.assembler
		call['multiple'] = args.multiple
		call['misassembly'] = args.misassembly
		call['mismatch'] = args.mismatch
		call['quast'] = args.quast
		call['kmer'] = args.kmer

		# MetaMorpher object drives control flow from here on.
		mmobj = MetaMorpher(**call)

	elif switch == "readsonly": # only create reads
		pass
		kwargs = {"target" : args.target, "insert_size" : args.insert, 
			"error_rate" : args.error, "number_reads" : args.reads, 
			"read_size" : args.readsize, "file1" : args.file1, "file2" : args.file2,
			"seed" : args.seed, "mc" : args.multiple}
		rb = rbdr.ReadBuilder(**kwargs)
		rb.make_reads()

	elif switch == "reportonly": #only produce report
		kwargs = {"psl" : args.align, "contigs" : args.query, "reference" : args.target, 
			"misassembly" : args.misassembly, "mismatch" : args.mismatch}
		pc = pslc.PSLCoverage(**kwargs)
		pc.fakeyreport()
		# TODO: QUAST!!!!!
		# alignment file should know if there's multiple chromosomes
	'''

class MetaMorpher(object):

	def __init__(self, option, reference, query, read1, read2=None, assembler='velvet', multiple=False, quast=False, outfile=None, misassembly=False, mismatch=False, kmer=21):

		dt = time.localtime()
		dt = time.strftime("%Y%m%d%H%M%S", dt)

		self.reference = reference
		self.contigs = query # get this from assembler, check runAssembler() for more
		self.read1 = read1
		self.read2 = read2
		self.assembler = assembler
		self.mc = multiple
		self.quast = quast
		if self.quast:
			self.quastdir = dt + "Quast"
			os.makedirs(self.quastdir)
		self.option = option
		self.misassembly = misassembly
		self.mismatch = mismatch

		if outfile:
			self.blatout = outfile
		else: 
			self.blatout = dt + ".psl"

		# touch the psl
		fh = open(self.blatout, "w")
		fh.close()

		# assembler options, to be set
		if kmer:
			self.kmer = kmer
		else:
			self.kmer = 21
		self.assemblerOutDir = dt # "assemblerOut"
		self.logfile = dt + ".log"
		
		self.logfile = open(self.logfile, 'w')

		self.driver()
		self.logfile.close()

	def driver(self):
		'''run assembler, blat, and PSLCoverage'''
		self.runAssembler()
		self.runBlat()
		self.runPSLCoverage()

	def runAssembler(self):
		# create output dir:
		os.makedirs(self.assemblerOutDir)

		# get assembler arguments from configuration
		# call assembler (how do you know when it's done running?)
		# get fasta file when done


		# for now, just run it with velvet 
		# (it'll be different anyway since there's 2 progs)
		if self.assembler.lower() == "velvet":
			velPath = "/s/chopin/h/proj/plant_pathogen_data/owen/bioinf/velvet/"
			velhcmd = " ".join((self.assemblerOutDir, str(self.kmer), "-fasta " \
				"-separate", self.read1, self.read2))
			subprocess.call(velPath +"velveth "+ velhcmd, shell=True, stdout=self.logfile)
			print "velveth done...\n"


			velhcmd = velPath + "velvetg" + " " + self.assemblerOutDir
			subprocess.call(velhcmd, shell=True, stdout=self.logfile)

			# now set contig location!
			self.contigs = self.assemblerOutDir + "/contigs.fa"

		else:
			pass
			# some other assembler

	
	def runBlat(self):
		'''run assembler and set self.contigs'''
		# again, get config settings for Blat
		# call Blat, get output psl

		# TODO: get blat location from config (or assume it is in path)
		blat = "/usr/local/blat/blat "
		if self.mc: # multiple chromosomes
			# create new file w/one file name per line
			pass
		else:
			# blat database query output.psl
			subprocess.call(blat  + self.reference + " " + self.contigs + " " + self.blatout, \
				stdout=self.logfile, shell=True)

	def runPSLCoverage(self):
		# run PSLCoverage
		# TODO: don't pass in quast... remove it from args!

		# TODO: print report + quast to file, call it <datestamp>.report
		p = pslc.PSLCoverage(self.blatout, self.contigs, self.reference, self.misassembly,
			self.quast, self.mismatch)
		p.fakeyreport()
		# run Quast
		if self.quast:
			call = "/s/chopin/h/proj/plant_pathogen_data/owen/bioinf/quast/quast-2.2/quast.py -o " \
				+ self.quastdir + " " + self.contigs
			subprocess.call(call, shell=True, stdout=self.logfile)
			# be sure to print out self.quastdir/report.txt for GC, N50, and N75

	def buildAssemblerCommands(self):
		# and lots of other arguments...
		# basically get 
			# name of assembler
			# arguments to pass to it
			# where output goes
		# and return this stuff (or put in self.whatever)
		pass
			

if __name__ == '__main__':
	main()
